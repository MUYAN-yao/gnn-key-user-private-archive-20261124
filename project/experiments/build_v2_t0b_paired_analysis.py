"""Build a strict paired-statistics bundle for a completed Higgs v2-T0b study.

The script deliberately refuses partial studies. It writes only to a separate
analysis directory and never alters the frozen study artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


REFERENCE = "gnn_guided_robust_greedy_v2_t0b"
FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(42, 52))
BASELINES = ("degree", "pagerank", "k_shell", "gnn_top_k", "greedy_mc", "ris_approx")
EXPECTED_CONFIG = {
    "seed_count": 2,
    "horizon": 4,
    "risk_lambda": 0.35,
    "community_weight": 0.25,
    "diffusion_model": "ic",
    "epochs": 10,
    "ants": 3,
    "iterations": 2,
    "simulations": 20,
    "optimizer": "robust_greedy",
    "candidate_pool_size": 120,
}
PROBABILITY_PROTOCOL = "v2_t0b_timestamp_grouped_isotonic"
DISPLAY = {
    "degree": "Degree",
    "pagerank": "PageRank",
    "k_shell": "k-shell",
    "gnn_top_k": "GNN Top-K",
    "greedy_mc": "Greedy MC",
    "ris_approx": "RIS",
}
COLORS = {
    "degree": "#4C78A8",
    "pagerank": "#F58518",
    "k_shell": "#54A24B",
    "gnn_top_k": "#B279A2",
    "greedy_mc": "#E45756",
    "ris_approx": "#72B7B2",
}


def expected_run_ids() -> set[str]:
    return {f"split-{fraction:.2f}-seed-{seed}" for fraction in FRACTIONS for seed in SEEDS}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_rows(run_id: str, artifact: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    result = artifact.get("result")
    baselines = artifact.get("baselines")
    if not isinstance(result, dict) or not isinstance(baselines, dict):
        raise ValueError(f"{run_id} has an incomplete method-result payload")
    methods = {REFERENCE: result, **baselines}
    if set(methods) != {REFERENCE, *BASELINES}:
        raise ValueError(f"{run_id} has an unexpected method set")
    return {(run_id, method): values for method, values in methods.items()}


def matches(value: object, expected: object) -> bool:
    if isinstance(expected, float):
        try:
            return bool(np.isclose(float(value), expected, rtol=0.0, atol=1e-12))
        except (TypeError, ValueError):
            return False
    return value == expected


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
        raise ValueError(f"Expected {len(SEEDS)} paired differences, got {len(differences)}")
    sd = float(differences.std(ddof=1))
    half_width = float(stats.t.ppf(0.975, len(differences) - 1) * sd / np.sqrt(len(differences)))
    average = float(differences.mean())
    return {
        "mean_difference": average,
        "sd_difference": sd,
        "ci_low": average - half_width,
        "ci_high": average + half_width,
        "cohen_dz": average / sd if sd else float("inf") if average else 0.0,
        "exact_sign_flip_p": exact_sign_flip_pvalue(differences),
        "wins": int(np.sum(differences > 0)),
        "ties": int(np.sum(np.isclose(differences, 0.0))),
        "losses": int(np.sum(differences < 0)),
    }


def validate_study(study_dir: Path) -> pd.DataFrame:
    expected_ids = expected_run_ids()
    manifest_path = study_dir / "manifest.json"
    metrics_path = study_dir / "method_metrics.csv"
    if not manifest_path.is_file() or not metrics_path.is_file():
        raise ValueError("Study is incomplete: manifest.json and method_metrics.csv are both required")

    run_paths = {path.stem: path for path in study_dir.glob("split-*.json")}
    if set(run_paths) != expected_ids:
        missing = sorted(expected_ids - set(run_paths))
        unexpected = sorted(set(run_paths) - expected_ids)
        raise ValueError(f"Study run files do not match the preregistered set; missing={missing}, unexpected={unexpected}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest_names = {f"{run_id}.json" for run_id in expected_ids}
    if set((manifest.get("runs") or {})) != expected_manifest_names:
        raise ValueError("Manifest run set does not match the preregistered 30-run set")

    artifact_rows: dict[tuple[str, str], dict[str, object]] = {}
    for run_id, path in run_paths.items():
        artifact = json.loads(path.read_text(encoding="utf-8"))
        if manifest["runs"].get(path.name) != sha256(path):
            raise ValueError(f"{run_id} does not match its manifest hash")
        if artifact.get("result", {}).get("method") != REFERENCE:
            raise ValueError(f"{run_id} has an unexpected reference method")
        reproducibility = artifact.get("reproducibility", {})
        if reproducibility.get("evaluation_protocol") != "common_random_numbers":
            raise ValueError(f"{run_id} does not record common-random-number evaluation")
        if reproducibility.get("probability_protocol") != PROBABILITY_PROTOCOL:
            raise ValueError(f"{run_id} has an unexpected probability protocol")
        if reproducibility.get("calibration_cutoff") >= reproducibility.get("outer_test_start"):
            raise ValueError(f"{run_id} violates strict calibration-to-test timestamp ordering")
        _, fraction_text, _, seed_text = run_id.split("-")
        expected_config = {
            **EXPECTED_CONFIG,
            "train_fraction": float(fraction_text),
            "random_seed": int(seed_text),
        }
        config = artifact.get("config", {})
        if not isinstance(config, dict) or any(not matches(config.get(key), value) for key, value in expected_config.items()):
            raise ValueError(f"{run_id} does not match the frozen v2-T0b configuration")
        if not matches(reproducibility.get("train_fraction"), expected_config["train_fraction"]) or reproducibility.get("random_seed") != expected_config["random_seed"]:
            raise ValueError(f"{run_id} has inconsistent reproducibility identifiers")
        artifact_rows.update(expected_rows(run_id, artifact))

    data = pd.read_csv(metrics_path)
    required = {"run_id", "train_fraction", "random_seed", "method", "robust_objective", "mean_spread", "community_coverage"}
    missing_columns = required - set(data.columns)
    if missing_columns:
        raise ValueError(f"method_metrics.csv is missing columns: {sorted(missing_columns)}")
    if data["robust_objective"].isna().any():
        raise ValueError("method_metrics.csv contains missing robust-objective values")

    expected_methods = {REFERENCE, *BASELINES}
    if set(data["method"]) != expected_methods:
        raise ValueError(f"Unexpected method set: {sorted(set(data['method']))}")
    if set(data["run_id"]) != expected_ids:
        raise ValueError("Metric rows do not cover the preregistered run set")
    expected_metric_rows = len(expected_ids) * len(expected_methods)
    if len(data) != expected_metric_rows or data.duplicated(["run_id", "method"]).any():
        raise ValueError(f"Expected exactly {expected_metric_rows} unique run-method rows")
    if set(np.round(data["train_fraction"].astype(float), 2)) != set(FRACTIONS):
        raise ValueError("Metric rows have unexpected train fractions")
    if set(data["random_seed"].astype(int)) != set(SEEDS):
        raise ValueError("Metric rows have unexpected random seeds")
    for metric_row in data.to_dict(orient="records"):
        key = (str(metric_row["run_id"]), str(metric_row["method"]))
        artifact_values = artifact_rows.get(key)
        if artifact_values is None:
            raise ValueError(f"method_metrics.csv has an untraceable row: {key}")
        for metric in ("mean_spread", "robust_objective", "community_coverage"):
            if not matches(metric_row[metric], artifact_values.get(metric)):
                raise ValueError(f"method_metrics.csv does not match {key} for {metric}")
    return data


def paired_comparisons(data: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fraction in FRACTIONS:
        group = data[np.isclose(data["train_fraction"].astype(float), fraction)]
        reference = group[group["method"] == REFERENCE].set_index("run_id")["robust_objective"]
        for baseline in BASELINES:
            baseline_values = group[group["method"] == baseline].set_index("run_id")["robust_objective"]
            common = sorted(reference.index.intersection(baseline_values.index))
            if len(common) != len(SEEDS):
                raise ValueError(f"{fraction:.2f}/{baseline} has {len(common)} paired runs")
            differences = (reference.loc[common] - baseline_values.loc[common]).to_numpy(dtype=float)
            rows.append({
                "train_fraction": fraction,
                "reference": REFERENCE,
                "baseline": baseline,
                "run_ids": common,
                "differences": differences.tolist(),
                **summary(differences),
            })
    adjusted = holm_adjust([float(row["exact_sign_flip_p"]) for row in rows])
    for row, adjusted_p in zip(rows, adjusted):
        row["holm_adjusted_p"] = adjusted_p
    return rows


def make_figures(rows: list[dict[str, object]], output_dir: Path) -> None:
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 7), constrained_layout=True)
    for axis, fraction in zip(axes, FRACTIONS):
        subset = [row for row in rows if row["train_fraction"] == fraction]
        labels = [DISPLAY[row["baseline"]] for row in subset]
        means = [float(row["mean_difference"]) for row in subset]
        errors = np.asarray([
            [float(row["mean_difference"]) - float(row["ci_low"]) for row in subset],
            [float(row["ci_high"]) - float(row["mean_difference"]) for row in subset],
        ])
        axis.barh(np.arange(len(subset)), means, xerr=errors, capsize=3,
                  color=[COLORS[row["baseline"]] for row in subset], alpha=0.9)
        axis.axvline(0, color="#333333", linewidth=0.8)
        axis.set_yticks(np.arange(len(subset)), labels, fontsize=9)
        axis.invert_yaxis()
        axis.set_title(f"Train fraction {fraction:.2f}")
        axis.set_xlabel("Reference minus baseline robust objective")
        axis.grid(axis="x", color="#dddddd", linewidth=0.7)
    fig.savefig(figure_dir / "figure-01-paired-objective-improvement.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "figure-01-paired-objective-improvement.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 6), constrained_layout=True, sharey=True)
    for axis, fraction in zip(axes, FRACTIONS):
        subset = [row for row in rows if row["train_fraction"] == fraction]
        for position, row in enumerate(subset):
            values = np.asarray(row["differences"], dtype=float)
            jitter = np.linspace(-0.14, 0.14, len(values))
            axis.scatter(np.full(len(values), position) + jitter, values,
                         color=COLORS[row["baseline"]], alpha=0.85, s=30)
            axis.hlines(float(row["mean_difference"]), position - 0.18, position + 0.18,
                        color="#111111", linewidth=1.3)
        axis.axhline(0, color="#333333", linewidth=0.8, linestyle="--")
        axis.set_xticks(np.arange(len(subset)), [DISPLAY[row["baseline"]] for row in subset], rotation=40, ha="right")
        axis.set_title(f"Train fraction {fraction:.2f}")
        axis.set_ylabel("Reference minus baseline robust objective")
        axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    fig.savefig(figure_dir / "figure-02-seed-level-paired-differences.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "figure-02-seed-level-paired-differences.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def format_effect(value: float) -> str:
    return "infinite" if np.isinf(value) else f"{value:.2f}"


def write_reports(rows: list[dict[str, object]], output_dir: Path) -> None:
    table_rows = []
    for row in rows:
        outcome = "tie" if row["ties"] == len(SEEDS) else "reference higher" if float(row["mean_difference"]) > 0 else "reference lower"
        table_rows.append(
            f"| {float(row['train_fraction']):.2f} | {DISPLAY[str(row['baseline'])]} | "
            f"{float(row['mean_difference']):.3f} +/- {float(row['sd_difference']):.3f} | "
            f"[{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] | "
            f"{row['wins']}/{row['ties']}/{row['losses']} | {float(row['exact_sign_flip_p']):.6f} | "
            f"{float(row['holm_adjusted_p']):.6f} | {format_effect(float(row['cohen_dz']))} | {outcome} |"
        )
    report = f"""# Higgs v2-T0b Strict Paired Analysis

## Question and Unit

For each preregistered timestamp-grouped Higgs split, does
`{REFERENCE}` change the robust objective relative to each retained baseline?
The unit is one paired protocol run: methods share the timestamp split, random
seed, and common random diffusion streams. Each contrast contains {len(SEEDS)}
paired runs; this does not represent independent social-network samples.

## Exact Numerical Summary

Difference is `reference - baseline`; positive values favor the reference.
`W/T/L` counts run-level wins, ties, and losses. Holm correction spans all 18
preregistered method-by-fraction contrasts.

| Train fraction | Baseline | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact sign-flip p | Holm p | Cohen dz | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table_rows)}

## Claim Candidates

- Claim:
  - Source evidence: complete v2-T0b `method_metrics.csv`, the paired-comparison
    table, and Figure 1.
  - Allowed wording: fill only after reviewing every contrast and its Holm-adjusted
    result.
  - Forbidden stronger wording: universal superiority, causal diffusion claims,
    or any claim beyond the timestamp-grouped Higgs protocol.
  - Uncertainty: one dataset; ten stochastic paired protocol runs; results remain
    conditional on the preregistered candidate pool and diffusion constants.
  - Next check: update the claim ledger before revising manuscript prose.
  - Decision: pending human-readable evidence review.
"""
    appendix = f"""# Statistical Appendix: Higgs v2-T0b Paired Comparisons

## Design and Checks

- Input guard: exactly 30 preregistered JSON artifacts, a batch manifest, and a
  method-metrics table with all {len(SEEDS)} seeds and 7 methods are required.
- Pairing: the same timestamp split, random seed, and common-random diffusion
  streams define a paired run.
- Primary metric: robust objective, higher is better.
- Test: exact two-sided sign-flip randomization test over all 2^10 sign
  assignments. The p-value does not require a normality assumption for paired
  differences.
- Interval: 95% t interval of the paired mean difference, reported descriptively.
- Effect size: paired Cohen dz, mean paired difference divided by the sample SD.
- Multiplicity: Holm correction across all 18 preregistered contrasts.

## Limits

- Random seeds quantify protocol stochasticity, not a population of independent
  social networks.
- Every conclusion is limited to timestamp-grouped Higgs and the frozen T0b
  configuration, candidate pool, diffusion model, horizon, and simulation count.
- This bundle does not establish causal diffusion probabilities or cross-dataset
  generalization.
"""
    catalog = """# Figure Catalog

## Figure 1: Paired Robust-Objective Differences

- File: `figures/figure-01-paired-objective-improvement.pdf`
- Purpose: compare the reference with every retained baseline at each timestamp
  fraction while retaining uncertainty and zero-centered interpretation.
- Data source: paired robust-objective differences from the complete v2-T0b
  method-metrics table.
- Error bars: 95% t intervals across ten paired runs.
- Interpretation check: inspect all bars, intervals, run counts, and the Holm
  table before selecting any manuscript claim.

## Figure 2: Seed-Level Paired Differences

- File: `figures/figure-02-seed-level-paired-differences.pdf`
- Purpose: expose seed-level heterogeneity hidden by each mean difference.
- Data source: the ten paired differences for each baseline and split.
- Marking: colored points are runs and black segments are their mean; dashed
  horizontal lines indicate a tie.
- Interpretation check: do not convert a positive mean into a robust conclusion
  without checking dispersion, ties, exact p-values, and Holm adjustment.
"""
    (output_dir / "analysis-report.md").write_text(report, encoding="utf-8")
    (output_dir / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output_dir / "figure-catalog.md").write_text(catalog, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    study_dir = Path(args.study_dir)
    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        parser.error(f"Refusing to overwrite non-empty output directory: {output_dir}")

    data = validate_study(study_dir)
    rows = paired_comparisons(data)
    output_dir.mkdir(parents=True, exist_ok=False)
    make_figures(rows, output_dir)
    write_reports(rows, output_dir)
    (output_dir / "paired_comparisons.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote strict paired analysis bundle to {output_dir}")


if __name__ == "__main__":
    main()
