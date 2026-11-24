# Key User Identification under Temporal Uncertainty and Cross-Community Constraints

## Abstract

Key user identification often optimizes propagation scale on static networks,
without jointly addressing temporal variation in edges, diffusion uncertainty,
and cross-community coverage constraints. We study Top-K seed selection in
temporal social networks with a robust objective that subtracts a risk penalty
from expected spread and adds a community-coverage reward. A
graph-neural-network prior restricts the candidate set for greedy search. To
avoid treating reconstruction of training edges as evidence of future
predictive utility, we audit probability learning separately from influence
optimization: frozen two-dataset comparisons evaluate the optimization
objective, whereas a temporally forward external test on Higgs evaluates an
independent future-edge-prediction candidate. Across ten paired repetitions in
 three predefined temporal splits of the Digg and Higgs protocols, the proposed
 procedure attains higher robust objectives than Degree and Greedy MC. GNN
 Top-K is retained only as a protected lower-bound audit of the return rule,
 rather than as an independent efficacy comparison. On Higgs, it ties the RIS
 baseline at training fraction 0.60 and attains
higher robust objectives at 0.65 and 0.70. In a completed strict
timestamp-grouped Higgs v2-T0b validation, all 18 mean paired differences are
positive, but only 11 survive the separate 18-contrast Holm correction and no
RIS comparison is significant. Fixed candidate T0 meets the
prespecified ranking, calibration, inverse-score, and seed-stability gates on
the three isolated Higgs outer splits. We do not interpret Digg parent links as
observed causal resharing, and we do not claim universal superiority across
networks or baselines. In the completed preregistered Higgs v3 confirmation,
screened and full-candidate robust greedy were exactly tied across all three
fractions; candidate-pool contrasts were also null, and the weight-sensitivity
family yielded no Holm-supported utility difference. These negative findings
are conditional on the v3 protocol.

**Keywords:** key user identification; influence maximization; graph neural
networks; temporal networks; uncertainty; community coverage

## Translation Boundary

This English title, abstract, and keyword set is a controlled translation of
the current Chinese draft. It follows `manuscript/claim_ledger.md` and
`manuscript/terminology_ledger.md`; its v2-T0b claim is limited to the
Higgs-only, Holm-corrected comparison boundary recorded in Claim C5.
