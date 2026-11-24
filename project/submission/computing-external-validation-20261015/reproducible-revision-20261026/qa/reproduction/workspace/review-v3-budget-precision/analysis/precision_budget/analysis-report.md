# Strict-PageRank budget sensitivity analysis

This report is regenerated from the frozen default matrix, the previously frozen strict W=1280 control and the separately frozen strict W=80/W=320 matrix. The added control reuses original paths and is post-hoc; it adds no independent networks or selection paths.

## Main readout

- college_msg, pagerank_4k: mean incremental losses default W=80: 9.331%; default W=320: 8.518%; default W=1280: 9.012%; strict W=80: 9.331%; strict W=320: 8.518%; strict W=1280: 9.012%.
- college_msg, pagerank_5pct: mean incremental losses default W=80: 4.572%; default W=320: 3.723%; default W=1280: 4.277%; strict W=80: 4.572%; strict W=320: 3.723%; strict W=1280: 4.277%.
- ca_grqc, pagerank_4k: mean incremental losses default W=80: -5.613%; default W=320: 2.529%; default W=1280: 5.070%; strict W=80: -11.251%; strict W=320: -2.963%; strict W=1280: -0.544%.
- ca_grqc, pagerank_5pct: mean incremental losses default W=80: -2.623%; default W=320: 0.000%; default W=1280: 0.000%; strict W=80: -2.623%; strict W=320: 0.000%; strict W=1280: 0.000%.
- wiki_vote, pagerank_4k: mean incremental losses default W=80: 73.011%; default W=320: 73.063%; default W=1280: 73.011%; strict W=80: 74.054%; strict W=320: 74.055%; strict W=1280: 73.955%.
- wiki_vote, pagerank_5pct: mean incremental losses default W=80: 24.906%; default W=320: 24.670%; default W=1280: 24.275%; strict W=80: 24.834%; strict W=320: 24.672%; strict W=1280: 24.472%.

## Required interpretation limits

- Default and strict PageRank are separate named implementations. Strict ranking is stable at tolerance 1e-14 for every pool, but a strict/default difference can arise through candidate-pool truncation and downstream greedy choice.
- Conditional Monte Carlo intervals quantify simulation noise for the fixed seeds/worlds. Path variation quantifies variation across five paired computational paths; neither is a population confidence interval across social networks.
- The analysis does not add a p-value family or reclassify post-hoc outcomes as confirmatory. Full eligibility, propagation, graph and evaluation families remain frozen.

See `path_metrics.csv`, `tolerance_effects_by_path.csv`, `budget_transitions_by_path.csv`, `budget_tolerance_interaction_by_path.csv`, and the figure source CSV for all values.
