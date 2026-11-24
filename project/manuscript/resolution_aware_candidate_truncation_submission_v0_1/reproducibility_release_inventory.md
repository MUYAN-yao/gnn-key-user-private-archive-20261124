# Reproducibility release inventory

Create the public archive from this allowlist after author review. The archive
should be tagged and assigned a persistent DOI before the final manuscript is
submitted.

## Include

- `protocols/sociopatterns_resolution_confirmation_protocol_v0_1.md`
- `protocols/candidate_truncation_data_admission_v0_1.md`
- `experiments/prepare_sociopatterns_confirmation.py`
- `experiments/v10_sociopatterns_resolution_confirmation.py`
- `experiments/run_v10_sociopatterns_resolution_confirmation.py`
- `experiments/validate_v10_sociopatterns_resolution_confirmation.py`
- `experiments/analyze_v10_sociopatterns_resolution_confirmation.py`
- `analysis/build_sociopatterns_resolution_confirmation_report.py`
- `reproducibility/v10-source-snapshots/sociopatterns-resolution-confirmation-v0_1-20260920-r3/`
- `audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920/`
- `analysis/sociopatterns-resolution-confirmation-v0_2/`
- `analysis/build_visio_mechanism.ps1` and `analysis/build_visio_experimental_design.ps1`;
- `analysis/build_computing_main_figures.py` and `analysis/extend_resolution_diagnostics.py`;
- `analysis/build_reference_resolution_figures.py` and supplementary figure source data;
- `analysis/resolution-diagnostics-posthoc-20260920/`;
- manuscript, supplementary text, original figure masters and exports, and verified bibliography from this manuscript directory (subject to the exclusions below).

## Exclude by default

- `data/raw/sociopatterns/` provider archives;
- downloaded publisher HTML and reference figures in `literature/`, manuscript backups, and `*.previous.vsdx`;
- `*.before-simplification.*` superseded figure backups (their old denominator is incorrect);
- prior non-admitted output roots marked by `NON_ADMISSION.md`;
- unrelated historical studies, cached bytecode, editor settings, temporary
  files, credentials and local environment files.

## Reproduction sequence

1. Obtain each raw archive directly from the cited SocioPatterns provider page.
2. Verify the provider archive SHA-256 values recorded in the data admission
   ledger and run the preparation script.
3. Verify the immutable source snapshot before running the confirmation matrix.
4. Run the frozen 42-condition matrix with the resource ceiling.
5. Run the validator, the read-only analyzer and the report builder.

The release must preserve the wording that results concern simulated IC on
contact-derived bidirectional topologies, not observed information cascades.
