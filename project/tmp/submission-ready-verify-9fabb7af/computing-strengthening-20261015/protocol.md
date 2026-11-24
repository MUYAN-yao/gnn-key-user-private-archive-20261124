# Frozen extension protocol, v1 (2026-10-15)

This is a prospective computational extension designed after reading the original
study. It is not a preregistered replication on previously unseen networks. Only
resource timings (no new extension selections or utility outcomes) were inspected
before this freeze. The historical audit replay is a correctness check.

## Questions and design
1. Does higher selection resolution stabilize membership, independent utility, or both?
2. Do weighted-degree restrictions behave differently from topology degree, PageRank,
   and randomized pools at equal candidate counts?
3. Does sensitivity persist under changed p/h and fixed-live-edge coupling?
4. What loss-tolerance/cost curves describe this finite collection of instances?

All real graphs retain the original first 65% complete timestamp groups, directed
endpoint topology and lexicographic node IDs. No learned representations or new
pruning method. Four source networks: invs2013, invs2015, kenya2012, sfhh2009.

## Matrix (520 unique conditions)
- Resolution: all four graphs, k=5, paths 1001..1010, W=20,80,320,1280,5120,
  p=.01, h=3, step coupling (200).
- Larger seed budgets: invs2013/invs2015/kenya2012, k=20, same ten paths,
  W=320,1280, p=.01, h=3, step coupling (60).
- Parameter sensitivity: all four graphs, k=5, ten paths, W=320, step coupling;
  (p,h)=(.005,3),(.05,3),(.01,1),(.01,5) (160).
- Coupling control: all four graphs, k=5, ten paths, W=320,1280, p=.01,h=3,
  fixed edge coupling using step-zero hash for each directed edge (80).
- Scale/structure sensitivity: one BA(2000,3) and one four-block SBM(500 each;
  within p=.012/between p=.0005), generation seed 20261015; bidirectional edges,
  k=5, paths 1001..1005, W=80,320, p=.01,h=3, step coupling (20).
Synthetic graphs are two fixed instances, not 10 independent network replicates.
Their event-weighted degree equals topology degree by construction.

## Arms and world control
Nine arms: full; weighted 2k,4k,8k; topology degree 4k; PageRank 4k; three
independently randomized 4k pools. Pool randomization is nested within each
network/path and fixed across W and p/h. Random-pool repeats are averaged
within a path for across-path inference. Pool size is min(n,factor*k).
The whole graph always propagates; eligibility alone changes.

Selection IDs are SHA256(namespace|dataset|path|selection|index), first 63 bits;
evaluation uses a different family and 10,000 worlds. Paths are nested in W;
evaluation worlds are shared across all arms, budgets and parameter settings
within each network/path. No tuning or arm selection uses these outcomes.
Explicitly check uniqueness and cross-family/path collisions for the used IDs.
Hash pseudorandomness is reproducible but not a proof of mathematical independence.

## Computational semantics and correctness
Compiled exhaustive enumeration exactly follows archived step-coupled IC; no
CELF or submodularity assumption. Scores compare integer total spread, equivalent
to archived rounded means at these W values (minimum nonzero gap >=1/5120).
Lexicographic tie-breaking. Preserve per-round totals, winners, margins, tie counts,
candidate membership and all per-world evaluation spreads.
Fixed-edge coupling is a separately identified control, not a silent change of
the original simulator. Its worlds reduce to h-hop reachability coverage.
The old step-coupled finite objective is not guaranteed monotone; an explicit
three-node counterexample is part of the audit, not evidence of biased expected IC.

## Outcomes and analysis fixed before the extension
Primary: paired candidate-minus-full independent mean spread and incremental
spread sigma-k at W=5120,k=5,p=.01,h=3 (four real graphs), with actual coverage
and selection time. Secondary: reference changes across W; other settings.
Report path-level values, sample SD, bootstrap mean intervals (10,000 path
resamples; ten paths, limited precision), and conditional paired MC intervals.
No pooling of independent-network inference. Random arms average within path.
Primary two-sided exact sign tests across paths for six restricted method types
(weighted2/4/8k,degree4k,pagerank4k,random4k) vs full, four networks: 24-contrast
Holm family. Zero differences are dropped and reported; tests address sign
balance/median direction conditional on these fixed graphs, not mean superiority.
Report effect sizes in activated nodes and avoid selective significant-only reporting.
No prespecified practical noninferiority margin is available. Tolerances
0,1,2.5,5,10,20 percent of incremental full spread are descriptive sensitivity
readouts, not formal noninferiority or equivalence declarations. Nonpositive
incremental denominators produce NA. Conditional loss bounds divided by a
point-estimate denominator are descriptive, not ratio confidence bounds.

## Timing and resources
Serial single-worker computation, warm JIT; no concurrent experimental workers.
Record graph preparation, ranking, shared world preparation, selection, evaluation,
absolute elapsed time and peak process working set. Online scenario: graph and
worlds prepared; offline end-to-end: allocated shared preparation plus ranking,
selection and evaluation. Report scopes explicitly; compare arms on identical code.
Randomized execution order per condition. For each real graph, k5/W320/path1001,
repeat all arm selections/evaluations in five additional randomized timing trials.
JIT compilation is recorded separately; do not blend old Python and new compiled
timings. Native code preflight: SFHH W1280/k5 ~3.26s, invs2015 W320/k20 ~3.01s,
SFHH p=.05/h5/W320 ~16.44s. Expected full extension order 20–45 minutes with
uncertain hardware scaling. User explicitly authorized unrestricted duration.
Any exception preserves completed hashed outputs and blocks completion claims;
no outcome-based condition exclusions or replacement.

## Provenance and delivery
Freeze engine/runner/config/protocol hashes before execution and verify on start
and completion. Each condition records source/input/graph/world hashes. Resume
only identical protocol and sources; immutable result files, checkpoint manifest.
Original 42-condition outputs remain unchanged. New main manuscript must identify
old findings, audit results and prospective extension separately. No public upload.
