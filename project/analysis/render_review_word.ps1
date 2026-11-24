$ErrorActionPreference='Stop'
$pkg=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1'
$inputFile=Join-Path $pkg 'manuscript_review_20260921.docx'
$output=Join-Path $pkg 'word_qa'
New-Item -ItemType Directory -Path $output -Force | Out-Null
$word=$null;$doc=$null
try {
    $word=New-Object -ComObject Word.Application
    $word.Visible=$false;$word.DisplayAlerts=0
    $doc=$word.Documents.Open($inputFile,$false,$true)
    $doc.Repaginate()
    $doc.ExportAsFixedFormat((Join-Path $output 'manuscript_review_20260921.pdf'),17)
    Write-Output "Word rendering completed; pages=$($doc.ComputeStatistics(2))"
} finally {if($doc){$doc.Close(0)};if($word){$word.Quit()}}
