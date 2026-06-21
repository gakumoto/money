# myCompany-StudioData: studio-data.json を15分ごとに再生成（ダッシュボードを動的に）
$ErrorActionPreference = "Stop"
$root = "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"
$py = Join-Path $root ".venv\Scripts\python.exe"
$script = Join-Path $root "scripts\build_studio_data.py"

$action = New-ScheduledTaskAction -Execute $py -Argument ('"' + $script + '"') -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 8)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName "myCompany-StudioData" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output "registered: myCompany-StudioData (15min)"
