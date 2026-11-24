# Manuscript-Evidence Consistency Audit (r31)

Date: 2026-07-31

## Scope

This is a read-only consistency audit of the r31 manuscript source against the
frozen paired-analysis bundle, the completed strict v2-T0b paired-analysis
bundle, and the implementation constants. It does not rerun experiments,
regenerate analysis outputs, or modify model configuration.

## Evidence Checked

- `analysis/frozen-main-comparison-v1/paired_comparisons.json`;
- `analysis/v2-t0b-strict-paired-v1/paired_comparisons.json`;
- `backend/app/optimizer.py`, `backend/app/pipeline_v2_t0b.py`, and
  `experiments/build_v2_t0b_paired_analysis.py`;
- `manuscript/draft_zh_v0_1.md`, claim ledger, and statistical appendix.

## Results

| Check | Evidence | Result |
| --- | --- | --- |
| Frozen comparison family | 24 rows in the frozen paired-comparison JSON | matches the manuscript's separate 24-contrast Holm family |
| Frozen zero-difference disclosure | the only zero-mean row is Higgs 50k / 0.60 / RIS, with 0 wins, 10 ties, and 0 losses | matches the disclosed exact Higgs/RIS tie |
| Frozen nonzero contrasts | every nonzero frozen contrast has Holm-adjusted p <= 0.05 | matches the bounded frozen result wording |
| Strict comparison family | 18 rows, three fractions, six recorded comparators | matches the separate 18-contrast Holm family |
| Strict numerical Holm results | 11 rows have Holm-adjusted p <= 0.05 | matches the manuscript's numerical 11/18 statement |
| Strict independent-comparator results | 10 Holm-significant rows remain after excluding GNN Top-K | matches the narrative: PageRank, k-shell, and Greedy MC at every fraction, and Degree only at 0.65 |
| Protected GNN Top-K check | the 0.65 GNN Top-K row has Holm p = 0.039062, while `gnn_guided_robust_greedy()` returns the better of greedy and the same GNN Top-K set | relabeled as a lower-bound implementation audit, not independent efficacy evidence |
| Strict RIS boundary | Holm p values are 1.000000, 1.000000, and 0.750000 at 0.60, 0.65, and 0.70 | matches the prohibition on significant RIS superiority |
| Strict constants | `seed_count=2`, horizon 4, risk lambda 0.35, community weight 0.25, IC, 10 epochs, 20 simulations, candidate pool 120 | matches the protocol and manuscript settings |
| Pairing and temporal boundary | strict pipeline records common random numbers and asserts calibration cutoff before outer-test start | matches the stated protocol-level interpretation |

## Conclusion

The r31 manuscript source matches the reviewed numerical evidence and current
implementation boundaries for the checked claims. This audit does not close the
remaining submission gates: fuller literature comparison, data/archive
decisions, author metadata, official-template conversion, and page-by-page
visual QA remain required.
