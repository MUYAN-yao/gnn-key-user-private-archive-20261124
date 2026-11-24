# Figure catalog and QA contract

Figures 1--3 and S1 show the frozen main matrix with default PageRank tolerance.
Figure 4 is the separately frozen post-hoc tightened-tolerance diagnostic. Its
strict values must not be silently substituted into the frozen default-tolerance
cost or coupling curves.
Python/matplotlib quantitative grids, 119 mm width; editable PDF/SVG, 300 dpi PNG
preview. Raster previews are not submission masters; no TIFF is required for
these vector charts. Font size is at least 8 pt. Width-preflight warning is a
literal-expression parser error (119/25.4 inches is exactly119 mm); PDF MediaBox
is checked independently. Log x-values are the positive budgets80,320,1280.

| Figure | Claim | Statistics and source |
| --- | --- | --- |
| Fig1 | Ranking/coverage loss depends on topology and budget | Each point mean of five paths; bars are path SD; random repeats averaged first; Fig1_source.csv |
| Fig2 | Set changes and independent gains differ | All five paths for each graph and adjacent budget pair; filled circles changed set, hollow squares same set; bars unadjusted conditional MC95%; Fig2_source.csv |
| Fig3 | Large speed savings do not ensure tolerated loss | Counts of five paths passing point-estimate tolerances at W1280; label is mean hybrid verification saving across all five; not a noninferiority test; Fig3_source.csv |
| Fig4 | Default PageRank budget patterns can differ from strict-ranking patterns | Six panels: 3 graphs × 2 PageRank pool sizes; default versus strict tolerance; points are five-path means, bars path SD; post-hoc diagnostic; analysis/precision_budget/figures/precision_budget_loss_figure_source.csv |
| FigS1 | Coupling control preserves key losses but changes some references | Three preselected paths, W320; circle step/square fixed-edge; no inferential bars; FigS1_source.csv |

No train/validation optimization uses final evaluation worlds. No image manipulation
or data exclusions beyond the stated stage/method selections; complete tables keep
all methods, budgets and coupling controls. See qa/visual-review.md for actual
render inspection; source preflight alone is not a visual-quality certificate.
