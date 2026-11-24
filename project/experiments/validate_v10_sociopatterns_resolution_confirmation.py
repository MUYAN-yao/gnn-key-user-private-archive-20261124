"""Read-only integrity validator for a completed v10 confirmation matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiments.run_v10_sociopatterns_resolution_confirmation import expected_keys
from experiments.v10_sociopatterns_resolution_confirmation import EVALUATION_WORLDS, world_ids
from experiments.v10_source_snapshot import manifest_digest, verify


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(root: Path) -> dict:
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE":
        raise ValueError(f"confirmation matrix is not COMPLETE: {manifest.get('status')!r}")
    source = manifest.get("source_snapshot")
    if not isinstance(source, dict):
        raise ValueError("missing source snapshot")
    snapshot = Path(source.get("path", ""))
    snapshot_manifest = snapshot / "snapshot_manifest.json"
    verified_snapshot = verify(snapshot)
    if source.get("manifest_sha256") != manifest_digest(snapshot_manifest):
        raise ValueError("source snapshot manifest hash mismatch")
    declared = {(row["dataset"], row["world_path"], row["k"], row["selection_world_count"]) for row in manifest.get("runs", [])}
    expected = set(expected_keys())
    if declared != expected:
        raise ValueError("matrix coverage is incomplete or changed")
    files = []
    for row in manifest["runs"]:
        path = root / row["path"]
        report = json.loads(path.read_text(encoding="utf-8"))
        key = (report.get("dataset"), report.get("world_path"), report.get("k"), report.get("selection_world_count"))
        if key != (row["dataset"], row["world_path"], row["k"], row["selection_world_count"]):
            raise ValueError(f"condition metadata mismatch: {path}")
        if report.get("confirmation_data") is not True or report.get("simulation_only") is not True:
            raise ValueError(f"semantic flag mismatch: {path}")
        if report.get("source_snapshot", {}).get("manifest_sha256") != source["manifest_sha256"] or report["source_snapshot"].get("snapshot_id") != verified_snapshot["snapshot_id"]:
            raise ValueError(f"condition source snapshot mismatch: {path}")
        selection = world_ids(report["dataset"], report["world_path"], "selection", report["selection_world_count"])
        evaluation = world_ids(report["dataset"], report["world_path"], "evaluation", EVALUATION_WORLDS)
        if report["selection_world_sha256"] != hashlib.sha256(json.dumps(selection).encode()).hexdigest() or report["evaluation_world_sha256"] != hashlib.sha256(json.dumps(evaluation).encode()).hexdigest():
            raise ValueError(f"world digest mismatch: {path}")
        if set(report.get("arms", {})) != {"full", "degree_2k", "degree_4k", "degree_8k"}:
            raise ValueError(f"arm coverage mismatch: {path}")
        files.append({"path": row["path"], "sha256": sha256(path)})
    return {"schema": "sociopatterns-resolution-confirmation-validation-0.1", "status": "PASS", "condition_count": len(files), "source_snapshot": {"id": verified_snapshot["snapshot_id"], "manifest_sha256": source["manifest_sha256"]}, "condition_file_hashes": files}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(validate(args.input_root), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
