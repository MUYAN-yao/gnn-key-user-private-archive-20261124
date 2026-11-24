param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))
$ErrorActionPreference='Stop'; $OutputDir=[IO.Path]::GetFullPath($OutputDir); New-Item -ItemType Directory -Force -Path $OutputDir|Out-Null
$app=New-Object -ComObject Visio.Application; $app.Visible=$false; $app.AlertResponse=7; $doc=$null
$script:items=[System.Collections.Generic.List[object]]::new(); $C=@{ink='RGB(22,31,42)';muted='RGB(102,112,124)';rule='RGB(218,223,229)';gray='RGB(189,196,204)';blue='RGB(25,103,166)';blueFill='RGB(230,240,250)';orange='RGB(198,93,43)';orangeFill='RGB(253,238,229)';teal='RGB(0,133,125)';tealFill='RGB(225,245,241)';white='RGB(255,255,255)'}
function C($s,$n,$v){$s.CellsU($n).FormulaU=[string]$v};function X($v){7.5*$v/1200};function Y($v){$script:H-(7.5*$v/1200)}
function Track($s,$t,$x,$y,$w,$h,$f){$script:items.Add([pscustomobject]@{id=$s.ID;text=$t;x=$x;y=$y;width=$w;height=$h;font_pt=$f})}
function T($x,$y,$w,$h,$t,$f=8,$b=$false,$a=0,$col=$C.ink){$s=$script:p.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));C $s 'FillPattern' '0';C $s 'LinePattern' '0';$s.Text=$t;C $s 'Char.Font' $script:font;C $s 'Char.Size' "$f pt";C $s 'Char.Style' $(if($b){1}else{0});C $s 'Char.Color' $col;C $s 'Para.HorzAlign' $a;C $s 'VerticalAlign' 1;Track $s $t $x $y $w $h $f;return $s}
function RectBox($x,$y,$w,$h,$t='',$fill=$C.white,$line=$C.rule,$f=8,$b=$false,$a=1){$s=$script:p.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));C $s 'FillForegnd' $fill;C $s 'LineColor' $line;C $s 'LineWeight' '0.65 pt';C $s 'Rounding' '0.018 in';$s.Text=$t;C $s 'Char.Font' $script:font;C $s 'Char.Size' "$f pt";C $s 'Char.Style' $(if($b){1}else{0});C $s 'Char.Color' $C.ink;C $s 'Para.HorzAlign' $a;C $s 'VerticalAlign' 1;Track $s $t $x $y $w $h $f;return $s}
function L($x1,$y1,$x2,$y2,$col=$C.muted,$arrow=$true,$w='0.85 pt',$dash=$false){$s=$script:p.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));C $s 'LineColor' $col;C $s 'LineWeight' $w;if($dash){C $s 'LinePattern' '2'};if($arrow){$dx=$x2-$x1;$dy=$y2-$y1;$z=[math]::Sqrt($dx*$dx+$dy*$dy);if($z -gt 0){$ux=$dx/$z;$uy=$dy/$z;foreach($q in @(-1,1)){$ax=$x2-10*$ux+$q*4*(-$uy);$ay=$y2-10*$uy+$q*4*$ux;$a=$script:p.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));C $a 'LineColor' $col;C $a 'LineWeight' $w}}};return $s}
function N($x,$y,$txt='',$fill=$C.white,$line=$C.muted,$d=22,$b=$false){$s=$script:p.DrawOval((X($x-$d/2)),(Y($y+$d/2)),(X($x+$d/2)),(Y($y-$d/2)));C $s 'FillForegnd' $fill;C $s 'LineColor' $line;C $s 'LineWeight' '0.9 pt';$s.Text=$txt;C $s 'Char.Font' $script:font;C $s 'Char.Size' '7.4 pt';C $s 'Char.Style' $(if($b){1}else{0});C $s 'Char.Color' $C.ink;C $s 'Para.HorzAlign' 1;C $s 'VerticalAlign' 1;Track $s $txt ($x-$d/2) ($y-$d/2) $d $d 7.4;return $s}
try{
 $doc=$app.Documents.Add('');$script:font=$doc.Fonts.Item('Arial').ID;$script:H=4.2;$script:p=$doc.Pages.Add();$script:p.Name='Candidate coverage mechanism';C $script:p.PageSheet 'PageWidth' '7.5 in';C $script:p.PageSheet 'PageHeight' '4.2 in'
 T 34 18 1120 22 'Candidate coverage can change diffusion before spread is evaluated' 10.0 $true|Out-Null
 T 36 46 1110 17 'Structural diagnostic for wiki-Vote at W = 1280. Arcs are stored and propagated from voter to votee.' 7.2 $false 0 $C.muted|Out-Null
 L 34 72 1166 72 $C.rule $false '0.55 pt'|Out-Null
 # A: node role discrepancy in the observed arc direction
 T 38 88 320 25 'A  Direction of the diagnostic' 8.1 $true|Out-Null;T 38 116 320 23 'incoming ranking score versus outward simulated reach' 6.5 $false 0 $C.muted|Out-Null
 L 36 145 378 145 $C.rule $false '0.5 pt'|Out-Null
 N 178 209 'P' $C.orangeFill $C.orange 32 $true|Out-Null
 foreach($q in @(@(78,171),@(88,250),@(144,294),@(273,170))){N $q[0] $q[1] '' $C.white $C.gray 14|Out-Null;L $q[0] $q[1] 162 207 $C.orange $true '0.8 pt'|Out-Null}; N 281 222 '' $C.white $C.gray 14|Out-Null;L 194 211 269 221 $C.orange $true '0.8 pt'|Out-Null
 T 83 307 194 15 'incoming-prestige motif' 7 $false 1 $C.orange|Out-Null
 N 195 362 'B' $C.blueFill $C.blue 32 $true|Out-Null; N 104 365 '' $C.white $C.gray 14|Out-Null;L 117 365 179 362 $C.blue $true '0.8 pt'|Out-Null
 foreach($q in @(@(271,324),@(309,357),@(270,400),@(344,385))){N $q[0] $q[1] '' $C.tealFill $C.teal 14|Out-Null;L 211 362 $q[0] $q[1] $C.blue $true '0.9 pt'|Out-Null};T 89 416 220 15 'outgoing-broadcaster motif' 7 $false 1 $C.blue|Out-Null
 # B: the candidate truncation actually blocks a seed.
 T 415 88 340 25 'B  Eligibility changes at the cutoff' 8.1 $true|Out-Null;T 415 116 340 23 'the pool constrains seed selection, not the diffusion graph' 6.5 $false 0 $C.muted|Out-Null
 L 407 145 792 145 $C.rule $false '0.5 pt'|Out-Null
 T 430 160 110 15 'full candidates' 7.3 $true 0 $C.blue|Out-Null;N 478 201 'B' $C.blueFill $C.blue 25 $true|Out-Null;T 510 189 185 25 'outward broadcaster is eligible' 7 $false 0 $C.blue|Out-Null
 L 434 238 744 238 $C.rule $false '0.5 pt'|Out-Null
 T 430 255 170 15 'PageRank-4k pool' 7.3 $true 0 $C.orange|Out-Null
 foreach($yy in @(289,326,363,400)){N 476 $yy 'P' $C.orangeFill $C.orange 23 $true|Out-Null}; L 432 415 535 415 $C.orange $false '0.9 pt' $true|Out-Null;T 545 405 117 18 'top-20 cutoff' 7.2 $true 0 $C.orange|Out-Null;N 476 451 'B' $C.white $C.blue 23 $true|Out-Null;T 510 439 205 28 'broadcaster is outside the pool' 7 $false 0 $C.orange|Out-Null
 T 431 480 290 16 '0 of 5 full-reference seeds covered on every path' 7.3 $true 0 $C.orange|Out-Null
 # C: use a real paired aggregate, native bars.
 T 824 88 330 25 'C  Independent spread is then measured' 8.1 $true|Out-Null;T 824 116 330 23 'same processed graph; disjoint 10,000-world evaluation' 6.5 $false 0 $C.muted|Out-Null
 L 807 145 1166 145 $C.rule $false '0.5 pt'|Out-Null
 T 850 164 260 16 'mean incremental spread (nodes)' 7.3 $true|Out-Null
 L 874 430 1116 430 $C.muted $false '0.7 pt'|Out-Null; L 874 189 874 430 $C.muted $false '0.7 pt'|Out-Null
 foreach($g in @(@(15,366),@(30,302),@(45,238),@(60,174))){L 874 $g[1] 1116 $g[1] $C.rule $false '0.45 pt' $true|Out-Null;T 836 ($g[1]-8) 32 15 ([string]$g[0]) 6.7 $false 2 $C.muted|Out-Null}
 RectBox 920 207 70 223 '55.74' $C.blueFill $C.blue 8.2 $true 1|Out-Null;RectBox 1022 370 70 60 '15.04' $C.orangeFill $C.orange 8.2 $true 1|Out-Null;T 900 438 110 16 'full reference' 7.1 $false 1 $C.blue|Out-Null;T 1006 438 105 16 'PageRank-4k' 7.1 $false 1 $C.orange|Out-Null
 T 840 470 276 22 'Delta = -40.69334 nodes   |   loss = 73.01%' 7.8 $true 1 $C.teal|Out-Null
 L 34 522 1166 522 $C.rule $false '0.55 pt'|Out-Null
 T 38 540 1108 25 'Interpretation: under the recorded wiki-Vote orientation, low candidate coverage is consistent with the observed utility gap. The experiment did not reverse edge orientation and does not identify a unique causal mechanism.' 7.4 $false 0 $C.ink|Out-Null
 T 38 576 1108 16 'Evidence: analysis/direction_diagnostics.csv and analysis/summary_by_method.csv (wiki_vote, resolution, W=1280). This is a network-specific diagnostic, not a general claim about PageRank.' 6.6 $false 0 $C.muted|Out-Null
 if($doc.Pages.Count -gt 1){$doc.Pages.Item(1).Delete(1)}; $f=Join-Path $OutputDir 'wiki_vote_candidate_coverage_mechanism_v2.vsdx';$doc.SaveAs($f);$script:p.Export((Join-Path $OutputDir 'wiki_vote_candidate_coverage_mechanism_v2.svg'));$script:p.Export((Join-Path $OutputDir 'wiki_vote_candidate_coverage_mechanism_v2.png'));$script:items|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $OutputDir 'native_shape_inventory_domain_v2.json') -Encoding utf8;Write-Output "Saved native Visio source: $f"
}finally{if($doc){$doc.Close()};$app.Quit()}
