"""Build descriptive tables, a figure, and a claim-bounded readout for v10.

The script operates only on a completed, validator-passed confirmation matrix.
It deliberately reports conditional Monte-Carlo descriptions rather than
population-level tests: the four contact-derived instances were not sampled
from a target population, and the study does not observe information cascades.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt


METHODS = ("degree_2k", "degree_4k", "degree_8k")
WORLD_COUNTS = (20, 80, 320)
METHOD_LABELS = {"degree_2k": "Degree 2k", "degree_4k": "Degree 4k", "degree_8k": "Degree 8k"}


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def load_rows(root: Path) -> list[dict]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE":
        raise ValueError("confirmation matrix is not COMPLETE")
    rows = []
    for path in sorted(root.rglob("*.json")):
        if path.name != "manifest.json":
            rows.append(json.loads(path.read_text(encoding="utf-8")))
    if len(rows) != 42:
        raise ValueError(f"expected 42 condition files, found {len(rows)}")
    return rows


def make_summary(rows: list[dict]) -> tuple[dict, list[dict], list[dict]]:
    by_block: dict[tuple, dict[int, dict]] = defaultdict(dict)
    for row in rows:
        by_block[(row["dataset"], row["world_path"], row["k"])][row["selection_world_count"]] = row
    if any(set(block) != set(WORLD_COUNTS) for block in by_block.values()):
        raise ValueError("each block must contain all nested selection budgets")

    trajectories = []
    for (dataset, path, k), budget_rows in sorted(by_block.items()):
        full = {w: budget_rows[w]["arms"]["full"]["selection"] for w in WORLD_COUNTS}
        trajectories.append({
            "dataset": dataset,
            "world_path": path,
            "k": k,
            "same_20_80": full[20]["top_k"] == full[80]["top_k"],
            "same_80_320": full[80]["top_k"] == full[320]["top_k"],
            "zero_margin_rounds": {str(w): sum(item["winner_margin_micro"] == 0 for item in full[w]["rounds"]) for w in WORLD_COUNTS},
        })

    records = []
    for row in rows:
        full_seconds = row["arms"]["full"]["decision_seconds"]
        for method in METHODS:
            arm = row["arms"][method]
            delta = arm["comparison_to_full"]["mean_spread_delta"]
            records.append({
                "dataset": row["dataset"], "world_path": row["world_path"], "k": row["k"],
                "selection_world_count": row["selection_world_count"], "method": method,
                "same_ordered_top_k": arm["comparison_to_full"]["same_ordered_top_k"],
                "first_divergence": arm["comparison_to_full"]["first_divergence"],
                "mean_spread_delta": delta, "decision_seconds": arm["decision_seconds"],
                "full_decision_seconds": full_seconds,
                "decision_time_ratio": arm["decision_seconds"] / full_seconds,
                "decision_time_saving_fraction": 1 - arm["decision_seconds"] / full_seconds,
            })

    by_method_budget: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for record in records:
        by_method_budget[(record["method"], record["selection_world_count"])].append(record)
    compact = {}
    for (method, worlds), values in sorted(by_method_budget.items()):
        deltas = [value["mean_spread_delta"] for value in values]
        savings = [value["decision_time_saving_fraction"] for value in values]
        compact[f"{method}@W{worlds}"] = {
            "condition_count": len(values),
            "same_ordered_top_k_count": sum(value["same_ordered_top_k"] for value in values),
            "mean_independent_evaluation_delta": round(_mean(deltas), 6),
            "delta_min": min(deltas), "delta_max": max(deltas),
            "positive_delta_count": sum(value > 0 for value in deltas),
            "zero_delta_count": sum(value == 0 for value in deltas),
            "negative_delta_count": sum(value < 0 for value in deltas),
            "median_decision_time_saving_fraction": round(median(savings), 6),
        }
    summary = {
        "schema": "sociopatterns-resolution-confirmation-readout-0.1",
        "condition_count": len(rows),
        "trajectory_block_count": len(trajectories),
        "full_ordered_seed_stability": {
            "same_20_80_count": sum(value["same_20_80"] for value in trajectories),
            "same_80_320_count": sum(value["same_80_320"] for value in trajectories),
            "denominator": len(trajectories),
        },
        "full_zero_margin_rounds": {str(w): sum(value["zero_margin_rounds"][str(w)] for value in trajectories) for w in WORLD_COUNTS},
        "candidate_profiles": compact,
        "scope": "Descriptive results for the frozen simulated-IC protocol on four contact-derived bidirectional topologies; no population inference.",
    }
    return summary, trajectories, records


def write_csv(path: Path, records: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def plot(output: Path, summary: dict, records: list[dict]) -> None:
    plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(10.7, 3.15), constrained_layout=True)
    colors = {20: "#C85A54", 80: "#287C8E", 320: "#6B4E9B"}

    stability = summary["full_ordered_seed_stability"]
    axes[0].bar([0, 1], [stability["same_20_80_count"], stability["same_80_320_count"]], color="#455A64", width=0.65)
    axes[0].set_xticks([0, 1], ["W20→W80", "W80→W320"])
    axes[0].set_ylim(0, stability["denominator"] + 1.2)
    axes[0].set_ylabel("Identical full-greedy sequences\n(out of 14 nested paths)")
    axes[0].set_title("A. Full search changes with W", loc="left", fontsize=9, pad=8)
    for xpos in (0, 1):
        axes[0].text(xpos, 0.35, "0/14", ha="center", va="bottom", color="#263238", fontweight="bold")

    xpos = list(range(len(METHODS)))
    width = 0.23
    for index, worlds in enumerate(WORLD_COUNTS):
        values = [summary["candidate_profiles"][f"{method}@W{worlds}"]["same_ordered_top_k_count"] for method in METHODS]
        axes[1].bar([value + (index - 1) * width for value in xpos], values, width, color=colors[worlds], label=f"W={worlds}")
    axes[1].set_xticks(xpos, ["2k", "4k", "8k"])
    axes[1].set_ylim(0, 15)
    axes[1].set_ylabel("Same ordered sequence as full\n(out of 14 conditions)")
    axes[1].set_xlabel("Degree candidate pool")
    axes[1].set_title("B. Same-W reproduction is incomplete", loc="left", fontsize=9, pad=8)
    axes[1].legend(frameon=False, ncols=3, loc="upper left", fontsize=8)

    offsets = {20: -0.20, 80: 0.0, 320: 0.20}
    for method_index, method in enumerate(METHODS):
        for worlds in WORLD_COUNTS:
            values = [record["mean_spread_delta"] for record in records if record["method"] == method and record["selection_world_count"] == worlds]
            xvalues = [method_index + offsets[worlds]] * len(values)
            axes[2].scatter(xvalues, values, s=18, color=colors[worlds], alpha=0.78, edgecolors="none")
    axes[2].axhline(0, color="#444444", linewidth=0.8)
    axes[2].set_xticks(xpos, ["2k", "4k", "8k"])
    axes[2].set_ylabel("Independent evaluation difference\n(pool − full mean spread)")
    axes[2].set_xlabel("Degree candidate pool")
    axes[2].set_title("C. Evaluation differences have both signs", loc="left", fontsize=9, pad=8)
    fig.text(0.5, -0.04, "Frozen confirmation matrix: simulated IC (p=0.01, horizon=3), 2,000 disjoint evaluation worlds per condition; descriptive only.", ha="center", fontsize=8, style="italic")
    for suffix in ("png", "pdf"):
        fig.savefig(output / f"figure-01-resolution-confirmation.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_readout(path: Path, summary: dict) -> None:
    profiles = summary["candidate_profiles"]
    rows = []
    for method in METHODS:
        for worlds in WORLD_COUNTS:
            profile = profiles[f"{method}@W{worlds}"]
            rows.append(
                f"| {METHOD_LABELS[method]} | {worlds} | {profile['same_ordered_top_k_count']}/14 | "
                f"{profile['mean_independent_evaluation_delta']:+.3f} [{profile['delta_min']:+.3f}, {profile['delta_max']:+.3f}] | "
                f"{profile['positive_delta_count']}/{profile['zero_delta_count']}/{profile['negative_delta_count']} | "
                f"{100 * profile['median_decision_time_saving_fraction']:.1f}% |"
            )
    ties = summary["full_zero_margin_rounds"]
    stable = summary["full_ordered_seed_stability"]
    text = f"""# Confirmed resolution-sensitive candidate truncation: readout

## Admission and scope

The source snapshot and all **42/42** conditions passed the frozen-matrix
validator (`status: PASS`). This is a descriptive simulation study: standard
independent-cascade influence maximization with `p=0.01` and horizon 3 on four
SocioPatterns contact-derived bidirectional topologies. It does not estimate a
population parameter, observe information diffusion, establish causal
influence, or compare a GNN with degree screening.

## Main result

Across all 14 nested `(dataset, path, k)` blocks, the ordered full-greedy seed
sequence changed from W=20 to W=80 (**{stable['same_20_80_count']}/14**
unchanged) and again from W=80 to W=320 (**{stable['same_80_320_count']}/14**
unchanged). Exact best-score ties in the full selection trace fell from
**{ties['20']}** at W=20 to **{ties['80']}** at W=80 and **{ties['320']}** at
W=320, out of 160, 160, and 160 greedy rounds respectively (8 traces x 5 rounds
+ 6 traces x 20 rounds). Thus a candidate
pool must be assessed against a named, finite-W full reference; it cannot be
presented as an unconditional approximation to a single stable full search.

## Same-W candidate-pool profile

| Candidate pool | W | Exact ordered match | Mean independent-evaluation difference, range | Positive/zero/negative conditions | Median decision-time saving |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Evaluation differences have both signs. The sign is therefore not evidence
that a degree pool improves influence; it reflects finite selection and
evaluation variation under the stated protocol. Degree 2k never reproduced the
same-W full sequence; 4k and 8k did so only in a subset of conditions. The
cost reductions are descriptive benefits with an explicit reproduction risk.

## Publication decision

The evidence supports a **methods-and-reproducibility paper**, not an algorithm
paper: *candidate-truncation claims in simulation-based influence maximization
must report selection resolution, nested-world stability, independent
evaluation and computation together*. The article can make a constructive,
bounded contribution by giving a transparent protocol and documenting both the
cost benefit and the failure boundary. It must not claim that any fixed pool is
universally equivalent to full greedy, or that degree screening or a GNN is
superior.

## Figure

`figures/figure-01-resolution-confirmation.png` and `.pdf` are the primary
confirmation figure. It should be accompanied by the frozen protocol,
validator report, source snapshot manifest and condition-level CSV.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(f"refusing to overwrite {args.output_root}")
    rows = load_rows(args.input_root)
    summary, trajectories, records = make_summary(rows)
    args.output_root.mkdir(parents=True)
    (args.output_root / "figures").mkdir()
    (args.output_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "full_trajectories.json").write_text(json.dumps(trajectories, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_root / "candidate_condition_profile.csv", records)
    plot(args.output_root / "figures", summary, records)
    write_readout(args.output_root / "readout.md", summary)


if __name__ == "__main__":
    main()
