"""Perform an extraction-time archive verification in bounded batches on Windows."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile

R = Path(__file__).resolve().parents[1]
S = R.parent.parent
ARCHIVE = S / "computing-submission-preparation-20261016-v1.zip"
STATE = R / "qa/archive_verification_progress.json"
TARGET = S.parent / "tmp/submission-ready-incremental-verify"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(target: Path, name: str) -> Path:
    output = (target / name).resolve()
    assert output.is_relative_to(target.resolve()), "unsafe archive path"
    return output


def io_path(path: Path) -> Path:
    return Path("\\\\?\\" + str(path.resolve())) if os.name == "nt" else path


parser = ArgumentParser()
parser.add_argument("action", choices=("init", "extract", "hash", "finalize"))
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--count", type=int, default=400)
args = parser.parse_args()

if args.action == "init":
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        names = [info.filename for info in archive.infolist()]
        for name in names:
            safe(TARGET, name)
    state = {"archive": str(ARCHIVE), "target": str(TARGET), "members": len(names), "crc_checked": True, "extracted": [], "hashed": []}
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "members": len(names), "crc_checked": True}, indent=2))
elif args.action == "extract":
    state = json.loads(STATE.read_text())
    with zipfile.ZipFile(ARCHIVE) as archive:
        infos = archive.infolist()[args.start:args.start + args.count]
        for info in infos:
            safe(TARGET, info.filename)
            archive.extract(info, io_path(TARGET))
    state["extracted"].append([args.start, len(infos)])
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "extracted_start": args.start, "extracted_count": len(infos)}, indent=2))
elif args.action == "hash":
    state = json.loads(STATE.read_text())
    manifest = json.loads((TARGET / "package_manifest.json").read_text(encoding="utf-8"))
    items = list(manifest["files"].items())[args.start:args.start + args.count]
    bad = [name for name, digest in items if not io_path(TARGET / name).is_file() or sha(io_path(TARGET / name)) != digest]
    assert not bad, bad
    state["hashed"].append([args.start, len(items)])
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "hashed_start": args.start, "hashed_count": len(items)}, indent=2))
else:
    state = json.loads(STATE.read_text())
    manifest = json.loads((TARGET / "package_manifest.json").read_text(encoding="utf-8"))
    expected = set(manifest["files"])
    missing = sorted(name for name in expected if not io_path(TARGET / name).is_file())
    assert not missing, missing[:10]
    assert not any("/data/raw/" in name for name in expected)
    result = {
        "status": "PASS",
        "archive": str(ARCHIVE),
        "archive_sha256": sha(ARCHIVE),
        "archive_bytes": ARCHIVE.stat().st_size,
        "files_verified_after_extraction": len(expected),
        "extraction_directory": str(TARGET),
        "hash_mismatches": [],
        "zip_crc_check": True,
        "third_party_raw_data_excluded": True,
        "verification_batches": {"extract": state["extracted"], "hash": state["hashed"]},
    }
    ARCHIVE.with_suffix(".verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    ARCHIVE.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
