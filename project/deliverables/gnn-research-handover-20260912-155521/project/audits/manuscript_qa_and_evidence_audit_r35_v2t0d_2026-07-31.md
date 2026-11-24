# Manuscript QA and Evidence Consistency Audit (r35 v2-T0d)

Date: 2026-07-31

## Scope

This audit covers the internal Word manuscript r35 and its Markdown sources
after integration of the independently versioned v2-T0d common-world objective
ablation. It does not change any experiment configuration, frozen result, or
analysis output.

## Evidence Integration

- Reviewed `analysis/v2-t0d-common-world-objective-ablation-v1/paired_comparisons.json`.
  The nine preregistered full-minus-ablation contrasts (three training fractions
  by three ablation arms) each contain ten exact zero differences, with ten ties,
  exact sign-flip p = 1.0, and Holm-adjusted p = 1.0.
- The manuscript source, claim ledger, statistical appendix, reproducibility
  appendix, and submission-readiness record consistently describe this as a
  controlled protocol-specific null result. They prohibit attribution of the
  main-study gains to the risk or community term individually, prohibit pooling
  v2-T0d with v2-T0b, and exclude the invalid v2-T0c output as evidence.
- All six Markdown figure targets resolve to existing analysis figures,
  including the new common-world-ablation figure.

## r35 Structural and Render QA

| Check | Result |
| --- | --- |
| Word structure | 181 nonempty paragraphs, 34 headings, 5 tables, 30 references, and 6 embedded figures |
| v2-T0d integration | present in the draft and in the appendices; no English residual text marks the ablation pending |
| Accessibility | `internal_docx_a11y_audit_r35_v2t0d_2026-07-31.json` reports 0 high, 0 medium, and 0 low findings |
| Page rendering | Word COM export was rendered to PDF and PyMuPDF PNGs: 23 pages, no out-of-bounds text blocks, and no raw LaTeX markers |
| Visual review | all four contact sheets were reviewed; pages 11 and 21--22 were additionally inspected at high resolution |
| Table continuation | r34's split table row was retained as an audit trace; r35 applies `w:cantSplit`, repeats the continued header, and has no split individual table rows |

LibreOffice was unavailable in this environment. The completed Word-COM/PyMuPDF
render inspection is therefore the visual-QA record for r35. It found no
clipping, overlap, missing figure, or unreadable table content. The whitespace
after the table continuation on page 22 is intentional and preferable to a
split row.

## Conclusion

r35 is an internally reviewed, evidence-bounded manuscript draft. It is not an
official *Journal of Software* template submission and must not be represented
as submitted or accepted. Remaining publication gates are fuller domestic and
full-text related-work coverage, conversion using the official journal template,
author-supplied publication metadata, and a data/code archive decision after
rights verification.
