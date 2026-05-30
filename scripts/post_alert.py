"""投稿後のメトリクスアラート (Threads アルゴリズム対策).

Threads アルゴリズム 2026:
- 投稿後 30〜60 分のリプ速度がアルゴリズム配信幅を決定
- 24 時間で 50 リプより、30 分で 20 リプの方が拡散される

threads_auto_post.py が投稿成功時に予約ファイルを作成する.
このスクリプトが 5 分おきに実行され、所定タイミング (15/30/60 分) で
メトリクスを取得し Discord に「数字 + 推奨アクション」を通知する.

予約ファイル: `.company/.alert_pending/<media_id>_<posted_at_iso>.json`

使い方:
    python scripts/post_alert.py            # スキャン + 該当アラート実行
    python scripts/post_alert.py --dry-run  # 動作確認のみ

タスクスケジューラ:
    5 分おきに実行 (毎時 0/5/10/.../55 分)
    register_alert_task.ps1 で登録可能.
"""
from __future__ import annotations

import datetime as dt
import json
import os
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

ALERT_DIR = PROJECT_ROOT / ".company" / ".alert_pending"
# チェックするタイミング (投稿後の経過分)
ALERT_TIMINGS = [15, 30, 60]
# タイミングを過ぎてから何分以内ならまだチェック対象とするか
TIMING_TOLERANCE = 15


def schedule_alert(
    account: str,
    media_id: str,
    posted_at: dt.datetime,
    first_line: str,
) -> Path:
    """投稿成功時に予約ファイルを作成 (threads_auto_post.py から呼ぶ).

    Returns: 作成した予約ファイルのパス
    """
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    safe_ts = posted_at.strftime("%Y%m%dT%H%M%S")
    fname = f"{media_id}_{safe_ts}.json"
    data = {
        "account": account,
        "media_id": media_id,
        "posted_at": posted_at.isoformat(timespec="seconds"),
        "first_line": (first_line or "").replace("\n", " ")[:80],
        "checked": [],  # 既にチェック済みの分数リスト
    }
    fpath = ALERT_DIR / fname
    fpath.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return fpath


def recommend_action(timing: int, views: int) -> str:
    """タイミングと views で推奨アクションを返す."""
    if timing == 15:
        if views < 5:
            return "↓低速。30 分以内に他人の投稿へリプ 2〜3 件推奨"
        if views < 20:
            return "→普通。他人の投稿に 1〜2 リプ返推奨"
        return "↑好調。リプ返継続でさらに伸ばす"
    if timing == 30:
        if views < 15:
            return "↓苦戦。リプ返 3 件 + 投稿 1 コメ目に体験談追加推奨"
        if views < 50:
            return "→普通。リプ返継続推奨"
        return "↑好調。Stage1 突破見込み"
    if timing == 60:
        if views < 30:
            return "↓配信幅小。投稿時刻 / 冒頭 1 行を次回見直し推奨"
        if views < 80:
            return "→普通。Stage1 通過判定保留"
        return "↑Stage1 通過、おすすめ拡散開始の可能性"
    return ""


def process_alert(data: dict, timing: int) -> bool:
    """1 つの予約 × タイミングを処理. 成功なら True."""
    try:
        client = ThreadsClient.from_env(account=data["account"])
        metrics = client.get_insights(data["media_id"])
        views = int(metrics.get("views", 0) or 0)
        likes = int(metrics.get("likes", 0) or 0)
        replies = int(metrics.get("replies", 0) or 0)
        reposts = int(metrics.get("reposts", 0) or 0)
        action = recommend_action(timing, views)
        notify(
            f"⏰ 投稿後 {timing} 分メトリクス\n"
            f"「{data['first_line']}」\n"
            f"views={views} / likes={likes} / replies={replies} / reposts={reposts}\n"
            f"💡 {action}"
        )
        print(
            f"    [{timing}min] views={views} likes={likes} replies={replies}: {action}"
        )
        return True
    except Exception as e:
        print(
            f"    [{timing}min] メトリクス取得失敗: {e}", file=sys.stderr
        )
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    if not ALERT_DIR.exists():
        print("[post_alert] 予約ディレクトリなし")
        return

    files = list(ALERT_DIR.glob("*.json"))
    if not files:
        print("[post_alert] 予約ファイルなし")
        return

    if not dry_run:
        if not wait_for_network():
            msg = "[post_alert] ネット復帰待ちタイムアウト"
            print(msg, file=sys.stderr)
            notify(msg)
            sys.exit(1)

    now = dt.datetime.now()
    print(
        f"[post_alert] {len(files)} 件の予約をチェック ({now.isoformat(timespec='seconds')})"
    )

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            posted_at = dt.datetime.fromisoformat(data["posted_at"])
            elapsed_min = (now - posted_at).total_seconds() / 60
            checked = list(data.get("checked", []))
            updated = False

            for timing in ALERT_TIMINGS:
                if timing in checked:
                    continue
                # まだその時刻に達してない
                if elapsed_min < timing:
                    continue
                # 大幅に遅れたらスキップ済み扱い (再起動などで遅延した場合の救済)
                if elapsed_min > timing + TIMING_TOLERANCE:
                    print(
                        f"  - {data['media_id'][:20]}…: [{timing}min] 期限切れスキップ "
                        f"(経過 {elapsed_min:.0f}min)"
                    )
                    checked.append(timing)
                    updated = True
                    continue

                print(
                    f"  - {data['media_id'][:20]}…: [{timing}min] 該当 "
                    f"(経過 {elapsed_min:.0f}min)"
                )
                if dry_run:
                    print("    (dry-run: API call スキップ)")
                else:
                    if process_alert(data, timing):
                        checked.append(timing)
                        updated = True

            # 全タイミング完了したらファイル削除
            if all(t in checked for t in ALERT_TIMINGS):
                if not dry_run:
                    f.unlink()
                    print(
                        f"  - {data['media_id'][:20]}…: 全タイミング完了 → 削除"
                    )
                else:
                    print(
                        f"  - {data['media_id'][:20]}…: (dry-run) 完了予定"
                    )
            elif updated and not dry_run:
                data["checked"] = checked
                f.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        except Exception as e:
            print(f"  - {f.name}: 処理失敗 {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
