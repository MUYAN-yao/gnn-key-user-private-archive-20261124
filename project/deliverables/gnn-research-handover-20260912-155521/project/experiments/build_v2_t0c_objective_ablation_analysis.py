"""Build strict paired analysis for the completed v2-T0c objective ablation.

This script is intentionally read-only with respect to experiment artifacts.
It refuses partial studies and writes a fresh analysis directory only after
validating the v2-T0c and v2-T0b manifests against their run files.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from run_v2_t0c_objective_ablation import (  # noqa: E402
    ARMS,
    FRACTIONS,
    FULL_OBJECTIVE,
    REFERENCE_METHOD,
    SEEDS,
    run_id,
    sha256,
    validate_reference,
)


def exact_sign_flip_pvalue(differences: np.ndarray) -> float:
    observed = abs(float(differences.mean()))
    null_means = np.fromiter(
        (abs(float(np.dot(signs, differences) / len(differences))) for signs in product((-1, 1), repeat=len(differences))),
        dtype=float,
    )
    return float(np.mean(null_means >= observed - 1e-12))


def holm_adjust(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(pvalues) - rank) * pvalues[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def summary(differences: np.ndarray) -> dict[str, float | int]:
    if len(differences) != len(SEEDS):
        raise ValueError(f"Expected {len(SEEDS)} paired differences, found {len(differences)}")
    mean = float(differences.mean())
    sd = float(differences.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(differences) - 1) * sd / np.sqrt(len(differences)))
    return {
        "mean_difference": mean,
        "sd_difference": sd,
        "ci_low": mean - half,
        "ci_high": mean + half,
        "cohen_dz": mean / sd if sd else float("inf") if mean else 0.0,
        "exact_sign_flip_p": exact_sign_flip_pvalue(differences),
        "wins": int(np.sum(differences > 0)),
        "ties": int(np.sum(np.isclose(differences, 0.0))),
        "losses": int(np.sum(differences < 0)),
    }


def validate_ablation(study_dir: Path, reference_dir: Path) -> pd.DataFrame:
    references = validate_reference(reference_dir)
    manifest_path = study_dir / "manifest.json"
    metrics_path = study_dir / "method_metrics.csv"
    if not manifest_path.is_file() or not metrics_path.is_file():
        raise ValueError("The ablation study requires manifest.json and method_metrics.csv")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("reference", {}).get("manifest_sha256") != sha256(reference_dir / "manifest.json"):
        raise ValueError("The ablation does not point to the supplied v2-T0b reference manifest")
    expected_paths = {
        f"{arm}/{run_id(fraction, seed)}.json"
        for arm in ARMS for fraction in FRACTIONS for seed in SEEDS
    }
    recorded_paths = set((manifest.get("runs") or {}).keys())
    if recorded_paths != expected_paths:
        missing = sorted(expected_paths - recorded_paths)
        unexpected = sorted(recorded_paths - expected_paths)
        raise ValueError(f"Ablation run set is incomplete or unexpected; missing={missing}, unexpected={unexpected}")
    records: list[dict] = []
    for relative in sorted(expected_paths):
        path = study_dir / relative
        if not path.is_file():
            raise ValueError(f"Missing ablation artifact: {relative}")
        if manifest["runs"].get(relative) != sha256(path):
            raise ValueError(f"Ablation artifact hash mismatch: {relative}")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        arm, name = relative.split("/")
        _, fraction_text, _, seed_text = name.removesuffix(".json").split("-")
        fraction, seed = float(fraction_text), int(seed_text)
        expected_config = {
            "seed_count": 2, "horizon": 4, "risk_lambda": ARMS[arm]["risk_lambda"],
            "community_weight": ARMS[arm]["community_weight"], "diffusion_model": "ic",
            "random_seed": seed, "epochs": 10, "ants": 3, "iterations": 2,
            "simulations": 20, "train_fraction": fraction, "optimizer": "robust_greedy",
            "candidate_pool_size": 120,
        }
        if artifact.get("arm") != arm or artifact.get("config") != expected_config:
            raise ValueError(f"Ablation configuration mismatch: {relative}")
        if artifact.get("reporting_objective") != FULL_OBJECTIVE:
            raise ValueError(f"Ablation reporting objective mismatch: {relative}")
        repro = artifact.get("reproducibility", {})
        if repro.get("evaluation_protocol") != "common_random_numbers":
            raise ValueError(f"Missing common-random-number record: {relative}")
        if repro.get("probability_protocol") != "v2_t0b_timestamp_grouped_isotonic":
            raise ValueError(f"Probability protocol mismatch: {relative}")
        if repro.get("calibration_cutoff") >= repro.get("outer_test_start"):
            raise ValueError(f"Timestamp ordering violation: {relative}")
        values = artifact.get("result", {}).get("full_objective_evaluation", {})
        if set(values) != {"top_k", "mean_spread", "spread_std", "robust_objective", "community_coverage"}:
            raise ValueError(f"Full-objective result payload mismatch: {relative}")
        reference = artifact.get("reference", {})
        identifier = run_id(fraction, seed)
        expected_reference = references[identifier]["result"]
        if reference.get("method") != REFERENCE_METHOD or reference.get("full_objective") != {
            "mean_spread": expected_reference["mean_spread"],
            "spread_std": expected_reference["spread_std"],
            "robust_objective": expected_reference["robust_objective"],
            "community_coverage": expected_reference["community_coverage"],
        }:
            raise ValueError(f"Reference payload mismatch: {relative}")
        records.append({
            "run_id": identifier, "train_fraction": fraction, "random_seed": seed,
            "arm": arm, "ablation_robust_objective": values["robust_objective"],
            "reference_robust_objective": expected_reference["robust_objective"],
        })
    data = pd.DataFrame(records)
    metrics = pd.read_csv(metrics_path)
    required = {
        "run_id", "train_fraction", "random_seed", "arm", "method", "mean_spread",
        "spread_std", "robust_objective", "community_coverage", "runtime_seconds",
    }
    if set(metrics.columns) != required or len(metrics) != len(records):
        raise ValueError("Ablation method_metrics.csv does not match the preregistered schema")
    joined = data.merge(
        metrics[["run_id", "arm", "robust_objective"]], on=["run_id", "arm"],
        how="left", validate="one_to_one", suffixes=("", "_csv"),
    )
    if joined["robust_objective"].isna().any() or not np.allclose(
        joined["ablation_robust_objective"].astype(float), joined["robust_objective"].astype(float), rtol=0.0, atol=1e-12
    ):
        raise ValueError("Ablation method_metrics.csv does not match the run artifacts")
    return data


def paired_rows(data: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for fraction in FRACTIONS:
        for arm in ARMS:
            subset = data[(np.isclose(data.train_fraction, fraction)) & (data.arm == arm)].set_index("run_id")
            ids = [run_id(fraction, seed) for seed in SEEDS]
            if set(subset.index) != set(ids):
                raise ValueError(f"Missing paired runs for {fraction:.2f}/{arm}")
            differences = (
                subset.loc[ids, "reference_robust_objective"].to_numpy(float)
                - subset.loc[ids, "ablation_robust_objective"].to_numpy(float)
            )
            rows.append({
                "train_fraction": fraction, "arm": arm, "run_ids": ids,
                "differences": differences.tolist(), **summary(differences),
            })
    adjusted = holm_adjust([float(row["exact_sign_flip_p"]) for row in rows])
    for row, value in zip(rows, adjusted):
        row["holm_adjusted_p"] = value
    return rows


def make_figures(rows: list[dict], output_dir: Path) -> None:
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    labels = {"risk_off": "Risk off", "community_off": "Community off", "spread_only": "Both off"}
    colors = {"risk_off": "#4C78A8", "community_off": "#F58518", "spread_only": "#54A24B"}
    figure, axes = plt.subplots(1, 3, figsize=(14, 5.5), constrained_layout=True)
    for axis, fraction in zip(axes, FRACTIONS):
        subset = [row for row in rows if row["train_fraction"] == fraction]
        means = [float(row["mean_difference"]) for row in subset]
        errors = np.asarray([
            [float(row["mean_difference"]) - float(row["ci_low"]) for row in subset],
            [float(row["ci_high"]) - float(row["mean_difference"]) for row in subset],
        ])
        axis.barh(np.arange(len(subset)), means, xerr=errors, capsize=3,
                  color=[colors[row["arm"]] for row in subset])
        axis.axvline(0, color="#222222", linewidth=0.8)
        axis.set_yticks(np.arange(len(subset)), [labels[row["arm"]] for row in subset])
        axis.invert_yaxis()
        axis.set_title(f"Train fraction {fraction:.2f}")
        axis.set_xlabel("Full objective: v2-T0b minus ablation")
        axis.grid(axis="x", color="#dddddd", linewidth=0.7)
    figure.savefig(figure_dir / "figure-01-objective-ablation-paired-differences.pdf", bbox_inches="tight")
    figure.savefig(figure_dir / "figure-01-objective-ablation-paired-differences.png", dpi=240, bbox_inches="tight")
    plt.close(figure)


def write_reports(rows: list[dict], output_dir: Path) -> None:
    labels = {"risk_off": "Risk penalty removed", "community_off": "Community reward removed", "spread_only": "Both terms removed"}
    lines = []
    for row in rows:
        dz = "infinite" if np.isinf(float(row["cohen_dz"])) else f"{float(row['cohen_dz']):.2f}"
        lines.append(
            f"| {float(row['train_fraction']):.2f} | {labels[row['arm']]} | "
            f"{float(row['mean_difference']):.3f} +/- {float(row['sd_difference']):.3f} | "
            f"[{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] | "
            f"{row['wins']}/{row['ties']}/{row['losses']} | {float(row['exact_sign_flip_p']):.6f} | "
            f"{float(row['holm_adjusted_p']):.6f} | {dz} |"
        )
    report = f"""# Higgs v2-T0c Objective-Ablation Analysis

## Question and Unit

For each strict timestamp-grouped Higgs fraction, does selection with the
complete v2-T0b objective differ from selection after removing one or both
explicit objective terms? The unit is one matched stochastic protocol run.
Every compared pair uses the same fraction, seed, time windows, and common
random diffusion streams. All seeds are evaluated under the same full objective
`mean spread - 0.35 * spread SD + 0.25 * community coverage`.

## Exact Numerical Summary

Difference is `v2-T0b full objective - ablation`; positive values favor the
complete objective. `W/T/L` counts run-level wins, ties, and losses. Holm
correction spans the 9 preregistered fraction-by-arm contrasts.

| Train fraction | Ablation | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact sign-flip p | Holm p | Cohen dz |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(lines)}

## Claim Boundary

- Allowed wording: state only contrasts whose Holm-adjusted result supports
  the specified direction, and only for this timestamp-grouped Higgs protocol.
- Forbidden wording: universal importance of either term, causal diffusion
  interpretation, cross-dataset generalization, or an optimal weight claim.
- Uncertainty: one network dataset and ten stochastic paired runs per
  fraction; candidate-pool and diffusion settings remain fixed.
"""
    appendix = """# Statistical Appendix: v2-T0c Objective Ablation

- Input validation requires all 90 new artifacts, their manifest hashes, the
  completed 30-run v2-T0b reference manifest, and a matching metrics table.
- The primary metric is the common full robust objective, higher is better.
- Each contrast uses an exact two-sided sign-flip randomization test over all
  2^10 sign assignments. Holm correction covers all 9 preregistered contrasts.
- A 95% t interval and paired Cohen dz are descriptive complements to the
  exact test. Seeds quantify protocol stochasticity, not independent networks.
"""
    catalog = """# Figure Catalog

## Figure 1: Paired Objective-Ablation Differences

- File: `figures/figure-01-objective-ablation-paired-differences.pdf`
- Purpose: show whether removing the risk term, community term, or both
  changes the common full-objective score at every strict temporal fraction.
- Error bars: 95% t intervals across ten matched protocol runs.
- Interpretation: read alongside the exact sign-flip and Holm-corrected table;
  do not infer an effect from a positive mean alone.
"""
    (output_dir / "analysis-report.md").write_text(report, encoding="utf-8")
    (output_dir / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output_dir / "figure-catalog.md").write_text(catalog, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--reference-dir", default="results/large-robust-greedy-higgs-50000-v2-t0b")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error("Refusing to overwrite a non-empty analysis directory")
    data = validate_ablation(Path(args.study_dir), Path(args.reference_dir))
    rows = paired_rows(data)
    output.mkdir(parents=True, exist_ok=False)
    make_figures(rows, output)
    write_reports(rows, output)
    (output / "paired_comparisons.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote v2-T0c objective-ablation analysis to {output}")


if __name__ == "__main__":
    main()
