$ErrorActionPreference='Stop'
$pkg=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1'
$main=Join-Path $pkg 'manuscript.md'
$text=Get-Content -LiteralPath $main -Raw -Encoding UTF8
if($text.Contains('Fig2-experimental-design.png')){throw 'Design already integrated; refusing duplicate insertion.'}
Copy-Item -LiteralPath $main -Destination (Join-Path $pkg 'manuscript_before_design_integration_20260921.md')
# Renumber display references simultaneously; original result asset names stay stable.
$text=[regex]::Replace($text,'\b(Figure |Fig\. )([2-6])\b',{param($m) $m.Groups[1].Value+([int]$m.Groups[2].Value+1)})
$text=$text.Replace('Table 3','Table 4')
$overview=@'
## 3 Experimental design

The experiment addresses three linked questions. First, does refinement of a fixed selection-world path preserve the full-greedy decision? Second, does a degree-restricted search reproduce the full reference at the same selection budget? Third, how do its independently evaluated spread and measured computation time compare? Figure 2 summarizes the crossed comparison structure. Table 2 describes the graph instances, while Table 3 distinguishes varied factors from shared controls.

![Experimental comparison design](figures/Fig2-experimental-design.png)

**Fig. 2** Experimental design and comparison units. (a) Four contact-derived graphs provide seven admitted combinations of network and seed budget; filled circles indicate inclusion and the cross marks the SFHH setting excluded during resource preflight. (b) Each setting is crossed with two random-world paths and three nested selection budgets, giving 42 conditions. (c) Each condition runs full greedy and three degree-pool arms, giving 168 arm executions. Eligibility alone changes between arms; the diffusion topology is shared. The small networks illustrate this distinction and do not encode measured pool sizes. (d) Selected sets are evaluated on 2,000 worlds disjoint from selection and shared across arms, selection budgets and seed budgets within each pair of network and path. Seed traces and timing come from selection records and the timed execution; spread comes from evaluation. Diagram tiles are schematic. Conditions sharing data or worlds are dependent comparisons, not independent network replicates.
'@
$text=$text.Replace('## 3 Experimental design',$overview)
$table=@'
**Table 3. Experimental factors and controls. The matrix was fixed before confirmation results; the final row identifies diagnostics added subsequently.**

| Component | Setting | Role in the comparison |
| --- | --- | --- |
| Network and seed budget | Four networks; k = 5 for all, k = 20 for three | Seven admitted settings (Table 2) |
| Selection resolution | W = 20, 80, 320 | Refines the empirical objective on nested prefixes |
| Random-world path | 301, 302 | Two realizations within each network–seed-budget setting |
| Candidate eligibility | Full V; top min(n, 2k), min(n, 4k), min(n, 8k) by historical weighted degree | Four paired arms; the pool remains fixed during selection |
| Historical graph | First 65% of complete timestamp groups; bidirectional aggregate | Shared input graph and ranking information |
| Diffusion | Independent cascade; p = 0.01; horizon 3 | Fixed simulator across all comparisons |
| Selection controls | Same worlds and deterministic node-ID tie-breaking within a condition | Makes same-budget arm comparisons reproducible |
| Evaluation worlds | 2,000 disjoint from selection; reused within a network–path pair | Paired utility estimates; shared worlds induce dependence |
| Timing scope | Greedy search plus final evaluation; excludes graph preparation and ranking | Defines the reported time saving |
| Additional diagnostics | Set overlap, first divergence, full-pool classification, conditional Monte Carlo intervals | Post-hoc analysis of frozen outputs |

Three comparison units follow from this design. A trajectory block fixes the network, seed budget and path, and contains the three nested selection budgets; there are 14 such blocks. An arm comparison additionally fixes the selection budget and contrasts one pool against full greedy; there are 126 such comparisons. A paired evaluation difference compares two selected sets on one shared evaluation world. These units answer different questions and must not be treated as interchangeable replications.

'@
$text=$text.Replace('### 3.3 Analysis',$table+'### 3.3 Analysis')
$text=$text.Replace('because its projected full-reference computation exceeded the four-hour serial ceiling.','because preflight projections indicated that including it would exceed the four-hour serial ceiling for the confirmation matrix.')
[IO.File]::WriteAllText($main,$text,[Text.UTF8Encoding]::new($false))
$si=Join-Path $pkg 'supplementary_information.md'
$s=Get-Content -LiteralPath $si -Raw -Encoding UTF8
$s=$s.Replace('Table 3 of the main manuscript','Table 4 of the main manuscript').Replace('Figures 5 and 6','Figures 6 and 7').Replace('Figures 2–4','Figures 3–5').Replace('Figures 5–6','Figures 6–7').Replace('Figure 3 distinguishes','Figure 4 distinguishes')
$s+="`n`nFigure 2 documents the admitted matrix, nested budgets, paired arms and disjoint evaluation design. Its native master is ``figures/Fig2-experimental-design.vsdx``, generated by ``analysis/build_visio_experimental_design.ps1`` using the shared helpers in ``analysis/build_visio_mechanism.ps1``. Original result-asset filenames retain their earlier numbers; display numbering in the manuscript and the figure index is authoritative.`n"
[IO.File]::WriteAllText($si,$s,[Text.UTF8Encoding]::new($false))
