$ErrorActionPreference='Stop'
$pkg=Join-Path (Split-Path $PSScriptRoot -Parent) 'manuscript\resolution_aware_candidate_truncation_submission_v0_1'
$inputFile=Join-Path $pkg 'manuscript_review_20260921.docx'
$output=Join-Path $pkg 'word_qa'
New-Item -ItemType Directory -Path $output -Force | Out-Null
$app=$null;$doc=$null
try {
    Write-Output 'Connecting to installed WPS document renderer.'
    $app=New-Object -ComObject kwps.Application
    Write-Output 'Opening task manuscript read-only.'
    $doc=$app.Documents.Open($inputFile,$false,$true)
    Write-Output 'Exporting internal PDF preview.'
    $doc.ExportAsFixedFormat((Join-Path $output 'manuscript_review_20260921.pdf'),17)
    Write-Output "WPS rendering completed; pages=$($doc.ComputeStatistics(2))"
} finally {
    if($doc){$doc.Close(0)}
    # Do not quit WPS: unrelated user documents may be open in the application.
    if($app){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)}
}
