"""Descriptive-only analysis for the frozen v8 development matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics

from experiments.run_v8_candidate_truncation_development import BUDGETS, DATASETS, METHOD_IDS, SEEDS


def expected_blocks() -> set[tuple[str, int, int]]:
    return {(dataset, budget, seed) for dataset in DATASETS for budget in BUDGETS for seed in SEEDS}


def _summary(values: list[float]) -> dict:
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 6),
        "sample_sd": round(statistics.stdev(values), 6) if len(values) > 1 else None,
        "median": round(statistics.median(values), 6),
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
    }


def analyze(study_root: Path) -> dict:
    manifest = json.loads((study_root / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("development_only"):
        raise ValueError("analysis accepts only a development-only manifest")
    completed = {(row["dataset"], int(row["k"]), int(row["seed"])) for row in manifest["runs"] if row["status"] == "completed"}
    missing = expected_blocks() - completed
    unexpected = completed - expected_blocks()
    if missing or unexpected:
        raise ValueError(f"matrix is incomplete or unexpected; missing={sorted(missing)}, unexpected={sorted(unexpected)}")
    rows = []
    block_diagnostics = []
    for entry in manifest["runs"]:
        path = study_root / entry["path"]
        block = json.loads(path.read_text(encoding="utf-8"))
        if block["dataset"] != entry["dataset"] or block["block_seed"] != entry["seed"] or block["protocol"]["seed_budget"] != entry["k"]:
            raise ValueError(f"manifest/block identity mismatch: {path}")
        if set(block["arms"]) != set(METHOD_IDS):
            raise ValueError(f"method set mismatch: {path}")
        block_diagnostics.append({
            "dataset": block["dataset"],
            "k": block["protocol"]["seed_budget"],
            "seed": block["block_seed"],
            "full_winner_degree_ranks": block["rankings"]["degree"]["full_winner_ranks"],
            "full_winner_pagerank_ranks": block["rankings"]["pagerank"]["full_winner_ranks"],
            "full_winner_margins_micro": [row["winner_margin_micro"] for row in block["arms"]["full"]["selection"]["rounds"]],
        })
        for method, arm in block["arms"].items():
            rows.append({
                "dataset": block["dataset"],
                "k": block["protocol"]["seed_budget"],
                "seed": block["block_seed"],
                "method": method,
                "same_ordered_top_k": arm["comparison_to_full"]["same_ordered_top_k"],
                "first_divergence": arm["comparison_to_full"]["first_divergence"],
                "mean_spread_delta": arm["comparison_to_full"]["mean_spread_delta"],
                "cold_seconds": arm["timing"]["cold_accounted_seconds"],
                "decision_seconds": arm["timing"]["decision_seconds"],
                "candidate_count": arm["candidate_count"],
            })
    cells = []
    for dataset in DATASETS:
        for budget in BUDGETS:
            for method in METHOD_IDS:
                cell = [row for row in rows if row["dataset"] == dataset and row["k"] == budget and row["method"] == method]
                if len(cell) != len(SEEDS):
                    raise ValueError(f"incomplete method cell: {(dataset, budget, method)}")
                full_cell = [row for row in rows if row["dataset"] == dataset and row["k"] == budget and row["method"] == "full"]
                ratios = [row["cold_seconds"] / full["cold_seconds"] for row, full in zip(sorted(cell, key=lambda r: r["seed"]), sorted(full_cell, key=lambda r: r["seed"]))]
                divergence = [row["first_divergence"] for row in cell if row["first_divergence"] is not None]
                cells.append({
                    "dataset": dataset,
                    "k": budget,
                    "method": method,
                    "same_ordered_top_k_count": sum(row["same_ordered_top_k"] for row in cell),
                    "divergent_count": len(divergence),
                    "first_divergence_values": divergence,
                    "mean_spread_delta": _summary([row["mean_spread_delta"] for row in cell]),
                    "cold_time_ratio_to_full": _summary(ratios),
                    "candidate_count": _summary([row["candidate_count"] for row in cell]),
                })
    return {
        "schema": "candidate-truncation-development-analysis-0.2",
        "status": "DEVELOPMENT_DESCRIPTIVE_ONLY",
        "study_root": str(study_root),
        "block_count": len(completed),
        "method_execution_count": len(rows),
        "gnn_status": "not_run_no_frozen_reproducible_model_input",
        "no_inferential_statistics": True,
        "cells": cells,
        "block_diagnostics": block_diagnostics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = analyze(args.study_root)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"blocks": report["block_count"], "method_executions": report["method_execution_count"], "status": report["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
