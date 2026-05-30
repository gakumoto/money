# scripts/register_bot_task.ps1
# Register Discord Bot to auto-start on PC logon.
# Auto-restart on failure (5 times, 1 min interval).
#
# Usage (admin PowerShell):
#   powershell -ExecutionPolicy Bypass -File scripts/register_bot_task.ps1
#
# Verify:
#   Get-ScheduledTask -TaskName "myCompany-DiscordBot"
#
# Remove:
#   Unregister-ScheduledTask -TaskName "myCompany-DiscordBot" -Confirm:$false

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$botScript = Join-Path $scriptDir "discord_bot.py"
$envFile = Join-Path $scriptDir ".env"

if (-not (Test-Path $botScript)) {
    Write-Error "discord_bot.py not found: $botScript"
    exit 1
}
if (-not (Test-Path $envFile)) {
    Write-Error ".env not found: $envFile"
    exit 1
}

# Python path from .env (UTF8 forced - PS 5.1 reads as CP932 by default, breaks Japanese paths)
$pythonExe = ""
try {
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        if ($_ -match "^PYTHON_EXE=(.+)$") {
            $pythonExe = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
} catch {
    Write-Warning "Failed to read .env: $_"
}

# Fallback chain: .env -> Get-Command -> common candidate paths
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    Write-Warning ".env PYTHON_EXE not resolved. Trying Get-Command..."
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $pythonExe = $cmd.Source
        Write-Host "Found via Get-Command: $pythonExe" -ForegroundColor Yellow
    }
}
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    $candidates = @(
        "C:\Users\$env:USERNAME\AppData\Local\Python\pythoncore-3.14-64\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
        "C:\Python314\python.exe",
        "C:\Python312\python.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            $pythonExe = $c
            Write-Host "Found candidate: $pythonExe" -ForegroundColor Yellow
            break
        }
    }
}
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    Write-Error "Python not found. Please set PYTHON_EXE in scripts/.env to the full path."
    exit 1
}

Write-Host "Project: $projectRoot" -ForegroundColor Cyan
Write-Host "Python:  $pythonExe" -ForegroundColor Cyan
Write-Host "Bot:     $botScript" -ForegroundColor Cyan
Write-Host ""

$taskName = "myCompany-DiscordBot"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task $taskName ..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Splatting (avoid backtick line continuation - safer with various encodings)
$actionParams = @{
    Execute          = $pythonExe
    Argument         = "`"$botScript`""
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
    Description = "myCompany Discord Bot (persistent, auto-restart on logon)"
    Action      = $action
    Trigger     = $trigger
    Settings    = $settings
    RunLevel    = "Highest"
}
Register-ScheduledTask @registerParams

Write-Host ""
Write-Host "Task registered: $taskName" -ForegroundColor Green
Write-Host ""
Write-Host "Start now: Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Status:    Get-ScheduledTask -TaskName '$taskName' | Format-List"
Write-Host "Next login will auto-start the bot."
