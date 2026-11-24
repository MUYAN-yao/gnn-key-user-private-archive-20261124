# Internal Manuscript QA: r41 Temporal-Activity Literature Update

## Scope

This audit covers the internal evidence-bounded DOCX
`manuscript/temporal_key_user_identification_internal_draft_r41_temporal_activity_literature_update.docx`.
It is not an official *Journal of Software* template conversion or a submission
authorization.

## Content and Structure

- The source draft, bibliography, citation audit, and related-work matrix add
  Jia et al. (2022) as reference `[33]` after Crossref and OpenAlex metadata
  agreement and source-retrieved Crossref BibTeX.
- The added discussion is restricted to title/metadata scope and explicitly
  does not infer its temporal-isolation protocol, candidate mechanism,
  diffusion model, objective, data, or results.
- The DOCX has 187 paragraphs, 33 numbered references, 22 Heading-1
  paragraphs, 12 Heading-2 paragraphs, five tables, six inline figures, one
  section, a visible `[33]` reference, and no missing-figure marker.
- Accessibility audit output is `audits/r41_docx_a11y.json`: high = 0,
  medium = 0, low = 0.

## Rendering and Visual Review

- The standard `render_docx.py` route was attempted with the bundled document
  runtime but could not start because LibreOffice/`soffice` is unavailable in
  this environment.
- A hidden, read-only Word COM export completed within the 90-second watchdog
  and produced `tmp/word_render_r41/r41.pdf`.
- `pdftoppm` could not resolve the local path, so the bundled Python runtime
  plus the existing local PyMuPDF QA dependency rasterized all 24 PDF pages at
  144 DPI under `tmp/word_render_r41/pages/`.
- Visual review of every page through four contact sheets, with full-resolution
  inspection of the related-work and reference pages, found no clipping,
  overlap, missing glyph, broken table or figure geometry, raw LaTeX, or
  header/footer defect. The added citation is legible on page 16.

## Remaining Gates

- The v3 fairness/sensitivity batch remains incomplete and cannot yet alter
  the manuscript results.
- Author metadata, archive/licence approval, a freshly verified official
  template, final template conversion, and template-specific visual QA remain
  required before submission.
