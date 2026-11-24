"""Immutable source snapshots for the separately versioned v6 Digg study."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import stat

STUDY = 'v6-digg-k5-candidate-reduction'
SCHEMA = 'v6-source-snapshot-1'
MANIFEST = 'snapshot_manifest.json'
FILES = (
    'experiments/v6_digg_snapshot.py',
    'experiments/create_v6_digg_snapshot.py',
    'experiments/run_v6_digg_k5.py',
    'experiments/v5_source_snapshot.py',
    'experiments/run_v5_candidate_reduction.py',
    'backend/app/__init__.py', 'backend/app/baselines.py',
    'backend/app/contracts.py', 'backend/app/diffusion.py',
    'backend/app/graph.py', 'backend/app/model_v2.py',
    'backend/app/optimizer.py', 'backend/app/pipeline_v2_t0.py',
    'backend/app/pipeline_v2_t0b.py', 'backend/app/validation.py',
    'protocols/influence_v6_digg_k5_preregistration.md',
    'requirements.txt', 'pyproject.toml',
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def expected_paths(root: Path) -> dict[str, Path]:
    return {relative: root / relative for relative in FILES}


def _identifier(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:20]


def verify(snapshot: Path) -> dict:
    snapshot = snapshot.resolve()
    manifest_path = snapshot / MANIFEST
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'Unreadable v6 snapshot manifest: {exc}') from exc
    if manifest.get('schema') != SCHEMA or manifest.get('study_version') != STUDY:
        raise ValueError('v6 snapshot schema or study mismatch')
    files = manifest.get('files')
    if not isinstance(files, dict) or set(files) != set(FILES):
        raise ValueError('v6 snapshot source set mismatch')
    for relative, digest in files.items():
        candidate = (snapshot / relative).resolve()
        try:
            candidate.relative_to(snapshot)
        except ValueError as exc:
            raise ValueError(f'v6 snapshot source path escapes root: {relative}') from exc
        if not candidate.is_file() or sha256(candidate) != digest:
            raise ValueError(f'v6 snapshot hash mismatch: {relative}')
    if manifest.get('snapshot_id') != _identifier(files):
        raise ValueError('v6 snapshot identifier mismatch')
    return manifest


def create(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f'Refusing non-empty v6 snapshot destination: {destination}')
    paths = expected_paths(source)
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    if missing:
        raise ValueError('Missing v6 snapshot source: ' + ', '.join(missing))
    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for relative, path in paths.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        files[relative] = sha256(target)
    manifest = {'schema': SCHEMA, 'study_version': STUDY, 'snapshot_id': _identifier(files),
                'created_at_utc': datetime.now(timezone.utc).isoformat(), 'files': files,
                'hash_algorithm': 'sha256'}
    manifest_path = destination / MANIFEST
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path in [*(destination / item for item in FILES), manifest_path]:
        path.chmod(path.stat().st_mode & ~stat.S_IWRITE)
    verify(destination)
    return manifest
