"""Create an immutable source snapshot for the v10 confirmation runner."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.v10_source_snapshot import create


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create(args.source_root, args.snapshot), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
