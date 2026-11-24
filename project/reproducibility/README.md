# Reproducibility Guide

## Scope and Preservation Rule

This directory documents the evidence package for the temporal
uncertainty-aware cross-community key-user study. The following frozen
directories are evidence artifacts and must not be overwritten, regenerated,
or summarized in place:

- `results/large-robust-greedy-higgs-50000-v1/`
- `results/large-robust-greedy-digg-20000-v1/`

The strict v2-T0b study is separately versioned at
`results/large-robust-greedy-higgs-50000-v2-t0b/`. Its formal batch remains
incomplete while this guide is written; it is excluded from manuscript
performance claims until all planned artifacts are present and verified.

## Frozen v1 Integrity Record

`frozen-study-manifest-v1.json` is a read-only provenance manifest. It records:

- the hashes of the three processed inputs for each study;
- 30 run-artifact hashes per study (60 in total);
- hashes of the frozen aggregate statistics and eight core source files;
- deterministic environment versions and the three non-seed configurations;
- the ten random seeds (`42` through `51`) for every train fraction.

The frozen data inputs are:

| Study | Processed input directory | Runs |
| --- | --- | ---: |
| Higgs 50k | `data/processed/higgs-twitter/pilot-50000/` | 30 |
| Digg 20k | `data/processed/digg/pilot-20000/` | 30 |

For an integrity check, compute SHA-256 values with `Get-FileHash` and compare
them to the matching fields in the manifest. This is a read-only operation.

```powershell
Get-FileHash data\processed\higgs-twitter\pilot-50000\nodes.csv -Algorithm SHA256
Get-FileHash results\large-robust-greedy-higgs-50000-v1\split-0.60-seed-42.json -Algorithm SHA256
```

## Evidence Map

| Question | Artifact | Claim boundary |
| --- | --- | --- |
| Frozen paired optimization comparisons | `analysis/frozen-main-comparison-v1/` | Two protocols only; Higgs/RIS at 0.60 is an exact tie. |
| Frozen v1 temporal-prediction audit | `analysis/higgs-edge-prediction-audit-v2/` | Exposes seed instability; does not validate v1 as a future-edge probability model. |
| Fixed T0 prediction gate | `analysis/edge-prediction-v2-t0-gate-v2/` | One-dataset validated candidate, not a selected global optimum. |
| Third-dataset screen | `data_cards/third_dataset_admission.md` | No third primary dataset was admitted. |
| Strict timestamp-window audit | `audits/timestamp-grouped-v2-t0b-window-audit-v1.json` | Confirms the planned v2-T0b windows have strict timestamp separation. |
| Claim and citation audit | `manuscript/claim_ledger.md`, `manuscript/citation_audit.md` | Manuscript wording must not exceed listed evidence. |

## Formal v2-T0b Completion Procedure

Do not start another process while the existing formal batch is active. After
the batch stops, first verify all of the following:

1. Exactly 30 `split-*.json` artifacts are present in the v2-T0b directory.
2. `logs/higgs-v2-t0b-formal.stderr.log` contains no runtime failure.
3. Every artifact records the strict timestamp-window fields, and the
   batch-level `manifest.json` records the expected frozen Higgs input hashes,
   source hashes, protocol hash, and each run-file hash.

Only then run the preregistered aggregation command:

```powershell
python experiments\summarize_study.py `
  --study-dir results\large-robust-greedy-higgs-50000-v2-t0b `
  --reference-method gnn_guided_robust_greedy_v2_t0b
```

The runner creates `method_metrics.csv` and `manifest.json` only after all
planned runs complete. The aggregation then writes `aggregate_statistics.json`
inside the v2-T0b study directory. It must not be redirected to a frozen v1
directory. A separate paired-statistics analysis bundle and a claim-ledger
update are required before any v2-T0b manuscript conclusion is added.

## Environment

The frozen manifest records Python 3.13, NumPy 2.3.3, pandas 2.3.2,
scikit-learn 1.7.2, NetworkX 3.5, PyTorch 2.11.0+cu128, and CUDA 12.8. The
v2-T0b protocol additionally fixes a one-layer GATv2 encoder (width 32), 10
epochs, learning rate 0.01, isotonic calibration, `k=2`, IC horizon 4, risk
coefficient 0.35, community weight 0.25, 20 common random streams, and a
120-node candidate pool. The authoritative specification is
`protocols/influence_v2_t0b_timestamp_preregistration.md`.

`environment-record-v2-t0b-2026-07-29.md` additionally records the active
formal-run interpreter, complete core package versions, CUDA visibility,
launch invocation, and hashes of the dependency declarations, protocol, and
runner. It is a local capture for the future archive, not evidence that the
incomplete v2-T0b batch has passed its completion gate.
