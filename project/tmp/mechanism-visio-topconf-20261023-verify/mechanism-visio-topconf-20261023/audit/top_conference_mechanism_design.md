# Mechanism-figure design record

## Design decision

The previous overview placed every audit item in a separate rectangular panel.
That format preserved detail but obscured the scientific mechanism: readers had
to read the cards before seeing why the two resolution choices could affect the
same comparison. The revised Figure 1 is a single, vertically ordered mechanism
map whose reading path is:

1. a fixed diffusion graph and a visibly truncated candidate ranking;
2. two explicitly distinct perturbation routes: finite reference budget $W$ and
   numerical ranking tolerance $\tau$;
3. matched selection followed by a disjoint, independent utility readout; and
4. agreement, utility and cost as three non-interchangeable outputs.

This makes the paper's central evaluative claim visible before readers encounter
the detailed protocol. It does not add a new causal theory or change any result.

## Top-conference visual grammar used

- **One visual question per figure.** The headline states the tension, not a
  generic process name: one candidate-restriction comparison has two resolutions.
- **A concrete object before abstraction.** The graph, cutoff and candidate
  ordering appear before $W$, $\tau$ or the spread contrast.
- **Few semantic colors.** Blue is finite-reference resolution, teal is the
  restricted pool/independent readout, orange is the near-cutoff tolerance path;
  neutral gray is shared computation. Color is not used as decoration.
- **A converging dependency structure.** The two paths enter the same matched
  comparison and then the same fresh-world utility readout. This is more legible
  than presenting the factors as unrelated checklists.
- **A compact empirical anchor.** The ca-GrQc count is present but does not
  attempt to replace the quantitative precision plot or make a visual claim of
  effect size.
- **Caption carries qualifications.** The diagram stays readable; the caption
  states the post-hoc identity, the link to the numerical figure and the fact
  that arrows are computational dependencies rather than a causal diffusion
  model.

## Presentation references

The layout draws only on general presentation principles, not on visual assets or
scientific claims, from:

- Vaswani et al., *Attention Is All You Need*, NeurIPS 2017, Fig. 1:
  aligned components, directional flow and concise module names.
  https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
- Jumper et al., *Highly accurate protein structure prediction with AlphaFold*,
  Nature 2021, Fig. 1e: an information-flow diagram that separates major
  component families before detailed quantitative evidence.
  https://www.nature.com/articles/s41586-021-03819-2

No panel, icon, source artwork or distinctive layout has been copied. These are
design references only and are not cited as scientific support in the manuscript.

## Integrity boundary

The small graph, scores, seed sets and world cards are explanatory glyphs. The
only empirical statement shown inside the diagram is the ca-GrQc count; it is
checked by `src/prepare_figure_assets.py` against the validated source CSVs.
All quantitative claims remain traceable to the frozen external-validation
outputs and the existing numerical figures.
