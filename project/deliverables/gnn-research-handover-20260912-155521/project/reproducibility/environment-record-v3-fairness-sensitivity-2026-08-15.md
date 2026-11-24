# v3 Fairness and Sensitivity Environment Record

## Scope

This archival sidecar records the local runtime observed while the formal v3
fairness and sensitivity batch was active. It is outside the study directory:
it neither alters run JSON artifacts nor replaces the final v3 manifest. The
record contains no raw interaction data and creates no publication archive.

## Capture Context

- Captured: 2026-08-15 while formal process PID 41732 was active.
- Process creation time: 2026-08-15 16:13:09 local time.
- Interpreter command: `C:\\Users\\36024\\Miniconda3\\python.exe
  experiments/run_v3_fairness_sensitivity.py --dataset
  data/processed/higgs-twitter/pilot-50000 --output-dir
  results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity`.
- Result boundary: only the separately versioned v3 study; frozen v1,
  v2-T0b, v2-T0c, and v2-T0d outputs are not covered or changed.

## Platform and Dependencies

- Operating system: Microsoft Windows 11 Home Chinese Edition, version
  `10.0.26200`, build `26200`.
- Interpreter: conda-forge Python `3.13.0`, 64-bit AMD64.
- PyTorch: `2.11.0+cu128`; PyTorch Geometric: `2.8.0.post1`.
- NumPy: `2.3.3`; pandas: `2.3.2`; SciPy: `1.16.1`; scikit-learn: `1.7.2`.
- Matplotlib: `3.10.6`; NetworkX: `3.5`.
- CUDA runtime reported by PyTorch: `12.8`; CUDA available: `true`.
- Visible accelerator: one NVIDIA GeForce RTX 4070.

## Hash Snapshot

The code/protocol hashes below were captured while PID 41732 was active. They
match the corresponding v3 smoke-manifest snapshot and are intended to be
compared with the final formal v3 manifest, rather than inferred from a later
working-tree state.

| File | SHA-256 |
| --- | --- |
| `protocols/influence_v3_fairness_sensitivity_preregistration.md` | `4EE2C0F4C062EE374771B9EC859F66221BC20E02AE278A762B707B5B583A1985` |
| `experiments/run_v3_fairness_sensitivity.py` | `942D1C5F7393BE17170502192E8FAF3EE83461FA42D5EF38F9EAA9CF1574979E` |
| `backend/app/pipeline_v2_t0.py` | `6D321005EB81FA132F54D967349EDDF981ECD3921145AB24721AA3DC4C893D55` |
| `backend/app/pipeline_v2_t0b.py` | `54EC7169056FCEF066C4840E8D1E025BBBCE0730168430D09CA21635BE8A814F` |
| `backend/app/model_v2.py` | `33BA30F22B47760F4960064BC90B987636FE4F530C970FA174718DBDDB735316` |
| `requirements.txt` | `0CD554E6872D08E1D7742E2E15F59CCB411DC9FD65A4503848CC802440F12D45` |
| `pyproject.toml` | `091D90437B70A8D8EDFE8FC59F11076C16371E01C63F5C7AB0CDF9EB240D3CD5` |

## Verification Rule

Before accepting v3 for manuscript evidence, confirm that the completed
manifest contains the same protocol, input, and source hashes; validate all
30 run hashes; and retain this record as the runtime context. A mismatch is
an evidence-integrity failure, not a reason to overwrite any result artifact.
