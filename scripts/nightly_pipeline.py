"""毎晩2時に動かすパイプライン.

実行内容:
1. /threads-daily-run を Claude Code ヘッドレスモードで呼ぶ
2. 生成された下書きを数える
3. Discord に通知

Windows Task Scheduler から呼ぶ場合:
    schtasks /Create /SC DAILY /TN "myCompany-NightlyPipeline" /TR "python C:\\path\\to\\scripts\\nightly_pipeline.py" /ST 02:00

cron (Mac/Linux) なら:
    0 2 * * * cd /path/to/project && python scripts/nightly_pipeline.py
"""
from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Windows の cp932 対策
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")
PROJECT_ROOT = SCRIPT_DIR.parent

# queued/ にこの本数以上たまっていたら、その夜の生成をスキップする（バックログ防止）。
# 2026-06-26: 型別実数で1日15→7本に削減（♡が付く型D/H/Cに集約）。消費は約7本/日。
# 上限14にしておくと生成後でも最大 ~21本（約3日分）まで許容し、PCが1〜2晩落ちても
# 枯れず、かつ溜まりすぎて鮮度が崩れない範囲に収める。.env の THREADS_MAX_QUEUE で上書き可。
MAX_QUEUE = int(os.getenv("THREADS_MAX_QUEUE", "14"))

# Discord 通知ヘルパーをインポート
sys.path.insert(0, str(SCRIPT_DIR))
from _discord import notify  # noqa: E402
from _net_wait import wait_for_network  # noqa: E402


def _build_claude_cmd(claude_cmd: str, args: list[str]) -> list[str]:
    """CLAUDE_CMD が .ps1 (PowerShell スクリプト) なら powershell.exe で wrap."""
    if claude_cmd.lower().endswith(".ps1"):
        return [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
        ] + args
    return [claude_cmd] + args


def run_threads_daily_run() -> tuple[bool, str]:
    """Claude Code ヘッドレスで /threads-daily-run を実行.

    stdout / stderr を `scripts/logs/claude_headless_<timestamp>.log` に全文保存し,
    「ヘッドレスが exit=0 で返ってきたのに 0 本生成」のような事故を後追いできるようにする.
    """
    claude_cmd = os.getenv("CLAUDE_CMD", "claude")
    # --permission-mode bypassPermissions: ヘッドレスで Edit/Write/Bash 等を全自動承認
    # (2026-05-14 D-001/D-009 対策: 書き込み権限 + Bash 権限の両方が必要なため)
    cmd = _build_claude_cmd(
        claude_cmd,
        ["-p", "/threads-daily-run", "--permission-mode", "bypassPermissions"],
    )

    # 詳細ログのパス
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    claude_log_path = log_dir / f"claude_headless_{ts}.log"

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,  # 30分
        )
        # 全文を別ファイルに保存 (診断用)
        try:
            with open(claude_log_path, "w", encoding="utf-8") as f:
                f.write(f"=== CMD ===\n{' '.join(cmd)}\n\n")
                f.write(f"=== EXIT ===\n{result.returncode}\n\n")
                f.write(f"=== STDOUT ===\n{result.stdout}\n\n")
                f.write(f"=== STDERR ===\n{result.stderr}\n")
        except OSError as e:
            print(f"[nightly_pipeline] 詳細ログ保存失敗: {e}", file=sys.stderr)

        if result.returncode != 0:
            return False, (
                f"exit={result.returncode}\nstderr: {result.stderr[:1000]}\n"
                f"詳細: {claude_log_path}"
            )
        return True, f"{result.stdout[-2000:]}\n詳細ログ: {claude_log_path}"
    except subprocess.TimeoutExpired:
        return False, "タイムアウト (30分)"
    except FileNotFoundError:
        return False, f"claude コマンドが見つからない. CLAUDE_CMD={claude_cmd}"


def count_drafts_for(account: str, date: dt.date) -> int:
    """指定アカウントの指定日下書き数をカウント (queued/posted/rejected サブフォルダ含む).

    threads-create-post の出力先や Discord Bot による振り分けでファイルが
    サブフォルダに入るため、rglob で再帰的にカウントする.
    """
    drafts_dir = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account
    if not drafts_dir.exists():
        return 0
    prefix = date.isoformat()
    return sum(1 for f in drafts_dir.rglob(f"{prefix}_*.md"))


def count_queued(accounts: list[str]) -> int:
    """アクティブアカウントの queued/ にある未投稿下書きの合計本数."""
    total = 0
    for account in accounts:
        qdir = (
            PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "queued"
        )
        if qdir.exists():
            total += sum(1 for _ in qdir.glob("*.md"))
    return total


def find_active_accounts() -> list[str]:
    """marketing/accounts/ から status: active のアカウントを抽出."""
    acc_dir = PROJECT_ROOT / ".company" / "marketing" / "accounts"
    if not acc_dir.exists():
        return []
    active = []
    for f in acc_dir.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            if "status: active" in content:
                active.append(f.stem)
        except OSError:
            continue
    return active


def rebuild_research_index() -> tuple[bool, str]:
    """build_research_index.py を実行して index.json を最新化."""
    builder = SCRIPT_DIR / "build_research_index.py"
    try:
        result = subprocess.run(
            [sys.executable, str(builder)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        out = (result.stdout or "").strip()
        if result.returncode != 0:
            return False, f"exit={result.returncode}\n{result.stderr[:500]}"
        return True, out
    except subprocess.TimeoutExpired:
        return False, "タイムアウト (120秒)"


def main():
    started = dt.datetime.now()
    print(f"[nightly_pipeline] 開始: {started.isoformat(timespec='seconds')}")

    # --- バックログ防止ゲート（2026-06-14 D-049）---
    # queued がすでに十分あるなら、その夜の生成をまるごとスキップする。
    # 生成を消費(約7本/日)に合わせ、青天井に溜まって「5日遅れ」になるのを防ぐ。
    accounts_now = find_active_accounts()
    queued_now = count_queued(accounts_now)
    if queued_now >= MAX_QUEUE:
        msg = (
            f"[myCompany] 夜パイプライン: queued {queued_now}本 "
            f"(上限{MAX_QUEUE}) のため今夜の生成はスキップ。"
            "バックログ防止のため在庫が減るまで作りません。"
        )
        print(f"[nightly_pipeline] スキップ: {msg}")
        notify(msg)
        sys.exit(0)

    # スリープ復帰直後の DNS 不安定対策: ネット復帰まで最大3分待つ
    # 02:00 起動時に Wi-Fi が再接続できていないケースを救済
    if not wait_for_network(host="api.anthropic.com"):
        msg = "[nightly_pipeline] ネット復帰待ちタイムアウト: スキップ"
        print(msg, file=sys.stderr)
        notify(msg)
        sys.exit(1)

    notify(f"[myCompany] 夜のパイプライン開始: {started.strftime('%H:%M')}")

    # 下書き生成の前に index.json を最新化（threads-daily-run がネタ選びに使う）
    idx_ok, idx_log = rebuild_research_index()
    print(f"[nightly_pipeline] index rebuild: {'ok' if idx_ok else 'NG'}\n{idx_log}")

    ok, log = run_threads_daily_run()

    # 翌日分のドラフトをカウント
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    accounts = find_active_accounts()
    counts = {a: count_drafts_for(a, tomorrow) for a in accounts}
    total = sum(counts.values())

    ended = dt.datetime.now()
    elapsed = (ended - started).total_seconds()

    if ok:
        summary = (
            f"📥 下書き{total}本できました ({tomorrow.isoformat()}分)\n"
            + "\n".join(f"- {a}: {n}本" for a, n in counts.items())
            + f"\n所要時間: {elapsed:.0f}秒\n\n"
            "👉 Discord で `/review` を打つと、スマホからボタンでレビューできます。\n"
            "（承認 → キュー追加 / 編集 → モーダルで本文修正 / 再生成 / 却下）"
        )
        print(f"[nightly_pipeline] 完了\n{summary}")
        notify(summary)
        sys.exit(0)
    else:
        msg = f"夜パイプライン失敗\n{log}\n所要: {elapsed:.0f}秒"
        print(f"[nightly_pipeline] 失敗\n{msg}", file=sys.stderr)
        notify(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
