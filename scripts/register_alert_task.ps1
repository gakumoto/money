# scripts/register_alert_task.ps1
# Register post_alert.py to run every 5 minutes.
# This catches the 15/30/60 minute alerts after each Threads post.
#
# Usage (admin PowerShell):
#   powershell -ExecutionPolicy Bypass -File scripts/register_alert_task.ps1
#
# Check:
#   Get-ScheduledTask -TaskName "myCompany-PostAlert"
#
# Remove:
#   Unregister-ScheduledTask -TaskName "myCompany-PostAlert" -Confirm:$false

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$alertScript = Join-Path $scriptDir "post_alert.py"
$envFile = Join-Path $scriptDir ".env"

if (-not (Test-Path $alertScript)) { Write-Error "post_alert.py not found"; exit 1 }

# Python path from .env
$pythonExe = ""
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^PYTHON_EXE=(.+)$") {
            $pythonExe = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
}
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    Write-Warning ".env PYTHON_EXE missing. Fallback to 'python'."
    $pythonExe = "python"
}

Write-Host "Project: $projectRoot" -ForegroundColor Cyan
Write-Host "Python:  $pythonExe" -ForegroundColor Cyan

$taskName = "myCompany-PostAlert"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task $taskName ..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$actionParams = @{
    Execute          = $pythonExe
    Argument         = "`"$alertScript`""
    WorkingDirectory = $projectRoot
}
$action = New-ScheduledTaskAction @actionParams

# Trigger: every 5 minutes, starting now, for 365 days
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)

$settingsParams = @{
    AllowStartIfOnBatteries    = $true
    DontStopIfGoingOnBatteries = $true
    StartWhenAvailable         = $true
    WakeToRun                  = $true
    ExecutionTimeLimit         = (New-TimeSpan -Minutes 10)
}
$settings = New-ScheduledTaskSettingsSet @settingsParams

$registerParams = @{
    TaskName    = $taskName
    Description = "myCompany post-alert (every 5 min, checks 15/30/60 min after each post)"
    Action      = $action
    Trigger     = $trigger
    Settings    = $settings
    RunLevel    = "Highest"
}
Register-ScheduledTask @registerParams

Write-Host ""
Write-Host "Task registered: $taskName" -ForegroundColor Green
Write-Host "Runs every 5 minutes."
Write-Host ""
Write-Host "Manual run: Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Verify:     Get-ScheduledTask -TaskName '$taskName' | Format-List"
