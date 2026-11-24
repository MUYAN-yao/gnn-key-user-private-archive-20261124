"""Build a hash inventory for an author-approved code-and-metadata release.

This script never creates an archive and never copies files. It writes only an
inventory after the completed v3 study and its strict analysis bundle pass
their gates. Raw or processed interaction data, result directories, logs, and
workspace-private paths are rejected rather than silently omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from build_v3_fairness_sensitivity_analysis import validate


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = (
    "data/raw/", "data/processed/", "results/", "tmp/", "logs/",
    "runtime-data/", "web/node_modules/", ".git/",
)
REQUIRED_ANALYSIS_FILES = {
    "analysis-report.md", "stats-appendix.md", "figure-catalog.md", "paired_comparisons.json",
    "sensitivity_descriptives.csv", "sensitivity-descriptives.md",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Release path must be a workspace-relative descendant: {value}")
    return path


def require_completed_evidence(study_dir: Path, analysis_dir: Path) -> None:
    validate(study_dir)
    missing = sorted(name for name in REQUIRED_ANALYSIS_FILES if not (analysis_dir / name).is_file())
    if missing:
        raise ValueError(f"Strict v3 analysis bundle is incomplete: {', '.join(missing)}")


def collect(paths: list[Path]) -> list[dict[str, object]]:
    files: list[Path] = []
    for relative in paths:
        normalized = relative.as_posix().rstrip("/") + "/"
        if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            raise ValueError(f"Forbidden release path: {relative.as_posix()}")
        absolute = ROOT / relative
        if not absolute.exists():
            raise FileNotFoundError(f"Requested release path does not exist: {relative.as_posix()}")
        files.extend(item for item in absolute.rglob("*") if item.is_file()) if absolute.is_dir() else files.append(absolute)
    entries = []
    for path in sorted(set(files)):
        relative = path.relative_to(ROOT).as_posix()
        if any(relative.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            raise ValueError(f"Forbidden file reached through requested path: {relative}")
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True, help="Completed non-smoke v3 result directory")
    parser.add_argument("--analysis-dir", required=True, help="Accepted strict v3 analysis directory")
    parser.add_argument("--output-dir", required=True, help="New, empty inventory-only output directory")
    parser.add_argument("--include", nargs="+", required=True, help="Author-approved workspace-relative files or directories")
    args = parser.parse_args()
    study_dir, analysis_dir, output_dir = Path(args.study_dir), Path(args.analysis_dir), Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        parser.error(f"Refusing to overwrite non-empty output directory: {output_dir}")
    require_completed_evidence(study_dir, analysis_dir)
    includes = [relative_path(value) for value in args.include]
    entries = collect(includes)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = {
        "release_scope": "code-and-metadata inventory only; no archive is created",
        "v3_study": str(study_dir),
        "v3_analysis": str(analysis_dir),
        "includes": [path.as_posix() for path in includes],
        "file_count": len(entries),
        "files": entries,
        "exclusions": list(FORBIDDEN_PREFIXES),
    }
    (output_dir / "release-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Public Release Inventory", "", "This is a hash inventory only; no archive was created.", "", f"Files: {len(entries)}", "", "| Path | Bytes | SHA-256 |", "| --- | ---: | --- |"]
    lines.extend(f"| `{item['path']}` | {item['bytes']} | `{item['sha256']}` |" for item in entries)
    (output_dir / "release-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} approved entries to {output_dir}")


if __name__ == "__main__":
    main()
