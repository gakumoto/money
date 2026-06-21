# myCompany-StudioWeb: /studio ダッシュボードを常駐起動（ログイン時・ポート3010）
# next dev を node + next バイナリ直接で起動（PATH/npm依存を避ける）
$ErrorActionPreference = "Stop"
$root = "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"
$dash = Join-Path $root "dashboard"
$node = "C:\Program Files\nodejs\node.exe"
$nextbin = Join-Path $dash "node_modules\next\dist\bin\next"

$action = New-ScheduledTaskAction -Execute $node -Argument ('"' + $nextbin + '" dev -p 3010') -WorkingDirectory $dash
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName "myCompany-StudioWeb" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output "registered: myCompany-StudioWeb (logon, port 3010)"
