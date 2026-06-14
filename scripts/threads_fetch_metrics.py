"""Threads 投稿のメトリクスを取得して posted/ の各ファイルに書き込む.

直近30日分の投稿のうち、既にメトリクスが入っているものはスキップ.
毎晩22時に実行する想定.

使い方:
    python scripts/threads_fetch_metrics.py <account> [days]
    python scripts/threads_fetch_metrics.py gaku_ai_life 30
"""
from __future__ import annotations

import datetime as dt
import re
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
from _threads_api import ThreadsClient  # noqa: E402
from _discord import notify  # noqa: E402
from _net_wait import wait_for_network  # noqa: E402

METRICS_BLOCK_MARK = "<!-- THREADS_METRICS -->"


def list_posted_files(account: str, days: int) -> list[Path]:
    """posted/<account>/ から過去 days 日分のファイルを返す."""
    posted = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "posted"
    if not posted.exists():
        return []
    cutoff = dt.date.today() - dt.timedelta(days=days)
    out = []
    for f in posted.glob("*.md"):
        # ファイル名から日付抽出 (YYYY-MM-DD_HHMM_...)
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", f.name)
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d >= cutoff:
            out.append(f)
    return out


def has_metrics(path: Path) -> bool:
    return METRICS_BLOCK_MARK in path.read_text(encoding="utf-8")


def extract_media_id(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"threads_media_id:\s*(\S+)", text)
    return m.group(1).strip() if m else ""


def write_metrics(path: Path, metrics: dict, fetched_at: dt.datetime) -> None:
    """ファイル末尾にメトリクスブロックを追加."""
    block = [
        f"\n\n{METRICS_BLOCK_MARK}",
        f"## Threadsメトリクス (取得: {fetched_at.isoformat(timespec='seconds')})",
        "",
        "| 指標 | 値 |",
        "|------|----|",
    ]
    for k in ("views", "likes", "replies", "reposts", "quotes", "shares"):
        v = metrics.get(k, "-")
        block.append(f"| {k} | {v} |")
    block.append("")
    path.write_text(
        path.read_text(encoding="utf-8") + "\n".join(block), encoding="utf-8"
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    account = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    # スリープ復帰直後の DNS 不安定対策: ネット復帰まで最大3分待つ
    if not wait_for_network():
        print(
            f"[fetch_metrics] ネット復帰待ちタイムアウト ({account}): スキップ",
            file=sys.stderr,
        )
        sys.exit(1)

    files = list_posted_files(account, days)
    print(f"[fetch_metrics] 対象: {len(files)}件 (過去{days}日, {account})")

    if not files:
        print("[fetch_metrics] スキップ (対象なし)")
        return

    try:
        client = ThreadsClient.from_env(account=account)
    except Exception as e:
        print(f"[fetch_metrics] 認証失敗: {e}", file=sys.stderr)
        sys.exit(1)

    now = dt.datetime.now()
    updated = 0
    skipped = 0
    failed = 0

    for f in files:
        if has_metrics(f):
            skipped += 1
            continue
        media_id = extract_media_id(f)
        if not media_id:
            print(f"  - {f.name}: media_id 無し → スキップ")
            skipped += 1
            continue
        try:
            metrics = client.get_insights(media_id)
            write_metrics(f, metrics, now)
            updated += 1
            print(f"  - {f.name}: {metrics}")
        except Exception as e:
            failed += 1
            print(f"  - {f.name}: 失敗 {e}", file=sys.stderr)

    summary = (
        f"[Threadsメトリクス取得] {account}\n"
        f"- 更新: {updated}件\n"
        f"- スキップ(既存): {skipped}件\n"
        f"- 失敗: {failed}件"
    )
    print(summary)
    if updated > 0 or failed > 0:
        notify(summary)

    # メトリクス更新があれば、feedback への自動転記を実行
    # (伸びた / スベった パターンを feedback 蓄積に自動反映)
    if updated > 0:
        try:
            from metrics_to_feedback import run as m2f_run

            m2f_result = m2f_run(account, days, silent=False)
            if (
                m2f_result["high_added"] > 0
                or m2f_result["low_added"] > 0
            ):
                notify(
                    f"[m2f] {account}: 良かった例 +{m2f_result['high_added']}件 "
                    f"/ 悪かった例 +{m2f_result['low_added']}件 → 次回生成に反映"
                )
        except Exception as e:
            print(f"[fetch_metrics] m2f 連動失敗: {e}", file=sys.stderr)

        # メトリクスを INDEX に紐付け（型×ジャンル別の効き目集計が更新される）
        try:
            import subprocess

            sync_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "sync_metrics_to_research_index.py"),
                    "--account",
                    account,
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            if sync_result.returncode == 0:
                print(f"[fetch_metrics] sync_metrics_to_research_index ok\n{sync_result.stdout.strip()}")
            else:
                print(
                    f"[fetch_metrics] sync_metrics_to_research_index failed: "
                    f"exit={sync_result.returncode}\n{sync_result.stderr.strip()}",
                    file=sys.stderr,
                )
        except Exception as e:
            print(f"[fetch_metrics] sync_metrics_to_research_index 連動失敗: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
