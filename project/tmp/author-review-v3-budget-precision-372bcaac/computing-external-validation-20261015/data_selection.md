# External-network data selection and source record

## Selection was fixed before inspecting new-network seeds or utilities

The new evidence layer uses three real observed networks from the Stanford Large Network Dataset Collection (SNAP). The set was fixed using source provenance, structural diversity and a size target above the 75–402 nodes of the earlier contact graphs. It was not selected after a ranking or diffusion result.

| ID | Source and retrieval page | Observed relation and retained topology | Why it complements earlier evidence | What it cannot establish |
|---|---|---|---|---|
| `college_msg` | SNAP, [CollegeMsg](https://snap.stanford.edu/data/CollegeMsg.html), retrieved 2026-10-15 | Directed private messages in a UC Irvine online community; each input row has `(src,dst,timestamp)`. SNAP reports 1,899 users, 59,835 temporal messages and 20,296 static directed pairs over 193 days. | A temporal, directed online communication network with authentic event counts, substantially larger than every historical contact graph. It permits a time-cut historical-event ranking while holding the propagation topology to the pre-cut history. | Message events are not observed influence cascades. The simulated IC process does not estimate message adoption, and the source's timestamps do not identify causal transmissions. |
| `ca_grqc` | SNAP, [ca-GrQc](https://snap.stanford.edu/data/ca-GrQc.html), retrieved 2026-10-15 | Undirected coauthorship pairs among arXiv GR-QC authors, interpreted as two reciprocal directed eligibility/propagation arcs per observed pair. SNAP reports 5,242 nodes and 14,496 edges. | A larger, sparse scholarly-collaboration topology with reciprocity induced explicitly and recorded in preprocessing; it tests whether findings depend on communication-network directionality. | The published edge list has no per-event history in the downloaded file. It is topology only, not a temporal interaction sequence or a real contagion record; no historical-weighted ranking will be asserted. |
| `wiki_vote` | SNAP, [wiki-Vote](https://snap.stanford.edu/data/wiki-Vote.html), retrieved 2026-10-15 | Directed Wikipedia administrator voting relation; an arc means one user voted on another. SNAP reports 7,115 nodes and 103,689 arcs. | A larger directed governance network with much higher edge density than the collaboration topology, providing an explicit check of scale and directionality. | The edge list is static and represents votes rather than propagation. It has no usable event sequence or edge strength in this file; no historical-weighted ranking will be asserted. |

## Provenance and permitted handling

- The source pages name the original studies: Panzarasa, Opsahl and Carley (2009) for CollegeMsg; Leskovec, Kleinberg and Faloutsos (2007) for ca-GrQc; and Leskovec, Huttenlocher and Kleinberg, *Signed Networks in Social Media* (CHI 2010) plus *Predicting Positive and Negative Links in Online Social Networks* (WWW 2010) for wiki-Vote. SNAP asks users to cite its dataset collection (Leskovec and Krevl, 2014).
- The SNAP software licence page is BSD for software, but it does **not** establish a dataset-specific licence for these individual files. Dataset pages provide public download links and citation guidance. This package will keep the downloaded source files locally for the authorized analysis, preserve their hashes and source URLs, and exclude raw source files from any reproducibility ZIP unless their redistribution terms are independently confirmed.
- The three data pages and their original-format files are source material only. Preprocessing will preserve a raw SHA256 manifest and document every deterministic transformation.

## Planned preprocessing, fixed before outcomes

1. `college_msg`: sort timestamp ties deterministically by `(timestamp,src,dst,input-row-index)`; form a 65% prefix by unique timestamp, retain its observed directed pairs as the propagation topology, and use the number of prefix messages emitted by each source as the authentic historical-event score. The cutoff operates on timestamp groups, never inside one group.
2. `ca_grqc`: read each non-comment pair, remove self loops and duplicate pairs, then add both directions. Retain all listed nodes appearing in edges. Use unweighted out-degree and PageRank; do not create a weighted method.
3. `wiki_vote`: read each non-comment directed pair, remove self loops and duplicate pairs, retain all listed nodes appearing in edges. Use unweighted out-degree and PageRank; do not create a weighted method.

These transformations are not selected from results and will be frozen, together with raw hashes, before the main experiment.
