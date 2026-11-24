# Figure Catalog

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
