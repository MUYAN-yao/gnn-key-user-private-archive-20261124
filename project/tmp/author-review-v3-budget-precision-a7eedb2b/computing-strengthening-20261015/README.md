# Computing author-review and reproducibility package

This local package accompanies **Selection Resolution, Random-World Coupling, and Utility in Candidate-Restricted Influence Maximization**. It is prepared for author review. No journal submission, public upload, DOI registration, or software-license declaration has been made.

## Evidence and contents

- `snapshot/`: immutable extension engine, runner, configuration, protocol and SHA256 manifest. Run this copy for experiments.
- `results/`: 520 condition JSON/NPZ pairs and a checkpoint manifest. Each condition has nine arms and 10,000 evaluation worlds. Per-round candidate scores and per-world spreads are retained.
- `analysis/`: independently regenerated tables, statistical checks and five figures in PDF/SVG/PNG. `round_diagnostics.csv` separates marginal gains from winner–runner-up score margins.
- `src/`: validators, analysis, plotting, manuscript assembly, data preparation and packaging utilities. Analysis/reporting utilities are not part of the pre-experiment frozen engine; their final hashes are in the package manifest.
- `data_cards/`: original provider URLs, licenses and raw archive hashes. The stated download date records the original acquisition; rerunning preprocessing does not imply a new download on that date.
- `legacy_project/`: the archived source snapshot, original 42-condition outputs, validation ledger and original manuscript/template assets needed to audit the historical evidence.
- `manuscript/`: editable, flat LaTeX sources and compiled main manuscript / Online Resource 1. The original Springer class files are included without modification.
- `audit/`: implementation audit, outcome-blind timing preflight, count erratum and primary-source literature/journal checks.
- `research_report_zh.md`, `summary_for_editor.txt`, `cover_letter_draft.txt`, `author_checklist_zh.md`: interpretation and submission preparation.

The original archive and this extension are distinct evidence layers. The extension was frozen after reviewing the old findings and resource timings. It is a prospective computational extension on known datasets, not a publicly preregistered or unseen-network replication. The new study has four real graph instances and two synthetic instances; 520 conditions and 46.8 million stored evaluation counts are not independent-network sample sizes.

## Environment

Tested on Windows, Python 3.13.0, 20 physical CPU cores, about 32 GiB RAM. Experiments use one serial worker. Versions are pinned in `requirements.txt`; their compatibility outside the tested environment has not been independently certified. A C compiler is not needed for ordinary Numba JIT use. PDF assembly additionally uses TeX Live 2026 with `pdflatex`; PDFs are already supplied. Actual runtime and peak process memory are recorded in `analysis/summary.json`.

Install into an isolated environment of your choice, then run from the extracted package directory:

```powershell
python -m pip install -r requirements.txt
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
python src/minimal_smoke.py
```

The smoke test needs no empirical data. It checks a step-coupling counterexample, fixed-edge reachability, seed counting and the full-pool identity. The longer audit uses independent reference implementations, not just this smoke test.

## Verify and regenerate results analysis without raw data

```powershell
python src/verify_package.py .
python src/analyze.py .
python src/plot_figures.py .
python src/build_manuscript.py legacy_project .
```

The analysis refuses an incomplete matrix and checks source/result hashes, greedy score winners, tie handling, full-pool identity, same-set evaluations and paired statistics. It does not rerun 520 experiments. Generated reports can be recreated using `python src/report_package.py .`.

The package manifest describes the delivered files. Regenerating PDFs, timings, metadata or platform-dependent figure files can change their byte hashes; retain the delivered package as an immutable reference and work on a copy. Numeric results should remain identical for the frozen results.

## Obtain and prepare empirical data

Obtain the exact four original archives from the provider pages in `data_cards/`. This package intentionally does not redistribute provider archives or normalized contact records. Preserve these filenames in a raw-data directory:

- `workplace_InVS_tij.dat.zip`
- `workplace_InVS15_tij.dat.gz`
- `scc2034_household_contact_dataset.zip`
- `SFHH_tij.dat.gz`

Provider links and licenses are recorded evidence, not a substitute for checking the provider's current terms. No downloads or uploads are performed by the preparation command.

```powershell
python src/prepare_data.py --raw-dir 'C:/path/to/provider-archives' --project-root 'C:/path/to/new-reproduction'
```

The script checks each raw SHA256 before preprocessing and refuses to overwrite a dataset. It writes the original project-relative layout under `data/processed/sociopatterns-confirmation-v0_1/`. `cascades.csv` is an empty schema, never observed influence data. Historical graph formation remains inside the frozen engine. Byte-identical CSV hashes can depend on OS newline conventions; the canonical graph hash and graph statistics provide a second semantic check. This release was tested on Windows.

## Rerun the extension

```powershell
python snapshot/run_extension.py --project 'C:/path/to/new-reproduction' --output 'C:/path/to/new-extension-results'
```

Use a new output directory to preserve delivered results. The runner uses the frozen matrix, source verification, deterministic execution-order randomization, disjoint evaluation family, and nested selection prefixes. Each completed condition is hashed and checkpointed. Rerunning the identical command resumes valid completed conditions. If interrupted while writing an unmanifested condition pair, preserve that orphan pair outside the run directory before resuming; never delete validated entries to obtain preferred outcomes. Timings will vary with machine load. An interruption is not an outcome-based exclusion.

To analyze a rerun, create a new analysis directory with the supplied `snapshot/` and put the newly completed result directory at `results/`, then pass that parent directory to `src/analyze.py`. Repeated timing observations are execution repeats, not additional utility replicates. Initial JIT warmup is excluded from comparison times. Shared world preparation remains explicitly attributable in full-pipeline cost.

## Reproduce the historical audit

Prepare data into `legacy_project` (or into a separate copy with the same historical assets), then:

```powershell
python src/audit_engine.py legacy_project audit-rerun
```

This performs semantic comparisons with the archived Python implementation, verifies all 42 old condition hashes, replays 32 old arms/64,000 outcomes, and repeats the resource preflight. Audit timings need not equal the supplied record. The preserved first audit JSON has a mislabeled count (324 instead of 108 uniform comparisons); `audit/audit-count-erratum.json` and the corrected executable audit make the correction explicit. Do not replace the preserved pre-freeze audit record.

## Compile the supplied manuscript

```powershell
Set-Location manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
```

The main paper uses uncompressed `svjour3` `smallextended`. Figures are vector PDFs. See `qa/verification.json` for the delivered page count and checks. Read the author checklist before external use. A local archive is not a public data/code-access commitment; authors must decide license, repository, archival identifier and access arrangement.

For optional PDF QA, install `requirements-qa.txt`, then run `python src/render_qa.py .` and inspect every generated page. `qa/visual_review.json` records the delivered version's actual inspection; it must not be reused as evidence that a changed PDF has been visually reviewed. `python src/final_checks.py .` checks page count, citations, unchanged template files, 119-mm figure widths, embedded fonts and data-rebuild evidence. The delivered main PDF is 19 pages and Online Resource 1 is 4 pages; the abstract has 210 words and five keywords.

The complete serial experiment took 32.7 minutes on the tested machine, with a recorded peak process working set of about 780 MiB. This excludes the earlier audit, package construction and manuscript preparation. Keep the distinction between experiment time and total research work. The original outcome-blind preflight estimated 20–45 minutes; no frozen condition was dropped.
