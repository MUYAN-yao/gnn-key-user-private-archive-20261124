$ErrorActionPreference='Stop'
# Reuse only the native drawing helpers from the accepted mechanism figure.
$helpers=Get-Content (Join-Path $PSScriptRoot 'build_visio_mechanism.ps1') -Raw
$helpers=$helpers.Substring(0,$helpers.IndexOf('$visio=$null;$doc=$null'))
$helpers=$helpers.Substring($helpers.IndexOf('$script:pw='))
Invoke-Expression $helpers
$OutputDir=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1\figures'
$base=Join-Path $OutputDir 'Fig2-experimental-design'
$visio=$null;$doc=$null
try {
    $visio=New-Object -ComObject Visio.InvisibleApp
    $doc=$visio.Documents.Add('')
    $script:page=$doc.Pages.Item(1)
    $script:fontId=$doc.Fonts.Item('Arial').ID
    Cell $page.PageSheet 'PageWidth' '12 in';Cell $page.PageSheet 'PageHeight' '7.5 in'
    $page.Name='Experimental design'
    $n=$page.Shapes.Count
    Head 'a' 'Network and seed-budget coverage' 20 15 535
    Txt 300 62 85 28 'k = 5' 14 1 | Out-Null
    Txt 417 62 95 28 'k = 20' 14 1 | Out-Null
    $names=@('invs2013','invs2015','kenya2012','sfhh2009')
    for($i=0;$i -lt 4;$i++){
        $y=97+$i*51
        Graph 28 $y 74 38 'all' 3
        Txt 115 $y 150 33 $names[$i] 14 | Out-Null
        Dot 342 ($y+17) 10 $blue | Out-Null
        if($i -lt 3){Dot 465 ($y+17) 10 $blue | Out-Null}
        else {Line 451 ($y+6) 479 ($y+28) $gray | Out-Null;Line 479 ($y+6) 451 ($y+28) $gray | Out-Null}
    }
    Txt 25 302 520 27 '7 network-budget settings; SFHH k = 20 excluded by preflight' 12 | Out-Null
    GroupSince $n 'A_AdmissionMatrix'
    $n=$page.Shapes.Count
    Head 'b' 'Nested selection-world budgets' 605 15 565
    foreach($j in @(0,1)){
        $y=100+$j*86
        Txt 602 $y 102 30 @('Path 301','Path 302')[$j] 13 | Out-Null
        foreach($q in @(0,1,2)){
            $x=725+$q*143
            $nTiles=@(2,5,8)[$q]
            for($t=0;$t -lt $nTiles;$t++){
                $fill=if($t -lt 2){$blue}elseif($t -lt 5){'RGB(137,176,201)'}else{'RGB(207,225,237)'}
                Rect ($x+($t%4)*17) ($y+[math]::Floor($t/4)*17) 13 13 $fill | Out-Null
            }
            Txt ($x-3) ($y+36) 75 23 @('W = 20','W = 80','W = 320')[$q] 12 | Out-Null
            if($q -lt 2){Line ($x+85) ($y+15) ($x+128) ($y+15) $ink 1 | Out-Null}
        }
    }
    Txt 622 278 535 27 '7 settings x 2 paths x 3 budgets = 42 conditions' 14 1 | Out-Null
    Txt 622 309 535 23 'World prefixes are nested within each path' 12 | Out-Null
    GroupSince $n 'B_NestedBudgets'
    Line 584 20 584 687 'RGB(220,225,229)' 0 2 | Out-Null
    Line 22 355 1170 355 'RGB(220,225,229)' 0 2 | Out-Null
    $n=$page.Shapes.Count
    Head 'c' 'Four paired search arms' 20 382 535
    for($q=0;$q -lt 4;$q++){
        $x=25+$q*136
        Graph $x 446 115 94 $(if($q -eq 0){'all'}else{'pool'}) 6
        Txt $x 550 118 27 @('Full','Degree 2k','Degree 4k','Degree 8k')[$q] 13 1 | Out-Null
    }
    Txt 30 593 518 29 'Same topology, worlds and deterministic tie-breaking' 12 | Out-Null
    Txt 32 630 513 28 '42 conditions x 4 arms = 168 arm executions' 14 1 | Out-Null
    GroupSince $n 'C_PairedArms'
    $n=$page.Shapes.Count
    Head 'd' 'Disjoint evaluation and readouts' 605 382 565
    for($q=0;$q -lt 4;$q++){
        Dot (639+$q*26) 475 8 $blue | Out-Null
    }
    Txt 598 495 155 27 'Selected seed sets' 12 | Out-Null
    Line 758 475 794 475 $ink 1 | Out-Null
    Rect 818 450 108 80 'RGB(237,246,241)' $green | Out-Null
    Rect 812 444 108 80 $white $green | Out-Null
    Graph 822 453 82 55 'seed' 4
    Txt 778 545 184 29 '2,000 evaluation worlds' 12 0 $green | Out-Null
    Line 942 475 984 475 $ink 1 | Out-Null
    Txt 985 438 182 25 'Trace agreement' 13 | Out-Null
    Txt 985 473 182 25 'Paired spread difference' 12 | Out-Null
    Txt 985 508 182 25 'Measured time' 13 | Out-Null
    Txt 616 594 552 28 'Evaluation worlds are never used for selection' 13 1 | Out-Null
    Txt 616 632 552 35 'Shared across arms, W and k within each network-path pair' 12 | Out-Null
    GroupSince $n 'D_EvaluationReadouts'
    Txt 20 713 1158 23 'Protocol schematic: graph motifs and tile counts are illustrative; repeated conditions are not independent datasets.' 11 0 'RGB(100,110,118)' | Out-Null
    if(Test-Path -LiteralPath "$base.vsdx"){Copy-Item -LiteralPath "$base.vsdx" -Destination "$base.previous.vsdx" -Force}
    $doc.SaveAs("$base.vsdx")
    $visio.Settings.SetRasterExportResolution(2,300,300,0)
    $page.Export("$base.png");$page.Export("$base.svg")
    $doc.ExportAsFixedFormat(1,"$base.pdf",1,0)
    Write-Output 'Saved editable experimental design and PNG/SVG/PDF.'
} finally {if($doc){$doc.Close()};if($visio){$visio.Quit()}}
