# Literature Expansion Audit

Date: 2026-07-31

## Scope

This audit records the post-r28 literature expansion undertaken for the
Software Journal candidate. It follows the two-source metadata and
source-retrieved-BibTeX rule in `manuscript/citation_audit.md`. It does not
claim an exhaustive review.

## Search Procedure

- Workflow: multi-source literature search under `nature-academic-search`.
- Primary discovery source available in this environment: OpenAlex fallback
  search, queried for temporal/dynamic, community-aware, risk/uncertainty, and
  GNN influence maximization combinations.
- Metadata verification sources: Crossref REST DOI record and Semantic Scholar
  DOI record.
- BibTeX source: Crossref DOI transformation endpoint.
- Domestic-search attempt: Crossref DOI-prefix endpoint for prefix `10.13328`
  returned HTTP 404. This does not show that no additional domestic work
  exists; it means that endpoint cannot support an exhaustive domestic search.

## Screened Result Added

| DOI | Decision | Evidence boundary |
| --- | --- | --- |
| `10.3390/e24070904` | added as Fu et al. (2022) [29] | Crossref and Semantic Scholar agree on title, authors, journal, year, DOI, and abstract. The open PubMed Central record `PMC9322785` subsequently supplied the complete HTML text, whose abstract and introduction confirm the effective-link dynamic-IC and two-stage OEL scope. Crossref-sourced BibTeX is retained. No cross-paper numerical or protocol-equivalence claim is made. |
| `10.1002/ett.3054` | added as Han et al. (2017) [30] | Crossref and Semantic Scholar agree on title, authors, venue, DOI, and the 2016-online/2017-print timing. The Crossref abstract supports only the partial-community probing, observed-versus-real topology, and divide-and-conquer scope. Crossref-sourced BibTeX is retained. The author-manuscript URL returned HTML rather than a PDF, so no full-text feature, data, theorem, or result claim is made. |

## Screened But Not Added

- *基于社交网络弱连接属性的影响力最大化算法* (Yi Xiushuang, Hu Jinlin,
  and Wang Xingwei, *软件学报*, 2016, online record `16012`): a fresh official
  *软件学报* keyword search for “影响力最大化” returned four records: the two
  already cited 2017 records, the already cited online-first multilayer-GNN
  record, and this additional 2016 weak-tie method. The official record gives
  its title, authors, volume/issue and keyword set, and exposes a PDF link, but
  it provides no DOI. Crossref title search did not resolve a matching record,
  and OpenAlex keyword search did not return a matching work. It is therefore
  logged as a domestic lead, not added to the bibliography under the project's
  two-source metadata rule. This query is a journal-specific screening step,
  not evidence of an exhaustive Chinese-literature search.
- `10.1360/sspma-2023-0134`, Zhan et al., *A node-embedding-based influence
  maximization algorithm in temporal network*: CrossRef and OpenAlex agree on
  the title, five authors, journal record, DOI, and temporal-network/MMC
  abstract scope; DOI content negotiation returned source BibTeX. The
  publisher PDF endpoint returned a WAF block both to an ordinary HTTP client
  and to a browser session, while the OpenAlex full-text XML endpoint required
  authorization. It therefore remains an uncited lead rather than a
  full-text-backed domestic comparison.
- Recent results for dynamic-network influence maximization were identified
  through OpenAlex, including GCN, adaptive evolutionary, diversified, and
  survey directions. They were not added because their full text was not
  available in the current environment or because the retrieved metadata did
  not support a sharper comparison than the existing 30-reference record.
- Broad GNN, community, and uncertainty queries produced substantial off-topic
  results after relevance re-ranking. These were discarded rather than cited
  for coverage.

## Consequence for the Manuscript

The bibliography now has 30 verified entries and includes title/abstract-scoped
dynamic effective-link and partial-community-probing comparisons. The Software
Journal literature-depth gate remains open: the official keyword screen confirms
three already cited domestic *软件学报* records plus one unverified domestic lead,
but it does not establish a comprehensive domestic review or full-text-backed
comparison for every cited recent method.

## Existing-Citation Full-Text Upgrade

- Yanchenko, Murata, and Holme (2023) [19], DOI `10.1007/s41109-023-00594-z`:
  the previously truncated publisher download was retried through the public
  Springer Open PDF endpoint on 2026-07-31 and yielded a valid 23-page PDF.
  Its abstract and formal problem statement confirm an ex ante setup: observe
  network snapshots through time p, select seeds before the remaining snapshots
  are observed, forecast future evolution using statistical, NMF, or GNN
  link-prediction methods, then apply IM methods on predicted networks. The
  study evaluates eight real-world and synthetic networks under SI diffusion.
  The related-work matrix and citation audit are upgraded to full-text scope;
  the manuscript's existing controlled differentiation is retained. No
  cross-paper numerical comparison, protocol equivalence, or new bibliography
  entry is claimed.
- Liu, Wang, and Ding (2024) [28], DOI `10.3390/electronics13163110`: although
  the interactive MDPI page returns access-denied in this environment, the
  public static PDF endpoint returned a valid 24-page CC BY article on
  2026-07-31. The abstract and introduction confirm an NDD_AGCN regression
  route using network/centrality vectors, neighborhood-discount labels to
  address overlap, learned node-spreading-power scores, and Top-K seed
  selection. Its experiments use IC and SIR models on several real-world
  networks. The citation audit and matrix are upgraded to full-text scope;
  no cross-paper performance claim or protocol equivalence is added.
- Li, Cai, Deng, Wang, Sellis, and Xia (2020) [17], DOI
  `10.1016/j.is.2020.101522`: the existing Figshare API route returned HTTP
  403, and the OpenAlex-listed Federation University ResearchOnline manuscript
  routes timed out over both HTTP and HTTPS on 2026-07-31. This entry remains
  title-scoped; the failed access routes are not treated as evidence about the
  paper's method, data, or results.
