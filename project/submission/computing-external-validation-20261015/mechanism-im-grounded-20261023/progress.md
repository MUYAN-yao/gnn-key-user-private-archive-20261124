# Progress

Created from the finalized author-review baseline rather than the rejected generic-mechanism draft. The final candidate figure is domain grounded: directed arcs, ranking cutoff, candidate coverage, selected seed eligibility and independently evaluated diffusion utility.

The source is `figures/wiki_vote_candidate_coverage_mechanism_v2.vsdx`, made from 89 native Visio shapes and no embedded media. `src/prepare_domain_figure.py` checked the frozen source rows, produced a vector PDF with no raster images, and recorded the result in `audit/direction_figure_validation.json`. The manuscript was compiled twice; the new cross-references resolve. Page 3 was rendered and visually inspected.

`src/verify_archive.py` created `submission/computing-mechanism-im-grounded-20261023-v1.zip`. Extraction reproduced all 56 archived file hashes. The current archive digest is recorded by the verifier in its terminal output and can be recomputed without changing the source package.
