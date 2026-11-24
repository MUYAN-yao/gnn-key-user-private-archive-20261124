# Influence v5 Candidate-Reduction Preregistration

Date: 2026-09-17

## Purpose and contribution boundary

This is a new, separately versioned validation of a narrow claim: under the
stated simulation protocol, can a small screened candidate set reproduce the
selection and common-world evaluation of full-candidate robust greedy search at
a seed budget larger than the existing `k=2` evidence?

It does not claim a new GNN architecture, learned-probability efficacy, causal
diffusion, GNN superiority over weighted-degree screening, statistical
equivalence, or end-to-end acceleration. It does not alter or pool v1, v2,
v2-T0b, v2-T0d, v3, v4-diagnostic, or provenance-limited v4-formal outputs.

## Data and scope

The study uses only the two locally hash-verified processed inputs below.

| Dataset | Directory | Nodes / edges / cascade events | nodes.csv SHA-256 | edges.csv SHA-256 | cascades.csv SHA-256 | Scope limit |
| --- | --- | ---: | --- | --- | --- | --- |
| Higgs 50k | `data/processed/higgs-twitter/pilot-50000` | 33,529 / 50,000 / 50,000 | `04560116149c19d1bd7f0dcdaad6b70dbbaa32cf1932cab9221c2aeebfac8e57` | `5178d5be13faf6b0875b584e936d24d8043112dcc1b25b0b49ea95dc17f5b7f9` | `d503d39922201baa8dd018c187beb7500c5cf5910ce745c948478525f867b552` | Activity-derived interactions; no complete causal cascade truth. |
| Digg 20k | `data/processed/digg/pilot-20000` | 7,321 / 2,111 / 20,000 | `b1ee9740805a04f594c8e0f1ee102131f7ba1db661fef4992d83a9f80769cb56` | `95b4163488e4ae690eba7e42f839db27c0a61cda0d13f6733783694152b16d67` | `18fe5afa3196de05e6757e6c1015d6dcc434f4740d28db51be44021ce778c246` | Flow links are inferred exposure proxies, not observed reshare parents. |

Digg provides an independent network only for this **conditional simulated
selection** check. It is not admitted as causal-propagation validation, and no
result may describe its inferred parent links as observed spread.

## Fixed protocol

- Training fraction: 0.65 only. This is a single predeclared mid-prefix
  condition, not one of several fractions to be selected after results.
- Formal stochastic protocol seeds: 63--72 (ten matched blocks per dataset).
  Seed 62 is reserved only for the non-inferential timing preflight and is
  excluded from every formal table and test.
- Selection budget: `k=5`; IC horizon: 4; risk lambda: 0.35; community weight:
  0.25.
- One shared learned probability graph is fitted per dataset-seed block using
  the fixed T0 configuration: one GATv2 layer, width 32, 10 epochs, learning
  rate 0.01, concatenation MLP decoder, isotonic calibration, and probability
  bounds `[0.02, 0.98]`.
- The inherited calibration-negative rule excludes pairs observed anywhere in
  the fixed dataset. The study is transductive and retrospective; it does not
  claim a strictly online probability pipeline.
- Candidates are selected with 20 deterministic selection worlds. Primary
  reporting uses a disjoint set of 100 deterministic evaluation worlds; a
  second, disjoint 100-world stability set is reported as a sensitivity check.
  Every world list, namespace, and digest is stored in each artifact. Canonical
  edge-time randomization must be independent of Python container traversal.
- Candidate scores are rounded to six decimals before a winner is compared.
  Ties use a stored canonical ascending string-ID candidate order.

## Arms

Each arm uses the same probability graph, objective, selection worlds, and
evaluation worlds in a given block.

1. `full_candidate`: robust greedy over the complete decision graph.
2. `gnn_pool_30`: robust greedy over the top 30 learned-prior nodes.
3. `gnn_pool_60`: robust greedy over the top 60 learned-prior nodes.
4. `gnn_pool_120`: robust greedy over the top 120 learned-prior nodes.
5. `weighted_out_degree_pool_120`: robust greedy over the top 120 nodes ranked
   by time-decayed weighted out-degree.

The first four arms define the candidate-reduction and failure-boundary
question. The weighted-degree arm is a same-budget reference and does not
create a learned-screening superiority claim.

## Outcomes and analysis

Primary contrasts are `gnn_pool_120 - full_candidate`, one contrast per
dataset. The robust objective is calculated on the common 100-world primary
evaluation set. Report paired mean difference, sample SD, 95% paired t
interval, exact two-sided sign-flip p-value, Holm-adjusted p-value across the
two primary contrasts, win/tie/loss counts, and Cohen dz. A zero-variance
difference has undefined dz; exact equality is not converted to equivalence.

Secondary contrasts are `gnn_pool_30 - full_candidate`,
`gnn_pool_60 - full_candidate`, and
`weighted_out_degree_pool_120 - full_candidate`, separately Holm-adjusted over
their six dataset-by-arm contrasts. All outcomes are reported regardless of
significance.

For every arm and seed, also report ordered Top-K identity with the full arm,
Jaccard overlap, both 100-world objective values, mean spread, spread SD,
community coverage, and stage timings. The 30/60/120 pool sequence is a
failure-boundary description: the smallest pool retaining the full arm's
ordered Top-K and common-world objective within each block is recorded; a
difference is retained as a failure, not filtered out.

The 100-world stability set is not a second primary test. It checks whether the
reported full-versus-screened direction or exact tie is preserved under an
independent evaluation-world set. A changed direction or loss of an exact tie
is reported as Monte Carlo sensitivity, not hidden by pooling the two sets.

## Cost accounting

Record shared stages separately: load/validation, window partition, decision
graph construction, training-calibration-inference, and learned-prior scoring.
For every arm record membership generation, sorting, greedy search,
selection-world final scoring, 100-world primary evaluation, 100-world
stability evaluation, and total arm time. Synchronize CUDA around timed stages
when available. The complete cost is `shared stages + arm-specific stages`; no
arm may be assigned zero probability-model cost merely because that graph is
shared.

## Preflight and resource stop rule

Before formal execution, run a new non-inferential preflight for each dataset
at fraction 0.65 and seed 62. It uses the exact formal k=5 arms and output
schema, writes below `audits/candidate-reduction-v5-cost-preflight/`, and is
marked `not_eligible_for_inference=true`. Only integrity and elapsed-time
fields may be used for its resource decision; its selected seeds, objectives,
and arm comparisons must not be read into the formal analysis.

Launch the fixed 20-block formal batch only if both preflights pass schema and
hash validation, each full-candidate arm completes within 14,400 seconds, and
the sum of their full-arm elapsed times multiplied by ten is at most 72 hours.
If any condition fails, do not change k, pools, worlds, seeds, objectives, or
datasets to obtain a cheaper positive result. Preserve the preflight and report
the feasibility limit; any replacement study needs a new version and protocol.

During formal execution, a block exceeding 18,000 seconds or failing its
integrity checks stops the batch. Existing completed artifacts remain
preserved, but the incomplete batch is ineligible for inferential claims.

## Reproducibility and anti-drift requirements

- Build a dedicated v5 runner, validator, analysis script, and tests in new
  paths; no existing study file or output directory may be modified.
- Before preflight, create an immutable local source snapshot containing the
  runner, validator, analysis code, required backend modules, this protocol,
  dependency record, and a SHA-256 manifest. Both preflight and formal outputs
  must reference that snapshot manifest. The runner must verify every source
  hash before it writes an artifact.
- A non-empty preflight or formal output directory is rejected unless an
  explicit resume check verifies every matching protocol, input, snapshot, and
  schema hash. The final manifest includes every run-file hash and a tabular
  metrics copy.
- A dry run writes nothing. A bounded smoke run is clearly ineligible and
  cannot be merged with preflight or formal results.

## Interpretation rules

- If 120-node screening reproduces full search at k=5 on both datasets, claim
  only an observed protocol-conditional preservation and measured cost profile.
- If a smaller pool fails, describe that threshold as a failure boundary; it
  does not invalidate successful larger pools.
- If 120-node screening fails, withdraw any preservation generalization beyond
  the existing k=2 Higgs result and report the observed failure.
- A weighted-degree tie or advantage does not prove learned priors are useless;
  it limits any claim that observed reduction value is uniquely due to GNN
  ranking.
- No result supports causal spread, online deployment, cross-hardware speedup,
  real-world intervention benefit, or a general equivalence theorem.
