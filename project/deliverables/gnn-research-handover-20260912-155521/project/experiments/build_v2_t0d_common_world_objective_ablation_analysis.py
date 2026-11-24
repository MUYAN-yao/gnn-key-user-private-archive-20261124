"""Strict paired analysis for a completed v2-T0d common-world ablation."""
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
from run_v2_t0d_common_world_objective_ablation import ARMS, FRACTIONS, FULL, SEEDS, run_id, sha256


def exact_sign_flip_pvalue(differences: np.ndarray) -> float:
    observed = abs(float(differences.mean()))
    values = np.fromiter(
        (abs(float(np.dot(signs, differences) / len(differences))) for signs in product((-1, 1), repeat=len(differences))),
        dtype=float,
    )
    return float(np.mean(values >= observed - 1e-12))


def holm_adjust(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(pvalues) - rank) * pvalues[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def summarize(differences: np.ndarray) -> dict[str, float | int]:
    mean, sd = float(differences.mean()), float(differences.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(differences) - 1) * sd / np.sqrt(len(differences)))
    return {
        "mean_difference": mean, "sd_difference": sd, "ci_low": mean - half, "ci_high": mean + half,
        "cohen_dz": mean / sd if sd else float("inf") if mean else 0.0,
        "exact_sign_flip_p": exact_sign_flip_pvalue(differences),
        "wins": int(np.sum(differences > 0)), "ties": int(np.sum(np.isclose(differences, 0.0))),
        "losses": int(np.sum(differences < 0)),
    }


def validate(study_dir: Path) -> pd.DataFrame:
    manifest_path, metrics_path = study_dir / "manifest.json", study_dir / "method_metrics.csv"
    if not manifest_path.is_file() or not metrics_path.is_file():
        raise ValueError("A complete v2-T0d manifest and metrics table are required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_ids = {run_id(fraction, seed) for fraction in FRACTIONS for seed in SEEDS}
    paths = {path.stem: path for path in study_dir.glob("split-*.json")}
    if set(paths) != expected_ids or set((manifest.get("runs") or {}).keys()) != {path.name for path in paths.values()}:
        raise ValueError("The v2-T0d run set is incomplete or differs from preregistration")
    records: list[dict] = []
    for identifier, path in paths.items():
        if manifest["runs"].get(path.name) != sha256(path):
            raise ValueError(f"Artifact hash mismatch: {path.name}")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        _, fraction_text, _, seed_text = identifier.split("-")
        fraction, seed = float(fraction_text), int(seed_text)
        expected_config = {
            "seed_count": 2, "horizon": 4, "risk_lambda": 0.35, "community_weight": 0.25,
            "diffusion_model": "ic", "random_seed": seed, "epochs": 10, "ants": 3,
            "iterations": 2, "simulations": 20, "train_fraction": fraction,
            "optimizer": "robust_greedy", "candidate_pool_size": 120,
        }
        if artifact.get("config") != expected_config or artifact.get("reporting_objective") != FULL:
            raise ValueError(f"Configuration or reporting objective mismatch: {identifier}")
        repro = artifact.get("reproducibility", {})
        if repro.get("evaluation_protocol") != "v2_t0d_deterministic_edge_time_common_worlds":
            raise ValueError(f"Common-world evaluation protocol mismatch: {identifier}")
        if repro.get("calibration_cutoff") >= repro.get("outer_test_start"):
            raise ValueError(f"Strict timestamp ordering violation: {identifier}")
        arms = artifact.get("arms", {})
        if set(arms) != set(ARMS):
            raise ValueError(f"Ablation-arm set mismatch: {identifier}")
        for arm, payload in arms.items():
            values = payload.get("full_objective_evaluation", {})
            expected_fields = {"top_k", "mean_spread", "spread_std", "robust_objective", "community_coverage"}
            if set(values) != expected_fields or values.get("top_k") != payload.get("selection_objective", {}).get("top_k"):
                raise ValueError(f"Arm payload mismatch: {identifier}/{arm}")
            records.append({
                "run_id": identifier, "train_fraction": fraction, "random_seed": seed, "arm": arm,
                "robust_objective": values["robust_objective"], "mean_spread": values["mean_spread"],
                "spread_std": values["spread_std"], "community_coverage": values["community_coverage"],
            })
    data = pd.DataFrame(records)
    metrics = pd.read_csv(metrics_path)
    required = {"run_id", "train_fraction", "random_seed", "arm", "method", "mean_spread", "spread_std", "robust_objective", "community_coverage", "runtime_seconds"}
    if set(metrics.columns) != required or len(metrics) != len(records) or metrics.duplicated(["run_id", "arm"]).any():
        raise ValueError("method_metrics.csv does not have the preregistered v2-T0d schema")
    joined = data.merge(metrics[["run_id", "arm", "robust_objective"]], on=["run_id", "arm"], how="left", validate="one_to_one", suffixes=("", "_csv"))
    if joined["robust_objective_csv"].isna().any() or not np.allclose(joined.robust_objective, joined.robust_objective_csv, rtol=0.0, atol=1e-12):
        raise ValueError("method_metrics.csv does not match run-level full-objective scores")
    return data


def paired_rows(data: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for fraction in FRACTIONS:
        subset = data[np.isclose(data.train_fraction, fraction)]
        full = subset[subset.arm == "full"].set_index("run_id")["robust_objective"]
        for arm in ("risk_off", "community_off", "spread_only"):
            other = subset[subset.arm == arm].set_index("run_id")["robust_objective"]
            ids = [run_id(fraction, seed) for seed in SEEDS]
            if set(full.index) != set(ids) or set(other.index) != set(ids):
                raise ValueError(f"Incomplete paired data for {fraction:.2f}/{arm}")
            diff = (full.loc[ids] - other.loc[ids]).to_numpy(float)
            rows.append({"train_fraction": fraction, "arm": arm, "run_ids": ids, "differences": diff.tolist(), **summarize(diff)})
    for row, adjusted in zip(rows, holm_adjust([float(row["exact_sign_flip_p"]) for row in rows])):
        row["holm_adjusted_p"] = adjusted
    return rows


def write_outputs(rows: list[dict], output_dir: Path) -> None:
    names = {"risk_off": "Risk penalty removed", "community_off": "Community reward removed", "spread_only": "Both terms removed"}
    colors = {"risk_off": "#4C78A8", "community_off": "#F58518", "spread_only": "#54A24B"}
    figure_dir = output_dir / "figures"; figure_dir.mkdir(parents=True)
    figure, axes = plt.subplots(1, 3, figsize=(14, 5.4), constrained_layout=True)
    for axis, fraction in zip(axes, FRACTIONS):
        subset = [row for row in rows if row["train_fraction"] == fraction]
        means = [float(row["mean_difference"]) for row in subset]
        errors = np.asarray([[float(row["mean_difference"]) - float(row["ci_low"]) for row in subset], [float(row["ci_high"]) - float(row["mean_difference"]) for row in subset]])
        axis.barh(np.arange(3), means, xerr=errors, capsize=3, color=[colors[row["arm"]] for row in subset])
        axis.axvline(0, color="#222222", linewidth=0.8); axis.invert_yaxis()
        axis.set_yticks(np.arange(3), [names[row["arm"]] for row in subset]); axis.set_title(f"Train fraction {fraction:.2f}")
        axis.set_xlabel("Full minus ablation full objective"); axis.grid(axis="x", color="#dddddd", linewidth=0.7)
    figure.savefig(figure_dir / "figure-01-common-world-objective-ablation.pdf", bbox_inches="tight")
    figure.savefig(figure_dir / "figure-01-common-world-objective-ablation.png", dpi=240, bbox_inches="tight")
    plt.close(figure)
    table = []
    for row in rows:
        dz = "infinite" if np.isinf(float(row["cohen_dz"])) else f"{float(row['cohen_dz']):.2f}"
        table.append(f"| {float(row['train_fraction']):.2f} | {names[row['arm']]} | {float(row['mean_difference']):.3f} +/- {float(row['sd_difference']):.3f} | [{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] | {row['wins']}/{row['ties']}/{row['losses']} | {float(row['exact_sign_flip_p']):.6f} | {float(row['holm_adjusted_p']):.6f} | {dz} |")
    report = f"""# Higgs v2-T0d Common-World Objective-Ablation Analysis

## Question and Unit

Within each strict timestamp-grouped Higgs fraction, how does removing one or
both objective terms change seed selection when all four arms share one trained
probability map and deterministic edge-time diffusion worlds? The unit is one
fraction-seed run. The primary score is the same full objective for all arms.

## Exact Numerical Summary

Difference is `full - ablation`; positive favors the complete objective. Holm
correction covers all 9 preregistered contrasts.

| Train fraction | Ablation | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact p | Holm p | Cohen dz |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table)}

## Claim Boundary

Only Holm-supported contrasts may be described as evidence that a term changes
the selected-set score, and only for this separately versioned Higgs protocol.
The analysis does not establish universal term importance, causal diffusion,
cross-dataset generalization, or interchangeability with v2-T0b.
"""
    appendix = """# Statistical Appendix: v2-T0d Common-World Objective Ablation

- Validates 30 hashed artifacts, 120 metrics rows, strict timestamp ordering,
  fixed model/decision configuration, and the shared deterministic edge-time
  common-world evaluator.
- Tests the 9 preregistered full-minus-ablation contrasts with exact two-sided
  sign-flip randomization tests over all 2^10 assignments and Holm correction.
- 95% t intervals and paired Cohen dz are descriptive; seeds represent
  stochastic protocol runs, not independent networks.
"""
    catalog = """# Figure Catalog

## Figure 1: Common-World Objective Ablation

- File: `figures/figure-01-common-world-objective-ablation.pdf`
- Purpose: compare every objective-removal arm with the full objective under a
  fixed probability map and fixed edge-time diffusion worlds per paired run.
- Error bars: 95% t intervals across ten paired runs.
- Interpretation: use the exact and Holm-adjusted table before making any
  objective-term claim.
"""
    (output_dir / "analysis-report.md").write_text(report, encoding="utf-8")
    (output_dir / "stats-appendix.md").write_text(appendix, encoding="utf-8")
    (output_dir / "figure-catalog.md").write_text(catalog, encoding="utf-8")
    (output_dir / "paired_comparisons.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True); parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(); output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error("Refusing to overwrite a non-empty analysis directory")
    data = validate(Path(args.study_dir)); rows = paired_rows(data)
    output.mkdir(parents=True, exist_ok=False); write_outputs(rows, output)
    print(f"Wrote strict v2-T0d common-world ablation analysis to {output}")


if __name__ == "__main__":
    main()
