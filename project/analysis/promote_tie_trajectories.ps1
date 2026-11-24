$ErrorActionPreference='Stop'
$pkg=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1'
$main=Join-Path $pkg 'manuscript.md'
$supp=Join-Path $pkg 'supplementary_information.md'
$m=Get-Content -LiteralPath $main -Raw -Encoding UTF8
$s=Get-Content -LiteralPath $supp -Raw -Encoding UTF8
$pattern='(?s)!\[Individual tie trajectories\]\(figures/FigS1-tie-trajectories\.png\)\r?\n\r?\n\*\*Fig\. S1\*\*.*?(?=\r?\n\r?\nDecision time)'
$block=[regex]::Match($s,$pattern)
if(-not $block.Success){throw 'Expected supplementary figure block missing; no changes made.'}
Copy-Item -LiteralPath $main -Destination (Join-Path $pkg 'manuscript_before_trajectory_promotion_20260921.md')
Copy-Item -LiteralPath $supp -Destination (Join-Path $pkg 'supplement_before_trajectory_promotion_20260921.md')
$m=[regex]::Replace($m,'\b(Figure |Fig\. )([4-7])\b',{param($v) $v.Groups[1].Value+([int]$v.Groups[2].Value+1)})
$m=$m.Replace('Supplementary Fig. S1','Fig. 4')
$insert=$block.Value.Replace('**Fig. S1**','**Fig. 4**')
$m=$m.Replace('### 4.2 Which pools reproduce the reference, and at what cost?', $insert+"`n`n"+'### 4.2 Which pools reproduce the reference, and at what cost?')
$s=[regex]::Replace($s,$pattern,'The complete individual tie trajectories are displayed in main-text Fig. 4. Their 42 block-budget observations remain available in `figures/FigS1-tie-trajectories-source.csv`.')
$s=$s.Replace('Figures 6 and 7','Figures 7 and 8').Replace('Figure 4 distinguishes','Figure 5 distinguishes')
$s=$s.Replace(('Figures 3'+[char]0x2013+'5'),'Figures 3, 5 and 6')
$s=$s.Replace(('Figures 6'+[char]0x2013+'7'),'Figures 7 and 8')
$s=$s.Replace('Figure 3 and Supplementary Figure S1','Figures 3 and 4')
[IO.File]::WriteAllText($main,$m,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($supp,$s,[Text.UTF8Encoding]::new($false))
$numbers=@([regex]::Matches($m,'\*\*Fig\. (\d+)\*\*') | ForEach-Object {[int]$_.Groups[1].Value})
if(($numbers -join ',') -ne '1,2,3,4,5,6,7,8'){throw 'Figure numbering verification failed.'}
$links=[regex]::Matches($m,'!\[[^]]*\]\(([^)]+)\)')
foreach($l in $links){if(-not(Test-Path (Join-Path $pkg $l.Groups[1].Value))){throw 'Missing figure asset.'}}
Write-Output "Verified eight consecutive main figures and $($links.Count) image links."
