# Edge-Prediction v2 Preregistration

Date: 2026-07-28

## Purpose and Separation From v1

This protocol tests whether a revised edge-probability model can make stable,
calibrated, time-forward predictions. It does not revise, overwrite, or
reinterpret frozen `v1` outputs. Any implementation and output created under
this protocol must use a new `v2` path and preserve the v1 manifest hashes.

The immediate target is the processed Higgs 50k dataset. Digg's parent links
are exposure proxies, so it cannot establish causal re-share prediction and is
not used to pass this probability-validity gate.

## Predeclared Questions

1. Can a model trained at an earlier temporal cutoff rank subsequent observed
   Higgs edges above absent directed pairs?
2. Does that result hold for every predeclared training seed, rather than only
   on average?
3. Are the resulting scores calibrated well enough to be used as diffusion
   probabilities?

## Data Splits and Isolation

For each outer train fraction `f` in `{0.60, 0.65, 0.70}`:

1. Sort interactions chronologically and reserve the final `1-f` for the
   untouched outer test window.
2. Split the outer training window chronologically into 64% configuration-fit,
   16% configuration-validation, and 20% final-calibration windows.
3. Construct graph features and message-passing edges only from the relevant
   model-fit window. The model must never receive a later window's edges,
   weights, timestamps, or features derived from them.
4. Choose architecture and optimization settings once by mean raw AUC on the
   configuration-validation window across the 10 seeds and all three outer
   fractions.
5. For each outer fraction and seed, fit the selected model on the first 80%
   of the outer-training window, fit any score calibrator on predictions from
   the final-calibration 20%, and evaluate once on the untouched outer test.
   The calibrated model never trains on calibration or outer-test labels.

Within every model-fit window, reserve its earliest 80% as the encoder-history
window and use the following 20% only as supervised future-edge labels. The
encoder sees only the history graph; the classifier is trained to distinguish
observed edges in the supervised window from pairs absent up to that window's
cutoff. Thus `v2` is a temporal prediction objective, not training-edge
reconstruction. For final outer evaluation this yields: 64% history graph,
16% supervised future-edge labels, 20% calibration, and the untouched outer
test window.

## Labels and Metrics

- Positives: unique observed directed edges in the relevant held-out window.
- Negatives: an equal number of uniformly sampled non-self pairs with no
  observed interaction anywhere in the fixed collection horizon. Full-horizon
  absence is permitted only for evaluation labels, never as a model feature or
  training signal.
- Training negatives: uniformly sampled non-self pairs absent up to the end of
  the supervised-label window. Later edges are not consulted during training
  negative sampling.
- Primary metric: ROC-AUC on outer-test edges.
- Secondary ranking metric: average precision.
- Calibration metrics: Brier score and 10-bin ECE, accompanied by a reliability
  diagram.
- Baselines: prevalence predictor and a recency-weighted degree score. A model
  must beat the prevalence predictor on Brier score to support a probability
  claim.

## Determinism and Seeds

- Fixed seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51`.
- Set `PYTHONHASHSEED`, Python `random`, NumPy, PyTorch CPU, and CUDA seeds.
- Set `CUBLAS_WORKSPACE_CONFIG=:4096:8`, disable cuDNN benchmarking, enable
  deterministic cuDNN, and call `torch.use_deterministic_algorithms(True)`.
- Before the pilot, run seed 42 twice on one split. If the predicted scores
  differ by more than `1e-7`, run the validation pilot on CPU and record the
  device change. Do not call a GPU result deterministic merely because its
  seed was set.

## Candidate Model Selection

The implementation may compare only the following predeclared choices:

| Component | Values |
| --- | --- |
| Encoder depth | 1 or 2 temporal GATv2 layers |
| Hidden width | 32 or 64 |
| Training epochs | 10, 30, or 60 |
| Learning rate | 0.001 or 0.01 |
| Edge decoder | existing concatenation MLP or bilinear decoder |
| Probability calibration | isotonic calibration fitted only on the final-calibration window |

The selected architecture/optimization configuration is the one with highest
mean raw validation AUC. Probability calibration is fixed to isotonic
regression and is fitted only after that selection. Ties select the smaller
model, then fewer epochs, then the lower learning rate in that order.

## Acceptance Gates

All gates must pass on the untouched outer tests for **each** outer fraction.

1. Every seed has ROC-AUC strictly greater than 0.50.
2. The seed-mean ROC-AUC has a 95% t-confidence lower bound above 0.55.
3. Across-seed ROC-AUC SD is at most 0.05.
4. Mean Brier score is below 0.25 on the balanced evaluation set and below the
   prevalence baseline; mean ECE is at most 0.10.
5. Inverted-score ROC-AUC is below 0.50 for every seed.

## Stop Rules

- If any gate fails, save the pilot artifacts and report the failure. Do not
  rerun influence maximization or present the model as a probability-valid
  `v2` repair.
- If all gates pass, freeze source/configuration hashes, repeat the audit on
  the full 10 seeds, and only then propose a separately versioned influence
  experiment. Candidate-pool size, diffusion simulations, baselines, and
  temporal fractions must remain identical to v1 unless a new preregistration
  explicitly changes them.
- No v2 outcome, positive or negative, changes the frozen v1 claim table.

## Required Artifacts

- `audits/edge-prediction-v2-pilot/`: per-seed scores, predictions summary,
  calibration curves, gate decision, environment, and hashes.
- `protocols/edge_prediction_v2_preregistration.md`: this document, copied
  unchanged into the pilot directory.
- A manifest that hashes data, source code, selected configuration, and every
  pilot artifact before any full experiment is authorized.
