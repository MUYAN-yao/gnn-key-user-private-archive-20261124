# Figure Catalog

## Figure 1: Future AUC by Seed

- File: `figures/figure-01-future-auc-by-seed.pdf`
- Purpose: show the full seed-level temporal ranking distribution rather than
  only a mean.
- Data source: `audits/higgs-edge-prediction-v1/audit_report.json`.
- Caption requirements: state 10 seeds per cutoff, point meaning, and dashed
  random-ranking reference. Report numerical means and 95% t-CIs in the
  accompanying table rather than obscuring the points with overlapping bands.
- Key observation: seeds 42 and 48 fall below 0.5 in all three cutoff panels.
- Interpretation checklist: readers should see that a favorable mean does not
  imply a stable probability model; the next decision is to version a repair
  protocol before causal probability claims.

## Figure 2: Train-to-Future AUC Gap

- File: `figures/figure-02-train-to-future-gap.pdf`
- Purpose: contrast reconstruction accuracy with time-forward predictive
  accuracy for every stochastic run.
- Data source: `audits/higgs-edge-prediction-v1/audit_report.json`.
- Caption requirements: identify paired seed lines, red below-random future
  runs, and the random-ranking reference.
- Key observation: high reconstruction AUC does not rule out reversed future
  ranking.
- Interpretation checklist: this changes the claim boundary from "predictive
  edge probabilities" to an unvalidated heuristic pending a new protocol.
