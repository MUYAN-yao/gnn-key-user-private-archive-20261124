# Manuscript QA and Evidence Consistency Audit (r37 literature full-text update)

Date: 2026-07-31

## Scope

This audit covers the internal Word manuscript r37 after upgrading two existing
related-work citations to retrieved-full-text scope. It does not alter any
experiment configuration, frozen result, or analysis output.

## Evidence Boundary

- Yanchenko et al. (2023) [19] is now supported by a public 23-page Springer
  Open PDF. The manuscript uses it only to delimit the ex ante information
  boundary between observed and future snapshots; its SI model, predicted
  network, data, and outcomes are not equated with the present protocol.
- Liu et al. (2024) [28] is now supported by a public 24-page MDPI PDF. The
  corrected related-work wording confines the attribution to its adaptive-GCN,
  neighborhood-discount, Top-K route and IC/SIR evaluation. It makes no
  cross-paper numerical, temporal-protocol, or objective-equivalence claim.
- The separately versioned v2-T0d ablation remains a protocol-specific null
  result: all nine full-minus-ablation contrasts are exact zero with
  Holm-adjusted p = 1.0. The draft prohibits independent term-effect claims,
  pooling with v2-T0b, and use of invalid v2-T0c output as evidence.

## r37 Structural and Render QA

| Check | Result |
| --- | --- |
| Word structure | 166 nonempty paragraphs, 34 headings, 5 tables, 30 references, and 6 embedded figures |
| Literature update | r37 carries the corrected full-text evidence wording for [28]; [19] remains a scope-limited ex ante comparison |
| v2-T0d integration | present and retained as a protocol-specific null result |
| Accessibility | `internal_docx_a11y_audit_r37_literature_fulltext_update_2026-07-31.json` reports 0 high, 0 medium, and 0 low findings |
| Page rendering | watchdog-bounded Word COM export and PyMuPDF raster review: 23 pages, 0 out-of-bounds text blocks, and no raw LaTeX markers |
| Visual review | four contact sheets covering every page were inspected; no clipping, overlap, broken table/figure, or legibility defect was found |
| Table continuation | the whitespace after the continued table on page 22 is intentional and prevents a split row |

LibreOffice was unavailable in this environment. The completed Word-COM and
PyMuPDF review is therefore the visual-QA record for r37.

## Conclusion

r37 is the current internally reviewed, evidence-bounded manuscript draft. It
is not an official *Journal of Software* template submission and must not be
represented as submitted or accepted. Remaining gates are fuller related-work
coverage, author-supplied publication metadata, archive-rights verification,
and final conversion using a freshly downloaded official template followed by
page-by-page QA.
