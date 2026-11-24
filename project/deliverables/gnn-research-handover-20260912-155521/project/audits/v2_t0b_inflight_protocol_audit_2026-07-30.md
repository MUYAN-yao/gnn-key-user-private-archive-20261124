# In-Flight v2-T0b Protocol Audit

## Scope

Read-only continuation audit of the twenty v2-T0b artifacts present on
2026-07-30: `split-0.60-seed-42.json` through
`split-0.60-seed-51.json`, and `split-0.65-seed-42.json` through
`split-0.65-seed-51.json`. The audit does not inspect, aggregate, or
interpret performance values.

## Checks

All twenty artifacts passed every checked invariant:

| Invariant | Expected value | Result |
| --- | --- | --- |
| Training fraction | 0.60 (10 artifacts); 0.65 (10 artifacts) | 20/20 match |
| Random seeds | 0.60: 42--51; 0.65: 42--51, one artifact each | 20/20 match |
| Method identifier | `gnn_guided_robust_greedy_v2_t0b` | 20/20 match |
| Strict timestamp order | calibration cutoff < outer-test start | 20/20 pass |
| Evaluation protocol | `common_random_numbers` | 20/20 match |
| Probability protocol | `v2_t0b_timestamp_grouped_isotonic` | 20/20 match |
| Seed count | 2 | 20/20 match |
| IC horizon | 4 | 20/20 match |
| Risk coefficient | 0.35 | 20/20 match |
| Community weight | 0.25 | 20/20 match |
| Diffusion simulations | 20 | 20/20 match |
| Candidate-pool size | 120 | 20/20 match |

## Boundary

The formal study remains incomplete at 20/30 artifacts. This audit verifies
that the existing artifacts respect the preregistered protocol; it does not
admit a partial result into the manuscript, does not replace the final batch
manifest, and does not replace the required post-completion aggregation and
paired-statistics analysis.
