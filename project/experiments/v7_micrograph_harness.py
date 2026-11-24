"""Runnable E1 micrograph correctness harness for the v7 exact search."""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

from experiments.v7_exact_search import (
    exact_score_micro,
    full_greedy,
    partial_upper_micro,
    reachable_total_upper_bound,
    risk_bound_greedy,
)


WORLDS = tuple(range(8101, 8109))


def _fixture(edges, nodes, probability, communities=None):
    graph = {node: [] for node in nodes}
    probabilities = {}
    for source, target, edge_probability in edges:
        graph[source].append(target)
        probabilities[(source, target)] = edge_probability
    return {
        "graph": {node: tuple(targets) for node, targets in graph.items()},
        "probabilities": probabilities,
        "communities": communities or {node: str(index % 3) for index, node in enumerate(nodes)},
    }


def fixed_micrographs():
    """Six <=8-node fixtures covering the E1 structural and tie conditions."""
    return {
        "directed_chain": _fixture(
            [("0", "1", 1.0), ("1", "2", 0.0), ("2", "3", 1.0), ("3", "4", 0.0)],
            ["0", "1", "2", "3", "4"], 0.0,
        ),
        "out_star": _fixture(
            [("0", target, 1.0) for target in ["1", "2", "3", "4", "5"]],
            ["0", "1", "2", "3", "4", "5"], 0.0,
        ),
        "disconnected": _fixture(
            [("0", "1", 1.0), ("1", "2", 0.0), ("3", "4", 1.0), ("4", "5", 1.0)],
            ["0", "1", "2", "3", "4", "5"], 0.0,
        ),
        "duplicate_neighborhood": _fixture(
            [("0", "3", 1.0), ("1", "3", 1.0), ("2", "3", 0.0), ("3", "4", 1.0)],
            ["0", "1", "2", "3", "4"], 0.0,
        ),
        "late_rank_complement": _fixture(
            [("0", "1", 1.0), ("0", "2", 1.0), ("6", "3", 1.0), ("6", "4", 1.0), ("6", "5", 1.0)],
            ["0", "1", "2", "3", "4", "5", "6"], 0.0,
            {"0": "A", "1": "A", "2": "A", "3": "B", "4": "B", "5": "B", "6": "B"},
        ),
        "exact_and_near_ties": _fixture(
            [("10", "x", 1.0), ("2", "x", 1.0), ("a", "y", 0.0), ("b", "y", 1.0)],
            ["10", "2", "a", "b", "x", "y"], 0.0,
        ),
    }


def _prefixes(nodes):
    for length in range(min(3, len(nodes)) + 1):
        yield from itertools.permutations(nodes, length)


def run_check() -> dict:
    report = {
        "schema": "v7-e1-micrograph-check-0.1",
        "world_count": len(WORLDS),
        "checked_structural_cases": 0,
        "checked_partial_cases": 0,
        "checked_trajectories": 0,
        "unsafe_prunes": 0,
        "trajectory_mismatches": 0,
        "status": "PASS",
    }
    for fixture_name, fixture in fixed_micrographs().items():
        graph = fixture["graph"]
        probabilities = fixture["probabilities"]
        communities = fixture["communities"]
        nodes = tuple(sorted(graph))
        ranking = tuple(reversed(nodes))
        for horizon in (1, 4):
            for prefix in _prefixes(nodes):
                for node in nodes:
                    if node in prefix:
                        continue
                    trial = prefix + (node,)
                    upper = reachable_total_upper_bound(graph, trial, horizon)
                    # Recompute directly without assuming a particular greedy
                    # winner, so every legal prefix/candidate pair is covered.
                    from experiments.v7_exact_search import CandidateEvaluator, SimulationCache
                    evaluator = CandidateEvaluator(graph, probabilities, horizon, {name: index for index, name in enumerate(nodes)}, SimulationCache())
                    spreads = evaluator.values(trial, WORLDS)
                    if max(spreads) > upper:
                        raise AssertionError(f"{fixture_name}: structural upper bound failed")
                    coverage = len({communities[name] for name in trial})
                    for risk_lambda in (Fraction(0), Fraction(7, 20), Fraction(1)):
                        final_score = exact_score_micro(spreads, coverage, risk_lambda=risk_lambda)
                        for observed in range(len(WORLDS) + 1):
                            bound = partial_upper_micro(spreads[:observed], len(WORLDS), upper, coverage, risk_lambda=risk_lambda)
                            report["checked_partial_cases"] += 1
                            if bound < final_score:
                                report["unsafe_prunes"] += 1
                                raise AssertionError(f"{fixture_name}: unsafe partial upper bound")
                    report["checked_structural_cases"] += 1
            for risk_lambda in (Fraction(0), Fraction(7, 20), Fraction(1)):
                for community_weight in (Fraction(0), Fraction(1, 4)):
                    for seed_count in range(1, min(4, len(nodes)) + 1):
                        full = full_greedy(graph, probabilities, communities, WORLDS, horizon=horizon, seed_count=seed_count, risk_lambda=risk_lambda, community_weight=community_weight)
                        bounded = risk_bound_greedy(graph, probabilities, communities, WORLDS, horizon=horizon, seed_count=seed_count, ranking=ranking, risk_lambda=risk_lambda, community_weight=community_weight)
                        report["checked_trajectories"] += 1
                        if full["selected"] != bounded["selected"]:
                            report["trajectory_mismatches"] += 1
                            raise AssertionError(f"{fixture_name}: exact trajectory mismatch")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_check()
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
