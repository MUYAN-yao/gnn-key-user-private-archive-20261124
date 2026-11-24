# Internal Manuscript QA: r39 ML-Survey Update

Date: 2026-08-15

## Artifact

- DOCX: `manuscript/temporal_key_user_identification_internal_draft_r39_ml_survey_update.docx`
- DOCX SHA-256: `9cec715906e3ae8bbc3451e0178951ce38769679f58e043b9f31c1d946d25d7b`
- Scope: internal evidence-bounded draft; not the official Software Journal
  template and not a submission package.

## Structural and Accessibility Checks

- 22 Heading-1 paragraphs and 12 Heading-2 paragraphs.
- 31 numbered references; the manuscript citation audit reports no missing or
  unknown citation numbers.
- Six inline figures, five tables, one portrait US-letter section, and
  one-inch margins.
- Accessibility audit: high 0, medium 0, low 0.
- OOXML scan: zero occurrences of the known raw LaTeX controls `\\lambda`,
  `\\eta`, `\\sigma`, `\\mathbb`, and `\\operatorname`.

## Controlled Visual QA

- LibreOffice/`soffice` renderer: unavailable in the environment.
- A hidden Microsoft Word COM process opened the DOCX read-only and exported
  `tmp/word_render_r39/r39.pdf` within the 90-second watchdog.
- PDF SHA-256:
  `84C099BA99DBBFC0D3495C082F01761104CBD449B253BFCD833B7EE4B8A055A4`.
- PyMuPDF rendered all 23 pages at 1.5x resolution. Every page was inspected
  for clipping, overlap, missing glyphs, broken table/figure geometry, and
  raw LaTeX display. No defect was found. Table continuation headers and the
  new page-2 related-work paragraph render correctly.
- The temporary Word export process exited; no Word process was left running.

## Gate Decision

r39 passes internal structural, accessibility, and controlled visual QA. It
must still be converted to a freshly verified official journal template after
the v3 statistical evidence and author-supplied submission metadata are
complete.
