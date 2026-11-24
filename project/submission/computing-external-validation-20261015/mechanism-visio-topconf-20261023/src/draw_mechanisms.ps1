param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))
$ErrorActionPreference = 'Stop'
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
$app = New-Object -ComObject Visio.Application
$app.Visible = $false
$app.AlertResponse = 7
$doc = $null
$script:inventory = [System.Collections.Generic.List[object]]::new()
$C = @{
  ink='RGB(27,38,52)'; muted='RGB(102,116,132)'; light='RGB(222,228,235)'; white='RGB(255,255,255)';
  blue='RGB(45,91,156)'; blueFill='RGB(234,241,252)'; teal='RGB(9,126,121)'; tealFill='RGB(229,246,242)';
  orange='RGB(196,108,36)'; orangeFill='RGB(253,241,227)'; grayFill='RGB(247,249,251)'; red='RGB(182,70,72)'
}
function Cell($s,$n,$v) { $s.CellsU($n).FormulaU = [string]$v }
function X($v) { return 6.0*$v/1000 }
function Y($v) { return $script:height-(6.0*$v/1000) }
function AddMeta($s,$text,$x,$y,$w,$h,$font) { $script:inventory.Add([pscustomobject]@{page=$script:page.Name;id=$s.ID;text=$text;x=$x;y=$y;w=$w;h=$h;font_pt=$font}) }
function Box($x,$y,$w,$h,$text='',$fill=$C.white,$stroke=$C.light,$font=10,$bold=$false,$align=1,$round=$true) {
  $s=$script:page.DrawRectangle((X $x),(Y ($y+$h)),(X ($x+$w)),(Y $y))
  if($fill -eq 'none'){Cell $s 'FillPattern' '0'}else{Cell $s 'FillForegnd' $fill}
  if($stroke -eq 'none'){Cell $s 'LinePattern' '0'}else{Cell $s 'LineColor' $stroke;Cell $s 'LineWeight' '0.7 pt'}
  if($round){Cell $s 'Rounding' '0.035 in'}
  $s.Text=$text;Cell $s 'Char.Font' $script:fontID;Cell $s 'Char.Size' "$font pt";Cell $s 'Char.Color' $C.ink;Cell $s 'Char.Style' $(if($bold){1}else{0});Cell $s 'Para.HorzAlign' $align;Cell $s 'VerticalAlign' 1
  foreach($n in @('LeftMargin','RightMargin','TopMargin','BottomMargin')){Cell $s $n '2 pt'}
  AddMeta $s $text $x $y $w $h $font;return $s
}
function Txt($x,$y,$w,$h,$text,$font=10,$bold=$false,$align=0,$color=$C.ink){$s=Box $x $y $w $h $text 'none' 'none' $font $bold $align $false;Cell $s 'Char.Color' $color;return $s}
function Line($x1,$y1,$x2,$y2,$color=$C.muted,$arrow=$true,$dash=$false,$weight='0.9 pt') {
  $s=$script:page.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));Cell $s 'LineColor' $color;Cell $s 'LineWeight' $weight;if($dash){Cell $s 'LinePattern' '2'}
  if($arrow){$dx=$x2-$x1;$dy=$y2-$y1;$l=[Math]::Sqrt($dx*$dx+$dy*$dy);if($l -gt 0){$ux=$dx/$l;$uy=$dy/$l;foreach($side in @(-1,1)){$ax=$x2-10*$ux+$side*4.5*(-$uy);$ay=$y2-10*$uy+$side*4.5*$ux;$a=$script:page.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));Cell $a 'LineColor' $color;Cell $a 'LineWeight' $weight}}};return $s
}
function Oval($x,$y,$w,$h,$text='',$fill=$C.white,$stroke=$C.ink,$font=9,$bold=$false) {
  $s=$script:page.DrawOval((X $x),(Y ($y+$h)),(X ($x+$w)),(Y $y));Cell $s 'FillForegnd' $fill;Cell $s 'LineColor' $stroke;Cell $s 'LineWeight' '0.9 pt';$s.Text=$text;Cell $s 'Char.Font' $script:fontID;Cell $s 'Char.Size' "$font pt";Cell $s 'Char.Color' $C.ink;Cell $s 'Char.Style' $(if($bold){1}else{0});Cell $s 'Para.HorzAlign' '1';Cell $s 'VerticalAlign' '1';AddMeta $s $text $x $y $w $h $font;return $s
}
function Dot($cx,$cy,$label,$fill=$C.white,$stroke=$C.muted,$size=26){return Oval ($cx-$size/2) ($cy-$size/2) $size $size $label $fill $stroke 8 $true}
function Number($cx,$cy,$n,$color){return Oval ($cx-15) ($cy-15) 30 30 $n $color $color 10.6 $true}
function World($x,$y,$tint=$C.blueFill){
  Box $x $y 40 29 '' $tint $C.blue 8 $false | Out-Null
  Line ($x+9) ($y+9) ($x+20) ($y+18) $C.blue $false $false '0.5 pt'|Out-Null;Line ($x+20) ($y+18) ($x+31) ($y+9) $C.blue $false $false '0.5 pt'|Out-Null
  Dot ($x+9) ($y+9) '' $C.white $C.blue 5|Out-Null;Dot ($x+20) ($y+18) '' $C.white $C.blue 5|Out-Null;Dot ($x+31) ($y+9) '' $C.white $C.blue 5|Out-Null
}
function DrawGraph($x,$y,$scale=1.0,$highlight=@(),$seed=@()) {
  $pts=@(@(0,54),@(32,16),@(64,60),@(92,28),@(120,80),@(154,43),@(183,15),@(204,65),@(164,102),@(84,113),@(34,92))
  $edges=@(@(0,1),@(0,2),@(1,3),@(2,3),@(2,4),@(3,5),@(4,5),@(5,6),@(5,7),@(4,8),@(8,7),@(8,9),@(9,10),@(10,0),@(9,2))
  foreach($e in $edges){$a=$pts[$e[0]];$b=$pts[$e[1]];Line ($x+$a[0]*$scale) ($y+$a[1]*$scale) ($x+$b[0]*$scale) ($y+$b[1]*$scale) $C.light $false $false '0.7 pt'|Out-Null}
  for($i=0;$i -lt $pts.Count;$i++){$p=$pts[$i];$fill=$C.white;$stroke=$C.muted;if($highlight -contains $i){$fill=$C.tealFill;$stroke=$C.teal};if($seed -contains $i){$fill=$C.blueFill;$stroke=$C.blue};Dot ($x+$p[0]*$scale) ($y+$p[1]*$scale) '' $fill $stroke (20*$scale)|Out-Null}
}
function NewPage($name,$h){$script:page=$doc.Pages.Add();$script:page.Name=$name;$script:height=$h;Cell $script:page.PageSheet 'PageWidth' '6 in';Cell $script:page.PageSheet 'PageHeight' "$h in"}
try {
  $doc=$app.Documents.Add('');$script:fontID=$doc.Fonts.Item('Arial').ID
  NewPage 'Mechanism overview' 7.75
  Txt 32 20 930 25 'Candidate-restriction comparison has two resolutions' 12.2 $true | Out-Null
  Line 28 95 972 95 $C.light $false $false '0.7 pt' | Out-Null

  # Shared task: a full graph, a visibly truncated candidate ordering, and the pool boundary.
  Number 55 138 '1' $C.ink | Out-Null
  Txt 82 121 255 25 'One graph; restricted pool' 10.8 $true | Out-Null
  DrawGraph 60 177 1.28 @(1,3,5,7,8) @()
  Txt 66 333 255 26 'propagation graph G' 10.6 $true 1 $C.ink | Out-Null
  Line 343 218 387 218 $C.muted $true $false '1.1 pt' | Out-Null
  Txt 392 150 190 25 'ranking r(v)' 10.6 $true 1 $C.ink | Out-Null
  $ranks=@('1','2','3','4','5','6','7','8')
  for($i=0;$i -lt $ranks.Count;$i++){ $yy=180+$i*30;$fill=if($i -lt 5){$C.tealFill}else{$C.grayFill};$stroke=if($i -lt 5){$C.teal}else{$C.light};Box 413 $yy 108 27 $ranks[$i] $fill $stroke 10.6 $false|Out-Null }
  Line 397 332 538 332 $C.orange $false $true '1.4 pt' | Out-Null
  Txt 545 317 154 35 "top-m`nboundary" 10.6 $true 0 $C.orange | Out-Null
  Box 407 436 121 38 'C(tau)' $C.tealFill $C.teal 10.6 $true | Out-Null

  # Budget path (blue): finite world resolution moves the full reference.
  Number 82 546 '2' $C.blue | Out-Null
  Txt 110 529 300 25 'Finite reference W' 10.8 $true | Out-Null
  foreach($i in 0..2){World (118+$i*53) 596 $C.blueFill}
  Txt 286 599 64 25 'low W' 10.6 $true 0 $C.blue | Out-Null
  foreach($i in 0..5){World (118+$i*35) 640 $C.blueFill}
  Txt 347 643 70 25 'high W' 10.6 $true 0 $C.blue | Out-Null
  Line 253 610 271 610 $C.blue $true | Out-Null
  Line 305 653 323 653 $C.blue $true | Out-Null
  Txt 116 690 248 25 'full seeds S_full(W)' 10.6 $true 1 $C.blue | Out-Null
  Box 148 720 76 38 '{a, c}' $C.blueFill $C.blue 10.6 $true | Out-Null
  Line 229 737 259 737 $C.blue $true | Out-Null
  Box 264 720 76 38 '{a, d}' $C.blueFill $C.blue 10.6 $true | Out-Null

  # Tolerance path (orange): a boundary exchange moves the restricted pool before greedy selection.
  Number 542 546 '3' $C.orange | Out-Null
  Txt 570 529 315 25 'Ranking tolerance tau' 10.8 $true | Out-Null
  Box 586 599 107 36 'm' $C.orangeFill $C.orange 10.6 $true | Out-Null
  Box 586 643 107 36 'm+1' $C.grayFill $C.light 10.6 $false | Out-Null
  Line 706 619 750 619 $C.orange $true | Out-Null
  Box 761 599 107 36 'm' $C.tealFill $C.teal 10.6 $true | Out-Null
  Box 761 643 107 36 'm+1' $C.orangeFill $C.orange 10.6 $false | Out-Null
  Box 614 720 99 38 '{a, c}' $C.tealFill $C.teal 10.6 $true | Out-Null
  Line 718 737 748 737 $C.teal $true | Out-Null
  Box 753 720 99 38 '{a, e}' $C.tealFill $C.teal 10.6 $true | Out-Null

  # Merge into a clean evaluation stage, drawn on its own fresh worlds.
  Line 300 802 300 842 $C.blue $true | Out-Null
  Line 802 802 802 842 $C.teal $true | Out-Null
  Box 155 850 690 63 'MATCHED SELECTION: full greedy S_full(W)  versus  restricted-pool greedy S_pool(W, tau)' $C.grayFill $C.light 10.6 $true | Out-Null
  Line 500 940 500 978 $C.ink $true | Out-Null
  Box 155 972 690 78 "INDEPENDENT UTILITY READOUT`nD_eval = spread_eta(S_pool) - spread_eta(S_full)" $C.tealFill $C.teal 11 $true | Out-Null
  Box 150 1080 700 49 'Observed ca-GrQc: 2/20 candidates exchange; 5/5 selected sets change at W = 1280.' $C.white $C.light 10.6 $false 1 | Out-Null

  Line 28 1170 972 1170 $C.light $false $false '0.7 pt' | Out-Null
  Txt 40 1190 260 25 'Keep outputs distinct:' 10.6 $true | Out-Null
  Oval 315 1188 28 28 'A' $C.blueFill $C.blue 10.6 $true | Out-Null;Txt 351 1188 180 28 'agreement' 10.6 $false | Out-Null
  Oval 553 1188 28 28 'U' $C.tealFill $C.teal 10.6 $true | Out-Null;Txt 589 1188 150 28 'utility' 10.6 $false | Out-Null
  Oval 755 1188 28 28 'C' $C.orangeFill $C.orange 10.6 $true | Out-Null;Txt 791 1188 130 28 'cost' 10.6 $false | Out-Null
  NewPage 'Coupling mechanism' 3.96
  Txt 35 20 920 30 'Step-indexed coupling: an analytical timing mechanism' 13 $true|Out-Null
  Txt 37 54 916 25 'Illustrative chain s → u → v, h = 2. The same step-indexed world is used in the two rows.' 8.8 $false 0 $C.muted|Out-Null
  Line 30 89 970 89 $C.light $false $false '0.6 pt'|Out-Null
  Txt 44 112 167 24 'initial seeds' 9 $true|Out-Null;Txt 274 112 105 24 't = 0' 9 $true|Out-Null;Txt 525 112 105 24 't = 1' 9 $true|Out-Null;Txt 812 112 120 24 'realized reach' 9 $true|Out-Null
  Box 42 154 145 47 'S = {s}' $C.tealFill $C.teal 9.5 $true|Out-Null
  Dot 304 177 's' $C.tealFill $C.teal 28|Out-Null;Line 320 177 409 177 $C.teal $true|Out-Null;Dot 425 177 'u' $C.white $C.muted 28|Out-Null
  Dot 560 177 'u' $C.tealFill $C.teal 28|Out-Null;Line 576 177 665 177 $C.teal $true|Out-Null;Dot 681 177 'v' $C.white $C.muted 28|Out-Null
  Box 814 154 125 47 '3 nodes' $C.tealFill $C.teal 9.5 $true|Out-Null
  Box 42 244 145 47 "S' = {s, u}" $C.orangeFill $C.orange 9.5 $true|Out-Null
  Dot 304 267 'u' $C.orangeFill $C.orange 28|Out-Null;Line 320 267 409 267 $C.orange $false|Out-Null;Line 351 257 377 277 $C.orange $false|Out-Null;Line 351 277 377 257 $C.orange $false|Out-Null;Dot 425 267 'v' $C.white $C.muted 28|Out-Null
  Txt 535 246 180 42 "u already acted at t = 0;`nno retry at t = 1" 8.8 $false 1 $C.muted|Out-Null
  Box 814 244 125 47 '2 nodes' $C.orangeFill $C.orange 9.5 $true|Out-Null
  Box 42 331 897 51 'Adding u advances its only attempt. This realized step-indexed objective can be nonmonotone.' $C.grayFill $C.light 9.5 $false 1|Out-Null
  Txt 42 395 897 36 'A fixed-edge control draws one state per edge/world. This illustration alone does not establish any general submodularity result.' 8.4 $false 1 $C.muted|Out-Null
  if($doc.Pages.Count -gt 2){$doc.Pages.Item(1).Delete(1)}
  $vsdx=Join-Path $OutputDir 'evaluation_mechanisms.vsdx';$doc.SaveAs($vsdx)
  for($i=1;$i -le $doc.Pages.Count;$i++){$p=$doc.Pages.Item($i);$stem=if($i -eq 1){'mechanism_overview'}else{'coupling_counterexample'};$p.Export((Join-Path $OutputDir ($stem+'.svg')));$p.Export((Join-Path $OutputDir ($stem+'.png')))}
  try{$doc.ExportAsFixedFormat(1,(Join-Path $OutputDir 'evaluation_mechanisms.pdf'),1,0)}catch{'Visio fixed-format export unavailable. Use exported Visio SVG for vector PDF conversion.' | Set-Content (Join-Path $OutputDir 'pdf_export_note.txt')}
  $script:inventory | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDir 'native_shape_inventory.json') -Encoding utf8
  Write-Output "Saved native Visio: $vsdx"
} finally {if($doc){$doc.Close()};$app.Quit()}
