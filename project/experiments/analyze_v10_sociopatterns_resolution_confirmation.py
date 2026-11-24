"""Read-only analysis for the frozen SocioPatterns resolution confirmation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.run_v10_sociopatterns_resolution_confirmation import expected_keys


METHODS = ("full", "degree_2k", "degree_4k", "degree_8k")
WORLD_COUNTS = (20, 80, 320)


def summarize(root: Path) -> dict:
    files = [path for path in sorted(root.rglob("*.json")) if path.name != "manifest.json"]
    if len(files) != len(expected_keys()):
        raise ValueError(f"expected {len(expected_keys())} conditions, found {len(files)}")
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    keys = {(row["dataset"], row["world_path"], row["k"], row["selection_world_count"]) for row in rows}
    if keys != set(expected_keys()):
        raise ValueError("condition coverage differs from frozen matrix")
    by_key = {(row["dataset"], row["world_path"], row["k"], row["selection_world_count"]): row for row in rows}
    trajectories = []
    for dataset, path, budget in sorted({key[:3] for key in keys}):
        seeds = [by_key[(dataset, path, budget, worlds)]["arms"]["full"]["selection"] for worlds in WORLD_COUNTS]
        trajectories.append({
            "dataset": dataset,
            "world_path": path,
            "k": budget,
            "same_20_80": seeds[0]["top_k"] == seeds[1]["top_k"],
            "same_80_320": seeds[1]["top_k"] == seeds[2]["top_k"],
            "zero_margin_rounds": {str(worlds): sum(round_["winner_margin_micro"] == 0 for round_ in selection["rounds"]) for worlds, selection in zip(WORLD_COUNTS, seeds)},
        })
    method_summary = {}
    for worlds in WORLD_COUNTS:
        subset = [row for row in rows if row["selection_world_count"] == worlds]
        method_summary[str(worlds)] = {}
        for method in METHODS:
            arms = [row["arms"][method] for row in subset]
            method_summary[str(worlds)][method] = {
                "condition_count": len(arms),
                "same_ordered_top_k_count": sum(arm["comparison_to_full"]["same_ordered_top_k"] for arm in arms),
                "mean_spread_deltas": [arm["comparison_to_full"]["mean_spread_delta"] for arm in arms],
                "decision_seconds": [arm["decision_seconds"] for arm in arms],
            }
    return {"schema": "sociopatterns-resolution-confirmation-analysis-0.1", "condition_count": len(rows), "simulation_only": True, "population_inference": "not_performed", "full_trajectories": trajectories, "methods_by_world_count": method_summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summarize(args.input_root), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
