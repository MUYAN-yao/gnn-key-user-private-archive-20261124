# Budget–precision sensitivity and narrative revision — 2026-10-16

## Objective

Create a new, independent author-review version that tests whether the observed
PageRank budget sensitivity persists after candidate ranking uses a stricter
numerical tolerance. Then reorganize the Computing manuscript around the
strongest supported evaluation contribution. The prior `review-v2` package,
the external frozen matrix, the historical archive and the v3 delivery ZIP are
read-only evidence.

## Guardrails

- New results live in `submission/computing-external-validation-20261015/review-v3-budget-precision`.
- The addition is an outcome-seen post-hoc numerical sensitivity study, not a
  confirmation study, a new preregistration or additional independent networks.
- Use the original three graphs, five paths, step-coupled worlds, propagation
  parameters, deterministic ties and disjoint 10,000-world evaluation family.
- Do not rerun already verified full eligibility. Reuse it only after checking
  graph/source/world hashes and store paired restricted outputs separately.
- Preserve all adverse, null and precision-sensitive results. No automatic
  submission, publication or external contact.

## Phases

1. Verify v2 inputs and create a minimal pre-outcome protocol/source manifest — complete.
2. Freeze and execute strict-tolerance PageRank at W=80 and W=320 for all graph/path/pool combinations — complete (30 conditions, 60 arms).
3. Recompute paired effects, Monte Carlo uncertainty, path variation, candidate-pool changes and budget/tolerance interaction — complete.
4. Compare contribution framings, select the most defensible narrative, and rewrite manuscript/materials — complete (separate evaluation resolutions selected as the main line).
5. Compile, regenerate, inspect, verify and archive a new local author-review package — complete (all delivery gates and an extraction-time SHA-256 verification pass).
