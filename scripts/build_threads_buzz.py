"""バズThreads投稿のリサーチURL集をパースして構造化JSONにする。

入力: 既定 = ~/Downloads/Threadsのリサーチ.md（第1引数で別パス指定可）
出力:
  - .company/research/topics/threads-buzz-urls.md（原本コピー・versioned）
  - .company/research/threads-buzz.json（url/handle/post_id/likes/genre・重複排除・いいね降順）

使い方: python scripts/build_threads_buzz.py [source.md]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import datetime as dt
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

LINE_RE = re.compile(r"(https://www\.threads\.com/@([\w.]+)/post/([\w-]+))（([^）]*)）")
GENRE_RE = re.compile(r"^###\s*(.+?)ジャンル")
LIKES_RE = re.compile(r"([\d,]+)\s*いいね")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else (Path.home() / "Downloads" / "Threadsのリサーチ.md")
    if not src.exists():
        print(f"[buzz] 入力が見つかりません: {src}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    genre: str | None = None
    seen: dict[str, dict] = {}

    for line in text.splitlines():
        h = GENRE_RE.match(line)
        if h:
            g = h.group(1).strip()
            genre = "Claude/AI" if "Claude" in g or "AI" in g else g
            continue
        m = LINE_RE.search(line)
        if not m:
            continue
        url, handle, pid, likestr = m.group(1), m.group(2), m.group(3), m.group(4)
        lm = LIKES_RE.search(likestr)
        likes = int(lm.group(1).replace(",", "")) if lm else None
        cur = seen.get(url)
        if cur is None or (likes or 0) > (cur["likes"] or 0):
            seen[url] = {"url": url, "handle": handle, "post_id": pid, "likes": likes, "genre": genre}

    items = sorted(seen.values(), key=lambda x: (x["likes"] or 0), reverse=True)
    by_genre: dict[str, int] = {}
    for it in items:
        by_genre[it["genre"] or "?"] = by_genre.get(it["genre"] or "?", 0) + 1

    # 原本コピー（versioned）
    dst_md = ROOT / ".company" / "research" / "topics" / "threads-buzz-urls.md"
    dst_md.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(src, dst_md)
    except Exception as e:
        print(f"[buzz] 原本コピー失敗(続行): {e}", file=sys.stderr)

    out = ROOT / ".company" / "research" / "threads-buzz.json"
    data = {
        "generated_at": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)).strftime("%Y-%m-%dT%H:%M:%S+09:00"),
        "source": src.name,
        "count": len(items),
        "by_genre": by_genre,
        "items": items,
    }
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[buzz] {out} count={len(items)} genres={by_genre}")


if __name__ == "__main__":
    main()
