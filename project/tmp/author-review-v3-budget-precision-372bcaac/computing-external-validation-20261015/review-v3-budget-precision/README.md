# Author final-review package: external influence-maximization evaluation

This version is local and awaits human author approval. It preserves the immutable
external experiment and the historical archive. It is not a submission, public
data deposit, software-licence grant or promise of journal acceptance.

## Start here

Read research_report_zh.md, then manuscript/manuscript.pdf and
manuscript/Online_Resource_1.pdf, analysis-report.md, stats-appendix.md and
author_checklist_zh.md. summary_for_editor.txt and cover_letter_draft.txt remain
author-review drafts. The current study reaches W1280, not W5120.
`claim_evidence_matrix.md` is the wording gate linking every material claim to
its evidence and stated limit.

Two separately frozen post-hoc numerical controls are supplied. `supplement-pr-precision`
contains 15 W1280 conditions/30 restricted arms. `supplement-pr-budget-precision`
adds 30 W80/W320 conditions/60 restricted arms and combines with the earlier
control during analysis. Both reuse the original five paths; they are not extra
independent path evidence and do not replace the54-condition/468-arm main study.
The newer protocol and source manifest were frozen before its utility outputs;
see `analysis/precision_budget` for paired effects, pool diagnostics and figure
sources.

The parent directory contains frozen config/protocol/data manifests/snapshot and
results/main/conditions (54 JSON+54 NPZ files). review-v2 contains new scripts,
strict audit, analysis, figures, manuscript, reports and QA. Every NPZ holds
`<method>_evaluation` (10,000 per-world spreads) and `<method>_round_totals` (k by
candidate-count integer totals). JSON supplies its pool and selected original IDs.
run_status.json indexes expected keys and SHA256 values. A combined archive also
retains the sibling computing-strengthening-20261015 historical evidence tree.
Only the original third-party data must be reacquired; no raw data are in the ZIP.

## Environment

Tested Python3.13.0 on Windows11, NumPy2.3.3, pandas2.3.2, SciPy1.16.1,
NetworkX3.5, matplotlib3.10.6, psutil7.2.2, Numba0.68.0, llvmlite0.50.0.
Use the parent's frozen requirements.txt in an isolated environment. PDF QA uses
PyMuPDF and Pillow (exact installed versions recorded in qa/environment.json).
TeX Live2026 with pdflatex compiles the flat manuscript directory. The bundled
svjour3/svglov3 class files are unchanged from the previous package.

The local run uses a single worker with OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1.
Main frozen elapsed-condition sum is30.65 minutes; its process-lifetime peak is
3.449 GiB. Audit replay is additional work. Timings change with hardware/load.
Imports/JIT are excluded from reported search/assembled deployment estimates.

From the extracted `computing-external-validation-20261015` directory:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install pymupdf pillow
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
.venv/Scripts/python review-v2/src/download_data.py
.venv/Scripts/python review-v2/src/audit_results.py --replay
.venv/Scripts/python review-v2/src/check_regeneration.py
```

The two precision controls are already supplied. Re-execution requires a fresh
copy and a new empty output location; neither script overwrites condition pairs.
The budget control must first be frozen, then executed:

```powershell
python review-v3-budget-precision/src/run_precision_budget_control.py --freeze-only
python review-v3-budget-precision/src/run_precision_budget_control.py --execute
python review-v3-budget-precision/src/analyze_precision_budget.py
python review-v3-budget-precision/src/validate_precision_budget.py
```

Do not delete delivered results to rerun in place.

download_data.py validates existing files and refuses a changed hash. Provider
terms remain applicable. Original sources and retrieval hashes are in
data_selection.md and data/source_manifest.json; the review audit explains the
ca-GrQc endpoint rule. The original frozen runner is unchanged and its raw-input
enforcement gap is documented. Use the guarded wrapper for a fresh experiment:

```powershell
.venv/Scripts/python review-v2/src/run_guarded.py --output D:/new-empty-run
```

Use a new directory; do not replace archived results. To analyze a rerun, make a
separate copy of this package and place the new result tree at results/main in
that copy. The scripts resolve files relative to their own locations, not a
hard-coded machine path. Preserve the sibling historical package for document
generation and class verification. Restart interrupted runs only after inspecting
partial condition files; this frozen runner has no automatic resume support.

For new-machine setup timings, work on a copy and run
`python review-v2/src/supplement_setup_timing.py` before `analyze.py`.
That changes timing-derived results and requires a new version/QA; it must not be
confused with deterministic regeneration of the delivered numerical results.

```powershell
Set-Location review-v2/manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
Set-Location ..
python src/render_and_check.py
```

Inspect every rendered page again after changes; an old visual-review record does
not certify a new PDF. verify_references.py queries Crossref and regenerates the
bibliography from preserved historical entries plus verified external references;
the saved metadata are supplied for offline review. It is not required for offline
statistical regeneration. The historical package README describes its own data
acquisition/preparation and reproduction separately.

## Verification records and boundaries

- audit/full_validation.json: complete matrix/hash/score/evaluation audit.
- audit/preprocessing-and-timing-findings.md: documented discrepancies and scope.
- audit/reference_metadata.json and journal-and-literature.md: citation/guide checks.
- qa/render_checks.json, visual-review.md: numerical layout checks and actual inspection.
- qa/regeneration.json: all CSVs, figure PNGs and generated tables reproduce.
- qa/final_checks.json: manuscript/statistical assertions, environment and freeze identity.
- The ZIP includes package_manifest.json; the adjacent verification JSON reports
  extraction and every-file SHA256 verification, with the archive's own SHA256.

Audit does not establish causal influence, expected-optimality, practical
equivalence, a universal restriction threshold or author approval. Five paths are
computational replicates. Hybrid cost estimates assemble supplementary setup with
frozen stage timings and exclude cold-start/import/download/output-writing costs.
All such limits remain in the manuscript and author checklist.
