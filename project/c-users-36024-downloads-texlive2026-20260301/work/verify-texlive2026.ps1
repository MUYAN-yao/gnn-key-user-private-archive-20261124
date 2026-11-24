$ErrorActionPreference = 'Stop'
$texBin = 'C:\texlive\2026\bin\windows'
$env:Path = $texBin + ';' + $env:Path
$env:LC_ALL = 'C'
$env:LC_CTYPE = 'C'
$env:LANG = 'C'
Set-Location -LiteralPath $PSScriptRoot
$texChecks = @()
function Invoke-TexCheck {
    param([string]$Name, [string]$Executable, [string[]]$TexArguments)
    & (Join-Path $texBin $Executable) @TexArguments *> (Join-Path $PSScriptRoot ($Name + '.console.log'))
    $texExit = $LASTEXITCODE
    $script:texChecks += [pscustomobject]@{ name = $Name; exitCode = $texExit }
    if ($texExit -ne 0) {
        $script:texChecks | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'texlive-verification.json') -Encoding UTF8
        throw "$Name failed with exit code $texExit."
    }
}
Invoke-TexCheck 'pdflatex-english' 'pdflatex.exe' @('-interaction=nonstopmode','-halt-on-error','verify-english.tex')
Invoke-TexCheck 'xelatex-chinese-first' 'xelatex.exe' @('-interaction=nonstopmode','-halt-on-error','verify-chinese.tex')
Invoke-TexCheck 'biber-references' 'biber.exe' @('verify-chinese')
Invoke-TexCheck 'xelatex-chinese-second' 'xelatex.exe' @('-interaction=nonstopmode','-halt-on-error','verify-chinese.tex')
Invoke-TexCheck 'xelatex-chinese-final' 'xelatex.exe' @('-interaction=nonstopmode','-halt-on-error','verify-chinese.tex')
Invoke-TexCheck 'lualatex-english' 'lualatex.exe' @('-interaction=nonstopmode','-halt-on-error','-jobname=verify-lualatex','verify-english.tex')
$texChecks | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'texlive-verification.json') -Encoding UTF8
$texChecks | ConvertTo-Json -Compress
