# v2-T0b Environment Record

## Scope

This record captures the local environment used by the active formal
v2-T0b runner on 2026-07-29. It is an archival aid, not a replacement for the
run-level manifest that the runner writes after all 30 preregistered artifacts
complete.

## Runtime

- Operating system: Windows 11, build `10.0.26200`.
- Interpreter: conda-forge Python `3.13.0`, 64-bit.
- PyTorch: `2.11.0+cu128`.
- PyTorch Geometric: `2.8.0.post1`.
- NumPy: `2.3.3`; pandas: `2.3.2`; SciPy: `1.16.1`;
  scikit-learn: `1.7.2`; Matplotlib: `3.10.6`; NetworkX: `3.5`.
- CUDA runtime reported by PyTorch: `12.8`.
- CUDA availability: `true`; one NVIDIA GeForce RTX 4070 device was visible.

## Active Formal Invocation

The active process uses the Miniconda Python interpreter to run:

```text
experiments/run_rolling_study_v2_t0b.py
  --dataset data/processed/higgs-twitter/pilot-50000
  --output-dir results/large-robust-greedy-higgs-50000-v2-t0b
```

The runner's formal configuration is additionally fixed by
`protocols/influence_v2_t0b_timestamp_preregistration.md`; this record does
not reproduce it independently.

## Input Specifications

`requirements.txt` gives declared lower-bound dependencies and `pyproject.toml`
records the project Python requirement. Their hashes, the v2-T0b protocol hash,
and the runner hash at capture time are:

| File | SHA-256 |
| --- | --- |
| `requirements.txt` | `0CD554E6872D08E1D7742E2E15F59CCB411DC9FD65A4503848CC802440F12D45` |
| `pyproject.toml` | `091D90437B70A8D8EDFE8FC59F11076C16371E01C63F5C7AB0CDF9EB240D3CD5` |
| `protocols/influence_v2_t0b_timestamp_preregistration.md` | `D9A98FD9BDD10C39FAC9D709927C2FACE9F0A1F0DEB11ADF7D93BDE2B517E364` |
| `experiments/run_rolling_study_v2_t0b.py` | `2362DDE95528346BB94FE636CCF4C679DFEBC8BB657A5355591975CEF3025D51` |

## Boundary

This environment record does not license raw-data redistribution and does not
make the incomplete formal study eligible for manuscript claims. A lawful
public archive must pair this record with the completed v2-T0b manifest,
analysis bundle, source snapshot, and verified source-data terms.
