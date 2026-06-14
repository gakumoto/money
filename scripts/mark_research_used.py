"""リサーチINDEXのエントリのステータスを更新する.

使い方:
    python scripts/mark_research_used.py --id "<id>" --status used --draft <path>
    python scripts/mark_research_used.py --id "<id>" --status dropped
    python scripts/mark_research_used.py --id "<id>" --status unused

`--status used` のときは used_at に今の JST 時刻、used_in に draft パスを記録する。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = ROOT / ".company" / "research" / "index.json"
JST = timezone(timedelta(hours=9))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--status", choices=["used", "dropped", "unused"], default="used")
    p.add_argument("--draft", default="")
    args = p.parse_args()

    if not INDEX_JSON.exists():
        print(f"[mark_research_used] index not found: {INDEX_JSON}", file=sys.stderr)
        return 1

    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])

    target = None
    for it in items:
        if it.get("id") == args.id:
            target = it
            break

    if target is None:
        print(f"[mark_research_used] id not found: {args.id}", file=sys.stderr)
        return 2

    target["status"] = args.status
    if args.status == "used":
        target["used_at"] = datetime.now(JST).isoformat()
        if args.draft:
            target["used_in"] = args.draft
    else:
        target["used_at"] = ""
        target["used_in"] = ""

    INDEX_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[mark_research_used] {args.id} → {args.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
