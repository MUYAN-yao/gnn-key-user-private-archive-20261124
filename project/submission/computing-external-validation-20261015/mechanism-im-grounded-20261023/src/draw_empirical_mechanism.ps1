param([string]$OutputDir = (Join-Path $PSScriptRoot '..\figures'))
$ErrorActionPreference='Stop';$OutputDir=[IO.Path]::GetFullPath($OutputDir);New-Item -ItemType Directory -Force -Path $OutputDir|Out-Null
$app=New-Object -ComObject Visio.Application;$app.Visible=$false;$app.AlertResponse=7;$doc=$null
$script:items=[System.Collections.Generic.List[object]]::new();$C=@{ink='RGB(24,31,39)';muted='RGB(103,112,122)';rule='RGB(218,223,229)';gray='RGB(190,197,205)';blue='RGB(34,102,161)';blueFill='RGB(231,240,250)';orange='RGB(194,89,41)';orangeFill='RGB(253,238,229)';white='RGB(255,255,255)'}
function SetC($s,$n,$v){$s.CellsU($n).FormulaU=[string]$v};function X($v){7.5*$v/1200};function Y($v){$script:H-(7.5*$v/1200)}
function Track($s,$t,$x,$y,$w,$h,$f){$script:items.Add([pscustomobject]@{id=$s.ID;text=$t;x=$x;y=$y;width=$w;height=$h;font_pt=$f})}
function TextBox($x,$y,$w,$h,$t,$f=8,$b=$false,$a=0,$col=$C.ink){$s=$script:p.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));SetC $s 'FillPattern' 0;SetC $s 'LinePattern' 0;$s.Text=$t;SetC $s 'Char.Font' $script:font;SetC $s 'Char.Size' "$f pt";SetC $s 'Char.Style' $(if($b){1}else{0});SetC $s 'Char.Color' $col;SetC $s 'Para.HorzAlign' $a;SetC $s 'VerticalAlign' 1;Track $s $t $x $y $w $h $f;return $s}
function RectBox($x,$y,$w,$h,$t='',$fill=$C.white,$line=$C.rule,$f=8,$b=$false,$a=1){$s=$script:p.DrawRectangle((X $x),(Y($y+$h)),(X($x+$w)),(Y $y));SetC $s 'FillForegnd' $fill;SetC $s 'LineColor' $line;SetC $s 'LineWeight' '0.65 pt';SetC $s 'Rounding' '0.018 in';$s.Text=$t;SetC $s 'Char.Font' $script:font;SetC $s 'Char.Size' "$f pt";SetC $s 'Char.Style' $(if($b){1}else{0});SetC $s 'Char.Color' $C.ink;SetC $s 'Para.HorzAlign' $a;SetC $s 'VerticalAlign' 1;Track $s $t $x $y $w $h $f;return $s}
function L($x1,$y1,$x2,$y2,$col=$C.muted,$arrow=$true,$w='0.8 pt',$dash=$false){$s=$script:p.DrawLine((X $x1),(Y $y1),(X $x2),(Y $y2));SetC $s 'LineColor' $col;SetC $s 'LineWeight' $w;if($dash){SetC $s 'LinePattern' 2};if($arrow){$dx=$x2-$x1;$dy=$y2-$y1;$z=[math]::Sqrt($dx*$dx+$dy*$dy);if($z -gt 0){$ux=$dx/$z;$uy=$dy/$z;foreach($q in @(-1,1)){$ax=$x2-9*$ux+$q*3.5*(-$uy);$ay=$y2-9*$uy+$q*3.5*$ux;$a=$script:p.DrawLine((X $ax),(Y $ay),(X $x2),(Y $y2));SetC $a 'LineColor' $col;SetC $a 'LineWeight' $w}}};return $s}
function Node($cx,$cy,$t='',$fill=$C.white,$line=$C.muted,$d=26,$f=7,$b=$false){$s=$script:p.DrawOval((X($cx-$d/2)),(Y($cy+$d/2)),(X($cx+$d/2)),(Y($cy-$d/2)));SetC $s 'FillForegnd' $fill;SetC $s 'LineColor' $line;SetC $s 'LineWeight' '0.75 pt';$s.Text=$t;SetC $s 'Char.Font' $script:font;SetC $s 'Char.Size' "$f pt";SetC $s 'Char.Style' $(if($b){1}else{0});SetC $s 'Char.Color' $C.ink;SetC $s 'Para.HorzAlign' 1;SetC $s 'VerticalAlign' 1;Track $s $t ($cx-$d/2) ($cy-$d/2) $d $d $f;return $s}
try{
 $doc=$app.Documents.Add('');$script:font=$doc.Fonts.Item('Arial').ID;$script:H=4.15;$script:p=$doc.Pages.Add();$script:p.Name='Empirical coverage pathway';SetC $script:p.PageSheet 'PageWidth' '7.5 in';SetC $script:p.PageSheet 'PageHeight' '4.15 in'
 TextBox 34 18 1120 22 'wiki-Vote: candidate coverage changes seed eligibility' 10.8 $true|Out-Null
 TextBox 35 45 1125 17 'Default PageRank-4k; W = 1280; paths 1101--1105. Labels are actual retained node IDs and values are from frozen condition records.' 7.0 $false 0 $C.muted|Out-Null
 L 34 72 1166 72 $C.rule $false '0.55 pt'|Out-Null
 # Left half: concrete candidate and selected seed sets.
 TextBox 38 92 560 20 'Candidate sets in a recorded path' 8.7 $true|Out-Null;TextBox 38 114 560 15 'Path 1101; all five paths share this final seed set.' 6.5 $false 0 $C.muted|Out-Null
 L 36 137 596 137 $C.rule $false '0.5 pt'|Out-Null
 TextBox 56 161 130 16 'all nodes eligible' 7.1 $true 0 $C.blue|Out-Null;RectBox 56 184 122 32 'V = 7,115' $C.blueFill $C.blue 8.4 $true|Out-Null;L 190 200 260 200 $C.blue $true|Out-Null;TextBox 270 188 80 17 'full greedy' 6.9 $false 0 $C.blue|Out-Null
 TextBox 358 182 230 35 'S_full = {2565, 766, 11, 457, 2688}' 7.2 $true 1 $C.blue|Out-Null
 L 48 253 584 253 $C.rule $false '0.5 pt'|Out-Null
 TextBox 56 275 174 16 'PageRank-4k restricted pool' 7.1 $true 0 $C.orange|Out-Null;RectBox 56 298 122 32 'C_PR = 20' $C.orangeFill $C.orange 8.4 $true|Out-Null;L 190 314 260 314 $C.orange $true|Out-Null;TextBox 270 302 85 17 'greedy in C_PR' 6.9 $false 0 $C.orange
 TextBox 358 296 230 35 'S_PR = {3352, 2237, 2328, 2654, 1297}' 7.2 $true 1 $C.orange|Out-Null
 TextBox 55 382 532 30 'S_full has 0/5 coverage in C_PR on every recorded path. Candidate restriction changes who can be selected; it does not alter the propagation graph.' 7.4 $true 1 $C.ink|Out-Null
 # Right half: structural metrics and independent evaluation, drawn as data not a cartoon.
 TextBox 652 92 500 20 'Recorded direction and independent utility' 8.7 $true|Out-Null;TextBox 652 114 500 15 'stored arcs: voter to votee; ranking: incoming; simulation: outgoing' 6.5 $false 0 $C.muted|Out-Null
 L 642 137 1166 137 $C.rule $false '0.5 pt'|Out-Null
 TextBox 667 159 145 15 'pool degree profiles' 7.2 $true|Out-Null
 TextBox 817 153 90 18 'mean in-degree' 6.5 $false 1 $C.muted|Out-Null;TextBox 970 153 104 18 'mean out-degree' 6.5 $false 1 $C.muted|Out-Null
 TextBox 667 184 130 19 'PageRank-4k' 7.2 $true 0 $C.orange|Out-Null;RectBox 822 177 76 27 '249.75' $C.orangeFill $C.orange 7.7 $true|Out-Null;RectBox 984 177 62 27 '56.2' $C.orangeFill $C.orange 7.7 $true|Out-Null
 TextBox 667 220 130 19 'Degree-4k' 7.2 $true 0 $C.blue|Out-Null;RectBox 822 213 76 27 '70.3' $C.blueFill $C.blue 7.7 $true|Out-Null;RectBox 972 213 86 27 '489.25' $C.blueFill $C.blue 7.7 $true|Out-Null
 L 660 257 1140 257 $C.rule $false '0.5 pt'|Out-Null
 TextBox 668 273 315 17 'independently evaluated mean incremental spread' 7.2 $true|Out-Null
 L 721 370 1108 370 $C.muted $false '0.7 pt'|Out-Null;L 721 289 721 370 $C.muted $false '0.7 pt'|Out-Null;RectBox 770 293 76 77 '55.736' $C.blueFill $C.blue 8.2 $true|Out-Null;RectBox 929 348 76 22 '15.043' $C.orangeFill $C.orange 8.2 $true|Out-Null;TextBox 746 375 124 16 'full reference' 6.7 $false 1 $C.blue|Out-Null;TextBox 906 375 124 16 'PageRank-4k' 6.7 $false 1 $C.orange|Out-Null
 TextBox 688 407 398 20 'paired mean difference = -40.69334 nodes (73.01% loss)' 7.8 $true 1 $C.ink|Out-Null
 L 34 458 1166 458 $C.rule $false '0.55 pt'|Out-Null
 TextBox 38 476 1110 30 'This is a network-specific descriptive pathway. It supports neither a reverse-orientation causal claim nor a statement that PageRank is generally unsuitable for influence maximization.' 7.2 $false 0 $C.muted|Out-Null
 if($doc.Pages.Count -gt 1){$doc.Pages.Item(1).Delete(1)};$f=Join-Path $OutputDir 'wiki_vote_empirical_coverage_pathway_v4.vsdx';$doc.SaveAs($f);$script:p.Export((Join-Path $OutputDir 'wiki_vote_empirical_coverage_pathway_v4.svg'));$script:p.Export((Join-Path $OutputDir 'wiki_vote_empirical_coverage_pathway_v4.png'));$script:items|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $OutputDir 'native_shape_inventory_empirical_v4.json') -Encoding utf8;Write-Output "Saved native Visio source: $f"
}finally{if($doc){$doc.Close()};$app.Quit()}
