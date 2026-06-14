# scripts/run.ps1
# Task Scheduler から Python スクリプトを起動するラッパー。
# stdout/stderr を scripts/logs/<script>.log に UTF-8 で追記する。
#
# 使い方:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run.ps1 nightly_pipeline.py
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run.ps1 threads_auto_post.py gaku_ai_life

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Script,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments = @()
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$logDir = Join-Path $scriptDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Python 解決: repo の venv を最優先。
# （タスク経由の非対話 PowerShell + 日本語パスでは .env の Select-String 読取りが
#   失敗し "python"=Microsoft Store スタブにフォールバック→無言で何もせず終了する事故があったため、
#   .env に依存せず venv の python を直接使う）
$pythonExe = $null
$venvPy = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
    $pythonExe = $venvPy
} else {
    $envFile = Join-Path $scriptDir ".env"
    if (Test-Path $envFile) {
        $line = Select-String -Path $envFile -Pattern "^PYTHON_EXE=" -Encoding UTF8 | Select-Object -First 1
        if ($line) { $pythonExe = ($line.Line -replace "^PYTHON_EXE=", "").Trim().Trim('"') }
    }
    if (-not $pythonExe) { $pythonExe = "python" }
}

$scriptPath = Join-Path $scriptDir $Script
$logName = [System.IO.Path]::GetFileNameWithoutExtension($Script) + ".log"
$logFile = Join-Path $logDir $logName

function Append-Utf8 {
    param([string]$Path, [string]$Text)
    if ($null -eq $Text) { return }
    [System.IO.File]::AppendAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$argStr = $Arguments -join " "
Append-Utf8 -Path $logFile -Text "===== $now START $Script $argStr =====`r`n"

# Python の stdout を UTF-8 に
$env:PYTHONIOENCODING = "utf-8"

$exitCode = 1
$rawOutput = $null

try {
    Push-Location $projectRoot
    # Start-Process は環境変数 PATH/Path の重複で落ちることがあるため、
    # 直接呼び出しで stdout/stderr をまとめて捕捉する。
    $rawOutput = & $pythonExe $scriptPath @Arguments 2>&1
    if ($null -ne $LASTEXITCODE) {
        $exitCode = [int]$LASTEXITCODE
    } else {
        $exitCode = 0
    }
    if ($rawOutput) {
        $text = ($rawOutput | Out-String)
        if ($text) {
            Append-Utf8 -Path $logFile -Text $text
        }
    }
} catch {
    Append-Utf8 -Path $logFile -Text "[RUN ERROR] $_`r`n"
} finally {
    Pop-Location
}

$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Append-Utf8 -Path $logFile -Text "===== $now END exit=$exitCode =====`r`n`r`n"
exit $exitCode
