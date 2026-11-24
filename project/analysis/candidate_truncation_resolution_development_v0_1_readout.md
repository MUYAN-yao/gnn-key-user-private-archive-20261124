# Development readout: finite selection-world resolution

**Status:** development-only diagnostic; not confirmation evidence and not a
manuscript result. Protocol:
`protocols/candidate_truncation_resolution_development_protocol_v0_1.md`.
Raw immutable condition files:
`audits/candidate-truncation-resolution-development-v0_1/formal-run-20260920/`.

## Question

Does a candidate-truncation conclusion remain unchanged when the Monte Carlo
world budget used to make greedy choices grows from 20 to 80, holding the
first 20 worlds nested inside the 80-world set?

## Design and completed coverage

The complete frozen matrix has 16 conditions: local Digg pilot-5000 and Higgs
pilot-1500; two world seeds (104, 105); `k` in {5, 20}; and W in {20, 80}.
Every condition uses standard mean-spread IC selection (`p=0.05`, `h=4`) and
the same 2,000 independent evaluation worlds for all arms within its
dataset/seed. It compares full greedy with weighted-out-degree pools 2k, 4k,
and 8k. No learned method, GNN, PageRank, p-value, or network-population
inference appears in this diagnostic.

## Descriptive findings

1. The ordered full-greedy seed sequence changed between W=20 and W=80 in all
   8 matched `(dataset, seed, k)` blocks. Therefore, a statement such as
   “the truncated pool equals full greedy” is meaningful only at a stated
   selection-world budget.
2. Full-search winner ties were common at W=20 (45 zero-margin rounds out of
   100) and still present at W=80 (19/100). At `k=20`, every local block still
   had at least two zero-margin rounds at W=80. Increasing W improved
   resolution but did not establish a stable limiting sequence.
3. At W=80, degree-4k and degree-8k matched the finite-world full sequence in
   8/8 blocks, whereas degree-2k matched in 5/8. The 4k/8k matches had a zero
   independent-evaluation mean difference in these same local blocks because
   they selected identical seed sequences. This is a conditional reproduction
   result, not a guarantee on new graphs.
4. At W=20, 4k matched in 7/8 and 8k in 8/8; 2k matched in 4/8. Some
   independent-evaluation deltas for divergent pools were positive, which
   confirms why these deltas must not be used to claim a truncated pool beats
   full greedy selected on a different finite Monte Carlo objective.

## Consequence

The defensible paper is not “GNN candidate pruning improves influence
maximization.” It is a protocol-and-evidence paper on how finite simulation
resolution changes the apparent quality--cost frontier of candidate pools. A
confirmation study must use an admitted external-data set, pre-register its
resolution path (at least W={20,80,320}), and report seed-set stability,
winner margins/ties, out-of-sample spread, and end-to-end cost together.
