# Key user identification in temporal social networks: evaluating GNN screening, risk penalties, and community rewards

## Abstract

We evaluate whether graph neural network (GNN) candidate screening, diffusion-risk penalties, and seed-community rewards change seed selection and utility in temporal social networks. Our evaluation separates future-edge prediction, baseline comparisons, and component tests under an objective combining mean spread, a standard-deviation penalty, and seed-community coverage. Frozen comparisons cover Digg and Higgs; strict timestamp-grouped studies use Higgs with two selected seeds and ten paired protocol repetitions per temporal split. In the strict comparison, the reference procedure exceeds PageRank, k-shell, and Monte Carlo greedy (Greedy MC) after Holm correction at all three splits, whereas Degree is exceeded at one split and no reverse-influence-sampling (RIS) comparison is significant. In a separately versioned common-world ablation, removing risk or community terms leaves selected sets unchanged, yielding nine exact-zero contrasts. Subsequent v3 tests using independent evaluation worlds find identical utility for screened and full-candidate robust greedy, exact-null candidate-pool contrasts, and no Holm-supported utility difference in the weight-sensitivity family. Recorded search-and-final-scoring times are lower for screening, but exclude training and other preprocessing costs. Separately, a fixed future-edge predictor passes the Higgs external-test gates under the specified sampling protocol. These findings distinguish conditional objective improvements from unsupported component-utility gains and descriptive differences in local computational cost, providing an auditable basis for interpreting temporal-network seed-selection pipelines.

**Keywords:** key user identification; influence maximization; temporal social networks; graph neural networks; risk penalties; seed-community coverage

## Editorial note — not part of the submission abstract

This title and abstract correspond to the SNAM revision of the Chinese source.
Claims are bounded by C2, C5, C6, C7, and C8 in the claim ledger. GNN Top-K
is excluded from independent efficacy claims. The v3 timing observation
is descriptive and does not establish end-to-end speedup. The original
Chinese source is preserved in `snam_revision_01/source_before_revision.md`.
