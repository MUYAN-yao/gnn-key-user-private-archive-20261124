# Influence Maximization v2-T0d Common-World Objective-Ablation Preregistration

Date: 2026-07-31

## Reason for a New Version

The first v2-T0c ablation artifact reproduced the strict timestamp windows and
selected seed set of its v2-T0b reference, but its re-evaluated objective did
not equal the archived reference objective. Inspection identified a
cross-process reproducibility defect in the inherited simulator: traversal of
Python sets can consume an otherwise identical pseudorandom stream in a
different order. The incomplete v2-T0c directory is retained as a failed
infrastructure audit and is not evidence.

v2-T0d makes the objective ablation internally identifiable. For every
fraction-seed pair it trains the fixed T0 probability model exactly once, then
selects all arms from that same probability map and scores every arm on the
same deterministic edge-time possible worlds. It does not alter v1, v2-T0,
v2-T0b, or v2-T0c artifacts.

## Frozen Inputs and Shared Conditions

- Dataset: hash-verified Higgs `pilot-50000` input.
- Fractions: 0.60, 0.65, and 0.70; seeds 42--51.
- Windows: the strict v2-T0b timestamp-grouped history, supervised,
  calibration, and outer-test windows.
- Model: fixed T0 GATv2 encoder, isotonic calibration, and probability bounds
  inherited from v2-T0b.
- Decision constants: two seeds, IC horizon 4, candidate pool 120, and 20
  evaluation worlds.

## Deterministic Common Worlds

For a diffusion replication, round, source-node rank, and target-node rank,
the Bernoulli uniform is deterministically derived from those four integers by
a fixed SplitMix64-style integer transform. Node frontiers and successors are
traversed in canonical rank order. Thus every arm evaluates a candidate set on
the same edge-time random world regardless of Python process hash state.

This version changes the evaluation randomization implementation only to make
the ablation comparable within run. It is a separate protocol and must not be
pooled numerically with v2-T0b.

## Arms and Primary Contrast

| Arm | Selection risk lambda | Selection community weight |
| --- | ---: | ---: |
| `full` | 0.35 | 0.25 |
| `risk_off` | 0.00 | 0.25 |
| `community_off` | 0.35 | 0.00 |
| `spread_only` | 0.00 | 0.00 |

All selected sets are reported under the common full objective
`mean_spread - 0.35 * spread_std + 0.25 * community_coverage`. For each
fraction, compare `full - arm` for the three non-full arms across the ten
matched runs. Use exact two-sided sign-flip tests and Holm correction across
the prespecified 9 contrasts; report paired differences, 95% t intervals,
paired Cohen dz, and win/tie/loss counts.

## Integrity Rules

- The output directory name must contain `v2-t0d` and must not overwrite
  existing artifacts.
- Each artifact records all four selections, the shared probability/model
  protocol, timestamp boundaries, full-objective evaluations, and whether the
  v2-T0d full selection matches the read-only v2-T0b archived seed set.
- The run manifest records input, protocol, reference-manifest, source, and
  artifact hashes. A dry-run writes no output.
- No conclusion may claim that v2-T0d is numerically interchangeable with
  v2-T0b; it supplies a separately versioned objective-ablation test only.
