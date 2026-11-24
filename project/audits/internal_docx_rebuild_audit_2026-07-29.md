# Internal DOCX Rebuild Audit

Date: 2026-07-29

## Scope

This audit covers the rebuilt internal manuscript artifact
`manuscript/temporal_key_user_identification_internal_draft_tgn_rebuilt.docx`.
It is not an official *Software Journal* template file and does not certify
submission readiness.

## Source Alignment

- Rebuilt from the current Markdown after the verified TGAT and TGN paragraphs
  and references [23]--[24] were incorporated.
- The active WPS window held the older internal draft, so the rebuilt artifact
  was deliberately written under a new filename rather than overwriting a
  possibly unsaved open document.
- The artifact contains 143 paragraphs, 19 Heading-1 paragraphs, 10 Heading-2
  paragraphs, three tables, and three inline figures.
- `python-docx` checks confirm the TGN paragraph, reference [24], and all 24
  bibliography entries. The previous TGAT checks remain applicable because the
  same current Markdown source is rebuilt in this artifact.
- The two manuscript tables contain seven rows each (header plus six data
  rows); the appendix statistics table contains 25 rows.

## Structural Checks

- `a11y_audit.py` report:
  `audits/internal_docx_a11y_audit_tgn_rebuild_2026-07-29.json` reports zero
  high, medium, and low findings.
- Heading audit confirms Heading-1 and Heading-2 style counts of 19 and 10.
- Image audit reports three inline figures with nonzero dimensions.
- Section audit reports one portrait US-letter section with one-inch margins.

## Render Gate

The bundled `render_docx.py` command was attempted on 2026-07-29 for this
rebuilt file and could not start its LibreOffice conversion process because
`soffice` is absent in this environment (`WinError 2`). Therefore no page PNGs
or PDF were produced, and visual page-level QA remains pending. Structural and
accessibility checks do not substitute for the render gate.
