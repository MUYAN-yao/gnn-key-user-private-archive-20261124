# Frozen external-real-network validation protocol, v1 (2026-10-15)

## Status and evidence separation

This local protocol is frozen after a timing-and-resource preflight and before
inspection of any new-network seed or utility result. It is not a public
preregistration. The historical 42-condition evidence and the prior 520-condition
extension remain separate, immutable evidence layers. This protocol creates a
third, external-real-network layer.

## Questions

1. On three new observed topologies, does the selection-world budget change the
   independent evaluation of restricted candidate methods?
2. Do degree-4k and PageRank-4k reproduce full greedy trajectories at low and
   high predeclared selection budgets?
3. When a full-greedy reference set changes across budgets, how often does its
   independent diffusion utility change materially under shared evaluation worlds?
4. At several descriptive loss tolerances, what measured selection and
   end-to-end costs can each eligible-pool restriction save?
5. Do these observations vary across a temporal communication network, an
   reciprocalized collaboration topology and a dense directed voting topology,
   and between step-indexed and fixed-edge world coupling?

## Data and preprocessing

The exact sources, terms caveat, transformations and scope limits are recorded
in `data_selection.md`. The three gzip source hashes and the deterministic graph
metadata are in `data/source_manifest.json`. CollegeMsg alone has authentic
temporal event counts, so it alone receives a `history_weighted` ranking. Static
edge lists are never described as real diffusion cascades or supplied with
fabricated weights.

## Preflight and feasible matrix

Outcome-blind preflight used full greedy, k=5, p=.01, h=3 and W=80/320 with
1,000 independent evaluation worlds but persisted no seeds or utilities. Its
W=320 full-greedy timings were 2.67 s (CollegeMsg), 10.17 s (ca-GrQc), and
39.38 s (wiki-Vote); peak Windows working sets were below 625 MB. The main matrix
therefore uses five independent selection paths at W=80, 320 and 1,280 for each
network. W=5,120 is intentionally outside this frozen primary matrix: linear
projection from the outcome-blind wiki-Vote W=320 timing alone is about 10.5
minutes per full-greedy path before restricted-pool arms and repeat timing. A
future W=5,120 study requires a separately frozen extension rather than an
outcome-conditioned addition.

The main resolution stage has 45 conditions: 3 datasets × 5 paths × 3 budgets,
under step-indexed coupling. A fixed-edge control has 9 conditions: 3 datasets
× 3 predeclared paths at W=320. The matrix deliberately does not add propagation
parameter sweeps or new influence-maximization algorithms; it concentrates
computing on the five stated questions.

## Simulator and randomization

The new engine imports the prior compiled exhaustive IC core byte-for-byte. It
uses per-round enumeration of every eligible but unselected node; it does not
use CELF, pruning or a submodularity assumption. Nodes are lexicographically
ordered; equal finite-world totals resolve to the first such node. Candidate
restriction changes seed eligibility only, never the graph used for diffusion.

Primary diffusion is IC with probability .01 and horizon 3. A step-indexed hash
couples worlds between arms within a condition. The fixed-edge control hashes an
edge only once per world and is separately labelled. World identifiers are
SHA256-derived and use separate selection/evaluation families. For a path,
selection IDs are prefixes as W rises; evaluation IDs are disjoint and number
10,000. Candidate-pool randomization derives only from the frozen namespace,
dataset, path and repeat, so it is held across W and coupling for that path.

## Arms and timing

Every graph includes full eligibility, degree-4k, PageRank-4k, three random-4k
pools, degree-5%-coverage and PageRank-5%-coverage. CollegeMsg additionally
includes history-weighted-4k and history-weighted-5%-coverage. Here 4k means
`min(n, 4*5)=20` eligible nodes; 5% means `min(n, ceil(.05*n))`. Report actual
candidate counts and coverage; do not interpret the two pool-size schemes as
interchangeable.

All conditions execute serially after JIT warmup. For each dataset, path 1101
at W=320 in the main stage repeats every arm five times in randomized order,
checking equal selected sequences and equal per-world values. Report graph
preparation, ranking, selection/evaluation-world preparation, selection,
evaluation, condition elapsed time and peak working set. End-to-end costs add
the shared preparation and arm-specific costs; online costs exclude work assumed
precomputed. No result can exclude or replace a condition.

## Analysis frozen before outcomes

The primary comparisons at W=1,280 are degree-4k, PageRank-4k and the mean of
the three random-4k pools against full greedy, separately for each fixed graph.
Report ordered-trajectory and final-set agreement, Jaccard, first divergence,
paired independent utility differences, total/incremental spread, conditional
Monte Carlo standard errors, path-level variation, actual coverage and cost.
For the three fixed primary contrasts within each graph, use two-sided exact
sign tests over nonzero path differences and Holm correction; report effect
sizes and dropped zeros. Five paths do not justify a claim about a population of
networks. Do not pool paths, worlds, arms or conditions as independent networks.

Loss tolerances 0, 1, 2.5, 5, 10 and 20 percent of each path's full incremental
spread are descriptive decision curves, not a noninferiority test. Intervals
crossing zero, a nonsignificant sign test or an unchanged trace cannot establish
equivalence or noninferiority.

## Verification, failures and provenance

Before every execution, the runner verifies the frozen source manifest including
the data-source manifest, protocol and config. Each condition writes immutable
NPZ arrays plus JSON metadata including source, graph and world hashes. It
checks source/evaluation disjointness, candidate uniqueness, full-pool identity,
spread bounds, complete-pool reproduction and repeat-timing equality. A partial
condition blocks resume until inspected; a failed condition is retained in the
status log and prevents a completed-study claim.
