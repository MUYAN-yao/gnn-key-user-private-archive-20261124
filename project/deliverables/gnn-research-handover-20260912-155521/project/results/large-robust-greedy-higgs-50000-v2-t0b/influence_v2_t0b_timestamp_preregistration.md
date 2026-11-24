# Influence Maximization v2-T0b Timestamp-Grouped Preregistration

Date: 2026-07-28

## Reason for a New Version

The completed v2-T0 smoke test found that positional splitting placed distinct
rows with timestamp `2012-07-03T09:53:03+00:00` on both sides of the
calibration/outer-test boundary. v2-T0 remains an immutable smoke artifact and
is not a formal result. This `v2-T0b` protocol replaces positional boundaries
with timestamp-grouped boundaries before any formal rerun.

## Timestamp-Grouped Windows

For each nominal outer fraction `f` in `{0.60, 0.65, 0.70}`, choose the outer
cutoff from the observed unique timestamps such that all rows with timestamps
strictly less than the cutoff are outer training and all rows with timestamps
greater than or equal to it are outer test. Select the eligible cutoff whose
outer-training row count is closest to `f * N`; ties select the earlier
cutoff. Each subwindow boundary is selected by the same rule from timestamps
within its parent window, targeting 64%, 80%, and 100% cumulative rows of the
outer training interval.

The four windows are therefore: history `[start, t1)`, supervised `[t1, t2)`,
calibration `[t2, t3)`, and outer test `[t3, end]`. Every boundary must have
strictly increasing timestamps and every window must contain at least one
edge. The runner records nominal and achieved row fractions plus all four
boundary timestamps, and aborts before training if any assertion fails.

## Inherited Elements

T0 remains fixed: one GATv2 layer, width 32, 10 epochs, learning rate 0.01,
concatenation MLP, and isotonic calibration. Higgs `pilot-50000`, seeds
42--51, probability bounds `[0.02, 0.98]`, two selected seeds, IC horizon 4,
risk lambda 0.35, community weight 0.25, 20 common random streams, candidate
pool 120, robust greedy, and all v1 baselines remain fixed. The decision graph
is the complete timestamp-grouped outer-training graph; the encoder sees
history only.

New output paths must be named `v2-t0b`; no v1 or v2-T0 artifact may be
modified. Formal inference remains blocked until a matching isolated runner
passes a one-run smoke test and its achieved fractions are audited.
