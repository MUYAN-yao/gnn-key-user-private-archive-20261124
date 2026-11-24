# V3 visual review

Reviewed after the final successful LaTeX build and `render_and_check.py` run on
2026-10-16. This is an actual page-image inspection, in addition to the automated
text-block and log checks in `render_checks.json`.

| PDF | Pages reviewed | Result |
| --- | --- | --- |
| `manuscript/manuscript.pdf` | 19/19 | Title page, text, equations, all five tables, Figs. 1--4 and references are legible; no clipped blocks, unresolved markers, overlapping elements, accidental blank content pages or figure/table overflow observed. The new Fig. 1 budget--precision panel grid and Table 3 fit the normal journal page width and retain readable legends/captions. |
| `manuscript/Online_Resource_1.pdf` | 11/11 | Source-scoped related-work table, audit tables, post-hoc precision section, Table 7 and Fig. S1 render correctly. Dense full-matrix tables are intentionally retained in the supplement; their columns remain inside the page and readable at rendered-page scale. No citation placeholders, cut-off figures or overflow observed. |

Evidence images are the numbered PNGs in `qa/manuscript/`,
`qa/Online_Resource_1/`, and the corresponding `*-contact-*.png` contact sheets.
This review confirms layout only; numerical claims are gated separately by
`audit/precision_budget_validation.json` and `qa/final_checks_v3.json`.
