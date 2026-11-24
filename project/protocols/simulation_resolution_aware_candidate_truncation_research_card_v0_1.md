# Research card: simulation-resolution-aware candidate truncation

**Version:** 0.1, 2026-09-20. This replaces the unpublishable learned-pruning
claim as the proposed paper direction.

## Research question

When simulation-based greedy influence maximization is run on a candidate
pool, how does the Monte Carlo budget used for *selection* alter the observed
quality--cost frontier and the apparent agreement with full greedy search?

## Central contribution

Define and report a **selection-resolution profile** rather than a single
candidate-pool result. For each graph, `k`, pool policy and nested selection
world budget W, the profile contains (i) the ordered greedy seed set, (ii)
round-level winner margins and exact tie counts, (iii) agreement with the
same-W full reference, (iv) independent evaluation spread, and (v) measured
end-to-end decision cost. The paper tests whether conclusions drawn at a small
W survive a pre-fixed larger W.

This is an empirical computational-methods contribution. It does **not** claim
a new influence-maximization approximation algorithm, a universal pool-size
rule, a causal social-diffusion result, or GNN superiority.

## Existing evidence that supports feasibility

On the complete local v9 development matrix, all eight full-greedy sequences
changed between nested W=20 and W=80, while degree-4k/8k reproduced the W=80
finite-world full sequence in all eight blocks. The result identifies a
measurable failure mode for one-shot candidate-pruning evaluations and a
concrete reporting protocol. The result is development-only because the two
local datasets are not yet admitted confirmation data.

## Confirmation design, fixed before confirmation outcomes

1. Admit at least four independently sourced network instances with explicit
   reusable data terms and documented field semantics. Use the current Digg
   and Higgs files only as labelled case studies unless their source terms are
   independently verified.
2. Use a standard IC task as primary (`p`, horizon, and time split fixed in
   the final protocol). Use candidate policies full, degree-2k, degree-4k,
   degree-8k; retain PageRank only as a negative control. A learned ranking is
   optional only if it is fully reproducible and explicitly secondary.
3. For each network and `k` in {5,20}, re-optimize from nested selection
   worlds W={20,80,320}. Use disjoint common evaluation worlds for all arms
   within each graph/seed/W condition.
4. Report no cross-graph null-hypothesis test as though graph instances were
   random draws. Report per-instance profiles, pooled descriptive summaries,
   and all predefined failures. Do not call a pool “equivalent” if the full
   seed sequence changes over the resolution path without an explicit
   same-W qualifier.
5. Require a reproducibility snapshot, source/data hashes, raw round traces,
   and a non-destructive public code archive before submission.

## Falsification conditions

Abandon this direction if the confirmation layer finds that (a) full seed
sequences are resolution-stable at W=20 across nearly all instances, (b) pool
agreement does not systematically change with W, or (c) the observed local
effect is explained solely by a data-parsing artefact. In those cases the
existing evidence remains a limitation audit rather than a contribution.

## Position against prior work

Candidate reduction, simulation sampling and adaptive-sampling influence
maximization methods already exist. The novelty must be limited to the
auditable *evaluation target*: nested selection-world re-optimization jointly
with candidate-pool agreement, tie/margin diagnostics and disjoint
out-of-sample evaluation. The final related-work review must verify that this
exact protocol is not already published before a submission claim is made.
