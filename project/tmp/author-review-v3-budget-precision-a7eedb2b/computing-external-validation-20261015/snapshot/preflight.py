"""Outcome-blind resource preflight for the external-validation protocol.

The script deliberately emits timings, memory and structural metadata only. It
does run the full greedy and independent evaluator to measure resource use, but
does not serialize, print, compare or retain selected seed identifiers, round
scores or utility values.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import time
from pathlib import Path

import numpy as np
import psutil

import engine


def _peak_bytes(process):
    memory = process.memory_info()
    return int(getattr(memory, "peak_wset", getattr(memory, "rss", 0)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worlds", type=int, nargs="+", default=[80, 320])
    parser.add_argument("--evaluation-worlds", type=int, default=1000)
    args = parser.parse_args()
    if any(w <= 0 for w in args.worlds) or args.evaluation_worlds <= 0:
        raise ValueError("world counts must be positive")
    process = psutil.Process()
    warm_start = time.perf_counter()
    engine.warmup()
    warm_seconds = time.perf_counter() - warm_start
    rows = []
    for dataset in ("college_msg", "ca_grqc", "wiki_vote"):
        graph = engine.load_external_graph(args.raw, dataset)
        for world_count in args.worlds:
            select_ids = engine.world_ids(
                dataset, 9001, "resource-preflight-selection", world_count,
                namespace="computing-external-validation-20261015-preflight-v1",
            )
            eval_ids = engine.world_ids(
                dataset, 9001, "resource-preflight-evaluation", args.evaluation_worlds,
                namespace="computing-external-validation-20261015-preflight-v1",
            )
            if set(select_ids) & set(eval_ids):
                raise RuntimeError("preflight world namespaces collided")
            started = time.perf_counter()
            selection_worlds = engine.make_worlds(
                select_ids, graph["sources"], graph["targets"], 0.01, 3, False
            )
            evaluation_worlds = engine.make_worlds(
                eval_ids, graph["sources"], graph["targets"], 0.01, 3, False
            )
            world_seconds = time.perf_counter() - started
            started = time.perf_counter()
            selected, round_scores = engine.greedy(
                graph["indptr"], graph["targets"], selection_worlds,
                np.arange(len(graph["nodes"]), dtype=np.int64), 5, 3,
            )
            selection_seconds = time.perf_counter() - started
            started = time.perf_counter()
            values = engine.evaluate(
                graph["indptr"], graph["targets"], evaluation_worlds, selected, 3
            )
            evaluation_seconds = time.perf_counter() - started
            # Do not inspect or serialize outcomes. Explicitly release outcome arrays.
            del values, selected, round_scores, selection_worlds, evaluation_worlds
            gc.collect()
            rows.append(
                {
                    "dataset": dataset,
                    "selection_worlds": world_count,
                    "evaluation_worlds": args.evaluation_worlds,
                    "world_preparation_seconds": world_seconds,
                    "full_greedy_selection_seconds": selection_seconds,
                    "independent_evaluation_seconds": evaluation_seconds,
                    "peak_working_set_bytes": _peak_bytes(process),
                    "outcome_values_persisted": False,
                    "seed_identifiers_persisted": False,
                }
            )
    report = {
        "kind": "outcome-blind resource preflight",
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "jit_warmup_seconds": warm_seconds,
        "propagation": {"p": 0.01, "horizon": 3, "coupling": "step"},
        "candidate_pool": "full only",
        "selection_budget": 5,
        "datasets": {
            name: engine.load_external_graph(args.raw, name)["metadata"]
            for name in ("college_msg", "ca_grqc", "wiki_vote")
        },
        "measurements": rows,
        "guarantee": (
            "No selected seed identifiers, greedy round scores, per-world values, "
            "mean utility, utility differences, rankings or candidate memberships were printed or serialized."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
