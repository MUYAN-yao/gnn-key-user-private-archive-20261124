# Manuscript Figure Visual QA

## Scope

Read-only visual inspection of the three PNG figures referenced by
`manuscript/draft_zh_v0_1.md`. No source figure or experiment output was
modified.

| Figure | File | Raster dimensions / DPI | Result | Publication handling |
| --- | --- | --- | --- | --- |
| Figure 1 | `analysis/frozen-main-comparison-v1/figures/figure-01-paired-objective-improvement.png` | 2445 x 1125, 220 DPI | Bar labels, error bars, panel titles, and axes are legible | The Higgs/RIS 0.60 zero bar is visually absent by definition. Retain its explicit caption statement and Appendix B row when typesetting. |
| Figure 2 | `analysis/higgs-edge-prediction-audit-v2/figures/figure-01-future-auc-by-seed.png` | 1565 x 971, 220 DPI | Seed points, legend, and random-ranking line are legible | Retain the per-seed display; do not replace it with only a mean. |
| Figure 3 | `analysis/edge-prediction-v2-t0-gate-v2/figures/figure-01-t0-outer-auc.png` | 1565 x 949, 220 DPI | Points, threshold lines, and legend are legible | Preserve the distinction between the random-ranking and CI-gate lines. |

## Constraints for Template Adaptation

- All present figure-internal labels are English. A Chinese-journal rendering
  may add Chinese captions and, if a separately versioned presentation copy is
  made, translated internal labels. It must not alter plotted values, error
  bars, colors, threshold positions, or omit the zero-difference case.
- The frozen PNGs are evidence artifacts. Any publication-layout derivative
  must be stored separately, cite its source filename, and pass a visual
  comparison against the frozen original.
- Figure 1 must always be read with its caption and Appendix B, because an
  exact zero bar cannot be seen as a positive-width rectangle.
