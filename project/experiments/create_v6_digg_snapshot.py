"""Create the required immutable v6 source snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.v6_digg_snapshot import MANIFEST, create, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot-dir', required=True)
    args = parser.parse_args()
    output = Path(args.snapshot_dir)
    manifest = create(ROOT, output)
    print(json.dumps({'status': 'PASS', 'snapshot_id': manifest['snapshot_id'],
                      'manifest_sha256': sha256(output / MANIFEST),
                      'file_count': len(manifest['files'])}, indent=2))


if __name__ == '__main__':
    main()
