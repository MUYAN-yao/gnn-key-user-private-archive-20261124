# Core-Journal Manuscript Readiness Audit

## Scope

This audit evaluates `manuscript/draft_zh_v0_1.md` against the current
evidence ledger and the working target, *Software Journal* (软件学报).  It is
an editorial readiness audit, not a result analysis.  It neither alters the
frozen v1 evidence nor treats the incomplete v2-T0b batch as evidence.

## Current evidence-backed narrative

**One-sentence contribution.** Under a fixed two-dataset temporal protocol,
the study evaluates a GNN-prioritized, cross-community seed-selection
procedure with an explicitly risk-penalized objective, while independently
auditing whether its probability component generalizes to future time windows.

| Paper element | Current evidence | Status |
| --- | --- | --- |
| Conditional optimization result | `analysis/frozen-main-comparison-v1/analysis-report.md`, `manuscript/statistical_appendix.md`, and Claim C1 | supported; complete 24-contrast statistics explicitly retain the Higgs/RIS 0.60 tie |
| Future-edge probability result | `analysis/edge-prediction-v2-t0-gate-v2/analysis-report.md` and Claim C2 | supported only for fixed T0 on Higgs |
| Dataset semantics | data cards and Claim C3 | supported; Digg remains an exposure proxy |
| Reproducibility statement | frozen manifest, 60 run-hash and 8 source-hash recheck | supported for frozen v1 only |
| Related work | 22 metadata- and source-BibTeX-audited entries; six feature-level comparison points have completed full-text inspection | suitable for initial framing; broader full-text expansion remains required |
| Limitations | Section 7 | supported and correctly excludes incomplete v2-T0b results |

## Strengths now present

1. The abstract, introduction, results, discussion, and conclusion all
   preserve the same conditional scope: two protocol-specific datasets, not
   universal superiority or causal diffusion-probability inference.
2. The experimental section identifies the paired unit, common random streams,
   exact sign-flip test, Holm correction, seed range, time fractions, and the
   main fixed constants.
3. The manuscript exposes negative or non-superior evidence rather than
   suppressing it: the exact Higgs/RIS 0.60 tie and the unstable v1
   future-edge audit are both reported.
4. The draft has a dedicated limitation section and a data/code availability
   statement that does not claim a public archive before one exists.

## Gates still open before submission

| Gate | Required evidence / action | Current state |
| --- | --- | --- |
| Strict v2-T0b inference | Complete 30-run batch, final manifest, standard aggregation, then a separately reviewed paired-statistics bundle | running; no partial outcome may enter prose |
| Literature completeness | Add and audit further domestic and international work; obtain full texts before feature-level contrasts beyond metadata/abstract | incomplete |
| Reimplementation detail | Package versions, fixed protocol, determinism check, and known unrecorded hardware fields are now compiled in `manuscript/reproducibility_appendix.md`; recover hardware/runtime metadata only if authoritative logs exist | partially complete |
| Publication rendering | Retrieve and verify the current official *Software Journal* Word template; transfer content only after evidence and literature gates pass | pending |
| Release archive | Create a public source/environment snapshot only after raw-data redistribution terms are checked | pending |

## Explicit non-claims

- No third-dataset conclusion.
- No causal interpretation of Digg parent links.
- No universal statement that the method dominates RIS.
- No statement that T0 is globally optimal.
- No v2-T0b performance result before the formal batch and strict statistics
  are both complete.
