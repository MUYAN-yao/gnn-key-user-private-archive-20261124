"""Run outcome-blind W=20 timing preflights for the v10 resource redesign."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.v10_sociopatterns_resolution_confirmation import DATASETS, run_preflight


WORLD_COUNT = 20


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError("refusing to reuse preflight output")
    args.output_root.mkdir(parents=True)
    manifest = {"schema": "sociopatterns-resolution-w20-preflight-0.1", "outcome_blind": True, "world_count": WORLD_COUNT, "runs": []}
    for dataset in DATASETS:
        for budget in (5, 20):
            report = run_preflight(dataset, budget, WORLD_COUNT)
            path = args.output_root / f"{dataset}-k{budget}.json"
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            manifest["runs"].append({"dataset": dataset, "k": budget, "path": path.name, "elapsed_seconds": report["elapsed_seconds"]})
            (args.output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(manifest["runs"][-1]), flush=True)


if __name__ == "__main__":
    main()
