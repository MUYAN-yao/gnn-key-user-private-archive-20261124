# Strict external-validation analysis

## V3 update: budget--precision sensitivity

The frozen main matrix below remains the primary default-tolerance evidence. The
new post-hoc strict-ranking budget control is reported separately in
`analysis/precision_budget/analysis-report.md` and uses 30 additional conditions
at W80/W320 plus the prior strict W1280 layer. It shows that ca-GrQc's default
gain-to-loss direction reversal is not precision-robust: strict 4k losses are
-11.25%, -2.96% and -0.54% at W80/W320/W1280. CollegeMsg is unchanged by
tolerance; wiki-Vote retains about 74% strict 4k loss. The final manuscript uses
this control to distinguish budget-dependent magnitude/seed changes from a
precision-dependent directional interpretation.

This report is regenerated from all 54 frozen JSON/NPZ pairs. There are 468
executed arms, plus 54 derived within-path random-pool means. No failed or adverse
condition is excluded. Audit acceptance is separately recorded in
`../audit/full_validation.json`; generating this report alone does not certify it.

## Primary results (W=1280; frozen default PageRank tolerance)

Important qualification: the separately frozen post-hoc precision control changes
ca-GrQc PageRank4k from -.25082 to +.02608 when tolerance is tightened. CollegeMsg
is unchanged and wiki-Vote's large loss persists. The original ca-GrQc loss is not
precision-robust; default and tightened results are not interchangeable. Full
control results appear below and in supplement-pr-precision/summary.csv.

| dataset | method | delta_mean | delta_path_sd | loss_percent_mean | same_order_mean | verification_saving_percent_mean |
| --- | --- | --- | --- | --- | --- | --- |
| ca_grqc | degree_4k | 0.0 | 0.0 | 0.0 | 1.0 | 92.76927 |
| ca_grqc | degree_5pct | 0.0 | 0.0 | 0.0 | 1.0 | 88.13306 |
| ca_grqc | full | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| ca_grqc | pagerank_4k | -0.25082 | 0.07636 | 5.07038 | 0.0 | 92.70243 |
| ca_grqc | pagerank_5pct | 0.0 | 0.0 | 0.0 | 1.0 | 88.13904 |
| ca_grqc | random_mean_4k | -3.94366 | 0.22137 | 79.9044 | 0.0 | 93.0306 |
| college_msg | degree_4k | 0.0 | 0.0 | 0.0 | 1.0 | 86.588 |
| college_msg | degree_5pct | 0.0 | 0.0 | 0.0 | 1.0 | 82.9055 |
| college_msg | full | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| college_msg | history_weighted_4k | -0.25224 | 0.0236 | 2.5038 | 0.0 | 86.60218 |
| college_msg | history_weighted_5pct | 0.0 | 0.0 | 0.0 | 1.0 | 82.99008 |
| college_msg | pagerank_4k | -0.9078 | 0.04058 | 9.01183 | 0.0 | 86.43684 |
| college_msg | pagerank_5pct | -0.43094 | 0.04325 | 4.27706 | 0.0 | 82.83312 |
| college_msg | random_mean_4k | -8.22745 | 0.26602 | 81.68829 | 0.0 | 87.65356 |
| wiki_vote | degree_4k | 0.0 | 0.0 | 0.0 | 1.0 | 96.26362 |
| wiki_vote | degree_5pct | 0.0 | 0.0 | 0.0 | 1.0 | 91.04159 |
| wiki_vote | full | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| wiki_vote | pagerank_4k | -40.69334 | 0.13835 | 73.0107 | 0.0 | 96.42355 |
| wiki_vote | pagerank_5pct | -13.53012 | 0.09582 | 24.27522 | 0.0 | 91.98097 |
| wiki_vote | random_mean_4k | -50.90179 | 1.8917 | 91.32667 | 0.0 | 96.57434 |

Degree-4k reproduces all 15 ordered references across the three fixed graphs.
PageRank-4k does not reproduce any of these trajectories. These are finite-reference
statements; the references are not optimal expected-spread sets. Selection budgets
stop at 1280. Standard incoming PageRank and outgoing IC are different objectives.
On wiki-Vote, the PageRank top 20 have mean out-degree 56.2 versus 489.25 for degree;
they cover 0/5 full seeds on each path. At 5% coverage PageRank still loses 24.28%
of incremental spread. This is evidence of sensitivity to ranking, coverage and
topology, not a causal isolation of direction or a universal failure of PageRank.

## Full-reference budget transitions

| dataset | low | high | paths | changed | mean_delta | delta_sd | min_delta | max_delta | mean_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ca_grqc | 80 | 320 | 5 | 5 | 0.39616 | 0.15803 | 0.1819 | 0.6139 | 0.20238 |
| ca_grqc | 80 | 1280 | 5 | 5 | 0.52336 | 0.2083 | 0.3664 | 0.8532 | 0.20794 |
| ca_grqc | 320 | 1280 | 5 | 5 | 0.1272 | 0.12185 | -0.0266 | 0.2411 | 0.52381 |
| college_msg | 80 | 320 | 5 | 2 | 0.09994 | 0.13915 | 0.0 | 0.2855 | 0.86667 |
| college_msg | 80 | 1280 | 5 | 2 | 0.1533 | 0.221 | 0.0 | 0.481 | 0.81905 |
| college_msg | 320 | 1280 | 5 | 1 | 0.05336 | 0.11932 | 0.0 | 0.2668 | 0.93333 |
| wiki_vote | 80 | 320 | 5 | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| wiki_vote | 80 | 1280 | 5 | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| wiki_vote | 320 | 1280 | 5 | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |

At 320→1280, six of fifteen final sets change. Four changed-set contrasts have
positive pointwise normal 95% conditional MC intervals; two ca-GrQc contrasts
cross zero. These are unadjusted exploratory diagnostics, not six hypothesis tests
or an application-specific materiality criterion. Nine same-set transitions have
identical per-world values; some ordered traces still change. The three graphs
are reported separately and are not pooled for population inference.

## Inference and cost limits

| dataset | method | paths | nonzero_paths | zero_paths | positive_paths | negative_paths | mean_delta | mean_loss_percent | p_raw | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| college_msg | degree_4k | 5 | 0 | 5 | 0 | 0 | 0.0 | 0.0 | 1.0 | 1.0 |
| college_msg | pagerank_4k | 5 | 5 | 0 | 0 | 5 | -0.9078 | 9.011829 | 0.0625 | 0.1875 |
| college_msg | random_mean_4k | 5 | 5 | 0 | 0 | 5 | -8.227447 | 81.688286 | 0.0625 | 0.1875 |
| ca_grqc | degree_4k | 5 | 0 | 5 | 0 | 0 | 0.0 | 0.0 | 1.0 | 1.0 |
| ca_grqc | pagerank_4k | 5 | 5 | 0 | 0 | 5 | -0.25082 | 5.070377 | 0.0625 | 0.1875 |
| ca_grqc | random_mean_4k | 5 | 5 | 0 | 0 | 5 | -3.94366 | 79.904401 | 0.0625 | 0.1875 |
| wiki_vote | degree_4k | 5 | 0 | 5 | 0 | 0 | 0.0 | 0.0 | 1.0 | 1.0 |
| wiki_vote | pagerank_4k | 5 | 5 | 0 | 0 | 5 | -40.69334 | 73.010697 | 0.0625 | 0.1875 |
| wiki_vote | random_mean_4k | 5 | 5 | 0 | 0 | 5 | -50.901793 | 91.326672 | 0.0625 | 0.1875 |

No primary sign-test comparison passes Holm 0.05. With five nonzero paths even all
five negative signs yield p=.0625 before correction. That low-powered test does
not erase a large measured effect or prove equivalence. Conditional MC uncertainty
and between-path variability answer different questions; path t intervals are
post-hoc descriptive intervals, not cross-network confidence statements.

Selection-only savings require prepared graph and worlds. Hybrid deployment adds
supplementary method-specific setup and frozen selection-world preparation;
verification further adds independent-world preparation and evaluation. The
setup contribution is newly measured; no direct cold-start or end-to-end trial is
claimed. All repeated frozen timings are in timing_repeats.csv/timing_summary.csv.
Tolerance curves report point-estimate eligibility and do not certify a loss bound.
Random-mean cost is the average cost of deploying one random pool, not the cost
of executing all three research repetitions. Negative loss remains visible.

## Provenance and claim ledger

| Claim | Evidence | Allowed wording | Unsupported stronger wording |
| --- | --- | --- | --- |
| Three default PageRank losses | arm_path.csv; primary_tests.csv; original NPZ; full_validation.json | Measured default-tolerance differences; ca-GrQc is precision-sensitive | PageRank universally fails or ca-GrQc loss is solver-robust |
| Degree agreement | arm_path.csv; direction_diagnostics.csv; replayed round totals | Reproduces W1280 reference for 15 paths | Expected-optimal or universally lossless |
| Resolution sensitivity | full_reference_transitions.csv; Fig2_source.csv | ca-GrQc and CollegeMsg references change in utility on some paths | Every network is budget-sensitive |
| Coverage control | summary_by_method.csv; Fig1_source.csv | 5% restores ca-GrQc PageRank agreement, not wiki-Vote | A universal 5% threshold |
| Coupling | coupling_transitions.csv; FigS1_source.csv | PR losses persist in the preselected W320 edge control | Coupling never matters |
| Cost savings | arm_path.csv; supplement_setup_timing.csv; timing_repeats.csv; Fig3_source.csv | Savings in explicitly assembled warm-process scenarios | Guaranteed production acceleration |
| Smaller high-budget gains in historical graphs | historical analysis/summary.json | Historical 1280→5120 evidence retained | External graphs converge by 1280 |

## Post-hoc PageRank numerical-precision controls

The first separately frozen precision protocol reran both PageRank pool sizes on
all three graphs and five original W1280 paths with tol1e-12 (pool membership also
agrees at 1e-14). The later, separately frozen budget control added the same
restricted arms at W80 and W320: 30 new conditions/60 restricted-arm executions.
Together the two post-hoc layers contain 45 conditions/90 restricted-arm
executions, reuse the original paths and add no independent samples or primary
tests. The all-budget analysis, rather than this W1280-only table, is in
`analysis/precision_budget/analysis-report.md`.

| dataset | method | paths | delta_vs_full | mean_loss_percent | delta_vs_default | same_order_as_default | same_set_as_default |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ca_grqc | pagerank_4k | 5 | 0.02608 | -0.544437 | 0.2769 | 0 | 0 |
| ca_grqc | pagerank_5pct | 5 | 0.0 | 0.0 | 0.0 | 5 | 5 |
| college_msg | pagerank_4k | 5 | -0.9078 | 9.011829 | 0.0 | 5 | 5 |
| college_msg | pagerank_5pct | 5 | -0.43094 | 4.277063 | 0.0 | 5 | 5 |
| wiki_vote | pagerank_4k | 5 | -41.2197 | 73.955131 | -0.52636 | 0 | 0 |
| wiki_vote | pagerank_5pct | 5 | -13.63982 | 24.472041 | -0.1097 | 3 | 3 |
