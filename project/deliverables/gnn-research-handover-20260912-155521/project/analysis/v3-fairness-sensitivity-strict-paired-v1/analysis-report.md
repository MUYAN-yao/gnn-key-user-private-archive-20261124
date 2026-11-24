# Higgs v3 Fairness and Sensitivity Analysis

## Questions and Unit

The primary question asks whether GNN-screened robust greedy differs from an
independent full-decision-graph robust greedy search under the common reporting
objective. Candidate-pool and objective-weight sensitivity are separate
questions. Each contrast has ten paired stochastic protocol runs per strict
timestamp fraction; these are not independent social-network samples.

## Exact Numerical Summary

Difference is `reference - comparator`. Positive values favor the stated
reference. The three families each have their own Holm correction: three primary
fairness contrasts, nine pool contrasts, and twenty-four non-base weight-arm
contrasts. GNN Top-K is retained in the source artifacts only as a protected
lower-bound audit and is absent from every efficacy family.

| Family | Fraction | Reference | Comparator | Mean +/- SD | 95% t-CI | W/T/L | Exact p | Holm p | Cohen dz |
| --- | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| primary_fairness | 0.60 | screened_robust_greedy | full_candidate_robust_greedy | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| primary_fairness | 0.65 | screened_robust_greedy | full_candidate_robust_greedy | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| primary_fairness | 0.70 | screened_robust_greedy | full_candidate_robust_greedy | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.60 | screened_pool_120 | screened_pool_60 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.60 | screened_pool_120 | screened_pool_240 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.60 | screened_pool_120 | screened_pool_480 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.65 | screened_pool_120 | screened_pool_60 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.65 | screened_pool_120 | screened_pool_240 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.65 | screened_pool_120 | screened_pool_480 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.70 | screened_pool_120 | screened_pool_60 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.70 | screened_pool_120 | screened_pool_240 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| candidate_pool_sensitivity | 0.70 | screened_pool_120 | screened_pool_480 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.25 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.25 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.60 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.25 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.25 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.65 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.25 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.00_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.00 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.35_community-0.50 | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.00 | 10.751 +/- 33.998 | [-13.570, 35.072] | 1/9/0 | 1.000000 | 1.000000 | 0.32 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.25 | 10.751 +/- 33.998 | [-13.570, 35.072] | 1/9/0 | 1.000000 | 1.000000 | 0.32 |
| objective_weight_sensitivity | 0.70 | objective_risk-0.35_community-0.25 | objective_risk-0.70_community-0.50 | 10.751 +/- 33.998 | [-13.570, 35.072] | 1/9/0 | 1.000000 | 1.000000 | 0.32 |

## Reporting Metrics and Selection Changes

`sensitivity_descriptives.csv` and `sensitivity-descriptives.md` report the
held-out mean spread, spread standard deviation, community coverage, selection
time, selected-set overlap with the full search, selected-set overlap with the
base screened method, and the number of distinct selected Top-K sets. These
quantities are descriptive complements to the predeclared utility tests above.

## Claim Candidates

- Claim:
  - Source evidence: completed v3 hashes, run artifacts, and the primary
    fairness family above.
  - Allowed wording: only describe a direction when the corresponding Holm
    result supports it, and only for this Higgs v3 protocol.
  - Forbidden wording: GNN Top-K independent superiority, universal algorithmic
    superiority, independent network-population inference, or causal diffusion.
  - Decision: update the manuscript claim ledger only after all three families
    are reviewed.
