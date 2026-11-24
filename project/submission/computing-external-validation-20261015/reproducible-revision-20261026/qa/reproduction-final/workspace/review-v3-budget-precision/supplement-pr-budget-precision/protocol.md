# Post-hoc strict-PageRank budget-sensitivity protocol

## Status and purpose

This protocol is written after inspection of the frozen main matrix and the
W=1280 precision control, but before inspecting any new W=80 or W=320
strict-tolerance utility result. It is a paired numerical sensitivity study, not
a confirmatory replication, a preregistration or new independent sample.

The question is narrow: after candidate pools are computed with NetworkX 3.5
PageRank at `tol=1e-12, max_iter=1000`, does changing the finite selection-world
budget from 80 to 320 to 1280 still change the independently evaluated quality
of the PageRank-restricted seed sets? The original default-tolerance result is
retained as a comparator, rather than replaced.

## Fixed design

- Graphs: CollegeMsg, ca-GrQc and wiki-Vote, using the identical processed graphs,
  raw-input hashes and source snapshot of the 54-condition frozen external study.
- Paths: the five original paths 1101–1105 for each graph. They are computational
  paired paths, not independent network observations.
- Budgets: add `W=80` and `W=320`; incorporate existing strict-tolerance
  `W=1280` results from `review-v2/supplement-pr-precision` only during analysis.
- Arms: PageRank pools of 20 vertices (4k) and `ceil(.05 n)` vertices (5%). This
  creates exactly 3 graphs × 5 paths × 2 budgets = 30 conditions and 60 new arms.
- Propagation: k=5, p=.01, horizon=3, primary step-indexed coupling. Selection
  IDs are the already frozen budget prefixes; evaluation uses the existing,
  disjoint 10,000-world family. Candidate eligibility alone is changed.
- Sorting: decreasing PageRank score, then lexical original node ID. Greedy
  eligibility IDs are lexically ordered under the unchanged integer-score,
  full-per-round enumeration. No CELF, pruning, retuned probabilities or graph
  change is permitted.

## Reused and new evidence

For each condition, the verified frozen JSON/NPZ file supplies the full-reference
seed set and evaluation vector. The new script checks source, graph, selection-ID
and evaluation-ID hashes before using it. It recomputes only restricted arms;
therefore full-greedy is not rerun. If a new seed set equals the recorded default
or full set, its per-world evaluation vector must be byte-identical to the stored
one. All new JSON and NPZ files are write-once.

Before utility calculation, each strict candidate pool must agree with a
`tol=1e-14` ranking for both sizes. The default-versus-strict pool overlap and
changed IDs are stored per graph/pool; they are not treated as utility evidence.

## Analysis and interpretation

The primary output is the paired difference against the same frozen full reference,
reported in nodes, incremental-spread percent loss, conditional Monte Carlo SE and
path variation. It also reports strict-minus-default differences at a fixed budget,
and within-strict budget changes. Candidate-pool changes, seed-set changes and
utility changes are recorded separately.

No new p-value family is introduced. Five paths do not become five networks, and
the 10,000 evaluation worlds do not create extra selection replications. A sign
change without effect magnitude and uncertainty is not described as a substantive
reversal. The result may weaken, replace or preserve the default-tolerance budget
interpretation; no outcome determines graph inclusion or the analysis rule.

## Stop/failure rules

Stop and retain partial files if any frozen source/input/hash check fails, a pool
is unstable at 1e-12 versus 1e-14, an output pair already exists, a spread violates
bounds, an identical seed set yields a different stored evaluation vector, or a
condition fails. A failed or incomplete matrix is reported as such and is not
silently retried in place.
