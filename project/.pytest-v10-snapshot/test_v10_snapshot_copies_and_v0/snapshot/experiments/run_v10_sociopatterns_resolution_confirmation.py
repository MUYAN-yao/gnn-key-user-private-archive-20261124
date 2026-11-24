"""Run the frozen v10 SocioPatterns confirmation matrix serially and resumably."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiments.v10_sociopatterns_resolution_confirmation import WORLD_COUNTS, WORLD_PATHS, run_condition
from experiments.v10_source_snapshot import MANIFEST_NAME, manifest_digest, verify


PROTOCOL = "sociopatterns_resolution_confirmation_protocol_v0_1.md"
MATRIX = {
    "invs2013": (5, 20),
    "invs2015": (5, 20),
    "sfhh2009": (5,),
    "kenya2012": (5, 20),
}


def expected_keys():
    return [(dataset, path, budget, worlds) for dataset, budgets in MATRIX.items() for path in WORLD_PATHS for budget in budgets for worlds in WORLD_COUNTS]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    snapshot = args.source_snapshot.resolve()
    verify(snapshot)
    source_file = Path(__file__).resolve()
    if source_file != (snapshot / "experiments" / "run_v10_sociopatterns_resolution_confirmation.py").resolve():
        raise ValueError("confirmation runner must execute from its verified source snapshot")
    snapshot_manifest_sha256 = manifest_digest(snapshot / MANIFEST_NAME)
    manifest_path = args.output_root / "manifest.json"
    if args.resume:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        if args.output_root.exists():
            raise FileExistsError("refusing to reuse an existing root")
        args.output_root.mkdir(parents=True)
        manifest = {"schema": "sociopatterns-resolution-confirmation-manifest-0.1", "protocol": PROTOCOL, "source_snapshot": {"path": str(snapshot), "manifest_sha256": snapshot_manifest_sha256}, "matrix": {key: list(value) for key, value in MATRIX.items()}, "world_paths": list(WORLD_PATHS), "world_counts": list(WORLD_COUNTS), "runs": []}
    if manifest.get("protocol") != PROTOCOL or manifest.get("source_snapshot") != {"path": str(snapshot), "manifest_sha256": snapshot_manifest_sha256} or manifest.get("matrix") != {key: list(value) for key, value in MATRIX.items()} or manifest.get("world_paths") != list(WORLD_PATHS) or manifest.get("world_counts") != list(WORLD_COUNTS):
        raise ValueError("manifest does not match frozen confirmation matrix")
    completed = {(row["dataset"], row["world_path"], row["k"], row["selection_world_count"]) for row in manifest["runs"]}
    for dataset, path, budget, worlds in expected_keys():
        key = (dataset, path, budget, worlds)
        if key in completed:
            continue
        relative = Path(dataset) / f"k{budget}" / f"path-{path}-w{worlds}.json"
        output = args.output_root / relative
        if output.exists():
            raise FileExistsError(f"untracked output exists: {relative}")
        report = run_condition(dataset, path, budget, worlds)
        report["source_snapshot"] = {"manifest_sha256": snapshot_manifest_sha256, "snapshot_id": verify(snapshot)["snapshot_id"]}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["runs"].append({"dataset": dataset, "world_path": path, "k": budget, "selection_world_count": worlds, "path": str(relative).replace("\\", "/")})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest["runs"][-1]), flush=True)


if __name__ == "__main__":
    main()
