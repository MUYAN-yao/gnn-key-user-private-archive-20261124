"""Generate manuscript mechanism figures with a restrained, CMYK-safe palette.

All figures are schematic and contain no experimental values.  The source
figures are kept separate from frozen analysis outputs.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image

OUT = Path(__file__).resolve().parent / "figures_v44"

# Low-saturation palette inspired by Monet's cool water, muted lavender and ochre.
COLORS = {
    "ink": "#33424A",
    "history": "#9EB7BE",
    "future": "#C7D7D4",
    "teal": "#7FA9A2",
    "lavender": "#B8AFC6",
    "rose": "#C8A6A2",
    "ochre": "#C6B184",
    "paper": "#F7F5F0",
    "line": "#6F7F83",
}
CMYK = {"history": (0.16, 0.00, 0.03, 0.28), "future": (0.07, 0.00, 0.03, 0.16),
        "teal": (0.25, 0.00, 0.07, 0.34), "lavender": (0.07, 0.13, 0.00, 0.22),
        "rose": (0.00, 0.17, 0.17, 0.22), "ochre": (0.00, 0.11, 0.33, 0.22)}

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                     "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False})


def box(ax, xy, w, h, text, color, fontsize=9):
    patch = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                           facecolor=color, edgecolor=COLORS["ink"], linewidth=0.9)
    ax.add_patch(patch)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
            color=COLORS["ink"], fontsize=fontsize, wrap=True)


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                 linewidth=1.1, color=COLORS["line"]))


def base(name, figsize=(7.0, 3.2)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title(name, loc="left", fontsize=11, fontweight="bold", color=COLORS["ink"], pad=6)
    return fig, ax


def save(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / stem
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    png = path.with_suffix(".png")
    fig.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")
    # Explicit CMYK raster for print workflows; source palette is CMYK-safe.
    Image.open(png).convert("CMYK").save(path.with_suffix(".tif"), compression="tiff_lzw")
    plt.close(fig)


def time_boundary():
    fig, ax = base("Research protocol and temporal boundary", (7.2, 2.8))
    ax.add_patch(Rectangle((0.05, 0.30), 0.46, 0.34, color=COLORS["history"], alpha=.72, ec="none"))
    ax.add_patch(Rectangle((0.51, 0.30), 0.18, 0.34, color=COLORS["lavender"], alpha=.72, ec="none"))
    ax.add_patch(Rectangle((0.69, 0.30), 0.26, 0.34, color=COLORS["future"], alpha=.9, ec="none"))
    ax.axvline(0.51, color=COLORS["ink"], ls="--", lw=1)
    ax.axvline(0.69, color=COLORS["ink"], ls="--", lw=1)
    ax.text(.28, .48, "History window\nfeature construction", ha="center", va="center", color=COLORS["ink"])
    ax.text(.60, .48, "Supervised +\ncalibration", ha="center", va="center", color=COLORS["ink"])
    ax.text(.82, .48, "Outer test\nfuture unseen", ha="center", va="center", color=COLORS["ink"])
    ax.text(.51, .22, "selection world", ha="center", color=COLORS["ink"], fontsize=8)
    ax.text(.82, .22, "evaluation world", ha="center", color=COLORS["ink"], fontsize=8)
    ax.text(.51, .72, "strict timestamp boundary", ha="center", color=COLORS["ink"], fontsize=8)
    save(fig, "fig-07-time-boundary")


def method_flow():
    fig, ax = base("Method mechanism: from temporal graph to seed set", (7.2, 3.0))
    xs = [0.04, 0.22, 0.40, 0.58, 0.76]
    labels = ["Temporal\nsnapshots", "GATv2\nrepresentation", "Edge\nprobability prior", "Candidate pool\n(top 120)", "Robust greedy + IC\nevaluation -> Top-K"]
    cols = [COLORS["history"], COLORS["lavender"], COLORS["teal"], COLORS["rose"], COLORS["ochre"]]
    for x, label, col in zip(xs, labels, cols): box(ax, (x, .42), .14, .22, label, col)
    for x in xs[:-1]: arrow(ax, (x + .145, .53), (x + .175, .53))
    ax.text(.50, .18, "same random streams for candidate scoring and evaluation-world comparison",
            ha="center", color=COLORS["ink"], fontsize=8)
    save(fig, "fig-08-method-mechanism")


def objective_structure():
    fig, ax = base("Joint objective and interpretation boundary", (7.2, 3.0))
    box(ax, (.07, .48), .22, .22, "Expected\nspread", COLORS["teal"])
    box(ax, (.39, .48), .22, .22, "Risk penalty\nλ × SD", COLORS["rose"])
    box(ax, (.71, .48), .22, .22, "Community\ncoverage η × C", COLORS["lavender"])
    ax.text(.50, .30, "J(S) = mean spread − λ·SD + η·coverage", ha="center", color=COLORS["ink"], fontsize=10)
    ax.text(.50, .13, "v2-T0d and v3: zero-difference results bound interpretation to the tested protocol",
            ha="center", color=COLORS["ink"], fontsize=8)
    save(fig, "fig-09-objective-structure")


def fairness_paths():
    fig, ax = base("Fairness comparison: candidate screening versus full-candidate search", (7.2, 3.1))
    box(ax, (.06, .62), .24, .18, "GNN-screened\nrobust greedy", COLORS["teal"])
    box(ax, (.06, .20), .24, .18, "Full-candidate\nrobust greedy", COLORS["lavender"])
    box(ax, (.43, .41), .22, .20, "Shared robust\nobjective J(S)", COLORS["ochre"])
    box(ax, (.76, .41), .18, .20, "Independent\nevaluation world", COLORS["rose"])
    arrow(ax, (.31, .71), (.42, .54)); arrow(ax, (.31, .29), (.42, .47)); arrow(ax, (.66, .51), (.75, .51))
    ax.text(.50, .13, "v3 reports paired selection, overlap, runtime and Holm-adjusted differences",
            ha="center", color=COLORS["ink"], fontsize=8)
    save(fig, "fig-10-fairness-paths")


if __name__ == "__main__":
    time_boundary(); method_flow(); objective_structure(); fairness_paths()
