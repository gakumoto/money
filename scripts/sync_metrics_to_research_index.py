"""posted/*.md のメトリクスを `research/index.json` に紐付け、型×ジャンルの集計を出力する.

データの流れ:
1. `.company/marketing/drafts/<account>/posted/*.md` を走査
2. frontmatter から `research_used: [{id: <id>}]` を抽出
3. ファイル末尾の `<!-- THREADS_METRICS -->` ブロックから views / likes / replies を抽出
4. INDEX エントリの `metrics` 配列に該当 draft のメトリクスを追記
5. 型×ジャンル別の平均メトリクスを `.company/research/INDEX-performance.md` に出力

使い方:
    python scripts/sync_metrics_to_research_index.py
    python scripts/sync_metrics_to_research_index.py --account gaku_ai_life

メトリクス取得（threads_fetch_metrics.py）の後に実行する想定。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / ".company" / "marketing" / "drafts"
INDEX_JSON = ROOT / ".company" / "research" / "index.json"
PERFORMANCE_MD = ROOT / ".company" / "research" / "INDEX-performance.md"

JST = timezone(timedelta(hours=9))

METRICS_BLOCK_MARK = "<!-- THREADS_METRICS -->"


def extract_frontmatter(text: str) -> dict | None:
    """先頭の `---` ... `---` を簡易パース."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    block = text[3:end].strip()
    fm: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    for line in block.split("\n"):
        m_list_id = re.match(r"\s*-\s*id:\s*\"?([^\"]+?)\"?\s*$", line)
        if m_list_id and current_list is not None:
            current_list.append({"id": m_list_id.group(1)})
            continue
        m = re.match(r"^([a-zA-Z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val in ("", "[]"):
                if val == "[]":
                    fm[key] = []
                    current_list = None
                else:
                    fm[key] = []
                    current_list = fm[key]
                current_key = key
            else:
                fm[key] = val.strip("\"'")
                current_list = None
    return fm


def extract_metrics_block(text: str) -> dict:
    """ファイル末尾のメトリクスマークダウンテーブルから数値を取り出す."""
    idx = text.find(METRICS_BLOCK_MARK)
    if idx < 0:
        return {}
    block = text[idx:]
    out: dict[str, int] = {}
    for line in block.split("\n"):
        m = re.match(r"\|\s*(views|likes|replies|reposts|quotes|shares)\s*\|\s*([0-9-]+)\s*\|", line)
        if not m:
            continue
        val = m.group(2)
        if val == "-":
            continue
        try:
            out[m.group(1)] = int(val)
        except ValueError:
            continue
    return out


def parse_posted_filename(name: str) -> dict:
    """`2026-06-02_0730_<media_id>_<original_name>.md` から日時を取得."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{4})_", name)
    if not m:
        return {}
    date_str, time_str = m.group(1), m.group(2)
    try:
        dt_obj = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H%M").replace(tzinfo=JST)
    except ValueError:
        return {}
    return {"posted_at": dt_obj.isoformat()}


def collect_metrics_per_research(account: str | None) -> dict[str, list[dict]]:
    """research id → [{draft, posted_at, views, likes, replies}, ...] のマップ."""
    out: dict[str, list[dict]] = defaultdict(list)
    accounts = [account] if account else [p.name for p in DRAFTS_DIR.iterdir() if p.is_dir()]
    for acc in accounts:
        posted_dir = DRAFTS_DIR / acc / "posted"
        if not posted_dir.exists():
            continue
        for f in posted_dir.glob("*.md"):
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = extract_frontmatter(text) or {}
            research_used = fm.get("research_used", [])
            if not isinstance(research_used, list) or not research_used:
                continue
            metrics = extract_metrics_block(text)
            if not metrics:
                continue
            meta = parse_posted_filename(f.name)
            rec = {
                "draft": str(f.relative_to(ROOT)).replace("\\", "/"),
                "posted_at": meta.get("posted_at", ""),
                "views": metrics.get("views", 0),
                "likes": metrics.get("likes", 0),
                "replies": metrics.get("replies", 0),
                "reposts": metrics.get("reposts", 0),
                "shares": metrics.get("shares", 0),
            }
            for entry in research_used:
                if isinstance(entry, dict) and entry.get("id"):
                    out[entry["id"]].append(rec)
    return out


def update_index(metrics_map: dict[str, list[dict]]) -> tuple[int, dict]:
    """INDEX に metrics を反映。更新件数と data を返す."""
    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    updated = 0
    for it in data["items"]:
        recs = metrics_map.get(it["id"], [])
        if recs:
            it["metrics"] = recs
            updated += 1
        elif "metrics" not in it:
            it["metrics"] = []
    INDEX_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return updated, data


def avg(nums: list[float]) -> float:
    return round(sum(nums) / len(nums), 1) if nums else 0.0


def render_performance_md(data: dict) -> None:
    """型×ジャンル別の平均メトリクスを INDEX-performance.md に出力."""
    items_with_metrics = [it for it in data["items"] if it.get("metrics")]

    by_genre: dict[str, list[dict]] = defaultdict(list)
    by_type: dict[str, list[dict]] = defaultdict(list)
    by_genre_type: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for it in items_with_metrics:
        latest = it["metrics"][-1]
        by_genre[it["genre"]].append(latest)
        by_type[it["type"]].append(latest)
        by_genre_type[(it["genre"], it["type"])].append(latest)

    lines = [
        f"# リサーチINDEX パフォーマンス集計",
        "",
        f"_生成: {datetime.now(JST).strftime('%Y-%m-%d %H:%M')} ／ "
        f"メトリクス紐付けエントリ数: **{len(items_with_metrics)}**_",
        "",
        "## ジャンル別 平均",
        "",
        "| ジャンル | 件数 | 平均views | 平均likes | 平均replies |",
        "|---|---:|---:|---:|---:|",
    ]
    for genre, recs in sorted(by_genre.items(), key=lambda x: -avg([r["likes"] for r in x[1]])):
        lines.append(
            f"| {genre} | {len(recs)} | "
            f"{avg([r['views'] for r in recs])} | "
            f"{avg([r['likes'] for r in recs])} | "
            f"{avg([r['replies'] for r in recs])} |"
        )

    lines += [
        "",
        "## 型別 平均",
        "",
        "| 型 | 件数 | 平均views | 平均likes | 平均replies |",
        "|---|---:|---:|---:|---:|",
    ]
    for type_name, recs in sorted(by_type.items(), key=lambda x: -avg([r["likes"] for r in x[1]])):
        lines.append(
            f"| {type_name} | {len(recs)} | "
            f"{avg([r['views'] for r in recs])} | "
            f"{avg([r['likes'] for r in recs])} | "
            f"{avg([r['replies'] for r in recs])} |"
        )

    # TOP10 / WORST5
    sorted_by_likes = sorted(items_with_metrics, key=lambda it: it["metrics"][-1]["likes"], reverse=True)
    lines += ["", "## いいね TOP 10", ""]
    for it in sorted_by_likes[:10]:
        m = it["metrics"][-1]
        lines.append(
            f"- **{it['title'][:50]}** ／ {it['genre']} ／ {it['type']} "
            f"／ views {m['views']} ／ likes {m['likes']} ／ replies {m['replies']}"
        )

    if len(sorted_by_likes) > 10:
        lines += ["", "## いいね WORST 5（使ったけど伸びなかった）", ""]
        for it in sorted_by_likes[-5:]:
            m = it["metrics"][-1]
            lines.append(
                f"- **{it['title'][:50]}** ／ {it['genre']} ／ {it['type']} "
                f"／ views {m['views']} ／ likes {m['likes']}"
            )

    PERFORMANCE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--account", default="", help="特定アカウントのみ集計（空なら全アカウント）")
    args = p.parse_args()

    if not INDEX_JSON.exists():
        print(f"[sync_metrics] index.json not found: {INDEX_JSON}", file=sys.stderr)
        return 1

    account = args.account or None
    metrics_map = collect_metrics_per_research(account)
    if not metrics_map:
        print("[sync_metrics] 紐付けるメトリクス無し（draft frontmatter に research_used が無いか、まだメトリクス未取得）")
    updated, data = update_index(metrics_map)
    render_performance_md(data)

    total_with_metrics = sum(1 for it in data["items"] if it.get("metrics"))
    print(
        f"[sync_metrics] 紐付け更新: {updated}件 ／ "
        f"INDEXメトリクス保有: {total_with_metrics}/{data['total']}件"
    )
    print(f"[sync_metrics] performance report → {PERFORMANCE_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
