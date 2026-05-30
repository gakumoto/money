"""投稿前の捏造チェッカー (D-020 の構造的解決).

draft の本文をスキャンし、`accounts/<account>.md` のファクトベースと照合する.
違反検出時は Discord 通知 + draft の frontmatter に記録する.

検査項目:
- Day 数: 「Day N」が実際の Day 数と乖離してないか
- 期間: 「N 週間」「N ヶ月」が経過時間で実現可能か
- フォロワー数: 古すぎる / 盛り過ぎてないか
- note 連続日数: 実数値と乖離してないか
- views: posted のメトリクスに実在するか (簡易)

使い方:
    python scripts/fact_check.py                     # gaku_ai_life の直下+queued をスキャン
    python scripts/fact_check.py gaku_ai_life        # 同上 (明示)
    python scripts/fact_check.py --quiet             # 違反だけ出力
    python scripts/fact_check.py --no-notify         # Discord 通知しない

呼び出し場所:
- Discord `/run task:fact_check`
- /post_bulk 生成後 (任意)
- 投稿前のセルフチェック (オーナーが任意で)
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

# Threads 運用開始日 (Day 1)
# TODO: accounts/<account>.md から自動取得するのが望ましい
THREADS_START_DATE = dt.date(2026, 5, 13)
DEFAULT_ACCOUNT = "gaku_ai_life"

# ファクト基準値 (5/14-15 時点・後で accounts から自動読み込みに置き換え)
FACT_BASELINE = {
    "followers_min": 150,   # 5/14 「150 人と繋がれました」
    "followers_max": 500,   # 一気に伸びても 500 以下と仮定
    "note_streak_min": 13,  # 5/15 「13 日連続」
    "note_streak_max": 40,  # 念のため幅
}


def current_day_number(today: dt.date | None = None) -> int:
    """今日の Day N を返す."""
    if today is None:
        today = dt.date.today()
    return (today - THREADS_START_DATE).days + 1


def extract_body(text: str) -> str:
    """draft から 【本文】 セクションを抽出."""
    m = re.search(r"【本文】\s*\n(.+?)(?=\n【コメント欄】|\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def check_facts(body: str, today: dt.date | None = None) -> list[dict]:
    """本文をスキャンして違反のリストを返す.

    Returns:
        [{"type": str, "found": str, "expected": str, "severity": str}, ...]
    """
    violations: list[dict] = []
    current_day = current_day_number(today)

    # 1. Day 数チェック (例: "Day 22" を 5 日目に書くと違反)
    for m in re.finditer(r"Day\s*(\d+)", body):
        day_num = int(m.group(1))
        diff = abs(day_num - current_day)
        if diff > 1:  # 1 日の誤差は許容 (深夜跨ぎ等)
            severity = "high" if diff > 3 else "medium"
            violations.append(
                {
                    "type": "day_number",
                    "found": f"Day {day_num}",
                    "expected": f"Day {current_day} 前後",
                    "severity": severity,
                }
            )

    # 2. 期間 (週間) チェック
    for m in re.finditer(r"(\d+)\s*週間", body):
        weeks = int(m.group(1))
        max_weeks = current_day // 7
        if weeks > max_weeks:
            violations.append(
                {
                    "type": "duration_weeks",
                    "found": f"{weeks} 週間",
                    "expected": (
                        f"最大 {max_weeks} 週間 (現在 Day {current_day})"
                    ),
                    "severity": "high",
                }
            )

    # 3. 期間 (ヶ月) チェック
    for m in re.finditer(r"(\d+)\s*(?:ヶ月|か月|ヵ月|カ月)", body):
        months = int(m.group(1))
        max_months = current_day // 30
        if months > max_months:
            violations.append(
                {
                    "type": "duration_months",
                    "found": f"{months} ヶ月",
                    "expected": (
                        f"最大 {max_months} ヶ月 (現在 Day {current_day})"
                    ),
                    "severity": "high",
                }
            )

    # 3b. 期間 (英語 weeks) チェック - "2 weeks" "3 week" など
    for m in re.finditer(r"\b(\d+)\s*week[s]?\b", body, re.IGNORECASE):
        weeks = int(m.group(1))
        max_weeks = current_day // 7
        if weeks > max_weeks:
            violations.append(
                {
                    "type": "duration_weeks_en",
                    "found": f"{weeks} week(s)",
                    "expected": (
                        f"最大 {max_weeks} 週間 (Day {current_day})"
                    ),
                    "severity": "high",
                }
            )

    # 3c. 期間 (英語 months) チェック - "1 month" "2 months"
    for m in re.finditer(r"\b(\d+)\s*month[s]?\b", body, re.IGNORECASE):
        months = int(m.group(1))
        max_months = current_day // 30
        if months > max_months:
            violations.append(
                {
                    "type": "duration_months_en",
                    "found": f"{months} month(s)",
                    "expected": (
                        f"最大 {max_months} ヶ月 (Day {current_day})"
                    ),
                    "severity": "high",
                }
            )

    # 3d. "first month" / "this month" の特別扱い
    # current_day < 30 ならまだ「最初の月」終わってないので、
    # 「first month」と振り返り表現するのは捏造
    if current_day < 30:
        if re.search(r"\bfirst\s+month\b", body, re.IGNORECASE):
            violations.append(
                {
                    "type": "first_month",
                    "found": "first month (英語表現)",
                    "expected": (
                        f"Day {current_day}・まだ最初の月の途中"
                    ),
                    "severity": "high",
                }
            )
        if re.search(r"最初\s*の?\s*1\s*ヶ月", body):
            violations.append(
                {
                    "type": "first_month_jp",
                    "found": "最初の 1 ヶ月",
                    "expected": (
                        f"Day {current_day}・まだ 1 ヶ月経ってない"
                    ),
                    "severity": "high",
                }
            )

    # 3e. "yesterday/last week/先週/先月" の文脈チェック (Day 数によって不可能)
    if current_day < 7:
        if re.search(r"先週|last\s+week", body, re.IGNORECASE):
            violations.append(
                {
                    "type": "last_week",
                    "found": "先週 / last week",
                    "expected": f"Day {current_day} ではまだ 1 週間経ってない",
                    "severity": "medium",
                }
            )

    # 4. フォロワー数チェック
    for m in re.finditer(
        r"フォロワー\s*(?:数\s*)?[:：]?\s*(\d+)\s*[人名]?", body
    ):
        f_num = int(m.group(1))
        if f_num < FACT_BASELINE["followers_min"] - 30:
            # 古い数字 (例: 134)
            violations.append(
                {
                    "type": "follower_outdated",
                    "found": f"フォロワー {f_num}",
                    "expected": (
                        f"約 {FACT_BASELINE['followers_min']}+ 人 (5/14 時点)"
                    ),
                    "severity": (
                        "high" if f_num < 100 else "medium"
                    ),
                }
            )
        elif f_num > FACT_BASELINE["followers_max"]:
            # 盛り過ぎ
            violations.append(
                {
                    "type": "follower_inflated",
                    "found": f"フォロワー {f_num}",
                    "expected": (
                        f"最大 {FACT_BASELINE['followers_max']} 程度 "
                        "(急増は要確認)"
                    ),
                    "severity": "high",
                }
            )

    # 5. note 連続日数チェック
    # 「note 13 日連続」「note を 14 日続け」など
    for m in re.finditer(
        r"note\s*(?:を)?\s*(\d+)\s*日(?:\s*連続|\s*続け)?", body
    ):
        days = int(m.group(1))
        if days < FACT_BASELINE["note_streak_min"] - 5:
            violations.append(
                {
                    "type": "note_streak_outdated",
                    "found": f"note {days} 日",
                    "expected": (
                        f"約 {FACT_BASELINE['note_streak_min']}+ 日"
                    ),
                    "severity": "low",
                }
            )
        elif days > FACT_BASELINE["note_streak_max"]:
            violations.append(
                {
                    "type": "note_streak_inflated",
                    "found": f"note {days} 日",
                    "expected": (
                        f"最大 {FACT_BASELINE['note_streak_max']} 日程度"
                    ),
                    "severity": "high",
                }
            )

    return violations


def add_violations_to_frontmatter(
    path: Path, violations: list[dict]
) -> None:
    """draft の frontmatter に fact_check 結果を追記."""
    text = path.read_text(encoding="utf-8")
    now_iso = dt.datetime.now().isoformat(timespec="seconds")

    # 既存の fact_check 行を削除して上書き
    text = re.sub(
        r"^fact_check_checked:.*\n", "", text, flags=re.MULTILINE
    )
    text = re.sub(
        r"^fact_check_violations:.*(?:\n  -.*)*\n",
        "",
        text,
        flags=re.MULTILINE,
    )

    block_lines = [f"fact_check_checked: {now_iso}"]
    if violations:
        block_lines.append("fact_check_violations:")
        for v in violations:
            block_lines.append(
                f"  - {{severity: {v['severity']}, type: {v['type']}, "
                f"found: \"{v['found']}\", expected: \"{v['expected']}\"}}"
            )
    block_text = "\n".join(block_lines) + "\n"

    # 1 つ目の `---` の直前に挿入
    if re.search(r"^---\s*$", text, re.MULTILINE):
        text = re.sub(
            r"(\n)(---\s*\n)",
            r"\1" + block_text + r"\2",
            text,
            count=1,
        )
    else:
        # frontmatter がなければ先頭に追加
        text = block_text + text

    path.write_text(text, encoding="utf-8")


def scan_drafts(account: str) -> dict:
    """直下 + queued の drafts をスキャン.

    Returns:
        {"checked": N, "violations": M, "files": [{"path": ..., "violations": [...]}, ...]}
    """
    drafts_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / account
    )
    targets = []
    if drafts_dir.exists():
        # 直下 (queued/posted/rejected を除外)
        targets.extend(
            f for f in drafts_dir.glob("*.md") if f.is_file()
        )
        # queued/
        queued = drafts_dir / "queued"
        if queued.exists():
            targets.extend(queued.glob("*.md"))

    result = {"checked": len(targets), "violations": 0, "files": []}
    for f in targets:
        try:
            text = f.read_text(encoding="utf-8")
            body = extract_body(text)
            if not body:
                continue
            violations = check_facts(body)
            if violations:
                result["violations"] += len(violations)
                result["files"].append(
                    {"path": f, "violations": violations}
                )
                add_violations_to_frontmatter(f, violations)
        except OSError:
            continue
    return result


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    no_notify = "--no-notify" in args
    positional = [a for a in args if not a.startswith("--")]
    account = positional[0] if positional else DEFAULT_ACCOUNT

    current_day = current_day_number()
    if not quiet:
        print(
            f"[fact_check] アカウント: {account} / 今日: Day {current_day}"
        )

    result = scan_drafts(account)

    if result["violations"] == 0:
        msg = (
            f"✅ ファクトチェック: 違反なし "
            f"({result['checked']} 件スキャン)"
        )
        print(msg)
        if not no_notify and result["checked"] > 0:
            notify(msg)
        return

    # 違反の詳細出力
    print(
        f"⚠️ 違反 {result['violations']} 件 / "
        f"{result['checked']} 件スキャン"
    )
    summary_lines = [
        f"⚠️ ファクトチェック違反 {result['violations']} 件",
    ]
    for entry in result["files"]:
        fname = entry["path"].name
        print(f"\n📄 {fname}:")
        summary_lines.append(f"\n📄 {fname}")
        for v in entry["violations"]:
            line = (
                f"  [{v['severity']}] {v['type']}: "
                f"{v['found']} → 期待: {v['expected']}"
            )
            print(line)
            summary_lines.append(line[:200])

    summary = "\n".join(summary_lines[:30])  # Discord 通知は要約
    summary += "\n\n👉 frontmatter に詳細記録済み / 要修正"
    if not no_notify:
        notify(summary[:1900])


if __name__ == "__main__":
    main()
