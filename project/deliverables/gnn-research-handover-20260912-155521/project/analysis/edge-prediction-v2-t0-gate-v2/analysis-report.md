# v2 T0 Outer-Test Gate Report

## Question

Does temporal-supervision candidate T0 meet the preregistered predictive
validity and calibration gates on the isolated Higgs outer tests? Unit of
analysis: one deterministic training seed at a fixed outer temporal split
(`n=10` per split).

## Exact Summary

| Train fraction | AUC (mean +/- SD) | AUC 95% t-CI | Minimum AUC | Mean Brier | Mean ECE | Max inverse AUC | Gates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.60 | 0.8228 +/- 0.0275 | [0.8031, 0.8425] | 0.7614 | 0.1623 | 0.0160 | 0.2386 | pass |
| 0.65 | 0.8333 +/- 0.0320 | [0.8104, 0.8562] | 0.7639 | 0.1564 | 0.0172 | 0.2361 | pass |
| 0.70 | 0.8417 +/- 0.0325 | [0.8184, 0.8649] | 0.7680 | 0.1516 | 0.0139 | 0.2320 | pass |

## Gate Decision

All six numerical gates pass at all three outer fractions. T0 therefore
qualifies as a stable, calibrated **candidate** for a separately versioned
influence study. This is not a claim that T0 is the globally selected v2
configuration: the full preregistered candidate grid has not yet been run.

## Claim Candidates

- Claim:
  - Source evidence: 30 isolated outer-test runs and Figures 1-2.
  - Allowed wording: "The temporally supervised T0 candidate met the defined
    ranking, calibration, inversion, and seed-stability gates on Higgs."
  - Forbidden stronger wording: "T0 is the optimal architecture" or "v2
    universally solves edge prediction."
  - Uncertainty: one dataset; no completed architecture grid; balanced absent
    pair evaluation; no v2 influence-maximization rerun yet.
  - Next check: freeze the T0 manifest, then run a separately versioned
    influence study using unchanged v1 optimization/baseline controls.
  - Decision: advance conditionally.
