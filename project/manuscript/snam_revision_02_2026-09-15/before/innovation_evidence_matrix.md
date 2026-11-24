# Innovation Evidence Matrix

## Purpose and Claim Rule

This is an internal evidence-boundary record for the manuscript. It identifies
the differentiating contribution that can be stated from the current audited
record, the evidence supporting that statement, and the wording that must not
be used. It does not establish that any component is the first such method in
the literature.

| Contribution element | Evidence in this study | Literature boundary | Allowed manuscript wording | Forbidden wording | Current state |
| --- | --- | --- | --- | --- | --- |
| Temporally isolated candidate validation separate from seed optimization | T0 outer-test gate: `analysis/edge-prediction-v2-t0-gate-v2/`; complete strict study: `analysis/v2-t0b-strict-paired-v1/` | The matrix records adjacent time-restricted and dynamic-network work, but does not assert that no prior work separates these stages. | "We separate future-edge ranking validation from downstream seed optimization under a time-forward protocol." | "The first temporal GNN influence method" or "the first leakage-free method." | Candidate validation and strict Higgs influence study complete; configuration-specific. |
| Robust, cross-community seed objective | Frozen-study design and paired analysis in `analysis/frozen-main-comparison-v1/`; method boundary C1 in `manuscript/claim_ledger.md` | Risk-aware, robust, and community-aware influence studies exist; their objectives are not claimed to be identical to this study's formulation. | "The evaluated objective jointly rewards expected spread and cross-community coverage while penalizing simulated dispersion." | "A novel/proven optimal robustness objective" or equivalence to any cited robust objective. | Frozen protocol evidence complete and scope-limited. |
| GATv2-derived candidate prior used inside a greedy selection procedure | Encoder audit `analysis/edge-prediction-v2-t0-gate-v2/`; algorithm record `manuscript/algorithm_appendix.md` | GNN/embedding approaches to influence maximization are already represented in `manuscript/related_work_matrix.md`. | "The implementation uses an independently audited GATv2-derived candidate prior within the reported greedy procedure and retains GNN Top-K as a protected lower-bound audit." | "The first GNN-guided influence maximizer", "globally optimal GNN-guided selection", or an independent efficacy claim against the protected GNN Top-K lower bound. | Fixed candidate only; no architecture-wide optimality claim. |
| Repeated paired stochastic evaluation with common random diffusion streams | `analysis/frozen-main-comparison-v1/`; `analysis/v2-t0b-strict-paired-v1/`; reproducibility record C4 | The comparison matrix does not establish this evaluation design as unique in the literature. | "Within each evaluated protocol run, methods were compared on common random diffusion streams and analyzed as paired outcomes." | "Unbiased proof of superiority" or an independence claim beyond the paired protocol runs. | Complete for frozen v1 and v2-T0b. |
| Strict timestamp-grouped v2-T0b execution protocol | Complete study and hash-checked paired bundle in `analysis/v2-t0b-strict-paired-v1/` | Time-restricted and dynamic-network studies are adjacent, not evidence that this split is unprecedented. | "The v2-T0b study enforces a strict calibration-to-test timestamp boundary and evaluates the frozen configuration in 30 preregistered runs." | Any claim that the protocol is first of its kind, universal superiority, or significant advantage in a contrast whose Holm result is non-significant. | Complete; 11 of 18 Holm-adjusted contrasts are significant, and all RIS contrasts remain non-significant. |

## Permitted Contribution Paragraph Scope

The manuscript may present the work as a combination of a validated temporal
candidate prior, a risk-and-coverage seed objective, and paired stochastic
evaluation under the documented protocols. The empirical wording must retain
the frozen Higgs/RIS train-fraction-0.60 tie, the strict v2-T0b non-significant
RIS contrasts, and the Digg exposure-proxy limitation stated in
`manuscript/claim_ledger.md`.

## Gates Before Strengthening Any Claim

1. The v2-T0b completion, hash, summary, and strict-paired-analysis gates are
   complete. Preserve the 18-contrast Holm family and the non-significant RIS
   results when integrating the evidence.
2. Expand and full-text audit the temporal, uncertainty-aware, GNN, and
   community-aware literature before making any stronger feature-level
   differentiation claim.
3. Update this matrix, the claim ledger, and manuscript wording together;
   never convert an unverified absence in related work into a novelty claim.
