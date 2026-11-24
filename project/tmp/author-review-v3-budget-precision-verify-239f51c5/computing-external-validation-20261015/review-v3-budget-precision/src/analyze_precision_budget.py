"""Recompute the post-hoc budget-by-PageRank-precision analysis from NPZ files."""
from pathlib import Path
import hashlib
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1]
B = R.parent
D = R / "supplement-pr-budget-precision"
OUT = R / "analysis/precision_budget"
OUT.mkdir(parents=True, exist_ok=True)
METHODS = ("pagerank_4k", "pagerank_5pct")
BUDGETS = (80, 320, 1280)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired(values: np.ndarray) -> dict:
    values = values.astype(float)
    se = values.std(ddof=1) / np.sqrt(len(values))
    return {"mean": float(values.mean()), "mc_se": float(se), "mc_lo": float(values.mean() - 1.96 * se), "mc_hi": float(values.mean() + 1.96 * se)}


def stored_strict(dataset: str, path_id: int, worlds: int) -> tuple[Path, Path, str]:
    if worlds == 1280:
        root = B / "review-v2/supplement-pr-precision/conditions"
        label = "prior-posthoc-strict-w1280"
    else:
        root = D / "conditions"
        label = "new-posthoc-strict-w80-w320"
    stem = f"{dataset}__p{path_id}__w{worlds}"
    return root / f"{stem}.json", root / f"{stem}.npz", label


def selected_and_pool(record: dict, method: str) -> tuple[list, list]:
    arm = record["arms"][method]
    return arm["selected"], arm["candidate_ids"]


def write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(OUT / name, index=False)


def plot(summary: pd.DataFrame) -> None:
    labels = {"ca_grqc": "ca-GrQc", "college_msg": "CollegeMsg", "wiki_vote": "wiki-Vote"}
    method_labels = {"pagerank_4k": "PageRank 4k", "pagerank_5pct": "PageRank 5%"}
    colors = {"default": "#c65f20", "strict": "#176b87"}
    styles = {"default": "o--", "strict": "s-"}
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.5), sharex=True)
    chart = []
    for row, method in enumerate(METHODS):
        for col, dataset in enumerate(("ca_grqc", "college_msg", "wiki_vote")):
            axis = axes[row, col]
            part = summary[(summary.dataset == dataset) & (summary.method == method)]
            for solver in ("default", "strict"):
                values = part[part.solver == solver].sort_values("W")
                axis.errorbar(values.W, values.loss_percent_mean, yerr=values.loss_percent_path_sd, fmt=styles[solver], color=colors[solver], capsize=2.5, linewidth=1.2, markersize=4, label=solver.title())
                chart.extend(values.assign(panel=f"{method_labels[method]} | {labels[dataset]}").to_dict("records"))
            axis.axhline(0, color="#555555", linewidth=.7)
            axis.set_xscale("symlog", linthresh=80, base=2)
            axis.set_xticks(list(BUDGETS), [str(x) for x in BUDGETS])
            axis.grid(axis="y", color="#dddddd", linewidth=.55)
            if row == 0:
                axis.set_title(labels[dataset], fontsize=9)
            if col == 0:
                axis.set_ylabel(f"{method_labels[method]}\nIncremental loss (%)", fontsize=8)
            if row == 1:
                axis.set_xlabel("Selection worlds W", fontsize=8)
            axis.tick_params(labelsize=7)
    axes[0, 0].legend(loc="best", frameon=False, fontsize=7)
    fig.text(.5, .005, "Post-hoc comparison; bars show standard deviation across five paired computational paths. Negative loss favors the restricted set.", ha="center", fontsize=7)
    fig.tight_layout(rect=(0, .05, 1, 1))
    figs = OUT / "figures"
    figs.mkdir(exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"precision_budget_loss.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    write_csv(pd.DataFrame(chart), "precision_budget_loss_figure_source.csv")


def main() -> None:
    run = json.loads((D / "run_status.json").read_text(encoding="utf-8"))
    if run.get("status") != "complete" or run.get("conditions") != 30 or run.get("arms") != 60:
        raise RuntimeError("new strict-budget matrix is incomplete")
    if json.loads((B / "review-v2/supplement-pr-precision/run_status.json").read_text())["status"] != "complete":
        raise RuntimeError("prior strict W1280 matrix is incomplete")
    manifest_hash = sha(D / "source_manifest.json")
    rows, arrays = [], {}
    config = json.loads((B / "config.json").read_text())
    for dataset in config["datasets"]:
        for path_id in config["resolution"]["paths"]:
            for worlds in BUDGETS:
                frozen_json = B / "results/main/conditions" / f"resolution__{dataset}__p{path_id}__w{worlds}__step.json"
                frozen = json.loads(frozen_json.read_text(encoding="utf-8"))
                with np.load(frozen_json.with_suffix(".npz")) as default_arrays:
                    full_values = default_arrays["full_evaluation"].copy()
                    for method in METHODS:
                        default_values = default_arrays[method + "_evaluation"].copy()
                        default_selected, default_pool = selected_and_pool(frozen, method)
                        difference = default_values - full_values
                        metric = paired(difference)
                        key = (dataset, path_id, worlds, method, "default")
                        arrays[key] = {"evaluation": default_values, "full": full_values, "selected": default_selected, "pool": default_pool}
                        rows.append({"dataset": dataset, "path": path_id, "W": worlds, "method": method, "solver": "default", "source": "frozen-main", "candidate_count": len(default_pool), "candidate_coverage": len(default_pool) / frozen["graph"]["n"], "total_spread": float(default_values.mean()), "incremental_spread": float(default_values.mean() - 5), "full_incremental_spread": float(full_values.mean() - 5), "delta_vs_full": metric["mean"], "mc_se_vs_full": metric["mc_se"], "mc_lo_vs_full": metric["mc_lo"], "mc_hi_vs_full": metric["mc_hi"], "loss_percent": float(-100 * metric["mean"] / (full_values.mean() - 5)), "selected": ";".join(default_selected), "candidate_ids": ";".join(default_pool), "same_order_as_full": default_selected == frozen["arms"]["full"]["selected"], "same_set_as_full": set(default_selected) == set(frozen["arms"]["full"]["selected"]), "input_json_sha256": sha(frozen_json)})
                strict_json, strict_npz, source = stored_strict(dataset, path_id, worlds)
                strict = json.loads(strict_json.read_text(encoding="utf-8"))
                if strict["frozen_reference_json_sha256"] != sha(frozen_json):
                    raise RuntimeError(f"strict/full reference mismatch: {strict_json}")
                with np.load(strict_npz) as strict_arrays:
                    for method in METHODS:
                        strict_values = strict_arrays[method + "_evaluation"].copy()
                        strict_selected, strict_pool = selected_and_pool(strict, method)
                        difference = strict_values - arrays[(dataset, path_id, worlds, method, "default")]["full"]
                        metric = paired(difference)
                        key = (dataset, path_id, worlds, method, "strict")
                        arrays[key] = {"evaluation": strict_values, "full": full_values, "selected": strict_selected, "pool": strict_pool}
                        rows.append({"dataset": dataset, "path": path_id, "W": worlds, "method": method, "solver": "strict", "source": source, "candidate_count": len(strict_pool), "candidate_coverage": len(strict_pool) / frozen["graph"]["n"], "total_spread": float(strict_values.mean()), "incremental_spread": float(strict_values.mean() - 5), "full_incremental_spread": float(full_values.mean() - 5), "delta_vs_full": metric["mean"], "mc_se_vs_full": metric["mc_se"], "mc_lo_vs_full": metric["mc_lo"], "mc_hi_vs_full": metric["mc_hi"], "loss_percent": float(-100 * metric["mean"] / (full_values.mean() - 5)), "selected": ";".join(strict_selected), "candidate_ids": ";".join(strict_pool), "same_order_as_full": strict_selected == frozen["arms"]["full"]["selected"], "same_set_as_full": set(strict_selected) == set(frozen["arms"]["full"]["selected"]), "input_json_sha256": sha(strict_json)})
    path_metrics = pd.DataFrame(rows)
    write_csv(path_metrics, "path_metrics.csv")
    summary = path_metrics.groupby(["dataset", "W", "method", "solver"], as_index=False).agg(paths=("path", "size"), delta_nodes_mean=("delta_vs_full", "mean"), delta_nodes_path_sd=("delta_vs_full", "std"), loss_percent_mean=("loss_percent", "mean"), loss_percent_path_sd=("loss_percent", "std"), same_order_full_count=("same_order_as_full", "sum"), same_set_full_count=("same_set_as_full", "sum"), candidate_count=("candidate_count", "first"), candidate_coverage=("candidate_coverage", "first"))
    write_csv(summary, "summary_by_budget_precision.csv")

    tolerance_rows = []
    for dataset, path_id, worlds, method in path_metrics[["dataset", "path", "W", "method"]].drop_duplicates().itertuples(index=False, name=None):
        default = arrays[(dataset, path_id, worlds, method, "default")]
        strict = arrays[(dataset, path_id, worlds, method, "strict")]
        value = strict["evaluation"] - default["evaluation"]
        metric = paired(value)
        pool_overlap = len(set(default["pool"]) & set(strict["pool"]))
        tolerance_rows.append({"dataset": dataset, "path": path_id, "W": worlds, "method": method, "delta_strict_minus_default": metric["mean"], "mc_se": metric["mc_se"], "mc_lo": metric["mc_lo"], "mc_hi": metric["mc_hi"], "same_order": strict["selected"] == default["selected"], "same_set": set(strict["selected"]) == set(default["selected"]), "pool_overlap": pool_overlap, "pool_jaccard": pool_overlap / len(set(default["pool"]) | set(strict["pool"]))})
    tolerance = pd.DataFrame(tolerance_rows)
    write_csv(tolerance, "tolerance_effects_by_path.csv")
    tolerance_summary = tolerance.groupby(["dataset", "W", "method"], as_index=False).agg(paths=("path", "size"), strict_minus_default_mean=("delta_strict_minus_default", "mean"), strict_minus_default_path_sd=("delta_strict_minus_default", "std"), same_order_count=("same_order", "sum"), same_set_count=("same_set", "sum"), pool_jaccard=("pool_jaccard", "first"))
    write_csv(tolerance_summary, "tolerance_effects_summary.csv")

    transition_rows, interaction_rows = [], []
    for dataset in config["datasets"]:
        for path_id in config["resolution"]["paths"]:
            for method in METHODS:
                for low, high in zip(BUDGETS[:-1], BUDGETS[1:]):
                    solver_effect = {}
                    for solver in ("default", "strict"):
                        low_record = arrays[(dataset, path_id, low, method, solver)]
                        high_record = arrays[(dataset, path_id, high, method, solver)]
                        low_delta = low_record["evaluation"] - low_record["full"]
                        high_delta = high_record["evaluation"] - high_record["full"]
                        change = high_delta - low_delta
                        metric = paired(change)
                        solver_effect[solver] = change
                        transition_rows.append({"dataset": dataset, "path": path_id, "method": method, "solver": solver, "low_W": low, "high_W": high, "changed_order": low_record["selected"] != high_record["selected"], "changed_set": set(low_record["selected"]) != set(high_record["selected"]), "delta_change": metric["mean"], "mc_se": metric["mc_se"], "mc_lo": metric["mc_lo"], "mc_hi": metric["mc_hi"]})
                    interaction = solver_effect["strict"] - solver_effect["default"]
                    metric = paired(interaction)
                    interaction_rows.append({"dataset": dataset, "path": path_id, "method": method, "low_W": low, "high_W": high, "strict_minus_default_budget_effect": metric["mean"], "mc_se": metric["mc_se"], "mc_lo": metric["mc_lo"], "mc_hi": metric["mc_hi"]})
    transitions = pd.DataFrame(transition_rows)
    write_csv(transitions, "budget_transitions_by_path.csv")
    transition_summary = transitions.groupby(["dataset", "method", "solver", "low_W", "high_W"], as_index=False).agg(paths=("path", "size"), changed_order_count=("changed_order", "sum"), changed_set_count=("changed_set", "sum"), delta_change_mean=("delta_change", "mean"), delta_change_path_sd=("delta_change", "std"), mc_interval_excludes_zero_count=("mc_lo", lambda x: int(np.sum((x > 0) | (transitions.loc[x.index, "mc_hi"] < 0)))))
    write_csv(transition_summary, "budget_transitions_summary.csv")
    interaction = pd.DataFrame(interaction_rows)
    write_csv(interaction, "budget_tolerance_interaction_by_path.csv")
    interaction_summary = interaction.groupby(["dataset", "method", "low_W", "high_W"], as_index=False).agg(paths=("path", "size"), interaction_mean=("strict_minus_default_budget_effect", "mean"), interaction_path_sd=("strict_minus_default_budget_effect", "std"))
    write_csv(interaction_summary, "budget_tolerance_interaction_summary.csv")

    pool = pd.read_csv(D / "pool_diagnostics.csv")
    for col in ("strict_added_ids", "strict_removed_ids", "strict_candidate_ids", "default_candidate_ids"):
        if col in pool:
            pool[col] = pool[col].map(str)
    write_csv(pool, "candidate_pool_precision_diagnostics.csv")
    plot(summary)

    report = ["# Strict-PageRank budget sensitivity analysis", "", "This report is regenerated from the frozen default matrix, the previously frozen strict W=1280 control and the separately frozen strict W=80/W=320 matrix. The added control reuses original paths and is post-hoc; it adds no independent networks or selection paths.", "", "## Main readout", ""]
    for dataset in config["datasets"]:
        for method in METHODS:
            part = summary[(summary.dataset == dataset) & (summary.method == method)].sort_values(["solver", "W"])
            compact = "; ".join(f"{solver} W={int(w)}: {loss:.3f}%" for solver, w, loss in part[["solver", "W", "loss_percent_mean"]].itertuples(index=False, name=None))
            report.append(f"- {dataset}, {method}: mean incremental losses {compact}.")
    report.extend(["", "## Required interpretation limits", "", "- Default and strict PageRank are separate named implementations. Strict ranking is stable at tolerance 1e-14 for every pool, but a strict/default difference can arise through candidate-pool truncation and downstream greedy choice.", "- Conditional Monte Carlo intervals quantify simulation noise for the fixed seeds/worlds. Path variation quantifies variation across five paired computational paths; neither is a population confidence interval across social networks.", "- The analysis does not add a p-value family or reclassify post-hoc outcomes as confirmatory. Full eligibility, propagation, graph and evaluation families remain frozen.", "", "See `path_metrics.csv`, `tolerance_effects_by_path.csv`, `budget_transitions_by_path.csv`, `budget_tolerance_interaction_by_path.csv`, and the figure source CSV for all values."])
    (OUT / "analysis-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    provenance = {"status": "PASS", "script_sha256": sha(Path(__file__)), "posthoc_manifest_sha256": manifest_hash, "new_conditions": 30, "new_arms": 60, "inputs": {"main_result_directory": str(B / "results/main/conditions"), "prior_strict_w1280": str(B / "review-v2/supplement-pr-precision/conditions"), "new_strict_w80_w320": str(D / "conditions")}}
    (OUT / "analysis_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
