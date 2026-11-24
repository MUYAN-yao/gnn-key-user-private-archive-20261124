# v7 design review

Design date: 2026-09-19. Decision: suitable for bounded implementation work;
not approved evidence of novelty, efficiency, or publication readiness.

## Completed

- A mathematical finite-world upper bound and exact-comparison design were
  independently reviewed; no submodular or population-optimality claim is made.
- The small-vector checker passed 395,505 cases. Its JSON explicitly records
  zero graph experiments and zero training runs.
- The JSON and CSV agree on E2/E3/E4 sizes: 108/180/40 method executions.
  Rows are unique and marked planned_not_run; formal_enabled is false.
- Development and formal seed lists are disjoint; preflight seed is separate.
- Statistical review found and resolved primary-cost ambiguity, incomplete
  resource projections when development arms fail, and the GCOMB component's
  dependency on all development full-search labels.

## Still open before performance conclusions

1. Implement exact numerical scoring, structural bounds and cache-safe search.
2. Pass graph-based correctness fixtures and ordinary-bound/no-SSE controls.
3. Complete nearest-method novelty and applicability checks.
4. Demonstrate development feasibility; zero unresolved retained-arm failures.
5. Admit new datasets with recorded terms, semantics and hashes.
6. Freeze source/config/data/analysis and pass outcome-blind resource checks.

The design deliberately keeps GNN training outside the core study. It does
not promise that the upper bound will prune enough to cover its own cost.
