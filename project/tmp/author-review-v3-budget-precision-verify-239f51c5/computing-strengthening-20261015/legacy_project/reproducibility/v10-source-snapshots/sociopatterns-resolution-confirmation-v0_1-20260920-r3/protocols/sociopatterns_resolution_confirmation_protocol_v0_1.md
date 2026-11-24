# SocioPatterns confirmation: selection-resolution profiles

**Date:** 2026-09-20; **version:** 0.1; frozen before confirmation outcomes.

## Purpose and scope

This confirmation layer tests the simulation-resolution-aware candidate
truncation direction on four openly licensed, independently collected temporal
contact-network instances: InVS 2013 workplace, InVS 2015 workplace, SFHH
2009 conference, and Kenya 2012 households. It evaluates a *simulated* IC
task on bidirectional topologies derived from observed undirected contacts.
It does not claim observed information diffusion, causal influence, or social
media propagation.

Each source is explicitly listed by SocioPatterns as CC0. The downloaded
archive hash, source page, raw semantics, and bidirectional transformation are
frozen in each `data_card.json`. The raw contact archives will not be included
in a code release; the paper will cite the source pages as required.

## Fixed selection and evaluation protocol

- Historical graph: the first 65% of complete time groups; duplicate events
  collapse to a directed endpoint topology after each undirected contact is
  emitted in both directions at its original timestamp.
- Primary task: standard IC mean spread with `p=0.01`, horizon 3.
- Candidate arms: full greedy, weighted-degree 2k, 4k and 8k.
- Nested selection world budgets: W={20,80,320}; paths={301,302}. Each smaller
  W is the prefix of the same path's larger W.
- All arms within `(dataset,path,k,W)` share 2,000 disjoint evaluation worlds.
- Record ordered seed sets, winner margins/tie counts, same-W agreement with
  full, independent spread, decision time, data/source hashes and semantic
  limitation. No GNN and no PageRank arm is included.

## Resource-justified matrix

Outcome-blind W=4 preflights completed for k={5,20}. Extrapolating only the
observed full-reference timing, SFHH k=20 at W=320 would take about 54 minutes
per path before other arms. It is excluded by the pre-fixed 4-hour serial
resource ceiling. The confirmation matrix is therefore:

| Dataset | k | Paths | W |
| --- | --- | --- | --- |
| InVS 2013, InVS 2015, SFHH 2009, Kenya 2012 | 5 | 301, 302 | 20, 80, 320 |
| InVS 2013, InVS 2015, Kenya 2012 | 20 | 301, 302 | 20, 80, 320 |

This is 42 conditions and 168 method executions. If the serial runner exceeds
the 4-hour ceiling, it must stop, preserve completed files, and label the
matrix incomplete; no subset may be called confirmation-complete.

## Decision criteria

The paper direction remains viable only if at least one of the following is
observed transparently across multiple source instances: (a) full greedy seed
sets change on the nested W path, (b) tie/margin resolution changes materially
with W, or (c) candidate-pool agreement changes with W. Regardless of outcome,
candidate pools may only be described as reproducing a **same-W finite-world
full reference**. A null result is reportable only as evidence against the
proposed failure mode, not suppressed or reconfigured.
