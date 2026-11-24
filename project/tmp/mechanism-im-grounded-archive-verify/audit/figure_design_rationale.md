# Why this figure is domain grounded

This figure is not a generic machine-learning workflow. It follows the visual grammar of direct influence-maximization work: graph nodes and directed arcs, a seed-eligibility decision, and a diffusion/reach comparison. The design review used the mechanism figures of the following directly related conference papers as *visual references only*:

- Manchanda et al., **GCOMB: Learning Budget-constrained Combinatorial Algorithms over Billion-sized Graphs**, NeurIPS 2020, Figure 1. Official paper: <https://proceedings.nips.cc/paper_files/paper/2020/file/e7532dbeff7ef901f2e70daacb3f452d-Paper.pdf>.
- Ling et al., **Deep Graph Representation Learning and Optimization for Influence Maximization**, ICML 2023, Figure 1. Official paper: <https://proceedings.mlr.press/v202/ling23b/ling23b.pdf>.

Neither work is cited as evidence for this paper's empirical claims. The visual references informed only the choice to foreground graph direction, seed eligibility and diffusion rather than a generic data-processing pipeline.

## Evidence trace for the figure

| Drawn element | Frozen source | Permitted interpretation |
|---|---|---|
| voter-to-votee arc and outgoing simulated propagation | `manuscript/manuscript.tex`, data section | The recorded orientation and the simulation convention differ from PageRank's incoming-link emphasis. |
| mean degrees of PageRank-4k and degree-4k candidates | `review-v3-budget-precision/analysis/direction_diagnostics.csv` | A structural contrast under this orientation. |
| 0/5 PageRank-4k full-reference-seed coverage | `direction_diagnostics.csv` | Candidate-coverage fact for the five recorded paths at W=1280. |
| 55.73602 and 15.04268 incremental spread; -40.69334 delta; 73.0107% loss | `review-v3-budget-precision/analysis/summary_by_method.csv` | Independent-evaluation aggregate for the specified frozen condition. |

The visual motifs are illustrative. They do not represent a sampled wiki-Vote subgraph, observed real adoption, a reverse-orientation experiment or a causal proof that direction alone caused the loss.
