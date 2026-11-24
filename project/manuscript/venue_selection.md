# Target-Journal Decision Record

## Current selected target: Applied Intelligence

The user selected **Applied Intelligence** as the current working target after
requiring a non-OA or sub-¥10,000 publication route. The journal is hybrid;
the regular subscription route has no APC. Its official page lists EI
Compendex and SCIE, satisfying the school's SCI/EI recognition paths for a
regular published Article. The topic fit is stronger than the zero-APC
alternatives because the paper concerns a GNN prior, temporal network and
influence-maximization decision problem.

The paper must be submitted as a regular Original Paper on the subscription
route, rather than Open Access, a special issue, collection, supplement or
conference track. No manuscript has been submitted and no editorial contact
has been made.

The current writing source is `manuscript/draft_zh_v0_1.md`; the English
abstract and introduction are `abstract_en_v0_1.md` and
`snam_introduction_en_v1.md`. Revision scope and evidence checks remain in
`snam_revision_01/revision_notes.md`; their analytical content is retained,
but target-specific formatting now follows the Applied Intelligence strategy
in `manuscript/applied_intelligence_submission_strategy.md`.

Positioning: empirical evaluation of temporal-network seed selection, with
separate evidence for prediction, utility, component effects, local search
cost and a k=5 full-search feasibility limit. No independent GNN utility
benefit, RIS superiority, end-to-end speedup, or acceptance probability is
claimed.

## Historical target: Social Network Analysis and Mining

The user previously selected **Social Network Analysis and Mining (SNAM)** and
requested manuscript improvement toward that venue. It is no longer the
working target because it is fully OA and its APC exceeds the user's budget.

Historical SNAM source record:
The current writing source is `manuscript/draft_zh_v0_1.md`; the English
abstract and introduction are `abstract_en_v0_1.md` and
`snam_introduction_en_v1.md`. Revision scope and evidence checks are recorded
in `snam_revision_01/revision_notes.md`.

Positioning: empirical evaluation of temporal-network seed selection, with
separate evidence for prediction, utility, component effects, and local
computational cost. No independent GNN utility benefit, RIS superiority,
end-to-end speedup, or acceptance probability is claimed.

Official sources inspected for this decision and revision:

- https://link.springer.com/journal/13278 — scope: theoretical and experimental
  social network analysis and mining; publisher lists EI Compendex and ESCI.
- https://link.springer.com/journal/13278/submission-guidelines — abstract of
  150–250 words without undefined abbreviations or unspecified references;
  4–6 keywords; relevant Statements and Declarations; author contributions and
  competing interests must also be supplied through the submission interface.
  The guide accepts editable manuscript sources and gives Word/docx formatting
  guidance. The current English abstract contains 207 whitespace-delimited
  words and six keywords.

The SNAM record is retained for historical scope comparison only. The next
formatting pass must use the current Applied Intelligence requirements. The
Software Journal template and its old gates below are also historical, not a
prerequisite to prose revision.
No manuscript has been submitted and no editorial contact has been made.

## Historical target: Software Journal

**Software Journal (软件学报)** was an earlier working target for the Chinese
manuscript. This historical record is not a claim that the paper meets its
acceptance standard.

## Official scope and requirements

Source accessed on 2026-07-29:
<https://www.jos.org.cn/jos/site/menu/20210909102616001?id=20210909102616001&name=%E6%8A%95%E7%A8%BF%E6%8C%87%E5%8D%97>

The official guide states that the journal publishes original work in computer
software fields, including algorithm design and analysis, pattern recognition
and artificial intelligence, computer networks, and related areas. It requires
an original, complete, clearly argued manuscript, and explicitly requires
authors to survey and compare both domestic and international relevant work.
The guide says to submit online, using a Word-formatted manuscript (with a
template and example available in the download area), and describes its review
as single blind. It places no fixed word or page limit at first submission.

## Template Discovery Preflight

On 2026-07-29, the official home page exposed the downloadable sample
`软件学报排版样例2025年版.doc` at:

<https://www.jos.org.cn/uploadfile/news_images/jos/2026-04-02/%E8%BD%AF%E4%BB%B6%E5%AD%A6%E6%8A%A5%E6%8E%92%E7%89%88%E6%A0%B7%E4%BE%8B2025%E5%B9%B4%E7%89%88.doc>

The server returned `application/msword`, `3,027,456` bytes, and
`Last-Modified: 2026-04-02`. This is a discovery preflight only. The final
conversion must re-check the download-area artifact immediately beforehand,
because the journal may replace the sample or template.

## Fit assessment

| Item | Assessment | Evidence or action needed |
| --- | --- | --- |
| Topic fit | plausible | The study concerns temporal-network optimization, graph learning, and influence maximization. |
| Originality support | conditionally supported | The strict v2-T0b result set and the separate v3 fairness/sensitivity confirmation are complete. Claims remain limited to the v2-T0b 18-contrast Holm family and v3's protocol-conditional negative results. |
| Empirical credibility | conditionally supported | The 30-run v2-T0b Higgs batch and 30-run v3 confirmation are complete; retain the two-dataset scope, protocol-repeat unit, Digg proxy-semantic limits, and the full-candidate/GNN-screening null result. |
| Related-work completeness | conditionally supported | Thirty-four audited references include domestic reviews and a full-text-inspected domestic multilayer GNN method, international temporal, robust, risk-aware, GNN, dynamic-network, community-aware, and uncertainty-aware work, plus a full-text-inspected temporal k-shell method. Entries without full text remain explicitly title/abstract-scoped; no method-level claim relies on them. Further expansion must follow the same dual-source and source-retrieved-BibTeX rule. |
| Initial submission format | pending | Convert the finalized Markdown only after all evidence and bibliography gates pass; use the official Word template rather than an inferred layout. |
| Authorship and submission | pending | Confirm author order, affiliations, funding, and conflict disclosures before first online submission because the guide states that post-submission updates are restricted. |

## Submission gate

Do not upload the present draft. Before conversion to the official template:

1. Preserve the completed strict v2-T0b result as its own 18-contrast Holm
   family; do not pool it with frozen v1 or claim superiority over RIS.
2. Retain the v3 result as a separate, Higgs-only protocol-conditional null
   result; do not use it to claim a GNN-screening, candidate-pool, or
   independent weight advantage.
3. Audit every result sentence against `manuscript/claim_ledger.md`.
4. Add only two-source-verified references, including a substantive comparison
   to relevant domestic work as required by the journal's guide.
5. Verify the currently downloadable official Word template and its required
   metadata fields immediately before format conversion.
