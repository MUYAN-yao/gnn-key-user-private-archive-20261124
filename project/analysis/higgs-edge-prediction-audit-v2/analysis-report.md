# Higgs Edge-Prediction Audit Analysis

## Question

Does the frozen 50k-node Higgs protocol produce temporally valid and stable
GNN edge probabilities? The unit of analysis is one stochastic model-training
run at a fixed temporal split (10 pre-registered seeds per split). These are
replicates of training randomness on the same dataset, not independent
datasets; inferential tests quantify seed instability only and do not support
population-wide claims about Higgs.

## Evidence Summary

| Train fraction | Future AUC (mean +/- SD) | 95% t-CI | Train AUC (mean +/- SD) | Future Brier (mean +/- SD) | Future ECE (mean +/- SD) | AUC < 0.5 seeds |
| --- | --- | --- | --- | --- | --- | --- |
| 0.60 | 0.629 +/- 0.146 | [0.525, 0.734] | 0.960 +/- 0.033 | 0.235 +/- 0.088 | 0.182 +/- 0.111 | 42, 48 |
| 0.65 | 0.634 +/- 0.147 | [0.529, 0.739] | 0.955 +/- 0.036 | 0.231 +/- 0.086 | 0.195 +/- 0.097 | 42, 48 |
| 0.70 | 0.631 +/- 0.147 | [0.526, 0.736] | 0.951 +/- 0.039 | 0.232 +/- 0.086 | 0.197 +/- 0.099 | 42, 48 |

Train reconstruction is consistently high, whereas future-edge AUC has a
large seed-dependent spread. Seeds 42 and 48 score below 0.5 at every one of
the three temporal cutoffs. Their inverted scores exceed 0.5, so those runs
are directionally reversed on future edges rather than merely uninformative.

## Decision

The current frozen protocol supports reporting the influence-maximization
outcomes as empirical optimization results, subject to their existing baseline
and data-provenance caveats. It does **not** support a mechanism claim that
the learned edge probabilities are reliably calibrated predictors of future
interactions. Any model repair requires a new versioned protocol and a fresh
experiment batch; the frozen results remain unchanged.

## Claim Candidates

- Claim:
  - Source evidence: all 30 audit runs and Figures 1-2.
  - Allowed wording: "Temporal edge-prediction quality was seed-unstable; two
    seeds produced below-random future ranking at every evaluated cutoff."
  - Forbidden stronger wording: "The learned probabilities reliably predict
    future activation" or "the GNN is consistently temporally calibrated."
  - Uncertainty: results use one Higgs sample and balanced sampled non-edges.
  - Next check: version a temporal objective/validation protocol and rerun all
    influence comparisons under it.
  - Decision: revise.

- Claim:
  - Source evidence: deterministic audit-to-frozen AUC reconciliation.
  - Allowed wording: "The audit reproduces the frozen calibration outputs to
    the stored four-decimal precision."
  - Forbidden stronger wording: "Reproducibility establishes causal validity."
  - Uncertainty: this validates execution consistency, not suitability of the
    prediction target.
  - Next check: preserve the data hashes and code revision with future runs.
  - Decision: keep.
