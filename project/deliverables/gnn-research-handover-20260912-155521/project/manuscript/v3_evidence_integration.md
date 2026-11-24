# v3 Evidence Integration Note

## Status

The v3 fairness and sensitivity protocol is pre-registered but not yet a
completed study. Its bounded one-run smoke audit at
`audits/v3-fairness-sensitivity-smoke-2026-08-15/` verifies frozen Higgs input
hashes, strict timestamp ordering, deterministic canonical diffusion,
disjoint selection/evaluation world families, and the output schema. The
separate formal batch currently has three of 30 non-smoke artifacts, which
pass read-only integrity checks with an empty error log but have neither a
final manifest nor inferential eligibility. Neither smoke nor partial-batch
numbers may appear in the Results section.

## Intended Results Structure After Completion

1. Primary fairness: screened robust greedy versus an independent
   full-decision-graph robust greedy comparator.
2. Candidate-pool sensitivity: 60, 120, 240, and 480 candidates, reporting
   held-out robust objective, selection time, and overlap with the full search.
3. Objective-weight sensitivity: the preregistered 3x3 selection grid,
   evaluated under one common reporting objective.

Each family has its own exact paired sign-flip test, effect size, confidence
interval, and Holm correction. GNN Top-K remains a protected lower-bound audit
and is never an independent efficacy comparator.

## Required Claim Boundary

If the full batch is incomplete, fails integrity checks, or yields no Holm-
supported contrast, retain the existing frozen claims and describe v3 only as
a negative or incomplete fairness audit. If objective-weight arms remain
identical, report that protocol-specific null result and do not claim universal
irrelevance or optimal weights.
