# Statistical Appendix: Frozen Main Comparisons

## Method

- Primary metric: robust objective, higher is better.
- Pairing: same dataset, temporal split, random seed, and common-random
  diffusion streams; therefore the statistical object is the within-run
  objective difference.
- Test: exact two-sided sign-flip randomization test over all 2^10 sign
  assignments. This requires no normality assumption for the paired difference.
- Multiplicity: Holm correction across the 24 planned contrasts
  (2 datasets x 3 splits x 4 baselines).
- Effect size: paired Cohen dz, mean paired difference divided by the sample
  SD of paired differences. A value is reported as `infinite` only when every
  paired difference is the same nonzero value.

## Results

The exact numerical table in `analysis-report.md` contains every planned
contrast, including the Higgs/RIS null result at train fraction 0.60. No
contrast has been omitted for lack of significance.

## Limits

- Seed replicates quantify stochastic algorithm variation, not uncertainty over
  a population of independent datasets.
- Results are conditional on the frozen candidate pool, diffusion model,
  horizon, simulations, and baseline definitions recorded in the provenance
  manifest.
- Digg parent links are temporally valid exposure proxies, not observed
  reshares. Higgs probability predictions are seed-unstable and are not used
  as a validated causal explanation of the objective gains.
