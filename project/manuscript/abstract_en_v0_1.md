# Key user identification in temporal social networks: an empirical evaluation of propagation probability modeling and candidate reduction

## Abstract

We evaluate propagation probability modeling and candidate reduction for key user identification in temporal social networks, separating future-edge prediction, seed-selection utility, and search cost. The reference procedure uses learned edge probabilities for independent-cascade simulations and optimizes mean spread with a standard-deviation penalty and a seed-community reward. Frozen comparisons cover Digg and Higgs; timestamp-grouped Higgs studies use two seeds and ten paired protocol repetitions per split. Several baseline contrasts survive Holm correction, but none against reverse influence sampling does. Common-world objective ablations and subsequent v3 screening and candidate-pool tests yield null results, with no Holm-supported utility difference in the weight-sensitivity family. Across thirty v3 runs, screening to 120 candidates preserves full-search selections and evaluation scores with lower recorded search-and-final-scoring times, excluding training and preprocessing. In a separately versioned, single post-hoc diagnostic, graph neural network (GNN) screening and weighted out-degree screening also produce identical selections and evaluation outcomes. This observation does not establish population equivalence or a distinctive benefit of learned screening. A fixed predictor passes the recorded Higgs external-test gates, but calibration-negative eligibility uses full-period observed edges, limiting interpretation as strictly online prediction. The evidence establishes protocol-specific selection and stage-cost observations; independent seed-selection gains from learned probabilities and end-to-end acceleration remain untested.

**Keywords:** key user identification; influence maximization; temporal social networks; propagation probability modeling; candidate screening; computational cost

## Editorial note — not part of the submission abstract

This title and abstract correspond to the second SNAM revision (2026-09-15).
Claims are bounded by C2 and C5–C12 in the claim ledger. The v4 diagnostic
is not confirmatory evidence. The term probability modeling describes the
pipeline role, not verified causal transmission probabilities. GNN Top-K is
excluded from independent efficacy claims. The preceding source versions are
preserved in `snam_revision_02_2026-09-15/before/`.
