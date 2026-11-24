# Contribution positioning decision

## Candidate framing A — finite-reference budget sensitivity

**Claim.** A finite simulation budget can change the full-greedy reference and
therefore alter the apparent quality of a candidate restriction.

**Evidence.** In the frozen external matrix, ca-GrQc has five changed full sets
from W80 to W320 and again from W320 to W1280; CollegeMsg changes some sets;
wiki-Vote does not. The historical archive has 16/40 changes from W1280 to W5120.
Paired independent evaluations show that a set change and a utility change are
distinct outcomes.

**Boundary and risk.** This is useful evaluation evidence but budget sensitivity
is already a familiar finite-Monte-Carlo concern. The former ca-GrQc sign reversal
under default PageRank does not survive the strict-ranking control, so framing the
paper as a general ``budget reversal'' result would overstate the evidence.

## Candidate framing B — an evaluation chain with separate reference and ranking resolution

**Claim.** Candidate-restriction evaluation can be changed by two distinct,
reportable resolution choices: the finite-world reference budget and the numerical
resolution used to truncate a ranking. Both should be separated from independent
utility and candidate coverage.

**Evidence.** Strict PageRank pools are stable at 1e-14, but differ from default
pools on ca-GrQc and wiki-Vote. On ca-GrQc, strict PageRank4k changes every selected
set relative to default and removes the default W80-to-W1280 direction reversal;
its relative quality still shifts from a -11.25% to -0.54% loss. CollegeMsg is
identical under the two rankings and retains its loss. wiki-Vote retains 73.96%
strict 4k loss. The study separately records sequence/set agreement, independent
spread, coverage, coupling and cost.

**Boundary and risk.** The evidence is empirical, restricted to NetworkX PageRank
and the stated graphs/IC settings; it is not a new PageRank algorithm, an error
analysis theorem or proof of a universal evaluation protocol.

## Decision

Use framing B as the manuscript’s primary contribution. It has a sharper, more
actionable result than framing A while retaining the budget result as a supporting
component. The central message is not that every low budget is misleading; it is
that reference resolution and ranking resolution can lead to different conclusions,
and they must be reported alongside independent utility. External topology and
coverage provide the scope test: CollegeMsg, ca-GrQc and wiki-Vote do not support a
single PageRank or fixed-coverage conclusion.

## One-sentence contribution

This study shows, on traceable finite-world influence-maximization evaluations,
that reference budget and numerical ranking precision are separate resolution
choices whose interaction with candidate truncation can alter apparent utility,
so sequence agreement, independent spread and coverage must be reported separately.
