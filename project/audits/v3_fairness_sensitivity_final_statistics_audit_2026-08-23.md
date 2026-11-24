# v3 Fairness and Sensitivity Final Statistics Audit

## Scope and Acceptance

This read-only audit covers the completed non-smoke Higgs v3 study and the
strict bundle in `analysis/v3-fairness-sensitivity-strict-paired-v1/`. The
validator accepted exactly 30 run artifacts, the final manifest, strict
timestamp ordering, disjoint selection/evaluation world digests, the full
decision-graph comparator, four candidate-pool arms, and nine objective-weight
arms. No frozen v1, v2-T0b, v2-T0c, or v2-T0d output was modified or pooled.

## Unit and Families

Each fraction has ten paired stochastic protocol repetitions. They are not
independent social-network samples. The reporting objective is fixed at risk
lambda 0.35 and community weight 0.25 and is evaluated only on held-out
evaluation worlds. Exact two-sided sign-flip tests use the preregistered
families and Holm correction is applied separately to the 3 primary, 9 pool,
and 24 weight contrasts.

## Results

- Primary fairness: screened robust greedy minus full-candidate robust greedy
  is exactly 0.000 at fractions 0.60, 0.65, and 0.70; each has 10 ties,
  exact p = 1.000, Holm p = 1.000, and paired Cohen dz = 0.00.
- Candidate-pool sensitivity: all nine 120-minus-comparison contrasts for
  pools 60, 240, and 480 are exactly 0.000 with 10 ties and Holm p = 1.000.
- Objective-weight sensitivity: 23 of 24 contrasts are exactly 0.000 with
  10 ties and Holm p = 1.000. The three nonzero rows occur at fraction 0.70,
  risk lambda 0.70 (community weights 0.00, 0.25, 0.50): mean 10.751,
  SD 33.998, 95% t-CI [-13.570, 35.072], W/T/L = 1/9/0, exact p = 1.000,
  Holm p = 1.000, Cohen dz = 0.32.
- Descriptive selection summaries show Jaccard overlap of 1.000 between the
  screened and full-candidate sets for all primary fractions, and 1.000 for
  all candidate-pool arms. The risk-0.70 arms at fraction 0.70 have mean
  overlap 0.933 with the base screened set; this is a selection change, not
  evidence of a utility improvement.

## Claim Disposition

Keep: v3 supplies a protocol-conditional robust null result for GNN screening,
candidate-pool expansion, and objective-weight sensitivity.

Reject: any claim that GNN screening improves the common robust objective,
that the risk or community term has an independently demonstrated effect, or
that the null result proves universal equivalence or irrelevance.

GNN Top-K remains a protected lower-bound audit and is excluded from all
efficacy Holm families.
