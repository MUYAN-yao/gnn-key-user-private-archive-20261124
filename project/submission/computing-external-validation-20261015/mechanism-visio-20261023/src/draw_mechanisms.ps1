param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))
$ErrorActionPreference='Stop'
$OutputDir=[IO.Path]::GetFullPath($OutputDir)
$app=New-Object -ComObject Visio.Application
$app.Visible=$false
$app.AlertResponse=7
$doc=$null
$script:inventory=[System.Collections.Generic.List[object]]::new()
$C=@{ink='RGB(32,43,58)';gray='RGB(110,121,134)';border='RGB(213,220,228)';white='RGB(255,255,255)';bg='RGB(248,250,252)';teal='RGB(18,119,121)';paleTeal='RGB(233,246,244)';blue='RGB(50,94,155)';paleBlue='RGB(236,242,251)';orange='RGB(183,103,38)';paleOrange='RGB(252,242,230)'}
function Cell($s,$n,$v){try{$s.CellsU($n).FormulaU=[string]$v}catch{throw "Visio cell '$n' formula '$v': $($_.Exception.Message)"}}
function X($v){return 6.0*$v/1000}
function Y($v){return $script:height-(6.0*$v/1000)}
function Shape($x,$y,$w,$h,$label='',$fill=$C.white,$stroke=$C.border,$font=11,$bold=$false,$align=1){
 $s=$script:page.DrawRectangle((X $x),(Y ($y+$h)),(X ($x+$w)),(Y $y))
 if($fill -ne 'none'){Cell $s 'FillForegnd' $fill}; if($stroke -ne 'none'){Cell $s 'LineColor' $stroke}; Cell $s 'LineWeight' '0.7 pt';Cell $s 'Rounding' '0.035 in'
 if($stroke -eq 'none'){Cell $s 'LinePattern' '0'}
 if($fill -eq 'none'){Cell $s 'FillPattern' '0'}
 $s.Text=$label;Cell $s 'Char.Font' $script:fontID;Cell $s 'Char.Size' "$font pt";Cell $s 'Char.Color' $C.ink
 Cell $s 'Char.Style' $(if($bold){1}else{0}); Cell $s 'Para.HorzAlign' $align; Cell $s 'VerticalAlign' 1
 foreach($n in @('LeftMargin','RightMargin','TopMargin','BottomMargin')){Cell $s $n '2 pt'}
 $script:inventory.Add([pscustomobject]@{page=$script:page.Name;id=$s.ID;text=$label;x=$x;y=$y;w=$w;h=$h;font_pt=$font})
 return $s
}
function Text($x,$y,$w,$h,$t,$font=11,$bold=$false,$align=0){return Shape $x $y $w $h $t 'none' 'none' $font $bold $align}
function Line($x1,$y1,$x2,$y2,$col=$C.gray,$arrow=$true,$dash=$false){
 $s=$script:page.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));Cell $s 'LineColor' $col;Cell $s 'LineWeight' '0.9 pt'
 if($arrow){
  $dx=$x2-$x1;$dy=$y2-$y1;$len=[Math]::Sqrt($dx*$dx+$dy*$dy)
  if($len -gt 0){
   $ux=$dx/$len;$uy=$dy/$len
   foreach($side in @(-1,1)){
    $ax=$x2-10*$ux+$side*4.5*(-$uy);$ay=$y2-10*$uy+$side*4.5*$ux
    $wing=$script:page.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));Cell $wing 'LineColor' $col;Cell $wing 'LineWeight' '0.9 pt'
   }
  }
 };if($dash){Cell $s 'LinePattern' 2};return $s
}
function Node($cx,$cy,$label,$fill=$C.white){
 $s=$script:page.DrawOval((X ($cx-19)),(Y ($cy+19)),(X ($cx+19)),(Y ($cy-19)))
 Cell $s 'FillForegnd' $fill;Cell $s 'LineColor' $C.teal;Cell $s 'LineWeight' '1 pt'
 $s.Text=$label;Cell $s 'Char.Font' $script:fontID;Cell $s 'Char.Size' '11 pt';Cell $s 'Char.Color' $C.ink;return $s
}
function Panel($y,$h,$letter,$title){
 Shape 12 $y 976 $h '' $C.white $C.border | Out-Null
 Text 28 ($y+10) 35 35 $letter 14 $true | Out-Null
 Text 68 ($y+9) 890 37 $title 12 $true | Out-Null
}
function NewPage($name,$units){
 $script:page=$doc.Pages.Add();$script:page.Name=$name;$script:height=6*$units/1000
 Cell $script:page.PageSheet 'PageWidth' '6 in';Cell $script:page.PageSheet 'PageHeight' "$script:height in"
}
try{
 $doc=$app.Documents.Add('');$script:fontID=$doc.Fonts.Item('Arial').ID
 NewPage 'Evaluation mechanism' 1130
 Panel 12 465 'a' 'Two resolutions enter the same evaluation chain'
 Text 32 92 170 70 "Observed`ngraph G" 11 $true | Out-Null
 Line 70 220 135 180 $C.gray | Out-Null; Line 135 180 130 270 $C.gray | Out-Null;Line 70 220 130 270 $C.gray | Out-Null
 Node 70 220 'u' | Out-Null;Node 135 180 'v' | Out-Null;Node 130 270 'w' | Out-Null
 Text 27 305 178 78 "Fixed graph`np, h, node IDs" 10.5 | Out-Null
 Shape 230 138 205 82 "Full eligibility`nC = V" $C.bg $C.gray 11 $true | Out-Null
 Shape 230 291 205 82 "Rank + truncate`nPool C" $C.paleOrange $C.orange 11 $true | Out-Null
 Text 227 379 215 44 'tau, m, coverage' 10.5 | Out-Null
 Line 174 220 205 220 $C.gray $false | Out-Null;Line 205 179 205 332 $C.gray $false | Out-Null
 Line 205 179 230 179 | Out-Null;Line 205 332 230 332 | Out-Null
 Shape 488 138 191 82 "Full greedy`nSeeds S_V" $C.paleBlue $C.blue 11 $true | Out-Null
 Shape 488 291 191 82 "Pool greedy`nSeeds S_C" $C.paleTeal $C.teal 11 $true | Out-Null
 Line 435 179 488 179 $C.blue | Out-Null; Line 435 332 488 332 $C.teal | Out-Null
 Shape 471 64 226 59 "Nested worlds`nW: 80 / 320 / 1280" $C.paleBlue $C.blue 10.5 | Out-Null
 Line 584 113 584 138 $C.blue $true $true | Out-Null
 Line 697 91 715 91 $C.blue $false $true | Out-Null;Line 715 91 715 402 $C.blue $false $true | Out-Null
 Line 715 402 584 402 $C.blue $false $true | Out-Null;Line 584 402 584 373 $C.blue $true $true | Out-Null
 Line 679 179 738 238 $C.blue | Out-Null;Line 679 332 738 280 $C.teal | Out-Null
 Shape 738 210 220 101 "Paired spread`nM = 10,000" $C.bg $C.gray 11 $true | Out-Null
 Text 741 322 216 70 "Disjoint worlds eta`nShared across arms" 10.5 | Out-Null
 Text 33 424 916 47 'Only seed eligibility changes. Propagation uses the full processed graph.' 10.5 | Out-Null

 Panel 496 331 'b' 'Small ranking changes can cross the eligibility boundary'
 Text 35 546 902 35 'ca-GrQc: PageRank-4k, m = 20 (observed control)' 11 $true | Out-Null
 Text 35 590 120 50 'Default' 10.5 | Out-Null; Text 35 657 120 50 'Strict' 10.5 | Out-Null
 Shape 159 590 176 50 '18 shared' $C.bg $C.border 10.5 | Out-Null
 Shape 344 590 90 50 '1488' $C.paleOrange $C.orange 10.5 | Out-Null;Shape 442 590 90 50 '19865' $C.paleOrange $C.orange 10.5 | Out-Null
 Shape 159 657 176 50 '18 shared' $C.bg $C.border 10.5 | Out-Null
 Shape 344 657 90 50 '17655' $C.paleTeal $C.teal 10.5 | Out-Null;Shape 442 657 90 50 '6610' $C.paleTeal $C.teal 10.5 | Out-Null
 Text 35 722 500 68 "tau: 10^-6 vs 10^-12`nStrict pool unchanged at 10^-14" 10.5 | Out-Null
 Line 544 637 592 637 $C.gray | Out-Null
 Shape 601 587 352 124 "W = 1280: 5/5 sets change`nDelta vs full`n-0.25082 -> +0.02608" $C.paleBlue $C.blue 10.5 $true | Out-Null
 Text 601 724 352 86 "Post-hoc paired control`nPoint estimates only" 10.5 | Out-Null

 Panel 845 273 'c' 'Report three outcomes separately'
 Shape 36 906 285 124 "Agreement`nTrajectory / final set`nJaccard / divergence" $C.paleBlue $C.blue 10.5 $true | Out-Null
 Shape 358 906 285 124 "Utility`nTotal / extra spread`nPaired Delta / MC SE" $C.paleTeal $C.teal 10.5 $true | Out-Null
 Shape 680 906 285 124 "Cost`nSelection time`nSetup / verification" $C.paleOrange $C.orange 10.5 $true | Out-Null
 Text 35 1040 930 62 'Agreement alone does not quantify utility preservation or savings.' 10.5 | Out-Null

 NewPage 'Coupling mechanism' 660
 Panel 10 640 'a' 'Why step-indexed worlds can change realized reach'
 Text 38 60 922 43 'Illustrative chain s -> u -> v; h = 2. The same step-indexed world is used in both rows.' 11 | Out-Null
 Shape 38 112 923 71 "Open / closed draws: s -> u at t = 0 is open; u -> v at t = 0 is closed; u -> v at t = 1 is open." $C.bg $C.border 11 | Out-Null
 Text 40 201 190 37 'Initial seeds' 11 $true | Out-Null;Text 277 201 220 37 't = 0' 11 $true | Out-Null;Text 546 201 220 37 't = 1' 11 $true | Out-Null;Text 817 201 130 37 'Reach' 11 $true | Out-Null
 Shape 40 264 169 68 'S = {s}' $C.paleTeal $C.teal 11 $true | Out-Null
 Node 304 297 's' $C.paleTeal | Out-Null;Line 325 297 419 297 $C.teal | Out-Null;Node 440 297 'u' | Out-Null
 Node 573 297 'u' $C.paleTeal | Out-Null;Line 594 297 689 297 $C.teal | Out-Null;Node 710 297 'v' | Out-Null
 Shape 819 264 125 68 '3 nodes' $C.paleTeal $C.teal 11 $true | Out-Null
 Shape 40 386 169 68 "S' = {s, u}" $C.paleOrange $C.orange 11 $true | Out-Null
 Node 304 420 'u' $C.paleOrange | Out-Null;Line 325 420 419 420 $C.orange $false | Out-Null;Line 363 410 383 430 $C.orange $false | Out-Null;Line 363 430 383 410 $C.orange $false | Out-Null;Node 440 420 'v' | Out-Null
 Text 538 385 223 74 "u has already acted;`nno retry at t = 1" 11 | Out-Null
 Shape 819 386 125 68 '2 nodes' $C.paleOrange $C.orange 11 $true | Out-Null
 Text 39 477 911 65 'Adding u as an initial seed advances its attempt from t = 1 to t = 0. A larger seed set can therefore have smaller reach in a realized step-indexed world.' 11 | Out-Null
 Shape 40 554 914 80 "Fixed-edge control uses one draw per edge/world.`nThe example alone does not disprove submodularity." $C.paleBlue $C.blue 11 | Out-Null
 # Remove the empty default page; both scientific pages consist solely of native shapes.
 if($doc.Pages.Count -gt 2){$doc.Pages.Item(1).Delete(1)}
 $vsdx=Join-Path $OutputDir 'evaluation_mechanisms.vsdx'
 $doc.SaveAs($vsdx)
 for($i=1;$i -le $doc.Pages.Count;$i++){
  $p=$doc.Pages.Item($i);$stem=if($i -eq 1){'mechanism_overview'}else{'coupling_counterexample'}
  $p.Export((Join-Path $OutputDir ($stem+'.svg')))
  $p.Export((Join-Path $OutputDir ($stem+'.png')))
 }
 try{$doc.ExportAsFixedFormat(1,(Join-Path $OutputDir 'evaluation_mechanisms.pdf'),1,0)}catch{
  'Visio fixed-format export unavailable. Use exported Visio SVG for vector PDF conversion.' | Set-Content (Join-Path $OutputDir 'pdf_export_note.txt')
 }
 $script:inventory | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDir 'native_shape_inventory.json') -Encoding utf8
 Write-Output "Saved native Visio: $vsdx"
} finally {
 if($doc){$doc.Close()};$app.Quit()
}
