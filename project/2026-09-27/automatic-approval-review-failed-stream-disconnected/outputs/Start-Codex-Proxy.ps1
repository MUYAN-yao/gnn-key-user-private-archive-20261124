param([switch]$CheckOnly)

$ErrorActionPreference = 'Stop'
$proxyUrl = 'http://127.0.0.1:7888'

try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $pending = $tcp.BeginConnect('127.0.0.1', 7888, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(2000)) {
            throw '本地代理 127.0.0.1:7888 没有响应。请先启动原有的星辰代理。'
        }
        $tcp.EndConnect($pending)
    }
    finally {
        $tcp.Close()
    }

    if ($CheckOnly) {
        $previousHttp = [Environment]::GetEnvironmentVariable('HTTP_PROXY', 'Process')
        $previousHttps = [Environment]::GetEnvironmentVariable('HTTPS_PROXY', 'Process')
        try {
            [Environment]::SetEnvironmentVariable('HTTP_PROXY', $proxyUrl, 'Process')
            [Environment]::SetEnvironmentVariable('HTTPS_PROXY', $proxyUrl, 'Process')
            & codex doctor --summary --ascii --no-color
            exit $LASTEXITCODE
        }
        finally {
            [Environment]::SetEnvironmentVariable('HTTP_PROXY', $previousHttp, 'Process')
            [Environment]::SetEnvironmentVariable('HTTPS_PROXY', $previousHttps, 'Process')
        }
    }

    if (Get-Process -Name ChatGPT -ErrorAction SilentlyContinue) {
        throw 'Codex/ChatGPT 桌面应用仍在运行。请先保存正在进行的工作并从托盘完全退出应用，再运行此启动器。'
    }

    $package = Get-AppxPackage -Name OpenAI.Codex |
        Sort-Object Version -Descending |
        Select-Object -First 1
    if (-not $package) {
        throw '未找到已安装的 OpenAI.Codex Windows 应用。'
    }

    $appPath = Join-Path $package.InstallLocation 'app\ChatGPT.exe'
    if (-not (Test-Path -LiteralPath $appPath -PathType Leaf)) {
        throw "未找到桌面应用程序：$appPath"
    }

    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = $appPath
    $start.WorkingDirectory = Split-Path -Parent $appPath
    $start.UseShellExecute = $false
    $start.EnvironmentVariables['HTTP_PROXY'] = $proxyUrl
    $start.EnvironmentVariables['HTTPS_PROXY'] = $proxyUrl

    $process = [System.Diagnostics.Process]::Start($start)
    if (-not $process) {
        throw 'Windows 未能启动 Codex 桌面应用。'
    }

    Write-Host "已使用现有本地代理启动 Codex（进程 ID：$($process.Id)）。"
    Write-Host '代理设置仅属于这次启动的应用进程及其子进程。'
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
