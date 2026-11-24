"""Frozen confirmation runner for simulation-resolution candidate-pool profiles.

This module is deliberately restricted to the CC0 SocioPatterns confirmation
instances. It evaluates simulated IC on bidirectional contact-derived graphs;
it never treats the source contacts as observed information cascades.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.validation import load_dataset
from experiments.v7_exact_search import CandidateEvaluator, SimulationCache, full_greedy
from experiments.v8_candidate_truncation_development import compact, first_divergence, ranked_weighted_degree
from experiments.v8_candidate_truncation_preflight import build_history_graph, grouped_history, sha256


STUDY = "sociopatterns-resolution-confirmation-v0_1"
DATA_ROOT = Path(os.environ.get("IM_CONFIRMATION_DATA_ROOT", ROOT / "data" / "processed" / "sociopatterns-confirmation-v0_1"))
DATASETS = ("invs2013", "invs2015", "sfhh2009", "kenya2012")
WORLD_PATHS = (301, 302)
WORLD_COUNTS = (20, 80, 320)
POOLS = (2, 4, 8)
PROBABILITY = 0.01
HORIZON = 3
EVALUATION_WORLDS = 2000


def world_ids(dataset: str, path: int, family: str, count: int) -> tuple[int, ...]:
    if dataset not in DATASETS or path not in WORLD_PATHS or family not in {"selection", "evaluation"} or count <= 0:
        raise ValueError("invalid world specification")
    values = tuple(int.from_bytes(hashlib.sha256(f"{STUDY}|{dataset}|{path}|{family}|{index}".encode()).digest()[:8], "big") & ((1 << 63) - 1) for index in range(count))
    if len(set(values)) != len(values):
        raise AssertionError("world collision")
    return values


def _graph(dataset: str):
    loaded = load_dataset(DATA_ROOT / dataset)
    history, cutoff, groups = grouped_history(loaded.edges)
    graph, communities, _, metadata = build_history_graph(history)
    probabilities = {(source, target): PROBABILITY for source, targets in graph.items() for target in targets}
    return loaded, history, cutoff, groups, graph, communities, probabilities, metadata


def _evaluate(graph, probabilities, codes, seed_set, independent_worlds):
    started = time.perf_counter()
    evaluator = CandidateEvaluator(graph, probabilities, HORIZON, codes, SimulationCache())
    values = evaluator.values(seed_set, independent_worlds)
    mean = sum(values) / len(values)
    return {
        "mean_spread": round(mean, 6),
        "population_sd": round(math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)), 6),
        "world_spreads": values,
        "world_spreads_sha256": hashlib.sha256(json.dumps(values).encode()).hexdigest(),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


def run_preflight(dataset: str, seed_budget: int, selection_world_count: int = 4) -> dict:
    if seed_budget not in {5, 20}:
        raise ValueError("seed budget must be 5 or 20")
    loaded, history, cutoff, groups, graph, communities, probabilities, metadata = _graph(dataset)
    started = time.perf_counter()
    result = full_greedy(graph, probabilities, communities, world_ids(dataset, 301, "selection", selection_world_count), horizon=HORIZON, seed_count=seed_budget, codes={node: index for index, node in enumerate(sorted(graph))}, risk_lambda=0, community_weight=0)
    return {
        "schema": "sociopatterns-resolution-preflight-0.1",
        "study": STUDY,
        "dataset": dataset,
        "outcome_blind": True,
        "status": "COMPLETED_NO_SELECTION_RECORDED",
        "config": {"p": PROBABILITY, "horizon": HORIZON, "k": seed_budget, "selection_world_count": selection_world_count},
        "input_sha256": {name: sha256(DATA_ROOT / dataset / name) for name in ("nodes.csv", "edges.csv", "cascades.csv", "data_card.json")},
        "history_cutoff": cutoff,
        "timestamp_group_count": groups,
        "graph": metadata,
        "candidate_world_evaluations": result["world_evaluations"],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "warnings": loaded.warnings,
    }


def run_condition(dataset: str, path: int, seed_budget: int, selection_world_count: int) -> dict:
    if seed_budget not in {5, 20} or selection_world_count not in WORLD_COUNTS:
        raise ValueError("condition outside frozen matrix")
    loaded, history, cutoff, groups, graph, communities, probabilities, metadata = _graph(dataset)
    codes = {node: index for index, node in enumerate(sorted(graph))}
    selection = world_ids(dataset, path, "selection", selection_world_count)
    evaluation = world_ids(dataset, path, "evaluation", EVALUATION_WORLDS)
    degree = ranked_weighted_degree(history, graph)
    candidates = {"full": tuple(sorted(graph))}
    candidates.update({f"degree_{factor}k": tuple(degree[: min(len(graph), factor * seed_budget)]) for factor in POOLS})
    arms = {}
    for method, universe in candidates.items():
        started = time.perf_counter()
        result = full_greedy(graph, probabilities, communities, selection, horizon=HORIZON, seed_count=seed_budget, codes=codes, risk_lambda=0, community_weight=0, candidate_universe=universe)
        arms[method] = {"candidate_count": len(universe), "selection": compact(result), "evaluation": _evaluate(graph, probabilities, codes, result["selected"], evaluation), "decision_seconds": round(time.perf_counter() - started, 6)}
    reference = arms["full"]["selection"]["top_k"]
    reference_mean = arms["full"]["evaluation"]["mean_spread"]
    for arm in arms.values():
        arm["comparison_to_full"] = {"same_ordered_top_k": arm["selection"]["top_k"] == reference, "first_divergence": first_divergence(reference, arm["selection"]["top_k"]), "mean_spread_delta": round(arm["evaluation"]["mean_spread"] - reference_mean, 6)}
    return {
        "schema": "sociopatterns-resolution-condition-0.1",
        "study": STUDY,
        "confirmation_data": True,
        "simulation_only": True,
        "dataset": dataset,
        "world_path": path,
        "k": seed_budget,
        "selection_world_count": selection_world_count,
        "selection_world_sha256": hashlib.sha256(json.dumps(selection).encode()).hexdigest(),
        "evaluation_world_count": EVALUATION_WORLDS,
        "evaluation_world_sha256": hashlib.sha256(json.dumps(evaluation).encode()).hexdigest(),
        "config": {"p": PROBABILITY, "horizon": HORIZON},
        "history_cutoff": cutoff,
        "timestamp_group_count": groups,
        "graph": metadata,
        "input_sha256": {name: sha256(DATA_ROOT / dataset / name) for name in ("nodes.csv", "edges.csv", "cascades.csv", "data_card.json")},
        "arms": arms,
        "source_semantic_limit": "bidirectional contact-derived topology; no observed information cascades",
        "warnings": loaded.warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "condition"), required=True)
    parser.add_argument("--dataset", choices=DATASETS, required=True)
    parser.add_argument("--k", type=int, choices=(5, 20), required=True)
    parser.add_argument("--world-path", type=int, choices=WORLD_PATHS, default=301)
    parser.add_argument("--selection-worlds", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = run_preflight(args.dataset, args.k, args.selection_worlds) if args.mode == "preflight" else run_condition(args.dataset, args.world_path, args.k, args.selection_worlds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": args.mode, "dataset": args.dataset, "status": report["status"] if args.mode == "preflight" else "COMPLETED"}))


if __name__ == "__main__":
    main()
