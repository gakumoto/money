# scripts/register_report_server_task.ps1
# Register report_server.py to auto-start on PC logon.
# After registration, http://127.0.0.1:3940 will always serve gaku_ai_life_report.html.
# Tailscale Funnel exposes this safely to the internet.
#
# Usage (admin PowerShell):
#   powershell -ExecutionPolicy Bypass -File scripts/register_report_server_task.ps1
#
# Check:
#   Get-ScheduledTask -TaskName "myCompany-ReportServer"
#
# Remove:
#   Unregister-ScheduledTask -TaskName "myCompany-ReportServer" -Confirm:$false

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$serverScript = Join-Path $scriptDir "report_server.py"

if (-not (Test-Path $serverScript)) {
    Write-Error "report_server.py not found at $serverScript"
    exit 1
}

$pythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCmd) { Write-Error "python.exe not found"; exit 1 }
$pythonExe = $pythonCmd.Source

Write-Host "Project   : $projectRoot" -ForegroundColor Cyan
Write-Host "Python    : $pythonExe" -ForegroundColor Cyan
Write-Host "Server    : $serverScript" -ForegroundColor Cyan
Write-Host ""

$taskName = "myCompany-ReportServer"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task $taskName ..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$actionParams = @{
    Execute          = $pythonExe
    Argument         = "`"$serverScript`""
    WorkingDirectory = $projectRoot
}
$action = New-ScheduledTaskAction @actionParams

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settingsParams = @{
    AllowStartIfOnBatteries    = $true
    DontStopIfGoingOnBatteries = $true
    StartWhenAvailable         = $true
    RestartCount               = 5
    RestartInterval            = (New-TimeSpan -Minutes 1)
    ExecutionTimeLimit         = (New-TimeSpan -Days 365)
}
$settings = New-ScheduledTaskSettingsSet @settingsParams

$registerParams = @{
    TaskName    = $taskName
    Description = "myCompany Report Server (127.0.0.1:3940) - served via Tailscale Funnel"
    Action      = $action
    Trigger     = $trigger
    Settings    = $settings
    RunLevel    = "Highest"
}
Register-ScheduledTask @registerParams

Write-Host ""
Write-Host "Task registered: $taskName" -ForegroundColor Green
Write-Host ""
Write-Host "Start now : Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Test URL  : http://127.0.0.1:3940/healthz"
