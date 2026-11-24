"""Immutable source snapshot contract for the v10 confirmation matrix."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import stat


STUDY = "sociopatterns-resolution-confirmation-v0_1"
SCHEMA = "v10-source-snapshot-0.1"
MANIFEST_NAME = "snapshot_manifest.json"
FILES = (
    "experiments/v10_source_snapshot.py",
    "experiments/create_v10_source_snapshot.py",
    "experiments/v10_sociopatterns_resolution_confirmation.py",
    "experiments/run_v10_sociopatterns_resolution_confirmation.py",
    "experiments/v7_exact_search.py",
    "experiments/v8_candidate_truncation_development.py",
    "experiments/v8_candidate_truncation_preflight.py",
    "backend/app/__init__.py",
    "backend/app/validation.py",
    "protocols/sociopatterns_resolution_confirmation_protocol_v0_1.md",
    "requirements.txt",
    "pyproject.toml",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_digest(manifest_path: Path) -> str:
    return sha256(manifest_path)


def _id(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def create(source_root: Path, snapshot: Path) -> dict:
    source_root, snapshot = source_root.resolve(), snapshot.resolve()
    if snapshot.exists() and any(snapshot.iterdir()):
        raise ValueError("refusing to overwrite a non-empty snapshot")
    snapshot.mkdir(parents=True, exist_ok=True)
    file_hashes = {}
    for relative in FILES:
        source = source_root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        file_hashes[relative] = sha256(destination)
    manifest = {"schema": SCHEMA, "study": STUDY, "snapshot_id": _id(file_hashes), "created_at_utc": datetime.now(timezone.utc).isoformat(), "files": file_hashes, "data_policy": "External confirmation data are not copied; the snapshot runner records their hashes."}
    path = snapshot / MANIFEST_NAME
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path_to_lock in [*(snapshot / relative for relative in FILES), path]:
        try:
            path_to_lock.chmod(path_to_lock.stat().st_mode & ~stat.S_IWRITE)
        except OSError:
            pass
    verify(snapshot)
    return manifest


def verify(snapshot: Path) -> dict:
    snapshot = snapshot.resolve()
    path = snapshot / MANIFEST_NAME
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA or manifest.get("study") != STUDY or set(manifest.get("files", {})) != set(FILES):
        raise ValueError("snapshot manifest contract mismatch")
    for relative, expected in manifest["files"].items():
        candidate = (snapshot / relative).resolve()
        if not candidate.is_file() or sha256(candidate) != expected:
            raise ValueError(f"snapshot hash mismatch: {relative}")
    if manifest.get("snapshot_id") != _id(manifest["files"]):
        raise ValueError("snapshot id mismatch")
    return manifest
