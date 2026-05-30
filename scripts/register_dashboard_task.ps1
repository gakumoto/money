# scripts/register_dashboard_task.ps1
# Register cc-company-dashboard to auto-start on PC logon.
# After registration, http://localhost:3939 will be always available.
#
# Usage (admin PowerShell):
#   powershell -ExecutionPolicy Bypass -File scripts/register_dashboard_task.ps1
#
# Check:
#   Get-ScheduledTask -TaskName "myCompany-Dashboard"
#
# Remove:
#   Unregister-ScheduledTask -TaskName "myCompany-Dashboard" -Confirm:$false

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir

$npxCmd = "C:\Program Files\nodejs\npx.cmd"
if (-not (Test-Path $npxCmd)) {
    $cmd = Get-Command npx.cmd -ErrorAction SilentlyContinue
    if ($cmd) { $npxCmd = $cmd.Source } else { Write-Error "npx.cmd not found"; exit 1 }
}

Write-Host "Project: $projectRoot" -ForegroundColor Cyan
Write-Host "npx.cmd: $npxCmd" -ForegroundColor Cyan
Write-Host ""

$taskName = "myCompany-Dashboard"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task $taskName ..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Splatting (no line-continuation backticks - safer with various encodings)
$actionParams = @{
    Execute          = $npxCmd
    Argument         = "-y cc-company-dashboard --port 3939 --no-open"
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
    Description = "myCompany Dashboard (http://localhost:3939) - persistent"
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
Write-Host "Open URL  : http://localhost:3939"
Write-Host "Next login will auto-start the dashboard."
