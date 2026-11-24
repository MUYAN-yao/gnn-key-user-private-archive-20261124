# Figure logic and primary design references

## Design contract

Core conclusion: reference budget and ranking tolerance enter at different
points of a candidate-restriction evaluation, so agreement, independent utility
and computational cost must be interpreted separately.

Archetype: schematic-led overview, with an observed candidate-pool inset and a
separate analytical mechanism illustration. Drawing backend: native Microsoft
Visio COM, as explicitly requested. White canvas, three restrained color families,
direct labels, arrows and panel letters. Typography is sans serif for figure
labels, while the paper retains the journal's normal typeface and page geometry.
No source artwork, logo, screenshot or raster crop is included in the Visio file.

## Primary sources consulted for presentation

- Jumper et al., Nature (2021), Figure 1e, model architecture.
  https://www.nature.com/articles/s41586-021-03819-2
  The figure caption identifies arrows as information flow among components and
  uses component/array labels. Borrow the principle of explicit dependencies,
  not the biological content or the distinctive visual composition.
- Vaswani et al., NeurIPS (2017), Figure 1 and Sections 3--3.2.
  https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
  The architecture uses aligned modules and directed links, with explanatory
  prose moving from overall architecture to component operations. Apply this
  presentation pattern to existing evaluation logic; no new algorithm is implied.

## Scientific evidence map

| New panel | Evidence identity | Source | Permitted reading |
| --- | --- | --- | --- |
| Main a | Method definition | Existing Methods, frozen protocol and configuration | W changes the sampled selection objective; tau may change the truncated pool; evaluation is independent of selection. |
| Main b | Observed post-hoc numerical control | Prior `candidate_pool_precision_diagnostics.csv`, `summary_by_budget_precision.csv`, `tolerance_effects_summary.csv` | ca-GrQc changes two of 20 candidates; 18 remain shared; default/strict differences are -0.25082/+0.02608 at W1280, and five selected sets change. |
| Main c | Reporting distinction | Existing metrics/timing definitions | Agreement, independent utility and scoped costs answer different questions. |
| Supplement mechanism | Illustrative analytical counterexample | Existing main-text chain with h=2 | A realized step-indexed objective can be nonmonotone; no broader submodularity or marginal-law conclusion follows from the example. |

The observations in panel b were checked by `src/prepare_figure_assets.py` against
the prior validated CSVs. There is no invented network result and no new empirical
experiment. Prior data and statistical outputs remain in the original package.

## Export route and QA

Visio's fixed-format PDF API failed on this installation. The source of truth is
the two-page native `.vsdx`; SVG and PNG were exported directly from it. For the
manuscript PDF, Visio CSS styles were materialized as SVG presentation attributes,
Arial was mapped to the metrically equivalent Helvetica family, and the vector
content was converted with MuPDF at 119 mm width. Native line-shape arrowheads
avoid unsupported SVG marker references. The conversion contains no raster images;
text remains selectable. Both the Visio PNG and converted PDF were visually checked.

## Terminology

Use candidate pool C, full eligibility V, selection budget W, tolerance tau,
disjoint evaluation worlds eta, and paired difference Delta throughout the figure.
The caption maps these plain-text Visio labels to mathematical notation. The
graph in overview panel a is schematic; the IDs in panel b are observed IDs.
