# Core-Journal Manuscript Quality Audit

Date: 2026-07-29

## Scope

This is a read-only editorial and evidence audit of the current Chinese
manuscript for the working target, *Software Journal* (软件学报). It checks
whether the current draft presents only claims supported by the claim ledger
and identifies the remaining gates for a submission-ready package. It does
not certify acceptance or publication readiness.

## Central Narrative

The current evidence-supported one-sentence contribution is:

> Under two frozen temporal network protocols, the study evaluates a
> GNN-prior-constrained greedy seed-selection procedure against matched
> baselines using a risk-penalized, cross-community objective, while auditing
> future-edge prediction independently rather than treating training-edge
> reconstruction as predictive evidence.

This framing is supported by `manuscript/claim_ledger.md` C1--C4. It is
appropriately conditional: it excludes universal superiority, causal Digg
resharing, globally optimal T0 selection, and partial v2-T0b performance.

## Evidence-to-Prose Checks

| Manuscript element | Evidence checked | Result |
| --- | --- | --- |
| Abstract and conclusion | `claim_ledger.md` C1--C4 | Pass. The Higgs/RIS 0.60 tie, Digg proxy boundary, and non-universal scope are retained. |
| Frozen comparison result | `analysis/frozen-main-comparison-v1/analysis-report.md` and `manuscript/statistical_appendix.md` | Pass. The draft identifies ten paired repetitions, 24 Holm-adjusted contrasts, and the sole exact tie without converting them into cross-network inference. |
| Probability-audit narrative | `analysis/edge-prediction-v2-t0-gate-v2/analysis-report.md` | Pass. The draft identifies T0's fixed GATv2/decoder configuration and validated-candidate status; the incomplete candidate grid remains disclosed. |
| Formal v2-T0b status | `results/large-robust-greedy-higgs-50000-v2-t0b/` and `claim_ledger.md` C4 | Pass. The in-flight batch is explicitly excluded from manuscript results and contributions. |
| Reproducibility prose | `reproducibility/frozen-study-manifest-v1.json`, `audits/manuscript_code_consistency_audit_v1.md`, and Appendix A | Pass for the frozen v1 evidence. Missing hardware and total-runtime metadata are disclosed rather than inferred; journal-facing prose no longer exposes workspace paths. |
| Related-work claims | `manuscript/citation_audit.md` and `manuscript/related_work_matrix.md` | Pass at the current scope. Twenty-four audited entries are used only at their verified full-text or title/abstract evidence level, with no cross-paper numerical comparison. The manuscript's Table 1 compares only full-text-backed method settings and explicitly avoids cross-paper performance claims. |
| Figures and captions | `audits/figure_visual_qa_2026-07-29.md` | Pass with caveat. The frozen figures are legible; Figure 1 must retain its caption and Appendix-B disclosure of the zero-height Higgs/RIS bar. |

## Current Strengths

- The abstract starts from the precise temporal-network problem and states the
  main conditional result without a generic opening.
- The introduction provides four falsifiable contributions and separates
  optimization evidence from probability-validation evidence.
- The results report paired uncertainty, exact tests, multiplicity correction,
  and the non-advantage result rather than only positive comparisons.
- The limitations section directly addresses the two-data-protocol scope,
  Digg exposure-proxy semantics, incomplete T0 grid, and the unfinished strict
  v2-T0b run.
- The internal DOCX omits local repository paths from its visible manuscript
  and appendix prose, while preserving publication-facing appendix references.

## Submission Gates Still Open

1. Complete the 30-run strict timestamp-grouped v2-T0b batch, verify its
   manifest and error log, then run the prescribed summary and a separate
   paired-statistics analysis before introducing any v2-T0b claim.
2. Expand the domestic and international comparison with full-text-backed
   feature claims. Full texts for the two domestic Software Journal comparison
   points, a domestic multilayer GNN method, a recent AAAI GNN
   influence-maximization work, and an adaptive GNN method have now been
   inspected. Twenty-four audited references provide a broader but still
   controlled foundation; title/abstract-scoped entries must remain at that
   boundary until their full texts are inspected, and the comparison is not
   yet comprehensive enough for the target venue.
3. Acquire and validate the current official Software Journal Word template
   only after the evidence and literature gates pass; convert content into the
   template without copying inferred formatting.
4. The current internal DOCX was rebuilt after the verified 23rd TGAT
   reference under a new filename so that an open older WPS document was not
   overwritten. Its structural and accessibility checks pass, but the bundled
   renderer cannot start without `soffice`; inspect the completed official
   template with a supported renderer before submission. These checks do not
   substitute for page-level visual QA.
5. Create a lawful public source archive and attach the captured local
   environment record; raw dataset redistribution remains out of scope pending
   license review.

## Decision

The current manuscript is an evidence-bounded internal draft, not a
submission-ready core-journal manuscript. Its central narrative and existing
frozen claims are internally consistent, but the open evidence, literature,
template, rendering, and archival gates must remain visible until resolved.
