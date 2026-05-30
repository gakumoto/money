"""リサーチウォッチリストを順次実行する.

`.company/research/watchlist.md` を読み、登録された YouTube チャンネルと
Web テーマで自動リサーチを走らせる。タスクスケジューラから定期実行する想定。

使い方:
    python scripts/run_watchlist.py              # 全部実行
    python scripts/run_watchlist.py --type youtube   # YouTube だけ
    python scripts/run_watchlist.py --type web       # Web だけ
    python scripts/run_watchlist.py --dry-run        # 何を実行するか確認のみ
"""
from __future__ import annotations

import datetime as dt
import os
import re
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

sys.path.insert(0, str(SCRIPT_DIR))
from _discord import notify  # noqa: E402
from _net_wait import wait_for_network  # noqa: E402

WATCHLIST_PATH = (
    PROJECT_ROOT / ".company" / "research" / "watchlist.md"
)


def parse_watchlist() -> tuple[list[dict], list[str]]:
    """watchlist.md を解析して (youtube_entries, web_themes) を返す.

    youtube_entries: [{"url": ..., "count": int, "notes": str}, ...]
    web_themes: ["theme1", "theme2", ...]
    """
    if not WATCHLIST_PATH.exists():
        return [], []
    text = WATCHLIST_PATH.read_text(encoding="utf-8")

    youtube: list[dict] = []
    web: list[str] = []
    section = None

    for line in text.splitlines():
        # セクションヘッダで切替
        if re.match(r"^## .*YouTube", line, re.IGNORECASE):
            section = "youtube"
            continue
        if re.match(r"^## .*Web", line, re.IGNORECASE):
            section = "web"
            continue
        if line.startswith("## "):
            section = None
            continue
        # 太字見出し (**編集ルール**) や 水平線 (---) で項目セクション終了扱い
        # → これ以降の `-` 行は説明文なので無視
        if line.startswith("**") or line.strip() == "---":
            section = None
            continue

        # 各行: - <data> | <meta> | <note>
        m = re.match(r"^-\s+(.+?)\s*$", line)
        if not m or section is None:
            continue
        body = m.group(1).strip()

        if section == "youtube":
            # 形式: <url> | count:N | <notes>
            parts = [p.strip() for p in body.split("|")]
            url = parts[0]
            if not url.startswith("http"):
                continue
            if "example" in url:  # サンプル行はスキップ
                continue
            count = 10
            notes = ""
            for p in parts[1:]:
                cm = re.match(r"count\s*:\s*(\d+)", p)
                if cm:
                    count = max(1, min(int(cm.group(1)), 20))
                else:
                    notes = p
            youtube.append({"url": url, "count": count, "notes": notes})
        elif section == "web":
            if body:
                web.append(body)

    return youtube, web


def run_claude_skill(prompt: str, *, timeout: int = 1800) -> tuple[int, str, str]:
    """Claude Code ヘッドレスでスキルを実行. (rc, stdout_tail, stderr_tail)"""
    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"
    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    try:
        r = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return r.returncode, (r.stdout or "")[-1500:], (r.stderr or "")[-500:]
    except subprocess.TimeoutExpired:
        return -1, "", f"タイムアウト ({timeout}秒)"


def main():
    target_type = "all"
    dry_run = False
    for a in sys.argv[1:]:
        if a == "--dry-run":
            dry_run = True
        elif a.startswith("--type"):
            # --type youtube / --type web / --type all
            if "=" in a:
                target_type = a.split("=", 1)[1]
            else:
                # 次の引数を取る (簡易)
                pass
    # シンプルに位置引数で受ける
    if len(sys.argv) > 1 and sys.argv[1] in ("youtube", "web", "all"):
        target_type = sys.argv[1]

    started = dt.datetime.now()
    print(f"[watchlist] 開始: {started.isoformat(timespec='seconds')} (type={target_type})")

    if not dry_run:
        if not wait_for_network():
            msg = "[watchlist] ネット復帰待ちタイムアウト"
            print(msg, file=sys.stderr)
            notify(msg)
            sys.exit(1)

    yt_entries, web_themes = parse_watchlist()
    print(f"[watchlist] 登録: YouTube {len(yt_entries)} 件 / Web {len(web_themes)} 件")

    summary_lines = [
        f"📚 自動リサーチ実行 ({started.strftime('%Y-%m-%d %H:%M')})",
    ]

    yt_success = 0
    yt_failed = 0
    if target_type in ("all", "youtube") and yt_entries:
        print("\n=== YouTube リサーチ ===")
        for e in yt_entries:
            print(f"  - {e['url']} (count={e['count']})")
            if dry_run:
                continue
            prompt = f"/youtube-research {e['url']} {e['count']}"
            rc, out, err = run_claude_skill(prompt, timeout=1800)
            if rc == 0:
                yt_success += 1
                print("    ✅ 完了")
            else:
                yt_failed += 1
                print(f"    ❌ 失敗 (rc={rc}): {err[:200]}")
        summary_lines.append(
            f"📺 YouTube: 成功 {yt_success} / 失敗 {yt_failed}"
        )

    web_success = 0
    web_failed = 0
    if target_type in ("all", "web") and web_themes:
        print("\n=== Web リサーチ ===")
        for theme in web_themes:
            print(f"  - {theme}")
            if dry_run:
                continue
            prompt = f"/research-collect {theme}"
            rc, out, err = run_claude_skill(prompt, timeout=900)
            if rc == 0:
                web_success += 1
                print("    ✅ 完了")
            else:
                web_failed += 1
                print(f"    ❌ 失敗 (rc={rc}): {err[:200]}")
        summary_lines.append(
            f"🔍 Web: 成功 {web_success} / 失敗 {web_failed}"
        )

    ended = dt.datetime.now()
    elapsed = (ended - started).total_seconds()
    summary_lines.append(f"⏱️ 所要: {elapsed:.0f} 秒")
    summary_lines.append(
        f"💾 結果: .company/research/topics/ を確認 / 翌朝の /post_bulk が自動参照"
    )

    summary = "\n".join(summary_lines)
    print("\n" + summary)
    if not dry_run:
        notify(summary)


if __name__ == "__main__":
    main()
