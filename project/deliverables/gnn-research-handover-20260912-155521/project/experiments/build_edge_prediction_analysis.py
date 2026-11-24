"""Build a strict analysis bundle from audit_edge_prediction.py output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


METRICS = ("auc", "average_precision", "brier", "ece_10_bins", "inverse_probability_auc")


def mean_sd_ci(values: np.ndarray) -> tuple[float, float, float, float]:
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    half_width = float(stats.t.ppf(0.975, len(values) - 1) * sd / np.sqrt(len(values)))
    return mean, sd, mean - half_width, mean + half_width


def fraction_rows(report: dict) -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = {}
    for run in report["runs"]:
        rows.setdefault(f"{run['train_fraction']:.2f}", []).append(run)
    return rows


def wilcoxon_against_half(values: np.ndarray) -> tuple[float, float]:
    result = stats.wilcoxon(values - 0.5, alternative="two-sided", method="auto")
    return float(result.statistic), float(result.pvalue)


def make_figures(rows: dict[str, list[dict]], figures: Path) -> None:
    colors = {"0.60": "#1b9e77", "0.65": "#d95f02", "0.70": "#7570b3"}
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})

    fig, axis = plt.subplots(figsize=(7.0, 4.3), constrained_layout=True)
    for position, (fraction, runs) in enumerate(sorted(rows.items())):
        values = np.array([run["future_edge_prediction"]["auc"] for run in runs])
        seeds = np.array([run["random_seed"] for run in runs])
        jitter = (position - 1) * 0.10
        axis.scatter(seeds + jitter, values, s=40, color=colors[fraction], label=f"Train fraction {fraction}", zorder=3)
    axis.axhline(0.5, color="#444444", linestyle="--", linewidth=1, label="Random ranking")
    axis.set(xlabel="Training random seed", ylabel="Future-edge ROC-AUC", ylim=(0.25, 0.85))
    axis.legend(ncol=2, frameon=False, loc="upper left")
    axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    fig.savefig(figures / "figure-01-future-auc-by-seed.pdf", bbox_inches="tight")
    fig.savefig(figures / "figure-01-future-auc-by-seed.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.6), sharey=True, constrained_layout=True)
    for axis, (fraction, runs) in zip(axes, sorted(rows.items())):
        train = np.array([run["train_reconstruction"]["auc"] for run in runs])
        future = np.array([run["future_edge_prediction"]["auc"] for run in runs])
        seeds = [run["random_seed"] for run in runs]
        for index, (train_value, future_value) in enumerate(zip(train, future)):
            color = "#c43c39" if future_value < 0.5 else colors[fraction]
            axis.plot([0, 1], [train_value, future_value], color=color, alpha=0.6, linewidth=1.1)
            axis.scatter([0, 1], [train_value, future_value], color=color, s=20, zorder=3)
            if future_value < 0.5:
                axis.annotate(str(seeds[index]), (1, future_value), xytext=(4, 0), textcoords="offset points", fontsize=7, color=color)
        axis.axhline(0.5, color="#444444", linestyle="--", linewidth=0.8)
        axis.set_title(f"Train fraction {fraction}")
        axis.set_xticks([0, 1], ["Train reconstruction", "Future edges"])
        axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    axes[0].set_ylabel("ROC-AUC")
    axes[0].set_ylim(0.25, 1.02)
    fig.savefig(figures / "figure-02-train-to-future-gap.pdf", bbox_inches="tight")
    fig.savefig(figures / "figure-02-train-to-future-gap.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_bundle(report: dict, output: Path) -> None:
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    rows = fraction_rows(report)
    make_figures(rows, figures)

    table = []
    stats_lines = []
    for fraction, runs in sorted(rows.items()):
        future = np.array([run["future_edge_prediction"]["auc"] for run in runs])
        train = np.array([run["train_reconstruction"]["auc"] for run in runs])
        brier = np.array([run["future_edge_prediction"]["brier"] for run in runs])
        ece = np.array([run["future_edge_prediction"]["ece_10_bins"] for run in runs])
        inverse = np.array([run["future_edge_prediction"]["inverse_probability_auc"] for run in runs])
        future_mean, future_sd, future_low, future_high = mean_sd_ci(future)
        train_mean, train_sd, _, _ = mean_sd_ci(train)
        brier_mean, brier_sd, _, _ = mean_sd_ci(brier)
        ece_mean, ece_sd, _, _ = mean_sd_ci(ece)
        inverse_mean, inverse_sd, _, _ = mean_sd_ci(inverse)
        shapiro_w, shapiro_p = stats.shapiro(future)
        wilcoxon_w, wilcoxon_p = wilcoxon_against_half(future)
        sign_p = stats.binomtest(int(np.sum(future > 0.5)), len(future), 0.5, alternative="two-sided").pvalue
        unstable = [str(run["random_seed"]) for run in runs if run["future_edge_prediction"]["auc"] < 0.5]
        table.append(
            f"| {fraction} | {future_mean:.3f} +/- {future_sd:.3f} | [{future_low:.3f}, {future_high:.3f}] | "
            f"{train_mean:.3f} +/- {train_sd:.3f} | {brier_mean:.3f} +/- {brier_sd:.3f} | "
            f"{ece_mean:.3f} +/- {ece_sd:.3f} | {', '.join(unstable) or 'none'} |"
        )
        stats_lines.append(
            f"### Train fraction {fraction}\n\n"
            f"- Future AUC: mean {future_mean:.4f}, SD {future_sd:.4f}, 95% t-CI [{future_low:.4f}, {future_high:.4f}], n=10.\n"
            f"- Train reconstruction AUC: mean {train_mean:.4f}, SD {train_sd:.4f}.\n"
            f"- Future Brier: mean {brier_mean:.4f}, SD {brier_sd:.4f}; ECE: mean {ece_mean:.4f}, SD {ece_sd:.4f}.\n"
            f"- Inverted-score future AUC: mean {inverse_mean:.4f}, SD {inverse_sd:.4f}.\n"
            f"- Shapiro-Wilk on future AUC: W={shapiro_w:.4f}, p={shapiro_p:.4g}; normality is not supported at alpha=0.05.\n"
            f"- Two-sided Wilcoxon signed-rank test of future AUC against 0.5: W={wilcoxon_w:.4f}, p={wilcoxon_p:.4g}.\n"
            f"- Exact two-sided sign test: {int(np.sum(future > 0.5))}/10 seeds above 0.5, p={sign_p:.4g}.\n"
            f"- Below-random seeds: {', '.join(unstable) or 'none'}.\n"
        )

    analysis = f"""# Higgs Edge-Prediction Audit Analysis

## Question

Does the frozen 50k-node Higgs protocol produce temporally valid and stable
GNN edge probabilities? The unit of analysis is one stochastic model-training
run at a fixed temporal split (10 pre-registered seeds per split). These are
replicates of training randomness on the same dataset, not independent
datasets; inferential tests quantify seed instability only and do not support
population-wide claims about Higgs.

## Evidence Summary

| Train fraction | Future AUC (mean +/- SD) | 95% t-CI | Train AUC (mean +/- SD) | Future Brier (mean +/- SD) | Future ECE (mean +/- SD) | AUC < 0.5 seeds |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table)}

Train reconstruction is consistently high, whereas future-edge AUC has a
large seed-dependent spread. Seeds 42 and 48 score below 0.5 at every one of
the three temporal cutoffs. Their inverted scores exceed 0.5, so those runs
are directionally reversed on future edges rather than merely uninformative.

## Decision

The current frozen protocol supports reporting the influence-maximization
outcomes as empirical optimization results, subject to their existing baseline
and data-provenance caveats. It does **not** support a mechanism claim that
the learned edge probabilities are reliably calibrated predictors of future
interactions. Any model repair requires a new versioned protocol and a fresh
experiment batch; the frozen results remain unchanged.

## Claim Candidates

- Claim:
  - Source evidence: all 30 audit runs and Figures 1-2.
  - Allowed wording: "Temporal edge-prediction quality was seed-unstable; two
    seeds produced below-random future ranking at every evaluated cutoff."
  - Forbidden stronger wording: "The learned probabilities reliably predict
    future activation" or "the GNN is consistently temporally calibrated."
  - Uncertainty: results use one Higgs sample and balanced sampled non-edges.
  - Next check: version a temporal objective/validation protocol and rerun all
    influence comparisons under it.
  - Decision: revise.

- Claim:
  - Source evidence: deterministic audit-to-frozen AUC reconciliation.
  - Allowed wording: "The audit reproduces the frozen calibration outputs to
    the stored four-decimal precision."
  - Forbidden stronger wording: "Reproducibility establishes causal validity."
  - Uncertainty: this validates execution consistency, not suitability of the
    prediction target.
  - Next check: preserve the data hashes and code revision with future runs.
  - Decision: keep.
"""
    appendix = "# Statistical Appendix: Higgs Edge-Prediction Audit\n\n" + "\n".join(stats_lines) + """
## Test Scope and Limitations

- ROC-AUC is higher-is-better. Brier score and ECE are lower-is-better.
- Each future evaluation compares unique observed future edges with an equal
  number of uniformly sampled absent directed pairs, excluding all known past
  and future positives. This matches the frozen pipeline's evaluation design.
- Shapiro-Wilk rejects normality for the observed AUC distributions, so the
  Wilcoxon and exact sign tests are reported rather than a t-test. The three
  cutoff-specific tests are descriptive diagnostics; they are not a family of
  claims about different datasets, and no statistical winner claim is made.
- Training and future AUC use different edge sets. Their contrast demonstrates
  a generalization gap but is not a causal experiment.
- The same data split is reused across seeds. Consequently these intervals and
  p-values represent variability from stochastic optimization, not sampling
  uncertainty over the underlying social network.
"""
    catalog = """# Figure Catalog

## Figure 1: Future AUC by Seed

- File: `figures/figure-01-future-auc-by-seed.pdf`
- Purpose: show the full seed-level temporal ranking distribution rather than
  only a mean.
- Data source: `audits/higgs-edge-prediction-v1/audit_report.json`.
- Caption requirements: state 10 seeds per cutoff, point meaning, and dashed
  random-ranking reference. Report numerical means and 95% t-CIs in the
  accompanying table rather than obscuring the points with overlapping bands.
- Key observation: seeds 42 and 48 fall below 0.5 in all three cutoff panels.
- Interpretation checklist: readers should see that a favorable mean does not
  imply a stable probability model; the next decision is to version a repair
  protocol before causal probability claims.

## Figure 2: Train-to-Future AUC Gap

- File: `figures/figure-02-train-to-future-gap.pdf`
- Purpose: contrast reconstruction accuracy with time-forward predictive
  accuracy for every stochastic run.
- Data source: `audits/higgs-edge-prediction-v1/audit_report.json`.
- Caption requirements: identify paired seed lines, red below-random future
  runs, and the random-ranking reference.
- Key observation: high reconstruction AUC does not rule out reversed future
  ranking.
- Interpretation checklist: this changes the claim boundary from "predictive
  edge probabilities" to an unvalidated heuristic pending a new protocol.
"""
    (output / "analysis-report.md").write_text(analysis, encoding="utf-8")
    (output / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output / "figure-catalog.md").write_text(catalog, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-report", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite non-empty directory: {output}")
    output.mkdir(parents=True, exist_ok=False)
    report = json.loads(Path(args.audit_report).read_text(encoding="utf-8"))
    write_bundle(report, output)
    print(f"Wrote analysis bundle: {output}")


if __name__ == "__main__":
    main()
