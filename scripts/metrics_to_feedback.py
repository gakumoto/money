"""投稿実績(メトリクス)を feedback/<account>.md に自動転記する.

posted/ の過去 N 日の投稿の views を分析し、
- 上位 (mean + 1σ 以上) → feedback の「良かった例（型として再利用する）」セクションに追記
- 下位 (mean - 1σ 以下) → feedback の「悪かった例（同じパターンを繰り返さない）」に追記

これにより、AI 生成が「実際に伸びた / スベった」データを毎日学習する状態を作る。
オーナーが手動 /feedback を打たなくても、AI が自分で精度を上げていく。

使い方:
    python scripts/metrics_to_feedback.py <account> [days]
    python scripts/metrics_to_feedback.py gaku_ai_life 30

呼び出し場所:
    threads_fetch_metrics.py の末尾で自動呼び出し済み.
    手動実行も可能 (再計算したい時など).
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path
from statistics import mean, stdev

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

# 統計判定の最小本数 (これ未満ならスキップ)
MIN_SAMPLES = 3

# 自動転記のマーカー (重複防止のため・feedback 検索用)
AUTO_HIGH_MARK = "### 自動転記"


def parse_metrics(text: str) -> dict:
    """METRICS_BLOCK_MARK 以降のテーブルからメトリクスを抽出."""
    out: dict = {}
    block_m = re.search(r"<!-- THREADS_METRICS -->.*", text, re.DOTALL)
    if not block_m:
        return out
    block = block_m.group(0)
    for line in block.splitlines():
        m = re.match(r"\|\s*(\w+)\s*\|\s*(\S+?)\s*\|", line)
        if not m:
            continue
        k = m.group(1)
        v = m.group(2)
        if v in ("-", "値"):
            continue
        try:
            out[k] = int(v)
        except ValueError:
            pass
    return out


def parse_post_meta(text: str) -> dict:
    """投稿ファイルから topic / threads_media_id / posted_at / 本文先頭 を抽出."""
    out = {"topic": "", "media_id": "", "posted_at": "", "first_line": ""}
    topic_m = re.search(r'topic:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
    if topic_m:
        out["topic"] = topic_m.group(1).strip()
    media_m = re.search(r"threads_media_id:\s*(\S+)", text)
    if media_m:
        out["media_id"] = media_m.group(1).strip()
    posted_m = re.search(r"posted_at:\s*(\S+)", text)
    if posted_m:
        out["posted_at"] = posted_m.group(1).strip()
    body_m = re.search(r"【本文】\s*\n(.+?)(?:\n|$)", text)
    if body_m:
        out["first_line"] = body_m.group(1).strip()
    return out


def collect_posted_metrics(account: str, days: int = 30) -> list[dict]:
    """posted/<account>/ から直近 days 日のメトリクス付き投稿を集める."""
    posted = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "posted"
    )
    if not posted.exists():
        return []
    cutoff = dt.date.today() - dt.timedelta(days=days)
    out = []
    for f in posted.glob("*.md"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", f.name)
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d < cutoff:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        metrics = parse_metrics(text)
        if not metrics or "views" not in metrics:
            continue
        meta = parse_post_meta(text)
        meta["metrics"] = metrics
        meta["file"] = f.name
        out.append(meta)
    return out


def classify(posts: list[dict]) -> tuple[list[dict], list[dict]]:
    """views を基準に上位/下位を分類して返す.

    Returns:
        (high_list, low_list) — 上位/下位それぞれのメタ情報のリスト
    """
    views = [p["metrics"]["views"] for p in posts]
    if len(views) < MIN_SAMPLES:
        return [], []
    avg = mean(views)
    sd = stdev(views) if len(views) >= 2 else 0
    high_threshold = avg + sd
    low_threshold = avg - sd
    high = [
        p
        for p in posts
        if p["metrics"]["views"] >= high_threshold and p["metrics"]["views"] > avg
    ]
    low = [
        p
        for p in posts
        if p["metrics"]["views"] <= low_threshold and p["metrics"]["views"] < avg
    ]
    return high, low


def feedback_already_has(feedback_text: str, media_id: str) -> bool:
    """media_id がすでに feedback に記録されているかチェック."""
    if not media_id:
        return False
    return media_id in feedback_text


def build_entry(post: dict, fetched_at: dt.datetime, is_high: bool) -> str:
    """feedback に追記するブロックを組み立てる."""
    m = post["metrics"]
    label = "★伸びた" if is_high else "低反応"
    metric_line = (
        f"views={m.get('views', '-')} likes={m.get('likes', '-')} "
        f"replies={m.get('replies', '-')} reposts={m.get('reposts', '-')}"
    )
    return (
        f"\n{AUTO_HIGH_MARK} {post['posted_at'][:16]} ({label}): {post['topic']}\n"
        f"- media_id: {post['media_id']}\n"
        f"- {metric_line}\n"
        f"- 冒頭1行: {post['first_line']}\n"
        f"- 自動転記日時: {fetched_at.isoformat(timespec='seconds')}\n"
    )


def append_to_feedback(
    account: str, high: list[dict], low: list[dict]
) -> tuple[int, int]:
    """feedback ファイルに追記. 重複 (media_id 一致) はスキップ.

    Returns:
        (high_added, low_added) — 実際に追加された件数
    """
    fb_path = (
        PROJECT_ROOT / ".company" / "marketing" / "feedback" / f"{account}.md"
    )
    if not fb_path.exists():
        # 雛形を新規作成
        fb_path.parent.mkdir(parents=True, exist_ok=True)
        fb_path.write_text(
            f"# {account} フィードバック蓄積\n\n"
            "## 使い方（AI スタッフへ）\n"
            "- 生成前に必ず全文を読む\n"
            "- 「繰り返し指摘されている項目」を最優先で守る\n"
            "- 「良かった例」を型として再利用する\n"
            "- 「悪かった例」のパターンを繰り返さない\n\n"
            "## 良かった例（型として再利用する）\n\n"
            "## 悪かった例（同じパターンを繰り返さない）\n\n"
            "## フィードバック履歴（時系列）\n",
            encoding="utf-8",
        )
    text = fb_path.read_text(encoding="utf-8")
    now = dt.datetime.now()

    high_added = 0
    for p in high:
        if feedback_already_has(text, p["media_id"]):
            continue
        entry = build_entry(p, now, is_high=True)
        # 「## 良かった例」見出しの直後に追記
        new_text, n = re.subn(
            r"(## 良かった例[^\n]*\n)",
            r"\1" + entry,
            text,
            count=1,
        )
        if n == 1:
            text = new_text
            high_added += 1

    low_added = 0
    for p in low:
        if feedback_already_has(text, p["media_id"]):
            continue
        entry = build_entry(p, now, is_high=False)
        new_text, n = re.subn(
            r"(## 悪かった例[^\n]*\n)",
            r"\1" + entry,
            text,
            count=1,
        )
        if n == 1:
            text = new_text
            low_added += 1

    fb_path.write_text(text, encoding="utf-8")
    return high_added, low_added


def run(account: str, days: int = 30, *, silent: bool = False) -> dict:
    """メイン処理. 結果を dict で返す (他スクリプトから import 用)."""
    posts = collect_posted_metrics(account, days)
    n = len(posts)
    result = {
        "account": account,
        "days": days,
        "sampled": n,
        "high_added": 0,
        "low_added": 0,
        "skipped_reason": None,
    }

    if not silent:
        print(f"[m2f] 対象: {n} 件 (過去{days}日, {account})")

    if n < MIN_SAMPLES:
        result["skipped_reason"] = f"サンプル不足 ({n} < {MIN_SAMPLES})"
        if not silent:
            print(f"[m2f] スキップ: {result['skipped_reason']}")
        return result

    high, low = classify(posts)
    if not silent:
        print(
            f"[m2f] 上位 (>= mean+σ): {len(high)} 件 / "
            f"下位 (<= mean-σ): {len(low)} 件"
        )

    if not high and not low:
        result["skipped_reason"] = "全投稿が平均±σ内 (分散が小さい)"
        if not silent:
            print(f"[m2f] {result['skipped_reason']}")
        return result

    high_added, low_added = append_to_feedback(account, high, low)
    result["high_added"] = high_added
    result["low_added"] = low_added
    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    account = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    result = run(account, days)

    summary_lines = [f"[メトリクス→feedback 自動転記] {result['account']}"]
    if result["skipped_reason"]:
        summary_lines.append(f"- スキップ: {result['skipped_reason']}")
        summary_lines.append(
            f"- 解析対象: {result['sampled']} 件 (過去{result['days']}日)"
        )
        summary_lines.append(
            "次回サンプルが揃ったら自動で「良かった例 / 悪かった例」が増えます。"
        )
    else:
        summary_lines.append(f"- 良かった例に追加: {result['high_added']} 件")
        summary_lines.append(f"- 悪かった例に追加: {result['low_added']} 件")
        summary_lines.append(
            f"- 解析対象: {result['sampled']} 件 (過去{result['days']}日)"
        )
        summary_lines.append("次回 AI 生成からは新パターンが反映されます。")
    summary = "\n".join(summary_lines)

    print(summary)
    notify(summary)


if __name__ == "__main__":
    main()
