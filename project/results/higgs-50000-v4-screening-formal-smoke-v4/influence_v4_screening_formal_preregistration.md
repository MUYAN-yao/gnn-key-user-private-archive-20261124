# Influence v4 Screening Formal Preregistration

Date: 2026-09-16

## Scope and version boundary

This is a separately versioned paired comparison of candidate screening rules.
It does not modify or pool the v1, v2, v2-T0b, v2-T0c, v2-T0d, v3, or
v4-screening-diagnostic artifacts. Every formal artifact is written below a
new directory whose name contains `v4-screening-formal`.

The study asks whether a learned GNN node prior provides an incremental
screening benefit over a time-decayed weighted out-degree ranking when the
probability graph, robust greedy optimizer, objective, candidate budget, and
diffusion worlds are held fixed. PageRank and uniform random membership are
auxiliary reference arms.

The diagnostic run at fraction 0.70 and seed 48 is excluded from the formal
sample. Formal runs use only fractions 0.60, 0.65, and 0.70 crossed with seeds
52 through 61, for 30 paired protocol blocks.

## Fixed inputs and analysis constants

- Dataset: hash-verified Higgs `pilot-50000` only.
- Windows: timestamp-grouped history, supervised, calibration, and outer-test
  windows inherited from v2-T0b; all boundaries must be strictly increasing.
- T0: one GATv2 layer, width 32, 10 epochs, learning rate 0.01,
  concatenation MLP decoder, isotonic calibration, probability bounds
  `[0.02, 0.98]`.
- Candidate pool: 120 nodes for every arm.
- Seed budget: 2; IC horizon: 4.
- Objective: `J = mean_spread - 0.35 * spread_std + 0.25 * community_coverage`.
- Selection worlds: 20 deterministic worlds, namespace 101.
- Evaluation worlds: 20 deterministic worlds, namespace 202; disjoint from
  selection worlds and used for all reported arm comparisons.
- Uniform-random membership: namespace 303, sampled without replacement from
  the canonical string-sorted node universe.
- Arm execution order: deterministic per block using namespace 404 and stored
  in the artifact; it does not alter candidate membership or random worlds.

The inherited probability routine excludes calibration negatives using edges
observed anywhere in the fixed dataset. This study therefore retains the
transductive/future-aware limitation of v4 and does not claim a strictly
online probability pipeline.

## Candidate arms and deterministic decisions

1. **GNN prior**: descending calibrated learned node prior, then node ID.
2. **Weighted out-degree**: descending time-decayed edge-weight sum, then node
   ID.
3. **PageRank**: standard weighted PageRank on the decision graph, then node ID.
4. **Uniform random**: one independently generated 120-node membership sample.

After membership is fixed, each arm uses the same ascending string node-ID
order for robust greedy. Candidate scores are rounded to six decimal places
before comparison, objective ties are exact at that precision, and the first
candidate in the common order wins. The selected 120-node membership
ranking/sample and the canonical search order are stored for every arm.

## Timing and artifact requirements

Each block stores the shared load, window, graph, and probability-stage
timings. The probability implementation currently exposes training,
calibration, and inference as one callable; the formal runner records this as
`training_calibration_inference_seconds` rather than inventing a decomposition.
For every arm it records membership generation, candidate sorting, selection
search, final selection-world scoring, independent evaluation-world scoring,
and total arm time. CUDA synchronization is used around timed stages when a
CUDA device is available. Hardware, Python/package versions, source hashes,
input hashes, window boundaries, the canonical node-universe digest, world
lists and digests, candidate lists,
every candidate score in both greedy rounds, selected sets, winner/runner-up
margins, tie counts, per-world spreads, and phase timings are mandatory.

Artifacts are written one block at a time. A non-empty output directory is
never overwritten unless `--resume` is given. A smoke run may use one block and
a reduced candidate pool only to validate instrumentation; it is marked
`not_eligible_for_inference` and must not enter the formal analysis.

## Statistical questions and families

The primary metric is the common evaluation-world robust objective J. For each
fraction, the primary contrast is GNN minus weighted out-degree, giving three
paired contrasts. The auxiliary contrasts are GNN minus PageRank and GNN minus
uniform random, giving six contrasts in a separate family. Each contrast uses
the ten matched seeds within one fraction; the 30 blocks are not treated as
independent network samples.

For each contrast report the paired mean difference, sample SD, and the 95%
paired t interval as a descriptive uncertainty summary. The exact two-sided
sign-flip p-value is the preregistered inferential test; report its
Holm-adjusted p-value within the declared family, paired Cohen dz, and
win/tie/loss counts. If all paired differences are zero, dz is undefined and
must be reported as null; exact
equality is not converted into an equivalence claim. Report all prespecified
contrasts regardless of direction or significance.

The formal batch does not justify a claim that GNN improves the learned
probability model itself: all four arms share the same learned probability
graph within a block. Any result is limited to candidate membership under the
specified simulation and protocol.

## Decision boundary

If GNN and weighted out-degree select the same sets with indistinguishable J,
the manuscript retains candidate reduction as a conditional cost/result
observation and withdraws an independent learned-screening advantage. If
differences occur, wording is limited by fraction, effect size, and Holm result.
No post-hoc additional seeds, pools, objectives, or arms may be appended to
change the conclusion.
