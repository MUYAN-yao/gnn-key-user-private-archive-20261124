# Third-Dataset v3 Screening Protocol

## Purpose

Screen a third primary dataset without weakening the causal-provenance boundary
used by the manuscript. This is a registry for future candidates, not evidence
that a dataset has been admitted.

## Mandatory Evidence Per Candidate

1. A first-party license or terms page permitting the intended research use.
2. A citable field schema and a raw-record sample showing stable user IDs,
   directed interactions, and ISO-8601 timestamps.
3. An observed reshare/adoption parent identifier in the raw record, not a
   reconstructed parent based on time or graph proximity.
4. Documentation that the parent relation represents content re-propagation or
   adoption rather than a generic discussion reply.
5. A reproducible acquisition method that does not rely on unlicensed mirrors.

## Decision Procedure

- Record each candidate, source URLs, access date, schema fields, license
  evidence, and propagation semantics in a new section of
  `data_cards/third_dataset_admission.md`.
- Reject immediately if any mandatory item is absent. Do not download,
  preprocess, or cite a rejected source as primary evidence.
- Admit only after all five items are independently checked and a data card is
  complete. A newly admitted dataset must receive a separately preregistered
  time-forward protocol; it must not be merged with frozen Digg/Higgs results.

## Current State

No new candidate has been admitted. The previous PHEME, Stack Exchange, Hacker
News, Mastodon, and Reddit decisions remain controlling until a new candidate
meets every mandatory item.
