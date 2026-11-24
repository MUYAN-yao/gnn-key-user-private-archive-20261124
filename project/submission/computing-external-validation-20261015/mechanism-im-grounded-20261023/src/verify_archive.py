"""Create and verify a compact local review archive for this mechanism revision."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
SUBMISSION = ROOT.parents[1]
ARCHIVE = SUBMISSION / "computing-mechanism-im-grounded-20261023-v1.zip"
MANIFEST = SUBMISSION / "computing-mechanism-im-grounded-20261023-v1.sha256.json"
VERIFY = PROJECT / "tmp" / "mechanism-im-grounded-archive-verify"


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("manuscript/") or rel.startswith("audit/"):
        return True
    if rel in {"task_plan.md", "findings.md", "progress.md"}:
        return True
    if rel in {"src/draw_domain_mechanism.ps1", "src/prepare_domain_figure.py", "src/verify_archive.py"}:
        return True
    if rel.startswith("figures/wiki_vote_candidate_coverage_mechanism_v2"):
        return True
    if rel in {"figures/native_shape_inventory_domain_v2.json", "figures/wiki_vote_candidate_coverage_mechanism_preview.png"}:
        return True
    return False


def main() -> None:
    files = sorted((p for p in ROOT.rglob("*") if p.is_file() and include(p)), key=lambda p: p.as_posix())
    assert files
    manifest = {str(p.relative_to(ROOT).as_posix()): digest(p) for p in files}
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    MANIFEST.write_text(json.dumps({"archive": ARCHIVE.name, "files": manifest}, indent=2), encoding="utf-8")
    if VERIFY.exists():
        shutil.rmtree(VERIFY)
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive.extractall(VERIFY)
    extracted = {str(p.relative_to(VERIFY).as_posix()): digest(p) for p in VERIFY.rglob("*") if p.is_file()}
    assert extracted == manifest
    print(json.dumps({"status": "PASS", "archive": str(ARCHIVE), "archive_sha256": digest(ARCHIVE),
                      "file_count": len(files), "archive_bytes": ARCHIVE.stat().st_size,
                      "extracted_hashes_match": True}, indent=2))


if __name__ == "__main__":
    main()
