$ErrorActionPreference = 'Stop'
$texWork = $PSScriptRoot
$texStatus = Join-Path $texWork 'texlive-install-status.json'
$texStarted = Get-Date
try {
    $env:PERL5LIB = 'E:\tlpkg\tlperl\lib'
    $env:PERL5OPT = ''
    $env:PERLLIB = ''
    $env:Path = 'E:\tlpkg\tlperl\bin;' + $env:Path
    Set-Location -LiteralPath $texWork
    @{ state = 'running'; started = $texStarted.ToString('o'); pid = $PID } | ConvertTo-Json | Set-Content -LiteralPath $texStatus -Encoding UTF8
    $texProcess = Start-Process -FilePath 'E:\tlpkg\tlperl\bin\perl.exe' -ArgumentList @('E:/install-tl', '-no-gui', '-profile', ($texWork.Replace('\','/') + '/texlive2026.profile'), '-repository', 'E:/') -WindowStyle Hidden -WorkingDirectory $texWork -RedirectStandardOutput (Join-Path $texWork 'texlive-install.stdout.log') -RedirectStandardError (Join-Path $texWork 'texlive-install.stderr.log') -Wait -PassThru
    @{ state = 'finished'; started = $texStarted.ToString('o'); finished = (Get-Date).ToString('o'); exitCode = $texProcess.ExitCode } | ConvertTo-Json | Set-Content -LiteralPath $texStatus -Encoding UTF8
    exit $texProcess.ExitCode
} catch {
    @{ state = 'failed'; started = $texStarted.ToString('o'); finished = (Get-Date).ToString('o'); error = $_.Exception.Message } | ConvertTo-Json | Set-Content -LiteralPath $texStatus -Encoding UTF8
    exit 1
}
