# Third-Dataset Admission Record

Date: 2026-07-28

## Required Contract

A primary dataset for this study must provide all of the following from a
public, verifiable source:

1. A license or terms that permit the intended research use.
2. Stable user identifiers.
3. Directed, time-stamped interactions.
4. An observed parent-child propagation relation, rather than a parent inferred
   from timestamps, graph proximity, or heuristics.
5. A propagation semantics compatible with information diffusion, not merely
   an arbitrary temporal interaction.

## Candidate: PHEME Rumour Conversation Data

Status: **not admitted**.

- Potential fit: public conversation threads are commonly described as having
  tweet/reply identifiers and timestamps, which could supply observed reply
  parents.
- License verification: blocked. The Figshare article API endpoint for the
  candidate record returned HTTP 403 on three independent requests in this
  environment. The attempted mirror repository was unavailable (HTTP 404).
- Decision: do not download or use a mirror until a first-party landing page
  or archived metadata provides both the license and exact field provenance.

## Candidate: Stack Overflow via Stack Exchange API/Data Dump

Status: **not admitted as primary diffusion evidence**.

- License: official Stack Exchange API records returned `content_license:
  CC BY-SA 4.0`.
- Fields: question records expose `owner.user_id`, `question_id`, and
  `creation_date`; answer records expose `owner.user_id`, `question_id`, and
  `creation_date`. The answer `question_id` is an observed parent relation.
- Rejection reason: this is a question-answer response thread, not a content
  re-share or adoption cascade. Treating it as social diffusion would change
  the scientific target and violate the predeclared semantic criterion.
- Permitted future role: an explicitly labelled robustness study of temporal
  user-interaction influence, only after a separate protocol is approved.

## Candidate: Hacker News Comment Tree

Status: **not admitted as primary diffusion evidence**.

- Field evidence: the official Firebase record for comment `2921983` exposes
  `by`, `parent`, `time`, and `type: comment`, so a directed, time-stamped
  comment-parent interaction can be reconstructed without heuristic parent
  inference.
- License verification: incomplete. The official legal-page request timed out;
  no first-party research redistribution license was established.
- Rejection reason: comment-parent links encode discussion replies, not a
  content re-share/adoption cascade. Even with a verified license this would
  require a separately labelled interaction-influence protocol.

## Candidate: Mastodon Public Reblogs

Status: **not admitted**.

- Potential fit: public ActivityPub status objects can reference an original
  status for a reblog, which would be an observed propagation parent.
- Verification result: first-party public-timeline and terms requests timed
  out before returning a record or a license statement.
- Decision: no data were downloaded. A federated public endpoint is not a
  substitute for a citable dataset license and preservation policy.

## Candidate: Reddit Comment Tree

Status: **not admitted**.

- Potential fit: comment trees conventionally expose an author, parent ID, and
  UTC timestamp.
- Verification result: the first-party JSON endpoint timed out; neither raw
  field provenance nor a research redistribution license was established.
- Decision: no data were downloaded. In addition, comment-parent relations are
  discussion replies rather than content re-propagation.

## Admission Outcome

No third primary dataset is currently admitted after the fixed screen. The
research package must be scoped to two-dataset validation and must not claim
three-dataset generalization. A future candidate must be documented with a
first-party license source and a raw-record sample showing user IDs, times, and
observed cascade-parent fields before any preprocessing or experiment run.
