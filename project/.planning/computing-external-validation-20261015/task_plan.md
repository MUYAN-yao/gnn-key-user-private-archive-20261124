# Computing external-real-network validation — 2026-10-15

## Goal
Create a new, independently versioned external-validation evidence layer for the impact-maximization evaluation study. Acquire lawful public network data, perform outcome-blind resource preflight, freeze and run a traceable protocol, analyze only supported claims, and revise the Computing author-review package. Preserve every historical snapshot and result unchanged.

## Current phase
Author-review v2 complete: strict full-score replay, precision control, statistical regeneration and all-page PDF QA PASS. Final v3 ZIP extracted and all 1528 file hashes verified; author declarations remain explicitly pending.

## Guardrails
- Historical evidence is read-only: `submission/computing-strengthening-20261015` and its referenced v10 artifacts must never be edited.
- New data, code, outputs, manuscript revisions, and archive live only in `submission/computing-external-validation-20261015`.
- No paid compute, upload, external submission, public release, or communication on the author's behalf.
- Resource preflight must write timing and memory only; it must not retain or inspect seed sets or utilities. Any later outcome inspection is labelled exploratory until the main protocol is frozen.
- Claims entering prose require a provenance record and allowed wording; no citation is created from memory.

## Phases
1. Inventory old interfaces and create data-selection records; select 2–3 lawful, structurally distinct networks before inspecting outcomes — complete.
2. Build a versioned generic data/preflight adapter; run outcome-blind resource preflight and validate semantics against the inherited engine — complete.
3. Freeze dataset manifests, hashes, predeclared condition matrix, seeds, comparison families, stopping rules, source snapshot and environment — complete.
4. Execute the frozen serial experiment matrix — complete (54/54, 468 arms); strict full-score and evaluation replay PASS. Separately frozen post-hoc precision control complete (15 conditions, 30 arms).
5. Generate strict statistical analysis, figures, tables, claim ledger, and Chinese results report — complete; deterministic regeneration PASS (25 CSV/PNG/generated-table checks); final audit gate PASS.
6. Revise manuscript, supplement, summary, cover-letter draft, and author checklist — complete; 17+9 pages compiled twice and all 26 pages visually inspected; abstract 226 words, 23 cited references, no unresolved markers/overflow.
7. Package reproducibility materials, verify archive contents, and report supported conclusions and outstanding author decisions — complete; final v3 ZIP 52,352,375 bytes, CRC PASS, 1528 extracted file hashes PASS, third-party raw data excluded.

## Decisions made
- New layer id: `computing-external-validation-20261015`.
- Candidate sources will be official SNAP dataset pages/downloads, selected for a temporal communication network plus static networks with different topology/application. Final selection will be recorded before outcome inspection.
- Main propagation target remains independent cascade with p=0.01, horizon=3 and step-indexed shared worlds, to retain comparability. A limited fixed-edge-coupling check is planned only after resource preflight.
- Full greedy remains exhaustive per-round enumeration; CELF or pruning is prohibited unless separately proven semantically equivalent before protocol freeze.
- Outcome-blind preflight passed at W=80 and 320 with 1,000 evaluation worlds. W=320 full-greedy selection time was 2.67 s (CollegeMsg), 10.17 s (ca-GrQc), and 39.38 s (wiki-Vote); peak working set was at most 624,054,272 bytes.
- Frozen main matrix: 45 step-coupled resolution conditions (3 datasets × 5 paths × W 80/320/1280) plus 9 W=320 fixed-edge controls. Each uses 10,000 independent evaluation worlds; the primary arm set has full, degree/PageRank 4k, three random 4k pools and degree/PageRank 5%-coverage pools, with two authentic history-weighted arms only on CollegeMsg.
- W=5,120 is excluded before outcomes because an outcome-blind linear projection of wiki-Vote W=320 is approximately 10.5 minutes for one full-greedy path and over 52 minutes for its five-path full-only portion. It may only be added through a new freeze.
- `snapshot/source_manifest.json` was created with SHA256 `742047348d1da77fd7a68d33ae26cb53ce3a2b08e43e22b0d621be0363f687e6`; the runner refuses changed frozen inputs.
- Frozen execution completed 54/54 conditions with no failures. Validation confirms 54 paired JSON/NPZ files, matching array hashes, matching frozen source hash and full-pool invariants; 468 arm records are available for analysis.

## Next step
Author final scientific review and completion of true identity, funding, conflicts, contributions, AI-use and data/code-access declarations. No automatic submission or publication.

## Author-review v2 corrections
- Frozen source-manifest checks did not enforce raw file SHA256 at execution entry. Actual raw and graph/result hashes are now checked; a guarded reproduction wrapper fixes enforcement without changing frozen v1.
- ca-GrQc node12295 appears only in a self-loop. Frozen preprocessed size5241 is retained, and endpoint-rule prose ambiguity disclosed.
- Archived preparation includes all rankings; avoid double counting. Hybrid deployment/verification costs use separate method-specific setup measurements, labelled post-hoc.
- Main positive psutil peak is3.448822 GiB, not the smaller preflight peak. Earlier negative PowerShell values have no verified causal diagnosis.
- W5120 is not added because the revised external claim is explicitly limited to80–1280, not because of an elapsed-time authorization limit. No convergence assertion retained.
- Post-hoc numerical-ranking check found changed candidates when tightening PageRank tol1e-6 to1e-12 (n*tol stopping criterion). Froze a small all-graph precision control before new utility inspection:15 original-path W1280 conditions, two PageRank arms each, no new sample-size claim; frozen main matrix unchanged.
- Precision control completed: ca-GrQc PageRank-4k mean difference changes from -0.25082 to +0.02608, with mixed path signs; CollegeMsg unchanged; wiki-Vote losses remain -41.21970 (4k) and -13.63982 (5%). Main text explicitly qualifies solver sensitivity and does not claim superiority.
- Setup timing repeated with no concurrent experiment/audit load; final costs are labelled hybrid estimates, with duplicated lexical-sort charge removed. Provisional measurements retained.
- All 1191 historical manifest entries remain unchanged. Strict main audit checked 4,680,000 evaluation values and 1,401,120 stored score positions; scalar oracle checked 4,672 worlds.
- Initial ZIP extraction hit Windows long-path limits; preserve unverified v2 ZIP, deliver v3 ZIP using extended-path extraction and actual SHA256 checks. No source/result file is changed to shorten paths.

## Errors encountered
| Error | Attempt | Resolution |
|---|---:|---|
| `New-Item -LiteralPath` is unsupported in this PowerShell build | 1 | Created the directories with `New-Item -Path` instead; no data were modified. |
| `Invoke-WebRequest` received transport EOF for CollegeMsg and Wiki-Vote | 1 | ca-GrQc downloaded, but the batch cannot be trusted as complete. Retry only the missing files with `curl.exe --retry`, then hash and validate gzip contents before preprocessing. |
| `7z` was unavailable for gzip validation | 1 | Used Python's standard `gzip` reader to read every compressed source file successfully; retain this validation in the manifest. |
| Base Miniconda Python lacks `numba` | 1 | Locate the preserved extension dependency path used by the prior package and execute only through that isolated dependency path; do not alter the base environment. |
| First ranking-timing refactor left a stale `name` reference in the temporal ranking branch | 1 | Removed the stale lines before any frozen run; syntax and semantic checks will be rerun before freezing. |
| One status probe used a malformed workspace path | 1 | Retried with the verified workspace path; no experiment process or result file was altered. |
| A second status probe repeated the malformed workspace path | 2 | Corrected immediately; subsequent probe confirms the matrix advanced from 37 to 38 completed conditions. |
