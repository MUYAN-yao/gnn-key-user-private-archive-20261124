"""Run v2-T0d objective ablation with shared learned probabilities and worlds."""
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

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app import pipeline_v2_t0 as t0
from app.contracts import AnalysisConfig
from app.graph import build_snapshot
from app.pipeline_v2_t0b import _windows
from app.validation import NetworkDataset, load_dataset
from run_rolling_study_v2_t0 import expected_higgs_hashes, sha256
from run_v2_t0c_objective_ablation import REFERENCE_METHOD, validate_reference


FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(42, 52))
FULL = {"risk_lambda": 0.35, "community_weight": 0.25}
ARMS = {
    "full": FULL,
    "risk_off": {"risk_lambda": 0.00, "community_weight": 0.25},
    "community_off": {"risk_lambda": 0.35, "community_weight": 0.00},
    "spread_only": {"risk_lambda": 0.00, "community_weight": 0.00},
}
MASK64 = (1 << 64) - 1


def run_id(fraction: float, seed: int) -> str:
    return f"split-{fraction:.2f}-seed-{seed}"


def _uniform(world_seed: int, step: int, source: int, target: int) -> float:
    """Process-independent uniform for one edge-time trial."""
    value = (
        (world_seed + 0x9E3779B97F4A7C15)
        ^ ((step + 1) * 0xBF58476D1CE4E5B9)
        ^ ((source + 1) * 0x94D049BB133111EB)
        ^ ((target + 1) * 0xD2B74407B1CE6E93)
    ) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    return (value >> 11) * (1.0 / (1 << 53))


def simulate_ic_common_world(
    graph, seeds: list[str], probabilities: dict[tuple[str, str], float], horizon: int,
    world_seed: int, node_codes: dict[str, int],
) -> int:
    active = set(seeds)
    frontier = set(seeds)
    for step in range(horizon):
        next_frontier: set[str] = set()
        for source in sorted(frontier, key=node_codes.__getitem__):
            for target in sorted(graph.successors(source), key=node_codes.__getitem__):
                if target in active:
                    continue
                if _uniform(world_seed, step, node_codes[source], node_codes[target]) < probabilities[(source, target)]:
                    active.add(target)
                    next_frontier.add(target)
        frontier = next_frontier
        if not frontier:
            break
    return len(active)


def score(
    graph, probabilities: dict[tuple[str, str], float], communities: dict[str, int],
    nodes: list[str], config: AnalysisConfig, terms: dict[str, float], worlds: list[int], node_codes: dict[str, int],
) -> dict:
    values = [
        simulate_ic_common_world(graph, nodes, probabilities, config.horizon, world, node_codes)
        for world in worlds
    ]
    mean, std = float(np.mean(values)), float(np.std(values))
    coverage = len({communities[node] for node in nodes})
    return {
        "top_k": list(nodes), "mean_spread": round(mean, 3), "spread_std": round(std, 3),
        "robust_objective": round(mean - terms["risk_lambda"] * std + terms["community_weight"] * coverage, 3),
        "community_coverage": coverage,
    }


def select(
    graph, probabilities: dict[tuple[str, str], float], prior: dict[str, float], communities: dict[str, int],
    config: AnalysisConfig, terms: dict[str, float], worlds: list[int], node_codes: dict[str, int],
) -> dict:
    ranked = sorted(prior, key=lambda node: (-prior[node], str(node)))
    candidates = ranked[: min(max(config.seed_count, config.candidate_pool_size), len(ranked))]
    if not candidates:
        raise ValueError("Cannot optimize an empty candidate pool")
    selected: list[str] = []
    for _ in range(min(config.seed_count, len(candidates))):
        best_step: dict | None = None
        for node in candidates:
            if node in selected:
                continue
            trial = score(graph, probabilities, communities, selected + [node], config, terms, worlds, node_codes)
            # Match the original strict-greedy tie rule: ranked candidate order
            # wins when objectives are exactly equal.
            if best_step is None or trial["robust_objective"] > best_step["robust_objective"]:
                best_step = trial
        assert best_step is not None
        selected = best_step["top_k"]
    greedy = score(graph, probabilities, communities, selected, config, terms, worlds, node_codes)
    gnn = score(graph, probabilities, communities, candidates[: config.seed_count], config, terms, worlds, node_codes)
    return greedy if greedy["robust_objective"] > gnn["robust_objective"] else gnn


def run_one(dataset: NetworkDataset, fraction: float, seed: int, archived_reference: dict) -> dict:
    started = time.perf_counter()
    config = AnalysisConfig(
        seed_count=2, horizon=4, risk_lambda=FULL["risk_lambda"], community_weight=FULL["community_weight"],
        diffusion_model="ic", random_seed=seed, epochs=10, ants=3, iterations=2, simulations=20,
        train_fraction=fraction, optimizer="robust_greedy", candidate_pool_size=120,
    )
    history, supervised, calibration, outer_test, outer_train = _windows(dataset, fraction)
    if not (history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min()):
        raise AssertionError("v2-T0d timestamp windows are not strictly ordered")
    snapshot = build_snapshot(dataset, outer_train)
    probabilities, uses_pyg = t0._calibrated_probabilities(dataset, history, supervised, calibration, snapshot, seed)
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Every decision edge must receive a calibrated probability")
    prior = t0._node_prior(snapshot.graph, probabilities)
    worlds = [int(value) for value in np.random.default_rng(seed).integers(0, 2**31, size=config.simulations)]
    node_codes = {node: index for index, node in enumerate(sorted(snapshot.graph.nodes, key=str))}
    arms: dict[str, dict] = {}
    for name, terms in ARMS.items():
        selection_started = time.perf_counter()
        selected = select(snapshot.graph, probabilities, prior, snapshot.communities, config, terms, worlds, node_codes)
        full_score = score(snapshot.graph, probabilities, snapshot.communities, selected["top_k"], config, FULL, worlds, node_codes)
        arms[name] = {
            "selection_objective": selected,
            "full_objective_evaluation": full_score,
            "selection_seconds": round(time.perf_counter() - selection_started, 3),
        }
    archived_seeds = archived_reference["result"]["top_k"]
    return {
        "config": asdict(config), "reporting_objective": FULL,
        "reproducibility": {
            "random_seed": seed, "train_fraction": fraction,
            "achieved_outer_train_fraction": len(outer_train) / len(dataset.edges),
            "window_rows": {"history": len(history), "supervised": len(supervised), "calibration": len(calibration), "outer_test": len(outer_test)},
            "encoder_history_cutoff": history.timestamp.max().isoformat(), "supervised_cutoff": supervised.timestamp.max().isoformat(),
            "calibration_cutoff": calibration.timestamp.max().isoformat(), "outer_test_start": outer_test.timestamp.min().isoformat(),
            "probability_protocol": "v2_t0b_timestamp_grouped_isotonic",
            "evaluation_protocol": "v2_t0d_deterministic_edge_time_common_worlds",
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "arms": arms,
        "v2_t0b_reference_audit": {
            "method": REFERENCE_METHOD, "top_k": archived_seeds,
            "full_selection_matches_archived_v2_t0b": arms["full"]["selection_objective"]["top_k"] == archived_seeds,
        },
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }


def metric_rows(identifier: str, result: dict) -> list[dict]:
    return [
        {
            "run_id": identifier, "train_fraction": result["config"]["train_fraction"],
            "random_seed": result["config"]["random_seed"], "arm": arm,
            "method": f"gnn_guided_objective_ablation_{arm}",
            "mean_spread": values["full_objective_evaluation"]["mean_spread"],
            "spread_std": values["full_objective_evaluation"]["spread_std"],
            "robust_objective": values["full_objective_evaluation"]["robust_objective"],
            "community_coverage": values["full_objective_evaluation"]["community_coverage"],
            "runtime_seconds": result["runtime_seconds"],
        }
        for arm, values in result["arms"].items()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-dir", default="results/large-robust-greedy-higgs-50000-v2-t0b")
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if "v2-t0d" not in output.name.lower():
        parser.error("The output directory name must contain v2-t0d")
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
    protocol = Path(__file__).parents[1] / "protocols" / "influence_v2_t0d_common_world_objective_ablation_preregistration.md"
    if not (output / protocol.name).exists():
        shutil.copy2(protocol, output / protocol.name)
    dataset = load_dataset(dataset_dir)
    rows: list[dict] = []
    hashes: dict[str, str] = {}
    for fraction in FRACTIONS:
        for seed in SEEDS:
            identifier = run_id(fraction, seed)
            path = output / f"{identifier}.json"
            if path.exists():
                if not args.resume:
                    raise FileExistsError(f"Refusing to replace existing run: {path}")
                result = json.loads(path.read_text(encoding="utf-8"))
            else:
                result = run_one(dataset, fraction, seed, references[identifier])
                path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(identifier)
            rows.extend(metric_rows(identifier, result))
            hashes[path.name] = sha256(path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    manifest = {
        "protocol": {protocol.name: sha256(protocol)}, "inputs": inputs,
        "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True},
        "reference": {"directory": str(reference_dir), "manifest_sha256": sha256(reference_dir / "manifest.json")},
        "source": {
            "pipeline_v2_t0b.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0b.py"),
            "pipeline_v2_t0.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0.py"),
            "model_v2.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "model_v2.py"),
            "run_v2_t0d_common_world_objective_ablation.py": sha256(Path(__file__)),
        }, "runs": hashes,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
