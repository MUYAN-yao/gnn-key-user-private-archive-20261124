# Manuscript Claim Ledger

## C1: Conditional optimization improvement

- Evidence: `analysis/frozen-main-comparison-v1/analysis-report.md`.
- Unit: ten paired stochastic protocol runs per dataset/split; common random
  diffusion streams within each run.
- Allowed: Across the evaluated Digg and Higgs temporal protocols, the method
  improved the robust objective over Degree and Greedy MC. On Digg it also
  improved over RIS at all three splits. The recorded GNN Top-K differences
  are an algorithmic lower-bound audit because the reference returns the
  better of robust greedy and that same GNN Top-K seed set; they are not
  independent baseline-efficacy evidence.
- Constraint: On Higgs at train fraction 0.60, the method tied RIS; it
  improved over RIS only at 0.65 and 0.70.
- Forbidden: universal superiority or dominance of RIS at every split.

## C2: Temporal probability candidate validation

- Evidence: `analysis/edge-prediction-v2-t0-gate-v2/analysis-report.md`.
- Allowed: Fixed candidate T0 passed the prespecified ranking, calibration,
  inversion, and seed-stability gates on the isolated Higgs outer tests.
- Constraint: one dataset; balanced absent-pair evaluation; candidate grid
  incomplete; the subsequent strict-time influence result concerns only the
  frozen T0b configuration on Higgs.
- Forbidden: optimal architecture, universal probability prediction, or causal
  diffusion-probability claim.

## C3: Dataset scope and semantics

- Evidence: `data_cards/third_dataset_admission.md` and frozen study audit.
- Allowed: Higgs and Digg are analyzed under their documented temporal
  protocols; Digg parent links are treated as exposure proxies.
- Forbidden: a three-dataset claim or observed Digg re-share causality.

## C4: Reproducibility

- Evidence: `reproducibility/frozen-study-manifest-v1.json` and analysis
  manifests.
- Allowed: Frozen study inputs, run artifacts, aggregates, and core source
  files are hash-recorded; the complete v2-T0b study is separately versioned,
  manifest-hashed, and has a traceable 210-row metrics table.
- Constraint: the frozen v1 and strict v2-T0b studies are separate protocols;
  their numerical results must not be pooled.

## C5: Strict timestamp-grouped Higgs v2-T0b comparison

- Evidence: `results/large-robust-greedy-higgs-50000-v2-t0b/`,
  `analysis/v2-t0b-strict-paired-v1/paired_comparisons.json`, and
  `analysis/v2-t0b-strict-paired-v1/analysis-report.md`.
- Unit: ten paired stochastic protocol runs for each of the three Higgs
  training fractions. Methods share timestamp split, random seed, and common
  random diffusion streams; these runs are not independent social networks.
- Allowed: All 18 recorded reference-minus-comparator mean differences are
  positive. After Holm correction across the 18 preregistered contrasts, the
  reference is significant against PageRank, k-shell, and Greedy MC at all
  three fractions and against Degree at 0.65. The numerically significant
  GNN Top-K contrast at 0.65 is retained as a protected-lower-bound audit, not
  as independent baseline-efficacy evidence.
- Constraint: The remaining seven contrasts are not Holm-significant, including
  all three comparisons with RIS. Positive means and run-level win counts alone
  do not establish a strict advantage in those cases.
- Forbidden: significant superiority over RIS, universal superiority, causal
  diffusion claims, or cross-dataset generalization from this Higgs-only study.

## C6: Objective ablation (completed v2-T0d; null result)

- Invalid predecessor: `audits/v2_t0c_cross_process_reproducibility_failure_2026-07-31.md`.
  The incomplete v2-T0c output is excluded because cross-process set traversal
  did not preserve the archived diffusion random-stream mapping.
- Evidence: `results/large-robust-greedy-higgs-50000-v2-t0d-common-world-objective-ablation/`
  contains 30 hashed artifacts and 120 metrics rows; the separately generated
  analysis in `analysis/v2-t0d-common-world-objective-ablation-v1/` validates
  the run hashes, fixed configuration, timestamp order, common-world evaluator,
  and metrics-table agreement.
- Result: for all 30 fraction-seed runs, `full`, `risk_off`,
  `community_off`, and `spread_only` selected the same Top-K set and received
  the same score under the common full objective. All nine preregistered
  full-minus-ablation contrasts are exactly zero (10 ties per contrast;
  exact and Holm-adjusted p = 1.0).
- Allowed wording: within this separately versioned Higgs protocol, removing
  either or both terms did not change the selected set or common full-objective
  score. This is a null ablation result, not evidence that the terms are
  unnecessary in other candidate pools, budgets, datasets, or objectives.
- Forbidden: using v2-T0c as evidence, pooling v2-T0d with v2-T0b, universal
  necessity or irrelevance of either term, causal diffusion claims, or an
  optimal-weight claim.

## C7: v3 fairness and sensitivity (completed confirmatory null result)

- Protocol: `protocols/influence_v3_fairness_sensitivity_preregistration.md`.
- Smoke evidence: `audits/v3-fairness-sensitivity-smoke-2026-08-15/` verifies
  frozen inputs, strict timestamp ordering, separate world families, and the
  result schema. It is explicitly ineligible for inference.
- Evidence: `results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity/`
  and `analysis/v3-fairness-sensitivity-strict-paired-v1/`; the completed
  manifest validates all 30 non-smoke artifacts, strict timestamp ordering,
  disjoint selection/evaluation worlds, and the preregistered method schema.
- Result: all three primary screened-versus-full-candidate contrasts are
  exactly zero across ten paired runs (10 ties; exact and Holm p = 1.000).
  All nine candidate-pool contrasts are also exactly zero. In the 24-arm
  objective-weight family, 23 contrasts are exactly zero; the remaining three
  contrasts (fraction 0.70, risk lambda 0.70) have mean 10.751, 1/9/0
  wins/ties/losses, 95% CI [-13.570, 35.072], and Holm p = 1.000.
- Allowed wording: under this Higgs v3 protocol, GNN screening produced no
  detectable difference from the independent full-decision-graph robust-greedy
  comparator, candidate-pool changes produced no detectable utility change,
  and the preregistered weight sensitivity yielded a robust null result. These
  are protocol-conditional negative findings, not proof of universal
  equivalence or irrelevance.
- Forbidden: claiming GNN screening improves the robust objective, treating
  GNN Top-K as an independent efficacy baseline, claiming universal candidate
  pool or weight invariance, or pooling v3 with v1/v2 statistical families.
