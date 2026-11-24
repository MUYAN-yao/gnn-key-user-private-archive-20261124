"""Build a strict paired analysis bundle from frozen rolling-study artifacts."""
from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


REFERENCE = "gnn_guided_robust_greedy"
BASELINES = ("degree", "gnn_top_k", "greedy_mc", "ris_approx")
DISPLAY = {"degree": "Degree", "gnn_top_k": "GNN Top-K", "greedy_mc": "Greedy MC", "ris_approx": "RIS"}
COLORS = {"degree": "#4477aa", "gnn_top_k": "#66a61e", "greedy_mc": "#e6ab02", "ris_approx": "#d95f02"}


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


def summarize(differences: np.ndarray) -> dict[str, float]:
    sd = float(differences.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(differences) - 1) * sd / np.sqrt(len(differences)))
    return {
        "mean_difference": float(differences.mean()),
        "sd_difference": sd,
        "ci_low": float(differences.mean() - half),
        "ci_high": float(differences.mean() + half),
        "cohen_dz": float(differences.mean() / sd) if sd else float("inf") if differences.mean() else 0.0,
        "exact_sign_flip_p": exact_sign_flip_pvalue(differences),
        "wins": int(np.sum(differences > 0)),
        "ties": int(np.sum(np.isclose(differences, 0.0))),
        "losses": int(np.sum(differences < 0)),
    }


def load_study(name: str, directory: Path) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    data = pd.read_csv(directory / "method_metrics.csv")
    required = {"run_id", "train_fraction", "random_seed", "method", "robust_objective"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{directory} missing columns: {sorted(missing)}")
    if data["robust_objective"].isna().any():
        raise ValueError(f"{directory} contains missing robust objective values")
    expected = {REFERENCE, *BASELINES}
    observed = set(data.method)
    missing_methods = expected - observed
    if missing_methods:
        raise ValueError(f"{directory} missing methods: {sorted(missing_methods)}")
    data["dataset"] = name
    return data, []


def paired_rows(data: pd.DataFrame) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for (dataset, fraction), group in data.groupby(["dataset", "train_fraction"], sort=True):
        reference = group[group.method == REFERENCE].set_index("run_id")["robust_objective"]
        for baseline in BASELINES:
            values = group[group.method == baseline].set_index("run_id")["robust_objective"]
            common = reference.index.intersection(values.index)
            if len(common) != 10:
                raise ValueError(f"{dataset} split {fraction}: {baseline} has {len(common)} paired runs, expected 10")
            differences = (reference.loc[common] - values.loc[common]).to_numpy(dtype=float)
            result.append({
                "dataset": dataset,
                "train_fraction": float(fraction),
                "baseline": baseline,
                "reference": REFERENCE,
                "run_ids": common.tolist(),
                "differences": differences.tolist(),
                **summarize(differences),
            })
    adjusted = holm_adjust([row["exact_sign_flip_p"] for row in result])
    for row, value in zip(result, adjusted):
        row["holm_adjusted_p"] = value
    return result


def figures(rows: list[dict[str, object]], output: Path) -> None:
    figure_dir = output / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    datasets = ["Digg 20k", "Higgs 50k"]
    fractions = sorted({row["train_fraction"] for row in rows})

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=False, constrained_layout=True)
    for axis, dataset in zip(axes, datasets):
        subset = [row for row in rows if row["dataset"] == dataset]
        y_positions = np.arange(len(fractions) * len(BASELINES))
        labels, means, errors, colors = [], [], [], []
        for fraction in fractions:
            for baseline in BASELINES:
                row = next(item for item in subset if item["train_fraction"] == fraction and item["baseline"] == baseline)
                labels.append(f"{fraction:.2f} / {DISPLAY[baseline]}")
                means.append(row["mean_difference"])
                errors.append([[row["mean_difference"] - row["ci_low"]], [row["ci_high"] - row["mean_difference"]]])
                colors.append(COLORS[baseline])
        error_array = np.asarray(errors).reshape(len(errors), 2).T
        axis.barh(y_positions, means, xerr=error_array, color=colors, alpha=0.88, capsize=3)
        axis.axvline(0, color="#333333", linewidth=0.8)
        axis.set_yticks(y_positions, labels, fontsize=8)
        axis.invert_yaxis()
        axis.set_title(dataset)
        axis.set_xlabel("Robust-objective improvement over baseline")
        axis.grid(axis="x", color="#dddddd", linewidth=0.7)
    fig.savefig(figure_dir / "figure-01-paired-objective-improvement.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "figure-01-paired-objective-improvement.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=False, constrained_layout=True)
    for axis, dataset in zip(axes, datasets):
        subset = [row for row in rows if row["dataset"] == dataset and row["baseline"] == "ris_approx"]
        for position, row in enumerate(sorted(subset, key=lambda item: item["train_fraction"])):
            values = np.asarray(row["differences"])
            jitter = np.linspace(-0.12, 0.12, len(values))
            color = "#777777" if np.allclose(values, 0) else COLORS["ris_approx"]
            axis.scatter(np.full(len(values), position) + jitter, values, color=color, s=34, alpha=0.9)
            axis.hlines(row["mean_difference"], position - 0.18, position + 0.18, color="#111111", linewidth=1.4)
        axis.axhline(0, color="#333333", linewidth=0.9, linestyle="--")
        axis.set_xticks(range(len(fractions)), [f"{value:.2f}" for value in fractions])
        axis.set(xlabel="Train fraction", ylabel="Main method minus RIS robust objective", title=dataset)
        axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    fig.savefig(figure_dir / "figure-02-ris-paired-differences.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "figure-02-ris-paired-differences.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_reports(rows: list[dict[str, object]], output: Path) -> None:
    table = []
    for row in rows:
        outcome = "tie" if row["ties"] == 10 else "main higher" if row["mean_difference"] > 0 else "main lower"
        dz = "infinite" if np.isinf(row["cohen_dz"]) else f"{row['cohen_dz']:.2f}"
        table.append(
            f"| {row['dataset']} | {row['train_fraction']:.2f} | {DISPLAY[row['baseline']]} | "
            f"{row['mean_difference']:.3f} +/- {row['sd_difference']:.3f} | "
            f"[{row['ci_low']:.3f}, {row['ci_high']:.3f}] | {row['wins']}/{row['ties']}/{row['losses']} | "
            f"{row['exact_sign_flip_p']:.6f} | {row['holm_adjusted_p']:.6f} | {dz} | {outcome} |"
        )
    report = f"""# Frozen Main-Comparison Analysis

## Question and Unit

For each dataset and temporal split, does `gnn_guided_robust_greedy` improve
the robust objective relative to Degree, GNN Top-K, Greedy MC, and RIS? The
unit is a paired run: all methods use the same split, random seed, and common
random diffusion streams. There are 10 paired runs per contrast.

## Exact Numerical Summary

Difference is `main method - baseline`; positive values favour the main method.
`W/T/L` counts main-method wins, ties, and losses across the 10 paired runs.

| Dataset | Train fraction | Baseline | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact sign-flip p | Holm p (24 tests) | Cohen dz | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table)}

## Supported Boundaries

- Digg 20k: the main method has positive paired robust-objective differences
  against all four selected baselines in all three temporal splits.
- Higgs 50k: it has positive differences against Degree, GNN Top-K, and Greedy
  MC in all splits. Against RIS it ties exactly at 0.60, then improves at 0.65
  and 0.70.
- These are optimization outcomes on two datasets. They do not validate the
  learned probabilities as stable predictors of future interactions; see the
  separate Higgs edge-prediction audit.

## Claim Candidates

- Claim:
  - Source evidence: all 24 paired contrasts and Figure 1.
  - Allowed wording: "Across the evaluated temporal splits, the method improved
    the robust objective over Degree, GNN Top-K, and Greedy MC on the frozen
    Digg and Higgs protocols."
  - Forbidden stronger wording: "It universally outperforms all baselines."
  - Uncertainty: two datasets only; Digg uses exposure proxies; paired runs are
    stochastic protocol replicates, not independent social-network samples.
  - Next check: admit a third provenance-qualified cascade dataset.
  - Decision: keep, with scope limitation.

- Claim:
  - Source evidence: Figure 2 and the Higgs RIS rows.
  - Allowed wording: "On Higgs, the method tied RIS at a 0.60 train fraction
    and improved over RIS at 0.65 and 0.70."
  - Forbidden stronger wording: "It dominates RIS at every temporal split."
  - Uncertainty: the exact 0.60 tie arises from identical seed selections.
  - Next check: investigate candidate-pool sensitivity only in a new protocol.
  - Decision: keep.
"""
    appendix = """# Statistical Appendix: Frozen Main Comparisons

## Method

- Primary metric: robust objective, higher is better.
- Pairing: same dataset, temporal split, random seed, and common-random
  diffusion streams; therefore the statistical object is the within-run
  objective difference.
- Test: exact two-sided sign-flip randomization test over all 2^10 sign
  assignments. This requires no normality assumption for the paired difference.
- Multiplicity: Holm correction across the 24 planned contrasts
  (2 datasets x 3 splits x 4 baselines).
- Effect size: paired Cohen dz, mean paired difference divided by the sample
  SD of paired differences. A value is reported as `infinite` only when every
  paired difference is the same nonzero value.

## Results

The exact numerical table in `analysis-report.md` contains every planned
contrast, including the Higgs/RIS null result at train fraction 0.60. No
contrast has been omitted for lack of significance.

## Limits

- Seed replicates quantify stochastic algorithm variation, not uncertainty over
  a population of independent datasets.
- Results are conditional on the frozen candidate pool, diffusion model,
  horizon, simulations, and baseline definitions recorded in the provenance
  manifest.
- Digg parent links are temporally valid exposure proxies, not observed
  reshares. Higgs probability predictions are seed-unstable and are not used
  as a validated causal explanation of the objective gains.
"""
    catalog = """# Figure Catalog

## Figure 1: Paired Robust-Objective Improvement

- File: `figures/figure-01-paired-objective-improvement.pdf`
- Purpose: compare the main method against each primary baseline without
  hiding temporal-split variation.
- Data source: frozen `method_metrics.csv` from both studies.
- Error bars: 95% t-CIs of the 10 paired objective differences.
- Key observation: every listed contrast favors the main method except the
  Higgs/RIS contrast at 0.60, which is exactly zero.
- Decision implication: retain a conditional comparison claim; prohibit an
  all-baseline universal-dominance claim.

## Figure 2: Main Method versus RIS

- File: `figures/figure-02-ris-paired-differences.pdf`
- Purpose: make the one material non-superiority result visible at run level.
- Data source: paired robust-objective differences from frozen runs.
- Marking: points are individual seeds; short black segments are mean
  differences; dashed line is a tie.
- Key observation: Higgs 0.60 is a complete tie, while its later splits and
  all Digg splits favour the main method.
- Decision implication: qualification is required in any discussion of RIS.
"""
    (output / "analysis-report.md").write_text(report, encoding="utf-8")
    (output / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output / "figure-catalog.md").write_text(catalog, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--digg-study", required=True)
    parser.add_argument("--higgs-study", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=False)
    digg, _ = load_study("Digg 20k", Path(args.digg_study))
    higgs, _ = load_study("Higgs 50k", Path(args.higgs_study))
    rows = paired_rows(pd.concat([digg, higgs], ignore_index=True))
    figures(rows, output)
    write_reports(rows, output)
    (output / "paired_comparisons.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
