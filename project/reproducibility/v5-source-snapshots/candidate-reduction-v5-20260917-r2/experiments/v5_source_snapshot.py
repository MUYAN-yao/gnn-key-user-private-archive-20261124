"""Immutable-source snapshot support for the preregistered v5 study.

The snapshot is deliberately file-hash based: operating-system read-only flags
are useful hints, but the manifest is the actual provenance check used before
any v5 artifact is written.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import stat
from typing import Any


STUDY = "v5-candidate-reduction"
SNAPSHOT_SCHEMA = "v5-source-snapshot-1"
MANIFEST_NAME = "snapshot_manifest.json"

# These are the complete sources whose exact bytes define an executable v5
# study.  Data remain external and are hash-checked separately by the runner.
SNAPSHOT_FILES = (
    "experiments/v5_source_snapshot.py",
    "experiments/create_v5_source_snapshot.py",
    "experiments/run_v5_candidate_reduction.py",
    "experiments/validate_v5_candidate_reduction.py",
    "experiments/analyze_v5_candidate_reduction.py",
    "experiments/run_v3_fairness_sensitivity.py",
    "backend/app/__init__.py",
    "backend/app/baselines.py",
    "backend/app/contracts.py",
    "backend/app/diffusion.py",
    "backend/app/graph.py",
    "backend/app/model_v2.py",
    "backend/app/optimizer.py",
    "backend/app/pipeline_v2_t0.py",
    "backend/app/pipeline_v2_t0b.py",
    "backend/app/validation.py",
    "protocols/influence_v5_candidate_reduction_preregistration.md",
    "requirements.txt",
    "pyproject.toml",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def snapshot_manifest_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / MANIFEST_NAME


def expected_source_paths(root: Path) -> dict[str, Path]:
    return {relative: root / relative for relative in SNAPSHOT_FILES}


def _read_manifest(snapshot_dir: Path) -> dict[str, Any]:
    path = snapshot_manifest_path(snapshot_dir)
    if not path.is_file():
        raise ValueError(f"Source snapshot manifest is missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Source snapshot manifest is unreadable: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Source snapshot manifest must be a JSON object")
    return payload


def verify_snapshot(snapshot_dir: Path) -> dict[str, Any]:
    """Verify every snapshotted byte and return its parsed manifest.

    This function intentionally never falls back to the live workspace.
    """
    snapshot_dir = snapshot_dir.resolve()
    manifest = _read_manifest(snapshot_dir)
    if manifest.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("Source snapshot schema mismatch")
    if manifest.get("study_version") != STUDY:
        raise ValueError("Source snapshot study version mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(SNAPSHOT_FILES):
        raise ValueError("Source snapshot file set does not match the v5 contract")
    for relative, expected_hash in files.items():
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ValueError(f"Malformed source hash for {relative}")
        path = (snapshot_dir / relative).resolve()
        try:
            path.relative_to(snapshot_dir)
        except ValueError as exc:
            raise ValueError(f"Source path escapes snapshot: {relative}") from exc
        if not path.is_file() or sha256(path) != expected_hash:
            raise ValueError(f"Source snapshot hash mismatch: {relative}")
    expected_id = canonical_digest(files)[:20]
    if manifest.get("snapshot_id") != expected_id:
        raise ValueError("Source snapshot identifier mismatch")
    return manifest


def create_snapshot(source_root: Path, snapshot_dir: Path) -> dict[str, Any]:
    """Copy the fixed source set and create its independently verifiable manifest."""
    source_root = source_root.resolve()
    snapshot_dir = snapshot_dir.resolve()
    if snapshot_dir.exists() and any(snapshot_dir.iterdir()):
        raise ValueError(f"Refusing to overwrite non-empty snapshot directory: {snapshot_dir}")
    if snapshot_dir == source_root:
        raise ValueError("Source snapshot directory cannot be the live source root")
    source_paths = expected_source_paths(source_root)
    missing = [relative for relative, path in source_paths.items() if not path.is_file()]
    if missing:
        raise ValueError(f"Cannot snapshot missing required files: {', '.join(missing)}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    for relative, source in source_paths.items():
        destination = snapshot_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        files[relative] = sha256(destination)
    manifest: dict[str, Any] = {
        "schema": SNAPSHOT_SCHEMA,
        "study_version": STUDY,
        "snapshot_id": canonical_digest(files)[:20],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "hash_algorithm": "sha256",
        "data_policy": "External study inputs are not copied; the v5 runner verifies their fixed SHA-256 values.",
    }
    manifest_path = snapshot_manifest_path(snapshot_dir)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Read-only is advisory on Windows, so it never substitutes for verification.
    for path in [*(snapshot_dir / relative for relative in SNAPSHOT_FILES), manifest_path]:
        try:
            path.chmod(path.stat().st_mode & ~stat.S_IWRITE)
        except OSError:
            pass
    verify_snapshot(snapshot_dir)
    return manifest
