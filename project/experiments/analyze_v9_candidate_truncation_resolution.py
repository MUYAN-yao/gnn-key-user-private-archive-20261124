"""Read-only descriptive analysis for the frozen v9 nested-world study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHODS = ("full", "degree_2k", "degree_4k", "degree_8k")
WORLD_COUNTS = (20, 80)


def _load_reports(root: Path) -> list[dict[str, Any]]:
    reports = []
    for path in sorted(root.rglob("*.json")):
        if path.name == "manifest.json":
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("development_only") is not True:
            raise ValueError(f"report is not development-only: {path}")
        reports.append(report)
    return reports


def _round_summary(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    margins = [row["winner_margin_micro"] for row in rounds]
    return {
        "round_count": len(rounds),
        "zero_margin_rounds": sum(margin == 0 for margin in margins),
        "multiway_best_rounds": sum(row["exact_best_tie_count"] > 1 for row in rounds),
        "minimum_margin_micro": min(margins) if margins else None,
    }


def summarize(root: Path, expected_conditions: int = 16) -> dict[str, Any]:
    reports = _load_reports(root)
    if len(reports) != expected_conditions:
        raise ValueError(f"expected {expected_conditions} condition files, found {len(reports)}")
    keys = [(row["dataset"], row["seed"], row["k"], row["selection_world_count"]) for row in reports]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate condition key")
    by_key = {(row["dataset"], row["seed"], row["k"], row["selection_world_count"]): row for row in reports}
    paired_keys = sorted({key[:3] for key in by_key})
    if any((key + (world_count,)) not in by_key for key in paired_keys for world_count in WORLD_COUNTS):
        raise ValueError("each dataset/seed/k block must contain W=20 and W=80")

    full_cross_w = []
    for dataset, seed, budget in paired_keys:
        w20 = by_key[(dataset, seed, budget, 20)]["arms"]["full"]["selection"]
        w80 = by_key[(dataset, seed, budget, 80)]["arms"]["full"]["selection"]
        full_cross_w.append({
            "dataset": dataset, "seed": seed, "k": budget,
            "same_ordered_top_k": w20["top_k"] == w80["top_k"],
            "w20": _round_summary(w20["rounds"]),
            "w80": _round_summary(w80["rounds"]),
        })

    method_by_w: dict[str, dict[str, dict[str, Any]]] = {}
    for world_count in WORLD_COUNTS:
        method_by_w[str(world_count)] = {}
        subset = [row for row in reports if row["selection_world_count"] == world_count]
        for method in METHODS:
            arms = [row["arms"][method] for row in subset]
            method_by_w[str(world_count)][method] = {
                "condition_count": len(arms),
                "same_as_full_count": sum(arm["comparison_to_full"]["same_ordered_top_k"] for arm in arms),
                "mean_spread_delta_values": [arm["comparison_to_full"]["mean_spread_delta"] for arm in arms],
                "decision_seconds_values": [arm["decision_seconds"] for arm in arms],
                "zero_margin_rounds": sum(_round_summary(arm["selection"]["rounds"])["zero_margin_rounds"] for arm in arms),
            }
    return {
        "schema": "candidate-truncation-resolution-analysis-0.1",
        "development_only": True,
        "inferential_statistics": "not_performed",
        "condition_count": len(reports),
        "full_cross_w": full_cross_w,
        "method_by_w": method_by_w,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    result = summarize(args.input_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
