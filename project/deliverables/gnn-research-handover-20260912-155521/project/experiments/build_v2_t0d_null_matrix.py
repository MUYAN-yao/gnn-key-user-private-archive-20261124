"""Render a labelled 3x3 matrix for the completed v2-T0d exact-null result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FRACTIONS = (0.60, 0.65, 0.70)
ARMS = ("risk_off", "community_off", "spread_only")
DISPLAY = {
    "risk_off": "Risk penalty\nremoved",
    "community_off": "Community reward\nremoved",
    "spread_only": "Both terms\nremoved",
}


def validate(path: Path) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if len(rows) != 9:
        raise ValueError("Expected the nine preregistered v2-T0d contrasts")
    by_key = {(float(row["train_fraction"]), str(row["arm"])): row for row in rows}
    expected = {(fraction, arm) for fraction in FRACTIONS for arm in ARMS}
    if set(by_key) != expected:
        raise ValueError("v2-T0d contrast grid differs from preregistration")
    for row in rows:
        if not (float(row["mean_difference"]) == 0.0 and int(row["ties"]) == 10 and float(row["holm_adjusted_p"]) == 1.0):
            raise ValueError("This renderer is reserved for the exact-null v2-T0d result")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="analysis/v2-t0d-common-world-objective-ablation-v1/paired_comparisons.json")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error("Refusing to overwrite a non-empty analysis directory")
    rows = validate(Path(args.input))
    by_key = {(float(row["train_fraction"]), str(row["arm"])): row for row in rows}
    output.mkdir(parents=True, exist_ok=False)
    figure_dir = output / "figures"
    figure_dir.mkdir()
    matrix = np.zeros((3, 3))
    fig, axis = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
    image = axis.imshow(matrix, cmap="Greys", vmin=0.0, vmax=1.0)
    axis.set_xticks(range(3), [DISPLAY[arm] for arm in ARMS])
    axis.set_yticks(range(3), [f"Train fraction {fraction:.2f}" for fraction in FRACTIONS])
    for row_index, fraction in enumerate(FRACTIONS):
        for column_index, arm in enumerate(ARMS):
            row = by_key[(fraction, arm)]
            axis.text(column_index, row_index, f"{float(row['mean_difference']):.3f}\n10 ties\nHolm p={float(row['holm_adjusted_p']):.3f}", ha="center", va="center", fontsize=10)
    axis.set_title("Completed v2-T0d common-world objective ablation: exact null grid")
    fig.colorbar(image, ax=axis, label="Full minus ablation reporting objective")
    fig.savefig(figure_dir / "figure-01-exact-null-matrix.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "figure-01-exact-null-matrix.png", dpi=240, bbox_inches="tight")
    plt.close(fig)
    table = "\n".join(
        ["| Train fraction | Arm | Full - arm | Ties | Holm p |", "| --- | --- | ---: | ---: | ---: |"]
        + [f"| {float(row['train_fraction']):.2f} | {DISPLAY[str(row['arm'])].replace(chr(10), ' ')} | {float(row['mean_difference']):.3f} | {int(row['ties'])} | {float(row['holm_adjusted_p']):.3f} |" for row in rows]
    )
    (output / "analysis-report.md").write_text(
        "# v2-T0d Exact-Null Objective Matrix\n\n"
        "This display is a numerical matrix, not evidence of an independent objective-term benefit. "
        "Every preregistered full-minus-ablation contrast is exactly zero with ten ties and Holm p = 1.000.\n\n"
        + table + "\n",
        encoding="utf-8",
    )
    (output / "stats-appendix.md").write_text(
        "# Statistical Boundary\n\nThe source bundle contains 30 hashed artifacts and nine exact two-sided sign-flip contrasts. "
        "The matrix preserves its exact-null result and does not alter the source analysis.\n",
        encoding="utf-8",
    )
    (output / "figure-catalog.md").write_text(
        "# Figure Catalog\n\n- Figure 1 is a 3x3 numerical matrix. It makes the exact zero, ten ties, and Holm p = 1.000 visible for every contrast.\n",
        encoding="utf-8",
    )
    print(f"Wrote v2-T0d exact-null matrix to {output}")


if __name__ == "__main__":
    main()
