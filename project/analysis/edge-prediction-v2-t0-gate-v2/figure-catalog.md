# Figure Catalog

## Figure 1: T0 Outer-Test AUC by Seed

- File: `figures/figure-01-t0-outer-auc.pdf`
- Purpose: verify every seed exceeds the random-ranking threshold.
- Data: calibrated outer-test AUC from the 30 T0 runs.
- Notice: all points exceed 0.5 and split-level mean bars are well above 0.55.
- Decision implication: T0 clears the ranking and seed-stability gates.

## Figure 2: T0 Calibration Metrics

- File: `figures/figure-02-t0-calibration.pdf`
- Purpose: verify probabilities are not merely well ranked but poorly scaled.
- Data: seed-level calibrated Brier score and ECE.
- Notice: all distributions lie below the dashed preregistered gate.
- Decision implication: T0 is eligible for a new, separately versioned
  influence experiment; this does not revise frozen v1 results.
