# Reviewer-Style Method and Fairness Audit

Date: 2026-07-31

## Scope

This audit reviews the manuscript's method exposition, comparator fairness, and
statistical interpretation against the completed frozen v1 and strict Higgs
v2-T0b evidence. It does not rerun experiments and does not alter any model
configuration or experiment output.

## Evidence Read

- `backend/app/optimizer.py`, especially `gnn_guided_robust_greedy()`;
- `backend/app/pipeline.py` and `backend/app/pipeline_v2_t0b.py`;
- `experiments/build_v2_t0b_paired_analysis.py` and the strict paired report;
- `manuscript/draft_zh_v0_1.md`, claim ledger, statistical appendix, and
  reproducibility appendix.

## Findings and Disposition

### F1: GNN Top-K is a protected lower bound, not an independent comparator

`gnn_guided_robust_greedy()` evaluates both its greedy set and the pure
GNN Top-K set, then returns the one with the higher robust objective under the
same common-random streams. Consequently, the reported GNN Top-K difference is
structurally nonnegative apart from numerical ties. A Holm result against that
set is a valid record of the implemented return rule, but it is not independent
evidence that the complete method outperforms a separately competing baseline.

**Disposition:** manuscript, claim ledger, statistical appendix, and
reproducibility appendix now label the comparison as a protected-lower-bound
audit. The numerical rows remain intact. Independent-efficacy conclusions are
restricted to Degree, PageRank, k-shell, Greedy MC, and RIS within their stated
protocol limits.

### F2: Candidate-pool asymmetry must be explicit

The reference greedily enumerates only the top 120 nodes by its learned prior.
Degree, PageRank, k-shell, Greedy MC, and RIS select seeds over the complete
decision graph and are subsequently scored with the same common-random streams.
This asymmetry does not give the reference a larger search space; however,
omitting it would prevent a reviewer from judging computational and selection
fairness.

**Disposition:** methods and experimental settings now disclose both the
120-node restriction and full-graph baseline selection. No runtime superiority
claim is made.

### F3: Comparator-objective mismatch remains a bounded limitation

The reference optimizes expected spread minus a dispersion penalty plus
community coverage. Greedy MC and RIS are comparison points for expected-spread
optimization and do not optimize the full reported objective. Their outcomes
therefore support protocol-specific contrast under the shared evaluation metric,
not a claim that the reference is the best solver of classical expected-spread
influence maximization. The manuscript already states this for RIS; it should
retain the same interpretation for all expected-spread comparators at template
conversion.

**Disposition:** open submission-facing limitation; no result alteration is
justified. A future study would need independently implemented robust-objective
competitors or ablations to establish a broader algorithmic advantage.

### F4: Strict Higgs inference remains correctly bounded

The strict study has 30 preregistered artifacts, 210 metrics rows, 18 contrasts,
and an exact sign-flip test with Holm correction over that complete family.
Repetitions are stochastic protocol runs, not independent social networks.
All RIS contrasts remain Holm-nonsignificant. The revised interpretation keeps
these limits and does not treat confidence intervals or positive means as a
substitute for the multiplicity-corrected decision.

**Disposition:** no change needed beyond F1 wording.

## Current Reviewer-Facing Assessment

The manuscript now makes the main structural advantage transparent instead of
presenting it as independent baseline evidence. It remains a protocol-bounded
method-and-evaluation contribution. Before submission, the remaining material
risks are literature-depth coverage, the lack of a robust-objective competitor
or ablation that isolates each objective term, author-controlled metadata and
archiving, official-template conversion, and page-by-page visual QA.
