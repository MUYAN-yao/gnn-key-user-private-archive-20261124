# Online Resource 1: Experimental provenance and complete comparison profile

**Article:** Selection Resolution Changes Candidate-Truncation Conclusions in Simulated Influence Maximization  
**Target journal:** Computing  
**Authors:** Jiayue Sun, Binbin Yong\*, Junjie An, Tianyu Bo, and Shuai Li  
**Corresponding author:** Binbin Yong, yongbb14@lzu.edu.cn  
**Affiliations:** The main manuscript provides confirmed affiliations for Jiayue Sun and Binbin Yong. Affiliation details for Junjie An, Tianyu Bo, and Shuai Li are to be confirmed before submission.

## S1. Data transformation and scope

The graph instances are derived from the SocioPatterns invs2013, invs2015, sfhh2009, and kenya2012 contact records. Provider licenses, archive hashes, parsing rules, and semantic limitations are documented in the [data admission ledger](../../protocols/candidate_truncation_data_admission_v0_1.md). Dataset studies are cited in the main manuscript [3–6].

Complete timestamp groups are used to select the historical portion (first 65%). Undirected records are represented bidirectionally. The graph builder removes self-loops and collapses repeated directed pairs into adjacency edges; historical contact weights inform degree ranking. Thus the simulator operates on an aggregated historical graph. Temporal contacts are the source of the topology, not observations of information propagation.

The provider pages specify CC0 terms for the admitted datasets. The planned release preserves provenance and preparation code; raw provider archives are not included in the present manuscript package.

## S2. Fixed design and replication units

| Data instance | Seed budgets | Random-world paths | Selection budgets | Conditions |
| --- | --- | --- | --- | ---: |
| invs2013 | 5, 20 | 301, 302 | 20, 80, 320 | 12 |
| invs2015 | 5, 20 | 301, 302 | 20, 80, 320 | 12 |
| sfhh2009 | 5 | 301, 302 | 20, 80, 320 | 6 |
| kenya2012 | 5, 20 | 301, 302 | 20, 80, 320 | 12 |

The 42 conditions contain four arms each: full greedy and degree pools of at most 2k, 4k, and 8k nodes. Within an arm, the pool remains fixed. All conditions use independent cascade, probability 0.01, horizon three, and 2,000 evaluation worlds. Selection worlds are prefix-nested within each path; evaluation identifiers belong to a separate family. Within a dataset and path, the evaluation worlds are reused across selection budgets and seed budgets. Consequently, conditions are not mutually independent statistical replicates.

The SFHH k=20 combination was excluded through outcome-blind resource preflight under the four-hour serial ceiling. The [fixed protocol](../../protocols/sociopatterns_resolution_confirmation_protocol_v0_1.md) records the admission and stopping rules.

## S3. Execution provenance

The admitted execution is [snapshot-r3-confirmation-run-20260920](../../audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920/manifest.json). It completed 42/42 conditions. Its execution source snapshot is [the r3 snapshot manifest](../../reproducibility/v10-source-snapshots/sociopatterns-resolution-confirmation-v0_1-20260920-r3/snapshot_manifest.json).

The [validation report](../../analysis/sociopatterns-resolution-confirmation-v0_1/validation-v0_2.json) records PASS. Later manuscript editing and read-only reporting do not replace the frozen execution source. Historical runs outside this admitted source are not evidence for the main article.

## S4. Complete aggregate utility profile

Differences are candidate-minus-full mean activated-node counts on evaluation worlds. Each row summarizes 14 conditions. Minima and maxima are the observed condition range, not confidence intervals. Counts and means are descriptive; networks, seed budgets, and shared-world comparisons should not be treated as independent population samples.

| Pool | W | Mean difference | Minimum | Maximum | Positive / zero / negative |
| --- | ---: | ---: | ---: | ---: | --- |
| 2k | 20 | +0.053 | −0.755 | +1.270 | 8 / 0 / 6 |
| 2k | 80 | −0.225 | −0.848 | +0.156 | 3 / 0 / 11 |
| 2k | 320 | −0.356 | −0.831 | +0.019 | 1 / 0 / 13 |
| 4k | 20 | +0.090 | −0.513 | +0.669 | 8 / 4 / 2 |
| 4k | 80 | +0.028 | −0.739 | +0.905 | 7 / 4 / 3 |
| 4k | 320 | −0.158 | −0.672 | +0.031 | 1 / 4 / 9 |
| 8k | 20 | +0.007 | −1.112 | +0.752 | 6 / 6 / 2 |
| 8k | 80 | −0.040 | −0.636 | +0.470 | 5 / 5 / 4 |
| 8k | 320 | −0.124 | −0.610 | 0.000 | 0 / 7 / 7 |

Rounded values use three decimal places. The [machine-readable summary](../../analysis/sociopatterns-resolution-confirmation-v0_2/summary.json) retains additional precision. Exact agreement and timing appear in Table 4 of the main manuscript. These aggregate values include saturated pools; see S7 for the distinction between full coverage and genuine restriction.

## S5. Trace and timing interpretation

The primary agreement measure compares ordered sequences. A mismatch can result from order alone and is not sufficient to establish unequal final sets or lower utility. The full-round tie counts are 80/160, 46/160, and 21/160 for W=20, 80, and 320, respectively. Each denominator sums eight traces of five rounds and six traces of 20 rounds, totaling 160 rounds. Rounds within a trajectory are dependent.

The complete individual tie trajectories are displayed in main-text Fig. 4. Their 42 block-budget observations remain available in `figures/FigS1-tie-trajectories-source.csv`.

Decision time starts after graph preparation and degree ranking, and includes greedy search and final independent evaluation. Savings are calculated against the full arm within each condition, then summarized by their median. They are not end-to-end speedups or hardware-independent complexity measurements.

## S6. Supporting files and release status

- [Condition-level candidate profiles](../../analysis/sociopatterns-resolution-confirmation-v0_2/candidate_condition_profile.csv)
- [Full-reference trajectories](../../analysis/sociopatterns-resolution-confirmation-v0_2/full_trajectories.json)
- [Analysis readout](../../analysis/sociopatterns-resolution-confirmation-v0_2/readout.md)
- [Release inventory](reproducibility_release_inventory.md)

These links identify local evidence in the working package. Before submission, the selected files must be packaged into the supplementary upload or a persistent public archive and the local links replaced with publication-ready references. An archive DOI has not yet been assigned.

## S7. Post-hoc set, coverage, and uncertainty diagnostics

The additional analysis reads the frozen 42 outputs and does not rerun selection. Its [script](../../analysis/extend_resolution_diagnostics.py) exports [all 28 adjacent-budget set comparisons](../../analysis/resolution-diagnostics-posthoc-20260920/full_set_transitions.csv), [all 126 paired evaluation comparisons](../../analysis/resolution-diagnostics-posthoc-20260920/paired_evaluation_diagnostics.csv), and [historical graph sizes](../../analysis/resolution-diagnostics-posthoc-20260920/graph_instances.csv).

No final full-greedy set is unchanged at either adjacent transition (0/14 for each). Candidate-versus-full unordered and ordered agreement coincide in this matrix. Full-pool controls account for six matches at 4k and twelve at 8k. Excluding these controls gives genuine-restriction match counts of 0/42, 6/36, and 6/30 for 2k, 4k, and 8k, respectively. Exclusion changes the comparison populations; these ratios are descriptive.

Monte Carlo intervals use paired per-world spread differences, their sample standard deviation divided by the square root of 2,000, and the normal multiplier 1.96. They are conditional on selected sets and the simulator, unadjusted for multiple comparisons, and do not include selection or network-population uncertainty. These diagnostics were added after inspecting confirmation summaries and must be identified as post-hoc. Figures 7 and 8 do not represent newly collected experiments.

## S8. Figure sources and editable master

Figure 1 is a schematic with native Visio shapes in `figures/Fig1-mechanism-editable.vsdx`; it contains no measured network layout or proportionally scaled world counts. Its PNG, SVG, and PDF exports are supplied. Figures 3, 5 and 6 derive from `analysis/build_computing_main_figures.py`, which delegates Figures 3 and 4 to `analysis/build_reference_resolution_figures.py`; Figures 7 and 8 derive from the S7 script. Figure 5 distinguishes full-node pools from successful restricted matches.

Publisher figures downloaded into `literature/` are internal style references only. They are not manuscript figures and must be excluded from any public reproducibility archive, as must local backups and publisher HTML copies. Include the verified bibliography and original figure-generation scripts instead.


Figure 2 documents the admitted matrix, nested budgets, paired arms and disjoint evaluation design. Its native master is `figures/Fig2-experimental-design.vsdx`, generated by `analysis/build_visio_experimental_design.ps1` using the shared helpers in `analysis/build_visio_mechanism.ps1`. Original result-asset filenames retain their earlier numbers; display numbering in the manuscript and the figure index is authoritative.
