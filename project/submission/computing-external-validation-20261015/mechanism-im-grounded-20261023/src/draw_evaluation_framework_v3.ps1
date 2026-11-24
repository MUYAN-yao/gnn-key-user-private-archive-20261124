param(
    [string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'),
    [string]$BaseName = 'im_evaluation_mechanism_v3',
    [switch]$CloseExistingTarget,
    [switch]$LeaveOpen,
    [switch]$SkipInventory,
    [switch]$WithResultLayer
)

$ErrorActionPreference = 'Stop'
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$targetVsdx = Join-Path $OutputDir ($BaseName + '.vsdx')

if($CloseExistingTarget){
    try{
        $running = [Runtime.InteropServices.Marshal]::GetActiveObject('Visio.Application')
        foreach($openDoc in @($running.Documents)){
            try{
                if([IO.Path]::GetFullPath($openDoc.FullName) -ieq [IO.Path]::GetFullPath($targetVsdx)){
                    $openDoc.Save()
                    $openDoc.Close()
                }
            }catch{}
        }
    }catch{}

    if(Test-Path -LiteralPath $targetVsdx){
        $backupDir = Join-Path $OutputDir '.inplace-backup'
        New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        Copy-Item -LiteralPath $targetVsdx -Destination (Join-Path $backupDir ($BaseName + '-before-' + $stamp + '.vsdx'))
    }
}

$app = New-Object -ComObject Visio.Application
$app.Visible = [bool]$LeaveOpen
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

if($WithResultLayer){
    $script:RefWidth = 1400.0
    $script:PageWidth = 8.75
}else{
    $script:RefWidth = 1200.0
    $script:PageWidth = 7.5
}

function Set-Cell($shape,[string]$name,[string]$formula){try{$shape.CellsU($name).FormulaU=$formula}catch{}}
function X([double]$v){$script:PageWidth*$v/$script:RefWidth}
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
    $doc=$app.Documents.Add('');$script:Font=$doc.Fonts.Item('Arial').ID;$script:PageHeight=3.0;$script:Page=$doc.Pages.Add();$script:Page.Name='Evaluation mechanism';Set-Cell $script:Page.PageSheet 'PageWidth' ($script:PageWidth.ToString([Globalization.CultureInfo]::InvariantCulture) + ' in');Set-Cell $script:Page.PageSheet 'PageHeight' '3.0 in'

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
    Text-Box 294 75 84 20 (([char]0x03A9) + 'W') 9.4 $true 1 $C.blue|Out-Null
    Text-Box 286 100 100 31 'nested W-world prefixes' 7.7 $false 1 $C.muted|Out-Null
    Line-Segment 208 157 382 157 $C.rule 0.6 $false|Out-Null
    Draw-Ranking 218 184
    Line-Segment 172 113 193 113 $C.ink 0.8 $true|Out-Null

    # Shared paired selection: same graph and sampled worlds, different eligibility masks.
    Rect-Box 423 18 479 365 '' $C.white $C.ink 8 $false 2 0.85 0.04|Out-Null
    Text-Box 442 29 440 21 'Paired greedy selection' 11.0 $true 1 $C.ink|Out-Null
    Text-Box 442 54 440 18 ('shared G, ' + [char]0x03B8 + ', ' + [char]0x03A9 + 'W, k and tie rule; eligibility only differs') 7.8 $false 1 $C.muted|Out-Null
    Line-Segment 442 81 883 81 $C.rule 0.6 $false|Out-Null

    Text-Box 430 99 96 18 'full' 9.2 $true 1 $C.blue|Out-Null
    Rect-Box 443 125 69 38 'V' $C.blueFill $C.blue 12 $true 1 0.75 0.035|Out-Null
    Line-Segment 513 144 535 144 $C.blue 0.9 $true|Out-Null
    Draw-Iteration 537 90 't = 1' $C.blue $false
    Line-Segment 670 149 680 149 $C.blue 0.9 $false|Out-Null
    Text-Box 680 136 20 22 '...' 9.0 $true 1 $C.muted|Out-Null
    Line-Segment 700 149 705 149 $C.blue 0.9 $true|Out-Null
    Draw-Iteration 707 90 't = k' $C.blue $true
    Text-Box 834 124 58 48 'S_F' 8.2 $true 1 $C.blue|Out-Null

    Line-Segment 442 218 883 218 $C.rule 0.6 $false|Out-Null
    Text-Box 430 236 96 18 'pool C' 8.8 $true 1 $C.red|Out-Null
    Rect-Box 443 264 69 38 'C' $C.redFill $C.red 12 $true 1 0.75 0.035|Out-Null
    Line-Segment 513 283 535 283 $C.red 0.9 $true|Out-Null
    Draw-Iteration 537 229 't = 1' $C.red $false
    Line-Segment 670 288 680 288 $C.red 0.9 $false|Out-Null
    Text-Box 680 275 20 22 '...' 9.0 $true 1 $C.muted|Out-Null
    Line-Segment 700 288 705 288 $C.red 0.9 $true|Out-Null
    Draw-Iteration 707 229 't = k' $C.red $true
    Text-Box 834 263 58 48 'S_C' 8.2 $true 1 $C.red|Out-Null
    Rect-Box 522 350 318 25 'trajectory  |  final set  |  selection time' $C.pale $C.ink 7.4 $true 1 0.6 0.015|Out-Null

    # Independent evaluation and reporting.
    $evalWidth = if($WithResultLayer){442}else{242}
    Rect-Box 934 18 $evalWidth 365 '' $C.white $C.rule 8 $false 1 0.75 0.03|Out-Null
    Text-Box 948 29 ($evalWidth-28) 21 $(if($WithResultLayer){'Independent paired diagnosis'}else{'Paired evaluation'}) 10.3 $true 1 $C.ink|Out-Null
    Text-Box 948 54 214 32 ('same G, ' + [char]0x03B8 + '; disjoint ' + [char]0x03A9 + 'eval (10,000 worlds)') 7.5 $false 1 $C.muted|Out-Null
    Line-Segment 948 91 1162 91 $C.rule 0.6 $false|Out-Null

    Line-Segment 892 149 982 149 $C.blue 0.9 $true|Out-Null
    Draw-Graph 1018 149 0.48 @(1,4,7) @() @()
    Line-Segment 1050 149 1067 149 $C.blue 0.85 $true|Out-Null
    Rect-Box 1068 130 82 38 'U_F' $C.blueFill $C.blue 9.0 $true 1 0.7 0.025|Out-Null

    Line-Segment 948 218 1162 218 $C.rule 0.6 $false|Out-Null

    Line-Segment 892 288 982 288 $C.red 0.9 $true|Out-Null
    Draw-Graph 1018 288 0.48 @() @(0,3,6) @()
    Line-Segment 1050 288 1067 288 $C.red 0.85 $true|Out-Null
    Rect-Box 1068 269 82 38 'U_C' $C.redFill $C.red 9.0 $true 1 0.7 0.025|Out-Null

    if($WithResultLayer){
        Line-Segment 1176 51 1176 366 $C.rule 0.65 $false|Out-Null
        Text-Box 1192 57 166 20 'Measured outcomes' 8.8 $true 1 $C.ink|Out-Null

        Rect-Box 1193 92 164 40 'J(S_F, S_C)' $C.pale $C.ink 8.7 $true 1 0.65 0.02|Out-Null
        Text-Box 1200 133 150 18 'final-set agreement' 7.1 $false 1 $C.muted|Out-Null

        Rect-Box 1193 166 164 40 (([char]0x0394) + 'U = U_C - U_F') $C.goldFill $C.gold 8.5 $true 1 0.7 0.02|Out-Null
        Text-Box 1200 207 150 18 'independent utility gap' 7.1 $false 1 $C.muted|Out-Null

        Rect-Box 1193 240 164 40 (([char]0x03C1) + '_T = T_C / T_F') $C.blueFill $C.blue 8.5 $true 1 0.7 0.02|Out-Null
        Text-Box 1200 281 150 18 'selection-cost ratio' 7.1 $false 1 $C.muted|Out-Null

        Line-Segment 1275 309 1275 329 $C.ink 0.7 $true|Out-Null
        Rect-Box 1188 334 174 34 'quality-cost diagnosis' $C.white $C.ink 7.8 $true 1 0.75 0.02|Out-Null
    }else{
        Rect-Box 956 335 198 36 (([char]0x0394) + 'U = U_C - U_F') $C.goldFill $C.gold 8.4 $true 1 0.75 0.025|Out-Null
    }

    # Panel labels mirror the compact two-stage structure common in conference method figures.
    Text-Box 199 406 698 24 '(a) Resolution-controlled paired seed selection' 9.8 $true 1 $C.ink|Out-Null
    Text-Box 935 406 ($evalWidth-1) 24 '(b) Independent paired diagnosis' 9.3 $true 1 $C.ink|Out-Null

    if($doc.Pages.Count -gt 1){$doc.Pages.Item(1).Delete(1)}
    $base=$BaseName;$vsdx=Join-Path $OutputDir ($base+'.vsdx');$svg=Join-Path $OutputDir ($base+'.svg');$png=Join-Path $OutputDir ($base+'.png');$inv=Join-Path $OutputDir ('native_shape_inventory_' + $base + '.json')
    $doc.SaveAs($vsdx);$script:Page.Export($svg);$script:Page.Export($png);if(-not $SkipInventory){$script:inventory|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $inv -Encoding utf8}
    Write-Output "Saved: $vsdx";Write-Output "Saved: $svg";Write-Output "Saved: $png";Write-Output "Native shapes: $($script:Page.Shapes.Count)"
}finally{
    if(-not $LeaveOpen){
        if($doc){try{$doc.Close()}catch{}}
        if($app){try{$app.Quit()}catch{}}
    }
}
