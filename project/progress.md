# Progress Log

## 2026-09-20 SocioPatterns confirmation and publication package

- The frozen r3 confirmation matrix completed all 42 planned conditions under
  its serial resource ceiling. A strengthened validator checks that the
  manifest is `COMPLETE` in addition to the frozen matrix coverage, source
  snapshot, data-hash and world-digest contracts; it returned `PASS`. The v10
  test passed.
- Across all 14 nested `(dataset, path, k)` blocks, full greedy changed its
  ordered sequence at both W=20→80 and W=80→320. Exact full-selection ties
  fell from 80/190 rounds at W=20 to 21/190 at W=320. Degree 2k, 4k and 8k
  exactly matched the same-W full sequence in 0/42, 12/42 and 18/42 conditions
  respectively; held-out evaluation differences had both signs.
- Produced validator-passed descriptive analysis, condition-level CSV and a
  reviewed publication figure in
  `analysis/sociopatterns-resolution-confirmation-v0_2/`. Produced a complete
  English methods-and-reproducibility manuscript, cover-letter draft,
  release inventory and cost-aware venue screen in
  `manuscript/resolution_aware_candidate_truncation_submission_v0_1/`.
- The viable contribution is a selection-resolution reporting protocol for
  candidate-truncated simulated influence maximization. It is not a GNN,
  pruning-algorithm, causal-diffusion or universal-equivalence paper. Current
  publisher information excludes SNAM under the user’s non-OA/¥10,000 ceiling
  because it is fully OA with a £2,290 APC. Applied Intelligence retains a
  subscription/no-APC route but needs final author scope review.

## 2026-09-19 v7 E1 exact-search correctness

- Implemented the isolated v7 exact scorer, deterministic fixed-world IC
  simulator, directed h-hop structural upper bound, per-arm cache, reference
  full greedy search and conservative risk-bound greedy search. The module is
  separate from v6's NumPy/float scoring regime.
- Added six targeted tests and the runnable six-fixture E1 harness. Pytest
  passed 6/6 tests; the audit at `audits/v7_e1_micrograph_check_v0_1.json`
  passed 6,114 structural cases, 165,078 partial upper-bound cases and 288
  full-versus-pruned trajectories, with zero unsafe prunes and zero mismatches.
- Corrected one test expectation: `[0,8]` at risk weight 1 has objective zero,
  so `[0,0,8]` is used for the negative-objective case. This was a test-data
  arithmetic correction, not an algorithm defect.
- Next: document the nearest-method distinctiveness assessment and implement
  the development-only E2 runner. No real-network run or GNN training started.

## 2026-09-19 v7 nearest-method gate

- Completed a targeted original-paper comparison with GCOMB, H-DeepPruner,
  UBLF and ExpGreedy/TOPX; also noted variance-aware IM sample-complexity work.
  The audit is `audits/v7_nearest_method_gate_2026-09-19.md`.
- The review rejects learning-based/adaptive-pool claims as the contribution.
  A narrow difference remains possible for a finite-world, risk-objective,
  non-submodular completion certificate, but the literature check is not yet
  sufficient to call it novel. G0 stays open and real-network E2 is not run.
- Follow-up searches located robust IM Branch-and-Cut and IM presolving/Benders
  work, so the audit explicitly rejects general exact-pruning novelty language.
  This strengthens the decision to keep E2 planned rather than launched.

## 2026-09-20 v7 method-line stop decision

- Ran a directed multi-source literature check for risk-sensitive IM, SAA/fixed
  scenarios and exact/presolving methods. It found several relevant established
  lines and is fully documented in
  `audits/v7_g0_literature_decision_2026-09-20.md`.
- Marked G0 as not passed for a new-algorithm paper. No E2 performance batch or
  GNN training was launched. Next work is a separately versioned evaluation
  study, not a retrofitted v7 method experiment.

## 2026-09-20 candidate-truncation evaluation study design

- Created `protocols/candidate_truncation_evaluation_research_card_v0_1.md`.
  It replaces the method claim with an empirical quality--cost evaluation:
  full greedy, degree/PageRank fixed pools, degree doubling, and a conditional
  reproducible GNN ranker under a standard mean-spread primary task.
- Digg/Higgs are development-only. The design requires at least four newly
  admitted networks for confirmation, fixed selection/evaluation worlds,
  explicit cold-start accounting, preserved failures and a full-search
  feasibility preflight. No experiment or training started while the design
  is being built.

## 2026-09-20 candidate-data admission screen

- Added `protocols/candidate_truncation_data_admission_v0_1.md`. First-party
  SNAP pages verify CollegeMsg and email-Eu-core-temporal semantics and fields,
  but their data-specific terms are not shown. The SNAP BSD software license
  was explicitly rejected as a substitute for data permission.
- No candidate data were downloaded, parsed or executed. Confirmation data
  remain unadmitted pending verifiable use terms or authorization.

## 2026-09-20 outcome-blind local resource preflight

- Implemented `experiments/v8_candidate_truncation_preflight.py` with strict
  timestamp-group history construction, historical endpoint-only graphs,
  deterministic world IDs, input hashes and a no-overwrite output rule. It
  runs only the already-local Digg/Higgs development inputs and writes no seeds,
  scores, ranks or independent-evaluation values.
- Dry runs and serial full-reference preflights passed. Higgs completed 16,960
  candidate-world evaluations in 0.751 seconds; Digg completed 3,140 in 0.057
  seconds. These are resource-only observations, not candidate-truncation
  results. Combined v7/v8 tests passed 8/8.
- Next: freeze a development-only evaluation matrix and implement its runner;
  confirmation execution remains blocked by data admission.

## 2026-09-20 frozen development matrix and diagnostic iteration

- Froze v0.1 as a development-only 12-block/144-execution matrix and completed
  it, then found that its output did not retain raw evaluation spreads, full
  winner margins or ranking positions. It is preserved under
  `audits/candidate-truncation-development-v0_1/` as an implementation
  diagnostic and is not used in analysis.
- Created v0.2 with the missing evidence fields, a no-overwrite serial runner,
  manifest resume integrity, smoke/schema checks and a descriptive-only
  analysis script. Tests passed 15/15; v0.2 completed all 12 blocks/144 method
  executions in 504 seconds without runner errors.
- The readout documents degree-pool variability, poor PageRank pools, an
  expensive Digg doubling case and extensive W=20 full-score ties. Next:
  develop a predeclared selection-world-resolution diagnostic before any
  confirmation study; no claim is yet eligible for a manuscript.

## 2026-09-19 v7 experiment design delivered

- Created the Chinese staged protocol, exact-bound method/proof note, JSON
  settings and per-method planned CSV matrix. E2 has 108 planned executions;
  E3 has 180; E4 has 40. All are unrun; no GNN training was launched.
- Added and ran the standard-library arithmetic design checker: 395,505
  small vector/prefix/lambda cases passed. This checks a proposed bound,
  not empirical performance or production numerical code.
- Method and statistical reviewers checked the design. Incorporated exact
  integer/rational comparison, generic bound and no-SSE controls, a single
  primary total-cost measure, retained-failure resource gates and explicit
  development-threshold fitting order/cost.
- Verified JSON/CSV stage counts, unique rows, disjoint development/formal
  seeds, preflight separation and disabled formal launch status.
- Next: implement E1 scorer/micrographs and close the method-distinctiveness
  check before any formal performance batch.

## 2026-09-19 publication-pivot assessment

- Checked nearest literature and independently verified the v6 first-divergence
  and rank diagnosis from all ten original JSON artifacts, without training.
- Saved a derived diagnostic JSON, a source-labeled pivot evidence note, and
  a research question card with novelty, prototype and independent-validation
  gates plus explicit failure/stop conditions.
- Corrected the earlier readiness framing: evidence-faithful prose is not
  proof of sufficient scientific contribution. Journal positioning remains
  provisional while the proposed pivot is evaluated.

## 2026-09-19 (manuscript integration)

- Added the English six-figure caption/source map and consecutive in-text
  figure placement markers. The selected figures include the v6 Digg failure
  boundary and preserve its non-equivalence and non-superiority limits.

## 2026-09-19 Applied Intelligence full English draft

- Created `manuscript/applied_intelligence_full_draft_v0_1.md`, a complete
  English working manuscript with the revised candidate-reduction title, v5
  feasibility boundary and admitted v6 results. The narrative excludes
  learned-prior superiority, causal/online claims and end-to-end speedup.
- Completed `audits/applied_intelligence_full_draft_audit_2026-09-19.md`.
  Experimental evidence is coherent for the narrow narrative; final reference
  formatting, figures/captions, author-confirmed declarations, lawful archive,
  and current publisher verification remain open. Updated target-specific
  metadata, readiness and strategy records.
- Rechecked the official Applied Intelligence guidance and created a
  target-specific submission checklist. It records the abstract, keyword,
  source/PDF, declarations, data-availability, figure, citation and
  subscription-route requirements, including author confirmation of any
  generative-AI disclosure required by the current journal policy.
- The working abstract contains 235 words and six keywords, satisfying the
  current stated 150--250-word and 4--6-keyword bounds before final typesetting.

## 2026-09-18 v6 formal completion and analysis

- The formal Digg batch completed at 19:45:48 local time. All ten formal seeds
  (74--83) are present in `audits/candidate-reduction-v6-digg-k5-formal/digg/`.
  The post-run read-only validator accepted the complete batch with no errors.
- The first analyzer generated its JSON/CSV then crashed in the native
  Matplotlib renderer (`0xc06d007f`), even after selecting Agg. This did not
  touch study artifacts. Replaced the renderer with a standard-library SVG
  writer and generated the complete fresh analysis bundle at
  `analysis/v6-digg-k5-formal-v3/`; its four v6 tests pass.
- Formal findings: GNN-60 and GNN-120 exactly preserved the full-search result
  in all ten paired blocks; GNN-30 lost in all ten (mean delta -3.499, 95% CI
  [-4.011, -2.987], exact p=0.00195, secondary-family Holm p=0.00586). The
  degree-120 arm also exactly preserved full search. This supports conditional
  candidate reduction and a failure boundary, not GNN superiority over degree.
- Added the bounded English v6 Results/Discussion fragment and a
  publication-evidence audit. The main candidate-reduction line now has its
  planned independent-network and larger-budget validation. Its next work is
  manuscript integration and readiness auditing, not an adaptive search for a
  favourable learned-prior comparison.

## 2026-09-18 v6 preflight validation and formal launch

- User resumed training and delegated the experimental decision process within
  the established evidence boundaries. Added `experiments/validate_v6_digg_k5.py`,
  a read-only schema, provenance, deterministic-world, metric-cross-check and
  resource validator; added its rejection-path test.
- The default `python` resolved to a PyMOL interpreter without pytest. Switched
  to the recorded `C:\\Users\\36024\\Miniconda3\\python.exe`; targeted v5/v6 tests
  passed (8 tests, two Torch deprecation warnings).
- The validator accepted `audits/candidate-reduction-v6-digg-k5-preflight/digg`
  in preflight mode. The full-candidate arm took 227.4050059 seconds and the
  ten-block projection is 2,274.050059 seconds, so the fixed resource gate
  passed. The formal batch is eligible to start from the immutable r1 snapshot.
- Launched the formal seeds 74--83 batch at 18:59:08 local time as PID 13084,
  writing only to `audits/candidate-reduction-v6-digg-k5-formal/digg/` with
  persistent execution logs. An attempted completion-heartbeat update was not
  executed because its automatic approval review disconnected; direct session
  monitoring replaces it.
- Added a conservative formal-only v6 analysis program and a post-run local
  controller. The controller waits for PID 13084 to exit, validates the entire
  batch, and runs analysis only after a passing formal validation; it does not
  launch a new training run or alter any preregistered parameter. v6 unit tests
  passed (4 tests, two Torch deprecation warnings) and both new modules compile.

## 2026-09-18 v6 pause

- The user instructed that training wait until tomorrow. PID 29632 had already
  exited when the pause was applied; its preflight files remain preserved in
  `audits/candidate-reduction-v6-digg-k5-preflight/`. No effect metrics were
  opened or assessed, and no formal v6 experiment was started.
- Paused the v6 completion notification. Work resumes only with a read-only
  schema, provenance, and resource-gate validation.

## 2026-09-18 v6 Digg k=5 launch preparation

- User authorized continued training after the v5 predeclared feasibility stop.
  Wrote a separate v6 protocol rather than altering v5: Digg-only conditional
  simulated selection at k=5, seed-73 preflight, seeds 74--83 formal, fixed
  30/60/120 pools and a weighted-degree reference. Digg remains an inferred
  exposure-proxy network, not causal validation.
- Added an immutable-source snapshot module, snapshot creator, snapshot-only
  runner and two targeted tests. The test suite with the v5 checks passed:
  seven tests, warnings only. The first snapshot-creator invocation stopped
  before output because its direct-script import path omitted the project root;
  this is patched before the one allowed fresh snapshot attempt.
- Created verified v6 source snapshot `digg-k5-v6-20260918-r1`, snapshot ID
  `8e1f2d93f882d5be1cad`, manifest SHA-256
  `797e9863811e0d0587b94e6e25f3286609e3eeac43c8fd1d10f82888d7919c9b`,
  containing 18 files. Snapshot-executed dry run passed and wrote nothing.
  Started the sole seed-73 Digg preflight at 16:13:10 local time, PID 29632,
  with persistent logs in `audits/candidate-reduction-v6-digg-k5-preflight/`.
  No formal v6 output has been created.

## 2026-09-18 non-OA venue transition

- User requested a non-OA or sub-¥10,000 route that meets the school policy.
  Set Applied Intelligence as the working target: its official Springer page
  confirms a hybrid model, no APC for subscription publication, EI Compendex
  and SCIE indexing. The intended submission is a regular Original Paper via
  subscription, not an OA/collection/special-issue route.
- Added `manuscript/applied_intelligence_submission_strategy.md` with the
  scoped paper positioning, required manuscript work and two zero-APC fallback
  journals. Updated the target and readiness records; no submission occurred.

## 2026-09-18 v5 preflight decision

- The hash/schema validator accepted the Higgs seed-62 preflight: one complete
  run artifact and five metrics rows passed integrity validation. This result
  remains non-inferential; no selection/effect fields were examined for the
  decision.
- Its recorded full-candidate arm time was 37,498.606 seconds (10.42 hours),
  exceeding the preregistered 14,400-second limit. Its ten-block projection
  was 104.16 hours versus the 72-hour cap. The v5 protocol consequently blocks
  Digg preflight, every formal seed, and paired analysis. No such artifacts
  were created.
- The first controller stopped from a Windows output-encoding mismatch before
  applying the gate. Updated the external controller's report decoder and
  explicitly set future subprocess output to UTF-8. Nine focused tests passed.
  A separately named controller then verified the Higgs artifact and recorded
  the intended resource-gate stop. The earlier controller lock was renamed,
  not deleted, before the one recovery validation.
- The methods draft must be updated from "preflight is in progress" to the
  observed feasibility limit. v5 cannot contribute formal comparative results;
  it contributes a cost-feasibility boundary only.

## 2026-09-17 v5 execution continuation

- User requested continued experiments and additional data. Prior Higgs PID
  36260 no longer existed, no Python process remained, and the preflight
  directory contained only its protocol copy. Exit cause is unknown.
- Resumed unchanged r2 Higgs preflight at 20:51:34 local time, PID 16584,
  with logs under `audits/candidate-reduction-v5-cost-preflight/execution-logs`.
  No partial result was overwritten and no outcome was inspected.
- Added external serial controller `experiments/continue_v5_candidate_reduction.py`.
  Seven targeted tests passed, including joint 72-hour overrun rejection,
  invalid timings and smoke/incomplete preflight rejection. The frozen source
  snapshot and experimental design remain unchanged.
- Started controller PID 19040 at 20:54:32. Its status is recorded under
  `audits/candidate-reduction-v5-cost-preflight/controller-20260917/`.
  It waits for Higgs, runs Digg preflight, enforces the joint gate, then runs
  both formal batches sequentially and validates before paired analysis.
  Its persistent lock prevents a duplicate controller. Stops require review,
  not automatic reruns or edits to study configuration.
- Drafted `manuscript/v5_experimental_methods_en.md` from the protocol and
  implementation. Formal results remain pending. Included the incomplete
  ranking-cost attribution and post-block time-limit-check qualifications.


## 2026-07-28

- Created the publication-evidence strengthening plan.
- Recorded the completed Digg and Higgs large-scale results and their known
  claim limitations.
- Next: inspect the frozen Higgs run records to explain the RIS tie.
- Confirmed that the split-0.60 seed-42 main and RIS seed sets are identical.
- Next: quantify equality across all split-0.60 runs and inspect RIS code.
- Quantified RIS equality: 10/10 at 0.60; 0/10 at 0.65 and 0.70.
- Identified a below-chance future-edge AUC in the frozen Higgs results.
- Next: create and run a versioned probability-direction audit that does not
  modify frozen study outputs.
- Added `experiments/audit_edge_prediction.py`, a non-destructive audit that
  reports train reconstruction and future-edge AUC/AP/Brier/ECE plus inverted
  score AUC. Its smoke run exactly reproduced the frozen 0.3637 AUC for
  Higgs split 0.60, seed 42, at 10 epochs.
- Environment note: the workspace root is not a Git repository, so a Git
  diff-based workspace audit is unavailable.
- Completed all 30 Higgs edge-prediction audit runs without modifying frozen
  results. Reconciled them against frozen AUC values (maximum raw difference
  `7.45e-05`, caused by stored four-decimal rounding).
- Generated the reviewed strict analysis bundle at
  `analysis/higgs-edge-prediction-audit-v2/`; v1 is retained as the first
  generated figure pass and v2 resolves two visual-overlap issues.
- Completed Phase 1 and started Phase 2: third-dataset admission.
- Screened PHEME (license unverifiable from first-party endpoint) and Stack
  Exchange (licensed fields but non-diffusion reply semantics). Neither was
  admitted; recorded the evidence and rejection reasons in
  `data_cards/third_dataset_admission.md`.
- Generated and validated `reproducibility/frozen-study-manifest-v1.json`:
  both frozen studies have 30 hashed runs, 10 recorded seeds, three hashed
  data inputs, and eight hashed core code files. Phase 3 is now in progress;
  its remaining work is publication-facing performance analysis, contingent
  on the outstanding third-dataset admission decision.
- Generated and visually QA'd `analysis/frozen-main-comparison-v1/`, including
  all 24 paired contrasts, Holm-corrected exact sign-flip tests, and figures
  that preserve the Higgs/RIS 0.60 tie. No frozen experiment output changed.
- Began the next third-dataset screen with Mastodon public reblogs. The
  official API/terms requests timed out before returning verifiable field or
  license evidence, so the candidate remains unadmitted and no data were
  downloaded.
- Screened Hacker News: verified the raw comment-parent/user/time fields from
  its official Firebase endpoint, but rejected it because it is a discussion
  reply tree and no first-party redistribution license was verified.
- Completed the fixed screen: Mastodon and Reddit both timed out at their
  first-party endpoints, so neither was admitted or downloaded. Phase 2 is
  complete with no qualifying third dataset; Phase 3 is complete with the
  reproducibility manifest and two strict analysis bundles. Started Phase 4.
- Wrote `protocols/edge_prediction_v2_preregistration.md` and ran its GPU
  determinism preflight successfully. Next: implement the isolated temporal
  validation pilot for the predeclared candidate configurations, without
  touching v1 code or outputs.
- Completed the temporal-supervision T0 candidate on the isolated Higgs outer
  tests. All numerical prediction and calibration gates passed at fractions
  0.60, 0.65, and 0.70; the reviewed bundle is
  `analysis/edge-prediction-v2-t0-gate-v2/`.
- The calibration figure was visually QA'd and is legible. The first summary
  attempt failed only from a duplicate OpenMP runtime; a process-scoped
  compatibility retry wrote the successful `v2` bundle. The first failed
  output directory remains untouched for audit.
- T0 is deliberately recorded as a conditional fixed candidate because the
  full candidate-selection grid remains incomplete. Next: freeze a separate
  `v2-T0` influence-maximization preregistration before any new run.
- Frozen `protocols/influence_v2_t0_preregistration.md`. It locks temporal
  windows, the full outer-training graph parity rule, inherited v1 optimizer
  settings, statistics, hashes, and claim limits before any v2-T0 output may
  be produced. Next: build an isolated runner and execute only a leakage-safe
  smoke test.
- Added isolated `pipeline_v2_t0.py` and `run_rolling_study_v2_t0.py`;
  compilation and CLI checks passed. The first smoke invocation stopped before
  training because its assumed Higgs input directory had no `nodes.csv`.
  The partial audit directory is retained; next find the exact frozen dataset
  path and retry once in a new audit path.
- Confirmed the frozen Higgs path is `data/processed/higgs-twitter/pilot-50000`.
  Before retrying, strengthened the runner to fail closed unless its three
  input hashes exactly match the frozen Higgs manifest.
- Completed the one-run `v2-T0` smoke test in
  `audits/influence-v2-t0-higgs-50000-smoke-v2/`, then ran
  `summarize_study.py` successfully. It validates the isolated runner and
  hash/protocol chain but supplies no inference at `n=1`.
- The smoke audit found a timestamp tie between calibration and outer-test
  windows. Formal v2-T0 execution is paused before the 30-run batch; next
  write a separately versioned timestamp-grouped v2-T0b protocol and runner.
- Frozen the timestamp-grouped `v2-T0b` protocol. Next implement its isolated
  runner, verify strict boundaries in a one-run smoke test, and only then
  reconsider a formal batch.
- Implemented and ran a read-only timestamp-group boundary audit. All planned
  fractions have strict adjacent time boundaries and negligible achieved-
  fraction deviation. Next: implement the isolated v2-T0b runner.
- Added isolated `pipeline_v2_t0b.py` and `run_rolling_study_v2_t0b.py`.
  They compile and expose the intended CLI. Next: run one strict-timestamp
  Higgs smoke test before a formal batch.
- Started the single v2-T0b strict-timestamp smoke run. The foreground command
  hit the tool timeout while its Python child continued normally; it is being
  monitored and no duplicate run will be launched.
- Started Phase 5 and wrote `manuscript/claim_ledger.md` plus the Chinese
  evidence-bound first draft `manuscript/draft_zh_v0_1.md`. The draft records
  all known limits and deliberately excludes uncompleted v2-T0b outcomes.
- Citation APIs are rate-limited in the current environment. The manuscript
  therefore retains explicit bibliography placeholders instead of unverified
  or memory-generated references.
- CrossRef and Semantic Scholar later jointly verified Kempe, Kleinberg, and
  Tardos (KDD 2003, DOI 10.1145/956750.956769). Its CrossRef-derived BibTeX is
  now the first entry in `manuscript/references.bib`; no other unverified
  citation was added.
- Added `manuscript/submission_readiness.md` to distinguish the current draft
  from a submission-ready core-journal package and enumerate the remaining
  evidence, bibliography, and venue-format gates.
- A monitor command had a mistyped workdir and did not execute; the formal
  batch itself was not interrupted or modified.
- The formal v2-T0b batch completed its first run at split 0.60/seed 42. The
  strict boundary audit in that result passed and stderr remains empty. The
  process has advanced to subsequent runs; no partial outcome is reported as a
  paper finding.
- Completed strict v2-T0b fraction-0.60/seed-42 smoke testing, including its
  manifest and `summarize_study.py` aggregation. Strict timestamp separation
  and frozen-input verification passed. Next: start the independently versioned
  30-run formal Higgs v2-T0b batch.
- Started the formal 30-run Higgs v2-T0b batch in
  `results/large-robust-greedy-higgs-50000-v2-t0b/`. It writes separate stdout
  and stderr logs under `logs/`; the v1 results remain untouched.

## 2026-07-29 (continued)

- Resumed the autonomous publication workflow. Formal v2-T0b process PID
  51324 remains active, with 1/30 result artifacts and an empty stderr log.
  No result, configuration, or manuscript claim was changed while the batch
  remains incomplete.
- Began a citation audit for the GATv2 architecture. An OpenAlex title query
  failed because the literal question mark was treated as a wildcard; no
  citation was added. The retry will use a direct arXiv identifier and an
  independent metadata source.
- The direct GATv2 verification did not obtain two usable sources: arXiv XML
  parsing failed, Crossref returned 404, Semantic Scholar returned 429, and
  OpenAlex returned no usable record fields. The bibliography remains
  unchanged; no citation was synthesized from memory.
- Corrected the C4 ledger constraint: the strict v2-T0b smoke test passed;
  the incomplete 30-run formal batch, not the smoke test, is excluded from
  manuscript evidence.
- Audited the frozen comparison report against the draft and added a compact
  six-row, 24-contrast table of paired robust-objective mean differences.
  The table retains the Higgs/RIS 0.60 exact tie and states the scope of the
  protocol-level repeated-run inference.
- Verified the GATv2 architecture citation through matching arXiv and DBLP
  records, then retrieved the exact BibTeX from the DBLP official mirror.
  Added only this architectural attribution and logged its scope in
  `manuscript/citation_audit.md`.
- Began an RIS/IMM baseline-citation audit. The first DBLP title query returned
  HTTP 503, so no result or bibliography entry was added; use a different
  metadata index for the next attempt.
- Completed the RIS/IMM citation audit using matching Crossref and DBLP-mirror
  records, then added the DOI-exported BibTeX and a method-scope paragraph.
  The manuscript now limits RIS statements to the frozen budget-constrained
  comparison implementation.
- Added `reproducibility/README.md`, which distinguishes read-only frozen v1
  integrity verification from the authorized post-completion v2-T0b summary
  command and links every manuscript claim type to its evidence artifact.
- Corrected the v2-T0b README after source inspection: frozen input hashes are
  emitted in the final batch-level manifest, while strict timestamp windows
  are recorded in individual run artifacts.
- Added a self-contained related-work section to the Chinese draft using only
  the three audited citations, and renumbered later sections consistently.
- Integrated three existing, visually reviewed analysis figures into the draft
  with evidence-bound captions: frozen paired comparisons, v1 future-AUC
  instability, and T0 outer-test AUC. No figure or experiment output changed.
- Audited the local source metadata before adding dataset references. It
  confirms that Higgs has no raw topic-level cascade IDs and that Digg parent
  links are inferred exposure proxies; these limitations remain in the draft.
- Added audited Higgs and Digg source citations, including DOI-exported
  BibTeX. The data paragraph now states the observed Higgs activity fields and
  retains both datasets' semantic limits.
- Formal v2-T0b batch monitor: 4/30 artifacts are complete for the 0.60
  fraction (seeds 42--45), stderr remains empty, and the latest artifact
  confirms strict calibration-to-outer-test ordering. No partial result was
  added to manuscript claims.
- Updated submission readiness to record five audited foundational/dataset
  citations while keeping broader related-work coverage and target-journal
  formatting as explicit outstanding gates.
- Community-detection citation verification remains incomplete: Crossref and
  DOI BibTeX were available, but APS was Cloudflare-blocked and OpenAlex
  returned no usable record. No unaudited citation was added.
- Added a data-and-code availability section. It distinguishes the existing
  hash-based reproducibility package from a future public source archive and
  preserves the no-raw-redistribution constraint.
- Retrieved the official *Software Journal* (软件学报) author guide and
  recorded it as the working target in `manuscript/venue_selection.md`.
  The guide confirms topic fit but requires a thorough comparison with both
  domestic and international work; the current five audited entries are not
  enough. Template conversion remains blocked until the formal v2-T0b
  statistics and bibliography gates are complete.
- Formal v2-T0b monitor: 5/30 artifacts are complete through split 0.60,
  seed 46; strict calibration-to-outer-test ordering persists and stderr is
  empty. Seed 46 records a long wall-clock duration, while the active process
  continues to accumulate CPU time. No partial performance result was used.
- Completed a read-only manuscript-to-code consistency audit for the frozen
  v1 studies. The eight recorded core-source hashes and all 60 recorded run
  artifacts match the reproducibility manifest; the manuscript now states the
  implemented Monte Carlo, optimization, and protocol constants. Incomplete
  v2-T0b artifacts remain excluded from all performance claims.
- Added a dual-source-audited risk-aware influence-maximization reference
  (NasehiMoghaddam et al., 2022) to the manuscript, BibTeX file, citation
  audit, and related-work matrix. It is used only to establish risk aversion
  as a related problem framing; no cross-paper objective or performance claim
  was introduced.
- Added a dual-source-audited robust influence-maximization reference (He and
  Kempe, 2016) under the same bounded-use rule. The related-work comparison
  now explicitly prevents the shared label “robust” from implying the same
  uncertainty source, objective, or guarantee.
- Completed an editorial readiness audit against the claim ledger and the
  working core-journal target. The narrative, results, and limitations remain
  internally aligned; formal v2-T0b statistics, fuller literature review,
  reproducibility-appendix details, template rendering, and a lawful public
  archive remain explicit submission gates.
- Added a reproducibility appendix from the frozen manifest, preregistration,
  deterministic preflight, and implementation. It records validated versions,
  protocol constants, seed settings, and the explicit absence of GPU/CPU model
  and total-runtime metadata; it does not create a cross-hardware claim.
- Formal v2-T0b monitor: 6/30 artifacts are complete through fraction 0.60,
  seed 47. The new artifact retains strict calibration-to-outer-test timestamp
  ordering and the achieved outer-training fraction 0.599961; stderr remains
  empty. This is progress only, not a performance result.
- Added a manuscript statistical appendix that exposes all 24 frozen paired
  contrasts, their intervals, exact and Holm-adjusted p-values, win/tie/loss
  counts, and paired effect sizes. The exact Higgs/RIS 0.60 tie is preserved
  as a full table row.
- Verified the statistical-appendix transcription against all 24 records in
  `paired_comparisons.json`; every displayed value matches at the source
  report's stated precision.
- Completed read-only visual QA for all three manuscript figures. They are
  legible at their recorded dimensions; Figure 1's zero-height Higgs/RIS bar
  must remain explicitly disclosed by caption and Appendix B. Any Chinese
  presentation derivative is deferred and must not overwrite frozen figures.
- Added a dual-source-audited dynamic-social-network influence-maximization
  citation (Zhuang et al., 2013). The manuscript uses it only to situate an
  adjacent dynamic-network problem setting; it makes no claim of matching
  temporal split, objective, data, or performance.
- Added a controlled English title, abstract, and keyword set plus a bilingual
  terminology ledger. The translation preserves all claim-ledger constraints,
  including the Higgs/RIS tie and the exclusion of incomplete v2-T0b results.
- Added a source-mapped pseudocode appendix for GNN-guided robust greedy
  selection. It exposes candidate ordering, common-random-stream evaluation,
  greedy tie handling, and the protected GNN Top-K fallback without claiming a
  global optimum.
- Completed a read-only protocol audit across all six completed v2-T0b
  artifacts. Every file matches the strict timestamp, method, common-random,
  and frozen-constant invariants; the batch remains incomplete and no
  performance value was used.
- Generated `manuscript/temporal_key_user_identification_internal_draft.docx`
  from the evidence-bounded manuscript, figures, and appendices. Its headings,
  tables, three images, and image alternative text pass structural/a11y audits.
  LibreOffice is unavailable in the workspace, so required render-based visual
  QA remains incomplete; the file is an internal review draft, not an official
  journal-template submission.
- Added two evidence-bounded related-work citations: Kumar et al. (2022) for
  graph-embedding/GNN influence maximization, and Lin et al. (2026, online
  first in *Software Journal*) for differentiated graph embeddings in
  multilayer social-network influence maximization. Their metadata and source
  exports are audited in `manuscript/citation_audit.md`; neither supplies a
  cross-paper performance comparison or supports the manuscript's result
  claims.
- Added `manuscript/related_work_matrix.md`, which compares the verified
  survey, international GNN/embedding work, domestic multilayer work, and the
  present study without treating unreported features as absent or comparing
  cross-paper scores. The matrix records the remaining literature and
  full-text-audit gates required by the target journal.
- Added two strictly scoped related-work citations for a time-restricted IC
  model and community-structure influence identification. The manuscript and
  comparison matrix explicitly distinguish these models from the present
  timestamp-split, risk-penalized objective and contain no cross-paper score
  comparison.
- Added Murata and Koga (2018) as a dual-source-verified international
  dynamic-influence-maximization comparison point. Its use is limited to an
  adjacent-topic distinction; it supplies no cross-paper result or protocol
  claim.
- Completed `audits/core_journal_manuscript_quality_audit_2026-07-29.md`.
  The Chinese draft remains internally aligned with C1--C4, and the audit
  explicitly retains the open v2-T0b statistics, full-text literature,
  official-template, render-QA, and source-archive gates.
- Added two dual-source-verified domestic Software Journal references: Han et
  al. (2017) scopes node-influence analysis as a review, while Shan et al.
  (2017) supplies an adjacent overlapping-community selection setting. The
  updated matrix preserves their non-equivalence to the present objective and
  protocol.
- Updated the in-flight v2-T0b protocol audit to 7/30 artifacts. Seeds 42--48
  all preserve the strict calibration-to-outer-test ordering, fixed settings,
  method identifier, and common-random evaluation protocol; partial outcomes
  remain excluded from every manuscript claim.
- Added `manuscript/innovation_evidence_matrix.md` to constrain contribution
  wording to the audited combination and protocol. It prohibits unsupported
  first-of-kind and global-optimality claims and preserves the v2-T0b evidence
  gate.
- Added the dual-source-verified Li et al. (2020) community-diversified
  influence-maximization citation. Its use is deliberately metadata/title
  scoped because the full text could not be audited from this environment;
  the draft, BibTeX, citation audit, and related-work matrix now contain 17
  consistent references.
- Rebuilt the internal DOCX after the seventeenth citation was added. Its
  structural audit records 19 Heading-1 and 10 Heading-2 paragraphs, while
  the accessibility audit reports zero findings; text extraction confirms the
  new citation is present. Render QA remains blocked by the absent
  LibreOffice/soffice executable, so this remains an internal rather than
  template-validated manuscript artifact.
- Added a deliberately unfilled submission-metadata intake sheet after
  confirming that no verified author, affiliation, funding, correspondence,
  disclosure, or archive information is present in the workspace. This
  prevents invented metadata from entering a future official-template file.
- Tightened the fourth contribution statement from "publish" to "provide
  auditable records" so it does not contradict the explicit statement that a
  public archival code snapshot has not yet been established.
- Added explicit test questions at the start of both results subsections. They
  distinguish the frozen paired optimization question from the independent
  temporal-prediction audit without changing reported statistics or claims.
- Added Yadav et al. (2016) as a dual-source-verified, full-text-inspected
  dynamic-uncertainty comparison point. The manuscript distinguishes its
  feedback-driven sequential intervention setting from the present fixed-$k$,
  pre-windowed, non-adaptive protocol; all reference records now contain 18
  consistent entries.
- Updated the read-only v2-T0b protocol audit to nine artifacts (seeds 42--50
  at fraction 0.60). All checked protocol invariants pass; these partial files
  remain excluded from manuscript performance claims.
- Read both newly added domestic Software Journal PDFs. Their full-text-backed
  comparison rows now distinguish a field review from an overlapping-community,
  feedback-driven batch-selection method; neither is equated with the present
  fixed Top-K risk-coverage protocol or its outcomes.
- Located and HTTP-verified the official Software Journal formatting sample
  (`软件学报排版样例2025年版.doc`). This is a discovery preflight only; final
  template conversion remains gated on completed formal statistics, literature
  coverage, and a fresh template download check.
- Confirmed and terminated only the orphaned `WINWORD.EXE /Automation
  -Embedding` process (PID 43304) left by the prior timed-out internal-DOCX
  export attempt. The formal v2-T0b Python process was not touched. A fresh
  environment probe still finds no LibreOffice/soffice or alternate
  reproducible DOCX renderer, so visual render QA remains an explicit pending
  gate rather than a passed check.
- Added two dual-source-audited international related-work records:
  Yanchenko et al. (2023) for ex ante temporal-network influence maximization
  and Biswas et al. (2023) for aleatory/epistemic uncertainty in robust
  influence maximization. The new prose is deliberately restricted to their
  verified title/abstract scopes; the former's open PDF download was truncated
  and the latter has no inspected open full text, so neither supports a
  feature-level or cross-paper performance claim.
- Rebuilt `manuscript/temporal_key_user_identification_internal_draft.docx`
  after the literature update. The new structural audit records 19 Heading-1,
  10 Heading-2, and three inline images; the refreshed accessibility audit
  reports zero high, medium, or low findings. Visual render QA remains pending
  because no reproducible DOCX renderer is available in the workspace.
- Removed workspace-path-style cross-references from the manuscript body and
  appendices, replacing them with publication-facing appendix and artifact
  descriptions. Added the audited fixed-T0 configuration to the temporal
  validation method paragraph, explicitly retaining its non-optimal-candidate
  boundary. The rebuilt internal DOCX contains no local path tokens and its
  refreshed accessibility audit again reports zero findings.
- Refreshed the core-journal quality audit after the literature and editorial
  updates. It now records 20 audited references, the fixed-T0 configuration,
  and path-free journal-facing prose, while preserving the open full-text,
  formal-statistics, template, render, archive, and author-metadata gates.
- Added `experiments/build_v2_t0b_paired_analysis.py` for the post-completion
  v2-T0b evidence gate. It is a separate-output analysis builder with strict
  guards for all 30 preregistered runs, the batch manifest, seven methods,
  strict timestamp ordering, and common-random evaluation. Syntax and
  incomplete-study rejection were tested; it produced no output directory
  from the current partial study.
- Formal v2-T0b reached 10/30 artifacts, completing its fraction-0.60 seed
  block (42--51). A read-only protocol audit confirms all ten files retain the
  strict timestamp boundary, reference method, common-random evaluation, and
  frozen constants. This is execution consistency only; no partial metric or
  performance conclusion has been added to the manuscript.
- Corrected the v2-T0b paired-analysis guard to compare the batch manifest's
  actual `.json` filename keys rather than bare run IDs. The existing v2-T0b
  smoke manifest and its seven-method metrics table confirm the contract;
  the analysis builder retains its 30-run completion requirement.
- Added the dual-source-verified, official-full-text-inspected DeepSN AAAI
  2025 reference as a constrained GNN influence-maximization comparison.
  The updated manuscript, bibliography, citation audit, and comparison matrix
  now contain 21 audited references. The internal DOCX predates this added
  reference and is explicitly queued for rebuild and visual QA only after its
  Word window is idle; no document was overwritten during active use.
- Read the complete official 19-page Software Journal PDF for the existing
  Lin et al. (2026) domestic comparison citation. The citation audit and
  comparison matrix now record its multilayer, intra-/inter-layer diffusion,
  and adaptive-local-aggregation scope, while the manuscript keeps the
  comparison non-numerical and distinct from the present single-layer,
  time-windowed risk-coverage protocol.
- Hardened `experiments/build_v2_t0b_paired_analysis.py` before formal-batch
  completion. It now verifies every manifest hash, frozen configuration,
  timestamp/CRN/probability-protocol invariant, and metric-table value against
  its source run artifact. Temporary complete-study fixtures pass; deliberate
  hash, configuration, and metric-table mismatches are rejected. The partial
  formal study remains excluded and generated no analysis output.
- Added Tang et al. (2024), a dual-source-verified and official-full-text-
  inspected adaptive GNN influence-maximization comparison. The manuscript,
  bibliography, citation audit, and matrix now contain 22 audited references;
  prose distinguishes its feedback-driven multi-round adaptive ATGCN policy
  from the present fixed-$k$, time-windowed, non-adaptive protocol without
  making a cross-paper numerical claim.
- Added a publication-facing related-work comparison table to the Chinese
  draft. It compresses five full-text-audited domestic and international
  neighboring settings against the present protocol by decision information,
  representation/optimization, and boundary; it contains no cross-paper
  numerical comparison or unsupported feature claim.
- Rebuilt the internal DOCX after Word became idle, incorporating reference
  [22] and the related-work comparison table. Heading, image, section, and
  accessibility audits pass; `render_docx.py` cannot start because this
  environment still lacks LibreOffice/soffice, so visual page QA remains open.
- Captured a standalone v2-T0b local environment record with the active
  interpreter, package versions, CUDA visibility, formal invocation, and
  hashes of the dependency declarations, protocol, and runner. A lawful public
  archive and raw-data license verification remain separate open gates.

## 2026-07-31 continuation

- Restored the persistent plan and corrected its stale v2-T0b running state:
  the strict study is complete and its completed 18-contrast Holm analysis is
  now the controlling result boundary.
- Added audited reference [30] (Han et al., partial-community probing in a
  dynamic online social network) at title/abstract scope only. CrossRef and
  Semantic Scholar metadata agree; the expected author-manuscript PDF URL
  returned HTML, so no full-text claim was introduced.
- Rebuilt `manuscript/temporal_key_user_identification_internal_draft_r32_v2t0b.docx`.
  It has 30 reference paragraphs, 5 inline figures, no missing-figure marker,
  and zero high/medium/low accessibility findings. `render_docx.py` failed as
  expected because `soffice` is not installed; visual QA remains open.
- Full-text access retries for Liu et al. (2024) and Qin et al. (2022) were
  nonproductive: both returned HTML rather than PDF, with MDPI additionally
  closing the TLS session on its direct endpoint. Their existing title/abstract
  evidence boundaries remain unchanged.
- Renderer discovery found Word and WPS installations but no LibreOffice or
  comparable headless converter. WPS has active user documents and will not be
  used. The next visual-QA attempt will use only a watchdog-bounded, hidden
  Word COM subprocess and a temporary output path.
- Inspected all 21 controlled Word-rendered r32 pages. Other than the raw
  Markdown-LaTex expressions, figures, tables, reference list, appendices,
  headers, and footers are legible without overlap or truncation. The raw
  expressions occur on pages 5, 7, 16, and 21. The r33 builder-fix task is now
  active; no experiment or result artifact was modified.
- Built r33 and passed py_compile, structural, OOXML-token, and accessibility
  checks. Hidden Word exported r33 to PDF within 14 seconds and exited cleanly;
  no WPS process was accessed. The first rasterization attempt failed because
  `pdftoppm` could not resolve the Unicode workspace path, so the next attempt
  uses an isolated ASCII temporary copy.
- The same `pdftoppm` failure recurred from the ASCII temporary copy. This
  confirms a local renderer problem rather than a Unicode-path issue; no third
  retry will be made with that executable.
- Installed PyMuPDF only under `tmp/qa_python_deps` and used it to render the
  controlled Word-exported r33 PDF. Pages 1--10 have been inspected at full
  page resolution: the previous objective and inline-constant LaTex defects
  are corrected, with no new layout, clipping, or table/figure issue found.
- Completed r33 visual QA across pages 1--21. The exponent and algorithm-input
  defects are corrected; no raw LaTex, clipping, overlap, missing glyph, or
  broken table/figure geometry remains. Updated the readiness record and plan:
  r33 is the current internally QA-passed draft, while author metadata,
  archive/licence, literature-depth, and official-template gates remain open.
- Began the next bounded literature screen using the mandated multi-source
  fallback. The first OpenAlex command failed while printing a non-GBK author
  character, and one returned relevance pool was visibly off topic; no result
  was retained. A single UTF-8, narrower-query retry is queued.
- The UTF-8 retry identified Yang et al. (2024), *Influence Maximization in
  Temporal Social Networks with the Mixed K-Shell Method*, as a new candidate.
  OpenAlex and CrossRef agree on DOI `10.3390/electronics13132533`; CrossRef
  records a CC BY 4.0 licence. The first public-PDF request returned HTTP 403,
  so no full-text comparison or manuscript change has been admitted.
- The sole alternate-client retry for Yang et al. also returned HTTP 403.
  Per the failure rule, that path is closed: the article is retained only as an
  external metadata-screen record and has not been cited or used in the draft.

- Completed a read-only audit of `results/fair-rolling-higgs-pilot-5000-v2/`.
  It is a 5,000-node, 15-run pilot (three fractions and seeds 42--46), not a
  protocol-compatible extension of the strict 50,000-node v2-T0b evidence.
  It has no frozen input/source manifest or timestamp-grouped protocol, uses
  an older ACO-like comparator, and has one below-chance calibration AUC in
  each fraction (means 0.5648, 0.5716, and 0.5484). It is formally excluded
  from manuscript evidence and does not provide an independent robust-objective
  comparator.
- Estimated the cost of the necessary objective ablation from the strict
  v2-T0b artifacts: 30 runs consumed 44.22 recorded runtime hours (mean 88.44
  minutes; median 32.35 minutes; one 942.21-minute outlier). A minimum three
  additional full arms would require about 133 recorded runtime hours serially.
  The preregistered v2-T0c runner passed syntax and dry-run verification of
  all frozen inputs and 30 v2-T0b reference artifacts. The three-arm batch
  started at 2026-07-31 13:51 local time under
  `results/large-robust-greedy-higgs-50000-v2-t0c-objective-ablation/`, with
  independent stdout/stderr logs in `logs/`; it begins with `risk_off` and
  has not modified an existing experiment directory.
- Stopped v2-T0c after its first artifact exposed a cross-process evaluation
  defect: it selected the archived v2-T0b users and used the same strict
  windows, but re-evaluation produced 2318.972 rather than 2433.104. Python
  set traversal changed the random-stream consumption. The incomplete v2-T0c
  directory is preserved as an invalid infrastructure audit, not evidence.
- v2-T0d replaces it with one T0 fit per fraction-seed pair and four selections
  from that common probability map. It uses canonical, deterministic edge-time
  diffusion worlds. Its non-writing 0.60/42 smoke test passed strict ordering,
  produced every arm, and matched the archived full seed set. The formal batch
  started at 2026-07-31 14:09 in
  `results/large-robust-greedy-higgs-50000-v2-t0d-common-world-objective-ablation/`.

## 2026-08-15 publication-strengthening implementation

- Restored the persistent plan and began Phase 7. The requested target remains
  *Software Journal* (软件学报); frozen v1, v2-T0b, v2-T0c, and v2-T0d outputs
  remain outside the v3 write scope.
- The workspace root is not a Git repository, so v3 will use explicit SHA-256
  manifests for sources, inputs, protocols, and run artifacts. A prior command
  confirmed this limitation; no experiment state changed.
- Inspected the v2-T0b runner and optimizer. v3 will make selection and held-out
  evaluation random-world streams explicit and will add a full-candidate
  robust-greedy comparator plus candidate-pool and objective-weight sensitivity
  arms under a new preregistration.
- The v3 source compiles and its dry-run passed frozen Higgs input-hash and
  strict timestamp-window checks without writing output. The first foreground
  smoke exceeded the terminal's 64-second limit before it produced a run JSON;
  its audit directory contains only the copied protocol and will be resumed by
  one monitored hidden process rather than overwritten.
- The original smoke child completed in the new audit directory. It recorded
  strict timestamp ordering, separate selection/evaluation-world digests, the
  protected GNN lower-bound label, and `not_eligible_for_inference: true`.
  A later duplicate resume process was identified by PID and stopped before it
  could write an artifact; the original process was left intact.
- Added a v3 strict-analysis builder. It compiles and rejects the smoke
  directory without creating an analysis output, as required. Completed v3
  analysis remains blocked until a non-smoke, 30-run full-candidate batch exists.
- Created a separate v2-T0d exact-null matrix analysis directory. The new 3x3
  figure and table render every frozen contrast as `0.000`, `10 ties`, and
  `Holm p=1.000`; the old v2-T0d analysis was not modified.
- Corrected the English abstract to remove GNN Top-K as an independent efficacy
  comparator and added a v3 evidence-integration note plus claim-ledger gate.
- The v3 cost preflight verified frozen inputs and computed 1,424,860 diffusion
  calls per run and 42,745,800 calls for the complete 30-run batch. The formal
  batch was launched on 2026-08-15 in
  `results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity/`, with
  separate stdout and stderr logs in `logs/`. It remains a running protocol
  execution, not evidence, until all 30 artifacts pass strict analysis. A
  third-dataset v3 screening protocol was also added; no new dataset or
  citation was admitted.
- Built `manuscript/temporal_key_user_identification_internal_draft_r38_v3_protocol.docx`.
  Its structural inspection found 22 Heading-1 paragraphs, 12 Heading-2
  paragraphs, six inline figures, one portrait US-letter section with one-inch
  margins, and zero high/medium/low accessibility findings. LibreOffice is
  unavailable; a watchdog-bounded hidden Word export was attempted but did not
  return within 90 seconds and was terminated. r38 was superseded by the later
  r39 internal draft, whose controlled Word export and page-level visual QA are
  recorded separately.
- Added and exercised the read-only `experiments/monitor_v3_fairness_sensitivity.py`
  status auditor. At the first formal checkpoint it reports 1/30 complete,
  no integrity issues, no stderr output, and no manifest yet; it does not write
  to the study directory.
- The repository regression suite remains green after the v3 additions:
  `python -m pytest -q` reports 8 passed (55 dependency deprecation warnings).
- Added Li et al. (2023), *A Survey on Influence Maximization: From an
  ML-Based Combinatorial Optimization*, after Crossref and Semantic Scholar
  DOI-metadata agreement. Its Semantic Scholar abstract supports only a
  title/abstract-scoped learning-based-IM survey context; no temporal,
  objective, data, or cross-paper performance claim was added.
- Rebuilt `manuscript/temporal_key_user_identification_internal_draft_r39_ml_survey_update.docx`.
  It has 31 numbered references, 22 Heading-1 paragraphs, 12 Heading-2
  paragraphs, six inline figures, five tables, one section, and zero
  high/medium/low accessibility findings. The canonical document renderer
  cannot start because `soffice` is absent; controlled Word/PyMuPDF visual QA
  is recorded in the dedicated r39 audit, and the draft is not an official
  journal-template submission file.
- A hidden Word COM export of r39 completed within the watchdog, and all 23
  PyMuPDF-rendered pages were inspected. The controlled visual QA found no
  clipping, overlap, missing glyph, broken table/figure geometry, or raw LaTeX;
  the audit is recorded in
  `audits/manuscript_qa_r39_ml_survey_update_2026-08-15.md`. This closes the
  internal-draft visual gate only; official-template conversion remains open.
- The v3 read-only monitor reached its second formal artifact at 2026-08-15
  (`split-0.60-seed-42` and `split-0.60-seed-43`, 2/30 total). Both pass the
  formal-artifact integrity checks; stderr remains empty and no partial
  performance or statistical result is reported.
- Added `experiments/build_public_release_inventory.py`, an inventory-only
  release gate that requires an accepted 30-run v3 study and strict analysis
  bundle before it hashes an explicit author-approved allowlist. It rejects
  raw/processed data, result directories, logs, and workspace-private paths.
  It compiles, and its smoke-study rejection test exits without creating an
  output directory.
- Revalidated the v3 execution gate at the 2026-08-15 checkpoint: the
  read-only monitor reports 2/30 formal artifacts, no integrity issues, empty
  stderr, and no final manifest. The repository regression suite remains
  green (`8 passed`); all new v3 and release-inventory scripts compile; and
  the strict v3 analysis builder rejects the smoke directory without creating
  `tmp/v3-analysis-smoke-rejection-check`. No partial performance conclusion
  is authorized.
- Added Meena, Singh, and Singh (2025 online / 2026 issue) after Crossref and
  OpenAlex metadata agreement and source-retrieved Crossref BibTeX. The entry
  is restricted to title/metadata-level temporal-fairness context; no method,
  dataset, objective, or outcome equivalence is claimed. Rebuilt the internal
  manuscript as r40 with 32 numbered references. Structural and accessibility
  checks passed (22 Heading-1, 12 Heading-2, 6 figures, 5 tables, zero
  high/medium/low findings); the standard renderer lacks `soffice`, so a
  controlled Word-to-PDF export plus Poppler page inspection reviewed all 23
  pages without a layout defect. The r40 document remains an internal draft,
  not an official journal-template submission.
- The v3 monitor subsequently reached 3/30 formal artifacts. The process is
  still running, the final manifest is absent, stderr is empty, and all
  integrity checks pass; the batch remains ineligible for performance or
  statistical claims.
- Corrected the v3 evidence-integration note and submission-readiness index:
  the three verified formal artifacts are execution-status evidence only, and
  the r40 manuscript contains no v3 performance result. The v3 protocol
  remains a separate preregistration until the complete manifest passes its
  strict analysis builder.
- A read-only schema audit of the three completed v3 artifacts passed: each
  records the full 33,529-node decision graph, the 120-node screened pool,
  all four candidate-pool arms, all nine objective-weight arms, distinct
  selection/evaluation world digests, and the required v3 method names. This
  is protocol-integrity evidence only, not a performance result.

## 2026-08-15 continuation

- Rechecked the formal v3 monitor: the batch remains at 3/30 artifacts, PID
  41732 is responsive with increasing CPU time, stderr is empty, integrity
  issues are absent, and no final manifest has been written. No partial
  performance or inferential statistic was admitted.
- Ran the repository regression suite after the publication-strengthening
  changes: `python -m pytest -q` passed 8 tests (55 dependency deprecation
  warnings). The v3 strict analysis and public-release inventory gates remain
  intentionally unrun on the partial study; the smoke rejection contract is
  already recorded.
- Confirmed the current r40 internal manuscript, claim ledger, related-work
  matrix, and submission-readiness record agree on the v3 evidence boundary.
  Official-template conversion, author metadata, archive/licence decisions,
  and final v3 statistical integration remain gated dependencies.
- Strengthened `experiments/build_v3_fairness_sensitivity_analysis.py` so the
  accepted analysis bundle will also report held-out mean spread, spread
  standard deviation, community coverage, selection time, full-candidate
  Jaccard overlap, base-screened Jaccard overlap, and distinct selected Top-K
  sets. The builder independently recomputes and checks the recorded overlap
  fields from each run JSON; the public-release gate now requires both new
  descriptive outputs.
- Verified the new analysis contracts: both source files compile; the smoke
  analysis and partial-study release inventory reject without creating output;
  the descriptive fixture produces 48 rows; and all three existing formal
  v3 artifacts pass the overlap cross-check. No experiment output changed.
- Added `tests/test_v3_analysis.py` for the new descriptive-statistics and
  Jaccard contracts. The complete regression suite now passes 10 tests (55
  dependency deprecation warnings).
- Added `experiments/audit_submission_package.py`, a conservative final gate
  that checks citation numbering, claim-boundary wording, accepted v3
  evidence, author metadata, release inventory, fresh template verification,
  final DOCX, and page-level visual QA. Its 2026-08-15 precheck correctly
  passes the first two gates and reports the remaining six as open; it never
  writes to study or result directories.
- Added `tests/test_submission_package_audit.py`. The first collection run
  exposed a module-import path issue, which was fixed by adding the local
  experiments directory to the import path. The full regression suite now
  passes 12 tests (55 dependency deprecation warnings).
- Rechecked the third-dataset gate using the actual
  `data_cards/third_dataset_v3_screening_protocol.md` path. The prior fixed
  candidate screen remains valid: no data source meets all license, stable-ID,
  strict-timestamp, observed re-propagation-parent, and semantic criteria, so
  the manuscript remains scoped to two datasets. The initially assumed
  `protocols/third_dataset_v3_admission_screen.md` path was absent; no data or
  experiment state changed, and the corrected path is recorded in findings.
- Audited the pending v3 strict-analysis builder against its preregistered
  contrast directions. Corrected two sensitivity-figure labels: both paired
  families calculate the base configuration minus the comparison arm, so the
  candidate-pool plot now reads `120-pool` and the weight-grid colorbar now
  reads `Base minus weight-arm`. This changes only future analysis display
  labels, not v3 protocol, models, or experiment output. The builder compiles
  and the full repository test suite remains green (`12 passed`, with the
  existing 55 third-party deprecation warnings).
- Added `reproducibility/environment-record-v3-fairness-sensitivity-2026-08-15.md`
  while formal v3 PID 41732 was active. It records the active interpreter,
  process invocation, platform, package versions, CUDA/GPU visibility, and a
  source/protocol/dependency hash snapshot outside the study directory. The
  final manifest must still reconcile those hashes and all 30 run artifacts;
  this sidecar neither changes experiment output nor substitutes for the
  manifest.
- Strengthened `experiments/audit_submission_package.py` with a v3 runtime
  reconciliation gate. It now requires the environment-sidecar hash table to
  agree with the accepted final manifest's protocol and four archived source
  hashes. The new fixture covers a matching-manifest pass; the complete test
  suite passes (`13 passed`, with the existing 55 third-party deprecation
  warnings). The new v5 precheck correctly leaves the reconciliation gate open
  until the running study creates its final manifest.
- Added a negative test for v3 environment reconciliation: a deliberately
  mismatched final-manifest source hash is rejected. The v3 batch reached
  `4/30` formal artifacts during this checkpoint; all four pass the monitor's
  integrity checks, stderr remains empty, and no analysis result is admitted.
- Added release-inventory regression tests that reject an experiment-results
  path and parent-directory traversal. The tests exposed a command-line-only
  import defect in `build_public_release_inventory.py`; adding its local
  `experiments` path makes the same v3 validator available when imported by
  the audit suite. The full repository suite now passes `15` tests (the
  existing 55 third-party deprecation warnings remain).
- On 2026-08-16, the formal v3 batch reached 23/30 artifacts and entered its
  final 0.70-fraction seed block. The read-only monitor reports no integrity
  issue, no final manifest yet, an empty stderr log, and an active process;
  this is execution progress only and authorizes no performance or statistical
  conclusion.
- On 2026-08-17, the formal v3 batch completed all 30 non-smoke artifacts and
  wrote its manifest and metrics table without stderr errors. The strict
  builder accepted the study and wrote
  `analysis/v3-fairness-sensitivity-strict-paired-v1/`. The primary fairness
  family and all candidate-pool contrasts are exact nulls (10 ties, Holm
  p=1.000); 23/24 weight contrasts are exact nulls and the remaining three
  are Holm-nonsignificant (mean 10.751, 95% CI [-13.570, 35.072], W/T/L
  1/9/0, Holm p=1.000). No v3 result was pooled with frozen v1/v2 families.
- Integrated the completed v3 negative findings into `manuscript/claim_ledger.md`,
  the Chinese Results/Discussion/Conclusion, and the controlled English
  abstract. Rebuilt the internal draft as r42
  (`temporal_key_user_identification_internal_draft_r42_v3_null_result.docx`).
  Structural checks pass (191 paragraphs, 22 Heading-1, 13 Heading-2, five
  tables, six figures, six non-empty figure alt descriptions, no raw LaTeX
  markers); Word COM export produced `tmp/word_render_r42/r42.pdf`, while the
  local PDF rasterizer remains unavailable for page-level visual inspection.
- The v7 submission precheck passes citations, claim boundaries, completed v3
  evidence, and v3 environment reconciliation. It remains open only on
  author-controlled metadata, an approved release inventory, a fresh official
  Software Journal template, the template DOCX, and template-specific visual
  QA. The full regression suite remains green (`15 passed`).
- Re-verified the official Software Journal sample on 2026-08-23 and recorded
  `audits/official_template_verification_2026-08-23.md`: HTTP 200,
  `application/msword`, 3,027,456 bytes, SHA-256
  `6dd6d9f75609d4e6dc270fcc459a40fd14d46789c16c7a85a9c230eba815ffd0`, and a
  read-only Word structure check of 14 pages, 640 paragraphs, three tables,
  and one section. The v8 precheck passes this fresh-template gate but leaves
  author metadata, release inventory, final template DOCX, and template visual
  QA open.
- Added `experiments/audit_v3_manuscript_consistency.py` and its regression
  fixture. The audit cross-checks every v3 family against the Chinese source,
  English abstract, and claim ledger, including the exact-null counts and the
  three Holm-nonsignificant nonzero weight rows. It passes on the accepted
  bundle; the full test suite now passes `16` tests.
- Connected the v3 manuscript-consistency audit to
  `experiments/audit_submission_package.py`. The v9 precheck now passes
  citations, claim boundaries, completed v3 evidence, environment hashes,
  v3 text/statistics consistency, and fresh template verification. It remains
  open only on author metadata, approved release inventory, final template
  DOCX, and template-specific visual QA.
- Added Jia et al. (2022) as reference [33] only after Crossref and OpenAlex
  metadata agreement and retrieval of the Crossref BibTeX record. Its
  manuscript and related-work use is limited to title/metadata-level
  topic-and-temporal-activity context; no unverified method, data, objective,
  or result equivalence is asserted. The broader OpenAlex search produced
  off-topic leads and a Windows console encoding error; no such lead was
  retained as a citation.
- Rebuilt the evidence-bounded internal manuscript as r41
  (`temporal_key_user_identification_internal_draft_r41_temporal_activity_literature_update.docx`).
  It has 33 numbered references, 22 Heading-1 paragraphs, 12 Heading-2
  paragraphs, five tables, six inline figures, and no accessibility findings.
  Because LibreOffice/`soffice` is unavailable, a watchdog-bounded hidden Word
  PDF export and PyMuPDF page rendering were used for a read-only visual review
  of all 24 pages; no clipping, overlap, missing glyph, malformed table/figure,
  raw LaTeX, or header/footer defect was found. This remains an internal draft,
  not an official journal-template manuscript.
- Added author-controlled handoff forms
  `submission/author_confirmation_form.md` and
  `submission/release_inventory_approval_form.md`. They enumerate the exact
  fields and explicit-allowlist decisions needed to close the remaining
  submission gates without inferring identities, funding, contact details,
  licences, or archive permissions.
- 2026-09-16: User authorized the separately versioned formal v4 screening
  comparison. The active gate is new protocol + new runner + non-writing dry
  run + bounded smoke + read-only validator before any 30-run batch launch.
  The diagnostic 0.70/48 artifact remains excluded from formal inference.

## 2026-09-17 continuation: SNAM evidence-strengthening plan

- User accepted the staged plan: resolve v4 provenance, focus the current
  contribution on candidate reduction's conditional effect/cost/failure
  boundary, pre-register a small high-information validation set, and only
  then integrate accepted evidence into a complete SNAM package.
- Read-only v4 validation was attempted with the recorded conda interpreter.
  It reports one failure: the current formal runner hash differs from the hash
  in the result manifest. No source, result, protocol, or manifest file was
  changed. An independent file check found 30/30 result hashes match, 120 CSV
  rows, and GNN/weighted-out-degree equality in all 30 paired blocks; these
  facts are not yet formal statistical evidence.
- Added Phase 11 and the provenance error to `task_plan.md`, and recorded the
  evidence boundary in `findings.md`. Next action: local source-snapshot and
  metadata trace for the v4 runner mismatch.
- Corrected a transcription error in `findings.md`: the manifest's recorded
  runner digest is `0e8f312d90bb173add2bb0e5d5051c257c043a379b1af43d20d0df1b61153f93`.
  The audit report already contained this correct value. The first corrective
  patch failed because it tried to replace that correct audit line; the
  follow-up narrowed its scope. A broad text search through the large v4 JSON
  artifacts was unusable because it matched ordinary graph-edge source fields;
  future provenance checks will use structured metadata extraction.
- Structured inspection found that all v4 source hashes except the formal
  runner match current files. The current runner predates the first output
  artifact by 56 seconds, and its CPython bytecode cache was created four
  seconds after the first artifact; this is useful chronology but not proof of
  executed bytes. No alternate runner appeared in the checked Cursor/VS Code
  history paths. PowerShell history was permission-denied and is logged as a
  non-retryable read limitation. The next check compares the current source,
  its bytecode cache, and the runner's manifest-building logic.
- Source inspection confirms the runner hashes `Path(__file__)`, so a run of
  the current file should have recorded the current digest. The cached-bytecode
  header matches current timestamp and source length, but a direct marshalled
  comparison was inconclusive and is logged as such. The remaining local
  provenance hypothesis is a run from a now-missing alternate runner copy or
  an unrecorded source transition before the first artifact.
- Completed the read-only v4 provenance audit. All run-file hashes pass and
  current source/bytecode have matching executable semantics, but the captured
  runner bytes cannot be recovered. v4 is therefore not formally admitted and
  remains outside manuscript/statistical claims. The decision and future
  admission conditions are recorded in
  `audits/v4_provenance_audit_2026-09-17.md`; no result, protocol, source, or
  manifest was modified.
- Began the pre-registration design audit. The current data inventory confirms
  no admissible third causal-propagation dataset, while local Digg 20k is the
  only independent network candidate for a carefully limited simulation-based
  candidate-reduction check. Existing v3 full-search cost records mean a
  larger-k formal batch needs an explicit non-inferential cost preflight and
  a stopping rule. Next: inspect Digg's data card, existing cost records, and
  the generic v3 implementation boundary before writing the protocol.
- Completed that design inspection. Digg is usable only for a conditional
  simulated-selection check because its parent links are exposure proxies.
  Higgs k=2 full-search times range from roughly 0.8 to 1.7 hours per block,
  so k=5 requires a hard time-only preflight. The selected design is one
  narrow question at fraction 0.65: k=5, 30/60/120-node GNN pools plus a
  same-budget weighted-degree reference against full search, all scored on a
  common 100-world evaluation. The absent Higgs data card is logged; existing
  frozen provenance records remain the source of truth.
- Wrote and froze `protocols/influence_v5_candidate_reduction_preregistration.md`.
  It specifies the two-dataset k=5 design, full-vs-30/60/120 candidate pools,
  shared probability graph, a degree reference, two independent 100-world
  evaluations, formal seeds 63--72, and a non-inferential seed-62 time gate.
  It also prevents a v4-style provenance gap by requiring a verified immutable
  source snapshot before any preflight or formal output. Next: implement and
  test that isolated v5 infrastructure; no new experiment has started.
- Reviewed the v4 formal runner as the implementation reference. It confirms
  the useful deterministic world, timing, and resume patterns, but its v4-only
  pool structure and single-source hash scheme cannot be reused unchanged.
  Began v5 infrastructure work; no preflight or formal seed has been launched.
- Added the isolated v5 source-snapshot builder, runner, read-only validator,
  and analysis script. The implementation prevents a live-workspace runner
  from writing a v5 artifact while merely pointing at a snapshot. Next: add
  targeted tests, compile the new code, create a snapshot, and verify a dry
  run before considering an ineligible bounded smoke run.
- The first targeted pytest attempt compiled and ran four tests, but the fifth
  could not create pytest's default user-temp directory because that path is
  permission-denied in this environment. This is a test-harness location
  issue, not a study-code failure; rerun with an explicitly writable
  workspace-local pytest base directory.
- Created the first v5 snapshot and attempted a snapshot-executed dry run.
  Import resolution correctly stayed inside that snapshot but exposed missing
  transitive backend modules (`baselines`, `optimizer`, `diffusion`) in its
  copied source set. The snapshot is preserved as invalid/no-output evidence;
  the source-set contract now includes those modules and requires a fresh,
  separately named snapshot before another dry run.
- Created corrected snapshot `candidate-reduction-v5-20260917-r2`; snapshot
  dry runs passed for Higgs and Digg and all 12 targeted new/existing tests
  passed. Completed the bounded Higgs seed-61 smoke run. Its manifest, run
  hash, ineligible flags, and source-snapshot reference are consistent, and
  the formal validator rejects it exactly as designed. No smoke result values
  were used. Next: run the sequential, ineligible seed-62 Higgs cost preflight
  from the r2 snapshot, validate its schema/hash and resource gate, then run
  the Digg preflight only if Higgs returns normally.
- Started the sequential Higgs seed-62 cost preflight from the verified r2
  snapshot. It remains active and has not written a result artifact yet; no
  effect or selection output has been read. No Digg preflight or formal seed
  has been started in parallel, so the resource timing remains uncontaminated.

## 2026-09-20: candidate-truncation resolution pivot

- Completed the 16-condition v9 nested-W local development diagnostic and
  wrote a read-only JSON analysis. The v9 targeted test suite passes 3/3.
- Recorded the outcome-blind-to-outcome decision: W=20 versus W=80 changes all
  local full-greedy sequences, so candidate agreement needs a stated
  simulation-resolution condition.
- Wrote the publication-direction research card and readout. No learned
  ranking claim, GNN advantage claim, or confirmation-layer result was added.
