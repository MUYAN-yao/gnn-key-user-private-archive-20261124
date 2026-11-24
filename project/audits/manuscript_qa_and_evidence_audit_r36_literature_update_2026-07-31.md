# Manuscript QA and Evidence Consistency Audit (r36 literature update)

Date: 2026-07-31

## Scope

This audit covers the internal Word manuscript r36 after the conservative
related-work evidence update for Fu et al. (2022). It does not alter any
experiment configuration, frozen result, or analysis output.

## Evidence Boundary

- Reference [29] is now supported by retrieved full text (PMC9322785), rather
  than title/abstract metadata alone. The related-work wording is limited to
  its dynamic-network, effective-link method scope and reported comparison
  design; it makes no cross-paper numerical or protocol-equivalence claim.
- The completed v2-T0d ablation remains a separately versioned,
  protocol-specific null result: all nine full-minus-ablation contrasts are
  exact zero with Holm-adjusted p = 1.0. The draft continues to prohibit an
  independent term-effect claim, pooling with v2-T0b, or use of invalid v2-T0c
  output as evidence.

## r36 Structural and Render QA

| Check | Result |
| --- | --- |
| Word structure | 166 nonempty paragraphs, 34 headings, 5 tables, 30 references, and 6 embedded figures |
| v2-T0d integration | present in the draft and retained as a protocol-specific null result |
| Accessibility | `internal_docx_a11y_audit_r36_literature_update_2026-07-31.json` reports 0 high, 0 medium, and 0 low findings |
| Page rendering | Word COM export and PyMuPDF raster review: 23 pages, 0 out-of-bounds text blocks, and no raw LaTeX markers |
| Visual review | four contact sheets covering all 23 pages were inspected; no clipping, overlap, broken table/figure, or legibility defect was found |
| Table continuation | the page-22 whitespace after a continued table is intentional and avoids splitting a table row |

LibreOffice was unavailable in this environment. The completed watchdog-bounded
Word-COM/PyMuPDF review is therefore the visual-QA record for r36.

## Conclusion

r36 is the current internally reviewed, evidence-bounded manuscript draft. It
is not an official *Journal of Software* template submission and must not be
represented as submitted or accepted. Remaining gates are fuller related-work
coverage, author-supplied publication metadata, archive-rights verification,
and conversion using a freshly downloaded official template followed by final
page-by-page QA.
