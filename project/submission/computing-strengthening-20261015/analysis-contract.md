# Analysis and figure contract

Backend: Python, continuing the existing project workflow. Journal: Computing.
Final figure width: 119 mm; body labels >=8 pt; PDF embedded TrueType + editable
SVG + 300 dpi PNG previews. No artificially generated quantitative data.

## Terminology ledger
| Canonical term | Meaning |
|---|---|
| selection resolution W | number of worlds used to select seeds |
| full greedy | exhaustive candidate scan per round for the named finite objective |
| candidate pool C | eligible seeds; propagation graph remains complete |
| step coupling | deterministic edge-time randomness, archived implementation |
| fixed-edge coupling | one edge state per world; separately labelled control |
| incremental spread | total activated nodes minus k seeds |
| path | pseudorandom selection/evaluation stream realization, not a network replicate |

## Figure contracts (quantitative grids)
1. Reference stability: compare Jaccard changes to incremental utility across W.
   Use all ten real-network paths at k5; uncertainty over paths, not network population.
2. Main candidate effect: all six candidate types and four networks at W5120.
   Mean paired differences + bootstrap intervals across paths. Random repeats averaged
   within path. Negative values favour full; zero-crossing is not equivalence.
3. Cost/tolerance: show every main per-path mean effect vs matched selection saving;
   second panel shows fraction satisfying descriptive tolerance, no superiority ranking.
4. Sensitivity: all predefined p/h changes and both couplings, at matched W320;
   all methods retained in source tables, weighted4k singled out for a labelled
   diagnostic panel, not because of outcome. Synthetic instances labelled explicitly.
5. Timing: all 5 additional repeats for every real graph and arm; split select/eval
   phases, no comparison to historical Python speedup.

All 520 conditions and 4680 arm executions remain in tables regardless of plots.
No outcome-based exclusion. Main graph comparisons are conditional on four fixed
networks; synthetic structure panels do not enlarge the empirical sample size.
