# Influence Maximization v3 Fairness and Sensitivity Preregistration

Date: 2026-08-15

## Scope and Version Boundary

This protocol is a new confirmatory study. It does not alter or numerically
pool results from frozen v1, v2-T0b, invalid v2-T0c, or v2-T0d artifacts.
Every v3 result is stored beneath a new output directory whose name includes
`v3-fairness-sensitivity`.

## Inputs and Fixed Conditions

- Dataset: hash-verified Higgs `pilot-50000` input only.
- Outer training fractions: 0.60, 0.65, and 0.70.
- Repetitions: seeds 42--51, treated as paired stochastic protocol runs rather
  than independent social-network samples.
- Windows: timestamp-grouped history, supervised, calibration, and outer-test
  windows inherited from v2-T0b. Every boundary must be strictly increasing.
- T0: one GATv2 layer, width 32, 10 epochs, learning rate 0.01, concatenation
  MLP decoder, isotonic calibration, and probability bounds `[0.02, 0.98]`.
- Decision constants: two seeds, IC horizon 4, 20 selection worlds, 20
  evaluation worlds, base risk lambda 0.35, and base community weight 0.25.

## Deterministic Random Worlds

Selection worlds and evaluation worlds are generated from different deterministic
seed namespaces. Their values must be disjoint and their SHA-256 digests are
recorded in every run artifact. Diffusion trials use a canonical edge-time
SplitMix64 transform indexed by world, hop, source rank, and target rank, so
the outcome cannot depend on Python set traversal order. Selection uses only
selection worlds; reported comparisons use only evaluation worlds.

## Methods and Questions

1. **Primary screened robust greedy.** Rank nodes with the frozen T0 learned
   prior, retain the top 120 candidates, and greedily optimize
   `mean_spread - 0.35 * spread_std + 0.25 * community_coverage` on selection
   worlds. It does not return the better of this set and GNN Top-K.
2. **Independent full-candidate robust greedy.** Search every decision-graph
   node with the same greedy objective and selection worlds; it uses no learned
   prior. This is the primary fairness comparator.
3. **GNN Top-K audit.** Report the direct prior Top-K score separately as a
   protected lower-bound audit. It is not an independent efficacy baseline and
   is excluded from the primary superiority family.
4. **Candidate-pool sensitivity.** Repeat the screened greedy selection at
   pools 60, 120, 240, and 480. Report full-objective evaluation, selection
   time, and seed-set overlap with the full-candidate robust greedy set.
5. **Objective-weight sensitivity.** For the 3x3 grid `risk lambda` in
   `{0.00, 0.35, 0.70}` and `community weight` in `{0.00, 0.25, 0.50}`, use
   the 120-node screened candidate pool for selection. Evaluate every selected
   set under the common reporting objective `(0.35, 0.25)` and report spread,
   spread standard deviation, community coverage, selected seeds, and overlap
   with the base selected set.

## Statistics and Decision Rules

For every primary or sensitivity contrast, use ten matched runs per fraction,
an exact two-sided sign-flip test, 95% t intervals, paired Cohen dz, and a
Holm correction over the explicit contrast family written by the analysis
script. Do not infer independent-network population effects. No claim of
GNN Top-K superiority or independent risk/community-term benefit is allowed
unless the separately versioned analysis supports it.

## Integrity Rules

- Input files must match the frozen Higgs manifest before a run is allowed.
- The runner refuses non-empty output paths unless `--resume` is explicit and
  never overwrites an existing run artifact.
- `--dry-run` writes nothing. `--smoke` writes only a clearly labelled
  infrastructure audit with a bounded 64-candidate full-search proxy and
  cannot be used by the completed-study analysis.
- The final manifest records protocol, input, source, world-derivation, and
  per-run hashes. Raw source data are not redistributed.
