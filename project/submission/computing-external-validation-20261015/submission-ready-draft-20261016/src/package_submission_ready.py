"""Archive the independent submission-preparation package and verify extraction."""
from pathlib import Path
import hashlib
import json
import os
import uuid
import zipfile

R = Path(__file__).resolve().parents[1]
B = R.parent
S = B.parent
H = S / "computing-strengthening-20261015"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert json.loads((R / "qa/submission_ready_checks.json").read_text())["status"] == "PASS"
destination = S / "computing-submission-preparation-20261016-v1.zip"
if destination.exists():
    raise FileExistsError(f"Preserve existing release: {destination}")
files, excluded = [], []
for base in (B, H):
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".nbc", ".nbi", ".download"} or relative.parts[:2] == ("data", "raw"):
            excluded.append(str(path.relative_to(S)))
            continue
        files.append(path)
manifest = {
    "status": "local submission-preparation archive; no online submission or publication",
    "algorithm": "sha256",
    "files": {path.relative_to(S).as_posix(): sha(path) for path in files},
    "excluded": excluded,
    "raw_data_policy": "Third-party raw data are omitted; provider sources, download/preprocessing instructions and expected hashes are retained. No redistribution permission is asserted.",
}
with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in files:
        archive.write(path, path.relative_to(S).as_posix())
    archive.writestr("package_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
unpack = S.parent / "tmp" / ("submission-ready-verify-" + uuid.uuid4().hex[:8])
unpack.mkdir(parents=True)
target = Path("\\\\?\\" + str(unpack.resolve())) if os.name == "nt" else unpack
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    for info in archive.infolist():
        assert (unpack / info.filename).resolve().is_relative_to(unpack.resolve()), "unsafe archive path"
    archive.extractall(target)
extracted = json.loads((target / "package_manifest.json").read_text(encoding="utf-8"))
bad = [name for name, digest in extracted["files"].items() if sha(target / name) != digest]
assert not bad, bad
assert not any("/data/raw/" in name for name in extracted["files"])
result = {
    "status": "PASS",
    "archive": str(destination),
    "archive_sha256": sha(destination),
    "archive_bytes": destination.stat().st_size,
    "files_verified_after_extraction": len(extracted["files"]),
    "extraction_directory": str(unpack),
    "hash_mismatches": bad,
    "zip_crc_check": True,
    "third_party_raw_data_excluded": True,
}
destination.with_suffix(".verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
destination.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
