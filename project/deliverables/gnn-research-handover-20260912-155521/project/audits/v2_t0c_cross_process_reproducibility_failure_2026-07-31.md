# v2-T0c Cross-Process Reproducibility Failure Audit

Date: 2026-07-31

## Scope

This audit records why the incomplete `v2-T0c` objective-ablation output is
excluded from all manuscript evidence. It does not alter the frozen v1 or
v2-T0b artifacts, and it does not report an ablation conclusion.

## Observed Mismatch

The first new artifact was
`results/large-robust-greedy-higgs-50000-v2-t0c-objective-ablation/risk_off/split-0.60-seed-42.json`.
It and the read-only reference artifact
`results/large-robust-greedy-higgs-50000-v2-t0b/split-0.60-seed-42.json`
have all of the following in common:

- the same hash-verified Higgs input;
- the same model and v2-T0b source hashes;
- the same fraction and seed;
- the same strict timestamp boundaries (calibration cutoff `2012-07-03
  09:52:56+00:00`, outer-test start `2012-07-03T09:53:03+00:00`); and
- the same selected users, `88` and `677`.

Despite those agreements, the archived reference robust objective is
`2433.104`, while the v2-T0c re-evaluation of that same seed set reports
`2318.972`.

## Cause

The inherited IC simulator constructs `frontier` and `next_frontier` as Python
sets and iterates them directly. Python preserves a randomized hash seed per
process. An unchanged list of per-replication random seeds therefore need not
be consumed by the same edge trials in a different process. The old
`common_random_numbers` label is sufficient for within-process comparison but
does not support direct numeric equality with a separately executed process.

## Disposition

The v2-T0c process was stopped after the first artifact. Its protocol, runner,
logs, and one artifact are retained without overwrite as a negative
infrastructure record. The directory must not be pooled with v2-T0b, cited as
an ablation, or used for a performance or significance claim.

The replacement v2-T0d protocol is separately preregistered in
`protocols/influence_v2_t0d_common_world_objective_ablation_preregistration.md`.
It retains the input/model/time-window constants but evaluates the full and
three ablation selections from a single learned probability map with canonical
edge-time deterministic possible worlds. v2-T0d remains pending until its
complete 30-artifact batch and preregistered paired analysis pass.

## Remediation Check

The v2-T0d common-world simulator was executed in two independent Python
processes with `PYTHONHASHSEED=1` and `PYTHONHASHSEED=999` on the same small
directed graph, seed set, probabilities, and 20 world seeds. The two complete
spread sequences were identical. This validates process-hash independence of
the new evaluator; it is not a substitute for the pending full Higgs batch.
