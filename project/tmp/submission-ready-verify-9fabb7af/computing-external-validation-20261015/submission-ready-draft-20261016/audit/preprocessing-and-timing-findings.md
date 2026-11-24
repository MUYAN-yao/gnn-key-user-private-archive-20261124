# Audit findings and impact decisions

## Topology and direction

Independent raw-text reconstruction identifies ca-GrQc node `12295` as appearing
only in a self-loop. Frozen code removes loops before collecting node IDs. Thus
5,241 non-self-edge endpoints and 28,968 reciprocal arcs are reproducible. Twelve
loop rows are removed; the raw node universe is 5,242. The pre-outcome manifest
already froze n=5,241 and the processed graph hash. The prose 'retain all listed
nodes appearing in edges' is ambiguous about pre/post-filter endpoints; record
this ambiguity, not a post-hoc claim that all original nodes were retained.
The manuscript explicitly limits results to the frozen non-self-endpoint graph.
An isolated seed cannot add non-seed reach, but reinserting it changes lexical
indices and therefore hash worlds: no claim of byte-identical finite-path results
on a 5,242-node representation is made. No silent preprocessing change or rerun.

CollegeMsg arcs are sender to receiver; historical weighting counts sent retained
messages. wiki-Vote arcs are voter to votee, not empirically observed influence.
Diffusion follows those outgoing arcs as an explicit simulation assumption.
Standard unweighted PageRank follows incoming importance (NetworkX defaults:
alpha=.85, tol=1e-6, max_iter=100, uniform personalization/dangling handling).
Degree is distinct outgoing-neighbour count. Degree and PageRank differ in target
orientation on directed graphs; no universal superiority claim is justified.
ca-GrQc is reciprocal, so its difference cannot be attributed to direction alone.

## Source hash enforcement

The frozen runner validates the source manifest including the JSON data manifest,
but does not compare live raw-file bytes with that data manifest before execution.
This is a fail-closed enforcement gap relative to config.stopping_rules, not a
demonstrated changed-input experiment. Retrospective audit compares current raw
hashes, frozen graph hashes and every condition's recorded input/graph metadata.
The reproduction wrapper added in review-v2 checks raw and source hashes first.
Frozen runner and outputs remain unchanged. Any mismatch would block acceptance.

## Time and memory

Frozen preparation_seconds contains raw loading, CSR, all rankings, source/graph
hashes and graph statistics. Adding ranking_seconds again double counts ranking;
it also charges irrelevant rankings to full eligibility. Random pool construction
was not separately timed. Preserve these archived observations, and supply a
post-hoc setup-only measurement including one method's sorting/pool construction.
Hybrid deployment = fresh parse/CSR + relevant rank/pool + selection-world
preparation + selection. Hybrid verification adds evaluation-world preparation
and evaluation. These are assembled estimates under a warm Python process, not
direct end-to-end wall-clock trials. JIT/import/download/write overhead excluded.
Selection-only is separately reported with graph/worlds already available.

JSON peak_working_set_bytes is a positive psutil process-lifetime peak. Its maximum
is 3.448822 GiB in the main experiment with M=10,000, distinct from the preflight's
M=1,000 and sub-625 MB claim. Do not reinterpret archived JSON as an overflow.
Any earlier negative PowerShell display has no retained diagnostic establishing
its cause and is not used as a memory measurement or 'corrected' numerically.

## Claim scope and additional computation

Retain W<=1280 external claims; do not call that converged or approximate-optimal.
No W5120 matrix is required to report the measured contrasts within this range.
Strict replay reruns frozen scores for verification without adding new paths or
updating estimates. Post-hoc setup timing, structural diagnostics and descriptive
t intervals are labelled; primary sign-test family remains frozen.

## PageRank numerical precision: substantive qualification

The candidate-only diagnostic tightened NetworkX's tolerance from 1e-6 to 1e-12
and checked pool identity at 1e-14. NetworkX's stopping criterion scales with n,
so the default tolerance cannot be treated as an exact ranking oracle. Before
inspecting new utilities, a separate post-hoc protocol froze two PageRank arms
on all three graphs and all five original W1280 paths: 15 conditions, 30 arms.
All completed. This does not create new independent paths or replace primary tests.

ca-GrQc PageRank-4k replaces two candidates and changes all five selected sets:
its mean paired difference becomes +0.02608 rather than -0.25082. Individual
differences range from -0.0408 to +0.1789, and no ordered trace equals full greedy.
Thus the original mean loss is solver-sensitive; the positive mean does not
establish superiority or equivalence. CollegeMsg pools and outcomes are unchanged.
wiki-Vote replaces one candidate per pool and retains large losses: -41.21970
for 4k (73.96% incremental loss), -13.63982 for 5% (24.47%). Directional mismatch
remains a consistent explanation on wiki-Vote, not an isolated causal mechanism.
See supplement-pr-precision/protocol.md, source_manifest.json, summary.csv and
the 15 paired JSON/NPZ outputs. The main cost/tolerance figures continue to report
the frozen default solver and are explicitly labelled accordingly.

Final supplementary setup timings were rerun without concurrent audit or
precision-control computation. Earlier provisional timing files are retained;
they are not used for the final cost tables. Candidate lexical sorting already
inside the selection timer is not charged a second time.
