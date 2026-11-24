"""Run the separately versioned v3 fairness and sensitivity study.

The runner intentionally has no write path into any frozen v1/v2 directory.
Its reported outcomes use held-out deterministic worlds; selection worlds are
recorded separately so method selection cannot reuse the reported simulations.
"""
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


FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(42, 52))
POOL_SIZES = (60, 120, 240, 480)
RISK_LAMBDAS = (0.00, 0.35, 0.70)
COMMUNITY_WEIGHTS = (0.00, 0.25, 0.50)
REPORTING_OBJECTIVE = {"risk_lambda": 0.35, "community_weight": 0.25}
MASK64 = (1 << 64) - 1


def stable_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def world_sequence(seed: int, namespace: int, count: int) -> list[int]:
    generator = np.random.default_rng(np.random.SeedSequence([seed, namespace, 3]))
    return [int(value) for value in generator.integers(0, 2**63 - 1, size=count)]


def uniform(world_seed: int, step: int, source: int, target: int) -> float:
    """Return one process-independent uniform for a canonical edge-time trial."""
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


def simulate_ic_common_world(graph, seeds: list[str], probabilities: dict[tuple[str, str], float], horizon: int, world: int, codes: dict[str, int]) -> int:
    active, frontier = set(seeds), set(seeds)
    for step in range(horizon):
        next_frontier: set[str] = set()
        for source in sorted(frontier, key=codes.__getitem__):
            for target in sorted(graph.successors(source), key=codes.__getitem__):
                if target in active:
                    continue
                if uniform(world, step, codes[source], codes[target]) < probabilities[(source, target)]:
                    active.add(target)
                    next_frontier.add(target)
        frontier = next_frontier
        if not frontier:
            break
    return len(active)


def score(graph, probabilities: dict[tuple[str, str], float], communities: dict[str, int], nodes: list[str], config: AnalysisConfig, terms: dict[str, float], worlds: list[int], codes: dict[str, int]) -> dict[str, object]:
    values = [simulate_ic_common_world(graph, nodes, probabilities, config.horizon, world, codes) for world in worlds]
    mean, std = float(np.mean(values)), float(np.std(values))
    coverage = len({communities[node] for node in nodes})
    return {
        "top_k": list(nodes),
        "mean_spread": round(mean, 6),
        "spread_std": round(std, 6),
        "robust_objective": round(mean - terms["risk_lambda"] * std + terms["community_weight"] * coverage, 6),
        "community_coverage": coverage,
    }


def select_robust_greedy(graph, probabilities: dict[tuple[str, str], float], communities: dict[str, int], candidates: list[str], config: AnalysisConfig, terms: dict[str, float], worlds: list[int], codes: dict[str, int]) -> dict[str, object]:
    if not candidates:
        raise ValueError("Robust greedy search received an empty candidate set")
    selected: list[str] = []
    for _ in range(min(config.seed_count, len(candidates))):
        best: dict[str, object] | None = None
        for node in candidates:
            if node in selected:
                continue
            trial = score(graph, probabilities, communities, selected + [node], config, terms, worlds, codes)
            if best is None or float(trial["robust_objective"]) > float(best["robust_objective"]):
                best = trial
        assert best is not None
        selected = list(best["top_k"])
    return score(graph, probabilities, communities, selected, config, terms, worlds, codes)


def overlap(left: list[str], right: list[str]) -> dict[str, float | int]:
    shared = len(set(left).intersection(right))
    union = len(set(left).union(right))
    return {"shared_seed_count": shared, "jaccard": round(shared / union if union else 1.0, 6)}


def selected_and_evaluated(graph, probabilities, communities, candidates: list[str], config: AnalysisConfig, selection_terms: dict[str, float], selection_worlds: list[int], evaluation_worlds: list[int], codes: dict[str, int]) -> dict[str, object]:
    started = time.perf_counter()
    selected = select_robust_greedy(graph, probabilities, communities, candidates, config, selection_terms, selection_worlds, codes)
    return {
        "selection_terms": dict(selection_terms),
        "candidate_count": len(candidates),
        "selection": selected,
        "reporting_evaluation": score(graph, probabilities, communities, list(selected["top_k"]), config, REPORTING_OBJECTIVE, evaluation_worlds, codes),
        "selection_seconds": round(time.perf_counter() - started, 6),
    }


def run_one(
    dataset: NetworkDataset,
    fraction: float,
    seed: int,
    full_candidate_limit: int | None = None,
    screened_candidate_limit: int = 120,
    pool_sizes: tuple[int, ...] = POOL_SIZES,
) -> dict[str, object]:
    started = time.perf_counter()
    config = AnalysisConfig(
        seed_count=2, horizon=4, risk_lambda=REPORTING_OBJECTIVE["risk_lambda"],
        community_weight=REPORTING_OBJECTIVE["community_weight"], diffusion_model="ic",
        random_seed=seed, epochs=10, ants=3, iterations=2, simulations=20,
        train_fraction=fraction, optimizer="robust_greedy", candidate_pool_size=120,
    )
    history, supervised, calibration, outer_test, outer_train = _windows(dataset, fraction)
    if not (history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min()):
        raise AssertionError("v3 timestamp-grouped windows are not strictly ordered")
    snapshot = build_snapshot(dataset, outer_train)
    probabilities, uses_pyg = t0._calibrated_probabilities(dataset, history, supervised, calibration, snapshot, seed)
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Every v3 decision edge must receive a calibrated probability")
    prior = t0._node_prior(snapshot.graph, probabilities)
    ranked = sorted(prior, key=lambda node: (-prior[node], str(node)))
    full_candidates = sorted(snapshot.graph.nodes, key=str)
    if full_candidate_limit is not None:
        full_candidates = full_candidates[:full_candidate_limit]
    selection_worlds = world_sequence(seed, 101, config.simulations)
    evaluation_worlds = world_sequence(seed, 202, config.simulations)
    if set(selection_worlds).intersection(evaluation_worlds):
        raise AssertionError("Selection and evaluation worlds must be disjoint")
    codes = {node: position for position, node in enumerate(sorted(snapshot.graph.nodes, key=str))}

    screened_candidates = ranked[: min(screened_candidate_limit, len(ranked))]
    screened = selected_and_evaluated(
        snapshot.graph, probabilities, snapshot.communities,
        screened_candidates, config, REPORTING_OBJECTIVE,
        selection_worlds, evaluation_worlds, codes,
    )
    full = selected_and_evaluated(
        snapshot.graph, probabilities, snapshot.communities, full_candidates,
        config, REPORTING_OBJECTIVE, selection_worlds, evaluation_worlds, codes,
    )
    gnn_top_k = score(
        snapshot.graph, probabilities, snapshot.communities, ranked[:config.seed_count],
        config, REPORTING_OBJECTIVE, evaluation_worlds, codes,
    )
    pool_sensitivity: dict[str, object] = {}
    for pool in pool_sizes:
        result = selected_and_evaluated(
            snapshot.graph, probabilities, snapshot.communities,
            ranked[: min(pool, len(ranked))], config, REPORTING_OBJECTIVE,
            selection_worlds, evaluation_worlds, codes,
        )
        result["overlap_with_full_candidate"] = overlap(list(result["selection"]["top_k"]), list(full["selection"]["top_k"]))
        pool_sensitivity[str(pool)] = result
    weight_sensitivity: dict[str, object] = {}
    for risk_lambda in RISK_LAMBDAS:
        for community_weight in COMMUNITY_WEIGHTS:
            terms = {"risk_lambda": risk_lambda, "community_weight": community_weight}
            key = f"risk-{risk_lambda:.2f}_community-{community_weight:.2f}"
            result = selected_and_evaluated(
                snapshot.graph, probabilities, snapshot.communities,
                screened_candidates, config, terms,
                selection_worlds, evaluation_worlds, codes,
            )
            result["overlap_with_base_screened"] = overlap(list(result["selection"]["top_k"]), list(screened["selection"]["top_k"]))
            weight_sensitivity[key] = result

    return {
        "study_version": "v3-fairness-sensitivity",
        "config": asdict(config),
        "reporting_objective": REPORTING_OBJECTIVE,
        "reproducibility": {
            "random_seed": seed,
            "train_fraction": fraction,
            "achieved_outer_train_fraction": len(outer_train) / len(dataset.edges),
            "window_rows": {"history": len(history), "supervised": len(supervised), "calibration": len(calibration), "outer_test": len(outer_test)},
            "encoder_history_cutoff": history.timestamp.max().isoformat(),
            "supervised_cutoff": supervised.timestamp.max().isoformat(),
            "calibration_cutoff": calibration.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "probability_protocol": "v2_t0b_timestamp_grouped_isotonic",
            "diffusion_protocol": "v3_canonical_edge_time_common_worlds",
            "selection_worlds_sha256": stable_digest(selection_worlds),
            "evaluation_worlds_sha256": stable_digest(evaluation_worlds),
            "selection_evaluation_worlds_disjoint": True,
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "methods": {
            "screened_robust_greedy": screened,
            "full_candidate_robust_greedy": {**full, "selection_scope": "full_decision_graph" if full_candidate_limit is None else f"smoke_prefix_{full_candidate_limit}"},
            "gnn_top_k_protected_lower_bound_audit": {
                "candidate_count": config.seed_count,
                "reporting_evaluation": gnn_top_k,
                "interpretation": "protected_lower_bound_audit_not_independent_baseline",
            },
            "candidate_pool_sensitivity": pool_sensitivity,
            "objective_weight_sensitivity": weight_sensitivity,
        },
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }


def run_id(fraction: float, seed: int) -> str:
    return f"split-{fraction:.2f}-seed-{seed}"


def metric_rows(identifier: str, artifact: dict[str, object]) -> list[dict[str, object]]:
    methods = artifact["methods"]
    records: list[tuple[str, dict[str, object]]] = [
        ("screened_robust_greedy", methods["screened_robust_greedy"]),
        ("full_candidate_robust_greedy", methods["full_candidate_robust_greedy"]),
        ("gnn_top_k_protected_lower_bound_audit", methods["gnn_top_k_protected_lower_bound_audit"]),
    ]
    records.extend((f"screened_pool_{pool}", values) for pool, values in methods["candidate_pool_sensitivity"].items())
    records.extend((f"objective_{name}", values) for name, values in methods["objective_weight_sensitivity"].items())
    rows = []
    for name, values in records:
        evaluation = values["reporting_evaluation"]
        rows.append({
            "run_id": identifier, "train_fraction": artifact["config"]["train_fraction"],
            "random_seed": artifact["config"]["random_seed"], "method": name,
            "mean_spread": evaluation["mean_spread"], "spread_std": evaluation["spread_std"],
            "robust_objective": evaluation["robust_objective"], "community_coverage": evaluation["community_coverage"],
            "top_k": json.dumps(evaluation["top_k"], ensure_ascii=False),
            "selection_seconds": values.get("selection_seconds", 0.0),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=list(FRACTIONS))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if "v3" not in output.name.lower():
        parser.error("The output directory name must contain v3")
    inputs = {name: sha256(Path(args.dataset) / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    if inputs != expected_higgs_hashes(Path(args.frozen_manifest)):
        raise ValueError("Dataset hashes differ from the frozen Higgs 50k manifest")
    dataset = load_dataset(args.dataset)
    for fraction in args.fractions:
        history, supervised, calibration, outer_test, _ = _windows(dataset, fraction)
        if not (history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min()):
            raise AssertionError(f"Timestamp ordering failed for fraction {fraction:.2f}")
    if args.dry_run:
        print("Dry-run passed: frozen inputs and strict timestamp windows verified; no output written.")
        return
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    if args.smoke:
        fractions, seeds, full_candidate_limit = [args.fractions[0]], [args.seeds[0]], 64
        screened_candidate_limit, pool_sizes = 64, (16, 32, 64)
    else:
        fractions, seeds, full_candidate_limit = args.fractions, args.seeds, None
        screened_candidate_limit, pool_sizes = 120, POOL_SIZES
    output.mkdir(parents=True, exist_ok=True)
    protocol = Path(__file__).parents[1] / "protocols" / "influence_v3_fairness_sensitivity_preregistration.md"
    if not (output / protocol.name).exists():
        shutil.copy2(protocol, output / protocol.name)
    rows: list[dict[str, object]] = []
    run_hashes: dict[str, str] = {}
    for fraction in fractions:
        for seed in seeds:
            identifier = run_id(fraction, seed)
            path = output / f"{identifier}.json"
            if path.exists():
                if not args.resume:
                    raise FileExistsError(f"Refusing to replace existing run: {path}")
                artifact = json.loads(path.read_text(encoding="utf-8"))
            else:
                artifact = run_one(
                    dataset, fraction, seed, full_candidate_limit,
                    screened_candidate_limit, pool_sizes,
                )
                if args.smoke:
                    artifact["smoke_test"] = {"is_smoke": True, "full_candidate_limit": full_candidate_limit, "not_eligible_for_inference": True}
                path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
                print(identifier)
            rows.extend(metric_rows(identifier, artifact))
            run_hashes[path.name] = sha256(path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "study_version": "v3-fairness-sensitivity",
        "smoke_test": bool(args.smoke),
        "protocol": {protocol.name: sha256(protocol)},
        "inputs": inputs,
        "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True},
        "source": {
            "run_v3_fairness_sensitivity.py": sha256(Path(__file__)),
            "pipeline_v2_t0.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0.py"),
            "pipeline_v2_t0b.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0b.py"),
            "model_v2.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "model_v2.py"),
        },
        "run_parameters": {
            "fractions": fractions, "seeds": seeds,
            "full_candidate_limit": full_candidate_limit,
            "screened_candidate_limit": screened_candidate_limit,
            "pool_sizes": pool_sizes,
        },
        "runs": run_hashes,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
