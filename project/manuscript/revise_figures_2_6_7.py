"""Layout-only manuscript derivatives; never write to audits/ or analysis/.

Contract: Fig. 2 is a version-aware mechanism schematic. Figs. 6/7 show all
30 archived AUC observations each, without new inference or exclusions.
Python/matplotlib backend; 183 mm wide; editable PDF/SVG plus 600 dpi PNG/TIFF.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript/figures_snam_r45"
SOURCES = {
    "fig-06-v1-future-auc": ROOT / "audits/higgs-edge-prediction-v1/audit_report.json",
    "fig-07-t0-outer-auc": ROOT / "audits/edge-prediction-v2-t0-outer-test-v1/report.json",
}
WIDTH = 183 / 25.4
INK = "#33424A"
COLORS = ("#467F79", "#B37970", "#778FAF")
MARKERS = ("o", "s", "^")
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 10, "axes.labelsize": 11, "xtick.labelsize": 10,
    "ytick.labelsize": 10, "legend.fontsize": 9.5,
    "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": INK,
    "xtick.color": INK, "ytick.color": INK, "savefig.facecolor": "white",
})
QA = {"backend": "Python/matplotlib", "width_mm": 183, "figures": {}}


def save(fig, name):
    # Fixed physical canvas; no tight cropping that rescales fonts in Word.
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=600)
    fig.savefig(OUT / f"{name}.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    with Image.open(OUT / f"{name}.png") as preview:
        preview.thumbnail((1200, 900), Image.Resampling.LANCZOS)
        preview.save(OUT / f"{name}-preview.png")
    plt.close(fig)


def mechanism():
    fig = plt.figure(figsize=(WIDTH, 4.15))
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, WIDTH), ylim=(0, 4.15))
    ax.set_axis_off()
    labels = []
    boxes = []

    def label(x, y, text, size=9.5, bold=False, ha="center"):
        artist = ax.text(x, y, text, ha=ha, va="center", fontsize=size,
                         fontweight="bold" if bold else "normal", linespacing=1.25)
        labels.append(artist)
        return artist

    def box(x, y, w, h, text, fill, size=9.5):
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.055",
                              facecolor=fill, edgecolor="#97A4A8", linewidth=0.85)
        ax.add_patch(patch)
        artist = label(x + w / 2, y + h / 2, text, size=size)
        boxes.append((patch, artist))

    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9,
                                    color="#6F7F83", linewidth=1.0, shrinkA=2, shrinkB=2))

    label(.16, 3.94, "a  Shared construction", 10.5, True, "left")
    xs = [.16, 1.94, 3.72, 5.50]
    top = ["Temporal\nsnapshots", "GATv2 +\nedge decoder", "Edge probabilities p\nNode prior q", "Candidate pool\nTop L = 120"]
    for i, (x, text, color) in enumerate(zip(xs, top, ["#E5EEF0", "#EEEBF2", "#E5EFEC", "#F2E7E4"])):
        box(x, 3.26, 1.53, .52, text, color)
        if i:
            arrow((xs[i - 1] + 1.53, 3.52), (x, 3.52))

    # A dedicated routing gutter connects the shared candidate pool to both protocols.
    ax.plot([6.265, 6.265, 1.855], [3.26, 3.06, 3.06], color="#6F7F83", lw=1)
    for x in (1.855, 5.395):
        arrow((x, 3.06), (x, 2.82))

    for x, title, fill in ((.16, "b  Frozen reference (v1 / v2-T0b)", "#F7F4EE"),
                            (3.70, "c  Independent evaluation (v3)", "#F0F5F5")):
        panel = FancyBboxPatch((x, .71), 3.39, 2.11,
                              boxstyle="round,pad=0.0,rounding_size=0.075",
                              facecolor=fill, edgecolor="#D5DDDF", linewidth=.8)
        ax.add_patch(panel)
        label(x + 1.695, 2.60, title, size=9.8, bold=True)
    left = ["Robust greedy + IC scoring", "Compare with direct GNN Top-K", "Return the higher-scoring seed set"]
    right = ["Robust greedy: 20 selection worlds", "Fix seed set; no Top-K fallback", "Score on 20 independent worlds"]
    for x, steps in ((.30, left), (3.84, right)):
        for i, (y, text) in enumerate(zip((2.02, 1.47, .92), steps)):
            box(x, y, 3.11, .36, text, "white", size=9.2)
            if i < 2:
                arrow((x + 1.555, y), (x + 1.555, y - .19))

    label(.16, .43, "Shared scoring:", size=9.5, bold=True, ha="left")
    label(3.86, .43, "J(S) = mean spread − λ × spread SD + η × seed-community count", size=9.2)
    label(WIDTH / 2, .16, "Learned p drives IC simulation; matched comparisons share worlds within each scoring stage.", size=8.8)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    overlaps = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if a.get_window_extent(renderer).overlaps(b.get_window_extent(renderer)):
                overlaps.append([a.get_text(), b.get_text()])
    for patch, artist in boxes:
        bounds, text_bounds = patch.get_window_extent(renderer), artist.get_window_extent(renderer)
        assert bounds.contains(text_bounds.x0, text_bounds.y0) and bounds.contains(text_bounds.x1, text_bounds.y1), artist.get_text()
    assert not overlaps, overlaps
    QA["figures"]["fig-02-method-mechanism"] = {"text_overlap_pairs": overlaps, "box_text_containment": "pass"}
    save(fig, "fig-02-method-mechanism")


def read_rows(name, seed_key, metrics_key):
    path = SOURCES[name]
    report = json.loads(path.read_text(encoding="utf-8"))
    rows = sorted([{"train_fraction": float(r["train_fraction"]), "seed": r[seed_key],
                    "auc": r[metrics_key]["auc"]} for r in report["runs"]],
                  key=lambda r: (r["train_fraction"], r["seed"]))
    assert len(rows) == 30
    assert {(r["train_fraction"], r["seed"]) for r in rows} == {(f, s) for f in (.60, .65, .70) for s in range(42, 52)}
    assert all(np.isfinite(r["auc"]) and 0 <= r["auc"] <= 1 for r in rows)
    with (OUT / f"{name}-source-data.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["train_fraction", "seed", "auc"])
        writer.writeheader()
        writer.writerows(rows)
    QA["figures"][name] = {"source": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "observations": len(rows), "excluded": 0,
        "means": {str(f): float(np.mean([r["auc"] for r in rows if r["train_fraction"] == f])) for f in (.6, .65, .7)}}
    return rows


def chart():
    fig = plt.figure(figsize=(WIDTH, 3.65))
    # Figure-level legends occupy their own band above the axes.
    ax = fig.add_axes([.115, .15, .855, .67])
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E0E5E6", linewidth=.65, zorder=0)
    ax.tick_params(length=3, width=.7)
    return fig, ax


def check_legend(fig, ax, legend, name):
    fig.canvas.draw()
    box = legend.get_window_extent(fig.canvas.get_renderer())
    assert not box.overlaps(ax.get_window_extent()), "Legend overlaps plotting area"
    assert fig.bbox.contains(box.x0, box.y0) and fig.bbox.contains(box.x1, box.y1)
    QA["figures"][name]["legend_outside_axes"] = True


def future_auc():
    name = "fig-06-v1-future-auc"
    rows = read_rows(name, "random_seed", "future_edge_prediction")
    fig, ax = chart()
    for i, f in enumerate((.6, .65, .7)):
        runs = [r for r in rows if r["train_fraction"] == f]
        # Deterministic display offset on the categorical seed axis, not data noise.
        ax.scatter([r["seed"] + (i - 1) * .22 for r in runs], [r["auc"] for r in runs],
                   s=36, color=COLORS[i], marker=MARKERS[i], edgecolor="white", linewidth=.45,
                   label=f"Train fraction {f:.2f}", zorder=3)
    ax.axhline(.5, color="#656E73", linestyle="--", lw=1, label="Random ranking (0.50)", zorder=2)
    ax.set(xlabel="Training random seed", ylabel="Future-edge ROC-AUC",
           xlim=(41.45, 51.55), ylim=(.25, .85), xticks=list(range(42, 52)), yticks=np.arange(.3, .81, .1))
    legend = fig.legend(*ax.get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.54, .995),
                        ncol=2, frameon=False, columnspacing=2.3, handletextpad=.6, labelspacing=.65)
    check_legend(fig, ax, legend, name)
    save(fig, name)


def outer_auc():
    name = "fig-07-t0-outer-auc"
    rows = read_rows(name, "seed", "metrics")
    fig, ax = chart()
    for i, f in enumerate((.6, .65, .7)):
        runs = [r for r in rows if r["train_fraction"] == f]
        ax.scatter(i + np.linspace(-.16, .16, len(runs)), [r["auc"] for r in runs],
                   color=COLORS[i], marker=MARKERS[i], s=38, edgecolor="white", linewidth=.45, zorder=3)
        ax.hlines(np.mean([r["auc"] for r in runs]), i - .22, i + .22, color=INK, linewidth=1.4, zorder=2)
    ax.axhline(.5, linestyle="--", color="#656E73", lw=1, zorder=2)
    ax.axhline(.55, linestyle=":", color="#656E73", lw=1, zorder=2)
    ax.set(xlabel="Outer train fraction", ylabel="Calibrated outer-test ROC-AUC",
           xlim=(-.5, 2.5), ylim=(.45, .9), xticks=[0, 1, 2], xticklabels=["0.60", "0.65", "0.70"],
           yticks=np.arange(.45, .901, .05))
    handles = [Line2D([], [], linestyle="none", marker="o", color="#7E9299", label="One seed (10 per split)"),
               Line2D([], [], color=INK, lw=1.4, label="Mean across seeds"),
               Line2D([], [], color="#656E73", linestyle="--", label="Random ranking (0.50)"),
               Line2D([], [], color="#656E73", linestyle=":", label="95% CI lower-bound gate (0.55)")]
    legend = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.54, .995), ncol=2,
                        frameon=False, columnspacing=2.0, handletextpad=.6, labelspacing=.65)
    check_legend(fig, ax, legend, name)
    save(fig, name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in SOURCES.items()}
    mechanism()
    future_auc()
    outer_auc()
    assert before == {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in SOURCES.items()}
    (OUT / "layout_qa.json").write_text(json.dumps(QA, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(QA, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
