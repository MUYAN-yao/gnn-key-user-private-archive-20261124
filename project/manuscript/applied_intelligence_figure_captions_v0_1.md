# Figure captions and source map (working version)

This map records the six figures selected for the Applied Intelligence working
draft. Captions state only the evidence supported by the corresponding
artefact. Final production files must preserve readable labels, embedded fonts,
and the journal's required figure resolution and format.

**Fig. 1 Temporal information boundary.** A schematic of the prediction and
decision boundary used throughout the study. Features, labels, and candidate
selection use only information available before the decision time; later
diffusion is reserved for evaluation. Source:
`manuscript/figures_v44/fig-07-time-boundary.svg`.

**Fig. 2 Protocol and matched candidate comparison.** Overview of the temporal
graph construction, learned screening stage, matched candidate-pool comparison,
and common-world diffusion evaluation. The diagram describes the protocol; it
does not imply a causal or online deployment claim. Source:
`manuscript/figures_snam_r45/fig-02-method-mechanism.svg`.

**Fig. 3 Frozen-protocol paired comparison.** Paired outcomes for the frozen
evaluation protocol. Each paired point uses the same evaluation world for the
two compared policies, so the displayed difference isolates the declared policy
contrast within that world. Source:
`manuscript/figures_v44/fig-01-frozen-comparison.tif`.

**Fig. 4 Strict T0b comparison.** Paired outcomes under the stricter temporal
information boundary (T0b). The figure tests robustness to the declared
information restriction; it is not evidence of cross-platform generality.
Source: `manuscript/figures_v44/fig-04-t0b-comparison.tif`.

**Fig. 5 Higgs candidate-reduction comparison.** Formal Higgs common-world
comparison of full and screened candidate search. Exact objective ties in the
planned blocks are reported as ties, not as proof of equivalence. Source:
`analysis/v3-fairness-sensitivity-strict-paired-v1/figures/figure-01-screened-vs-full.pdf`.

**Fig. 6 Digg candidate-pool failure boundary.** Formal Digg k=5 common-world
paired objective differences relative to full-candidate search. Pools of 60 and
120 matched the full-search objective in all planned seeds; the pool of 30 lost
in every planned seed (mean difference -3.499, 95% CI [-4.011, -2.987], exact
two-sided p = 0.001953; Holm-adjusted p = 0.005859). The figure establishes a
protocol-conditional failure boundary, not a universal pool-size threshold or a
GNN advantage over degree screening. Source:
`analysis/v6-digg-k5-formal-v3/figures/figure-01-primary-paired-delta.svg`.

## Production checks remaining

- Export or retain a journal-compliant production version for each source.
- Place each caption in the manuscript text and number figures consecutively.
- Verify all axes, legends, units, and colours after the final PDF is rendered.
- Keep the source map with the reproducibility archive; do not use it as the
  submitted figure-legend page.
