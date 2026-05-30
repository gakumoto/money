# scripts/register_research_tasks.ps1
# 自動リサーチ (ウォッチリスト実行) をタスクスケジューラに登録する.
#
# 登録されるタスク:
#   - myCompany-Research-Youtube : 毎日 06:00 (YouTube だけ)
#   - myCompany-Research-Web     : 毎日 06:30 (Web だけ)
#
# 使い方:
#   管理者 PowerShell で:
#   powershell -ExecutionPolicy Bypass -File scripts/register_research_tasks.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$runScript = Join-Path $scriptDir "run_watchlist.py"
$envFile = Join-Path $scriptDir ".env"

if (-not (Test-Path $runScript)) {
    Write-Error "run_watchlist.py が見つかりません: $runScript"
    exit 1
}

# Python 実体パス
$pythonExe = ""
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^PYTHON_EXE=(.+)$") {
            $pythonExe = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
}
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    Write-Warning ".env の PYTHON_EXE が未設定。python コマンドで登録"
    $pythonExe = "python"
}

Write-Host "プロジェクト: $projectRoot" -ForegroundColor Cyan
Write-Host "Python:       $pythonExe" -ForegroundColor Cyan
Write-Host "Script:       $runScript" -ForegroundColor Cyan
Write-Host ""

# 共通 settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Task 1: YouTube 06:00
$taskName1 = "myCompany-Research-Youtube"
$existing = Get-ScheduledTask -TaskName $taskName1 -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "既存タスク $taskName1 を削除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName1 -Confirm:$false
}
$action1 = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "`"$runScript`" youtube" `
    -WorkingDirectory $projectRoot
$trigger1 = New-ScheduledTaskTrigger -Daily -At "06:00"
Register-ScheduledTask `
    -TaskName $taskName1 `
    -Description "myCompany: YouTube watchlist 自動リサーチ (毎日 06:00)" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings
Write-Host "✅ 登録完了: $taskName1 (毎日 06:00)" -ForegroundColor Green

# Task 2: Web 06:30
$taskName2 = "myCompany-Research-Web"
$existing = Get-ScheduledTask -TaskName $taskName2 -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "既存タスク $taskName2 を削除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName2 -Confirm:$false
}
$action2 = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "`"$runScript`" web" `
    -WorkingDirectory $projectRoot
$trigger2 = New-ScheduledTaskTrigger -Daily -At "06:30"
Register-ScheduledTask `
    -TaskName $taskName2 `
    -Description "myCompany: Web watchlist 自動リサーチ (毎日 06:30)" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings
Write-Host "✅ 登録完了: $taskName2 (毎日 06:30)" -ForegroundColor Green

Write-Host ""
Write-Host "=== 登録完了 ===" -ForegroundColor Cyan
Write-Host "確認: Get-ScheduledTask -TaskName 'myCompany-Research-*' | Format-Table"
Write-Host "即時実行: Start-ScheduledTask -TaskName '$taskName1'"
Write-Host "削除: Unregister-ScheduledTask -TaskName '$taskName1' -Confirm:`$false"
