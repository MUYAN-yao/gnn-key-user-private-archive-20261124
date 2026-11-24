"""Run preregistered v2-T0c objective ablations without altering v2-T0b."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app import pipeline_v2_t0 as t0
from app.contracts import AnalysisConfig
from app.graph import build_snapshot
from app.optimizer import evaluate_seed_set, gnn_guided_robust_greedy, simulation_seed_sequence
from app.pipeline_v2_t0b import _windows
from app.validation import NetworkDataset, load_dataset
from run_rolling_study_v2_t0 import expected_higgs_hashes, sha256


FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(42, 52))
FULL_OBJECTIVE = {"risk_lambda": 0.35, "community_weight": 0.25}
ARMS = {
    "risk_off": {"risk_lambda": 0.00, "community_weight": 0.25},
    "community_off": {"risk_lambda": 0.35, "community_weight": 0.00},
    "spread_only": {"risk_lambda": 0.00, "community_weight": 0.00},
}
REFERENCE_METHOD = "gnn_guided_robust_greedy_v2_t0b"
REFERENCE_CONFIG = {
    "seed_count": 2, "horizon": 4, "risk_lambda": 0.35,
    "community_weight": 0.25, "diffusion_model": "ic", "epochs": 10,
    "ants": 3, "iterations": 2, "simulations": 20,
    "optimizer": "robust_greedy", "candidate_pool_size": 120,
}


def run_id(fraction: float, seed: int) -> str:
    return f"split-{fraction:.2f}-seed-{seed}"


def validate_reference(reference_dir: Path) -> dict[str, dict]:
    manifest_path = reference_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("The completed v2-T0b reference manifest is required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    references: dict[str, dict] = {}
    expected = {run_id(fraction, seed) for fraction in FRACTIONS for seed in SEEDS}
    paths = {path.stem: path for path in reference_dir.glob("split-*.json")}
    if set(paths) != expected:
        raise ValueError("The reference directory does not contain the preregistered 30-run set")
    for identifier, path in paths.items():
        if manifest.get("runs", {}).get(path.name) != sha256(path):
            raise ValueError(f"Reference artifact hash mismatch: {path.name}")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        config = artifact.get("config", {})
        fraction = float(identifier.split("-")[1])
        seed = int(identifier.split("-")[3])
        required_config = {**REFERENCE_CONFIG, "train_fraction": fraction, "random_seed": seed}
        if any(config.get(key) != value for key, value in required_config.items()):
            raise ValueError(f"Reference configuration mismatch: {identifier}")
        reproducibility = artifact.get("reproducibility", {})
        if reproducibility.get("evaluation_protocol") != "common_random_numbers":
            raise ValueError(f"Reference does not record common-random-number evaluation: {identifier}")
        if reproducibility.get("probability_protocol") != "v2_t0b_timestamp_grouped_isotonic":
            raise ValueError(f"Reference probability protocol mismatch: {identifier}")
        if reproducibility.get("calibration_cutoff") >= reproducibility.get("outer_test_start"):
            raise ValueError(f"Reference violates strict timestamp ordering: {identifier}")
        if artifact.get("result", {}).get("method") != REFERENCE_METHOD:
            raise ValueError(f"Reference method mismatch: {identifier}")
        references[identifier] = artifact
    return references


def score_payload(score) -> dict[str, float | int | list[str]]:
    return {
        "top_k": score.seeds,
        "mean_spread": round(score.mean_spread, 3),
        "spread_std": round(score.std_spread, 3),
        "robust_objective": round(score.objective, 3),
        "community_coverage": score.community_coverage,
    }


def evaluate_decomposition(graph, probabilities, communities, seeds, config: AnalysisConfig, streams: list[int]) -> dict[str, dict]:
    payload: dict[str, dict] = {}
    for name, terms in {"full": FULL_OBJECTIVE, **ARMS}.items():
        score = evaluate_seed_set(
            graph, probabilities, communities, seeds, config.horizon,
            terms["risk_lambda"], terms["community_weight"], config.diffusion_model, streams,
        )
        payload[name] = score_payload(score)
    return payload


def run_arm(dataset: NetworkDataset, arm: str, fraction: float, seed: int, reference: dict) -> dict:
    started = time.perf_counter()
    terms = ARMS[arm]
    config = AnalysisConfig(
        seed_count=2, horizon=4, risk_lambda=terms["risk_lambda"],
        community_weight=terms["community_weight"], diffusion_model="ic",
        random_seed=seed, epochs=10, ants=3, iterations=2, simulations=20,
        train_fraction=fraction, optimizer="robust_greedy", candidate_pool_size=120,
    )
    history, supervised, calibration, outer_test, outer_train = _windows(dataset, fraction)
    if not (history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min()):
        raise AssertionError("v2-T0c timestamp windows are not strictly ordered")
    snapshot = build_snapshot(dataset, outer_train)
    probabilities, uses_pyg = t0._calibrated_probabilities(
        dataset, history, supervised, calibration, snapshot, seed
    )
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Every decision edge must receive a calibrated probability")
    prior = t0._node_prior(snapshot.graph, probabilities)
    selection_started = time.perf_counter()
    selected = gnn_guided_robust_greedy(
        snapshot.graph, probabilities, prior, snapshot.communities, config.seed_count,
        config.horizon, config.risk_lambda, config.community_weight,
        config.diffusion_model, config.simulations, config.random_seed,
        config.candidate_pool_size,
    )
    selection_seconds = time.perf_counter() - selection_started
    streams = simulation_seed_sequence(seed, config.simulations)
    decomposition = evaluate_decomposition(
        snapshot.graph, probabilities, snapshot.communities, selected.seeds, config, streams
    )
    identifier = run_id(fraction, seed)
    return {
        "arm": arm,
        "config": asdict(config),
        "reporting_objective": FULL_OBJECTIVE,
        "reproducibility": {
            "random_seed": seed, "train_fraction": fraction,
            "achieved_outer_train_fraction": len(outer_train) / len(dataset.edges),
            "window_rows": {"history": len(history), "supervised": len(supervised), "calibration": len(calibration), "outer_test": len(outer_test)},
            "encoder_history_cutoff": history.timestamp.max().isoformat(),
            "supervised_cutoff": supervised.timestamp.max().isoformat(),
            "calibration_cutoff": calibration.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "evaluation_protocol": "common_random_numbers",
            "probability_protocol": "v2_t0b_timestamp_grouped_isotonic",
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "result": {
            "method": f"gnn_guided_objective_ablation_{arm}",
            "selection_objective": score_payload(selected),
            "full_objective_evaluation": decomposition["full"],
            "selection_seconds": round(selection_seconds, 3),
        },
        "objective_decomposition": decomposition,
        "reference": {
            "run_id": identifier,
            "method": reference["result"]["method"],
            "top_k": reference["result"]["top_k"],
            "full_objective": {
                "mean_spread": reference["result"]["mean_spread"],
                "spread_std": reference["result"]["spread_std"],
                "robust_objective": reference["result"]["robust_objective"],
                "community_coverage": reference["result"]["community_coverage"],
            },
        },
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }


def method_row(identifier: str, result: dict) -> dict:
    values = result["result"]["full_objective_evaluation"]
    return {
        "run_id": identifier,
        "train_fraction": result["config"]["train_fraction"],
        "random_seed": result["config"]["random_seed"],
        "arm": result["arm"],
        "method": result["result"]["method"],
        "mean_spread": values["mean_spread"],
        "spread_std": values["spread_std"],
        "robust_objective": values["robust_objective"],
        "community_coverage": values["community_coverage"],
        "runtime_seconds": result["runtime_seconds"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-dir", default="results/large-robust-greedy-higgs-50000-v2-t0b")
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    parser.add_argument("--arms", nargs="+", choices=tuple(ARMS), default=tuple(ARMS))
    parser.add_argument("--fractions", type=float, nargs="+", default=FRACTIONS)
    parser.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if tuple(args.fractions) != FRACTIONS or tuple(args.seeds) != SEEDS:
        parser.error("v2-T0c requires the preregistered fractions and seeds")
    if set(args.arms) != set(ARMS):
        parser.error("v2-T0c requires exactly the three preregistered ablation arms")
    output = Path(args.output_dir)
    if "v2-t0c" not in output.name.lower():
        parser.error("The output directory name must contain v2-t0c")
    dataset_dir = Path(args.dataset)
    inputs = {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    if inputs != expected_higgs_hashes(Path(args.frozen_manifest)):
        raise ValueError("Dataset hashes differ from the frozen Higgs 50k manifest")
    reference_dir = Path(args.reference_dir)
    references = validate_reference(reference_dir)
    if args.dry_run:
        print("Dry-run passed: frozen inputs and all 30 strict v2-T0b reference artifacts verified.")
        return
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol = Path(__file__).parents[1] / "protocols" / "influence_v2_t0c_objective_ablation_preregistration.md"
    protocol_copy = output / protocol.name
    if not protocol_copy.exists():
        shutil.copy2(protocol, protocol_copy)
    dataset = load_dataset(dataset_dir)
    rows: list[dict] = []
    run_hashes: dict[str, str] = {}
    for arm in args.arms:
        arm_dir = output / arm
        arm_dir.mkdir(exist_ok=True)
        for fraction in args.fractions:
            for seed in args.seeds:
                identifier = run_id(fraction, seed)
                path = arm_dir / f"{identifier}.json"
                if path.exists():
                    if not args.resume:
                        raise FileExistsError(f"Refusing to replace existing run: {path}")
                    result = json.loads(path.read_text(encoding="utf-8"))
                else:
                    result = run_arm(dataset, arm, fraction, seed, references[identifier])
                    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"{arm}/{identifier}")
                rows.append(method_row(identifier, result))
                run_hashes[str(path.relative_to(output)).replace("\\", "/")] = sha256(path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    manifest = {
        "protocol": {protocol.name: sha256(protocol)},
        "inputs": inputs,
        "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True},
        "reference": {"directory": str(reference_dir), "manifest_sha256": sha256(reference_dir / "manifest.json")},
        "source": {
            "pipeline_v2_t0b.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0b.py"),
            "model_v2.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "model_v2.py"),
            "optimizer.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "optimizer.py"),
            "run_v2_t0c_objective_ablation.py": sha256(Path(__file__)),
        },
        "runs": run_hashes,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
