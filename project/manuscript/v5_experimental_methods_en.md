# Candidate reduction at a larger seed budget

Status: English protocol and feasibility record, 18 September 2026. The Higgs
cost preflight passed integrity validation but failed the fixed resource gate.
No v5 formal outcome is available or asserted here.

## Draft

### Question and data

The additional experiment tests whether candidate reduction preserves the
selection and simulated utility of full-candidate robust greedy search when
the seed budget increases from two to five. It also examines the consequences
of reducing the candidate pool and changing evaluation worlds. This design
addresses preservation under a fixed simulation protocol, rather than the
independent efficacy of learned probabilities.

The preregistered inputs are the existing Higgs and Digg processed datasets.
Higgs contains 33,529 nodes, 50,000 edges and 50,000 cascade-event records;
Digg contains 7,321 nodes, 2,111 edges and 20,000 cascade-event records. These
are input-file counts, not the sizes of every temporally restricted decision
graph. The nominal training fraction is fixed at 0.65, using the existing
timestamp-grouped pipeline. Input files are verified against fixed SHA-256
digests before execution.

Higgs comprises activity-derived interactions without complete causal cascade
truth. Digg flow links are inferred exposure proxies rather than observed
reshare-parent links. The networks therefore provide two settings for
conditional simulated selection. Calibration negative eligibility also uses
the fixed dataset-wide observed-edge set. The probability pipeline is
transductive and retrospective; temporal window separation does not establish
a strictly online information boundary.

### Matched comparisons

The formal design specifies ten matched protocol repetitions per network,
using seeds 63–72. One calibrated probability graph is fitted per network–seed
block and shared by all arms. The fixed T0 model uses one GATv2 layer of width
32, ten epochs, a learning rate of 0.01, a concatenation MLP decoder and
isotonic calibration. Probabilities are bounded to [0.02, 0.98]. These
repetitions are not independent samples of social networks.

The five arms comprise full-candidate robust greedy search; search over the
top 30, 60 or 120 nodes ranked by the graph-neural-network (GNN) prior; and
search over 120 nodes ranked by weighted out-degree. All arms use five seeds,
a diffusion horizon of four, a standard-deviation penalty of 0.35 and a
seed-community reward of 0.25. Weighted out-degree supplies a comparator with
the same candidate budget, but still shares the learned probability graph.

### Selection and evaluation

Selection uses 20 deterministic diffusion worlds. Primary evaluation uses a
disjoint set of 100 worlds, followed by another disjoint 100-world set for
stability analysis. Arms within a block share the corresponding worlds.
Canonical edge–time randomization avoids dependence on container traversal.
Candidate scores are rounded to six decimal places before comparison, and
ties use ascending string identifiers.

The reporting plan includes ordered seed-sequence identity, Jaccard overlap,
robust objective, mean spread, spread standard deviation and seed-community
coverage. Each block records the smallest tested GNN pool preserving both
the ordered selection and primary objective. Failure of all tested pools is
retained. Preservation refers to stored precision and specified simulation
conditions; it is not a mathematical or statistical equivalence claim.

### Statistical analysis

The two primary contrasts compare the 120-node GNN arm with full search,
once per network, using ten paired differences in primary robust objective.
The summary comprises the mean difference, sample standard deviation, 95%
paired t interval, exact two-sided sign-flip p-value, Holm adjustment across
these two contrasts, win/tie/loss counts and Cohen's dz. The sign-flip
distribution enumerates all 1,024 assignments; inferential interpretation
requires sign exchangeability under the null. Cohen's dz is undefined for
zero-variance differences.

The 30-node GNN, 60-node GNN and weighted out-degree contrasts against full
search form a separate six-contrast secondary Holm family across both
networks. The second evaluation set is a sensitivity check, not another
primary test. Changes in direction or loss of exact ties are reported without
pooling the evaluation sets. Earlier experimental versions are not pooled
with v5.

### Timing and reproducibility

Execution records shared processing and model stages, arm-specific search and
evaluation, and total block time. Every standalone arm still requires the
shared probability graph. The current implementation times pool copying and
canonical sorting inside each arm, but prepares ranking lists and pool slices
before arm timers start. Those operations contribute to total block elapsed
time without a separate ranking timer. Arm time consequently does not measure
the complete screening pipeline, and a search-stage ratio cannot be reported
as an end-to-end speedup.

Seed 62 was reserved for a non-inferential cost preflight. Formal execution
required both preflights to pass integrity validation, each full-candidate
arm to finish within 14,400 seconds, and ten times the sum of both full-arm
times to be no greater than 72 hours. The Higgs preflight passed schema, input
hash and source-snapshot validation, but its full-candidate arm required
37,498.606 seconds. Its ten-block projection was 104.16 hours, exceeding both
fixed limits. The protocol therefore terminated before the Digg preflight and
before every formal v5 block. This time-only feasibility result does not
authorize inspection or reporting of the preflight's selection or objective
outcomes. The projection covers full-arm time, not total study wall time.

Experiment code executes from the verified r2 source snapshot. Artifacts
record input digests, snapshot provenance, world identifiers, candidate
membership and run-file hashes. An external serial controller enforces the
joint resource gate and invokes paired analysis only after both complete
formal batches validate. The v4 formal batch remains excluded from inference
because its exact execution-source bytes could not be recovered; its raw
results are preserved as audit records.

## Section outline and claim–evidence map

| Section | Paragraph job | Evidence | Status |
| --- | --- | --- | --- |
| Question/data | Scope and limitations | Frozen v5 protocol | Design supported; outcomes pending |
| Comparisons | Fixed arms and settings | Snapshot runner | Supported implementation description |
| Evaluation | Worlds and preservation endpoints | Protocol and runner | Prespecified |
| Statistics | Paired families and uncertainty | Snapshot analysis | Prespecified; no estimates available |
| Timing/provenance | Measurement limits and admission | Runner and v4 source audit | Supported implementation description |

## Assumptions or missing inputs

- Insert formal counts, estimates, intervals, p-values, stability findings and
  timing summaries only after both formal batches pass validation.
- Add dataset/model citations from the existing audited bibliography during
  integration. This methods draft introduces no new literature claims.
- Do not label pool-copy time as full ranking cost. Retain the timing caveat.
- Final journal formatting and author declarations remain pending.

## 中文说明

沿用术语 candidate reduction（候选缩减）、robust objective（鲁棒目标）、
seed-community coverage（种子社区覆盖）及 exposure proxy（暴露代理）。结构先
说明问题和数据，再交代比较、评估、统计及成本，便于读者核查证据。当前只写方法，
不提前填写结果或改写旧稿结论；后续可按段落局部修改。
