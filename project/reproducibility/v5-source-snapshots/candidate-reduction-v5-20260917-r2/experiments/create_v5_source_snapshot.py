"""Create the immutable local source snapshot required before v5 execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.v5_source_snapshot import create_snapshot, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", required=True)
    args = parser.parse_args()
    snapshot_dir = Path(args.snapshot_dir)
    manifest = create_snapshot(ROOT, snapshot_dir)
    print(
        json.dumps(
            {
                "status": "PASS",
                "snapshot_dir": str(snapshot_dir.resolve()),
                "snapshot_id": manifest["snapshot_id"],
                "manifest_sha256": sha256(snapshot_dir / "snapshot_manifest.json"),
                "file_count": len(manifest["files"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
