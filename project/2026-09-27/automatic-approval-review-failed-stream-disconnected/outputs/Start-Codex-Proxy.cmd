@echo off
powershell.exe -NoProfile -File "%~dp0Start-Codex-Proxy.ps1" %*
if errorlevel 1 pause
