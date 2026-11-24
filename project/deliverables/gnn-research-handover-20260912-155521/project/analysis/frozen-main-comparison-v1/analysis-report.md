# Frozen Main-Comparison Analysis

## Question and Unit

For each dataset and temporal split, does `gnn_guided_robust_greedy` improve
the robust objective relative to Degree, GNN Top-K, Greedy MC, and RIS? The
unit is a paired run: all methods use the same split, random seed, and common
random diffusion streams. There are 10 paired runs per contrast.

## Exact Numerical Summary

Difference is `main method - baseline`; positive values favour the main method.
`W/T/L` counts main-method wins, ties, and losses across the 10 paired runs.

| Dataset | Train fraction | Baseline | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact sign-flip p | Holm p (24 tests) | Cohen dz | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Digg 20k | 0.60 | Degree | 25.360 +/- 1.349 | [24.395, 26.324] | 10/0/0 | 0.001953 | 0.046875 | 18.80 | main higher |
| Digg 20k | 0.60 | GNN Top-K | 25.360 +/- 1.349 | [24.395, 26.324] | 10/0/0 | 0.001953 | 0.046875 | 18.80 | main higher |
| Digg 20k | 0.60 | Greedy MC | 10.934 +/- 1.248 | [10.041, 11.827] | 10/0/0 | 0.001953 | 0.046875 | 8.76 | main higher |
| Digg 20k | 0.60 | RIS | 117.766 +/- 3.478 | [115.279, 120.254] | 10/0/0 | 0.001953 | 0.046875 | 33.86 | main higher |
| Digg 20k | 0.65 | Degree | 26.331 +/- 1.899 | [24.972, 27.689] | 10/0/0 | 0.001953 | 0.046875 | 13.86 | main higher |
| Digg 20k | 0.65 | GNN Top-K | 26.331 +/- 1.899 | [24.972, 27.689] | 10/0/0 | 0.001953 | 0.046875 | 13.86 | main higher |
| Digg 20k | 0.65 | Greedy MC | 11.156 +/- 1.140 | [10.341, 11.972] | 10/0/0 | 0.001953 | 0.046875 | 9.79 | main higher |
| Digg 20k | 0.65 | RIS | 134.621 +/- 3.819 | [131.889, 137.353] | 10/0/0 | 0.001953 | 0.046875 | 35.25 | main higher |
| Digg 20k | 0.70 | Degree | 29.265 +/- 1.756 | [28.009, 30.521] | 10/0/0 | 0.001953 | 0.046875 | 16.67 | main higher |
| Digg 20k | 0.70 | GNN Top-K | 29.265 +/- 1.756 | [28.009, 30.521] | 10/0/0 | 0.001953 | 0.046875 | 16.67 | main higher |
| Digg 20k | 0.70 | Greedy MC | 12.583 +/- 2.142 | [11.050, 14.115] | 10/0/0 | 0.001953 | 0.046875 | 5.87 | main higher |
| Digg 20k | 0.70 | RIS | 145.493 +/- 4.391 | [142.352, 148.634] | 10/0/0 | 0.001953 | 0.046875 | 33.14 | main higher |
| Higgs 50k | 0.60 | Degree | 395.109 +/- 161.005 | [279.933, 510.286] | 10/0/0 | 0.001953 | 0.046875 | 2.45 | main higher |
| Higgs 50k | 0.60 | GNN Top-K | 301.294 +/- 85.827 | [239.897, 362.691] | 10/0/0 | 0.001953 | 0.046875 | 3.51 | main higher |
| Higgs 50k | 0.60 | Greedy MC | 928.659 +/- 78.136 | [872.764, 984.554] | 10/0/0 | 0.001953 | 0.046875 | 11.89 | main higher |
| Higgs 50k | 0.60 | RIS | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 | tie |
| Higgs 50k | 0.65 | Degree | 401.491 +/- 218.053 | [245.506, 557.477] | 10/0/0 | 0.001953 | 0.046875 | 1.84 | main higher |
| Higgs 50k | 0.65 | GNN Top-K | 247.809 +/- 74.316 | [194.647, 300.971] | 10/0/0 | 0.001953 | 0.046875 | 3.33 | main higher |
| Higgs 50k | 0.65 | Greedy MC | 700.822 +/- 267.678 | [509.337, 892.307] | 9/1/0 | 0.003906 | 0.046875 | 2.62 | main higher |
| Higgs 50k | 0.65 | RIS | 927.432 +/- 137.168 | [829.308, 1025.557] | 10/0/0 | 0.001953 | 0.046875 | 6.76 | main higher |
| Higgs 50k | 0.70 | Degree | 426.037 +/- 264.878 | [236.555, 615.519] | 10/0/0 | 0.001953 | 0.046875 | 1.61 | main higher |
| Higgs 50k | 0.70 | GNN Top-K | 314.344 +/- 137.466 | [216.006, 412.681] | 10/0/0 | 0.001953 | 0.046875 | 2.29 | main higher |
| Higgs 50k | 0.70 | Greedy MC | 645.459 +/- 121.404 | [558.612, 732.306] | 10/0/0 | 0.001953 | 0.046875 | 5.32 | main higher |
| Higgs 50k | 0.70 | RIS | 1165.466 +/- 106.317 | [1089.412, 1241.521] | 10/0/0 | 0.001953 | 0.046875 | 10.96 | main higher |

## Supported Boundaries

- Digg 20k: the main method has positive paired robust-objective differences
  against all four selected baselines in all three temporal splits.
- Higgs 50k: it has positive differences against Degree, GNN Top-K, and Greedy
  MC in all splits. Against RIS it ties exactly at 0.60, then improves at 0.65
  and 0.70.
- These are optimization outcomes on two datasets. They do not validate the
  learned probabilities as stable predictors of future interactions; see the
  separate Higgs edge-prediction audit.

## Claim Candidates

- Claim:
  - Source evidence: all 24 paired contrasts and Figure 1.
  - Allowed wording: "Across the evaluated temporal splits, the method improved
    the robust objective over Degree, GNN Top-K, and Greedy MC on the frozen
    Digg and Higgs protocols."
  - Forbidden stronger wording: "It universally outperforms all baselines."
  - Uncertainty: two datasets only; Digg uses exposure proxies; paired runs are
    stochastic protocol replicates, not independent social-network samples.
  - Next check: admit a third provenance-qualified cascade dataset.
  - Decision: keep, with scope limitation.

- Claim:
  - Source evidence: Figure 2 and the Higgs RIS rows.
  - Allowed wording: "On Higgs, the method tied RIS at a 0.60 train fraction
    and improved over RIS at 0.65 and 0.70."
  - Forbidden stronger wording: "It dominates RIS at every temporal split."
  - Uncertainty: the exact 0.60 tie arises from identical seed selections.
  - Next check: investigate candidate-pool sensitivity only in a new protocol.
  - Decision: keep.
