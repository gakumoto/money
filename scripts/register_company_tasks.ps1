# A(絡みリスト)毎朝6:00 / C(社長日報)毎晩23:40 を自動化。会社を自走させる。
# 日本語パス対策: ルートはスクリプト位置(scripts/)の親から導出する。
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 8)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# A: ナナの絡みリスト（毎朝6:00）
$aAction = New-ScheduledTaskAction -Execute $py -Argument ('"' + (Join-Path $root "scripts\build_outbound_targets.py") + '"') -WorkingDirectory $root
$aTrigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
Register-ScheduledTask -TaskName "myCompany-OutboundTargets" -Action $aAction -Trigger $aTrigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output "registered: myCompany-OutboundTargets (daily 06:00)"

# C: 社長日報（毎晩23:40）
$cAction = New-ScheduledTaskAction -Execute $py -Argument ('"' + (Join-Path $root "scripts\ceo_briefing.py") + '"') -WorkingDirectory $root
$cTrigger = New-ScheduledTaskTrigger -Daily -At 11:40PM
Register-ScheduledTask -TaskName "myCompany-CeoBriefing" -Action $cAction -Trigger $cTrigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output "registered: myCompany-CeoBriefing (daily 23:40)"
