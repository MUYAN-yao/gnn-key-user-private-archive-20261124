# Code-and-Metadata Archive Scope

## Status

This is a release-scope specification, not a public archive, DOI, repository,
or permission statement. It supports a later code-and-metadata release without
including raw or processed source data.

## Intended Inclusions

The eventual archive should include the following only after the completed
v2-T0b manifest and paired-analysis bundle, plus the accepted non-smoke v3
fairness/sensitivity analysis bundle, are available:

- `backend/`, `experiments/`, `protocols/`, and `scripts/` source files;
- `requirements.txt`, `pyproject.toml`, `Dockerfile`, and
  `docker-compose.yml`;
- top-level `README.md` and `data/README.md`, with data-acquisition
  instructions pointing to original publishers;
- `data_cards/`, `reproducibility/`, and the completed study protocols;
- reviewed analysis reports, figures, statistical appendices, and manifests
  that contain no raw or processed interaction records;
- a release-specific file inventory with SHA-256 values.

## Explicit Exclusions

Do not include any of the following unless a later, first-party terms review
establishes permission for the exact redistribution:

- `data/raw/` and all publisher-downloaded archives;
- `data/processed/`, including `nodes.csv`, `edges.csv`, `cascades.csv`, and
  platform packages;
- any raw-data copy nested in `results/`, `tmp/`, or a release staging area;
- personal workspace files, user profile paths, editor state, caches,
  `runtime-data/`, `web/node_modules/`, and local logs;
- author contact details or unconfirmed submission metadata.

## Verification Before Release

1. Re-check the source-data terms and record first-party evidence.
2. Confirm author-approved archive destination and data-availability wording.
3. Complete v2-T0b and v3, generate their accepted strict paired-analysis
   bundles, and include only the reviewed artifacts selected for release.
4. Use `experiments/build_public_release_inventory.py` to generate a
   hash inventory from an explicit author-approved allowlist; it rejects raw
   data, processed data, result directories, logs, and workspace-private paths.
5. Inspect the archive recursively to confirm the exclusions above.

Until all five checks pass, the manuscript must continue to state that a
public code archive has not yet been established.
