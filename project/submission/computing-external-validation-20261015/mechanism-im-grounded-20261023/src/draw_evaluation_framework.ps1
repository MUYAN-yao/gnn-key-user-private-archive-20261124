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
    ink='RGB(35,38,42)'; muted='RGB(102,108,116)'; rule='RGB(196,202,209)'
    pale='RGB(247,248,250)'; white='RGB(255,255,255)'
    blue='RGB(28,91,153)'; blueFill='RGB(229,238,248)'
    red='RGB(184,69,68)'; redFill='RGB(248,231,229)'
    gold='RGB(177,121,34)'; goldFill='RGB(250,242,222)'
}

function Set-Cell($shape,[string]$name,[string]$formula){try{$shape.CellsU($name).FormulaU=$formula}catch{}}
function X([double]$v){7.5*$v/1200.0}
function Y([double]$v){$script:PageHeight-(7.5*$v/1200.0)}
function Track($shape,[string]$kind,[string]$text,[double]$x,[double]$y,[double]$w,[double]$h,[double]$font=0){
    $script:inventory.Add([pscustomobject]@{id=$shape.ID;kind=$kind;text=$text;x=$x;y=$y;width=$w;height=$h;font_pt=$font})|Out-Null
}

function Text-Box([double]$x,[double]$y,[double]$w,[double]$h,[string]$text,[double]$font=11,[bool]$bold=$false,[int]$align=0,[string]$color=$C.ink,[bool]$italic=$false){
    $s=$script:Page.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));Set-Cell $s 'FillPattern' '0';Set-Cell $s 'LinePattern' '0';$s.Text=$text
    Set-Cell $s 'Char.Font' ([string]$script:Font);Set-Cell $s 'Char.Size' "$font pt";$style=0;if($bold){$style+=1};if($italic){$style+=2};Set-Cell $s 'Char.Style' ([string]$style);Set-Cell $s 'Char.Color' $color
    Set-Cell $s 'Para.HorzAlign' ([string]$align);Set-Cell $s 'VerticalAlign' '1';foreach($m in 'TxtMarginLeft','TxtMarginRight','TxtMarginTop','TxtMarginBottom'){Set-Cell $s $m '0 pt'}
    Track $s 'text' $text $x $y $w $h $font;return $s
}

function Rect-Box([double]$x,[double]$y,[double]$w,[double]$h,[string]$text='',[string]$fill=$C.white,[string]$line=$C.rule,[double]$font=10,[bool]$bold=$false,[int]$dash=1,[double]$weight=0.75,[double]$round=0.025){
    $s=$script:Page.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));Set-Cell $s 'FillPattern' '1';Set-Cell $s 'FillForegnd' $fill;Set-Cell $s 'LineColor' $line;Set-Cell $s 'LineWeight' "$weight pt";Set-Cell $s 'LinePattern' ([string]$dash);if($round -gt 0){Set-Cell $s 'Rounding' "$round in"}
    if($text -ne ''){$s.Text=$text;Set-Cell $s 'Char.Font' ([string]$script:Font);Set-Cell $s 'Char.Size' "$font pt";Set-Cell $s 'Char.Style' $(if($bold){'1'}else{'0'});Set-Cell $s 'Char.Color' $line;Set-Cell $s 'Para.HorzAlign' '1';Set-Cell $s 'VerticalAlign' '1';foreach($m in 'TxtMarginLeft','TxtMarginRight','TxtMarginTop','TxtMarginBottom'){Set-Cell $s $m '1 pt'}}
    Track $s 'rect' $text $x $y $w $h $font;return $s
}

function Line-Segment([double]$x1,[double]$y1,[double]$x2,[double]$y2,[string]$color=$C.ink,[double]$weight=0.8,[bool]$arrow=$false,[int]$dash=1){
    $s=$script:Page.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));Set-Cell $s 'LineColor' $color;Set-Cell $s 'LineWeight' "$weight pt";Set-Cell $s 'LinePattern' ([string]$dash);Track $s 'line' '' ([Math]::Min($x1,$x2)) ([Math]::Min($y1,$y2)) ([Math]::Abs($x2-$x1)) ([Math]::Abs($y2-$y1)) 0
    if($arrow){$dx=$x2-$x1;$dy=$y2-$y1;$len=[Math]::Sqrt($dx*$dx+$dy*$dy);if($len -gt 0){$ux=$dx/$len;$uy=$dy/$len;foreach($sign in @(-1.0,1.0)){$ax=$x2-11*$ux+$sign*4.5*(-$uy);$ay=$y2-11*$uy+$sign*4.5*$ux;$h=$script:Page.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));Set-Cell $h 'LineColor' $color;Set-Cell $h 'LineWeight' "$weight pt";Track $h 'arrowhead' '' ([Math]::Min($ax,$x2)) ([Math]::Min($ay,$y2)) ([Math]::Abs($x2-$ax)) ([Math]::Abs($y2-$ay)) 0}}
    };return $s
}

function Node([double]$cx,[double]$cy,[double]$d=12,[string]$fill=$C.white,[string]$line=$C.ink,[string]$text='',[double]$font=7.5,[bool]$bold=$false){
    $r=$d/2;$s=$script:Page.DrawOval((X($cx-$r)),(Y($cy+$r)),(X($cx+$r)),(Y($cy-$r)));Set-Cell $s 'FillPattern' '1';Set-Cell $s 'FillForegnd' $fill;Set-Cell $s 'LineColor' $line;Set-Cell $s 'LineWeight' '0.7 pt';$s.Text=$text;Set-Cell $s 'Char.Font' ([string]$script:Font);Set-Cell $s 'Char.Size' "$font pt";Set-Cell $s 'Char.Style' $(if($bold){'1'}else{'0'});Set-Cell $s 'Char.Color' $line;Set-Cell $s 'Para.HorzAlign' '1';Set-Cell $s 'VerticalAlign' '1';Track $s 'node' $text ($cx-$r) ($cy-$r) $d $d $font;return $s
}

function Draw-Graph([double]$cx,[double]$cy,[double]$scale=1.0,[int[]]$blueSeeds=@(),[int[]]$redSeeds=@(),[int[]]$masked=@()){
    $pts=@(@(-36,-24),@(-8,-34),@(24,-27),@(39,-2),@(23,27),@(-8,35),@(-38,19),@(-9,0),@(17,2))
    $edges=@(@(0,1),@(1,2),@(2,3),@(3,4),@(4,5),@(5,6),@(6,0),@(0,7),@(1,7),@(2,8),@(3,8),@(4,8),@(5,7),@(6,7),@(7,8),@(1,8))
    foreach($e in $edges){$a=$pts[$e[0]];$b=$pts[$e[1]];Line-Segment ($cx+$scale*$a[0]) ($cy+$scale*$a[1]) ($cx+$scale*$b[0]) ($cy+$scale*$b[1]) $C.rule 0.5 $false|Out-Null}
    for($i=0;$i -lt $pts.Count;$i++){$p=$pts[$i];$fill=$C.white;$line=$C.ink;if($masked -contains $i){$fill=$C.redFill;$line=$C.red};if($blueSeeds -contains $i){$fill=$C.blue;$line=$C.blue};if($redSeeds -contains $i){$fill=$C.red;$line=$C.red};Node ($cx+$scale*$p[0]) ($cy+$scale*$p[1]) (11*$scale) $fill $line '' 6 $false|Out-Null}
}

function Draw-WorldStack([double]$x,[double]$y,[string]$label,[string]$color=$C.blue){
    foreach($offset in @(12,6,0)){Rect-Box ($x+$offset) ($y-$offset) 40 58 '' $C.white $color 8 $false 1 0.65 0|Out-Null;for($i=0;$i -lt 5;$i++){Line-Segment ($x+$offset+7) ($y-$offset+10+9*$i) ($x+$offset+32) ($y-$offset+10+9*$i) $C.rule 0.45 $false|Out-Null}}
    if($label -ne ''){Text-Box ($x-8) ($y+61) 72 20 $label 10.2 $true 1 $color|Out-Null}
}

function Draw-Ranking([double]$x,[double]$y){
    Text-Box $x $y 72 18 ('r' + [char]0x03C4 + '(v)') 8.0 $true 1 $C.ink|Out-Null
    Text-Box ($x+92) $y 44 18 'mask' 7.2 $true 1 $C.ink|Out-Null
    $nodes=@('v(1)','v(2)','v(3)','...','v(n)')
    $rowOffsets=@(22,44,66,103,125)
    for($i=0;$i -lt $nodes.Count;$i++){
        $rowY=$y+$rowOffsets[$i]
        $fill=if($i -lt 3){$C.redFill}else{$C.pale}
        $line=if($i -lt 3){$C.red}else{$C.rule}
        Rect-Box $x $rowY 70 18 $nodes[$i] $fill $line 7.6 ($i -lt 3) 1 0.55 0.015|Out-Null
        Rect-Box ($x+102) $rowY 22 18 $(if($i -lt 3){'1'}else{'0'}) $fill $line 7.6 $true 1 0.55 0.01|Out-Null
    }
    Line-Segment ($x-4) ($y+92) ($x+128) ($y+92) $C.red 0.75 $false 2|Out-Null
    Text-Box ($x-22) ($y+83) 18 18 'q' 8.0 $true 1 $C.red|Out-Null
    Text-Box ($x-7) ($y+151) 165 19 'candidate set  C' 8.0 $true 1 $C.red|Out-Null
}

function Draw-Iteration([double]$x,[double]$y,[string]$label,[string]$color,[bool]$last=$false){
    Rect-Box $x $y 130 118 '' $C.white $C.ink 8 $false 2 0.75 0.04|Out-Null
    Text-Box ($x+8) ($y+6) 114 19 $label 9.8 $true 1 $C.ink|Out-Null
    if($color -eq $C.blue){$seed=if($last){@(1,4,7)}else{@(1)}}else{$seed=if($last){@(0,3,6)}else{@(0)}}
    if($color -eq $C.blue){Draw-Graph ($x+65) ($y+70) 0.68 $seed @() @()}else{Draw-Graph ($x+65) ($y+70) 0.68 @() $seed @(0,3,6)}
}

try{
    $doc=$app.Documents.Add('');$script:Font=$doc.Fonts.Item('Arial').ID;$script:PageHeight=3.0;$script:Page=$doc.Pages.Add();$script:Page.Name='Evaluation mechanism';Set-Cell $script:Page.PageSheet 'PageWidth' '7.5 in';Set-Cell $script:Page.PageSheet 'PageHeight' '3.0 in'

    # Input topology: one graph is reused throughout selection and evaluation.
    Text-Box 24 22 150 22 'Observed topology' 11.5 $true 1 $C.ink|Out-Null
    Draw-Graph 99 113 0.92 @() @() @()
    Text-Box 34 159 130 30 'G = (V, E)' 10.0 $true 1 $C.ink|Out-Null
    Text-Box 29 198 142 38 'fixed propagation graph' 9.4 $false 1 $C.muted|Out-Null

    # Two resolutions that are varied independently.
    Rect-Box 193 18 205 365 '' $C.white $C.rule 8 $false 1 0.7 0.03|Out-Null
    Text-Box 207 29 176 20 'Resolutions' 10.8 $true 1 $C.ink|Out-Null
    Line-Segment 208 58 382 58 $C.rule 0.6 $false|Out-Null
    Draw-WorldStack 221 76 '' $C.blue
    Text-Box 294 86 84 32 'W worlds' 8.6 $true 1 $C.muted|Out-Null
    Line-Segment 208 157 382 157 $C.rule 0.6 $false|Out-Null
    Draw-Ranking 218 184
    Line-Segment 172 113 193 113 $C.ink 0.8 $true|Out-Null

    # Shared paired selection: same graph and sampled worlds, different eligibility masks.
    Rect-Box 423 18 479 365 '' $C.white $C.ink 8 $false 2 0.85 0.04|Out-Null
    Text-Box 442 29 440 21 'Paired greedy selection' 11.0 $true 1 $C.ink|Out-Null
    Text-Box 442 54 440 18 'same G and sampled worlds; only eligibility differs' 8.3 $false 1 $C.muted|Out-Null
    Line-Segment 442 81 883 81 $C.rule 0.6 $false|Out-Null

    Text-Box 430 99 96 18 'full' 9.2 $true 1 $C.blue|Out-Null
    Rect-Box 443 125 69 38 'V' $C.blueFill $C.blue 12 $true 1 0.75 0.035|Out-Null
    Line-Segment 513 144 535 144 $C.blue 0.9 $true|Out-Null
    Draw-Iteration 537 90 't = 1' $C.blue $false
    Line-Segment 670 149 705 149 $C.blue 0.9 $true|Out-Null
    Draw-Iteration 707 90 't = k' $C.blue $true
    Text-Box 834 124 58 48 'S_F' 8.2 $true 1 $C.blue|Out-Null

    Line-Segment 442 218 883 218 $C.rule 0.6 $false|Out-Null
    Text-Box 430 236 96 18 'pool C' 8.8 $true 1 $C.red|Out-Null
    Rect-Box 443 264 69 38 'C' $C.redFill $C.red 12 $true 1 0.75 0.035|Out-Null
    Line-Segment 513 283 535 283 $C.red 0.9 $true|Out-Null
    Draw-Iteration 537 229 't = 1' $C.red $false
    Line-Segment 670 288 705 288 $C.red 0.9 $true|Out-Null
    Draw-Iteration 707 229 't = k' $C.red $true
    Text-Box 834 263 58 48 'S_C' 8.2 $true 1 $C.red|Out-Null
    Text-Box 443 352 438 20 'exhaustive per-round enumeration' 8.7 $false 1 $C.muted|Out-Null

    # Independent evaluation and reporting.
    Line-Segment 904 197 932 197 $C.ink 0.9 $true|Out-Null
    Rect-Box 934 18 242 365 '' $C.white $C.rule 8 $false 1 0.75 0.03|Out-Null
    Text-Box 948 29 214 21 'Evaluation' 10.5 $true 1 $C.ink|Out-Null
    Text-Box 949 55 212 22 ('disjoint ' + [char]0x03A9 + '_eval') 8.5 $false 1 $C.muted|Out-Null
    Draw-WorldStack 952 105 '' $C.gold
    Text-Box 1024 96 130 42 '10,000 worlds' 8.7 $true 1 $C.gold|Out-Null
    Line-Segment 975 183 975 219 $C.gold 0.85 $true|Out-Null
    Rect-Box 953 220 198 51 'paired spread' $C.goldFill $C.gold 10.5 $true 1 0.75 0.035|Out-Null
    Text-Box 956 279 194 20 ('paired ' + [char]0x0394 + 'U') 8.8 $true 1 $C.ink|Out-Null
    Line-Segment 1052 306 1052 327 $C.ink 0.8 $true|Out-Null
    Rect-Box 952 329 201 39 'trajectory  |  set  |  utility  |  cost' $C.pale $C.ink 8.4 $true 1 0.65 0.02|Out-Null

    # Panel labels mirror the compact two-stage structure common in conference method figures.
    Text-Box 199 406 698 24 '(a) Resolution-controlled paired seed selection' 9.8 $true 1 $C.ink|Out-Null
    Text-Box 935 406 241 24 '(b) Independent diagnosis' 9.3 $true 1 $C.ink|Out-Null

    if($doc.Pages.Count -gt 1){$doc.Pages.Item(1).Delete(1)}
    $base='im_evaluation_mechanism_v2';$vsdx=Join-Path $OutputDir ($base+'.vsdx');$svg=Join-Path $OutputDir ($base+'.svg');$png=Join-Path $OutputDir ($base+'.png');$inv=Join-Path $OutputDir 'native_shape_inventory_mechanism_v2.json'
    $doc.SaveAs($vsdx);$script:Page.Export($svg);$script:Page.Export($png);$script:inventory|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $inv -Encoding utf8
    Write-Output "Saved: $vsdx";Write-Output "Saved: $svg";Write-Output "Saved: $png";Write-Output "Native shapes: $($script:Page.Shapes.Count)"
}finally{if($doc){try{$doc.Close()}catch{}};if($app){try{$app.Quit()}catch{}}}
