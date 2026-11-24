"""Development-only quality--cost block for candidate-truncation evaluation.

The runner compares existing ranking/truncation heuristics against an exact
finite-world full reference under *standard mean-spread* influence
maximization.  It is not a new-method runner: no learned pruning or v7 bound
arm is included.  Each invocation writes exactly one immutable block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Sequence

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.validation import load_dataset
from experiments.v7_exact_search import CandidateEvaluator, SimulationCache, full_greedy
from experiments.v8_candidate_truncation_preflight import (
    DATASETS,
    HISTORY_FRACTION,
    HORIZON,
    PROBABILITY,
    SEED_BUDGET,
    build_history_graph,
    grouped_history,
    sha256,
)


STUDY = "candidate-truncation-development-v0_2"
POOL_FACTORS = (1, 2, 4, 8, 16)
METHOD_IDS = ("full",) + tuple(f"degree_{factor}k" for factor in POOL_FACTORS) + tuple(
    f"pagerank_{factor}k" for factor in POOL_FACTORS
) + ("degree_doubling",)


def worlds(dataset_name: str, block_seed: int, family: str, count: int) -> tuple[int, ...]:
    if family not in {"selection", "evaluation"} or count <= 0:
        raise ValueError("invalid world family or count")
    values = []
    for index in range(count):
        payload = f"{STUDY}|{dataset_name}|{block_seed}|{family}|{index}".encode("utf-8")
        values.append(int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & ((1 << 63) - 1))
    if len(set(values)) != len(values):
        raise AssertionError("world collision")
    return tuple(values)


def ranked_weighted_degree(history, graph: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    counts = history.loc[history.src != history.dst].groupby("src").size().to_dict()
    return tuple(sorted(graph, key=lambda node: (-int(counts.get(node, 0)), node)))


def ranked_pagerank(graph: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    nx_graph = nx.DiGraph(graph)
    scores = nx.pagerank(nx_graph, weight=None)
    return tuple(sorted(graph, key=lambda node: (-float(scores[node]), node)))


def pool(ranking: Sequence[str], factor: int, seed_budget: int) -> tuple[str, ...]:
    return tuple(ranking[: min(len(ranking), factor * seed_budget)])


def compact(result: dict) -> dict:
    round_diagnostics = []
    for row in result["rounds"]:
        ordered = sorted(row["scores"].items(), key=lambda item: (-item[1], item[0]))
        winner_score = ordered[0][1]
        runner_up = ordered[1] if len(ordered) > 1 else None
        round_diagnostics.append({
            "winner": row["winner"],
            "winner_score_micro": winner_score,
            "runner_up": runner_up[0] if runner_up else None,
            "winner_margin_micro": winner_score - runner_up[1] if runner_up else None,
            "exact_best_tie_count": sum(score == winner_score for _, score in ordered),
        })
    return {
        "top_k": result["selected"],
        "rounds": round_diagnostics,
        "candidate_world_evaluations": result["world_evaluations"],
        "cache_hits": result["cache"].hits,
        "cache_misses": result["cache"].misses,
    }


def evaluate(graph, probabilities, codes, seeds: Sequence[str], worlds_for_evaluation: Sequence[int]) -> dict:
    started = time.perf_counter()
    evaluator = CandidateEvaluator(graph, probabilities, HORIZON, codes, SimulationCache())
    values = evaluator.values(seeds, worlds_for_evaluation)
    mean = sum(values) / len(values)
    population_sd = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))
    return {
        "mean_spread": round(mean, 6),
        "population_sd": round(population_sd, 6),
        "world_spreads_sha256": hashlib.sha256(json.dumps(values).encode("utf-8")).hexdigest(),
        "world_spreads": values,
        "world_count": len(values),
        "candidate_world_evaluations": evaluator.calls,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


def first_divergence(reference: Sequence[str], observed: Sequence[str]) -> int | None:
    for index, (left, right) in enumerate(zip(reference, observed), start=1):
        if left != right:
            return index
    return None if len(reference) == len(observed) else min(len(reference), len(observed)) + 1


def _run_fixed(graph, probabilities, communities, selection_worlds, codes, candidates, seed_budget):
    return full_greedy(
        graph, probabilities, communities, selection_worlds,
        horizon=HORIZON, seed_count=seed_budget, codes=codes,
        risk_lambda=0, community_weight=0, candidate_universe=candidates,
    )


def _run_doubling(graph, probabilities, communities, selection_worlds, codes, ranking, seed_budget):
    trace = []
    previous: list[str] | None = None
    final = None
    for factor in POOL_FACTORS:
        candidates = pool(ranking, factor, seed_budget)
        current = _run_fixed(graph, probabilities, communities, selection_worlds, codes, candidates, seed_budget)
        trace.append({"factor": factor, "candidate_count": len(candidates), "top_k": current["selected"]})
        final = current
        if previous == current["selected"]:
            return final, trace, "two_consecutive_equal"
        previous = list(current["selected"])
        if len(candidates) == len(graph):
            return final, trace, "full_candidate_reached"
    assert final is not None
    return final, trace, "largest_pool_reached"


def run_block(dataset_name: str, block_seed: int, seed_budget: int, selection_count: int, evaluation_count: int) -> dict:
    if dataset_name not in DATASETS:
        raise ValueError("development dataset is not registered")
    if seed_budget not in {5, 20}:
        raise ValueError("seed_budget must be 5 or 20")
    block_started = time.perf_counter()
    dataset_dir = DATASETS[dataset_name]
    dataset = load_dataset(dataset_dir)
    history, cutoff, timestamp_groups = grouped_history(dataset.edges)
    graph, communities, probabilities, graph_metadata = build_history_graph(history)
    codes = {node: index for index, node in enumerate(sorted(graph))}
    selection = worlds(dataset_name, block_seed, "selection", selection_count)
    evaluation = worlds(dataset_name, block_seed, "evaluation", evaluation_count)
    common_seconds = time.perf_counter() - block_started
    started = time.perf_counter()
    degree_order = ranked_weighted_degree(history, graph)
    degree_seconds = time.perf_counter() - started
    started = time.perf_counter()
    pagerank_order = ranked_pagerank(graph)
    pagerank_seconds = time.perf_counter() - started
    rankings = {"degree": degree_order, "pagerank": pagerank_order}
    ranking_seconds = {"degree": degree_seconds, "pagerank": pagerank_seconds}
    arms: dict[str, dict] = {}

    full_started = time.perf_counter()
    full_result = _run_fixed(graph, probabilities, communities, selection, codes, tuple(sorted(graph)), seed_budget)
    full_decision = time.perf_counter() - full_started
    full_evaluation = evaluate(graph, probabilities, codes, full_result["selected"], evaluation)
    arms["full"] = {
        "method": "full",
        "candidate_count": len(graph),
        "selection": compact(full_result),
        "evaluation": full_evaluation,
        "timing": {"rank_seconds": 0.0, "decision_seconds": round(full_decision, 6), "cold_accounted_seconds": round(common_seconds + full_decision, 6)},
    }

    for ranking_name, ranking in rankings.items():
        for factor in POOL_FACTORS:
            method = f"{ranking_name}_{factor}k"
            candidates = pool(ranking, factor, seed_budget)
            started = time.perf_counter()
            result = _run_fixed(graph, probabilities, communities, selection, codes, candidates, seed_budget)
            decision_seconds = time.perf_counter() - started
            evaluation_result = evaluate(graph, probabilities, codes, result["selected"], evaluation)
            arms[method] = {
                "method": method,
                "candidate_count": len(candidates),
                "selection": compact(result),
                "evaluation": evaluation_result,
                "timing": {"rank_seconds": ranking_seconds[ranking_name], "decision_seconds": round(decision_seconds, 6), "cold_accounted_seconds": round(common_seconds + ranking_seconds[ranking_name] + decision_seconds, 6)},
            }

    started = time.perf_counter()
    result, doubling_trace, stop_reason = _run_doubling(
        graph, probabilities, communities, selection, codes, degree_order, seed_budget
    )
    decision_seconds = time.perf_counter() - started
    arms["degree_doubling"] = {
        "method": "degree_doubling",
        "candidate_count": len(pool(degree_order, doubling_trace[-1]["factor"], seed_budget)),
        "selection": compact(result),
        "evaluation": evaluate(graph, probabilities, codes, result["selected"], evaluation),
        "doubling_trace": doubling_trace,
        "stop_reason": stop_reason,
        "timing": {"rank_seconds": ranking_seconds["degree"], "decision_seconds": round(decision_seconds, 6), "cold_accounted_seconds": round(common_seconds + ranking_seconds["degree"] + decision_seconds, 6)},
    }

    full_top_k = arms["full"]["selection"]["top_k"]
    full_mean = arms["full"]["evaluation"]["mean_spread"]
    for arm in arms.values():
        arm["comparison_to_full"] = {
            "same_ordered_top_k": arm["selection"]["top_k"] == full_top_k,
            "first_divergence": first_divergence(full_top_k, arm["selection"]["top_k"]),
            "mean_spread_delta": round(arm["evaluation"]["mean_spread"] - full_mean, 6),
        }
    return {
        "schema": "candidate-truncation-development-block-0.2",
        "study": STUDY,
        "development_only": True,
        "dataset": dataset_name,
        "block_seed": block_seed,
        "protocol": {
            "primary_objective": "mean_spread_on_fixed_selection_worlds",
            "history_fraction": HISTORY_FRACTION,
            "history_cutoff": cutoff,
            "timestamp_group_count": timestamp_groups,
            "horizon": HORIZON,
            "edge_probability": PROBABILITY,
            "seed_budget": seed_budget,
            "selection_world_count": selection_count,
            "evaluation_world_count": evaluation_count,
            "selection_world_sha256": hashlib.sha256(json.dumps(selection).encode("utf-8")).hexdigest(),
            "evaluation_world_sha256": hashlib.sha256(json.dumps(evaluation).encode("utf-8")).hexdigest(),
            "gnn_arm_status": "not_run_no_frozen_reproducible_model_input",
        },
        "input_sha256": {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")},
        "graph": graph_metadata,
        "rankings": {
            name: {
                "sha256": hashlib.sha256(json.dumps(order).encode("utf-8")).hexdigest(),
                "full_winner_ranks": [order.index(node) + 1 for node in full_top_k],
            }
            for name, order in rankings.items()
        },
        "warnings": dataset.warnings,
        "methods_planned": list(METHOD_IDS),
        "arms": arms,
        "common_preparation_seconds": round(common_seconds, 6),
        "block_elapsed_seconds": round(time.perf_counter() - block_started, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--k", type=int, choices=(5, 20), required=True)
    parser.add_argument("--selection-worlds", type=int, default=20)
    parser.add_argument("--evaluation-worlds", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = run_block(args.dataset, args.seed, args.k, args.selection_worlds, args.evaluation_worlds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "elapsed_seconds": report["block_elapsed_seconds"], "methods": len(report["arms"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
