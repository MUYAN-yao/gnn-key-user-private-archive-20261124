"""Nested-W development diagnostic for full and degree-truncated greedy IM."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.validation import load_dataset
from experiments.v7_exact_search import CandidateEvaluator, SimulationCache, full_greedy
from experiments.v8_candidate_truncation_preflight import DATASETS, HORIZON, build_history_graph, grouped_history, sha256
from experiments.v8_candidate_truncation_development import compact, first_divergence, ranked_weighted_degree

STUDY = "candidate-truncation-resolution-development-v0_1"
SEEDS = (104, 105)
BUDGETS = (5, 20)
WORLD_COUNTS = (20, 80)
FACTORS = (2, 4, 8)
EVALUATION_WORLDS = 2000


def worlds(dataset: str, seed: int, family: str, count: int) -> tuple[int, ...]:
    values = [int.from_bytes(hashlib.sha256(f"{STUDY}|{dataset}|{seed}|{family}|{index}".encode()).digest()[:8], "big") & ((1 << 63) - 1) for index in range(count)]
    if len(set(values)) != len(values):
        raise AssertionError("world collision")
    return tuple(values)


def evaluate(graph, probabilities, codes, seeds, independent_worlds):
    started = time.perf_counter()
    evaluator = CandidateEvaluator(graph, probabilities, HORIZON, codes, SimulationCache())
    values = evaluator.values(seeds, independent_worlds)
    mean = sum(values) / len(values)
    return {"mean_spread": round(mean, 6), "population_sd": round(math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)), 6), "world_spreads": values, "sha256": hashlib.sha256(json.dumps(values).encode()).hexdigest(), "elapsed_seconds": round(time.perf_counter() - started, 6)}


def run_condition(dataset_name: str, seed: int, budget: int, selection_world_count: int) -> dict:
    started = time.perf_counter()
    dataset_dir = DATASETS[dataset_name]
    dataset = load_dataset(dataset_dir)
    history, cutoff, group_count = grouped_history(dataset.edges)
    graph, communities, probabilities, graph_metadata = build_history_graph(history)
    codes = {node: index for index, node in enumerate(sorted(graph))}
    selection_worlds = worlds(dataset_name, seed, "selection", selection_world_count)
    independent_worlds = worlds(dataset_name, seed, "evaluation", EVALUATION_WORLDS)
    degree_order = ranked_weighted_degree(history, graph)
    methods = {"full": tuple(sorted(graph))}
    methods.update({f"degree_{factor}k": tuple(degree_order[: min(len(graph), factor * budget)]) for factor in FACTORS})
    arms = {}
    for method, candidates in methods.items():
        decision_started = time.perf_counter()
        result = full_greedy(graph, probabilities, communities, selection_worlds, horizon=HORIZON, seed_count=budget, codes=codes, risk_lambda=0, community_weight=0, candidate_universe=candidates)
        decision_seconds = time.perf_counter() - decision_started
        arms[method] = {"candidate_count": len(candidates), "selection": compact(result), "evaluation": evaluate(graph, probabilities, codes, result["selected"], independent_worlds), "decision_seconds": round(decision_seconds, 6)}
    full_top_k = arms["full"]["selection"]["top_k"]
    full_mean = arms["full"]["evaluation"]["mean_spread"]
    for arm in arms.values():
        arm["comparison_to_full"] = {"same_ordered_top_k": arm["selection"]["top_k"] == full_top_k, "first_divergence": first_divergence(full_top_k, arm["selection"]["top_k"]), "mean_spread_delta": round(arm["evaluation"]["mean_spread"] - full_mean, 6)}
    return {"schema": "candidate-truncation-resolution-condition-0.1", "study": STUDY, "development_only": True, "dataset": dataset_name, "seed": seed, "k": budget, "selection_world_count": selection_world_count, "selection_world_sha256": hashlib.sha256(json.dumps(selection_worlds).encode()).hexdigest(), "evaluation_world_count": EVALUATION_WORLDS, "evaluation_world_sha256": hashlib.sha256(json.dumps(independent_worlds).encode()).hexdigest(), "history_cutoff": cutoff, "timestamp_group_count": group_count, "graph": graph_metadata, "input_sha256": {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}, "degree_full_winner_ranks": [degree_order.index(node) + 1 for node in full_top_k], "arms": arms, "elapsed_seconds": round(time.perf_counter() - started, 6)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--k", type=int, choices=BUDGETS, required=True)
    parser.add_argument("--selection-worlds", type=int, choices=WORLD_COUNTS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = run_condition(args.dataset, args.seed, args.k, args.selection_worlds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "elapsed_seconds": report["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
