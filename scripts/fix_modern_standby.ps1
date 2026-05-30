# scripts/fix_modern_standby.ps1
# 目的: Windows 11 Modern Standby が原因で発生した
#       「タスクスケジューラ起動時に Wi-Fi 復帰が遅れて DNS 引けない」問題を恒久対策する.
#
# 実行方法:
#   1. PowerShell を「管理者として実行」で開く
#   2. cd "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"
#   3. powershell -ExecutionPolicy Bypass -File .\scripts\fix_modern_standby.ps1
#   4. 再起動 (反映に必要)
#
# 変更内容:
#   A. Modern Standby を無効化 (PlatformAoAcOverride = 0)
#   B. Wi-Fi アダプタの「電源節約のためにこのデバイスをオフにできるようにする」を OFF
#   C. AC 電源時のスリープタイムアウトを 0 (=しない) に再設定 (念のため)

#Requires -RunAsAdministrator

Write-Host "=== Modern Standby 対策 開始 ===" -ForegroundColor Cyan

# A. Modern Standby 無効化
Write-Host "`n[A] Modern Standby を無効化..." -ForegroundColor Yellow
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power"
New-ItemProperty -Path $regPath -Name "PlatformAoAcOverride" -Value 0 -PropertyType DWord -Force | Out-Null
$current = (Get-ItemProperty -Path $regPath -Name "PlatformAoAcOverride").PlatformAoAcOverride
Write-Host "  PlatformAoAcOverride = $current (0 = Modern Standby 無効)" -ForegroundColor Green

# B. Wi-Fi アダプタの省電力設定 OFF
Write-Host "`n[B] Wi-Fi アダプタの省電力設定を OFF..." -ForegroundColor Yellow
$wifi = Get-NetAdapter | Where-Object { $_.PhysicalMediaType -eq "Native 802.11" -or $_.MediaType -eq "Native 802.11" }
if ($wifi) {
    foreach ($adapter in $wifi) {
        try {
            Set-NetAdapterPowerManagement -Name $adapter.Name -AllowComputerToTurnOffDevice Disabled -ErrorAction Stop
            Write-Host "  $($adapter.Name) ($($adapter.InterfaceDescription)) -> 省電力 OFF" -ForegroundColor Green
        } catch {
            Write-Host "  $($adapter.Name): 設定変更失敗 ($_)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  Wi-Fi アダプタが見つかりません" -ForegroundColor Red
}

# C. AC 電源時のスリープを念のため 0 に再設定
Write-Host "`n[C] AC 電源時のスリープを 0 に再設定..." -ForegroundColor Yellow
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
Write-Host "  完了" -ForegroundColor Green

Write-Host "`n=== すべて完了 ===" -ForegroundColor Cyan
Write-Host "★ 反映には PC の再起動が必要です。再起動してください。" -ForegroundColor Magenta
