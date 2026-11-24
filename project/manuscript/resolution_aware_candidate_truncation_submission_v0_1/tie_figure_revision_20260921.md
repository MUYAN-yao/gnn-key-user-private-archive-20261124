# Tie-figure revision and denominator correction

Main Figure 3 now shows pooled tie proportions and post-hoc unordered final-set change counts. Supplementary Figure S1 displays all 14 trajectories in seven network/seed-budget facets; all 42 budget observations are exported as CSV. No observations were removed.

Recalculation revealed an erroneous hard-coded denominator of 190 in the preceding plot and prose. The correct denominator is 160: eight k=5 traces contribute 40 rounds and six k=20 traces contribute 120. Numerators remain 80, 46 and 21, giving 50.0%, 28.75% and 13.125%. Frozen experimental outputs are unchanged. The manuscript, supplement, active analysis readout and figure/report generators were corrected. Historical manuscript and figure backups retain their old content and must not be used for submission.

Source mapping: full_trajectories.json supplies k, world_path and zero_margin_rounds; summary.json cross-checks the summed numerators; full_set_transitions.csv supplies final-set changes in all 28 transitions. Different denominators are intentional: 160 rounds for tie rates, 14 trajectory blocks for set-change counts. These are descriptive results with dependent observations and no inferential error bars.

Python generates PDF/SVG with editable text and 600 dpi PNG. Both rendered figures were inspected. Static preflight has zero failures; its warnings concern PNG rather than TIFF (vector PDF/SVG are the manuscript masters) and 174 mm rather than its generic 183 mm default (174 mm matches the existing manuscript figures). Full journal-template layout remains a later submission step.
