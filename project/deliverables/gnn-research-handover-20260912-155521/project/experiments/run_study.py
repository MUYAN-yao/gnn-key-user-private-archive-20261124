"""Run one reproducible experiment configuration and save a JSON result.

Example:
python experiments/run_study.py --dataset sample_data --output results/sample.json --seed-count 3
"""
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.contracts import AnalysisConfig
from app.pipeline import run_analysis
from app.validation import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed-count", type=int, default=5)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--ants", type=int, default=18)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--simulations", type=int, default=30)
    parser.add_argument("--train-fraction", type=float, default=0.70)
    parser.add_argument("--optimizer", choices=["robust_greedy", "aco"], default="robust_greedy")
    parser.add_argument("--candidate-pool-size", type=int, default=120)
    args = parser.parse_args()
    config = AnalysisConfig(
        seed_count=args.seed_count,
        random_seed=args.random_seed,
        epochs=args.epochs,
        ants=args.ants,
        iterations=args.iterations,
        simulations=args.simulations,
        train_fraction=args.train_fraction,
        optimizer=args.optimizer,
        candidate_pool_size=args.candidate_pool_size,
    )
    result = run_analysis(load_dataset(args.dataset), config)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
