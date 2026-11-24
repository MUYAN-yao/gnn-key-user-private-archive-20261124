# Statistical Appendix: Higgs v2-T0b Paired Comparisons

## Design and Checks

- Input guard: exactly 30 preregistered JSON artifacts, a batch manifest, and a
  method-metrics table with all 10 seeds and 7 methods are required.
- Pairing: the same timestamp split, random seed, and common-random diffusion
  streams define a paired run.
- Primary metric: robust objective, higher is better.
- Test: exact two-sided sign-flip randomization test over all 2^10 sign
  assignments. The p-value does not require a normality assumption for paired
  differences.
- Interval: 95% t interval of the paired mean difference, reported descriptively.
- Effect size: paired Cohen dz, mean paired difference divided by the sample SD.
- Multiplicity: Holm correction across all 18 preregistered contrasts.

## Limits

- Random seeds quantify protocol stochasticity, not a population of independent
  social networks.
- Every conclusion is limited to timestamp-grouped Higgs and the frozen T0b
  configuration, candidate pool, diffusion model, horizon, and simulation count.
- This bundle does not establish causal diffusion probabilities or cross-dataset
  generalization.
