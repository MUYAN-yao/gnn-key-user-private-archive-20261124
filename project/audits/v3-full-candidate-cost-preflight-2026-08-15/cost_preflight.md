# v3 Full-Candidate Cost Preflight

- Decision-graph nodes: 33,529
- Exact robust-greedy candidate-set evaluations per run: 67,057 full-candidate, 239 screened-120, 1,796 pool-sensitivity, and 2,151 weight-sensitivity.
- Deterministic diffusion calls: 1,424,860 per run and 42,745,800 for all 30 runs.
- This is an operation-count budget, not a wall-clock estimate. A full batch must not start until the available compute allocation can cover this budget without modifying frozen studies.
