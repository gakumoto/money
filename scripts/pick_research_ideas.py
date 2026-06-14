"""リサーチINDEXから候補ネタをピックして stdout に JSON で出力する.

スキル（threads-create-post / threads-daily-run）が生成前に呼ぶ。
1073 件すべて読み込むのは重いので、フィルタ条件で 20 件ほどに絞る。

使い方:
    python scripts/pick_research_ideas.py --genre Threads --limit 10
    python scripts/pick_research_ideas.py --status unused --exclude-types 朝学び --limit 15

出力: JSON 配列（コンパクトな形式: id, title, hook, type, genre, source_url）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = ROOT / ".company" / "research" / "index.json"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--genre", default="", help="ジャンル部分一致（例: Threads / note / AI）")
    p.add_argument("--type", default="", help="型部分一致（例: 朝学び）")
    p.add_argument("--status", default="unused", help="unused / used / dropped / 空")
    p.add_argument("--exclude-types", default="", help="カンマ区切りで除外する型")
    p.add_argument("--limit", type=int, default=20)
    args = p.parse_args()

    if not INDEX_JSON.exists():
        print(json.dumps({"error": f"index not found: {INDEX_JSON}"}), file=sys.stderr)
        return 1

    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])

    exclude = [t.strip() for t in args.exclude_types.split(",") if t.strip()]

    filtered: list[dict] = []
    for it in items:
        if args.status and it.get("status") != args.status:
            continue
        if args.genre and args.genre not in it.get("genre", ""):
            continue
        if args.type and args.type not in it.get("type", ""):
            continue
        if exclude and any(ex in it.get("type", "") for ex in exclude):
            continue
        filtered.append(it)

    filtered = filtered[: args.limit]
    out = [
        {
            "id": it["id"],
            "title": it["title"],
            "hook": it.get("hook", ""),
            "type": it.get("type", ""),
            "genre": it.get("genre", ""),
            "source_url": it.get("source_url", ""),
        }
        for it in filtered
    ]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
