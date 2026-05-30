"""リサーチ結果 (collect.md) の投稿アイデアを inbox に自動変換.

`.company/research/topics/<date>-collect.md` には Web リサーチで得た
投稿アイデアが大量に含まれているが、`/post_bulk` は inbox/ の個別ネタしか
直接消化しない (D-006). このスクリプトが「投稿アイデア」セクションを
inbox/<ts>_<slug>.md に分解して、AI が個別ネタとして扱える形にする.

使い方:
    python scripts/research_to_inbox.py                        # 最新の collect.md を変換
    python scripts/research_to_inbox.py 2026-05-15-collect.md  # 特定ファイル指定
    python scripts/research_to_inbox.py --dry-run              # 変換せず確認のみ

形式 (collect.md 内の各セクション):
    ## N. <タイトル>
    - ソース: <URL>
    - 投稿アイデア:
      - 型: <型名>
      - 切り口: 「<ネタ本文>」

このうち「切り口」の本文を inbox の `content` として使用.
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
from _discord import notify  # noqa: E402

TOPICS_DIR = PROJECT_ROOT / ".company" / "research" / "topics"
INBOX_DIR = TOPICS_DIR / "inbox"


def find_latest_collect() -> Path | None:
    """最新の <YYYY-MM-DD>-collect.md を返す."""
    if not TOPICS_DIR.exists():
        return None
    candidates = sorted(TOPICS_DIR.glob("*-collect.md"), reverse=True)
    return candidates[0] if candidates else None


def slugify(text: str, max_len: int = 30) -> str:
    """日本語タイトル → 簡易 slug (filesystem-safe)."""
    text = re.sub(r"[\s/\\:*?\"<>|【】「」（）()『』]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "idea"


def parse_ideas(text: str) -> list[dict]:
    """collect.md から投稿アイデアを抽出.

    Returns:
        [{"title": str, "source": str, "type": str, "content": str, "section_num": int}, ...]
    """
    ideas: list[dict] = []

    # 各 ## セクションを切り出し
    sections = re.split(r"^## \d+\.\s+", text, flags=re.MULTILINE)
    section_titles = re.findall(r"^## (\d+)\.\s+(.+)$", text, re.MULTILINE)

    # sections[0] はヘッダ前部分なのでスキップ
    for i, section in enumerate(sections[1:], start=0):
        if i >= len(section_titles):
            break
        section_num, title = section_titles[i]

        # ソース URL
        source_m = re.search(r"- ソース:\s*(\S+)", section)
        source = source_m.group(1) if source_m else ""

        # 投稿アイデア部分を抽出
        idea_m = re.search(
            r"- 投稿アイデア:\s*\n((?:\s+-\s+.+\n)+)",
            section,
            re.MULTILINE,
        )
        if not idea_m:
            continue
        idea_block = idea_m.group(1)

        # 型と切り口を抽出
        type_m = re.search(r"-\s*型:\s*(.+?)$", idea_block, re.MULTILINE)
        cut_m = re.search(
            r"-\s*切り口:\s*[「『]?(.+?)[」』]?\s*$",
            idea_block,
            re.MULTILINE,
        )
        if not cut_m:
            continue

        ideas.append(
            {
                "section_num": int(section_num),
                "title": title.strip(),
                "source": source,
                "type": type_m.group(1).strip() if type_m else "",
                "content": cut_m.group(1).strip(),
            }
        )
    return ideas


def write_to_inbox(idea: dict, collect_filename: str, dry_run: bool = False) -> Path | None:
    """1 つのアイデアを inbox/<ts>_<slug>.md に書き出し."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    slug = slugify(idea["title"])
    fname = f"{ts}_{slug}_s{idea['section_num']}.md"
    fpath = INBOX_DIR / fname

    body = (
        f"---\n"
        f"type: idea\n"
        f"created: {now.isoformat(timespec='seconds')}\n"
        f"category: \"リサーチ\"\n"
        f"source: research_to_inbox\n"
        f"source_collect: {collect_filename}\n"
        f"source_url: {idea.get('source', '')}\n"
        f"source_section: {idea['section_num']}\n"
        f"source_type_hint: \"{idea.get('type', '')}\"\n"
        f"status: unused\n"
        f"used_in: \"\"\n"
        f"used_at: \"\"\n"
        f"---\n\n"
        f"# {idea['title']}\n\n"
        f"{idea['content']}\n"
    )

    if dry_run:
        print(f"  [dry-run] {fname}")
        return None
    fpath.write_text(body, encoding="utf-8")
    return fpath


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    positional = [a for a in args if not a.startswith("--")]

    if positional:
        target_name = positional[0]
        target = TOPICS_DIR / target_name
        if not target.exists():
            print(f"指定ファイルが見つからない: {target}", file=sys.stderr)
            sys.exit(1)
    else:
        target = find_latest_collect()
        if not target:
            print("collect.md が見つからない", file=sys.stderr)
            sys.exit(1)

    print(f"[research_to_inbox] 対象: {target.name}")
    text = target.read_text(encoding="utf-8")
    ideas = parse_ideas(text)
    print(f"[research_to_inbox] 抽出: {len(ideas)} 件の投稿アイデア")

    if dry_run:
        print("(dry-run: ファイル生成スキップ)")
        for idea in ideas[:5]:
            print(f"\n--- セクション {idea['section_num']}: {idea['title']} ---")
            print(f"  型: {idea.get('type', '?')}")
            print(f"  ソース: {idea.get('source', '?')}")
            print(f"  切り口: {idea['content'][:120]}...")
        if len(ideas) > 5:
            print(f"\n... 他 {len(ideas) - 5} 件")
        return

    # 既に同じ source_section のファイルがないか確認 (重複変換防止)
    existing_sections = set()
    for f in INBOX_DIR.glob("*.md"):
        try:
            t = f.read_text(encoding="utf-8")
            m_collect = re.search(r"source_collect:\s*(\S+)", t)
            m_section = re.search(r"source_section:\s*(\d+)", t)
            if m_collect and m_section and m_collect.group(1) == target.name:
                existing_sections.add(int(m_section.group(1)))
        except OSError:
            continue

    written = 0
    skipped = 0
    for idea in ideas:
        if idea["section_num"] in existing_sections:
            skipped += 1
            continue
        result = write_to_inbox(idea, target.name)
        if result:
            written += 1
            print(f"  ✅ {result.name}")

    summary = (
        f"[research_to_inbox] 完了\n"
        f"- 新規 inbox 化: {written} 件\n"
        f"- 重複スキップ: {skipped} 件\n"
        f"- 対象: {target.name}\n"
        f"次の /post_bulk でこれらが自動参照される。"
    )
    print("\n" + summary)
    if written > 0:
        notify(summary)


if __name__ == "__main__":
    main()
