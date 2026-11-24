# Figure Catalog

## Figure 1: Paired Robust-Objective Improvement

- File: `figures/figure-01-paired-objective-improvement.pdf`
- Purpose: compare the main method against each primary baseline without
  hiding temporal-split variation.
- Data source: frozen `method_metrics.csv` from both studies.
- Error bars: 95% t-CIs of the 10 paired objective differences.
- Key observation: every listed contrast favors the main method except the
  Higgs/RIS contrast at 0.60, which is exactly zero.
- Decision implication: retain a conditional comparison claim; prohibit an
  all-baseline universal-dominance claim.

## Figure 2: Main Method versus RIS

- File: `figures/figure-02-ris-paired-differences.pdf`
- Purpose: make the one material non-superiority result visible at run level.
- Data source: paired robust-objective differences from frozen runs.
- Marking: points are individual seeds; short black segments are mean
  differences; dashed line is a tie.
- Key observation: Higgs 0.60 is a complete tie, while its later splits and
  all Digg splits favour the main method.
- Decision implication: qualification is required in any discussion of RIS.
