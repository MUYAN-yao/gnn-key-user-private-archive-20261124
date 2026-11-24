# Candidate Reduction in Temporal Key-User Identification: A Protocol-Conditional Audit of Preservation, Cost, and Failure Boundaries

## Abstract

Candidate reduction can make diffusion-based key-user identification tractable,
but a smaller search space need not retain the seed set or utility of a full
search. We evaluate a temporal-network pipeline that learns edge scores with a
fixed GATv2 configuration, derives a node prior, and applies robust greedy
search under a mean-spread objective with a standard-deviation penalty and a
seed-community reward. The study separates future-edge validation,
seed-selection comparisons, candidate-reduction tests, and recorded
search-stage cost. Frozen Digg and Higgs comparisons and separately versioned,
timestamp-grouped Higgs studies provide the initial evidence. A new
preregistered Digg validation uses a larger five-node budget, ten matched
formal blocks, disjoint selection and evaluation worlds, and full-candidate,
30/60/120-node GNN-prior, and 120-node weighted-out-degree arms. The 60- and
120-node GNN pools exactly reproduced full search in all ten blocks, whereas
the 30-node pool lost robust objective in every block (mean paired difference
-3.499; 95% paired interval [-4.011, -2.987]; Holm-adjusted p=0.00586). The
120-node weighted-out-degree pool also reproduced full search. Thus, the
evidence supports a conditional preservation range, a tested failure boundary,
and search-stage cost differences; it does not support learned-screening
superiority, causal diffusion validity, online deployment, or end-to-end
acceleration. The contribution is an auditable empirical account of when a
candidate-reduction protocol retained full search and when it did not.

**Keywords:** key-user identification; influence maximization; temporal social
networks; candidate reduction; robust greedy search; graph neural networks

## 1 Introduction

Key-user identification selects a small seed set for subsequent diffusion in a
social network. Classical influence maximization commonly targets expected
spread [1,8]. In temporal networks, the decision is additionally constrained
by the evolving graph and by the distinction between information used for
selection and information observed later [19,25,26]. Consequently, a useful
empirical study must separate at least three questions: whether a score has
predictive support under a defined temporal protocol, whether a selection rule
improves a common seed-set objective, and whether any apparent computational
gain includes the full pipeline cost.

Learning-based influence-maximization pipelines combine representation learning,
candidate screening and combinatorial search [6,21,31]. An observed difference
from degree ranking or a spread-oriented baseline therefore does not identify
which component produced it. Risk-aware and community-oriented formulations
also encode decision preferences beyond expected spread [11,12,17,20]. Adding
such terms to an objective specifies a rule; it does not by itself show that
the terms changed the selected seeds or improved a common reporting outcome.

This paper studies candidate reduction as a bounded decision problem. A fixed
GATv2-based score is used to rank a candidate pool, after which robust greedy
search optimizes a shared simulated objective. The principal question is not
whether the learned prior is universally better than a structural ranking. It
is whether, under a specified temporal graph, simulator, objective, seed budget
and candidate-pool size, a reduced pool preserves the full-candidate result,
and where that preservation fails.

Our contribution has three parts.

1. We provide an artifact-backed separation of future-edge prediction,
   seed-selection comparisons, candidate-reduction tests and stage-cost
   observations. Passing a future-edge gate is not treated as proof of an
   independent learned-probability benefit for seed selection.
2. We report conditional candidate-reduction evidence on Higgs and an
   independently versioned Digg k=5 validation. The Digg study identifies both
   preserved pools (60 and 120) and a failed pool (30), using fixed matched
   repetitions and disjoint evaluation worlds.
3. We preserve negative and boundary findings. Same-budget weighted out-degree
   screening also preserves full search at 120 candidates, so we explicitly
   exclude a learned-screening-superiority claim. Search-stage timings are
   reported with their shared-preprocessing exclusion.

The study does not introduce a new graph architecture or an optimality
guarantee. Its conclusions are conditional on two networks, their processed
data semantics, fixed simulators, candidate pools and recorded temporal
protocols.

## 2 Related work

Influence maximization has developed from expected-spread formulations and
reverse-influence-sampling approximations [1,3,8] to temporal, dynamic and
uncertainty-aware settings [11--14,19,20,25,26]. Community-aware methods use
structural or diversity information in seed selection [10,16,17,27]. These
approaches motivate an objective that includes risk and seed-community terms,
but they do not establish the same uncertainty source, information boundary or
objective as ours.

GNN and graph-embedding methods have also been used to estimate node influence
or guide seed selection [6,21,22,28,31]. Their learned Top-K, subgraph
inference, or feedback-driven adaptive-seeding setups differ from the fixed-k,
non-adaptive candidate-reduction protocol here. Temporal representation models
such as GATv2, TGAT and TGN provide methodological context [2,23,24], but none
is evidence that the present score is a causal diffusion probability. A detailed
scope comparison is retained in `related_work_matrix.md`; it makes no
cross-paper numerical comparison.

## 3 Problem formulation and method

At decision time (t), let (G_t=(V,E_t)) be a time-weighted directed graph
constructed from historical interactions. The task selects a seed set (S) of
size (k) to maximize

\[
J(S)=\mathbb{E}[\sigma(S)]-\lambda\operatorname{SD}[\sigma(S)]+\eta C(S),
\]

where (sigma(S)) is independent-cascade spread at the fixed diffusion
horizon and (C(S)) counts distinct communities represented among the seeds.
The community term is a soft seed-diversity reward. It neither measures
communities reached by diffusion nor supplies a group-fairness guarantee.

Historical interactions form a weighted snapshot. Node features include
weighted in- and out-degree, historical cascade activity and PageRank;
communities are derived from a weighted undirected projection. A one-layer
GATv2 encoder with width 32, a concatenation MLP decoder, ten training epochs
and learning rate 0.01 produces edge scores. Isotonic calibration and the
specified bounds are applied before constructing the node prior. The prior is
the normalized product of a node's mean outgoing score and the logarithm of
its weighted out-degree.

Robust greedy search repeatedly evaluates candidate additions under common
selection worlds and uses a stable identifier tie-break. Candidate reduction
limits this enumeration to the highest-ranked prior nodes. Full-candidate
robust greedy search is the matched component comparator: it uses the same
probability graph, objective and worlds, but enumerates the entire decision
node set. Therefore it tests the candidate-membership step, not removal of
probability learning.

The temporal edge-prediction audit is also bounded. Its calibration-negative
eligibility rule uses the full-period observed-edge set, and the node universe
is transductive. Window separation therefore does not make the whole pipeline
a strictly online method. The learned scores are used as simulator parameters
and as a ranking prior, but neither use implies that they are verified causal
transmission probabilities.

[Insert Fig. 1 near here: temporal information boundary.]

[Insert Fig. 2 near here: protocol and matched candidate comparison.]

## 4 Experimental protocol

### 4.1 Data and evidence versions

Higgs 50k is derived from time-stamped Twitter activity observations [4]. Its
processed events are not treated as complete cascade-parent truth. Digg 20k is
derived from Network Data Repository relation and vote data [5]; its flow links
are inferred exposure proxies rather than observed reshare parents. A third
dataset was not admitted because no local candidate passed the stated
provenance, licensing, temporal and cascade-parent requirements. The paper is
therefore a two-network study.

Frozen Digg/Higgs comparisons, timestamp-grouped Higgs v2-T0b comparisons,
common-world v2-T0d ablations, and Higgs v3 candidate-reduction/sensitivity
tests are separate evidence versions with distinct manifests and statistical
families. The v4 diagnostic is excluded from inference because its exact
execution-source bytes could not be recovered. The v5 Higgs preflight is a
time-only feasibility boundary: the validated full-candidate arm exceeded its
fixed resource gate, so no v5 formal comparison is reported.

### 4.2 Matching and statistics

For the existing k=2 studies, each dataset/split uses ten paired protocol
repetitions. Within a paired block, compared methods share the relevant graph,
probability map and common random conditions. We report paired means, sample
standard deviations, 95% paired t intervals, win/tie/loss counts, exact
two-sided sign-flip tests and Holm-adjusted families defined by the respective
protocol. Repetitions are stochastic protocol realizations, not independent
social networks; overlapping temporal prefixes are not independent datasets.

The preregistered v6 Digg validation uses (k=5), seed 73 only for an
excluded cost preflight, and formal seeds 74--83. It compares full search,
GNN-prior pools of 30, 60 and 120 nodes, and a 120-node weighted-out-degree
pool. Twenty deterministic selection worlds are disjoint from primary and
stability evaluation sets of 100 worlds each. Before analysis, the immutable
source snapshot, input hashes, protocol copy, run hashes, configuration,
worlds, metric rows and formal-eligibility flags were verified.

## 5 Results

### 5.1 Earlier comparisons delimit, rather than prove, component effects

In frozen comparisons, the reference procedure exceeded degree and Greedy MC
under the recorded common objective across the listed Digg and Higgs splits;
the Higgs 0.60 RIS comparison was an exact ten-of-ten tie. In the stricter
timestamp-grouped Higgs v2-T0b study, only a subset of contrasts against
PageRank, k-shell, Greedy MC and degree survived the preregistered Holm family;
all RIS contrasts remained nonsignificant. These results support selected
protocol-specific baseline comparisons. They do not show universal superiority
or superiority over RIS.

[Insert Fig. 3 near here: frozen-protocol paired comparison.]

[Insert Fig. 4 near here: strict T0b comparison.]

The fixed T0 candidate passed its recorded external Higgs future-edge gates
(mean AUCs 0.8228, 0.8333 and 0.8417 across the three reported fractions).
This is a ranking result under balanced sampled pairs and the documented
transductive negative-eligibility rule. It is not a validation of causal
diffusion probabilities or an independent seed-selection gain.

Common-world objective ablations on Higgs selected the same seeds and had zero
reporting-objective differences in every planned contrast. The v3 full versus
screened candidate comparison likewise produced exact ties in its formal
Higgs blocks, and the weight-sensitivity family had no Holm-supported utility
difference. These null findings prevent us from attributing observed baseline
differences to an individual objective term or to the GNN screening step.

[Insert Fig. 5 near here: Higgs full-versus-screened candidate comparison.]

### 5.2 Independent Digg validation identifies preservation and failure ranges

The v6 formal Digg batch passed all artifact and provenance checks. The
120-node GNN-prior pool matched full-candidate robust greedy search in ordered
Top-K and primary objective in all ten formal blocks. Its paired primary
objective difference was exactly zero (mean 0.000, 95% paired interval
[0.000, 0.000], exact p=1.000). The 60-node GNN-prior pool produced the same
ten exact matches. Exact ties are reported as observed equality at the stored
precision; they are not transformed into equivalence claims.

The 30-node GNN-prior pool failed in every block. Its primary robust objective
was lower by a mean of 3.499 (SD 0.716; 95% paired interval [-4.011, -2.987];
exact p=0.00195; Holm-adjusted p=0.00586 in the preregistered secondary
family). Its stability outcome had the same negative direction in all ten
blocks. Reporting this arm establishes a tested boundary instead of presenting
only an effective candidate-pool size.

[Insert Fig. 6 near here: Digg candidate-pool failure boundary.]

| Arm | Exact primary preservation | Mean primary difference versus full | Mean search-stage time (s) |
| --- | ---: | ---: | ---: |
| Full candidate | 10/10 | 0.000 | 265.08 |
| GNN pool 30 | 0/10 | -3.499 | 1.15 |
| GNN pool 60 | 10/10 | 0.000 | 2.37 |
| GNN pool 120 | 10/10 | 0.000 | 4.71 |
| Weighted out-degree pool 120 | 10/10 | 0.000 | 4.59 |

The 120-node weighted-out-degree pool also matched full search in all blocks.
Accordingly, the v6 data do not support an independent claim that the GNN
prior is better than this structural same-budget screen. The result instead
supports a conditional candidate-reduction statement: in this Digg protocol,
the tested 60- and 120-node pools preserved the observed full-search outcome,
whereas the 30-node pool did not.

### 5.3 Cost interpretation

The v6 full-candidate arm averaged 265.08 seconds of search-stage time, versus
2.37 seconds for the GNN-60 arm and 4.71 seconds for GNN-120. These timers
exclude graph construction, edge-score learning, calibration, prior generation
and candidate ranking performed before arm timing. They are thus local
search-and-final-scoring measurements, not end-to-end speedups. The v5 Higgs
preflight independently records the complementary failure limit: its
full-candidate arm exceeded the fixed resource gate, so that larger-budget
Higgs batch was not eligible for inference.

## 6 Discussion

The combined evidence makes candidate reduction more defensible than a
learned-model efficacy headline. Higgs v3 shows that screening can preserve a
full-search solution under an independently evaluated same-objective protocol.
The preregistered Digg k=5 study extends that observation to another network
and a larger budget while adding a concrete failed pool. The observed pattern
is useful for decision support because it reports a boundary as well as a
preserved regime.

The same evidence limits the claim. The identical result of the 120-node
weighted-out-degree pool means that candidate preservation cannot be credited
to learned ranking alone. Similarly, shared learned probabilities mean that
full-versus-screened comparisons are not ablations of the entire probability
pipeline. A future component-attribution study would need a separately fixed,
same-budget GNN-versus-structural comparison and a common, prespecified
evaluation mechanism. We do not add such an adaptive experiment merely to
seek a positive result.

The study is also limited by data semantics. Digg uses exposure proxies and
Higgs does not provide complete causal cascades. The probability protocol is
retrospective and transductive because of its negative-eligibility rule. The
simulation results therefore do not establish intervention benefit, online
operation or general causal diffusion behavior. Finally, stage timings omit
shared preprocessing, and no cross-hardware or end-to-end efficiency claim is
made.

## 7 Conclusion

This work provides an auditable empirical study of candidate reduction for
temporal key-user identification. Under the recorded two-network protocols,
candidate pools can reproduce full-candidate robust greedy search while
substantially reducing the recorded search stage. The new Digg k=5 validation
shows preservation at 60 and 120 candidates and consistent loss at 30
candidates. These observations are conditional on the simulator, temporal
data treatment, candidate ranking and fixed objective. They do not establish
learned-prior superiority, equivalence beyond the tested blocks, causal
diffusion validity or end-to-end acceleration. This explicit boundary is the
paper's central result.

## Data and code availability

The project records input, protocol, source-snapshot and run-artifact hashes
for accepted studies. Raw Higgs and Digg files are not redistributed; they
must be obtained under their original providers' terms. Before submission, the
authors must select a lawful archive and publish an allowlisted source and
analysis snapshot, together with the environment record and artifact manifests.

## Declarations to be completed by the authors

Author order, institutional affiliations, corresponding author, funding,
acknowledgements, author contributions, conflicts of interest, ethics status
and archival URL are intentionally absent from this draft. They require
author-confirmed information before submission.

## AI assistance statement to be completed by the authors

The authors must confirm whether any generative-AI assistance used during
manuscript preparation requires disclosure under the journal's current policy,
describe the verified use accurately, and retain human responsibility for all
scientific content, analysis, and the final submitted text. This placeholder
must be replaced by an author-approved statement or removed only when the
authors confirm that no disclosure is required.

## References

Use the audited 34-entry bibliography in `references.bib`. Citation numbering
in this draft follows the existing source manuscript and must be regenerated
in the final Applied Intelligence template.

## Figure and supplement inventory

1. Temporal-window and information-boundary schematic from the accepted
   source figure set.
2. Candidate-reduction decision diagram, showing shared probability graph and
   separate selection/evaluation worlds.
3. Timestamp-grouped Higgs paired-comparison figure, including the RIS nulls.
4. v3 Higgs full-versus-screened timing and identity table.
5. v6 Digg paired-delta SVG from `analysis/v6-digg-k5-formal-v3/figures/`.
6. Supplement: protocols, source snapshot manifests, validator reports,
   seed-level metrics, statistical definitions and the v5 feasibility record.
