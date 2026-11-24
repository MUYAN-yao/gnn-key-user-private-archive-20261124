# Bilingual Abstract Consistency Audit

Date: 2026-07-29

## Scope

Read-only comparison of the Chinese abstract in `manuscript/draft_zh_v0_1.md`
and the controlled English abstract in `manuscript/abstract_en_v0_1.md`,
against `manuscript/claim_ledger.md` and `manuscript/terminology_ledger.md`.
It does not assess the unfinished v2-T0b formal study and does not introduce
new evidence.

## Claim-Boundary Check

| Required boundary | Chinese abstract | English abstract | Result |
| --- | --- | --- | --- |
| Problem scope | Temporal Top-K selection with uncertainty and community coverage | Temporal Top-K selection with uncertainty and community coverage | Match |
| Objective | Expected spread minus risk penalty plus coverage reward | Same robust objective | Match |
| Candidate restriction | GNN prior limits greedy-search candidates | GNN prior restricts greedy-search candidates | Match |
| Evidence separation | Frozen optimization comparison is separate from Higgs temporal prediction audit | Same separation stated | Match |
| Frozen comparison scope | Ten paired repetitions; Digg and Higgs; three splits | Same repetition, dataset-protocol, and split scope | Match |
| RIS boundary | Higgs 0.60 tie; higher objective only at 0.65 and 0.70 | Same tie and split-specific comparison | Match |
| T0 boundary | Meets prespecified gates as a temporal candidate | Fixed candidate T0 meets the same gates | Match |
| Limits | Digg parent links are not observed resharing causality; no universal superiority claim | Same exposure-proxy and non-universal boundaries | Match |
| v2-T0b boundary | No formal v2-T0b performance claim | Explicitly excluded by the translation boundary | Match |

## Terminology Check

The English abstract uses the canonical forms in the terminology ledger for
key user identification, influence maximization, cross-community constraints,
robust objective, graph-neural-network prior, temporally forward external
test, future-edge prediction, RIS baseline, and fixed candidate T0.

## Decision

The English abstract is a controlled translation of the current Chinese
abstract. It may be used as the source for a later journal-template English
abstract, subject to a final recheck after completed v2-T0b statistics are
validly integrated into both language versions.
