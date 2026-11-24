# Statistical specification and data dictionary

Prespecified family: W1280 step coupling, degree4k/PageRank4k/random mean versus
full, separately per graph; two-sided exact binomial sign tests on nonzero path
differences; Holm across 3 contrasts per graph, 9 tests total. Exact zeros are
reported. Sign tests concern sign balance, not expected effect size.

For each method/path, d_i = spread(method,i) - spread(full,i) on the same 10000
independent evaluation worlds. Delta=mean(d_i), MC SE=sd(d_i,ddof=1)/sqrt(10000).
The normal interval Delta +/-1.96 SE is conditional on the selected sets, graph,
and propagation law; it is not a selection-path or real-network interval.
Spread includes k=5 seeds. Incremental spread=spread-5. Loss percent=-100*Delta /
(mean(full)-5). Every observed denominator is positive; these plug-in ratios do
not have MC confidence bounds attached. A negative loss denotes measured gain.

Random repeats are coupled through shared evaluation worlds. First average all
three evaluation vectors within a path and compute its paired difference/SE,
preserving covariance; then aggregate path means. within_path_random_delta_sd
describes candidate-pool variability. Across-path SD includes the realized
evaluation noise as well as selection-path changes; it is not a deconvolved
selection-only variance. Post-hoc t intervals use df=n_paths-1 and are descriptive
with only 5 (or 3 control) computational paths. There is no network-population CI.

Agreement: same_order compares full sequences; same_set compares unordered sets;
Jaccard=intersection/union. first_divergence is one-based and zero means identical.
For random_mean rows agreement and Jaccard are repeat fractions/averages; there is
no single averaged seed set, so first_divergence is NA. Full-reference transitions
use shared evaluation IDs at both W values. Coupling contrasts compare separately
generated step/edge outcomes with shared IDs; they are post-hoc descriptive and
not a causal estimate of one algorithmic change independent of seed changes.

Tolerance curves use thresholds 0,1,2.5,5,10,20% of incremental spread. All paths
are retained; passing_paths and passing_mean_saving_percent describe realized
point estimates, with no simultaneous loss guarantee or noninferiority test.

The separately frozen post-hoc PageRank precision control reuses all five original
paths atW1280;15 conditions/30 restricted arms are not added to primary tests or
independent sample size. It compares tol1e-12 versus the frozen default1e-6. Full
results/protocol/hashes are in supplement-pr-precision, outside the main CSVs.

CSV inventory: arm_path (468 executed+54 random means); summary_by_method (graph/
stage/W/method averages and path SD); primary_tests; full_reference_transitions
(45 including direct80→1280); transition_summary; coupling_transitions;
direction_diagnostics; timing_repeats (130); timing_summary;
supplement_setup_timing (100 post-hoc); tolerance_cost_curves. Figure source CSVs
are filtered copies with all observations required for the indicated panels.
