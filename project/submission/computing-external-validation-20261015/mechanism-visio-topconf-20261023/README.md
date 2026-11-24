# Visio mechanism-figure revision — 2026-10-23

This independent version adds two native editable Visio figures and integrates
them into the existing Computing manuscript. The earlier submission-preparation
package and all frozen experimental results are preserved.

## Open first

- `figures/evaluation_mechanisms.vsdx`: two native editable Visio pages.
- `figures/mechanism_overview.pdf`: main computational-mechanism overview.
- `figures/coupling_counterexample.pdf`: supplementary timing counterexample.
- `manuscript/manuscript.pdf`: revised main text; new mechanism is Figure 1.
- `manuscript/Online_Resource_1.pdf`: revised online resource; counterexample is Figure 2.
- `audit/top_conference_mechanism_design.md`: mechanism-figure design record and
  presentation references.
- `audit/design_reference_and_evidence.md`: earlier design/evidence record,
  retained for provenance; superseded for Figure 1's visual design by the new
  design record.

SVG, PNG, high-resolution PDF previews, drawing script and shape inventory are
included. No whole-page bitmap is embedded in the `.vsdx`. Native Visio PDF export
was unavailable, so manuscript PDFs were converted from Visio's exported SVG using
the documented vector-preserving route. Quantitative plots were not redrawn.

## Revision scope

Main Figure 1 uses one continuous mechanism narrative rather than a collection
of audit cards: a fixed propagation graph is first restricted by a visible
candidate cutoff; finite reference budget moves the full reference, while ranking
tolerance changes near-cutoff eligibility; their resulting seed sets are then
resolved only by independent spread evaluation. The small ca-GrQc statement is an
observed anchor, not a substitute for the quantitative precision figure. The
supplementary figure explains the existing chain counterexample. Introduction and
Methods introduce this mechanism before its formal details. All effect sizes,
post-hoc labels, uncertainty definitions and external-validity limits are retained.

## Reproduce

1. Run `src/draw_mechanisms.ps1` on Windows with Visio installed.
2. Run `src/prepare_figure_assets.py` with PyMuPDF and access to the prior validated
   package at its sibling location. It checks the observed pool IDs and numbers,
   verifies native shapes, and converts the SVGs into vector PDFs.
3. Compile both TeX documents twice in the flat `manuscript` directory.
4. Run `src/render_and_check.py` and inspect the QA page renders.

This is a figure-and-writing revision, not a new experiment. The earlier package
contains full sources, original arrays and statistical analyses. This compact
delivery contains the drawings, updated TeX/PDF and QA required to review this change.
