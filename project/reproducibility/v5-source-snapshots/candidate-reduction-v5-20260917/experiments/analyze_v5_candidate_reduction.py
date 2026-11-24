"""Create the preregistered read-only v5 paired-analysis package.

The script refuses unvalidated batches and writes a new output directory.  It
does not turn exact equality into an equivalence claim.
"""
from __future__ import annotations

import argparse
import csv
from itertools import product
import json
from pathlib import Path
import sys
from statistics import mean
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.validate_v5_candidate_reduction import FORMAL_SEEDS, validate_study


DATASETS = ("higgs", "digg")
PRIMARY_ARM = "gnn_pool_120"
SECONDARY_ARMS = ("gnn_pool_30", "gnn_pool_60", "weighted_out_degree_pool_120")


def exact_sign_flip_pvalue(differences: list[float]) -> float:
    observed = abs(mean(differences))
    null_means = (
        abs(sum(sign * value for sign, value in zip(signs, differences)) / len(differences))
        for signs in product((-1, 1), repeat=len(differences))
    )
    return float(sum(value >= observed - 1e-12 for value in null_means) / (2 ** len(differences)))


def holm_adjust(pvalues: list[float]) -> list[float]:
    order = np.argsort(np.asarray(pvalues, dtype=float), kind="stable")
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(pvalues) - rank) * float(pvalues[index]))
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def paired_summary(differences: list[float]) -> dict[str, Any]:
    values = np.asarray(differences, dtype=float)
    if len(values) != len(FORMAL_SEEDS):
        raise ValueError("Formal paired summary requires exactly the ten preregistered seeds")
    average = float(values.mean())
    sd = float(values.std(ddof=1))
    half_width = float(stats.t.ppf(0.975, len(values) - 1) * sd / np.sqrt(len(values)))
    return {
        "n": len(values),
        "mean_difference": average,
        "sd_difference": sd,
        "ci_low": average - half_width,
        "ci_high": average + half_width,
        "cohen_dz": None if sd == 0.0 else average / sd,
        "cohen_dz_status": "undefined_zero_variance" if sd == 0.0 else "defined",
        "exact_two_sided_sign_flip_p": exact_sign_flip_pvalue(values.tolist()),
        "wins": int(np.sum(values > 0.0)),
        "ties": int(np.sum(values == 0.0)),
        "losses": int(np.sum(values < 0.0)),
        "differences": values.tolist(),
    }


def load_rows(study_dir: Path) -> list[dict[str, str]]:
    with (study_dir / "method_metrics.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def indexed_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["run_id"], row["method"]): row for row in rows}


def contrast(rows: list[dict[str, str]], dataset_id: str, arm: str) -> dict[str, Any]:
    indexed = indexed_rows(rows)
    differences: list[float] = []
    stability_directions: list[str] = []
    exact_primary_preservation = 0
    for seed in FORMAL_SEEDS:
        run_id = f"seed-{seed}"
        full = indexed[(run_id, "full_candidate")]
        screened = indexed[(run_id, arm)]
        delta = round(
            float(screened["primary_robust_objective"]) - float(full["primary_robust_objective"]), 6
        )
        differences.append(delta)
        stability_delta = round(
            float(screened["stability_robust_objective"]) - float(full["stability_robust_objective"]), 6
        )
        stability_directions.append("tie" if stability_delta == 0.0 else "positive" if stability_delta > 0 else "negative")
        if screened["top_k"] == full["top_k"] and delta == 0.0:
            exact_primary_preservation += 1
    return {
        "dataset_id": dataset_id,
        "screened_arm": arm,
        "reference_arm": "full_candidate",
        **paired_summary(differences),
        "exact_primary_preservation_blocks": exact_primary_preservation,
        "stability_direction_counts": {
            direction: stability_directions.count(direction)
            for direction in ("positive", "tie", "negative")
        },
    }


def block_records(rows: list[dict[str, str]], dataset_id: str) -> list[dict[str, Any]]:
    indexed = indexed_rows(rows)
    records: list[dict[str, Any]] = []
    for seed in FORMAL_SEEDS:
        run_id = f"seed-{seed}"
        full = indexed[(run_id, "full_candidate")]
        minimum_pool: int | None = None
        arms: dict[str, Any] = {}
        for arm, size in (("gnn_pool_30", 30), ("gnn_pool_60", 60), ("gnn_pool_120", 120)):
            screened = indexed[(run_id, arm)]
            primary_delta = round(float(screened["primary_robust_objective"]) - float(full["primary_robust_objective"]), 6)
            exact = screened["top_k"] == full["top_k"] and primary_delta == 0.0
            if exact and minimum_pool is None:
                minimum_pool = size
            arms[arm] = {
                "ordered_top_k_match": screened["top_k"] == full["top_k"],
                "top_k_jaccard": float(screened["top_k_jaccard_with_full"]),
                "primary_objective_delta": primary_delta,
                "stability_objective_delta": round(float(screened["stability_robust_objective"]) - float(full["stability_robust_objective"]), 6),
            }
        degree = indexed[(run_id, "weighted_out_degree_pool_120")]
        arms["weighted_out_degree_pool_120"] = {
            "ordered_top_k_match": degree["top_k"] == full["top_k"],
            "top_k_jaccard": float(degree["top_k_jaccard_with_full"]),
            "primary_objective_delta": round(float(degree["primary_robust_objective"]) - float(full["primary_robust_objective"]), 6),
            "stability_objective_delta": round(float(degree["stability_robust_objective"]) - float(full["stability_robust_objective"]), 6),
        }
        records.append({
            "dataset_id": dataset_id, "run_id": run_id, "seed": seed,
            "minimum_gnn_pool_with_exact_primary_preservation": minimum_pool,
            "arms": arms,
        })
    return records


def mean_costs(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for method in ("full_candidate", "gnn_pool_30", "gnn_pool_60", "gnn_pool_120", "weighted_out_degree_pool_120"):
        matching = [row for row in rows if row["method"] == method]
        result.append({
            "method": method,
            "mean_total_arm_seconds": float(np.mean([float(row["total_arm_seconds"]) for row in matching])),
            "mean_search_seconds": float(np.mean([float(row["search_seconds"]) for row in matching])),
            "mean_primary_evaluation_seconds": float(np.mean([float(row["primary_evaluation_seconds"]) for row in matching])),
            "mean_stability_evaluation_seconds": float(np.mean([float(row["stability_evaluation_seconds"]) for row in matching])),
        })
    return result


def analyze(study_root: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Refusing to overwrite non-empty analysis directory: {output_dir}")
    all_rows: dict[str, list[dict[str, str]]] = {}
    validation: dict[str, Any] = {}
    for dataset_id in DATASETS:
        study_dir = study_root / dataset_id
        report = validate_study(study_dir, "formal")
        validation[dataset_id] = report
        if report["status"] != "PASS":
            raise ValueError(f"{dataset_id} formal batch did not pass validation: {report['errors']}")
        all_rows[dataset_id] = load_rows(study_dir)
    primary = [contrast(all_rows[dataset_id], dataset_id, PRIMARY_ARM) for dataset_id in DATASETS]
    for entry, adjusted in zip(primary, holm_adjust([entry["exact_two_sided_sign_flip_p"] for entry in primary])):
        entry["holm_adjusted_p"] = adjusted
    secondary = [
        contrast(all_rows[dataset_id], dataset_id, arm)
        for dataset_id in DATASETS for arm in SECONDARY_ARMS
    ]
    for entry, adjusted in zip(secondary, holm_adjust([entry["exact_two_sided_sign_flip_p"] for entry in secondary])):
        entry["holm_adjusted_p"] = adjusted
    blocks = [record for dataset_id in DATASETS for record in block_records(all_rows[dataset_id], dataset_id)]
    report = {
        "study_version": "v5-candidate-reduction-analysis-1",
        "validated_formal_studies": validation,
        "primary_contrasts": primary,
        "secondary_contrasts": secondary,
        "failure_boundary_blocks": blocks,
        "mean_arm_costs": {dataset_id: mean_costs(rows) for dataset_id, rows in all_rows.items()},
        "interpretation_guard": [
            "This analysis reports protocol-conditional paired outcomes only.",
            "Exact equality is retained as equality and is not converted to statistical equivalence.",
            "Digg remains a conditional simulated-selection setting with inferred exposure-proxy links.",
            "The analysis does not establish causal propagation, online operation, GNN superiority, or end-to-end acceleration.",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "v5_candidate_reduction_analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    with (output_dir / "v5_failure_boundary_blocks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "dataset_id", "run_id", "seed", "minimum_gnn_pool_with_exact_primary_preservation", "arms_json"
        ])
        writer.writeheader()
        for record in blocks:
            writer.writerow({
                **{key: record[key] for key in ("dataset_id", "run_id", "seed", "minimum_gnn_pool_with_exact_primary_preservation")},
                "arms_json": json.dumps(record["arms"], ensure_ascii=False, sort_keys=True),
            })
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-root", required=True, help="Parent containing higgs/ and digg/ formal directories")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = analyze(Path(args.study_root), Path(args.output_dir))
    print(json.dumps({"status": "PASS", "primary_contrast_count": len(report["primary_contrasts"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
