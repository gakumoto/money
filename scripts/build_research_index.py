"""`.company/research/topics/*.md` から `index.json` を自動生成する.

各 topics ファイル内の `### <title>` セクションを 1 エントリとして抽出する。
- 「ソース: <URL>」「型: <型名>」「切り口: 「<...>」」を読み取る
- ジャンルはファイル名のキーワード辞書から自動推定
- 既存 `index.json` があれば status / used_at / used_in を引き継ぐ

人間が手動で集約した `INDEX.md` は触らない（保護）。
Web ビューア（research_viewer.py）が同じ `index.json` を読む。
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / ".company" / "research" / "topics"
INDEX_JSON = ROOT / ".company" / "research" / "index.json"

JST = timezone(timedelta(hours=9))

# ジャンル判定ルール（上から順に評価。先にマッチしたものを採用）
GENRE_RULES: list[tuple[str, str]] = [
    ("note-image", "画像テンプレ"),
    ("ponyo", "Ponyo教材"),
    ("buzz-references", "バズ参考"),
    ("kakuteishinkoku", "副業SE"),
    ("ai-fukugyou", "副業SE"),
    ("se-tenshoku", "副業SE"),
    ("se-fukugyo", "副業SE"),
    ("tenshoku", "副業SE"),
    ("fukugyo", "副業SE"),
    ("shakai", "副業SE"),
    ("engineer", "副業SE"),
    ("se-", "副業SE"),
    ("note-monetize", "note副業"),
    ("note-free-paid", "note副業"),
    ("note-premium", "note副業"),
    ("note-buzz", "note副業"),
    ("note", "note副業"),
    ("threads-deletion", "Threads運用"),
    ("threads-monetize", "Threads運用"),
    ("threads-follower", "Threads運用"),
    ("threads-vs-x", "Threads運用"),
    ("threads-algorithm", "Threads運用"),
    ("threads", "Threads運用"),
    ("ai-indie", "AI開発"),
    ("indie-dev", "AI開発"),
    ("claude", "AI開発"),
    ("chatgpt", "AI開発"),
    ("cursor", "AI開発"),
    ("windsurf", "AI開発"),
    ("sora", "AI開発"),
    ("langchain", "AI開発"),
    ("ai-", "AI開発"),
]

# ファイル名が以下のいずれかで始まる場合はスキップ（テンプレ・古い形式など）
SKIP_PREFIXES = ("_",)

# エントリの title + hook 内容からジャンル推定するキーワード辞書（ファイル名で決まらないとき）
GENRE_KEYWORDS: dict[str, list[str]] = {
    "Threads運用": [
        "threads", "スレッズ", "フォロワー", "リプライ", "インプ", "リーチ",
        "アルゴリズム", "シャドウバン", "凍結", "投稿後", "投稿時間",
    ],
    "note副業": [
        "note", "ノート", "有料記事", "マガジン", "メンバーシップ",
        "クリエイター", "無料エリア", "課金", "売れる",
    ],
    "副業SE": [
        "エンジニア", "se副業", "副業", "確定申告", "転職", "情シス",
        "クラウドワークス", "ランサーズ", "ses", "開業届",
    ],
    "AI開発": [
        "claude", "chatgpt", "cursor", "windsurf", "cline", "vibe coding",
        "anthropic", "openai", "agentic", "個人開発", "indie", "コーディング",
        "プロンプト", "langchain", "mcp", "agent", "sora", "ai動画",
    ],
}


def guess_genre(filename: str, title: str = "", hook: str = "") -> str:
    name = filename.lower()
    for keyword, genre in GENRE_RULES:
        if keyword in name:
            return genre
    # コンテンツベース（タイトル + 切り口から判定）
    text = (title + " " + hook).lower()
    scores: dict[str, int] = {}
    for genre, keywords in GENRE_KEYWORDS.items():
        s = sum(1 for kw in keywords if kw in text)
        if s > 0:
            scores[genre] = s
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "その他"


def _save_entry(
    items: list[dict],
    filename: str,
    title: str | None,
    title_line: int,
    source_url: str | None,
    type_name: str | None,
    hook: str | None,
) -> None:
    """1エントリを items に追加（型が無いものはスキップ）.

    ジャンルはファイル名 + title + hook から推定する。
    """
    if not title or not type_name:
        return
    genre = guess_genre(filename, title, hook or "")
    items.append(
        {
            "id": f"{filename}:{title_line}",
            "title": title,
            "hook": hook or "",
            "type": type_name,
            "genre": genre,
            "source_file": filename,
            "source_line": title_line,
            "source_url": source_url or "",
            "status": "unused",
            "used_at": "",
            "used_in": "",
        }
    )


def _clean(s: str) -> str:
    """前後の Markdown 装飾と空白を除去."""
    return s.strip().strip("*_`").strip().strip("「」\"").strip()


def parse_topic_file(file_path: Path) -> list[dict]:
    """1ファイルから「投稿アイデア」明示ブロックのみを抽出.

    厳格モード: `### <title>` 配下に「投稿アイデア:」ラベルが明示されているエントリだけ採用する。
    これによりリサーチ材料のみのセクション（投稿化されない解説など）は捨てる。
    """
    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    filename = file_path.name

    items: list[dict] = []
    title: str | None = None
    title_line = 0
    source_url: str | None = None
    type_name: str | None = None
    hook: str | None = None
    in_idea_block = False

    url_re = re.compile(r"https?://[^\s)]+")
    type_re = re.compile(r"型:\s*(.+)")
    hook_re = re.compile(r"切り口:\s*(.+)")
    idea_label_re = re.compile(r"^\s*-?\s*\**\s*投稿アイデア\s*[:：]")

    for i, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if raw.startswith("### "):
            _save_entry(items, filename, title, title_line, source_url, type_name, hook)
            title = _clean(raw[4:])
            title_line = i
            source_url = None
            type_name = None
            hook = None
            in_idea_block = False
            continue

        if title is None:
            continue

        if "ソース:" in stripped and source_url is None:
            m = url_re.search(stripped)
            if m:
                source_url = m.group(0)
            continue

        if idea_label_re.match(stripped):
            in_idea_block = True
            continue

        if not in_idea_block:
            continue

        if "型:" in stripped and type_name is None:
            m = type_re.search(stripped)
            if m:
                type_name = _clean(m.group(1))
            continue
        if "切り口:" in stripped and hook is None:
            m = hook_re.search(stripped)
            if m:
                hook = _clean(m.group(1))

    _save_entry(items, filename, title, title_line, source_url, type_name, hook)
    return items


def merge_status(new_items: list[dict], old_items: list[dict]) -> None:
    """既存のステータスを id 一致で引き継ぐ（破壊的に new_items を更新）."""
    old_map = {it["id"]: it for it in old_items}
    for it in new_items:
        old = old_map.get(it["id"])
        if not old:
            continue
        it["status"] = old.get("status", "unused")
        it["used_at"] = old.get("used_at", "")
        it["used_in"] = old.get("used_in", "")


def main() -> int:
    if not TOPICS_DIR.exists():
        print(f"[build_research_index] not found: {TOPICS_DIR}", file=sys.stderr)
        return 1

    all_items: list[dict] = []
    parsed_files = 0
    for f in sorted(TOPICS_DIR.glob("*.md")):
        if any(f.name.startswith(p) for p in SKIP_PREFIXES):
            continue
        try:
            items = parse_topic_file(f)
        except Exception as e:
            print(f"[build_research_index] parse error {f.name}: {e}", file=sys.stderr)
            continue
        all_items.extend(items)
        parsed_files += 1

    old_items: list[dict] = []
    if INDEX_JSON.exists():
        try:
            data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
            old_items = data.get("items", [])
        except Exception:
            pass

    merge_status(all_items, old_items)

    output = {
        "generated": datetime.now(JST).isoformat(),
        "total": len(all_items),
        "items": all_items,
    }
    INDEX_JSON.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    used = sum(1 for it in all_items if it["status"] == "used")
    dropped = sum(1 for it in all_items if it["status"] == "dropped")
    unused = len(all_items) - used - dropped
    print(
        f"[build_research_index] {parsed_files} files → {len(all_items)} items "
        f"(unused {unused} / used {used} / dropped {dropped})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
