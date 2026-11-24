"""Verify the already-created v3 archive by CRC and extraction-time SHA-256 checks."""
from pathlib import Path
import hashlib
import json
import os
import uuid
import zipfile

R = Path(__file__).resolve().parents[1]
S = R.parent.parent
archive_path = S / "computing-author-review-20261016-budget-precision-v2.zip"
assert archive_path.is_file(), archive_path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


unpack = S.parent / "tmp" / ("author-review-v3-budget-precision-verify-" + uuid.uuid4().hex[:8])
unpack.mkdir(parents=True)
target = Path("\\\\?\\" + str(unpack.resolve())) if os.name == "nt" else unpack
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    for info in archive.infolist():
        assert (unpack / info.filename).resolve().is_relative_to(unpack.resolve()), "unsafe archive path"
    archive.extractall(target)
manifest = json.loads((target / "package_manifest.json").read_text(encoding="utf-8"))
bad = [name for name, digest in manifest["files"].items() if sha(target / name) != digest]
assert not bad, bad
assert not any("/data/raw/" in name for name in manifest["files"])
result = {
    "status": "PASS",
    "archive": str(archive_path),
    "archive_sha256": sha(archive_path),
    "archive_bytes": archive_path.stat().st_size,
    "files_verified_after_extraction": len(manifest["files"]),
    "extraction_directory": str(unpack),
    "hash_mismatches": bad,
    "zip_crc_check": True,
    "third_party_raw_data_excluded": True,
}
archive_path.with_suffix(".verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
archive_path.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
