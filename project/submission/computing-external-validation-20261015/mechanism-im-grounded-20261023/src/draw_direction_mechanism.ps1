param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))
$ErrorActionPreference = 'Stop'
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$app = New-Object -ComObject Visio.Application
$app.Visible = $false
$app.AlertResponse = 7
$doc = $null
$script:items = [System.Collections.Generic.List[object]]::new()
$C = @{
  ink='RGB(20,29,38)'; muted='RGB(97,108,120)'; faint='RGB(222,226,231)'; pale='RGB(248,249,251)'; white='RGB(255,255,255)';
  blue='RGB(33,101,163)'; blueFill='RGB(229,240,250)'; orange='RGB(193,93,47)'; orangeFill='RGB(253,237,228)';
  teal='RGB(0,126,121)'; tealFill='RGB(226,245,242)'; gray='RGB(189,197,204)'
}
function SetCell($s,$n,$v){ $s.CellsU($n).FormulaU=[string]$v }
function X($v){ return 7.5*$v/1200 }
function Y($v){ return $script:H-(7.5*$v/1200) }
function Track($s,$t,$x,$y,$w,$h,$f){$script:items.Add([pscustomobject]@{id=$s.ID;text=$t;x=$x;y=$y;width=$w;height=$h;font_pt=$f})}
function Box($x,$y,$w,$h,$t='',$fill=$C.white,$stroke=$C.faint,$font=8.7,$bold=$false,$align=0,$round=$true){
  $s=$script:p.DrawRectangle((X $x),(Y ($y+$h)),(X ($x+$w)),(Y $y))
  if($fill -eq 'none'){SetCell $s 'FillPattern' '0'}else{SetCell $s 'FillForegnd' $fill}
  if($stroke -eq 'none'){SetCell $s 'LinePattern' '0'}else{SetCell $s 'LineColor' $stroke;SetCell $s 'LineWeight' '0.65 pt'}
  if($round){SetCell $s 'Rounding' '0.025 in'}
  $s.Text=$t;SetCell $s 'Char.Font' $script:font;SetCell $s 'Char.Size' "$font pt";SetCell $s 'Char.Color' $C.ink;SetCell $s 'Char.Style' $(if($bold){1}else{0});SetCell $s 'Para.HorzAlign' $align;SetCell $s 'VerticalAlign' '1'
  foreach($m in @('LeftMargin','RightMargin','TopMargin','BottomMargin')){SetCell $s $m '1.5 pt'};Track $s $t $x $y $w $h $font;return $s
}
function Txt($x,$y,$w,$h,$t,$font=8.7,$bold=$false,$align=0,$col=$C.ink){$s=Box $x $y $w $h $t 'none' 'none' $font $bold $align $false;SetCell $s 'Char.Color' $col;return $s}
function Line($x1,$y1,$x2,$y2,$col=$C.muted,$arrow=$true,$weight='0.8 pt',$dash=$false){
  $s=$script:p.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));SetCell $s 'LineColor' $col;SetCell $s 'LineWeight' $weight;if($dash){SetCell $s 'LinePattern' '2'}
  if($arrow){$dx=$x2-$x1;$dy=$y2-$y1;$len=[Math]::Sqrt($dx*$dx+$dy*$dy);if($len -gt 0){$ux=$dx/$len;$uy=$dy/$len;foreach($side in @(-1,1)){$ax=$x2-11*$ux+$side*4.4*(-$uy);$ay=$y2-11*$uy+$side*4.4*$ux;$a=$script:p.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));SetCell $a 'LineColor' $col;SetCell $a 'LineWeight' $weight}}};return $s
}
function Node($cx,$cy,$label='',$fill=$C.white,$stroke=$C.muted,$size=22,$bold=$false){
  $s=$script:p.DrawOval((X ($cx-$size/2)),(Y ($cy+$size/2)),(X ($cx+$size/2)),(Y ($cy-$size/2)));SetCell $s 'FillForegnd' $fill;SetCell $s 'LineColor' $stroke;SetCell $s 'LineWeight' '0.85 pt';$s.Text=$label;SetCell $s 'Char.Font' $script:font;SetCell $s 'Char.Size' '7.4 pt';SetCell $s 'Char.Color' $C.ink;SetCell $s 'Char.Style' $(if($bold){1}else{0});SetCell $s 'Para.HorzAlign' '1';SetCell $s 'VerticalAlign' '1';Track $s $label ($cx-$size/2) ($cy-$size/2) $size $size 7.4;return $s
}
function Tag($x,$y,$n,$col){$s=Node ($x+11) ($y+11) $n $col $col 22 $true;return $s}
try {
  $doc=$app.Documents.Add('');$script:font=$doc.Fonts.Item('Arial').ID;$script:H=4.5
  $script:p=$doc.Pages.Add();$script:p.Name='Direction and coverage diagnostic';SetCell $script:p.PageSheet 'PageWidth' '7.5 in';SetCell $script:p.PageSheet 'PageHeight' '4.5 in'
  Txt 34 20 1100 27 'A directed-network diagnostic: why a prestige pool can miss propagating seeds' 11.3 $true 0 $C.ink | Out-Null
  Txt 36 50 1090 18 'wiki-Vote, default PageRank-4k, W = 1280. Diagram uses the recorded arc orientation and summarizes a structural diagnostic; it is not a causal intervention.' 7.4 $false 0 $C.muted | Out-Null
  Line 34 78 1166 78 $C.faint $false '0.6 pt' | Out-Null

  # Three restrained panels; only the objects, not surrounding cards, carry the figure.
  Tag 38 103 'a' $C.ink | Out-Null; Txt 68 101 275 26 'Observed arc convention' 8.7 $true | Out-Null
  Txt 68 130 290 29 'stored arc: voter to votee; propagation follows the stored arc' 7.1 $false 0 $C.muted | Out-Null
  Line 52 165 360 165 $C.faint $false '0.55 pt' | Out-Null
  # Incoming-prestige node: many arrows enter, little outward reach.
  Node 173 232 'P' $C.orangeFill $C.orange 30 $true | Out-Null
  foreach($pt in @(@(90,185),@(100,275),@(162,325),@(262,180))){Node $pt[0] $pt[1] '' $C.white $C.gray 14|Out-Null;Line $pt[0] $pt[1] 158 229 $C.orange $true '0.8 pt'|Out-Null}
  Node 270 260 '' $C.white $C.gray 14|Out-Null;Line 188 236 258 257 $C.orange $true '0.8 pt'|Out-Null
  Txt 68 344 233 19 'incoming-prestige motif' 7.4 $false 1 $C.orange | Out-Null
  # Outward broadcaster node: fewer inputs, clearly fanning propagation forwards.
  Node 207 400 'B' $C.blueFill $C.blue 30 $true | Out-Null
  Node 118 405 '' $C.white $C.gray 14|Out-Null;Line 130 405 192 400 $C.blue $true '0.8 pt'|Out-Null
  foreach($pt in @(@(288,360),@(319,397),@(282,443),@(355,430))){Node $pt[0] $pt[1] '' $C.tealFill $C.teal 14|Out-Null;Line 222 400 $pt[0] $pt[1] $C.blue $true '0.9 pt'|Out-Null}
  Txt 83 452 244 19 'outgoing-broadcaster motif' 7.4 $false 1 $C.blue | Out-Null

  Tag 410 103 'b' $C.ink | Out-Null;Txt 440 101 320 26 'Candidate-pool truncation' 8.7 $true | Out-Null
  Txt 440 130 327 29 'ranking membership can differ from the nodes that the full reference selects' 7.1 $false 0 $C.muted | Out-Null
  Line 402 165 787 165 $C.faint $false '0.55 pt' | Out-Null
  Txt 446 174 140 18 'PageRank ranking' 8.2 $true 0 $C.orange | Out-Null
  $rankY=@(203,233,263,293,323,353);$rankLbl=@('P','P','P','P','...','B')
  for($i=0;$i -lt $rankY.Count;$i++){ $fill=if($i -lt 5){$C.orangeFill}else{$C.blueFill};$str=if($i -lt 5){$C.orange}else{$C.blue};Box 471 $rankY[$i] 76 23 $rankLbl[$i] $fill $str 8.4 $true 1|Out-Null }
  Line 448 341 566 341 $C.orange $false '1.0 pt' $true | Out-Null;Txt 575 329 128 25 'top-20 cutoff' 7.6 $true 0 $C.orange | Out-Null
  Txt 441 388 318 18 'PageRank-4k pool at W=1280:' 8.1 $true | Out-Null
  Box 441 410 285 47 'mean in-degree 249.75     mean out-degree 56.2' $C.orangeFill $C.orange 8.2 $false 1 | Out-Null
  Box 441 464 285 45 'full-reference seed coverage: 0/5 on every path' $C.white $C.orange 8.2 $true 1 | Out-Null

  Tag 818 103 'c' $C.ink | Out-Null;Txt 848 101 280 26 'Independent utility readout' 8.7 $true | Out-Null
  Txt 848 130 275 29 'the restricted pool changes eligibility only; both arms diffuse on the same graph' 7.1 $false 0 $C.muted | Out-Null
  Line 808 165 1166 165 $C.faint $false '0.55 pt' | Out-Null
  # Full candidate seed and cascade.
  Txt 845 174 132 17 'full candidate set' 8.0 $true 0 $C.blue | Out-Null
  Node 872 223 'B' $C.blueFill $C.blue 27 $true | Out-Null
  foreach($pt in @(@(945,194),@(980,227),@(936,264),@(1031,274))){Node $pt[0] $pt[1] '' $C.tealFill $C.teal 14|Out-Null;Line 887 223 $pt[0] $pt[1] $C.blue $true '0.9 pt'|Out-Null}
  Txt 1044 204 102 38 "reference seed`nreaches outward" 7.2 $false 0 $C.blue | Out-Null
  Line 838 299 1145 299 $C.faint $false '0.55 pt' | Out-Null
  Txt 845 316 147 17 'PageRank-4k eligible set' 8.0 $true 0 $C.orange | Out-Null
  Node 872 366 'P' $C.orangeFill $C.orange 27 $true | Out-Null
  Node 944 366 '' $C.white $C.gray 14|Out-Null;Line 887 366 932 366 $C.orange $true '0.9 pt'|Out-Null
  Txt 973 347 160 38 "reference seed is outside`nthe truncated pool" 7.2 $false 0 $C.orange | Out-Null
  Box 838 401 304 119 "Observed independent outcome`nmean across 5 paths`nDelta incremental spread = -40.69334 nodes`nincremental loss = 73.01%" $C.tealFill $C.teal 7.2 $true 1 | Out-Null

  Line 34 543 1166 543 $C.faint $false '0.6 pt' | Out-Null
  Txt 38 562 115 17 'Interpretation' 8.2 $true | Out-Null
  Txt 160 560 985 35 'Under the recorded wiki-Vote orientation, an incoming-importance ranking can exclude high-outgoing seed candidates. The observed loss is consistent with this direction-and-coverage pathway; reverse-orientation evidence was not collected.' 7.8 $false 0 $C.ink | Out-Null
  Txt 150 598 995 15 'This schematic does not claim that PageRank is generally unsuitable for influence maximization.' 6.9 $false 0 $C.muted | Out-Null

  if($doc.Pages.Count -gt 1){$doc.Pages.Item(1).Delete(1)}
  $vsdx=Join-Path $OutputDir 'wiki_vote_direction_coverage_mechanism_v3.vsdx';$doc.SaveAs($vsdx)
  $script:p.Export((Join-Path $OutputDir 'wiki_vote_direction_coverage_mechanism_v3.svg'));$script:p.Export((Join-Path $OutputDir 'wiki_vote_direction_coverage_mechanism_v3.png'))
  $script:items | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDir 'native_shape_inventory.json') -Encoding utf8
  Write-Output "Saved native Visio source: $vsdx"
} finally { if($doc){$doc.Close()};$app.Quit() }
