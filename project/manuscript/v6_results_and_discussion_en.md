# Independent Digg validation at a larger seed budget

## Results

We evaluated the preregistered candidate-reduction protocol on the independent
Digg network with a seed budget of five. The complete formal batch comprised
ten matched blocks (seeds 74--83). Before analysis, a read-only validator
confirmed the fixed Digg input hashes, immutable source snapshot, copied
protocol, all run-file hashes, deterministic disjoint world families, metric
cross-checks and formal eligibility flags. The paired blocks are repeated
protocol realizations, rather than independent network samples.

The primary 120-node GNN-prior pool selected the same ordered seed sequence as
full-candidate robust greedy search in every block. Its primary robust-objective
difference from full search was exactly zero in all ten blocks (mean 0.000,
95% paired t interval [0.000, 0.000], two-sided exact sign-flip p=1.000).
The 60-node GNN-prior pool produced the same result. These exact ties describe
preservation under the stored precision, candidate ranking and simulator; they
do not establish statistical equivalence beyond the protocol.

The smaller 30-node GNN-prior pool did not preserve the full-search result in
any block. Its primary robust objective was lower in all ten paired comparisons
(mean difference -3.499, SD 0.716, 95% paired t interval [-4.011, -2.987],
two-sided exact sign-flip p=0.00195, Holm-adjusted p=0.00586 within the
preregistered secondary family). The stability evaluation gave the same
direction in every block. Thus, the experiment records both a preservation
range (60 and 120 candidates) and a tested failure boundary (30 candidates),
rather than selecting only a successful pool size for reporting.

| Candidate arm | Exact primary preservation (blocks) | Mean primary-objective difference vs full | Mean search-stage time (s) |
| --- | ---: | ---: | ---: |
| Full candidate | 10/10 | 0.000 | 265.08 |
| GNN-prior pool, 30 nodes | 0/10 | -3.499 | 1.15 |
| GNN-prior pool, 60 nodes | 10/10 | 0.000 | 2.37 |
| GNN-prior pool, 120 nodes | 10/10 | 0.000 | 4.71 |
| Weighted-out-degree pool, 120 nodes | 10/10 | 0.000 | 4.59 |

The table reports arm-specific robust-greedy search and final scoring time.
It excludes common graph construction, probability learning, calibration,
prior computation and candidate-ranking operations performed before the arm
timers. The observed ratios must therefore be described as search-stage cost
differences, not end-to-end speedups.

## Interpretation and limits

The 120-node weighted-out-degree pool also exactly preserved the full-search
result in all ten blocks. This is direct evidence against an independent claim
that the GNN prior outperforms this simple same-budget screening rule in the
present protocol. The paper should consequently lead with conditional
candidate reduction and its failure boundary, not with learned-prior
superiority. A same-budget GNN-versus-degree comparison at 60 nodes would be
an exploratory component-attribution study if a later manuscript version
chooses to foreground the learned prior; it is not required for the narrower
candidate-reduction claim.

Digg flow links are inferred exposure proxies and the probability pipeline is
transductive and retrospective. The result does not establish causal
propagation, an online deployment guarantee, a universal screening threshold,
or a cross-hardware efficiency claim. Together with the previously completed
Higgs evidence, it supports a two-network, protocol-conditional account of
candidate reduction, not a claim about all temporal social networks.

## Evidence pointers

- Formal artifact and validator: `audits/candidate-reduction-v6-digg-k5-formal/digg/`
- Strict analysis bundle: `analysis/v6-digg-k5-formal-v3/`
- Preregistered protocol: `protocols/influence_v6_digg_k5_preregistration.md`
