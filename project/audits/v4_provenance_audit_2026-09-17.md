# v4 Formal Screening Batch: Source-Provenance Audit

Date: 2026-09-17

## Scope and decision

This is a read-only provenance audit of
`results/large-robust-greedy-higgs-50000-v4-screening-formal-30run/`. It does
not alter results, manifest entries, protocol, runner, or statistics.

**Decision: do not formally admit the v4 30-run batch for inferential or
manuscript-result use.** The run artifacts are internally hash-consistent, but
the exact runner source snapshot declared by the preregistered manifest cannot
be recovered or matched locally. It may be retained as a descriptive,
non-inferential engineering record only. It must not be used to claim a
confirmed GNN-versus-weighted-out-degree result, including a null/equivalence
claim.

## Checks performed

| Check | Result |
| --- | --- |
| Manifest runner digest | `0e8f312d90bb173add2bb0e5d5051c257c043a379b1af43d20d0df1b61153f93` |
| Current runner digest | `f39262ea80dc56371f606ca3f757df535b7665d3dd95b995518a9be0a5b268bf` |
| Other nine manifest source digests | All match current local files |
| All 30 per-run artifact digests | Match the final manifest |
| Metrics table | 120 rows, consistent with 30 blocks × 4 arms |
| Current runner's own `source_hashes()` | Returns the current runner digest, confirming the validator uses the same path rule as the runner |
| Current runner bytecode cache | Created four seconds after the first artifact; cache header timestamp and source size match the current runner |
| Current runner vs cached bytecode semantic fingerprint | Match, after excluding debug-position metadata |
| Alternate runner source | Not found in the workspace, checked Cursor/VS Code local-history locations, or selected user workspace/cache locations |

## Chronology and interpretation

- Current runner last-write time: 2026-09-16 05:49:24 UTC.
- First formal artifact creation: 2026-09-16 05:50:20 UTC.
- Current runner bytecode-cache creation: 2026-09-16 05:50:24 UTC.
- Final artifact and manifest creation: approximately 07:30 UTC.

The current source and bytecode have the same executable semantics, but source
timestamps and bytecode cannot reconstruct the exact source bytes whose SHA-256
was recorded. The runner explicitly hashes `Path(__file__)`; therefore a run of
the current canonical source would record the current digest. Possible causes
include execution from a now-missing alternate source copy or an unrecorded
source transition. This audit does not infer intent or data manipulation.

The preserved artifacts also record disjoint selection/evaluation world sets,
the expected source-digest map, and the protocol's stated future-aware negative
sampling limitation. These support artifact-level inspection only and do not
replace a reproducible execution-source chain.

## Descriptive observation kept outside formal inference

In the retained CSV, GNN-prior and weighted-out-degree have equal ordered
Top-K and equal robust-objective values in all 30 paired blocks. This is not an
equivalence result, a null-hypothesis conclusion, or evidence for the
manuscript until a versioned, source-verifiable study passes its validator.

## Required condition for later admission

One of the following must occur before any formal use:

1. Recover an immutable execution source snapshot whose runner digest matches
   the existing manifest and document how it produced this exact output; or
2. Conduct a newly versioned, preregistered study with a freshly captured
   immutable source snapshot and complete validator pass.

The existing manifest must never be edited to substitute the current digest.
