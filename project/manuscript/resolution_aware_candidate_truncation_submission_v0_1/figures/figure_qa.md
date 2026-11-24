# Main figure package

Four figures now accompany two main-text tables. All figures are generated with the existing Python/matplotlib workflow; no training or new simulation was performed.

## Figure contract

1. Fig1: schematic-led computational information flow. Explains why candidate restriction, finite selection worlds, independent evaluation, and time address different questions. It is not a causal mechanism claim or an empirical network diagram.
2. Fig2: quantitative reference-sensitivity panels. Shows all 14 tie-rate trajectories, pooled round counts, and the two changed-trace counts.
3. Fig3: complete binary agreement matrix. Includes all 126 restricted-arm comparisons, without selecting favorable networks or budgets.
4. Fig4: computation–utility scatter panels. Includes all 126 comparisons, retaining overlaps and observed negative time savings.

## Sources and checks

The source hashes and row counts are in source_provenance.json. The plotting source is analysis/build_computing_main_figures.py. Inputs are the previously admitted summary, trajectories, and condition-level profile. Raw execution evidence was not changed.

Static preflight: zero failures. The PNG-without-TIFF warning is accepted because editable PDF/SVG are the line-art deliverables and PNG is a preview. The width warning is a static-parser false positive on the expression 174/25.4: actual width is 174 mm, not 4419.6 mm. All figures have fixed dimensions, editable SVG/PDF text, and 600-dpi PNG previews. PNGs were visually inspected for clipping, glyph loss, crowded labels, and consistency; a missing subset glyph was replaced before final rendering.

No confidence intervals, population tests, trend fits, smoothing, artificial observations, or subsampling were added. Colors are backed by shapes or literal symbols, where needed. Figure 2 pooled tie rates weight rounds, not blocks equally; this is stated in its caption. Figure 4 uses common axes across budgets.

## Journal comparison

The publisher preview of Konidaris et al., Computing (2026), DOI 10.1007/s00607-026-01743-9, lists ten figures and two algorithms:
https://link.springer.com/article/10.1007/s00607-026-01743-9

This is an example of multi-figure presentation, not evidence of a universal four-figure minimum. The previous three-panel summary remains in the analysis archive; it has been replaced in the main text to avoid repeating the same evidence as a fifth figure.

Final template placement and readability at the journal's eventual scaled size still need verification during LaTeX layout.
