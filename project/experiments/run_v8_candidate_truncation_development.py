"""Run the frozen development-only candidate-truncation matrix serially."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from experiments.v8_candidate_truncation_development import METHOD_IDS, run_block


DATASETS = ("digg_pilot5000", "higgs_pilot1500")
SEEDS = (101, 102, 103)
BUDGETS = (5, 20)
SELECTION_WORLDS = 20
EVALUATION_WORLDS = 1000
PROTOCOL = "candidate_truncation_development_protocol_v0_2.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = args.output_root
    if root.exists() and not args.resume:
        raise FileExistsError(f"refusing to reuse existing development study root: {root}")
    if args.resume:
        manifest_path = root / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError("resume requires an existing manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {
            "development_only": True,
            "protocol": PROTOCOL,
            "datasets": list(DATASETS),
            "seeds": list(SEEDS),
            "budgets": list(BUDGETS),
            "selection_worlds": SELECTION_WORLDS,
            "evaluation_worlds": EVALUATION_WORLDS,
            "methods": list(METHOD_IDS),
        }
        if any(manifest.get(key) != value for key, value in expected.items()):
            raise ValueError("existing manifest does not match the frozen development matrix")
    else:
        root.mkdir(parents=True)
        manifest = {
            "schema": "candidate-truncation-development-manifest-0.2",
            "development_only": True,
            "protocol": PROTOCOL,
            "datasets": list(DATASETS),
            "seeds": list(SEEDS),
            "budgets": list(BUDGETS),
            "selection_worlds": SELECTION_WORLDS,
            "evaluation_worlds": EVALUATION_WORLDS,
            "methods": list(METHOD_IDS),
            "runs": [],
        }
    completed = {(item["dataset"], item["k"], item["seed"]) for item in manifest["runs"] if item["status"] == "completed"}
    started = time.perf_counter()
    for dataset in DATASETS:
        for budget in BUDGETS:
            for seed in SEEDS:
                if (dataset, budget, seed) in completed:
                    continue
                relative = Path(dataset) / f"k{budget}" / f"seed-{seed}.json"
                output = root / relative
                if output.exists():
                    raise FileExistsError(f"completed manifest lacks expected run state for {relative}")
                report = run_block(dataset, seed, budget, SELECTION_WORLDS, EVALUATION_WORLDS)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                manifest["runs"].append({
                    "dataset": dataset,
                    "k": budget,
                    "seed": seed,
                    "path": str(relative).replace("\\", "/"),
                    "status": "completed",
                    "block_elapsed_seconds": report["block_elapsed_seconds"],
                })
                (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(json.dumps(manifest["runs"][-1], ensure_ascii=False), flush=True)
    manifest["total_elapsed_seconds"] = round(time.perf_counter() - started, 6)
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
