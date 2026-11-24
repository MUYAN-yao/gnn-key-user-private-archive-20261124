# Frozen v1 Manuscript-to-Code Consistency Audit

## Scope and outcome

This is a read-only audit of the claims and implementation facts used by
`manuscript/draft_zh_v0_1.md`.  It covers only the frozen v1 Higgs-50k and
Digg-20k studies recorded in `reproducibility/frozen-study-manifest-v1.json`.
All eight recorded core-source SHA-256 values matched the manifest.  All 30
Higgs and all 30 Digg run-artifact hashes also matched.  No frozen result,
source file, configuration, or output was modified during this audit.

## Claim-to-implementation mapping

| Manuscript fact | Code / frozen evidence | Audit interpretation |
| --- | --- | --- |
| Robust objective is mean spread minus risk penalty plus community coverage reward | `backend/app/optimizer.py`: `mean - risk_lambda * std + community_weight * coverage` | Matches the equation in Section 3. |
| Spread uncertainty is a population standard deviation estimated from 20 simulations | `backend/app/optimizer.py`: `np.std(values)`; frozen protocol records 20 simulations | `np.std` uses `ddof=0`; manuscript therefore says “总体标准差”, not an unbiased sample estimator. |
| Paired methods use common random diffusion streams | `backend/app/optimizer.py` and frozen run protocol | Supports paired, protocol-level comparisons; it does not establish causal diffusion probabilities. |
| Fixed protocol constants are $k=2$, horizon 4, $\lambda=0.35$, $\eta=0.25$, candidate pool 120, fractions 0.60/0.65/0.70, seeds 42--51 | frozen manifests and `experiments/run_rolling_study.py` | These are study settings, not tuned claims or universal defaults. |
| Node inputs include log weighted in/out degree, prior cascade activity, and PageRank | `backend/app/pipeline.py`, `backend/app/graph.py` | Feature description is implementation-level and dataset-window scoped. |
| Community labels use a weighted undirected projection and greedy modularity | `backend/app/graph.py` | Community coverage is an operational objective term, not a claim of ground-truth community causality. |
| Candidate prior combines mean outgoing edge probability and log weighted out-degree | `backend/app/pipeline.py` | The top-120 pool limits greedy enumeration; it does not make a claim about the global unrestricted optimum. |

## Guardrails

- Higgs/RIS at training fraction 0.60 is an exact 10/10 paired tie and must
  remain disclosed.
- Digg parent links are an inferred exposure proxy, not observed retransmission
  causality.
- The T0 candidate is validated under its isolated prediction gate, not a
  globally optimized architecture.
- The ongoing `v2-T0b` batch is not covered by this audit.  Its partial files
  are not performance evidence.  Only after the complete batch manifest and
  aggregation exist may its results enter a separate paired-statistics audit.
