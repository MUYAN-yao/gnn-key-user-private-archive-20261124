# Influence v6: Digg independent-network k=5 validation

Date: 2026-09-18

## Purpose

This separately versioned experiment tests a narrow question left unresolved
by the completed Higgs k=2 evidence and the v5 feasibility stop: on the
independent Digg network, can a 30/60/120-node screened pool reproduce
full-candidate robust greedy search at a larger seed budget (`k=5`) under a
fixed simulation protocol? It is a conditional simulated-selection study.

It does not alter, pool, repair or reinterpret v1--v5 outputs. In particular,
the v5 Higgs preflight remains a feasibility limit, not a comparative result.
Digg links remain inferred exposure proxies, not observed reshare parents; no
claim concerns causal propagation, intervention benefit or online deployment.

## Fixed design

- Dataset: hash-verified `data/processed/digg/pilot-20000` only; nominal
  training fraction 0.65.
- Preflight: seed 73, non-inferential and excluded from all comparisons.
- Formal repetitions: seeds 74--83, ten matched blocks; no seed selection by
  outcome.
- Probability model: fixed T0 configuration, as implemented in the included
  v5 runner: one GATv2 layer, width 32, ten epochs, learning rate 0.01,
  concatenation MLP decoder, isotonic calibration and probability bounds
  [0.02, 0.98]. Calibration negatives retain the inherited dataset-wide
  observed-edge rule, so the pipeline is transductive and retrospective.
- Decision: `k=5`, IC horizon 4, standard-deviation penalty 0.35,
  seed-community reward 0.25. Twenty deterministic selection worlds are
  disjoint from one primary and one stability set of 100 evaluation worlds.
- Arms: full-candidate robust greedy; GNN-prior pools of 30, 60 and 120;
  and a 120-node weighted-out-degree pool. All arms share a probability graph
  and the three world families within a seed block.

## Outcomes and analysis

The primary contrast is `gnn_pool_120 - full_candidate` in primary robust
objective across the ten formal paired blocks. Report paired mean difference,
sample SD, 95% paired t interval, exact two-sided sign-flip p-value,
win/tie/loss counts and Cohen's dz; do not convert exact equality into
equivalence. The three remaining screened/degree contrasts form a separate
Holm-adjusted secondary family. Record ordered Top-K identity, Jaccard,
primary and stability objective, spread, coverage and stage times in every
block. Stability is a sensitivity check, not a second primary test.

## Resource gate and stopping rule

The preflight must pass input/source/schema integrity. Formal execution is
allowed only if its full-candidate arm is at most 14,400 seconds and ten times
that full-arm time is at most 72 hours. A formal block over 18,000 seconds or
an integrity failure stops the batch and makes it ineligible for inference.
If the preflight fails, do not change `k`, candidate pools, worlds, objective,
seeds or data to obtain a cheaper result. Preserve the artifact and report the
feasibility boundary.

## Reproducibility

The runner must execute only from a verified immutable v6 source snapshot that
contains this protocol, the v6 snapshot/runner code, the exact reused v5
computation code and every transitively imported backend module. Each artifact
records fixed input hashes, source-snapshot manifest digest, world digests and
its own SHA-256 hash. Existing directories are never overwritten. A dry run
writes nothing.
