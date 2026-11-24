"""Run the frozen v9 nested-W development matrix serially and resumably."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.v9_candidate_truncation_resolution import BUDGETS, SEEDS, WORLD_COUNTS, run_condition


DATASETS = ("digg_pilot5000", "higgs_pilot1500")
PROTOCOL = "candidate_truncation_resolution_development_protocol_v0_1.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    manifest_path = args.output_root / "manifest.json"
    if args.resume:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        if args.output_root.exists():
            raise FileExistsError("refusing to reuse an existing root")
        args.output_root.mkdir(parents=True)
        manifest = {"schema": "candidate-truncation-resolution-manifest-0.1", "development_only": True, "protocol": PROTOCOL, "datasets": list(DATASETS), "seeds": list(SEEDS), "budgets": list(BUDGETS), "world_counts": list(WORLD_COUNTS), "methods": ["full", "degree_2k", "degree_4k", "degree_8k"], "runs": []}
    expected = {"development_only": True, "protocol": PROTOCOL, "datasets": list(DATASETS), "seeds": list(SEEDS), "budgets": list(BUDGETS), "world_counts": list(WORLD_COUNTS), "methods": ["full", "degree_2k", "degree_4k", "degree_8k"]}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("manifest does not match frozen v9 matrix")
    done = {(row["dataset"], row["seed"], row["k"], row["selection_worlds"]) for row in manifest["runs"]}
    for dataset in DATASETS:
        for seed in SEEDS:
            for budget in BUDGETS:
                for world_count in WORLD_COUNTS:
                    key = (dataset, seed, budget, world_count)
                    if key in done:
                        continue
                    relative = Path(dataset) / f"k{budget}" / f"seed-{seed}-w{world_count}.json"
                    output = args.output_root / relative
                    if output.exists():
                        raise FileExistsError(f"untracked output exists: {relative}")
                    report = run_condition(dataset, seed, budget, world_count)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    row = {"dataset": dataset, "seed": seed, "k": budget, "selection_worlds": world_count, "path": str(relative).replace("\\", "/"), "elapsed_seconds": report["elapsed_seconds"]}
                    manifest["runs"].append(row)
                    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
