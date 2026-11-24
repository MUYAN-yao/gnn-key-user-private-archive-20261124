# Influence Maximization v2-T0 Preregistration

Date: 2026-07-28

## Purpose and Scope

This protocol evaluates the fixed temporal edge-probability candidate `T0` in
the Higgs influence-maximization workflow. It is authorized because
`analysis/edge-prediction-v2-t0-gate-v2/gate_decision.json` records that T0
passed every preregistered numerical outer-test gate. The candidate-selection
grid was not completed. Consequently this is a `v2-T0` fixed-candidate study,
not an architecture-selection or optimal-model result.

All frozen `v1` files, source code, configurations, results, manifests, and
claims remain unchanged. New code must be isolated under an explicit `v2_t0`
name and new outputs must be created only in
`results/large-robust-greedy-higgs-50000-v2-t0/`. The study uses Higgs only:
Digg remains excluded from probability-mechanism claims because its parent
links are exposure proxies.

## Fixed Inputs

- Dataset: the exact processed Higgs 50k input hashed in
  `reproducibility/frozen-study-manifest-v1.json`.
- Outer train fractions: `0.60`, `0.65`, and `0.70`.
- Random seeds: `42` through `51` inclusive.
- T0 model: one GATv2 layer, hidden width 32, 10 epochs, learning rate 0.01,
  concatenation-MLP decoder, and isotonic score calibration.
- Influence configuration inherited unchanged from v1: two selected seeds,
  horizon 4, IC diffusion, risk lambda 0.35, community weight 0.25,
  20 simulations, robust greedy optimizer, and candidate pool size 120.

No component above may be tuned after the first v2-T0 run is created.

## Time-Forward Probability Construction

For each outer fraction, form the same full outer-training graph used by v1
and reserve the final `1-f` interactions as a completely untouched outer test
window. Within the outer-training interval, use the first 64% as encoder
history, the next 16% as supervised future-edge labels, and the final 20% as
the calibration window.

1. Build node features and message-passing edges from encoder-history edges
   only.
2. Train T0 only on the supervised future-edge labels. Its negative sampler
   may inspect absence only through the supervised-label cutoff.
3. Fit isotonic calibration only on the final calibration window using the
   balanced positive/never-observed-pair procedure defined in
   `edge_prediction_v2_preregistration.md`.
4. Score every unique directed edge present in the full outer-training graph,
   using embeddings derived solely from encoder history. Transform scores with
   that split's fitted calibrator and clip the resulting probabilities to
   `[0.02, 0.98]`, matching v1's fixed diffusion-probability bounds.
5. Supply the unchanged full outer-training graph and these probabilities to
   the optimizer and every baseline. No outer-test edge, feature, label,
   timestamp, or derived statistic may enter training, calibration, scoring,
   candidate construction, or diffusion simulation.

Using the full outer-training graph is deliberate: it preserves v1's decision
time graph and baseline parity. The later supervised and calibration windows
are known before seed selection, but are never supplied as encoder edges.

## Selection and Evaluation

The node prior is v1's formula evaluated with T0 probabilities:
the mean outgoing calibrated probability multiplied by the log of the
weighted out-degree, then normalized by its maximum. The robust greedy method
and the following v1 baselines use this same full graph and the same T0
probabilities: Degree, PageRank, k-shell, GNN Top-K, greedy Monte Carlo, and
RIS approximation. All seed sets in a run use the identical 20 common random
diffusion streams produced from the run seed.

The primary comparisons are paired robust-objective differences between
`gnn_guided_robust_greedy_v2_t0` and each baseline, within each outer fraction
across the ten run seeds. The exact two-sided sign-flip test is computed on
those paired differences; Holm correction covers the 18 planned
method-by-fraction contrasts. Mean spread, objective standard deviation,
community coverage, seed sets, and selection duration are reported alongside
the primary objective.

The outer test interactions are not a diffusion ground truth and are not used
to compute the influence objective. They are retained only for the separately
completed probability-validity gate. This study therefore tests optimization
behavior under a temporally validated probability construction, not causal
real-world spread.

## Reproducibility and Stop Rules

- Use the deterministic controls and fixed seeds from
  `edge_prediction_v2_preregistration.md`.
- Hash the three input CSVs, `model_v2.py`, the v2-T0 pipeline/runner, this
  protocol, and every per-run result before aggregation.
- Refuse a non-empty output directory; never resume by overwriting a result.
  A deliberate `--resume` mode may reuse byte-valid per-run JSON only after
  their hashes are recorded in a run manifest.
- Stop and report rather than retrying if any run fails, a data hash differs
  from the frozen manifest, or a leakage assertion fails. Do not modify model
  parameters, optimizer parameters, candidate-pool size, or experiment output
  after a stop.

## Claim Boundary

Allowed after a complete successful run: conditional statements about the
fixed T0 probability construction and the declared Higgs v2-T0 protocol.

Forbidden: claims of universal superiority, global architecture optimality,
causal edge or diffusion probabilities, validation on Digg, or replacement of
the frozen v1 results.
