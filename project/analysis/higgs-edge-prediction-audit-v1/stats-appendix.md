# Statistical Appendix: Higgs Edge-Prediction Audit

### Train fraction 0.60

- Future AUC: mean 0.6294, SD 0.1460, 95% t-CI [0.5249, 0.7338], n=10.
- Train reconstruction AUC: mean 0.9597, SD 0.0334.
- Future Brier: mean 0.2348, SD 0.0881; ECE: mean 0.1820, SD 0.1112.
- Inverted-score future AUC: mean 0.3706, SD 0.1460.
- Shapiro-Wilk on future AUC: W=0.6744, p=0.000432; normality is not supported at alpha=0.05.
- Two-sided Wilcoxon signed-rank test of future AUC against 0.5: W=3.0000, p=0.009766.
- Exact two-sided sign test: 8/10 seeds above 0.5, p=0.1094.
- Below-random seeds: 42, 48.

### Train fraction 0.65

- Future AUC: mean 0.6336, SD 0.1467, 95% t-CI [0.5287, 0.7385], n=10.
- Train reconstruction AUC: mean 0.9552, SD 0.0362.
- Future Brier: mean 0.2310, SD 0.0858; ECE: mean 0.1954, SD 0.0971.
- Inverted-score future AUC: mean 0.3664, SD 0.1467.
- Shapiro-Wilk on future AUC: W=0.7154, p=0.001353; normality is not supported at alpha=0.05.
- Two-sided Wilcoxon signed-rank test of future AUC against 0.5: W=4.0000, p=0.01367.
- Exact two-sided sign test: 8/10 seeds above 0.5, p=0.1094.
- Below-random seeds: 42, 48.

### Train fraction 0.70

- Future AUC: mean 0.6306, SD 0.1469, 95% t-CI [0.5256, 0.7357], n=10.
- Train reconstruction AUC: mean 0.9506, SD 0.0391.
- Future Brier: mean 0.2318, SD 0.0860; ECE: mean 0.1967, SD 0.0988.
- Inverted-score future AUC: mean 0.3694, SD 0.1469.
- Shapiro-Wilk on future AUC: W=0.7466, p=0.003242; normality is not supported at alpha=0.05.
- Two-sided Wilcoxon signed-rank test of future AUC against 0.5: W=4.0000, p=0.01367.
- Exact two-sided sign test: 8/10 seeds above 0.5, p=0.1094.
- Below-random seeds: 42, 48.

## Test Scope and Limitations

- ROC-AUC is higher-is-better. Brier score and ECE are lower-is-better.
- Each future evaluation compares unique observed future edges with an equal
  number of uniformly sampled absent directed pairs, excluding all known past
  and future positives. This matches the frozen pipeline's evaluation design.
- Shapiro-Wilk rejects normality for the observed AUC distributions, so the
  Wilcoxon and exact sign tests are reported rather than a t-test. The three
  cutoff-specific tests are descriptive diagnostics; they are not a family of
  claims about different datasets, and no statistical winner claim is made.
- Training and future AUC use different edge sets. Their contrast demonstrates
  a generalization gap but is not a causal experiment.
- The same data split is reused across seeds. Consequently these intervals and
  p-values represent variability from stochastic optimization, not sampling
  uncertainty over the underlying social network.
