# v2-T0b Final Statistics Audit

Date: 2026-07-31

## Scope and Method

This is a read-only evidence audit of the completed strict timestamp-grouped
Higgs study. It does not rerun a summarizer, regenerate analysis outputs, or
modify configuration or experiment artifacts.

Evidence reviewed:

- `results/large-robust-greedy-higgs-50000-v2-t0b/manifest.json`;
- thirty preregistered `split-{fraction}-seed-{42..51}.json` artifacts;
- `method_metrics.csv` (210 rows) and `aggregate_statistics.json`;
- `analysis/v2-t0b-strict-paired-v1/paired_comparisons.json` and report;
- the read-only `validate_study()` check in
  `experiments/build_v2_t0b_paired_analysis.py`.

## Completeness and Provenance

- Required runs: 30; manifest runs: 30; artifacts present: 30.
- Fractions: 0.60, 0.65, and 0.70; seeds: 42--51.
- Seven methods per run yield 210 metrics rows; aggregate output has 21 groups.
- The strict validator passed the exact preregistered run set, manifest
  SHA-256 checks, common-random-number protocol, probability protocol, strict
  calibration cutoff, frozen configuration, and CSV-to-artifact traceability.
- No nonempty experiment logs matching `stderr` or `error` were found.
- There are 18 paired contrasts: three fractions times six baselines.

## Statistical Result

Differences are `gnn_guided_robust_greedy_v2_t0b - baseline`. Every paired mean
difference is positive. Exact two-sided sign-flip tests are Holm-corrected
within the preregistered 18-contrast family. The ten repetitions are paired
protocol repetitions, not independent social-network samples.

Holm-significant contrasts (11):

- 0.60: PageRank, k-shell, Greedy MC.
- 0.65: Degree, PageRank, k-shell, GNN Top-K, Greedy MC.
- 0.70: PageRank, k-shell, Greedy MC.

Not Holm-significant (7):

- 0.60: Degree (Holm p = 0.054688), GNN Top-K (0.054688), RIS (1.000000).
- 0.65: RIS (1.000000).
- 0.70: Degree (0.054688), GNN Top-K (0.125000), RIS (0.750000).

All three RIS confidence intervals cross zero: 0.60 [-11.050, 28.559], 0.65
[-109.706, 524.820], and 0.70 [-121.354, 480.659].

## Claim Boundary

Allowed wording: the strict timestamp-grouped Higgs study supports
protocol-conditional Holm-significant improvements over PageRank, k-shell, and
Greedy MC at all three fractions, and over Degree and GNN Top-K at 0.65 only.

Forbidden wording: "significantly superior to RIS," "significantly better than
every baseline at every split," universal superiority, causal diffusion claims,
or cross-dataset generalization from this Higgs-only study.
