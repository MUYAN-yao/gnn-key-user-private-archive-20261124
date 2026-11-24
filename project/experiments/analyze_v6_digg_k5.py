"""Analyze only a complete, validated v6 Digg formal batch.

Outputs a new strict analysis bundle.  The study remains a conditional
simulated-selection experiment and does not support causal or online claims.
"""
from __future__ import annotations

import argparse
import csv
from html import escape
from itertools import product
import json
from pathlib import Path
from statistics import mean
import sys
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.validate_v6_digg_k5 import FORMAL_SEEDS, validate_study


PRIMARY_ARM = "gnn_pool_120"
SECONDARY_ARMS = ("gnn_pool_30", "gnn_pool_60", "weighted_out_degree_pool_120")
ALL_SCREENED = ("gnn_pool_30", "gnn_pool_60", "gnn_pool_120", "weighted_out_degree_pool_120")


def exact_sign_flip_pvalue(values: list[float]) -> float:
    observed = abs(mean(values))
    null = (abs(sum(sign * value for sign, value in zip(signs, values)) / len(values))
            for signs in product((-1, 1), repeat=len(values)))
    return float(sum(value >= observed - 1e-12 for value in null) / (2 ** len(values)))


def paired_summary(values: list[float]) -> dict[str, Any]:
    vector = np.asarray(values, dtype=float)
    if len(vector) != len(FORMAL_SEEDS):
        raise ValueError("v6 paired analysis requires exactly ten formal seeds")
    average = float(vector.mean())
    sd = float(vector.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(vector) - 1) * sd / np.sqrt(len(vector)))
    return {"n": len(vector), "mean_difference": average, "sd_difference": sd,
            "ci_low": average - half, "ci_high": average + half,
            "cohen_dz": None if sd == 0.0 else average / sd,
            "cohen_dz_status": "undefined_zero_variance" if sd == 0.0 else "defined",
            "exact_two_sided_sign_flip_p": exact_sign_flip_pvalue(vector.tolist()),
            "wins": int(np.sum(vector > 0.0)), "ties": int(np.sum(vector == 0.0)),
            "losses": int(np.sum(vector < 0.0)), "differences": vector.tolist()}


def holm_adjust(pvalues: list[float]) -> list[float]:
    order = np.argsort(np.asarray(pvalues, dtype=float), kind="stable")
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(pvalues) - rank) * float(pvalues[index]))
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def _rows(study_dir: Path) -> list[dict[str, str]]:
    with (study_dir / "method_metrics.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _contrast(rows: list[dict[str, str]], arm: str) -> dict[str, Any]:
    indexed = {(row["run_id"], row["method"]): row for row in rows}
    differences, exact = [], 0
    stability = {"positive": 0, "tie": 0, "negative": 0}
    for seed in FORMAL_SEEDS:
        run_id = f"seed-{seed}"
        full, screened = indexed[(run_id, "full_candidate")], indexed[(run_id, arm)]
        delta = round(float(screened["primary_robust_objective"]) - float(full["primary_robust_objective"]), 6)
        differences.append(delta)
        stable_delta = round(float(screened["stability_robust_objective"]) - float(full["stability_robust_objective"]), 6)
        stability["tie" if stable_delta == 0 else "positive" if stable_delta > 0 else "negative"] += 1
        exact += int(screened["top_k"] == full["top_k"] and delta == 0.0)
    return {"dataset_id": "digg", "screened_arm": arm, "reference_arm": "full_candidate",
            **paired_summary(differences), "exact_primary_preservation_blocks": exact,
            "stability_direction_counts": stability}


def _mean_costs(rows: list[dict[str, str]]) -> list[dict[str, float | str]]:
    result = []
    for arm in ("full_candidate", *ALL_SCREENED):
        matching = [row for row in rows if row["method"] == arm]
        result.append({"method": arm,
                       "mean_total_arm_seconds": float(np.mean([float(row["total_arm_seconds"]) for row in matching])),
                       "mean_search_seconds": float(np.mean([float(row["search_seconds"]) for row in matching]))})
    return result


def _records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    indexed = {(row["run_id"], row["method"]): row for row in rows}
    records = []
    for seed in FORMAL_SEEDS:
        run_id = f"seed-{seed}"
        full = indexed[(run_id, "full_candidate")]
        arms: dict[str, Any] = {}
        for arm in ALL_SCREENED:
            screened = indexed[(run_id, arm)]
            delta = round(float(screened["primary_robust_objective"]) - float(full["primary_robust_objective"]), 6)
            arms[arm] = {"ordered_top_k_match": screened["top_k"] == full["top_k"],
                         "top_k_jaccard": float(screened["top_k_jaccard_with_full"]),
                         "primary_objective_delta": delta}
        records.append({"run_id": run_id, "seed": seed, "arms": arms})
    return records


def _write_figure(primary: dict[str, Any], secondary: list[dict[str, Any]], output: Path) -> None:
    entries = [*secondary[:2], primary, secondary[2]]
    means = [entry["mean_difference"] for entry in entries]
    errors = [max(0.0, entry["ci_high"] - entry["mean_difference"]) for entry in entries]
    low = min(mean - error for mean, error in zip(means, errors))
    high = max(0.0, *(mean + error for mean, error in zip(means, errors)))
    padding = max(0.5, (high - low) * 0.12)
    low, high = low - padding, high + padding
    width, height = 960, 560
    left, right, top, bottom = 110, 45, 70, 130
    plot_height, plot_width = height - top - bottom, width - left - right
    def y(value: float) -> float:
        return top + (high - value) * plot_height / (high - low)
    ticks = sorted(set([round(low + (high - low) * index / 5, 1) for index in range(6)] + [0.0]))
    colors = ("#8da0cb", "#8da0cb", "#1b9e77", "#d95f02")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#202124}.small{font-size:13px}.axis{stroke:#555;stroke-width:1}.grid{stroke:#d9d9d9;stroke-width:1}</style>',
             f'<text x="{width/2}" y="30" text-anchor="middle" font-size="18">Digg k=5 paired candidate-reduction contrasts</text>',
             f'<text x="{width/2}" y="52" text-anchor="middle" class="small">Difference in primary robust objective versus full candidate; 95% paired t intervals</text>']
    for tick in ticks:
        yy = y(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.2f}" x2="{width-right}" y2="{yy:.2f}" class="grid"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.2f}" text-anchor="end" class="small">{tick:g}</text>')
    parts.append(f'<line x1="{left}" y1="{y(0):.2f}" x2="{width-right}" y2="{y(0):.2f}" stroke="#222" stroke-width="1.5"/>')
    for index, (entry, average, error, color) in enumerate(zip(entries, means, errors, colors)):
        center = left + (index + 0.5) * plot_width / len(entries)
        bar_width = 92
        top_y, zero_y, bottom_y = y(average), y(0.0), y(average)
        rect_y, rect_h = min(zero_y, top_y), abs(zero_y - top_y)
        parts.append(f'<rect x="{center-bar_width/2:.2f}" y="{rect_y:.2f}" width="{bar_width}" height="{max(rect_h, 1):.2f}" fill="{color}"/>')
        upper, lower = y(average + error), y(average - error)
        parts.append(f'<line x1="{center:.2f}" y1="{upper:.2f}" x2="{center:.2f}" y2="{lower:.2f}" stroke="#222" stroke-width="1.5"/>')
        parts.append(f'<line x1="{center-7:.2f}" y1="{upper:.2f}" x2="{center+7:.2f}" y2="{upper:.2f}" stroke="#222" stroke-width="1.5"/>')
        parts.append(f'<line x1="{center-7:.2f}" y1="{lower:.2f}" x2="{center+7:.2f}" y2="{lower:.2f}" stroke="#222" stroke-width="1.5"/>')
        parts.append(f'<text x="{center:.2f}" y="{height-bottom+28}" text-anchor="middle" class="small">{escape(entry["screened_arm"].replace("_", " "))}</text>')
    parts.extend([f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>',
                  f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>',
                  f'<text x="22" y="{height/2}" transform="rotate(-90 22 {height/2})" text-anchor="middle" class="small">Primary robust-objective difference</text>', '</svg>'])
    output.write_text("\n".join(parts) + "\n", encoding="utf-8")


def analyze(study_dir: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty analysis directory: {output_dir}")
    validation = validate_study(study_dir, "formal")
    if validation["status"] != "PASS":
        raise ValueError("formal batch is not valid: " + "; ".join(validation["errors"]))
    rows = _rows(study_dir)
    primary = _contrast(rows, PRIMARY_ARM)
    secondary = [_contrast(rows, arm) for arm in SECONDARY_ARMS]
    for entry, adjusted in zip(secondary, holm_adjust([item["exact_two_sided_sign_flip_p"] for item in secondary])):
        entry["holm_adjusted_p"] = adjusted
    report = {"study_version": "v6-digg-k5-analysis-1", "validated_formal_study": validation,
              "primary_contrast": primary, "secondary_contrasts": secondary,
              "block_records": _records(rows), "mean_arm_costs": _mean_costs(rows),
              "interpretation_guard": [
                  "This is a protocol-conditional paired Digg simulation result.",
                  "Exact equality is not evidence of equivalence.",
                  "Digg links are inferred exposure proxies; no causal or online claim is supported.",
                  "The comparison does not establish end-to-end acceleration or general GNN superiority."]}
    output_dir.mkdir(parents=True)
    (output_dir / "v6_digg_k5_analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (output_dir / "v6_digg_k5_block_records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["run_id", "seed", "arms_json"])
        writer.writeheader()
        for record in report["block_records"]:
            writer.writerow({"run_id": record["run_id"], "seed": record["seed"], "arms_json": json.dumps(record["arms"], sort_keys=True)})
    figures = output_dir / "figures"; figures.mkdir()
    _write_figure(primary, secondary, figures / "figure-01-primary-paired-delta.svg")
    (output_dir / "analysis-report.md").write_text(
        "# v6 Digg k=5 strict analysis\n\n"
        "The formal batch passed provenance and schema validation before analysis. "
        "The primary contrast is GNN pool 120 minus full-candidate robust objective across ten paired blocks. "
        "See the JSON report for complete values; claims remain conditional on this retrospective, simulated Digg protocol.\n",
        encoding="utf-8")
    (output_dir / "stats-appendix.md").write_text(
        "# Statistical appendix\n\n"
        "Primary contrast: GNN pool 120 versus full candidate. Secondary family: GNN pools 30/60 and weighted out-degree pool 120, Holm adjusted. "
        "Each summary reports ten paired seeds, paired t 95% interval, exact two-sided sign-flip p value, wins/ties/losses and Cohen's dz (undefined for zero variance).\n",
        encoding="utf-8")
    (output_dir / "figure-catalog.md").write_text(
        "# Figure catalog\n\n"
        "`figures/figure-01-primary-paired-delta.svg` shows each screened arm's paired primary-objective difference from full search with 95% paired t intervals. "
        "Its purpose is to assess preservation or loss under the fixed candidate pools; it does not establish equivalence or causal validity.\n",
        encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = analyze(Path(args.study_dir), Path(args.output_dir))
    print(json.dumps({"status": "PASS", "primary_n": report["primary_contrast"]["n"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
