# Core-Journal Submission Readiness Audit (r37)

Date: 2026-07-31

## Scope

This audit evaluates the current internal manuscript r37 for the working
target, *Journal of Software* (*软件学报*). It records readiness evidence only;
it is not evidence of editorial acceptance, publication, or submission.

## Current Evidence State

| Requirement | Current evidence | Assessment |
| --- | --- | --- |
| Core empirical claims | frozen v1 paired analysis, strict v2-T0b Higgs analysis, and `manuscript/claim_ledger.md` | supported only at the stated protocol level |
| Strict v2-T0b completeness | 30/30 artifacts, manifest hashes, 210 metric rows, and strict paired analysis | complete |
| Objective ablation | v2-T0d: 30 artifacts, 120 rows, nine exact-zero contrasts, Holm p = 1.0 | complete protocol-specific null; no independent-term claim |
| Statistical reporting | separate 24-contrast frozen-v1 and 18-contrast v2-T0b Holm families; ten paired protocol repetitions per contrast | complete; not independent-network inference |
| Negative-result disclosure | frozen Higgs/RIS 0.60 exact tie and strict v2-T0b all-RIS Holm nonsignificance | complete |
| Literature traceability | 30 bibliography entries, two-source metadata/BibTeX audit, and expanded full-text scope for [19], [28], and [29] | complete at recorded scope; not an exhaustive review |
| Domestic comparison | two cited *软件学报* articles and the 2026 domestic multilayer-GNN paper inspected in full text | present, not a comprehensive domestic review |
| Internal manuscript package | r37: 30 references, six embedded figures, five tables, and all figure targets resolved | complete |
| Internal visual QA | watchdog-bounded hidden Word export plus PyMuPDF raster review: 23 pages, zero out-of-bounds blocks, no raw LaTeX, and no observed clipping/overlap | complete for the internal draft |
| Accessibility | r37 DOCX audit: 0 high, 0 medium, 0 low findings | complete |
| Official format availability | current 2025 official sample rechecked on 2026-07-31 and field mapping retained | available for later conversion |

## Required Claim Boundary

The manuscript may report protocol-conditional optimization improvements in the
specified frozen and strict Higgs comparisons. It must not claim universal
superiority, causal Digg resharing, cross-dataset generalization from strict
v2-T0b, a globally optimal T0 architecture, significant superiority over RIS
in v2-T0b, or independently demonstrated contributions from the risk and
community terms. Repetitions are paired stochastic protocol runs, not
independent social-network samples.

## Remaining Submission Gates

1. **Author-controlled metadata:** authorship, affiliations, correspondence,
   funding, acknowledgements, conflicts, ethics decision, and final data/code
   availability wording in `manuscript/submission_metadata_intake.md` have no
   verified values and cannot be inferred.
2. **Archive decision:** raw Higgs and Digg files must remain excluded unless
   a first-party review establishes redistribution permission. A code-and-
   metadata-only archive additionally needs author-approved destination and
   release wording.
3. **Literature depth:** current coverage is traceable and strengthened, but
   does not constitute an exhaustive domestic or international review.
4. **Official-template conversion:** after gates 1--3, download a fresh
   official sample, transfer the finalized manuscript without fabricated
   editorial or author fields, and conduct page-by-page Word/PDF QA.

## Decision

The project has a render-checked, evidence-bounded core-journal manuscript
candidate. It is not yet ready for online submission because the remaining
metadata, archive, literature-depth, and official-template gates require
author-controlled decisions or additional verified evidence.
