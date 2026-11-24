param([string]$OutputDir)
$ErrorActionPreference='Stop'
if (-not $OutputDir) { $OutputDir=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1\figures' }
$OutputDir=[IO.Path]::GetFullPath($OutputDir)
$base=Join-Path $OutputDir 'Fig1-mechanism-editable'
$script:pw=12.0; $script:ph=7.5
function VX([double]$x) { $x/100 }
function VY([double]$y) { $script:ph-$y/100 }
function Cell($s,$n,$v) {$s.CellsU($n).FormulaU=[string]$v}
$ink='RGB(38,52,65)'; $gray='RGB(174,184,192)'; $blue='RGB(43,111,158)'; $orange='RGB(209,124,65)'; $green='RGB(69,137,119)'; $white='RGB(255,255,255)'
function Style($s,$fill,$line,$weight=1) {
    Cell $s 'FillPattern' $(if($fill -eq 'none'){'0'}else{'1'})
    if($fill -ne 'none'){Cell $s 'FillForegnd' $fill}
    Cell $s 'LinePattern' $(if($line -eq 'none'){'0'}else{'1'})
    if($line -ne 'none'){Cell $s 'LineColor' $line}
    Cell $s 'LineWeight' "$weight pt"
}
function Rect($x,$y,$w,$h,$fill='none',$line='none') {
    $s=$script:page.DrawRectangle((VX $x),(VY ($y+$h)),(VX ($x+$w)),(VY $y))
    Style $s $fill $line; return $s
}
function Txt($x,$y,$w,$h,$text,$size=14,$bold=0,$color=$ink) {
    $s=Rect $x $y $w $h
    $s.Text=$text; Cell $s 'Char.Font' $script:fontId
    Cell $s 'Char.Size' "$size pt"; Cell $s 'Char.Style' $bold; Cell $s 'Char.Color' $color
    Cell $s 'Para.HorzAlign' '1'; Cell $s 'VerticalAlign' '1'
    foreach($m in @('LeftMargin','RightMargin','TopMargin','BottomMargin')){Cell $s $m '0 in'}
    return $s
}
function Line($x,$y,$xx,$yy,$color=$gray,$arrow=0,$dash=1) {
    $s=$script:page.DrawLine((VX $x),(VY $y),(VX $xx),(VY $yy))
    Cell $s 'LineColor' $color; Cell $s 'LineWeight' '1.1 pt'; Cell $s 'LinePattern' $dash
    if($arrow){Cell $s 'EndArrow' '4'}
    return $s
}
function Dot($x,$y,$r,$fill=$blue,$text='') {
    $s=$script:page.DrawOval((VX ($x-$r)),(VY ($y+$r)),(VX ($x+$r)),(VY ($y-$r)))
    Style $s $fill $white 1
    if($text){$s.Text=$text;Cell $s 'Char.Font' $script:fontId;Cell $s 'Char.Size' '11 pt';Cell $s 'Char.Color' $white}
    return $s
}
$coords=@(@(0.12,0.38),@(0.32,0.13),@(0.38,0.51),@(0.18,0.82),@(0.63,0.27),@(0.71,0.64),@(0.92,0.42),@(0.86,0.88))
$edges=@(@(0,1),@(0,2),@(0,3),@(1,2),@(1,4),@(2,3),@(2,4),@(2,5),@(4,5),@(4,6),@(5,6),@(5,7),@(6,7))
function Graph($x,$y,$w,$h,$mode='all',$radius=8) {
    foreach($e in $edges){$a=$coords[$e[0]];$b=$coords[$e[1]];Line ($x+$w*$a[0]) ($y+$h*$a[1]) ($x+$w*$b[0]) ($y+$h*$b[1]) | Out-Null}
    for($i=0;$i -lt $coords.Count;$i++){
        $fill=$blue
        if($mode -eq 'pool' -and $i -notin @(2,4,5)){ $fill='RGB(223,228,232)' }
        if($mode -eq 'seed'){$fill=if($i -in @(2,5)){$orange}else{$gray}}
        Dot ($x+$w*$coords[$i][0]) ($y+$h*$coords[$i][1]) $radius $fill | Out-Null
    }
}
function Head($letter,$title,$x,$y,$w) {
    Txt $x $y 28 26 $letter 20 1 | Out-Null
    Txt ($x+34) $y ($w-34) 26 $title 17 1 | Out-Null
}
function GroupSince($start,$name) {
    $sel=$script:page.CreateSelection(0)
    $new=@();for($i=$start+1;$i -le $script:page.Shapes.Count;$i++){$new+=$script:page.Shapes.Item($i)}
    foreach($s in $new){$sel.Select($s,2)}
    $g=$sel.Group();$g.NameU=$name
}
$visio=$null;$doc=$null
try {
    $visio=New-Object -ComObject Visio.InvisibleApp
    $doc=$visio.Documents.Add('')
    $script:page=$doc.Pages.Item(1)
    $script:fontId=$doc.Fonts.Item('Arial').ID
    Cell $page.PageSheet 'PageWidth' '12 in';Cell $page.PageSheet 'PageHeight' '7.5 in'
    $page.Name='Resolution-aware evaluation'
    # Four calibrated panels, no large text boxes. Every motif is native.
    $n=$page.Shapes.Count
    Head 'a' 'Contact-derived topology' 22 20 520
    Graph 40 75 200 165 'all' 10
    # Contact observations as an editable raster of events, then a time split.
    for($row=0;$row -lt 4;$row++){
        Line 300 (92+$row*29) 525 (92+$row*29) 'RGB(222,227,231)' | Out-Null
        foreach($col in @(0,2,3,6,8)){
            $shift=($col+$row)%9
            Rect (308+$shift*24) (85+$row*29) 13 14 $(if($shift -lt 6){$blue}else{$gray}) | Out-Null
        }
    }
    Line 447 68 447 210 $orange 0 2 | Out-Null
    Txt 290 215 160 27 'Historical contacts' 13 0 $blue | Out-Null
    Txt 442 215 96 27 'Unused' 13 0 | Out-Null
    Line 310 262 520 262 $ink 1 | Out-Null
    Txt 305 265 210 24 'Time' 13 | Out-Null
    Txt 40 260 220 32 'Aggregate repeated contacts' 13 | Out-Null
    GroupSince $n 'A_ContactTopology'
    $n=$page.Shapes.Count
    Head 'b' 'Candidate restriction' 632 20 540
    Graph 647 80 205 157 'all' 10
    Graph 937 80 205 157 'pool' 10
    Line 864 147 925 147 $ink 1 | Out-Null
    Txt 840 173 100 30 'Rank' 13 | Out-Null
    Txt 655 258 195 29 'All nodes: V' 14 | Out-Null
    Txt 928 258 225 29 'Fixed pool: C' 14 | Out-Null
    Txt 665 299 470 29 'Same graph; fewer eligible seed candidates' 13 | Out-Null
    GroupSince $n 'B_CandidateRestriction'
    # Light separators keep the reading order without container boxes.
    Line 602 32 602 691 'RGB(220,225,229)' 0 2 | Out-Null
    Line 25 351 1175 351 'RGB(220,225,229)' 0 2 | Out-Null
    $n=$page.Shapes.Count
    Head 'c' 'Selection-world refinement' 22 376 535
    # Nested collections represented as contiguous world tiles.
    for($j=0;$j -lt 3;$j++){
        $count=@(2,8,16)[$j]
        Txt 23 (433+$j*60) 67 28 @('20','80','320')[$j] 14 1 | Out-Null
        for($i=0;$i -lt $count;$i++){
            $fill=if($i -lt 2){$blue}elseif($i -lt 8){'RGB(137,176,201)'}else{'RGB(207,225,237)'}
            Rect (96+$i*21) (437+$j*60) 17 24 $fill 'none' | Out-Null
        }
    }
    Txt 92 615 347 30 'Retain earlier worlds; append new worlds' 13 | Out-Null
    Txt 72 651 390 28 'Re-optimize full and restricted searches' 13 1 | Out-Null
    GroupSince $n 'C_NestedWorlds'
    $n=$page.Shapes.Count
    Head 'd' 'Separate decision and utility' 632 376 540
    # Ordered-seed tokens are symbolic, not experimental observations.
    Txt 637 429 92 28 'Full' 13 | Out-Null
    Txt 637 478 92 28 'Pool' 13 | Out-Null
    for($i=0;$i -lt 4;$i++){
        Dot (750+$i*37) 443 13 $blue @('a','b','c','d')[$i] | Out-Null
        Dot (750+$i*37) 492 13 $(if($i -eq 2){$orange}else{$blue}) @('a','b','e','d')[$i] | Out-Null
    }
    Txt 716 522 198 24 'Compare seed traces' 13 | Out-Null
    Line 907 466 964 466 $ink 1 | Out-Null
    # Distinct evaluation-world stack containing a small propagation graph.
    Rect 983 438 153 90 'RGB(237,246,241)' $green | Out-Null
    Rect 977 431 153 90 'RGB(244,249,246)' $green | Out-Null
    Rect 971 424 153 90 $white $green | Out-Null
    Graph 986 430 118 69 'seed' 5
    Txt 947 534 205 24 '2,000 unused worlds' 13 0 $green | Out-Null
    # A scale and stopwatch denote utility and measured computation.
    Line 717 607 906 607 $ink 0 | Out-Null
    for($i=0;$i -lt 7;$i++){Line (724+$i*28) 601 (724+$i*28) 613 $ink | Out-Null}
    Dot 817 607 8 $orange | Out-Null
    Txt 698 633 225 27 'Held-out spread difference' 13 | Out-Null
    $clock=$page.DrawOval((VX 1007),(VY 626),(VX 1061),(VY 572));Style $clock 'none' $ink 1.3
    Line 1034 580 1034 599 $ink | Out-Null;Line 1034 599 1048 609 $ink | Out-Null
    Rect 1026 563 16 6 $ink 'none' | Out-Null
    Txt 957 633 170 27 'Measured time' 13 | Out-Null
    GroupSince $n 'D_IndependentEvaluation'
    Txt 20 711 1160 22 'Schematic node labels and world tiles illustrate the protocol; they are not measured results.' 12 0 'RGB(100,110,118)' | Out-Null
    if(Test-Path -LiteralPath "$base.vsdx"){
        Copy-Item -LiteralPath "$base.vsdx" -Destination "$base.previous.vsdx" -Force
    }
    $doc.SaveAs("$base.vsdx")
    $visio.Settings.SetRasterExportResolution(2,300,300,0)
    $page.Export("$base.png");$page.Export("$base.svg")
    $doc.ExportAsFixedFormat(1,"$base.pdf",1,0)
    Write-Output "Saved native Visio diagram and PNG/SVG/PDF exports."
} finally {
    if($doc){$doc.Close()}
    if($visio){$visio.Quit()}
}
