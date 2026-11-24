"""Create publication-ready paired statistics from a rolling-study output.

All methods in a run share common random diffusion streams.  The exact
sign-flip test therefore uses paired robust-objective differences, rather than
pretending independent Monte Carlo runs are comparable.
"""
from __future__ import annotations

import argparse
import csv
from itertools import product
import json
from pathlib import Path
from statistics import mean, stdev

import numpy as np


def bootstrap_ci(values: list[float], seed: int, rounds: int) -> list[float]:
    rng = np.random.default_rng(seed)
    sample = np.asarray(values, dtype=float)
    estimates = np.mean(rng.choice(sample, size=(rounds, len(sample)), replace=True), axis=1)
    return [round(float(np.quantile(estimates, 0.025)), 6), round(float(np.quantile(estimates, 0.975)), 6)]


def exact_sign_flip_pvalue(differences: list[float]) -> float | None:
    if not differences or len(differences) > 20:
        return None
    observed = abs(mean(differences))
    null_means = [abs(sum(sign * value for sign, value in zip(signs, differences)) / len(differences)) for signs in product((-1, 1), repeat=len(differences))]
    return round(sum(value >= observed - 1e-12 for value in null_means) / len(null_means), 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--bootstrap-rounds", type=int, default=10_000)
    parser.add_argument("--reference-method", default="gnn_guided_robust_greedy")
    args = parser.parse_args()
    study_dir = Path(args.study_dir)
    with (study_dir / "method_metrics.csv").open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["train_fraction"], row["method"]), []).append(row)

    report: dict[str, dict] = {}
    for (fraction, method), method_rows in sorted(groups.items()):
        key = f"split-{fraction}/{method}"
        objective = [float(row["robust_objective"]) for row in method_rows]
        spread = [float(row["mean_spread"]) for row in method_rows]
        coverage = [float(row["community_coverage"]) for row in method_rows]
        report[key] = {
            "train_fraction": float(fraction),
            "method": method,
            "runs": len(method_rows),
            "robust_objective": {"mean": round(mean(objective), 6), "std": round(stdev(objective), 6) if len(objective) > 1 else 0.0, "ci95": bootstrap_ci(objective, sum(key.encode("utf-8")), args.bootstrap_rounds)},
            "mean_spread": {"mean": round(mean(spread), 6), "std": round(stdev(spread), 6) if len(spread) > 1 else 0.0, "ci95": bootstrap_ci(spread, sum((key + "spread").encode("utf-8")), args.bootstrap_rounds)},
            "community_coverage": {"mean": round(mean(coverage), 6), "std": round(stdev(coverage), 6) if len(coverage) > 1 else 0.0},
        }

    for fraction in sorted({row["train_fraction"] for row in rows}):
        baseline = {row["run_id"]: float(row["robust_objective"]) for row in groups[(fraction, args.reference_method)]}
        for (group_fraction, method), method_rows in groups.items():
            if group_fraction != fraction or method == args.reference_method:
                continue
            paired = [float(row["robust_objective"]) - baseline[row["run_id"]] for row in method_rows if row["run_id"] in baseline]
            report[f"split-{fraction}/{method}"]["paired_vs_reference"] = {
                "difference_definition": f"method_minus_{args.reference_method}",
                "runs": len(paired),
                "mean_difference": round(mean(paired), 6) if paired else None,
                "exact_two_sided_sign_flip_p": exact_sign_flip_pvalue(paired),
            }
    output = study_dir / "aggregate_statistics.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
