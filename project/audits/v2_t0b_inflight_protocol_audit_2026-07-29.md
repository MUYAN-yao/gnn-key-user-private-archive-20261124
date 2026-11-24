# In-Flight v2-T0b Protocol Audit

## Scope

Read-only audit of the seventeen v2-T0b artifacts present on 2026-07-29:
`split-0.60-seed-42.json` through `split-0.60-seed-51.json`, and
`split-0.65-seed-42.json` through `split-0.65-seed-48.json`. This audit does
not inspect, aggregate, or interpret performance values.

## Checks

All seventeen artifacts passed every checked invariant:

| Invariant | Expected value | Result |
| --- | --- | --- |
| Training fraction | 0.60 (10 artifacts); 0.65 (7 artifacts) | 17/17 match |
| Random seeds | 0.60: 42--51; 0.65: 42--48, one artifact each | 17/17 match |
| Method identifier | `gnn_guided_robust_greedy_v2_t0b` | 17/17 match |
| Strict timestamp order | calibration cutoff < outer-test start | 17/17 pass |
| Evaluation protocol | `common_random_numbers` | 17/17 match |
| Seed count | 2 | 17/17 match |
| IC horizon | 4 | 17/17 match |
| Risk coefficient | 0.35 | 17/17 match |
| Community weight | 0.25 | 17/17 match |
| Diffusion simulations | 20 | 17/17 match |
| Candidate-pool size | 120 | 17/17 match |

## Boundary

The formal study remains incomplete at 17/30 artifacts. This audit verifies
that the existing artifacts respect the preregistered protocol; it does not
admit a partial result into the manuscript, does not replace the final batch
manifest, and does not replace the required post-completion aggregation and
paired-statistics analysis.
