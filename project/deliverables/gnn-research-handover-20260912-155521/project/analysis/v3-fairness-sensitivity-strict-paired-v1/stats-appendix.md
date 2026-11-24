# Statistical Appendix: v3 Fairness and Sensitivity

- Input guard: exactly 30 non-smoke artifacts, matching hashes, strict
  timestamp boundaries, and disjoint selection/evaluation world digests.
- Primary metric: reporting robust objective with risk lambda 0.35 and
  community weight 0.25, evaluated only on held-out deterministic worlds.
- Test: exact two-sided sign-flip randomization across the ten paired runs.
- Interval and effect size: 95% t interval and paired Cohen dz, descriptive.
- Multiplicity: Holm correction is applied separately to the predeclared
  primary-fairness, pool-sensitivity, and weight-sensitivity families.
- Limitation: all inference is protocol-conditional and Higgs-only.
