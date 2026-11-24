# Related-work wording check — 2026-10-27

No references were added. Existing bibliography metadata is preserved. This is a targeted claim check, not a systematic novelty search or a new full-text audit of every cited work.

| Source | Material inspected | Supported use and limit |
|---|---|---|
| Cheng et al., StaticGreedy (2013) | Author-hosted paper, abstract and introduction: https://www.junminghuang.com/publications/2013-cikm-cheng.pdf | Fixed realizations/static snapshots are part of its solver design. No claim that fixed-world evaluation originated here; no transfer of its guarantees to step-indexed worlds. |
| Rui et al., Computing (2020) | Publisher abstract and metadata: https://link.springer.com/article/10.1007/s00607-019-00778-5 | FNS uses multiple neighbour levels and FNS-dist for influence estimation. Changed the former “candidate approach / candidate restriction central” wording to this narrower supported description. Subscription full text was not accessed; no assertion about an unreported experiment. |
| Arora et al. (2017) | Author publication record https://sainyamgalhotra.com/publication/dblp-confsigmod-arora-gr-17/ and authors' NEDB research presentation https://mitdbg.github.io/nedbday/2017/talks/galhotr.pdf (slides on benchmarking ambiguity, quality, efficiency and model scope) | Retained the broad benchmarking characterization only. ACM DOI endpoint returned 403; no new detailed claim about SIGMOD implementation or omitted tests was introduced. Presentation is supporting author material, not a substitute claimed to be the published full text. |

The added synthesis distinguishes solver design, influence scoring and benchmarking by their stated objectives. Its specific question—how W and pool membership affect a restricted-versus-full comparison—is derived from this manuscript's own paired design. It does not infer that prior papers universally omit tolerance checks, independent evaluation or seed comparisons.

The IMM publisher endpoint also returned 403 during this check. Its already-cited solver description was retained without extension. Remaining existing citations and source-scoped judgments are inherited; this report does not claim their full texts were newly audited.
