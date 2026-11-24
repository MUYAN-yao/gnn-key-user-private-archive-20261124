"""Create a read-only provenance manifest for one or more frozen study folders."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import networkx
import numpy
import pandas
import sklearn
import torch


ROOT = Path(__file__).parents[1]
CODE_FILES = (
    "backend/app/model.py",
    "backend/app/pipeline.py",
    "backend/app/graph.py",
    "backend/app/optimizer.py",
    "backend/app/baselines.py",
    "backend/app/validation.py",
    "experiments/run_rolling_study.py",
    "experiments/summarize_study.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_hashes(study: Path) -> dict[str, str]:
    runs = sorted(study.glob("split-*-seed-*.json"))
    if not runs:
        raise ValueError(f"No per-run JSON files found in {study}")
    dataset_path = Path(json.loads(runs[0].read_text(encoding="utf-8"))["config"].get("dataset", ""))
    # The frozen run files do not retain a dataset path. Resolve the known study
    # families explicitly, then hash the raw tabular inputs rather than rely on
    # a path embedded after the fact.
    if "higgs" in study.name:
        dataset_path = ROOT / "data/processed/higgs-twitter/pilot-50000"
    elif "digg" in study.name:
        dataset_path = ROOT / "data/processed/digg/pilot-20000"
    else:
        raise ValueError(f"Cannot infer dataset path for study {study.name}")
    return {str(dataset_path / name): sha256(dataset_path / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}


def study_record(path: Path) -> dict[str, object]:
    runs = sorted(path.glob("split-*-seed-*.json"))
    configs = [json.loads(run.read_text(encoding="utf-8"))["config"] for run in runs]
    aggregate = path / "aggregate_statistics.json"
    return {
        "study_directory": str(path),
        "run_count": len(runs),
        "run_sha256": {run.name: sha256(run) for run in runs},
        "aggregate_statistics_sha256": sha256(aggregate) if aggregate.exists() else None,
        "unique_non_seed_configs": sorted(
            {json.dumps({key: value for key, value in config.items() if key != "random_seed"}, sort_keys=True) for config in configs}
        ),
        "seeds": sorted({config["random_seed"] for config in configs}),
        "dataset_sha256": dataset_hashes(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--studies", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error(f"Refusing to overwrite existing manifest: {output}")
    studies = [study_record(Path(value)) for value in args.studies]
    manifest = {
        "purpose": "Read-only provenance manifest for frozen study artifacts.",
        "code_sha256": {relative: sha256(ROOT / relative) for relative in CODE_FILES},
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": numpy.__version__,
            "pandas": pandas.__version__,
            "scikit_learn": sklearn.__version__,
            "networkx": networkx.__version__,
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda,
        },
        "studies": studies,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
