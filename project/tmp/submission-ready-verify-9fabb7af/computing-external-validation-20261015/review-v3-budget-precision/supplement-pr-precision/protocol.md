# Post-hoc PageRank numerical-precision control

This protocol is specified after main outcomes and after candidate-overlap-only
diagnostics, before any tightened-ranking diffusion outputs are inspected. It is
a numerical sensitivity analysis, not independent confirmatory replication or
public preregistration. The frozen54-condition study remains unchanged.

Purpose: distinguish frozen NetworkX3.5 default tolerance effects from the major
PageRank loss interpretation. On all three external graphs, compare tol1e-12
(alpha.85,max_iter1000) PageRank pools20 and ceil(.05n) with their frozen default
counterparts, using all five original paths1101–1105, W1280, k5,p.01,h3, step
coupling and the identical10,000 evaluation IDs. No new random paths or data.
The direction, propagation target, tie policy, graph, worlds and greedy objective
remain identical. Ranking candidates use decreasing score then lexical ID;
greedy again sorts eligible IDs lexically. Tightened1e-12 vs1e-14 candidate pools
already match on all six graph/pool-size combinations in the diagnostic.

This creates15 auxiliary conditions and30 additional restricted-arm executions.
Reuse the stored full reference for paired comparisons. Preserve NPZ evaluation
vectors and integer score matrices plus selected/candidate IDs. Recompute all
statistics and compare exact sequences/sets/vectors with frozen PageRank results.
Report every graph and pool size even if the interpretation worsens. No p-value
testing or model tuning is added to the frozen primary family. These are the same
paths, not additional sample size. Do not append their arms to the468 primary arms.

Execute serially after the main replay. Fail on source/input mismatch or partial
results. Preserve any failure file. Do not replace a completed auxiliary file.
New hash manifest covers this protocol, source, diagnostic and frozen-source
manifest hash before execution. A failed condition blocks completion claims.
