# Higgs v2-T0b Strict Paired Analysis

## Question and Unit

For each preregistered timestamp-grouped Higgs split, does
`gnn_guided_robust_greedy_v2_t0b` change the robust objective relative to each retained baseline?
The unit is one paired protocol run: methods share the timestamp split, random
seed, and common random diffusion streams. Each contrast contains 10
paired runs; this does not represent independent social-network samples.

## Exact Numerical Summary

Difference is `reference - baseline`; positive values favor the reference.
`W/T/L` counts run-level wins, ties, and losses. Holm correction spans all 18
preregistered method-by-fraction contrasts.

| Train fraction | Baseline | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact sign-flip p | Holm p | Cohen dz | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.60 | Degree | 202.967 +/- 128.035 | [111.376, 294.557] | 8/2/0 | 0.007812 | 0.054688 | 1.59 | reference higher |
| 0.60 | PageRank | 3247.322 +/- 680.212 | [2760.728, 3733.917] | 10/0/0 | 0.001953 | 0.035156 | 4.77 | reference higher |
| 0.60 | k-shell | 3007.037 +/- 459.685 | [2678.198, 3335.876] | 10/0/0 | 0.001953 | 0.035156 | 6.54 | reference higher |
| 0.60 | GNN Top-K | 264.736 +/- 253.853 | [83.141, 446.332] | 8/2/0 | 0.007812 | 0.054688 | 1.04 | reference higher |
| 0.60 | Greedy MC | 749.421 +/- 337.014 | [508.335, 990.506] | 10/0/0 | 0.001953 | 0.035156 | 2.22 | reference higher |
| 0.60 | RIS | 8.755 +/- 27.685 | [-11.050, 28.559] | 1/9/0 | 1.000000 | 1.000000 | 0.32 | reference higher |
| 0.65 | Degree | 160.509 +/- 76.850 | [105.534, 215.484] | 10/0/0 | 0.001953 | 0.035156 | 2.09 | reference higher |
| 0.65 | PageRank | 4079.709 +/- 674.077 | [3597.503, 4561.915] | 10/0/0 | 0.001953 | 0.035156 | 6.05 | reference higher |
| 0.65 | k-shell | 3751.071 +/- 466.518 | [3417.344, 4084.798] | 10/0/0 | 0.001953 | 0.035156 | 8.04 | reference higher |
| 0.65 | GNN Top-K | 136.386 +/- 86.011 | [74.858, 197.914] | 9/1/0 | 0.003906 | 0.039062 | 1.59 | reference higher |
| 0.65 | Greedy MC | 845.486 +/- 314.269 | [620.671, 1070.301] | 9/1/0 | 0.003906 | 0.039062 | 2.69 | reference higher |
| 0.65 | RIS | 207.557 +/- 443.503 | [-109.706, 524.820] | 2/8/0 | 0.500000 | 1.000000 | 0.47 | reference higher |
| 0.70 | Degree | 146.175 +/- 107.440 | [69.317, 223.033] | 8/2/0 | 0.007812 | 0.054688 | 1.36 | reference higher |
| 0.70 | PageRank | 4484.479 +/- 851.171 | [3875.588, 5093.370] | 10/0/0 | 0.001953 | 0.035156 | 5.27 | reference higher |
| 0.70 | k-shell | 3983.175 +/- 566.025 | [3578.265, 4388.085] | 10/0/0 | 0.001953 | 0.035156 | 7.04 | reference higher |
| 0.70 | GNN Top-K | 126.685 +/- 122.441 | [39.096, 214.274] | 6/4/0 | 0.031250 | 0.125000 | 1.03 | reference higher |
| 0.70 | Greedy MC | 699.468 +/- 397.368 | [415.208, 983.727] | 9/1/0 | 0.003906 | 0.039062 | 1.76 | reference higher |
| 0.70 | RIS | 179.652 +/- 420.778 | [-121.354, 480.659] | 3/7/0 | 0.250000 | 0.750000 | 0.43 | reference higher |

## Claim Candidates

- Claim:
  - Source evidence: complete v2-T0b `method_metrics.csv`, the paired-comparison
    table, and Figure 1.
  - Allowed wording: fill only after reviewing every contrast and its Holm-adjusted
    result.
  - Forbidden stronger wording: universal superiority, causal diffusion claims,
    or any claim beyond the timestamp-grouped Higgs protocol.
  - Uncertainty: one dataset; ten stochastic paired protocol runs; results remain
    conditional on the preregistered candidate pool and diffusion constants.
  - Next check: update the claim ledger before revising manuscript prose.
  - Decision: pending human-readable evidence review.
