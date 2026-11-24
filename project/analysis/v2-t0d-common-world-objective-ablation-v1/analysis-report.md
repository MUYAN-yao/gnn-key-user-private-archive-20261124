# Higgs v2-T0d Common-World Objective-Ablation Analysis

## Question and Unit

Within each strict timestamp-grouped Higgs fraction, how does removing one or
both objective terms change seed selection when all four arms share one trained
probability map and deterministic edge-time diffusion worlds? The unit is one
fraction-seed run. The primary score is the same full objective for all arms.

## Exact Numerical Summary

Difference is `full - ablation`; positive favors the complete objective. Holm
correction covers all 9 preregistered contrasts.

| Train fraction | Ablation | Difference (mean +/- SD) | 95% t-CI | W/T/L | Exact p | Holm p | Cohen dz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.60 | Risk penalty removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.60 | Community reward removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.60 | Both terms removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.65 | Risk penalty removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.65 | Community reward removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.65 | Both terms removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.70 | Risk penalty removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.70 | Community reward removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |
| 0.70 | Both terms removed | 0.000 +/- 0.000 | [0.000, 0.000] | 0/10/0 | 1.000000 | 1.000000 | 0.00 |

## Claim Boundary

Only Holm-supported contrasts may be described as evidence that a term changes
the selected-set score, and only for this separately versioned Higgs protocol.
The analysis does not establish universal term importance, causal diffusion,
cross-dataset generalization, or interchangeability with v2-T0b.
