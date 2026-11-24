# Journal and citation audit — 2026-10-15

Official guide: https://link.springer.com/journal/607/submission-guidelines
Rechecked during this review. One-column smallextended, maximum25 pages without
compression; abstract150–250 words;4–6 keywords; novelty/evaluation summary and
short journal-fit letter; editable sources; institutional email; flat LaTeX upload
layout. Contribution/conflict details also go through the submission interface.
AI assistance beyond language editing is disclosed in Methods. Author approval,
funding and conflict assertions remain pending. Formal compliance is not acceptance.

Primary data pages rechecked:
- https://snap.stanford.edu/data/CollegeMsg.html — sender→receiver temporal messages;
  points to Panzarasa/Opsahl/Carley2009, DOI10.1002/asi.21015.
- https://snap.stanford.edu/data/ca-GrQc.html — undirected coauthorship; source
  Leskovec/Kleinberg/Faloutsos2007, DOI10.1145/1217299.1217301.
- https://snap.stanford.edu/data/wiki-Vote.html — voter→votee; source studies
  DOI10.1145/1753326.1753532 and10.1145/1772690.1772756.
- https://snap.stanford.edu/data/ — repository acknowledgement; no inference that
  the SNAP software BSD licence authorizes redistribution of these raw datasets.

Metadata for every DOI-bearing citation is saved in reference_metadata.json from
the publisher-deposited Crossref record. Initial TLS EOF failures were retried;
they are not treated as missing publications. Authors/titles/venues/pages/years
are checked against those records and official pages. Crossref title fields omit
some subtitles (StaticGreedy, Graph evolution); the prior primary-source audit
and official SNAP citations support the full titles used. Online-first year2023
for Fan etal. corresponds to volume106(2024); this is not a year mismatch.

NetworkX implementation settings are verified against the installed3.5 function
signature/source and official PageRank documentation. The stable web documentation
currently redirects to3.7; the manuscript identifies the installed3.5 implementation
and does not silently upgrade it. The initially attempted /documentation/3.5/
address returned404. The correct version-specific documentation was then verified:
https://networkx.org/documentation/networkx-3.5/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html .
It documents convergence at L1 change below n*tol, not an absolute1e-6 vector error.

Relevant primary literature checks retain the previous audit, including Kempe
et al., CELF, StaticGreedy, IMM, and benchmarking debates. Current official article
pages checked for the Computing neighbour-scale approach
https://link.springer.com/article/10.1007/s00607-019-00778-5 and MONSTOR+
https://link.springer.com/article/10.1007/s10618-025-01137-z . Their roles are
distinguished from this study; no unrun algorithm comparison or exhaustive novelty
search is claimed. Original voting paper available from the authors:
https://www.cs.cornell.edu/~dph/papers/links-www10.pdf .
