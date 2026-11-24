"""Render the v2-T0d exact-null grid as a compact table-style manuscript figure."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

OUT = Path(__file__).resolve().parent / "figures_v44"
INK = "#33424A"
PAPER = "#F7F5F0"
HEAD = "#B8AFC6"
CELLS = ["#E7EFEE", "#EDF0E8", "#F1ECE3"]

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                     "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 9})


def save(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    base = OUT / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    png = base.with_suffix(".png")
    fig.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")
    Image.open(png).convert("CMYK").save(base.with_suffix(".tif"), compression="tiff_lzw")
    plt.close(fig)


def main():
    rows = ["Train fraction 0.60", "Train fraction 0.65", "Train fraction 0.70"]
    cols = ["Risk penalty\nremoved", "Community reward\nremoved", "Both terms\nremoved"]
    fig, ax = plt.subplots(figsize=(6.5, 2.8))
    ax.set_xlim(0, 3); ax.set_ylim(0, 3.55); ax.axis("off")
    for j, label in enumerate(cols):
        ax.add_patch(Rectangle((j, 3), 1, .55, facecolor=HEAD, edgecolor="white", linewidth=1.2))
        ax.text(j + .5, 3.275, label, ha="center", va="center", color=INK, fontsize=8.5)
    for i, label in enumerate(rows):
        y = 2 - i
        ax.text(-.08, y + .5, label, ha="right", va="center", color=INK, fontsize=8.5)
        for j in range(3):
            ax.add_patch(Rectangle((j, y), 1, 1, facecolor=CELLS[j], edgecolor="white", linewidth=1.2))
            ax.text(j + .5, y + .58, "0.000", ha="center", va="center", color=INK, fontsize=10, fontweight="bold")
            ax.text(j + .5, y + .34, "10 ties", ha="center", va="center", color=INK, fontsize=8)
            ax.text(j + .5, y + .15, "Holm p=1.000", ha="center", va="center", color=INK, fontsize=8)
    ax.add_patch(Rectangle((0, 0), 3, 3, fill=False, edgecolor=INK, linewidth=.8))
    ax.text(1.5, -0.25, "Complete objective minus ablation objective", ha="center", color=INK, fontsize=8)
    save(fig, "fig-08-t0d-null-matrix")


if __name__ == "__main__":
    main()
