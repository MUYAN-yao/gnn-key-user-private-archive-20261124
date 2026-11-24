"""Write raw-file and deterministic topology metadata without diffusion outcomes."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Stanford Large Network Dataset Collection (SNAP)",
        "datasets": {
            name: engine.load_external_graph(args.raw, name)["metadata"]
            for name in ("college_msg", "ca_grqc", "wiki_vote")
        },
        "raw_redistribution": "not included in project archive pending dataset-specific redistribution-term confirmation",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
