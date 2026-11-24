# Influence v4 Screening Diagnostic Protocol

Date: 2026-09-15

## Status and purpose

This is a mechanism diagnostic, not a confirmatory efficacy study. It compares
candidate membership rules while holding the learned probability graph, robust
greedy optimizer, objective, and random worlds fixed. It never writes to or
changes v1, v2, or v3 artifacts.

The first diagnostic run is fixed to Higgs 50k, outer fraction 0.70, seed 48.
Its results may validate instrumentation and motivate a separately locked formal
study, but are not eligible for significance claims or manuscript efficacy claims.

## Fixed inputs and decision conditions

- Hash-verified Higgs `pilot-50000` inputs.
- Timestamp-grouped windows inherited from v2-T0b.
- Frozen T0 configuration: one GATv2 layer, width 32, 10 epochs, learning rate
  0.01, concatenation MLP decoder, isotonic calibration, bounds [0.02, 0.98].
- Candidate pool size 120; seed budget 2; IC horizon 4.
- Reporting objective: mean spread - 0.35 population SD + 0.25 seed-community count.
- 20 selection worlds and 20 disjoint evaluation worlds, using the existing v3
  canonical edge-time simulator and namespaces 101 and 202.
- Random candidate membership uses namespace 303 and is independent of diffusion worlds.

## Candidate arms

1. Learned node prior (GNN): descending prior, then node ID.
2. Time-decayed weighted out-degree: descending score, then node ID.
3. Standard weighted PageRank: descending score, then node ID.
4. Uniform random sample without replacement from the fixed node universe.

Candidate membership follows each ranking/sample. After membership is fixed,
every arm passes candidates to robust greedy in ascending string node-ID order.
Exact objective ties retain the first node in that common order. This differs
from v3's prior-order tie behavior and is therefore a new diagnostic version.

## Required records

Store source/input hashes; environment; window boundaries; full probability and
prior tables; communities; candidate ranks/lists; world values and hashes; every
candidate score in every greedy round; winner, runner-up, margin and tie count;
per-world spreads for selected and evaluated sets; and phase timings. GPU work is
synchronized around timed training/inference where available.

The inherited probability calibration excludes negatives using relationships
observed anywhere in the fixed dataset. This diagnostic therefore does not claim
a strictly online, future-unaware probability pipeline.

## Decision boundary

One run reports descriptive mechanisms only. Do not select a screening rule,
change hyperparameters, or formulate superiority based on this diagnostic. A
formal comparison requires a separately frozen protocol and all planned paired
runs, reported regardless of outcome.
