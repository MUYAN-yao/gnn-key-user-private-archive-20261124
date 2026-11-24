param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))

$ErrorActionPreference = 'Stop'
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$app = New-Object -ComObject Visio.Application
$app.Visible = $false
$app.AlertResponse = 7
$doc = $null
$script:inventory = [System.Collections.Generic.List[object]]::new()

$C = @{
    ink      = 'RGB(39,39,39)'
    muted    = 'RGB(101,108,116)'
    rule     = 'RGB(216,221,227)'
    pale     = 'RGB(245,247,249)'
    blue     = 'RGB(15,77,146)'
    blueFill = 'RGB(230,238,248)'
    red      = 'RGB(182,67,66)'
    redFill  = 'RGB(246,227,225)'
    white    = 'RGB(255,255,255)'
}

function Set-Cell($shape, [string]$name, [string]$formula) {
    try { $shape.CellsU($name).FormulaU = $formula } catch {}
}

function X([double]$value) { 7.5 * $value / 1200.0 }
function Y([double]$value) { $script:PageHeight - (7.5 * $value / 1200.0) }

function Track($shape, [string]$kind, [string]$text, [double]$x, [double]$y, [double]$w, [double]$h, [double]$font = 0) {
    $script:inventory.Add([pscustomobject]@{
        id = $shape.ID; kind = $kind; text = $text
        x = $x; y = $y; width = $w; height = $h; font_pt = $font
    }) | Out-Null
}

function Text-Box(
    [double]$x, [double]$y, [double]$w, [double]$h,
    [string]$text, [double]$font = 11, [bool]$bold = $false,
    [int]$align = 0, [string]$color = $C.ink, [bool]$italic = $false
) {
    $shape = $script:Page.DrawRectangle((X $x), (Y ($y + $h)), (X ($x + $w)), (Y $y))
    Set-Cell $shape 'FillPattern' '0'
    Set-Cell $shape 'LinePattern' '0'
    $shape.Text = $text
    Set-Cell $shape 'Char.Font' ([string]$script:Font)
    Set-Cell $shape 'Char.Size' "$font pt"
    $style = 0
    if ($bold) { $style += 1 }
    if ($italic) { $style += 2 }
    Set-Cell $shape 'Char.Style' ([string]$style)
    Set-Cell $shape 'Char.Color' $color
    Set-Cell $shape 'Para.HorzAlign' ([string]$align)
    Set-Cell $shape 'VerticalAlign' '1'
    foreach ($margin in 'TxtMarginLeft','TxtMarginRight','TxtMarginTop','TxtMarginBottom') {
        Set-Cell $shape $margin '0 pt'
    }
    Track $shape 'text' $text $x $y $w $h $font
    return $shape
}

function Line-Segment(
    [double]$x1, [double]$y1, [double]$x2, [double]$y2,
    [string]$color = $C.rule, [double]$weight = 0.75,
    [bool]$arrow = $false, [int]$dash = 1
) {
    $shape = $script:Page.DrawLine((X $x1), (Y $y1), (X $x2), (Y $y2))
    Set-Cell $shape 'LineColor' $color
    Set-Cell $shape 'LineWeight' "$weight pt"
    Set-Cell $shape 'LinePattern' ([string]$dash)
    if ($arrow) {
        # Use two native line segments for the arrowhead. Visio's marker-based
        # arrowheads are not preserved consistently by every SVG/PDF importer.
        $dx = $x2-$x1; $dy = $y2-$y1
        $length = [Math]::Sqrt($dx*$dx + $dy*$dy)
        if ($length -gt 0) {
            $ux = $dx/$length; $uy = $dy/$length
            $arrowLength = 12.0; $halfWidth = 5.0
            foreach ($sign in @(-1.0,1.0)) {
                $ax = $x2 - $arrowLength*$ux + $sign*$halfWidth*(-$uy)
                $ay = $y2 - $arrowLength*$uy + $sign*$halfWidth*$ux
                $head = $script:Page.DrawLine((X $ax), (Y $ay), (X $x2), (Y $y2))
                Set-Cell $head 'LineColor' $color
                Set-Cell $head 'LineWeight' "$weight pt"
                Set-Cell $head 'LinePattern' ([string]$dash)
                Track $head 'arrowhead' '' ([Math]::Min($ax,$x2)) ([Math]::Min($ay,$y2)) ([Math]::Abs($x2-$ax)) ([Math]::Abs($y2-$ay)) 0
            }
        }
    }
    Track $shape 'line' '' ([Math]::Min($x1,$x2)) ([Math]::Min($y1,$y2)) ([Math]::Abs($x2-$x1)) ([Math]::Abs($y2-$y1)) 0
    return $shape
}

function Circle(
    [double]$cx, [double]$cy, [double]$diameter,
    [string]$fill = $C.white, [string]$line = $C.ink,
    [string]$text = '', [double]$font = 10.5, [bool]$bold = $false,
    [double]$weight = 0.9
) {
    $r = $diameter / 2.0
    $shape = $script:Page.DrawOval((X ($cx-$r)), (Y ($cy+$r)), (X ($cx+$r)), (Y ($cy-$r)))
    Set-Cell $shape 'FillPattern' '1'
    Set-Cell $shape 'FillForegnd' $fill
    Set-Cell $shape 'LineColor' $line
    Set-Cell $shape 'LineWeight' "$weight pt"
    $shape.Text = $text
    Set-Cell $shape 'Char.Font' ([string]$script:Font)
    Set-Cell $shape 'Char.Size' "$font pt"
    Set-Cell $shape 'Char.Style' $(if ($bold) {'1'} else {'0'})
    Set-Cell $shape 'Char.Color' $line
    Set-Cell $shape 'Para.HorzAlign' '1'
    Set-Cell $shape 'VerticalAlign' '1'
    foreach ($margin in 'TxtMarginLeft','TxtMarginRight','TxtMarginTop','TxtMarginBottom') {
        Set-Cell $shape $margin '0 pt'
    }
    Track $shape 'circle' $text ($cx-$r) ($cy-$r) $diameter $diameter $font
    return $shape
}

function Rounded-Rect(
    [double]$x, [double]$y, [double]$w, [double]$h,
    [string]$text, [string]$fill, [string]$line,
    [double]$font = 10.5, [bool]$bold = $false
) {
    $shape = $script:Page.DrawRectangle((X $x), (Y ($y+$h)), (X ($x+$w)), (Y $y))
    Set-Cell $shape 'FillPattern' '1'
    Set-Cell $shape 'FillForegnd' $fill
    Set-Cell $shape 'LineColor' $line
    Set-Cell $shape 'LineWeight' '0.75 pt'
    Set-Cell $shape 'Rounding' '0.035 in'
    $shape.Text = $text
    Set-Cell $shape 'Char.Font' ([string]$script:Font)
    Set-Cell $shape 'Char.Size' "$font pt"
    Set-Cell $shape 'Char.Style' $(if ($bold) {'1'} else {'0'})
    Set-Cell $shape 'Char.Color' $line
    Set-Cell $shape 'Para.HorzAlign' '1'
    Set-Cell $shape 'VerticalAlign' '1'
    foreach ($margin in 'TxtMarginLeft','TxtMarginRight','TxtMarginTop','TxtMarginBottom') {
        Set-Cell $shape $margin '1 pt'
    }
    Track $shape 'rounded-rect' $text $x $y $w $h $font
    return $shape
}

function Filled-Rect(
    [double]$x, [double]$y, [double]$w, [double]$h,
    [string]$fill, [string]$line = $C.white
) {
    $shape = $script:Page.DrawRectangle((X $x), (Y ($y+$h)), (X ($x+$w)), (Y $y))
    Set-Cell $shape 'FillPattern' '1'
    Set-Cell $shape 'FillForegnd' $fill
    Set-Cell $shape 'LineColor' $line
    Set-Cell $shape 'LineWeight' '0.4 pt'
    Track $shape 'bar' '' $x $y $w $h 0
    return $shape
}

function Draw-Candidate-Glyph([double]$cx, [double]$cy, [string]$color, [string]$fill, [string]$count) {
    # A sparse native-shape graph motif: evidence-specific, compact, and fully editable.
    $nodes = @(
        @(-30,-19), @(-4,-29), @(23,-18), @(-34,10), @(-4,0), @(29,10), @(-17,29), @(17,30)
    )
    $edges = @(@(0,1),@(1,2),@(0,3),@(0,4),@(1,4),@(2,5),@(3,4),@(4,5),@(3,6),@(4,6),@(4,7),@(5,7),@(6,7))
    foreach ($edge in $edges) {
        $a = $nodes[$edge[0]]; $b = $nodes[$edge[1]]
        Line-Segment ($cx+$a[0]) ($cy+$a[1]) ($cx+$b[0]) ($cy+$b[1]) $C.rule 0.55 $false | Out-Null
    }
    for ($i=0; $i -lt $nodes.Count; $i++) {
        $n = $nodes[$i]
        $nodeFill = if ($i -in @(1,4,7)) { $fill } else { $C.white }
        Circle ($cx+$n[0]) ($cy+$n[1]) 11 $nodeFill $color '' 7 $false 0.7 | Out-Null
    }
    if ($count -ne '') {
        Text-Box ($cx-80) ($cy+47) 160 20 $count 9.8 $true 1 $color | Out-Null
    }
}

function Draw-Seed-Set([double]$startX, [double]$cy, [string[]]$ids, [string]$color, [string]$fill) {
    for ($i=0; $i -lt $ids.Count; $i++) {
        $x = $startX + 69*$i
        Rounded-Rect $x ($cy-17) 64 34 $ids[$i] $fill $color 7.8 $true | Out-Null
    }
}

try {
    $doc = $app.Documents.Add('')
    $script:Font = $doc.Fonts.Item('Arial').ID
    $script:PageHeight = 4.75
    $script:Page = $doc.Pages.Add()
    $script:Page.Name = 'Publication figure'
    Set-Cell $script:Page.PageSheet 'PageWidth' '7.5 in'
    Set-Cell $script:Page.PageSheet 'PageHeight' '4.75 in'

    # Overall structure: one hero evidence panel and two compact quantitative panels.
    Line-Segment 718 32 718 724 $C.rule 0.7 $false | Out-Null
    Line-Segment 752 366 1158 366 $C.rule 0.7 $false | Out-Null

    # Panel a: candidate eligibility and the resulting selected seeds.
    Text-Box 42 26 28 28 'a' 17 $true 0 $C.ink | Out-Null
    Text-Box 82 27 590 26 'Candidate eligibility' 14 $true 0 $C.ink | Out-Null
    Text-Box 82 57 550 18 'wiki-Vote  |  W = 1,280  |  recorded path 1101' 9.6 $false 0 $C.muted | Out-Null

    Text-Box 52 105 220 23 'Full reference' 11.5 $true 0 $C.blue | Out-Null
    Text-Box 52 133 220 18 '7,115 eligible nodes' 9.2 $false 0 $C.muted | Out-Null
    Draw-Candidate-Glyph 138 205 $C.blue $C.blueFill ''
    Line-Segment 223 205 292 205 $C.blue 1.0 $true | Out-Null
    Text-Box 208 171 102 18 'greedy' 8.3 $false 1 $C.blue | Out-Null
    Text-Box 292 144 350 20 'selected seed set' 10.2 $true 0 $C.blue | Out-Null
    Draw-Seed-Set 292 205 @('2565','766','11','457','2688') $C.blue $C.blueFill

    Line-Segment 52 286 674 286 $C.rule 0.65 $false | Out-Null

    Text-Box 52 322 220 23 'PageRank 4k' 11.5 $true 0 $C.red | Out-Null
    Text-Box 52 350 220 18 '20 eligible nodes' 9.2 $false 0 $C.muted | Out-Null
    Draw-Candidate-Glyph 138 422 $C.red $C.redFill ''
    Line-Segment 223 422 292 422 $C.red 1.0 $true | Out-Null
    Text-Box 208 388 102 18 'greedy' 8.3 $false 1 $C.red | Out-Null
    Text-Box 292 361 350 20 'selected seed set' 10.2 $true 0 $C.red | Out-Null
    Draw-Seed-Set 292 422 @('3352','2237','2328','2654','1297') $C.red $C.redFill

    # The central empirical observation is isolated typographically instead of placed in a callout box.
    Text-Box 292 489 350 30 '0 / 5 retained' 14.5 $true 1 $C.ink | Out-Null
    Text-Box 292 523 350 20 'reference seeds  |  all five paths' 9.5 $false 1 $C.muted | Out-Null
    Line-Segment 371 557 560 557 $C.rule 0.7 $false | Out-Null

    # A minimal mechanism key; the caption carries the interpretation and scope limitations.
    Text-Box 52 607 220 20 'Propagation' 10.2 $true 0 $C.ink | Out-Null
    Text-Box 52 635 164 22 'voter' 10.5 $false 1 $C.muted | Out-Null
    Line-Segment 205 646 295 646 $C.ink 0.9 $true | Out-Null
    Text-Box 302 635 164 22 'votee' 10.5 $false 1 $C.muted | Out-Null
    Text-Box 490 607 170 20 'PageRank' 10.2 $true 0 $C.ink | Out-Null
    Text-Box 490 635 170 22 'incoming score' 9.2 $false 0 $C.red | Out-Null
    Text-Box 52 682 610 36 'Restriction changes eligibility only; diffusion still uses the complete processed graph.' 9.5 $false 0 $C.muted | Out-Null

    # Panel b: candidate-pool direction profiles as direct-labelled dumbbells.
    Text-Box 752 26 28 28 'b' 17 $true 0 $C.ink | Out-Null
    Text-Box 792 27 358 26 'Candidate-pool profile' 13.5 $true 0 $C.ink | Out-Null
    Text-Box 792 58 155 18 ([char]0x25CB + '  in-degree') 10 $false 0 $C.muted | Out-Null
    Text-Box 936 58 165 18 ([char]0x25CF + '  out-degree') 10 $false 0 $C.muted | Out-Null

    $axisX0 = 878.0; $axisX1 = 1138.0; $axisW = $axisX1-$axisX0
    function Degree-X([double]$value) { $axisX0 + $axisW*$value/500.0 }
    Text-Box 754 111 118 26 'PageRank 4k' 8.8 $true 0 $C.red | Out-Null
    $prOut = Degree-X 56.2; $prIn = Degree-X 249.75
    Line-Segment $prOut 151 $prIn 151 $C.red 1.0 $false | Out-Null
    Circle $prOut 151 14 $C.red $C.red '' 7 $false 0.8 | Out-Null
    Circle $prIn 151 15 $C.white $C.red '' 7 $false 1.1 | Out-Null
    Text-Box ($prOut-32) 169 65 18 '56.2' 9.8 $false 1 $C.red | Out-Null
    Text-Box ($prIn-43) 113 86 18 '249.75' 9.8 $false 1 $C.red | Out-Null

    Text-Box 754 215 118 26 'Degree 4k' 8.8 $true 0 $C.blue | Out-Null
    $degIn = Degree-X 70.3; $degOut = Degree-X 489.25
    Line-Segment $degIn 255 $degOut 255 $C.blue 1.0 $false | Out-Null
    Circle $degIn 255 15 $C.white $C.blue '' 7 $false 1.1 | Out-Null
    Circle $degOut 255 14 $C.blue $C.blue '' 7 $false 0.8 | Out-Null
    Text-Box ($degIn-32) 273 65 18 '70.3' 9.8 $false 1 $C.blue | Out-Null
    Text-Box ($degOut-43) 217 86 18 '489.25' 9.8 $false 1 $C.blue | Out-Null

    Line-Segment $axisX0 319 $axisX1 319 $C.muted 0.65 $false | Out-Null
    foreach ($tick in @(0,250,500)) {
        $tx = Degree-X $tick
        Line-Segment $tx 315 $tx 324 $C.muted 0.65 $false | Out-Null
        Text-Box ($tx-35) 327 70 18 ([string]$tick) 7.5 $false 1 $C.muted | Out-Null
    }
    Text-Box 928 345 212 17 'mean degree in pool' 8.0 $false 2 $C.muted | Out-Null

    # Panel c: independently evaluated incremental spread.
    Text-Box 752 391 28 28 'c' 17 $true 0 $C.ink | Out-Null
    Text-Box 792 392 358 26 'Independent spread' 13.5 $true 0 $C.ink | Out-Null
    $plotLeft = 813.0; $plotRight = 1134.0; $plotTop = 477.0; $plotBottom = 661.0; $plotH = $plotBottom-$plotTop
    Line-Segment $plotLeft $plotTop $plotLeft $plotBottom $C.muted 0.65 $false | Out-Null
    Line-Segment $plotLeft $plotBottom $plotRight $plotBottom $C.muted 0.65 $false | Out-Null
    foreach ($tick in @(0,30,60)) {
        $ty = $plotBottom - $plotH*$tick/60.0
        Line-Segment ($plotLeft-5) $ty $plotLeft $ty $C.muted 0.65 $false | Out-Null
        Text-Box 754 ($ty-9) 50 18 ([string]$tick) 8.5 $false 2 $C.muted | Out-Null
    }
    $fullValue = 55.73602; $prValue = 15.04268
    $fullTop = $plotBottom - $plotH*$fullValue/60.0
    $prTop = $plotBottom - $plotH*$prValue/60.0
    Filled-Rect 862 $fullTop 72 ($plotBottom-$fullTop) $C.blue $C.blue | Out-Null
    Filled-Rect 1012 $prTop 72 ($plotBottom-$prTop) $C.red $C.red | Out-Null
    Text-Box 841 ($fullTop-31) 114 24 '55.736' 12.2 $true 1 $C.blue | Out-Null
    Text-Box 991 ($prTop-31) 114 24 '15.043' 12.2 $true 1 $C.red | Out-Null
    Text-Box 826 672 144 22 'Full reference' 9.2 $false 1 $C.blue | Out-Null
    Text-Box 976 672 144 22 'PageRank-4k' 9.2 $false 1 $C.red | Out-Null
    Text-Box 835 428 300 23 ([char]0x0394 + ' -40.693  |  73.01% loss') 9.0 $true 1 $C.ink | Out-Null
    Text-Box 835 713 305 20 '5 paths  |  10,000 worlds/path' 8.2 $false 2 $C.muted | Out-Null

    if ($doc.Pages.Count -gt 1) { $doc.Pages.Item(1).Delete(1) }

    $base = 'wiki_vote_publication_figure_v1'
    $vsdx = Join-Path $OutputDir ($base + '.vsdx')
    $svg = Join-Path $OutputDir ($base + '.svg')
    $png = Join-Path $OutputDir ($base + '.png')
    $inventory = Join-Path $OutputDir ('native_shape_inventory_publication_v1.json')
    $doc.SaveAs($vsdx)
    $script:Page.Export($svg)
    $script:Page.Export($png)
    $script:inventory | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $inventory -Encoding utf8
    Write-Output "Saved: $vsdx"
    Write-Output "Saved: $svg"
    Write-Output "Saved: $png"
    Write-Output "Native shapes: $($script:Page.Shapes.Count)"
}
finally {
    if ($doc) { try { $doc.Close() } catch {} }
    if ($app) { try { $app.Quit() } catch {} }
}
