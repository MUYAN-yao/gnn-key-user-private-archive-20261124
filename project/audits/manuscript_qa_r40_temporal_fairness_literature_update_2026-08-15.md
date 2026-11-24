# Internal Manuscript QA: r40 Temporal-Fairness Literature Update

Date: 2026-08-15

## Scope

This audit covers only the internal review artifact
`manuscript/temporal_key_user_identification_internal_draft_r40_temporal_fairness_literature_update.docx`.
It does not certify an official *Software Journal* template conversion and it
does not alter frozen experimental outputs.

## Content and Structure

- The source draft, bibliography, citation audit, and related-work matrix add
  Meena, Singh, and Singh (2025 online / 2026 issue) as reference `[32]`.
  Its use is restricted to title/metadata-scoped temporal-fairness context.
- The DOCX contains the new body citation and a numbered `[32]` reference.
- `python-docx` inspection reports 185 paragraphs, 5 tables, 1 section, and
  32 numbered references.
- Heading audit: 22 `Heading 1` paragraphs and 12 `Heading 2` paragraphs.
- Image audit: 6 inline figures with explicit dimensions.
- Accessibility audit output is `audits/r40_docx_a11y.json`: high = 0,
  medium = 0, low = 0.

## Visual QA

The canonical document renderer could not start because `soffice` is absent.
As a secondary controlled rendering path, Word opened the source read-only and
exported `tmp/word_render_r40/r40.pdf`; Poppler rasterized 23 pages at 150 DPI.
Each page was inspected. No clipping, overlap, missing glyphs, broken table or
figure geometry, raw Markdown/LaTeX, or misplaced header/footer was observed.

The final page has intentional whitespace after the short pseudocode appendix;
it contains no clipped or misplaced content.

## Remaining Gates

- The formal v3 fairness/sensitivity batch remains in progress and cannot be
  cited as performance evidence until all 30 non-smoke artifacts and the final
  manifest pass the strict analysis builder.
- Author-controlled metadata, raw-data redistribution terms, archival
  approval, current official template retrieval, and official-template QA
  remain outstanding.
