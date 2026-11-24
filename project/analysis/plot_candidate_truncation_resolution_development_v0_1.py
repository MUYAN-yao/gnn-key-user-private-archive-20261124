"""Render a clearly labelled development-only v9 diagnostic figure."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


OUT = Path(__file__).resolve().parents[1] / "figures"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.7), constrained_layout=True)
    colors = {20: "#C85A54", 80: "#287C8E"}

    axes[0].bar([0, 1], [45, 19], color=[colors[20], colors[80]], width=0.62)
    axes[0].set_xticks([0, 1], ["W=20", "W=80"])
    axes[0].set_ylim(0, 52)
    axes[0].set_ylabel("Full-greedy zero-margin rounds\n(out of 100)")
    axes[0].set_title("A. More worlds reduce, but do not remove ties", fontsize=9, loc="left", pad=8)
    for x, value in enumerate([45, 19]):
        axes[0].text(x, value + 1.5, str(value), ha="center", va="bottom", fontweight="bold")

    methods = ["Degree 2k", "Degree 4k", "Degree 8k"]
    x = list(range(3))
    width = 0.34
    axes[1].bar([value - width / 2 for value in x], [4, 7, 8], width, label="W=20", color=colors[20])
    axes[1].bar([value + width / 2 for value in x], [5, 8, 8], width, label="W=80", color=colors[80])
    axes[1].set_xticks(x, methods)
    axes[1].set_ylim(0, 8.8)
    axes[1].set_yticks(range(0, 9, 2))
    axes[1].set_ylabel("Same ordered sequence as full\n(out of 8 local blocks)")
    axes[1].set_title("B. Same-W reproduction is pool-size dependent", fontsize=9, loc="left", pad=8)
    axes[1].legend(frameon=False, ncols=2, loc="upper left")

    fig.text(0.5, -0.05, "Development-only local diagnostic: Digg pilot-5000 and Higgs pilot-1500; no population inference.", ha="center", fontsize=8, style="italic")
    for suffix in ("png", "pdf"):
        fig.savefig(OUT / f"candidate_truncation_resolution_development_v0_1.{suffix}", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
