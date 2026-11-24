"""Run the frozen v10 SocioPatterns confirmation matrix serially and resumably."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

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
    parser.add_argument("--max-elapsed-seconds", type=float, default=14_400)
    args = parser.parse_args()
    if args.max_elapsed_seconds <= 0:
        raise ValueError("--max-elapsed-seconds must be positive")
    snapshot = args.source_snapshot.resolve()
    if not args.output_root.is_absolute():
        raise ValueError("--output-root must be an absolute path")
    output_root = args.output_root.resolve()
    try:
        output_root.relative_to(snapshot)
    except ValueError:
        pass
    else:
        raise ValueError("--output-root must be outside the source snapshot")
    verify(snapshot)
    source_file = Path(__file__).resolve()
    if source_file != (snapshot / "experiments" / "run_v10_sociopatterns_resolution_confirmation.py").resolve():
        raise ValueError("confirmation runner must execute from its verified source snapshot")
    snapshot_manifest_sha256 = manifest_digest(snapshot / MANIFEST_NAME)
    manifest_path = output_root / "manifest.json"
    if args.resume:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        if output_root.exists():
            raise FileExistsError("refusing to reuse an existing root")
        output_root.mkdir(parents=True)
        manifest = {"schema": "sociopatterns-resolution-confirmation-manifest-0.1", "protocol": PROTOCOL, "source_snapshot": {"path": str(snapshot), "manifest_sha256": snapshot_manifest_sha256}, "matrix": {key: list(value) for key, value in MATRIX.items()}, "world_paths": list(WORLD_PATHS), "world_counts": list(WORLD_COUNTS), "started_at_epoch": time.time(), "max_elapsed_seconds": args.max_elapsed_seconds, "status": "RUNNING", "runs": []}
    if manifest.get("protocol") != PROTOCOL or manifest.get("source_snapshot") != {"path": str(snapshot), "manifest_sha256": snapshot_manifest_sha256} or manifest.get("matrix") != {key: list(value) for key, value in MATRIX.items()} or manifest.get("world_paths") != list(WORLD_PATHS) or manifest.get("world_counts") != list(WORLD_COUNTS) or manifest.get("max_elapsed_seconds") != args.max_elapsed_seconds:
        raise ValueError("manifest does not match frozen confirmation matrix")
    if manifest.get("status") not in {"RUNNING"}:
        raise ValueError("only a RUNNING matrix may be resumed")
    completed = {(row["dataset"], row["world_path"], row["k"], row["selection_world_count"]) for row in manifest["runs"]}
    for dataset, path, budget, worlds in expected_keys():
        key = (dataset, path, budget, worlds)
        if key in completed:
            continue
        if time.time() - manifest["started_at_epoch"] >= args.max_elapsed_seconds:
            manifest["status"] = "RESOURCE_STOP"
            manifest["stopped_at_epoch"] = time.time()
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"status": "RESOURCE_STOP", "completed_conditions": len(manifest["runs"])}), flush=True)
            return
        relative = Path(dataset) / f"k{budget}" / f"path-{path}-w{worlds}.json"
        output = output_root / relative
        if output.exists():
            raise FileExistsError(f"untracked output exists: {relative}")
        report = run_condition(dataset, path, budget, worlds)
        report["source_snapshot"] = {"manifest_sha256": snapshot_manifest_sha256, "snapshot_id": verify(snapshot)["snapshot_id"]}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["runs"].append({"dataset": dataset, "world_path": path, "k": budget, "selection_world_count": worlds, "path": str(relative).replace("\\", "/")})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest["runs"][-1]), flush=True)
    manifest["status"] = "COMPLETE"
    manifest["completed_at_epoch"] = time.time()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
