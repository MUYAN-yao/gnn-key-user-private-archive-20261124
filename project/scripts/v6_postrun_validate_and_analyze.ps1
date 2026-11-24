param(
    [Parameter(Mandatory = $true)]
    [int]$FormalProcessId
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$auditRoot = 'audits\candidate-reduction-v6-digg-k5-formal'
$studyDir = Join-Path $auditRoot 'digg'
$statusPath = Join-Path $auditRoot 'postrun-controller-status.json'
$validationPath = Join-Path $auditRoot 'postrun-validation.json'
$analysisDir = 'analysis\v6-digg-k5-formal-v1'

while ($null -ne (Get-Process -Id $FormalProcessId -ErrorAction SilentlyContinue)) {
    Start-Sleep -Seconds 30
}

$interpreter = 'C:\Users\36024\Miniconda3\python.exe'
& $interpreter 'experiments\validate_v6_digg_k5.py' '--study-dir' $studyDir '--mode' 'formal' |
    Set-Content -Encoding utf8 $validationPath
$validationExit = $LASTEXITCODE
$status = [ordered]@{
    formal_process_id = $FormalProcessId
    completed_at = (Get-Date).ToString('o')
    validation_exit_code = $validationExit
    analysis_started = $false
    analysis_exit_code = $null
}
if ($validationExit -eq 0) {
    $status.analysis_started = $true
    & $interpreter 'experiments\analyze_v6_digg_k5.py' '--study-dir' $studyDir '--output-dir' $analysisDir |
        Set-Content -Encoding utf8 (Join-Path $auditRoot 'postrun-analysis.log')
    $status.analysis_exit_code = $LASTEXITCODE
}
$status | ConvertTo-Json | Set-Content -Encoding utf8 $statusPath
