# Final PDF visual review — 2026-10-15

Actual rendered pages were viewed after the final two-pass compilation. Main manuscript: 17/17 pages. Online Resource 1: 9/9 pages. PDF hashes are bound to this review by render_checks.json and final_checks.py.

- Main pages 1–4: title, abstract, author-verification notice, citations, equations and method text fit the unchanged journal class.
- Main pages 5–8: audit/timing definitions, historical layers, dataset table, preprocessing, precision protocol and primary table have no clipping or overlap.
- Main pages 9–13: all three figures, transitions table, cost table and precision interpretation were inspected. Pages 10 and 13 were additionally viewed at the full rendered resolution. The error bars in Figure 1 fit the axes after extending the lower limit to -15; negative losses are retained. Figure 3 explicitly identifies the default-tolerance matrix and hybrid cost estimates.
- Main pages 14–17: limitations, conclusion, pending author declarations and all references are visible and contained within the page. The final reference page is short but intentional; no layout compression was applied.
- Supplement pages 1–4: provenance, uncertainty, timing and primary tests/first full matrix table are legible and complete.
- Supplement pages 5–7: remaining full matrix tables and the precision-control table are complete. Page 7 was additionally viewed at full rendered resolution: Table 5 distinguishes comparisons with full greedy from comparisons with the default PageRank solver, and records the original paths rather than extra samples.
- Supplement pages 8–9: coupling figure and reproduction/author-action text are complete. Page 9 is a short continuation, not an omitted figure or rendering failure.

No visible cut text, overlapping labels, clipped tables, missing glyphs or unresolved references were found. Machine checks independently report no overfull boxes, undefined citations/references, text outside page bounds or unresolved markers. Abstract: 226 words; keywords: 5; references: 23, all cited. Template class and option file are byte-identical to the historical journal template. Author declarations intentionally remain pending and prevent treating this draft as approved for submission.

The vector PDF/SVG figure masters are preserved; PNGs are inspection previews. Contact sheets cover every page and full-page images remain in qa/manuscript and qa/Online_Resource_1. Any later manuscript change requires new compilation and visual review.
