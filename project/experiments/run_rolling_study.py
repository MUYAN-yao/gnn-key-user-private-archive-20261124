"""Run rolling temporal-split experiments and write per-run plus aggregate results.

Example:
python experiments/run_rolling_study.py --dataset data/processed/higgs-twitter/pilot-1500 --output-dir results/rolling-pilot
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.contracts import AnalysisConfig
from app.pipeline import run_analysis
from app.validation import load_dataset


def summary_row(run_id: str, result: dict) -> dict:
    return {
        "run_id": run_id,
        "train_fraction": result["config"]["train_fraction"],
        "random_seed": result["config"]["random_seed"],
        "main_method": result["result"].get("method", "gnn_aco"),
        "main_mean_spread": result["result"]["mean_spread"],
        "main_std_spread": result["result"]["spread_std"],
        "main_robust_objective": result["result"]["robust_objective"],
        "main_community_coverage": result["result"]["community_coverage"],
        "main_selection_seconds": result["result"].get("selection_seconds"),
        "gnn_mean_spread": result["baselines"]["gnn_top_k"]["mean_spread"],
        "gnn_robust_objective": result["baselines"]["gnn_top_k"]["robust_objective"],
        "gnn_community_coverage": result["baselines"]["gnn_top_k"]["community_coverage"],
        "greedy_mean_spread": result["baselines"]["greedy_mc"]["mean_spread"],
        "greedy_robust_objective": result["baselines"]["greedy_mc"]["robust_objective"],
        "greedy_community_coverage": result["baselines"]["greedy_mc"]["community_coverage"],
        "ris_mean_spread": result["baselines"]["ris_approx"]["mean_spread"],
        "ris_robust_objective": result["baselines"]["ris_approx"]["robust_objective"],
        "ris_community_coverage": result["baselines"]["ris_approx"]["community_coverage"],
        "runtime_seconds": result["runtime_seconds"],
    }


def method_rows(run_id: str, result: dict) -> list[dict]:
    methods = {result["result"].get("method", "gnn_aco"): result["result"], **result["baselines"]}
    return [{
        "run_id": run_id,
        "train_fraction": result["config"]["train_fraction"],
        "random_seed": result["config"]["random_seed"],
        "method": name,
        "mean_spread": values["mean_spread"],
        "spread_std": values["spread_std"],
        "robust_objective": values["robust_objective"],
        "community_coverage": values["community_coverage"],
        "runtime_seconds": result["runtime_seconds"],
    } for name, values in methods.items()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Directory containing nodes.csv, edges.csv, cascades.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46])
    parser.add_argument("--seed-count", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--ants", type=int, default=18)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--simulations", type=int, default=30)
    parser.add_argument("--resume", action="store_true", help="Reuse existing per-run JSON files.")
    parser.add_argument("--optimizer", choices=["robust_greedy", "aco"], default="robust_greedy")
    parser.add_argument("--candidate-pool-size", type=int, default=120)
    args = parser.parse_args()
    if any(not 0.50 <= fraction <= 0.90 for fraction in args.fractions):
        parser.error("Each --fractions value must be between 0.50 and 0.90.")

    dataset = load_dataset(Path(args.dataset))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    method_metrics: list[dict] = []
    for fraction in args.fractions:
        for random_seed in args.seeds:
            config = AnalysisConfig(
                seed_count=args.seed_count,
                train_fraction=fraction,
                random_seed=random_seed,
                epochs=args.epochs,
                ants=args.ants,
                iterations=args.iterations,
                simulations=args.simulations,
                optimizer=args.optimizer,
                candidate_pool_size=args.candidate_pool_size,
            )
            run_id = f"split-{fraction:.2f}-seed-{random_seed}"
            run_path = output_dir / f"{run_id}.json"
            if args.resume and run_path.exists():
                result = json.loads(run_path.read_text(encoding="utf-8"))
                print(f"{run_id} (reused)")
            else:
                result = run_analysis(dataset, config)
                run_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(run_id)
            summary.append(summary_row(run_id, result))
            method_metrics.extend(method_rows(run_id, result))
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]) if summary else [])
        writer.writeheader()
        writer.writerows(summary)
    with (output_dir / "method_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(method_metrics[0]) if method_metrics else [])
        writer.writeheader()
        writer.writerows(method_metrics)


if __name__ == "__main__":
    main()
