# Internal r43 DOCX Audit

## Scope

- Document: `manuscript/temporal_key_user_identification_internal_draft_r43_literature_update.docx`
- Date: 2026-08-24.
- Change under review: insertion of the full-text-backed Yang et al. (2024)
  temporal-k-shell related-work comparison and reference [34].

## Structural and Accessibility Checks

| Check | Result |
| --- | --- |
| Build | succeeded with the bundled document Python runtime |
| Paragraphs (python-docx body collection) | 193 |
| Tables | 5 |
| Inline figures | 6 |
| Reference [34] | present exactly once |
| Accessibility audit | high/medium/low = 0/0/0 |

## Word Export Check

Microsoft Word COM opened the DOCX read-only and exported
`tmp/word_render_r43/r43.pdf` successfully. Word reported 25 pages, 5 tables,
and 6 inline shapes; the exported PDF is nonempty (1,061,478 bytes).

## Visual-QA Boundary

The document renderer cannot create page PNGs because LibreOffice (`soffice`)
is unavailable and the bundled `pdftoppm` wrapper lacks its expected native
Poppler executable. This audit therefore does not certify page-level visual
layout. The final official-template DOCX must still receive a complete
page-by-page visual review in a working renderer.

## Integrity Boundary

The audit and r43 build changed manuscript and audit artifacts only. No model
configuration, data, frozen result, or experiment output was changed.
