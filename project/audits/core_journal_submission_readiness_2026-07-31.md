# Core-Journal Submission Readiness Audit

Date: 2026-07-31

## Scope

This audit evaluates the current manuscript against the working target,
*软件学报* (*Journal of Software*). It records submission-readiness evidence;
it is not evidence of editorial acceptance or publication.

## Current Evidence State

| Requirement | Current evidence | Assessment |
| --- | --- | --- |
| Core empirical claims | Frozen v1 paired analysis plus strict v2-T0b Higgs analysis, claim ledger C1--C5 | supported only at the stated protocol level |
| Strict v2-T0b completeness | 30/30 preregistered artifacts, manifest hashes, 210 metric rows, strict validator pass, no nonempty error logs | complete |
| Statistical reporting | Separate 24-contrast frozen-v1 and 18-contrast v2-T0b Holm families; 10 paired protocol repetitions per contrast | complete, not independent-network inference |
| Negative-result disclosure | Frozen Higgs/RIS 0.60 tie; strict v2-T0b all RIS contrasts Holm-nonsignificant | complete |
| Literature traceability | 28 entries have two-source metadata verification and source-retrieved BibTeX; feature claims are bounded by the audit record | complete at the recorded scope |
| Domestic comparison | Two *软件学报* articles and a 2026 domestic multilayer-GNN method have been full-text inspected | present, but not yet a comprehensive domestic review |
| Official format availability | Official *软件学报* 2025 sample rechecked on 2026-07-31: HTTP 200, `application/msword`, 3,027,456 bytes, `Last-Modified: 2026-04-02` | available for later conversion |

## Claim Boundary Required for Submission

The manuscript may claim protocol-conditional improvement in the supported
frozen and strict Higgs comparisons. It must not claim universal superiority,
causal Digg resharing, cross-dataset generalization from strict Higgs v2-T0b,
a globally optimal T0 configuration, or significant superiority over RIS in
v2-T0b. The repeated unit is a paired stochastic protocol run, not an
independent social-network sample.

## Remaining Gates

1. **Literature depth:** expand the domestic and international literature
   comparison with additional full-text-backed method contrasts, or obtain a
   human editorial decision that the current 28-reference scope is sufficient
   for the target journal. Title/abstract-scoped entries must remain bounded.
2. **Author-controlled metadata:** the author order, affiliations,
   correspondence, funding, acknowledgements, conflict declaration, ethics
   decision, and archive decision in `manuscript/submission_metadata_intake.md`
   have no verified values. They cannot be inferred or fabricated.
3. **Archive and licensing:** create the source/environment archive only after
   confirming the raw Higgs and Digg redistribution terms.
4. **Official-template conversion and visual QA:** transfer the finalized
   manuscript only after the preceding gates are resolved, then inspect every
   rendered page. The current machine has no `soffice`; a read-only Microsoft
   Word background export was also attempted and stalled without generating a
   PDF. An internal DOCX structural check is not a substitute for visual QA.

## Decision

The project now has an evidence-bounded, reproducible core-journal manuscript
candidate and a current official sample available for conversion. It is not
yet authorized or technically verified for online submission because the four
remaining gates above require either more verified scholarly evidence, an
author decision, or a rendering/archive capability outside the current
artifacts.
