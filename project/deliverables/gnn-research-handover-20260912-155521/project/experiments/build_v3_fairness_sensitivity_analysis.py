"""Create a strict, separate analysis bundle for a completed v3 study.

This script rejects smoke tests and partial result directories. It never writes
inside the study directory or any frozen v1/v2 analysis directory.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from run_v3_fairness_sensitivity import COMMUNITY_WEIGHTS, FRACTIONS, POOL_SIZES, RISK_LAMBDAS, SEEDS, run_id


PRIMARY = "screened_robust_greedy"
FULL = "full_candidate_robust_greedy"
BASE_POOL = "screened_pool_120"
WEIGHT_BASE = "objective_risk-0.35_community-0.25"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_sign_flip_pvalue(differences: np.ndarray) -> float:
    observed = abs(float(differences.mean()))
    null = np.fromiter(
        (abs(float(np.dot(signs, differences) / len(differences))) for signs in product((-1, 1), repeat=len(differences))),
        dtype=float,
    )
    return float(np.mean(null >= observed - 1e-12))


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
        raise ValueError(f"Expected {len(SEEDS)} paired runs, found {len(differences)}")
    mean, sd = float(differences.mean()), float(differences.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(differences) - 1) * sd / np.sqrt(len(differences)))
    return {
        "mean_difference": mean, "sd_difference": sd,
        "ci_low": mean - half, "ci_high": mean + half,
        "cohen_dz": mean / sd if sd else float("inf") if mean else 0.0,
        "exact_sign_flip_p": exact_sign_flip_pvalue(differences),
        "wins": int(np.sum(differences > 0)), "ties": int(np.sum(np.isclose(differences, 0.0))),
        "losses": int(np.sum(differences < 0)),
    }


def expected_run_ids() -> set[str]:
    return {run_id(fraction, seed) for fraction in FRACTIONS for seed in SEEDS}


def expected_methods() -> set[str]:
    pools = {f"screened_pool_{pool}" for pool in POOL_SIZES}
    weights = {f"objective_risk-{risk:.2f}_community-{community:.2f}" for risk in RISK_LAMBDAS for community in COMMUNITY_WEIGHTS}
    return {PRIMARY, FULL, "gnn_top_k_protected_lower_bound_audit", *pools, *weights}


def jaccard(left: list[object], right: list[object]) -> float:
    left_set, right_set = set(map(str, left)), set(map(str, right))
    union = left_set | right_set
    return len(left_set & right_set) / len(union) if union else 1.0


def validate(study_dir: Path) -> pd.DataFrame:
    manifest_path, metrics_path = study_dir / "manifest.json", study_dir / "method_metrics.csv"
    if not manifest_path.is_file() or not metrics_path.is_file():
        raise ValueError("A completed v3 manifest and method_metrics.csv are required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("study_version") != "v3-fairness-sensitivity" or manifest.get("smoke_test"):
        raise ValueError("Smoke or non-v3 artifacts are not eligible for v3 inferential analysis")
    if manifest.get("run_parameters", {}).get("full_candidate_limit") is not None:
        raise ValueError("The full-candidate comparator is bounded; this is not a completed fairness study")
    paths = {path.stem: path for path in study_dir.glob("split-*.json")}
    if set(paths) != expected_run_ids():
        raise ValueError("v3 study does not contain exactly the preregistered 30 run artifacts")
    if set(manifest.get("runs", {})) != {path.name for path in paths.values()}:
        raise ValueError("v3 manifest run set does not match the run artifacts")
    expected = expected_methods()
    rows: list[dict[str, object]] = []
    for identifier, path in paths.items():
        if manifest["runs"].get(path.name) != sha256(path):
            raise ValueError(f"Manifest hash mismatch: {path.name}")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        if artifact.get("smoke_test", {}).get("is_smoke"):
            raise ValueError(f"Smoke artifact present: {identifier}")
        repro = artifact.get("reproducibility", {})
        if not repro.get("selection_evaluation_worlds_disjoint"):
            raise ValueError(f"World families are not disjoint: {identifier}")
        if repro.get("calibration_cutoff") >= repro.get("outer_test_start"):
            raise ValueError(f"Timestamp ordering violation: {identifier}")
        methods = artifact.get("methods", {})
        if set(methods) != {"screened_robust_greedy", "full_candidate_robust_greedy", "gnn_top_k_protected_lower_bound_audit", "candidate_pool_sensitivity", "objective_weight_sensitivity"}:
            raise ValueError(f"Unexpected method groups: {identifier}")
        full = methods["full_candidate_robust_greedy"]
        if full.get("selection_scope") != "full_decision_graph":
            raise ValueError(f"Full-candidate scope missing: {identifier}")
        if methods["gnn_top_k_protected_lower_bound_audit"].get("interpretation") != "protected_lower_bound_audit_not_independent_baseline":
            raise ValueError(f"GNN Top-K audit boundary missing: {identifier}")
        full_top_k = list(full.get("selection", {}).get("top_k", []))
        base_top_k = list(methods[PRIMARY].get("selection", {}).get("top_k", []))
        if not full_top_k or not base_top_k:
            raise ValueError(f"Selection sets missing: {identifier}")
        records = {
            PRIMARY: methods["screened_robust_greedy"],
            FULL: full,
            "gnn_top_k_protected_lower_bound_audit": methods["gnn_top_k_protected_lower_bound_audit"],
            **{f"screened_pool_{key}": value for key, value in methods["candidate_pool_sensitivity"].items()},
            **{f"objective_{key}": value for key, value in methods["objective_weight_sensitivity"].items()},
        }
        if set(records) != expected:
            raise ValueError(f"Method rows differ from preregistration: {identifier}")
        for method, values in records.items():
            evaluation = values.get("reporting_evaluation", {})
            if set(evaluation) != {"top_k", "mean_spread", "spread_std", "robust_objective", "community_coverage"}:
                raise ValueError(f"Incomplete reporting evaluation: {identifier}/{method}")
            selected_top_k = list(evaluation["top_k"])
            full_overlap = jaccard(selected_top_k, full_top_k)
            base_overlap = jaccard(selected_top_k, base_top_k)
            if method.startswith("screened_pool_"):
                recorded = values.get("overlap_with_full_candidate", {})
                if not np.isclose(float(recorded.get("jaccard", -1.0)), full_overlap):
                    raise ValueError(f"Full-candidate overlap mismatch: {identifier}/{method}")
            if method.startswith("objective_"):
                recorded = values.get("overlap_with_base_screened", {})
                if not np.isclose(float(recorded.get("jaccard", -1.0)), base_overlap):
                    raise ValueError(f"Base-screened overlap mismatch: {identifier}/{method}")
            rows.append({
                "run_id": identifier, "train_fraction": artifact["config"]["train_fraction"],
                "random_seed": artifact["config"]["random_seed"], "method": method,
                **evaluation,
                "selection_seconds": values.get("selection_seconds", 0.0),
                "top_k": json.dumps(selected_top_k, ensure_ascii=False),
                "jaccard_with_full_candidate": full_overlap,
                "jaccard_with_base_screened": base_overlap,
            })
    frame = pd.DataFrame(rows)
    if frame.duplicated(["run_id", "method"]).any() or len(frame) != len(expected_run_ids()) * len(expected):
        raise ValueError("Run-method table is incomplete or duplicated")
    return frame


def paired_rows(data: pd.DataFrame, reference: str, comparators: list[str], family: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fraction in FRACTIONS:
        subset = data[np.isclose(data["train_fraction"].astype(float), fraction)]
        ref = subset[subset["method"] == reference].set_index("run_id")["robust_objective"]
        for comparator in comparators:
            other = subset[subset["method"] == comparator].set_index("run_id")["robust_objective"]
            identifiers = sorted(ref.index.intersection(other.index))
            differences = (ref.loc[identifiers] - other.loc[identifiers]).to_numpy(dtype=float)
            rows.append({
                "family": family, "train_fraction": fraction, "reference": reference,
                "comparator": comparator, "run_ids": identifiers, "differences": differences.tolist(),
                **summary(differences),
            })
    adjusted = holm_adjust([float(row["exact_sign_flip_p"]) for row in rows])
    for row, value in zip(rows, adjusted):
        row["holm_adjusted_p"] = value
    return rows


def make_figures(data: pd.DataFrame, primary_rows: list[dict[str, object]], pool_rows: list[dict[str, object]], weight_rows: list[dict[str, object]], output: Path) -> None:
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots(figsize=(7.5, 4.2), constrained_layout=True)
    means = [float(row["mean_difference"]) for row in primary_rows]
    errors = np.asarray([[mean - float(row["ci_low"]) for mean, row in zip(means, primary_rows)], [float(row["ci_high"]) - mean for mean, row in zip(means, primary_rows)]])
    labels = [f"{float(row['train_fraction']):.2f}" for row in primary_rows]
    axis.bar(labels, means, yerr=errors, capsize=4, color="#4C78A8")
    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.set_xlabel("Outer training fraction")
    axis.set_ylabel("Screened minus full-candidate robust objective")
    axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    fig.savefig(figures / "figure-01-screened-vs-full.pdf", bbox_inches="tight")
    fig.savefig(figures / "figure-01-screened-vs-full.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, len(FRACTIONS), figsize=(13, 4), sharey=True, constrained_layout=True)
    for axis, fraction in zip(axes, FRACTIONS):
        subset = [row for row in pool_rows if row["train_fraction"] == fraction]
        labels = [row["comparator"].replace("screened_pool_", "") for row in subset]
        values = [float(row["mean_difference"]) for row in subset]
        axis.bar(labels, values, color="#59A14F")
        axis.axhline(0, color="#333333", linewidth=0.8)
        axis.set_title(f"Fraction {fraction:.2f}")
        axis.set_xlabel("Pool size vs 120")
        axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    axes[0].set_ylabel("120-pool robust-objective difference")
    fig.savefig(figures / "figure-02-candidate-pool-sensitivity.pdf", bbox_inches="tight")
    fig.savefig(figures / "figure-02-candidate-pool-sensitivity.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, len(FRACTIONS), figsize=(13, 4), constrained_layout=True, sharey=True)
    for axis, fraction in zip(axes, FRACTIONS):
        matrix = np.zeros((len(RISK_LAMBDAS), len(COMMUNITY_WEIGHTS)))
        for row in weight_rows:
            if row["train_fraction"] != fraction:
                continue
            risk, community = row["comparator"].replace("objective_risk-", "").split("_community-")
            matrix[RISK_LAMBDAS.index(float(risk)), COMMUNITY_WEIGHTS.index(float(community))] = float(row["mean_difference"])
        image = axis.imshow(matrix, cmap="coolwarm", aspect="auto")
        axis.set_xticks(range(len(COMMUNITY_WEIGHTS)), [f"{value:.2f}" for value in COMMUNITY_WEIGHTS])
        axis.set_yticks(range(len(RISK_LAMBDAS)), [f"{value:.2f}" for value in RISK_LAMBDAS])
        axis.set_xlabel("Selection community weight")
        axis.set_ylabel("Selection risk lambda")
        axis.set_title(f"Fraction {fraction:.2f}")
        for y in range(matrix.shape[0]):
            for x in range(matrix.shape[1]):
                axis.text(x, y, f"{matrix[y, x]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=axes, label="Base minus weight-arm reporting objective")
    fig.savefig(figures / "figure-03-objective-weight-sensitivity.pdf", bbox_inches="tight")
    fig.savefig(figures / "figure-03-objective-weight-sensitivity.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def markdown_table(rows: list[dict[str, object]]) -> str:
    lines = ["| Family | Fraction | Reference | Comparator | Mean +/- SD | 95% t-CI | W/T/L | Exact p | Holm p | Cohen dz |", "| --- | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |"]
    for row in rows:
        dz = "infinite" if np.isinf(float(row["cohen_dz"])) else f"{float(row['cohen_dz']):.2f}"
        lines.append(
            f"| {row['family']} | {float(row['train_fraction']):.2f} | {row['reference']} | {row['comparator']} | "
            f"{float(row['mean_difference']):.3f} +/- {float(row['sd_difference']):.3f} | "
            f"[{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] | {row['wins']}/{row['ties']}/{row['losses']} | "
            f"{float(row['exact_sign_flip_p']):.6f} | {float(row['holm_adjusted_p']):.6f} | {dz} |"
        )
    return "\n".join(lines)


def descriptive_sensitivity(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate all preregistered reporting quantities without new tests."""
    rows: list[dict[str, object]] = []
    for fraction in FRACTIONS:
        subset = data[np.isclose(data["train_fraction"].astype(float), fraction)]
        for method in sorted(subset["method"].unique()):
            values = subset[subset["method"] == method]
            if len(values) != len(SEEDS):
                raise ValueError(f"Incomplete descriptive row: {fraction:.2f}/{method}")
            rows.append({
                "train_fraction": fraction,
                "method": method,
                "paired_run_count": len(values),
                "mean_spread_mean": values["mean_spread"].mean(),
                "mean_spread_sd": values["mean_spread"].std(ddof=1),
                "spread_std_mean": values["spread_std"].mean(),
                "spread_std_sd": values["spread_std"].std(ddof=1),
                "community_coverage_mean": values["community_coverage"].mean(),
                "community_coverage_sd": values["community_coverage"].std(ddof=1),
                "selection_seconds_mean": values["selection_seconds"].mean(),
                "selection_seconds_sd": values["selection_seconds"].std(ddof=1),
                "jaccard_with_full_candidate_mean": values["jaccard_with_full_candidate"].mean(),
                "jaccard_with_base_screened_mean": values["jaccard_with_base_screened"].mean(),
                "distinct_top_k_sets": values["top_k"].nunique(),
            })
    return pd.DataFrame(rows)


def descriptive_markdown(data: pd.DataFrame) -> str:
    lines = [
        "# v3 Reporting-Metric and Selection Summary",
        "",
        "These are descriptive summaries over ten paired protocol repetitions per",
        "timestamp fraction. They add no hypothesis tests or claims beyond the",
        "separate Holm-corrected families in `paired_comparisons.json`.",
        "",
        "| Fraction | Method | Mean spread +/- SD | Spread SD +/- SD | Community coverage +/- SD | Selection seconds +/- SD | Jaccard vs full | Jaccard vs base screened | Distinct Top-K sets |",
        "| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in data.to_dict(orient="records"):
        lines.append(
            f"| {float(row['train_fraction']):.2f} | {row['method']} | "
            f"{float(row['mean_spread_mean']):.3f} +/- {float(row['mean_spread_sd']):.3f} | "
            f"{float(row['spread_std_mean']):.3f} +/- {float(row['spread_std_sd']):.3f} | "
            f"{float(row['community_coverage_mean']):.3f} +/- {float(row['community_coverage_sd']):.3f} | "
            f"{float(row['selection_seconds_mean']):.3f} +/- {float(row['selection_seconds_sd']):.3f} | "
            f"{float(row['jaccard_with_full_candidate_mean']):.3f} | "
            f"{float(row['jaccard_with_base_screened_mean']):.3f} | {int(row['distinct_top_k_sets'])} |"
        )
    return "\n".join(lines) + "\n"


def write_outputs(primary_rows: list[dict[str, object]], pool_rows: list[dict[str, object]], weight_rows: list[dict[str, object]], data: pd.DataFrame, output: Path) -> None:
    all_rows = primary_rows + pool_rows + weight_rows
    descriptives = descriptive_sensitivity(data)
    make_figures(data, primary_rows, pool_rows, weight_rows, output)
    report = f"""# Higgs v3 Fairness and Sensitivity Analysis

## Questions and Unit

The primary question asks whether GNN-screened robust greedy differs from an
independent full-decision-graph robust greedy search under the common reporting
objective. Candidate-pool and objective-weight sensitivity are separate
questions. Each contrast has ten paired stochastic protocol runs per strict
timestamp fraction; these are not independent social-network samples.

## Exact Numerical Summary

Difference is `reference - comparator`. Positive values favor the stated
reference. The three families each have their own Holm correction: three primary
fairness contrasts, nine pool contrasts, and twenty-four non-base weight-arm
contrasts. GNN Top-K is retained in the source artifacts only as a protected
lower-bound audit and is absent from every efficacy family.

{markdown_table(all_rows)}

## Reporting Metrics and Selection Changes

`sensitivity_descriptives.csv` and `sensitivity-descriptives.md` report the
held-out mean spread, spread standard deviation, community coverage, selection
time, selected-set overlap with the full search, selected-set overlap with the
base screened method, and the number of distinct selected Top-K sets. These
quantities are descriptive complements to the predeclared utility tests above.

## Claim Candidates

- Claim:
  - Source evidence: completed v3 hashes, run artifacts, and the primary
    fairness family above.
  - Allowed wording: only describe a direction when the corresponding Holm
    result supports it, and only for this Higgs v3 protocol.
  - Forbidden wording: GNN Top-K independent superiority, universal algorithmic
    superiority, independent network-population inference, or causal diffusion.
  - Decision: update the manuscript claim ledger only after all three families
    are reviewed.
"""
    appendix = """# Statistical Appendix: v3 Fairness and Sensitivity

- Input guard: exactly 30 non-smoke artifacts, matching hashes, strict
  timestamp boundaries, and disjoint selection/evaluation world digests.
- Primary metric: reporting robust objective with risk lambda 0.35 and
  community weight 0.25, evaluated only on held-out deterministic worlds.
- Test: exact two-sided sign-flip randomization across the ten paired runs.
- Interval and effect size: 95% t interval and paired Cohen dz, descriptive.
- Multiplicity: Holm correction is applied separately to the predeclared
  primary-fairness, pool-sensitivity, and weight-sensitivity families.
- Limitation: all inference is protocol-conditional and Higgs-only.
"""
    catalog = """# Figure Catalog

## Figure 1: Screened versus Full-Candidate Robust Greedy

- Purpose: display the primary fairness contrast with zero-centered intervals.
- Interpretation: inspect the three Holm-adjusted results before any claim.

## Figure 2: Candidate-Pool Sensitivity

- Purpose: show whether screening pool size changes the common reporting score.
- Interpretation: distinguish a candidate-screening effect from a protected
  GNN Top-K lower-bound audit.

## Figure 3: Objective-Weight Sensitivity

- Purpose: display the 3x3 selection-weight grid under one reporting utility.
- Interpretation: zero or unsupported differences are negative evidence, not
  proof that the terms are universally irrelevant.
"""
    (output / "analysis-report.md").write_text(report, encoding="utf-8")
    (output / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output / "figure-catalog.md").write_text(catalog, encoding="utf-8")
    (output / "paired_comparisons.json").write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    descriptives.to_csv(output / "sensitivity_descriptives.csv", index=False)
    (output / "sensitivity-descriptives.md").write_text(descriptive_markdown(descriptives), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error("Refusing to overwrite a non-empty analysis directory")
    data = validate(Path(args.study_dir))
    primary_rows = paired_rows(data, PRIMARY, [FULL], "primary_fairness")
    pool_rows = paired_rows(data, BASE_POOL, [f"screened_pool_{pool}" for pool in POOL_SIZES if pool != 120], "candidate_pool_sensitivity")
    weight_rows = paired_rows(data, WEIGHT_BASE, [method for method in sorted(expected_methods()) if method.startswith("objective_") and method != WEIGHT_BASE], "objective_weight_sensitivity")
    output.mkdir(parents=True, exist_ok=False)
    write_outputs(primary_rows, pool_rows, weight_rows, data, output)
    print(f"Wrote strict v3 fairness and sensitivity analysis to {output}")


if __name__ == "__main__":
    main()
