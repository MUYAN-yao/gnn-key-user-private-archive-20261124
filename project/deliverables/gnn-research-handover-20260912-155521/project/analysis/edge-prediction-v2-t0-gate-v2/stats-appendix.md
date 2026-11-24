# Statistical Appendix: v2 T0 Gate Test

- ROC-AUC is the primary ranking metric; each split has ten fixed seed
  replicates. The 95% t-CI is descriptive of seed variation, not uncertainty
  across social-network populations.
- Brier and ECE are calculated after isotonic calibration fitted only on the
  final-calibration temporal window. Lower is better; the balanced prevalence
  Brier reference is 0.25.
- The inverse AUC check detects score-direction reversal. All seed-level
  inverse AUC values are below 0.5.
- No p-value comparison to v1 is reported: T0 changes both training objective
  and temporal partitioning, so a causal improvement claim needs a separately
  fixed paired comparison protocol.
