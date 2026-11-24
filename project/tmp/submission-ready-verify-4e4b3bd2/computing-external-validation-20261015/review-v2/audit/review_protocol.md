# Author-review audit and post-hoc analysis protocol

Created 2026-10-15 after external outcomes were available. This is neither a new
confirmatory experiment nor a public preregistration. Frozen v1 is preserved.

The primary family remains three W=1280 comparisons within each graph, with
two-sided exact sign tests on nonzero path means and within-graph Holm correction.
Random pools are averaged within path before inference. No network pooling.
Conditional MC standard errors use paired per-world differences; path SD and
t intervals (descriptive, post-hoc) describe five algorithmic paths, not network
population uncertainty. Negative loss is retained, not truncated.

Verification reconstructs topology independently from raw text; checks all hashes,
matrix entries, candidates, world IDs, every stored score's argmax/tie trace,
evaluation arrays and summary fields; replays all evaluations and full greedy
scores using frozen core; and checks a scalar Python IC/hash oracle on predetermined
first 16 evaluation worlds per unique seed sequence. No result-based exclusions.
Repeated full-pool execution checks exact deterministic identity. Any discrepancy
blocks package acceptance and is recorded rather than overwritten.

Supplementary timing is post-hoc, outcome-independent, five repetitions per graph:
fresh raw parse/CSR, method-specific ranking and pool construction. It supplements
frozen selection/world/evaluation timings; this assembled warm-process, cached-file
scenario is explicitly a hybrid estimate, not an end-to-end wall-clock benchmark.
Archived graph preparation is an audit-rich operation containing all rankings;
the separate archived ranking values must not be added to it again. JIT compilation,
disk result writing and downloading are excluded from deployment estimates and
disclosed. Preserve selection-only and verification-inclusive scenarios separately.

Timing implementation correction before final delivery: the preliminary setup
probe included a candidate sort already present inside the frozen greedy timer
and overlapped CPU activity from the audit. Preserve that probe as provisional,
then repeat all five setup trials on all graphs after full replay completes,
omitting the duplicate sort. No outcome, graph or method is selected/excluded by
timing results. Final analyses use only the corrected-scope measurements.

No W=5120 study is needed for the revised, bounded claim: results concern budgets
80,320,1280 under p=.01,h=3,k=5 on these three topologies. Delete any assertion of
external high-budget convergence or universal ranking superiority. A future claim
of convergence would require a new design and cannot be inferred from this audit.

Figures: Python quantitative grids, 119 mm width, editable vector PDF/SVG and PNG
previews, minimum 8 pt font. Show all graph/path observations or explicitly stated
aggregates. Main evidence: paired incremental loss by budget and pool coverage;
reference-set changes versus utility; cost versus descriptive tolerances. Coupling
control remains separate (3 paths at W320). Source CSVs accompany every figure.
