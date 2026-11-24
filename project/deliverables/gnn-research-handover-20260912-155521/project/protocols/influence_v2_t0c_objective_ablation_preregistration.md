# Influence Maximization v2-T0c Objective-Ablation Preregistration

Date: 2026-07-31

## Purpose

This is a separately versioned ablation of the completed strict Higgs
v2-T0b study. It tests whether the two explicit selection-objective terms
change the seeds selected by the fixed GNN-guided robust-greedy procedure.
It is not a re-analysis of the historical 5,000-node ACO pilot and it does
not modify any v1, v2-T0, or v2-T0b artifact.

The reference selection objective is

`J_full(S) = mean_spread(S) - 0.35 * spread_std(S) + 0.25 * community_coverage(S)`.

## Frozen Inputs and Inherited Protocol

- Dataset: the hash-verified Higgs `pilot-50000` input used by v2-T0b.
- Outer fractions: 0.60, 0.65, and 0.70.
- Seeds: 42 through 51, paired with the completed v2-T0b reference run of the
  same fraction and seed.
- Timestamp windows: the v2-T0b timestamp-grouped history, supervised,
  calibration, and outer-test windows. Every boundary must remain strictly
  forward in time.
- Model and decision constants: T0 GATv2 encoder, isotonic calibration,
  candidate pool 120, two selected users, IC horizon 4, 20 simulations, and
  the v2-T0b common-random-number stream rule.
- The completed v2-T0b 30-run directory is read-only. Its run hashes are
  checked before an ablation artifact may be written.

## Selection Arms

The complete v2-T0b arm is reused as the reference. Exactly these three new
arms are run; no additional arm may be added after results are inspected.

| Arm | Selection risk lambda | Selection community weight | Question |
| --- | ---: | ---: | --- |
| `risk_off` | 0.00 | 0.25 | What changes when the risk penalty is removed? |
| `community_off` | 0.35 | 0.00 | What changes when the community reward is removed? |
| `spread_only` | 0.00 | 0.00 | What changes when both explicit terms are removed? |

## Reporting and Statistics

Each new seed set is evaluated on the same 20 common random diffusion streams
under the fixed full objective `J_full`, irrespective of the arm used for
selection. The artifact additionally reports mean spread, spread standard
deviation, community coverage, and all four objective decompositions. This
keeps the primary cross-arm score constant.

For each fraction and each non-reference arm, the primary contrast is
`J_full(v2-T0b reference) - J_full(ablation arm)` across its ten matched
seeds. The planned family has 9 contrasts (3 fractions x 3 arms). Use an exact
two-sided sign-flip test with Holm correction over this 9-contrast family,
and report paired mean difference, 95% t interval, paired Cohen dz, and
win/tie/loss counts. A positive difference favors the complete objective.

The runs quantify stochastic protocol variation, not independent social
networks. No causal, universal, cross-dataset, or post-hoc optimality claim is
allowed.

## Integrity Rules

- Outputs must be under a new directory whose name contains `v2-t0c`.
- The runner refuses a non-empty output directory without `--resume` and never
  overwrites a run artifact.
- Each output manifest hashes the inputs, protocol, runner, relevant source
  files, the referenced v2-T0b manifest, and every new run artifact.
- A dry-run may validate inputs and reference provenance but must create no
  experiment output.
