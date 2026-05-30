"""Discord Bot for myCompany.

スマホ→Threads の指示出し / レビューワークフロー専用 Bot。
PC 起動中は常駐。

主要スラッシュコマンド:
  /review        - 未レビュー下書きを一覧 (ボタン付き)
  /post   <text> - 即投稿
  /queue  <text> [time] - キューに入れる (time=HH:MM 今日中 or ISO8601)
  /list          - queued/draft の一覧
  /feedback <text> - feedback 蓄積に追加
  /status        - 現状サマリー
  /sync          - スラッシュコマンドをサーバーに同期 (初回 / 追加時)

ボタン操作:
  ✅ 承認 → queued/ へ移動 + publish_at 自動付与
  ✏️ 編集 → モーダルで本文編集 → 保存
  🔄 再生成 → Claude Code に再生成依頼
  ❌ 却下 → rejected/ へ移動 + 理由メモ

オーナー以外の操作は全てブロック (DISCORD_OWNER_ID で認証)。

起動:
  python scripts/discord_bot.py
"""
from __future__ import annotations

import asyncio
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
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

# --- Config ---
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("DISCORD_OWNER_ID", "0") or 0)
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0") or 0)
REVIEW_CHANNEL_ID = int(os.getenv("DISCORD_REVIEW_CHANNEL_ID", "0") or 0)
DEFAULT_ACCOUNT = "gaku_ai_life"

# gaku_ai_life の 5 投稿時刻枠 (JST)
DEFAULT_SLOTS = ["07:30", "12:30", "18:00", "21:30", "23:00"]


# --- Draft Helpers ---

@dataclass
class Draft:
    path: Path
    account: str
    status: str
    topic: str
    template_type: str
    publish_at: Optional[str]
    main_text: str
    comment_text: str


def parse_draft(path: Path) -> Draft:
    """下書きファイルを Draft オブジェクトに."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        raise ValueError(f"frontmatter なし: {path}")
    fm_str, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_str.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")

    body_match = re.search(r"【本文】\s*\n(.*?)(?=\n【コメント欄】|\Z)", body, re.DOTALL)
    main_text = body_match.group(1).strip() if body_match else body.strip()
    comment_match = re.search(r"【コメント欄】.*?\n(.*)", body, re.DOTALL)
    comment_text = comment_match.group(1).strip() if comment_match else ""

    return Draft(
        path=path,
        account=fm.get("account", DEFAULT_ACCOUNT),
        status=fm.get("status", "draft"),
        topic=fm.get("topic", path.stem),
        template_type=fm.get("template_type", ""),
        publish_at=fm.get("publish_at") or None,
        main_text=main_text,
        comment_text=comment_text,
    )


def scan_unreviewed(account: str = DEFAULT_ACCOUNT) -> list[Draft]:
    """draft 状態の下書きを一覧 (queued/ や posted/ は除外)."""
    drafts_dir = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account
    if not drafts_dir.exists():
        return []
    out = []
    for f in sorted(drafts_dir.glob("*.md")):
        try:
            d = parse_draft(f)
            if d.status == "draft":
                out.append(d)
        except (ValueError, OSError):
            continue
    return out


def scan_queued(account: str = DEFAULT_ACCOUNT) -> list[Draft]:
    """queued/ 内の予約投稿一覧."""
    queued_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "queued"
    )
    if not queued_dir.exists():
        return []
    out = []
    for f in sorted(queued_dir.glob("*.md")):
        try:
            out.append(parse_draft(f))
        except (ValueError, OSError):
            continue
    return out


def assign_next_slot(account: str) -> str:
    """次の空き時刻枠を ISO8601 で返す.

    今日の枠を順に試して、すでに queued に入っているものを除外した
    最初の枠を選ぶ。今日中の枠が全部埋まっていれば翌日の朝枠。
    """
    queued = scan_queued(account)
    used = set()
    for q in queued:
        if q.publish_at:
            try:
                pd = dt.datetime.fromisoformat(q.publish_at.replace("Z", "+00:00"))
                used.add(pd.strftime("%Y-%m-%d %H:%M"))
            except ValueError:
                pass

    now = dt.datetime.now().astimezone()
    for day_offset in (0, 1, 2):
        d = (now + dt.timedelta(days=day_offset)).date()
        for slot in DEFAULT_SLOTS:
            hh, mm = map(int, slot.split(":"))
            cand = dt.datetime.combine(
                d, dt.time(hh, mm), tzinfo=now.tzinfo
            )
            if cand <= now:
                continue
            key = cand.strftime("%Y-%m-%d %H:%M")
            if key in used:
                continue
            return cand.isoformat(timespec="seconds")
    # フォールバック: 1 時間後
    return (now + dt.timedelta(hours=1)).isoformat(timespec="seconds")


def update_draft_text(draft: Draft, new_main: str) -> None:
    """下書きの本文 (【本文】) を書き換えて保存."""
    text = draft.path.read_text(encoding="utf-8")
    new = re.sub(
        r"(【本文】\s*\n)(.*?)(?=\n【コメント欄】|\Z)",
        lambda m: m.group(1) + new_main,
        text,
        count=1,
        flags=re.DOTALL,
    )
    draft.path.write_text(new, encoding="utf-8")


def set_frontmatter(path: Path, key: str, value: str) -> None:
    """frontmatter の指定キーを更新 (存在しなければ追加)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return
    fm = m.group(1)
    if re.search(rf"^{re.escape(key)}:", fm, re.MULTILINE):
        new_fm = re.sub(
            rf"^{re.escape(key)}:.*$",
            f"{key}: {value}",
            fm,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        new_fm = fm + f"\n{key}: {value}"
    text = text[: m.start(1)] + new_fm + text[m.end(1) :]
    path.write_text(text, encoding="utf-8")


def move_to_queued(draft: Draft, publish_at: str) -> Path:
    """draft → queued/ へ移動。publish_at を frontmatter に書き込む."""
    queued_dir = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "drafts"
        / draft.account
        / "queued"
    )
    queued_dir.mkdir(parents=True, exist_ok=True)
    new_path = queued_dir / draft.path.name

    set_frontmatter(draft.path, "status", "queued")
    set_frontmatter(draft.path, "publish_at", publish_at)
    shutil.move(str(draft.path), str(new_path))
    return new_path


def move_to_rejected(draft: Draft, reason: str) -> Path:
    """draft → rejected/ へ移動。理由メモを追加."""
    rejected_dir = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "drafts"
        / draft.account
        / "rejected"
    )
    rejected_dir.mkdir(parents=True, exist_ok=True)
    new_path = rejected_dir / draft.path.name

    set_frontmatter(draft.path, "status", "rejected")
    set_frontmatter(
        draft.path, "rejected_at", dt.datetime.now().isoformat(timespec="seconds")
    )
    set_frontmatter(draft.path, "rejected_reason", reason.replace("\n", " "))
    shutil.move(str(draft.path), str(new_path))
    return new_path


# --- Daily Report Helpers ---

# セクションキー → 表示見出し (日報内の章タイトル)
REPORT_SECTIONS = {
    "kpi": "📊 KPI 速報",
    "done": "✅ 今日やったこと",
    "learn": "📝 学び・気づき",
    "fail": "⚠️ 失敗・つまずき",
    "tomorrow": "🎯 明日の重点",
    "memo": "💭 自由メモ",
}


def report_path(date: dt.date) -> Path:
    """日報のファイルパス."""
    return (
        PROJECT_ROOT
        / ".company"
        / "secretary"
        / "reports"
        / f"{date.isoformat()}.md"
    )


def _count_posted_today(date: dt.date) -> int:
    posted_dir = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "drafts"
        / DEFAULT_ACCOUNT
        / "posted"
    )
    if not posted_dir.exists():
        return 0
    prefix = date.isoformat()
    return sum(1 for _ in posted_dir.glob(f"{prefix}_*.md"))


def ensure_report(date: dt.date) -> Path:
    """指定日の日報ファイルを (なければ) 作成して返す."""
    fpath = report_path(date)
    if fpath.exists():
        return fpath
    fpath.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now()
    posted = _count_posted_today(date)
    queued_count = len(scan_queued())
    body_lines = [
        "---",
        "type: daily-report",
        f"date: {date.isoformat()}",
        "status: open",
        f"created: {now.isoformat(timespec='seconds')}",
        f"updated: {now.isoformat(timespec='seconds')}",
        "---",
        "",
        f"# 日報 {date.isoformat()}",
        "",
        "## 📊 KPI 速報",
        f"- 投稿: {posted} 本",
        f"- キュー残: {queued_count} 本",
        "- フォロワー: ? (起床時に手動更新)",
        "- note 売上: ? 円",
        "",
        "## ✅ 今日やったこと",
        "",
        "## 📝 学び・気づき",
        "",
        "## ⚠️ 失敗・つまずき",
        "",
        "## 🎯 明日の重点",
        "",
        "## 💭 自由メモ",
        "",
    ]
    fpath.write_text("\n".join(body_lines), encoding="utf-8")
    return fpath


def append_to_section(date: dt.date, section_key: str, content: str) -> None:
    """日報の指定セクションに bullet で追記."""
    fpath = ensure_report(date)
    text = fpath.read_text(encoding="utf-8")

    heading = REPORT_SECTIONS.get(section_key)
    if not heading:
        raise ValueError(f"不明なセクション: {section_key}")

    pattern = rf"(## {re.escape(heading)}\n)"
    m = re.search(pattern, text)
    if not m:
        # セクションが無ければ末尾に追加
        text = text.rstrip() + f"\n\n## {heading}\n- {content}\n"
    else:
        insert_at = m.end()
        # セクション内の既存 bullet の末尾を探す (次の ## or EOF)
        next_section = re.search(r"\n## ", text[insert_at:])
        section_end = insert_at + (
            next_section.start() if next_section else len(text) - insert_at
        )
        prefix = text[:section_end].rstrip()
        suffix = text[section_end:]
        ts = dt.datetime.now().strftime("%H:%M")
        text = prefix + f"\n- [{ts}] {content}\n\n" + suffix.lstrip("\n")

    # updated を更新
    text = re.sub(
        r"^updated:.*$",
        f"updated: {dt.datetime.now().isoformat(timespec='seconds')}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    fpath.write_text(text, encoding="utf-8")


def close_report(date: dt.date, comment: Optional[str] = None) -> Path:
    """日報を closed にする."""
    fpath = ensure_report(date)
    text = fpath.read_text(encoding="utf-8")
    text = re.sub(
        r"^status:.*$", "status: closed", text, count=1, flags=re.MULTILINE
    )
    text = re.sub(
        r"^updated:.*$",
        f"updated: {dt.datetime.now().isoformat(timespec='seconds')}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if comment:
        text = text.rstrip() + (
            f"\n\n## 🌙 締めコメント\n\n{comment}\n"
        )
    fpath.write_text(text, encoding="utf-8")
    return fpath


def list_recent_reports(days: int = 7) -> list[dict]:
    """過去 N 日分の日報メタ情報."""
    reports_dir = (
        PROJECT_ROOT / ".company" / "secretary" / "reports"
    )
    if not reports_dir.exists():
        return []
    out: list[dict] = []
    today = dt.date.today()
    for delta in range(days):
        d = today - dt.timedelta(days=delta)
        f = reports_dir / f"{d.isoformat()}.md"
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8")
            status_m = re.search(r"^status:\s*(\w+)", text, re.MULTILINE)
            updated_m = re.search(r"^updated:\s*(.+)$", text, re.MULTILINE)
            out.append(
                {
                    "date": d.isoformat(),
                    "status": status_m.group(1) if status_m else "?",
                    "updated": updated_m.group(1).strip() if updated_m else "?",
                    "path": f,
                }
            )
        except OSError:
            continue
    return out


def generate_ideas_via_claude(
    category: str, count: int
) -> tuple[bool, list[dict], str]:
    """Claude Code にネタ生成依頼。成功なら ideas のリストを返す."""
    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"
    prompt = (
        f"gaku_ai_life の Threads 投稿ネタを {count} 個生成してください。\n\n"
        f"カテゴリヒント: {category or 'なんでも'}\n\n"
        "# 必読ファイル\n"
        "- .company/CLAUDE.md\n"
        "- .company/marketing/CLAUDE.md\n"
        "- .company/marketing/feedback/gaku_ai_life.md\n\n"
        "# 守ること\n"
        "- 危険ワード「収益化」「マネタイズ」「稼ぐ」を売り文句にしない\n"
        "- 当たり訴求公式: (自分は何者か) × (気づき1つ)\n"
        "- ですます基本\n"
        "- 1 ネタ 1〜3 行のショート版でOK (これは投稿本文ではなくネタ素材)\n\n"
        "# 出力フォーマット (厳守・他の説明文は不要)\n"
        "下記の区切りを各ネタの前後に必ず入れてください:\n\n"
        "===IDEA===\n"
        "CATEGORY: <カテゴリ名>\n"
        "CONTENT: <ネタ本文 1〜3 行>\n"
        "===END===\n\n"
        f"{count} 個分繰り返し出力してください。"
    )
    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        if result.returncode != 0:
            return False, [], f"exit={result.returncode}\n{result.stderr[:800]}"
        output = result.stdout
        ideas: list[dict] = []
        for m in re.finditer(
            r"===IDEA===\s*\n(.*?)\n===END===",
            output,
            re.DOTALL,
        ):
            block = m.group(1)
            cat_m = re.search(r"CATEGORY:\s*(.+?)$", block, re.MULTILINE)
            con_m = re.search(
                r"CONTENT:\s*(.+?)(?=\nCATEGORY:|\Z)", block, re.DOTALL
            )
            if cat_m and con_m:
                ideas.append(
                    {
                        "category": cat_m.group(1).strip(),
                        "content": con_m.group(1).strip(),
                    }
                )
        return True, ideas, output[-800:]
    except subprocess.TimeoutExpired:
        return False, [], "タイムアウト (10分)"
    except FileNotFoundError:
        return False, [], f"claude 見つからない: {claude_cmd}"


def generate_posts_via_claude(
    account: str, count: int, theme_hint: str = ""
) -> tuple[bool, str]:
    """Claude Code に投稿下書きを N 本生成依頼.

    /threads-daily-run スキルを利用して N 本生成し、
    .company/marketing/drafts/<account>/ 直下に保存される.
    フィードバック蓄積を必ず読み込ませる.
    """
    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"
    tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
    theme_block = (
        f"\n# テーマ指定（オーナーから）\n{theme_hint}\n" if theme_hint.strip() else ""
    )
    prompt = (
        f"あなたは Threads 投稿生成エージェントです。\n"
        f"`.claude/skills/threads-daily-run/SKILL.md` を読み、その手順に従って\n"
        f"アカウント `{account}` の投稿下書きを **ちょうど {count} 本** 生成してください。\n\n"
        f"# 重要な変更点（SKILL.md の 10 本固定ではない）\n"
        f"- 生成本数: {count} 本（10 本固定ではない）\n"
        f"- 投稿日: {tomorrow} を基準にする。{count} 本が同日 5 投稿枠を超える場合は翌日に繰り上げる\n"
        f"- 保存先: .company/marketing/drafts/{account}/ 直下（queued などのサブフォルダには入れない）\n"
        f"- ファイル名: <YYYY-MM-DD>_NN_<slug>.md（NN は 01 始まりの連番）\n"
        f"- 各下書きの frontmatter に publish_at（ISO8601）と applied_feedback を必ず入れる\n"
        f"{theme_block}\n"
        f"# 必読（生成前にすべて読む・スキップ禁止）\n"
        f"- .company/CLAUDE.md\n"
        f"- .company/marketing/CLAUDE.md\n"
        f"- .company/marketing/feedback/{account}.md  ★最重要・必ず適用\n"
        f"- .company/marketing/accounts/{account}.md  ★★★ファクトベースセクションは絶対遵守★★★\n\n"
        f"# ★ 捏造禁止ルール（最重要・違反したら全本書き直し）\n"
        f"`.company/marketing/accounts/{account}.md` の「ファクトベース」セクションに**書かれた数字・期間・実績だけ**を投稿に使う。\n"
        f"以下は確認できない限り絶対に書かない:\n"
        f"- 「N 週間」「N ヶ月」など期間 → ファクトの「期間・Day 数」セクションを参照\n"
        f"- 「フォロワー X」 → ファクトの最新値か、書かない選択\n"
        f"- 「note 連続投稿 N 日」 → ファクトの最新値\n"
        f"- 「売上 X 円」「収益 X 円」 → ファクトの値\n"
        f"- 「投稿 N 本書いた」「却下 N 本」 → 実投稿数を `posted/` から数えるか、書かない\n"
        f"確認できない数字は **書かない** が正解 (盛らない・推測で書かない)。\n"
        f"違反例: 「2 週間悩んだ」(実際 4 日)、「Day 22」(実際 Day 4)、「フォロワー 134」(実際 150 超え)\n\n"
        f"# リサーチ結果とネタの活用（★必須・2026-05-15 強化）\n"
        f"以下を**生成前に必ずすべて読む**:\n"
        f"\n"
        f"## A. inbox の個別ネタ\n"
        f"- `.company/research/topics/inbox/` 配下の **status: unused** のネタ\n"
        f"- Glob で `inbox/*.md` を列挙\n"
        f"- 最低 {min(count, 3)} 本は活用して生成元にする\n"
        f"- 使ったネタは frontmatter `status: unused` → `status: used` に書き換え + `used_at` 追記\n"
        f"- 生成下書きに `used_idea_ids: [\"<stem>\", ...]` を記録\n"
        f"\n"
        f"## B. 直下のリサーチ結果 (★最重要・本日強化)\n"
        f"- `.company/research/topics/YYYY-MM-DD-collect.md` (Web トレンド最新)\n"
        f"- `.company/research/topics/youtube-YYYY-MM-DD.md` (YouTube 字幕 + 抽出ネタ・**大きい場合は末尾の「要約・投稿ネタ抽出」セクションだけ読む**)\n"
        f"- `.company/research/topics/post-pattern-YYYY-MM.md` (自己投稿分析・伸びた要因)\n"
        f"- これらは **inbox とは別の大きな知見ソース**。最新ファイルから抽出した\n"
        f"  - Web の旬な話題\n"
        f"  - 同業者の伸びてる切り口\n"
        f"  - 自分の過去で伸びた型\n"
        f"  を {count} 本中 **最低 {min(count, 2)} 本** に反映する\n"
        f"\n"
        f"## C. 競合の手本 (feedback の「他者の良かった例」)\n"
        f"- `feedback/{account}.md` の「他者の良かった例」セクション\n"
        f"- オーナーが手動登録した同業者の伸びてる投稿\n"
        f"- ここの型・トーンを {count} 本中 1〜2 本に取り入れる\n"
        f"\n"
        f"同テーマで重複しないよう、ネタ・リサーチ結果のうち多様な切り口を選ぶ。\n\n"
        f"# ★ 多様性を保つルール（最重要・画一化防止 2026-05-15 追加）\n"
        f"1. 生成前に必ず `.company/marketing/drafts/{account}/posted/` 配下の **直近 14 日の投稿を全部読む**\n"
        f"2. 各 posted の **冒頭 1 行** を抽出し、同じ語頭パターンを連発しない\n"
        f"   - 例: 「フォロワー○○、駆け出しSEのぼくが〜」を直近で使ってたら今回避ける\n"
        f"   - 例: 「○○ですか？」を 5 本中 3 本使ったら、今回は 1 本まで\n"
        f"3. `feedback/{account}.md` の **「冒頭1行のバリエーション集」A〜H** を必ず読み、\n"
        f"   {count} 本中 **最低 {min(count, 5)} 種類** を使い分けて生成する\n"
        f"   (A=数字先行 / B=シーン / C=失敗オープン / D=質問 / E=対比逆張り / F=引用 / G=未完型 / H=動作観察)\n"
        f"4. **★★★★★ 手本投稿の冒頭パターンは {count} 本中 1 本まで** (連発で飽きられる)\n"
        f"5. 数字を入れる時は「134 / 2日 / 3週間」などの定型ばかり使わない。\n"
        f"   時間 / 金額 / 人数 / 回数 / 期間 / 距離 / 容量 など **多様な単位を混ぜる**\n"
        f"6. テーマ分散: 「AI / 副業 / SE」の三角形に閉じない。\n"
        f"   {count} 本中 **最低 {max(1, count // 3)} 本** は日常 / 本 / 家族 / 散歩 / 食事 / 趣味 / 観察を含む\n"
        f"7. 各下書きの frontmatter に **`hook_pattern: A`** (使った冒頭型) を記録\n\n"
        f"# 必ず守るルール\n"
        f"- 「〜かもしれません」NG → 断定\n"
        f"- 「皆さん」NG → 主語なし問いかけ or 「あなた / 君」\n"
        f"- 装飾絵文字 (🔥✨🙌) NG / 思考系 (🤔😅😌) は文末 1 個まで\n"
        f"- 危険ワード「月100万」「月7桁」「収益化」「マネタイズ」を売り文句として連発しない\n"
        f"- 冒頭 1 行に固有名詞 + 数字 + ターゲット\n"
        f"- 本文に体験談 / 具体数字 / 弱さ開示\n"
        f"- 末尾は断定 or 問いかけ\n"
        f"- 同テーマを 2 本以上含めない\n\n"
        f"# 出力\n"
        f"全 {count} 本を保存後、ファイル名一覧と各冒頭 1 行を報告してください。"
        f"使ったネタの id 一覧も末尾に列挙してください。"
    )
    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,  # 30分 (10本生成で 2-5 分の想定)
        )
        # 詳細ログを残す（generate_ideas 同様、デバッグ用）
        log_dir = SCRIPT_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        (log_dir / f"post_bulk_{ts}.log").write_text(
            f"=== CMD ===\n{' '.join(cmd[:3])} ...\n\n"
            f"=== EXIT ===\n{result.returncode}\n\n"
            f"=== STDOUT ===\n{result.stdout}\n\n"
            f"=== STDERR ===\n{result.stderr}\n",
            encoding="utf-8",
        )
        if result.returncode != 0:
            return False, f"exit={result.returncode}\n{result.stderr[:800]}"
        return True, result.stdout[-2000:]
    except subprocess.TimeoutExpired:
        return False, "タイムアウト (30分)"
    except FileNotFoundError:
        return False, f"claude 見つからない: {claude_cmd}"


def append_idea(
    content: str, category: str = "", source: str = "discord_bot"
) -> Path:
    """投稿ネタを research/topics/inbox/ に追加."""
    inbox = PROJECT_ROOT / ".company" / "research" / "topics" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    raw = content.strip()[:24]
    slug = re.sub(r"[\s/\\:*?\"<>|]+", "-", raw).strip("-")
    if not slug:
        slug = "idea"
    fname = f"{ts}_{slug}.md"
    fpath = inbox / fname
    body = (
        f"---\n"
        f"type: idea\n"
        f"created: {now.isoformat(timespec='seconds')}\n"
        f'category: "{category}"\n'
        f"source: {source}\n"
        f"status: unused\n"
        f"---\n\n{content}\n"
    )
    fpath.write_text(body, encoding="utf-8")
    return fpath


def scan_ideas(
    category: Optional[str] = None, status: str = "unused"
) -> list[dict]:
    """ネタ一覧 (新しい順)."""
    inbox = PROJECT_ROOT / ".company" / "research" / "topics" / "inbox"
    if not inbox.exists():
        return []
    out: list[dict] = []
    for f in sorted(inbox.glob("*.md"), reverse=True):
        try:
            text = f.read_text(encoding="utf-8")
            m = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
            if not m:
                continue
            fm_str, body = m.group(1), m.group(2).strip()
            fm: dict = {}
            for line in fm_str.splitlines():
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
            if fm.get("status", "unused") != status:
                continue
            if category and fm.get("category", "") != category:
                continue
            out.append(
                {
                    "id": f.stem,
                    "category": fm.get("category", ""),
                    "content": body,
                    "created": fm.get("created", ""),
                    "path": f,
                }
            )
        except (ValueError, OSError):
            continue
    return out


def append_feedback(category: str, content: str) -> None:
    """feedback/gaku_ai_life.md に追記."""
    fb_path = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "feedback"
        / "gaku_ai_life.md"
    )
    if not fb_path.exists():
        return
    ts = dt.datetime.now().isoformat(timespec="seconds")
    entry = (
        f"\n\n### {ts} - Discord 経由フィードバック\n"
        f"- カテゴリ: {category}\n"
        f"- 内容: {content}\n"
    )
    with fb_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def regenerate_via_claude(draft: Draft, feedback: str) -> tuple[bool, str]:
    """Claude Code ヘッドレスで再生成依頼。

    フィードバック反映を最優先にした強い指示プロンプトを送り、
    実行後に「ファイルが実際に書き換わったか」を mtime と本文ハッシュで検証する。
    変更が検出されなければ False を返す (=「成功した気になるだけ」を防ぐ)。
    """
    import hashlib

    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"

    # 実行前のスナップショット (変更検証用)
    try:
        before_text = draft.path.read_text(encoding="utf-8")
        before_mtime = draft.path.stat().st_mtime
        before_hash = hashlib.sha1(before_text.encode("utf-8")).hexdigest()
    except OSError as e:
        return False, f"既存ファイルが読めない: {e}"

    prompt = (
        "あなたは Threads 投稿の書き直しエージェントです。\n\n"
        "# タスク\n"
        f"既存の下書きファイル `{draft.path}` の **【本文】セクションだけ** を、"
        "下記フィードバックを **必ず反映** して書き直してください。"
        "frontmatter (--- で囲まれた部分) は維持し、本文以外は変更しません。\n\n"
        "# フィードバック (最重要・必ずすべて反映する)\n"
        f"{feedback}\n\n"
        "# 既存下書きの情報\n"
        f"- account: {draft.account}\n"
        f"- topic: {draft.topic}\n"
        f"- template_type: {draft.template_type}\n\n"
        "# 必読 (生成前にすべて読む・スキップ禁止)\n"
        "- `.company/CLAUDE.md`\n"
        "- `.company/marketing/CLAUDE.md`\n"
        f"- `.company/marketing/feedback/{draft.account}.md`  ★最重要\n"
        f"- 既存下書き全文 (`{draft.path}`)\n\n"
        "# 守るルール\n"
        "- 「〜かもしれません」NG → 断定\n"
        "- 「皆さん」NG → 主語なし問いかけ\n"
        "- 装飾絵文字 (🔥✨🙌) NG / 思考系 (🤔😅😌) は文末 1 個まで\n"
        "- 危険ワード「月100万」「収益化」「マネタイズ」を売り文句として連発しない\n"
        "- 冒頭 1 行に固有名詞 + 数字 + ターゲット\n"
        "- 末尾は断定 or 問いかけ\n\n"
        "# 実行手順 (必ずこの順番で)\n"
        "1. 上記必読ファイルをすべて読む\n"
        "2. 既存下書きを Read で読み込み、frontmatter と本文を把握\n"
        f"3. **Edit ツールで `{draft.path}` の【本文】セクションを書き換える**\n"
        "4. frontmatter の `applied_feedback` に今回のフィードバック要点を追記\n"
        "5. 完了したら『書き換え完了。変更点: <要約>』を最後に出力\n\n"
        "**新規ファイルを作るのではなく、既存ファイルを Edit で書き換えてください。**"
    )

    # 詳細ログ用パス (毎回保存・デバッグ可)
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"regenerate_{ts}.log"

    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        # 詳細ログを全文保存 (フィードバックが反映されないバグ追跡用)
        try:
            log_path.write_text(
                f"=== FEEDBACK ===\n{feedback}\n\n"
                f"=== TARGET FILE ===\n{draft.path}\n\n"
                f"=== EXIT ===\n{result.returncode}\n\n"
                f"=== STDOUT ===\n{result.stdout}\n\n"
                f"=== STDERR ===\n{result.stderr}\n",
                encoding="utf-8",
            )
        except OSError:
            pass

        if result.returncode != 0:
            return False, (
                f"exit={result.returncode}\n{result.stderr[:500]}\n"
                f"詳細: {log_path}"
            )

        # ★ 実際にファイルが書き換わったか検証 (= 「成功した気になる」防止)
        try:
            after_text = draft.path.read_text(encoding="utf-8")
            after_hash = hashlib.sha1(after_text.encode("utf-8")).hexdigest()
            if after_hash == before_hash:
                return False, (
                    "⚠️ Claude は exit=0 で返ったが、ファイルが変更されていません。\n"
                    "フィードバックが反映されなかった可能性が高いです。\n"
                    f"詳細ログ: {log_path}\n"
                    "プロンプトを見直すか、ヘッドレスモードの挙動を確認してください。"
                )
        except OSError:
            pass

        return True, f"{result.stdout[-500:]}\n詳細ログ: {log_path}"
    except subprocess.TimeoutExpired:
        return False, "タイムアウト (10分)"
    except FileNotFoundError:
        return False, f"claude 見つからない: {claude_cmd}"


# --- UI Components ---


class ReviewView(discord.ui.View):
    """1 下書きにつき 1 つ表示するボタン群."""

    def __init__(self, draft: Draft, *, timeout: float = 60 * 60 * 24):
        super().__init__(timeout=timeout)
        self.draft = draft

    async def _ensure_owner(self, interaction: discord.Interaction) -> bool:
        if OWNER_ID and interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "オーナー以外は操作できません。", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="✅ 承認", style=discord.ButtonStyle.success)
    async def approve(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await self._ensure_owner(interaction):
            return
        try:
            slot = assign_next_slot(self.draft.account)
            new_path = move_to_queued(self.draft, slot)
            for c in self.children:
                c.disabled = True
            await interaction.response.edit_message(
                content=(
                    f"✅ 承認しました\n"
                    f"次の投稿時刻: `{slot}`\n"
                    f"ファイル: `{new_path.name}`"
                ),
                view=self,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"承認失敗: {e}", ephemeral=True
            )

    @discord.ui.button(label="✏️ 編集", style=discord.ButtonStyle.primary)
    async def edit(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await self._ensure_owner(interaction):
            return
        await interaction.response.send_modal(EditModal(self.draft, self))

    @discord.ui.button(label="🔄 再生成", style=discord.ButtonStyle.secondary)
    async def regenerate(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await self._ensure_owner(interaction):
            return
        await interaction.response.send_modal(RegenerateModal(self.draft, self))

    @discord.ui.button(label="❌ 却下", style=discord.ButtonStyle.danger)
    async def reject(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await self._ensure_owner(interaction):
            return
        await interaction.response.send_modal(RejectModal(self.draft, self))


class EditModal(discord.ui.Modal, title="本文を編集"):
    new_text = discord.ui.TextInput(
        label="本文 (500 字以内)",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
    )

    def __init__(self, draft: Draft, parent_view: ReviewView):
        super().__init__()
        self.draft = draft
        self.parent_view = parent_view
        self.new_text.default = draft.main_text[:500]

    async def on_submit(self, interaction: discord.Interaction):
        try:
            update_draft_text(self.draft, str(self.new_text.value).strip())
            # 編集を学習データに残す
            append_feedback(
                "本文編集 (Discord)",
                f"トピック『{self.draft.topic}』を Discord で編集。"
                f"編集前→後の diff は drafts/posted の対応ファイルで確認可能。",
            )
            # 表示更新
            self.draft.main_text = str(self.new_text.value).strip()
            embed = build_draft_embed(self.draft)
            await interaction.response.edit_message(
                content="✏️ 編集を保存しました。確認して承認してください。",
                embed=embed,
                view=self.parent_view,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"編集失敗: {e}", ephemeral=True
            )


class RegenerateModal(discord.ui.Modal, title="再生成の指示"):
    feedback = discord.ui.TextInput(
        label="どこをどう直してほしいか (具体的に)",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
        placeholder="例: 冒頭1行に固有名詞と数字を入れて。当たり訴求公式に沿わせて",
    )

    def __init__(self, draft: Draft, parent_view: ReviewView):
        super().__init__()
        self.draft = draft
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        feedback_text = str(self.feedback.value).strip()
        # 再生成と並行して、与えたフィードバックを蓄積に追加
        # (次回以降の生成でも効くように・1回の操作で「修正+学習」を両立)
        try:
            append_feedback(
                "再生成 (Discord)",
                f"トピック『{self.draft.topic}』への再生成指示: {feedback_text}",
            )
        except Exception as e:
            print(f"[regenerate] feedback 蓄積失敗 (続行): {e}", file=sys.stderr)

        ok, log = regenerate_via_claude(self.draft, feedback_text)
        if ok:
            # 再パース
            try:
                new_draft = parse_draft(self.draft.path)
                self.parent_view.draft = new_draft
                embed = build_draft_embed(new_draft)
                await interaction.followup.send(
                    content=(
                        "🔄 再生成完了。確認して承認してください。\n"
                        "💾 与えたフィードバックは `feedback/` 蓄積に追加済み。"
                    ),
                    embed=embed,
                    view=self.parent_view,
                )
            except Exception as e:
                await interaction.followup.send(f"再生成は走ったがパース失敗: {e}")
        else:
            await interaction.followup.send(
                f"❌ 再生成失敗 (フィードバックは蓄積に追加済み):\n```{log[:1500]}```"
            )


class RejectModal(discord.ui.Modal, title="却下の理由"):
    reason = discord.ui.TextInput(
        label="却下の理由 (フィードバック蓄積に追加されます)",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=True,
    )

    def __init__(self, draft: Draft, parent_view: ReviewView):
        super().__init__()
        self.draft = draft
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_path = move_to_rejected(self.draft, str(self.reason.value))
            append_feedback("却下 (Discord)", str(self.reason.value))
            for c in self.parent_view.children:
                c.disabled = True
            await interaction.response.edit_message(
                content=(
                    f"❌ 却下しました\n"
                    f"理由: {self.reason.value}\n"
                    f"ファイル: `{new_path.name}` (rejected/)"
                ),
                view=self.parent_view,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"却下失敗: {e}", ephemeral=True
            )


def build_draft_embed(draft: Draft) -> discord.Embed:
    """下書き 1 件を Embed 化."""
    embed = discord.Embed(
        title=f"📝 {draft.topic}",
        description=draft.main_text[:1000]
        + ("\n…" if len(draft.main_text) > 1000 else ""),
        color=0x4A90E2,
    )
    embed.add_field(
        name="アカウント / 型",
        value=f"{draft.account} / {draft.template_type or '-'}",
        inline=True,
    )
    embed.add_field(
        name="文字数", value=f"{len(draft.main_text)} 字", inline=True
    )
    if draft.comment_text:
        embed.add_field(
            name="コメント欄あり",
            value=draft.comment_text[:200],
            inline=False,
        )
    embed.set_footer(text=str(draft.path.name))
    return embed


# --- Bot Setup ---


class MyCompanyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()


bot = MyCompanyBot()


@bot.event
async def on_ready():
    print(f"[bot] ログイン: {bot.user} (id={bot.user.id})")
    # 起動時に slash commands を自動 sync (新コマンド追加後の手動 /sync を不要に)
    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
        else:
            synced = await bot.tree.sync()
        print(f"[bot] auto-sync: {len(synced)} コマンド")
    except Exception as e:
        print(f"[bot] auto-sync 失敗: {e}", file=sys.stderr)
    notify(f"[myCompany Bot] 起動完了: {bot.user}")


# --- Slash Commands ---


@bot.tree.command(name="status", description="myCompany の現状サマリーを表示")
async def cmd_status(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    unreviewed = scan_unreviewed()
    queued = scan_queued()
    posted_today = 0
    posted_dir = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "drafts"
        / DEFAULT_ACCOUNT
        / "posted"
    )
    if posted_dir.exists():
        today = dt.date.today().isoformat()
        posted_today = sum(1 for _ in posted_dir.glob(f"{today}_*.md"))

    embed = discord.Embed(title="📊 myCompany 現状", color=0x2ECC71)
    embed.add_field(name="未レビュー下書き", value=f"{len(unreviewed)} 本", inline=True)
    embed.add_field(name="キュー待ち", value=f"{len(queued)} 本", inline=True)
    embed.add_field(name="本日投稿済み", value=f"{posted_today} 本", inline=True)
    if queued:
        next_q = sorted(
            queued, key=lambda d: d.publish_at or "9999"
        )[0]
        embed.add_field(
            name="次の投稿予定",
            value=f"{next_q.publish_at or '未定'}\n{next_q.topic[:50]}",
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="review", description="未レビューの下書きを表示")
@app_commands.describe(account="アカウント名 (省略時 gaku_ai_life)")
async def cmd_review(
    interaction: discord.Interaction, account: Optional[str] = None
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    acc = account or DEFAULT_ACCOUNT
    drafts = scan_unreviewed(acc)
    if not drafts:
        await interaction.response.send_message(
            f"未レビューの下書きはありません ({acc})", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"📥 未レビュー {len(drafts)} 本 ({acc}) ---",
        ephemeral=True,
    )
    for d in drafts[:10]:
        await interaction.followup.send(
            embed=build_draft_embed(d),
            view=ReviewView(d),
            ephemeral=True,
        )


@bot.tree.command(name="post", description="即時投稿 (オーナーのみ)")
@app_commands.describe(text="投稿本文 (500字以内)")
async def cmd_post(interaction: discord.Interaction, text: str):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    if len(text) > 500:
        await interaction.response.send_message(
            f"500 字超え ({len(text)}字)。短くしてください。", ephemeral=True
        )
        return
    await interaction.response.defer(thinking=True, ephemeral=True)
    try:
        client = ThreadsClient.from_env(account=DEFAULT_ACCOUNT)
        media_id = client.create_text_post(text)
        await interaction.followup.send(
            f"✅ 投稿成功 (media_id={media_id})\n```{text[:200]}```",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.followup.send(f"❌ 失敗: {e}", ephemeral=True)


@bot.tree.command(name="queue", description="下書きをキューに追加 (時刻指定可・画像添付/URL対応)")
@app_commands.describe(
    text="本文 (500字以内)",
    time="HH:MM (今日) or ISO8601。省略時は次の空き枠",
    image="画像を直接添付 (スマホのスクショ等・JPEG/PNG・8MB以下)",
    image_url="画像URL (任意・添付がない時に外部URLを指定する場合)",
)
async def cmd_queue(
    interaction: discord.Interaction,
    text: str,
    time: Optional[str] = None,
    image: Optional[discord.Attachment] = None,
    image_url: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    if len(text) > 500:
        await interaction.response.send_message(
            f"500 字超え ({len(text)}字)。", ephemeral=True
        )
        return

    # publish_at を決める
    if time:
        try:
            if re.fullmatch(r"\d{2}:\d{2}", time):
                hh, mm = map(int, time.split(":"))
                now = dt.datetime.now().astimezone()
                cand = dt.datetime.combine(
                    now.date(), dt.time(hh, mm), tzinfo=now.tzinfo
                )
                if cand <= now:
                    cand += dt.timedelta(days=1)
                publish_at = cand.isoformat(timespec="seconds")
            else:
                pd = dt.datetime.fromisoformat(time.replace("Z", "+00:00"))
                publish_at = pd.isoformat(timespec="seconds")
        except ValueError:
            await interaction.response.send_message(
                f"時刻パース失敗: {time}", ephemeral=True
            )
            return
    else:
        publish_at = assign_next_slot(DEFAULT_ACCOUNT)

    # ファイルを queued/ に直接作る
    queued_dir = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "drafts"
        / DEFAULT_ACCOUNT
        / "queued"
    )
    queued_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    fname = f"{ts}_discord-queue.md"
    fpath = queued_dir / fname

    # 添付画像があれば優先 (Discord CDN URL を使用)
    # Discord CDN は永続性あり、Threads API も問題なく取得できる
    effective_image_url = ""
    if image is not None:
        # 形式チェック
        if image.content_type and not image.content_type.startswith("image/"):
            await interaction.response.send_message(
                f"添付ファイルが画像ではありません: {image.content_type}",
                ephemeral=True,
            )
            return
        # サイズチェック (Threads は 8MB まで)
        if image.size and image.size > 8 * 1024 * 1024:
            await interaction.response.send_message(
                f"画像が大きすぎます ({image.size / 1024 / 1024:.1f}MB > 8MB)",
                ephemeral=True,
            )
            return
        effective_image_url = image.url
    elif image_url:
        effective_image_url = image_url.strip()

    image_line = f'image_url: "{effective_image_url}"\n' if effective_image_url else ""
    content = (
        f"---\n"
        f"topic: \"Discord手動キュー\"\n"
        f"status: queued\n"
        f"template_type: \"discord-manual\"\n"
        f"account: \"{DEFAULT_ACCOUNT}\"\n"
        f"created_at: {dt.date.today().isoformat()}\n"
        f"publish_at: {publish_at}\n"
        f"{image_line}"
        f"source: discord_bot\n"
        f"---\n\n【本文】\n{text}\n"
    )
    fpath.write_text(content, encoding="utf-8")

    msg_lines = [
        f"✅ キュー追加",
        f"投稿予定: `{publish_at}`",
        f"ファイル: `{fname}`",
    ]
    if effective_image_url:
        if image is not None:
            msg_lines.append(f"🖼️ 画像添付済み: `{image.filename}` ({image.size // 1024} KB)")
        else:
            msg_lines.append(f"🖼️ 画像URL: `{effective_image_url[:80]}`")
    await interaction.response.send_message("\n".join(msg_lines), ephemeral=True)


@bot.tree.command(name="list", description="キュー一覧")
async def cmd_list(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    queued = sorted(
        scan_queued(), key=lambda d: d.publish_at or "9999"
    )
    if not queued:
        await interaction.response.send_message(
            "キューは空です。", ephemeral=True
        )
        return
    lines = ["📋 キュー (publish_at 順)"]
    for d in queued[:20]:
        lines.append(
            f"- `{d.publish_at or '時刻未定'}` : {d.topic[:40]} ({d.path.name})"
        )
    await interaction.response.send_message(
        "\n".join(lines), ephemeral=True
    )


@bot.tree.command(name="feedback", description="フィードバック蓄積に追加")
@app_commands.describe(
    category="カテゴリ (例: 冒頭1行 / 本文 / 末尾 / リスク)",
    content="具体的なフィードバック",
)
async def cmd_feedback(
    interaction: discord.Interaction, category: str, content: str
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    try:
        append_feedback(category, content)
        await interaction.response.send_message(
            f"✅ feedback/gaku_ai_life.md に追加しました\n"
            f"カテゴリ: {category}\n"
            f"内容: {content[:100]}",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(f"失敗: {e}", ephemeral=True)


@bot.tree.command(name="help", description="myCompany Bot の使い方ガイド")
@app_commands.describe(
    topic="詳細を見たい項目 (省略時は全体ガイド)"
)
@app_commands.choices(
    topic=[
        app_commands.Choice(name="基本コマンド", value="commands"),
        app_commands.Choice(name="レビューフロー", value="review"),
        app_commands.Choice(name="ネタ蓄積", value="ideas"),
        app_commands.Choice(name="日報管理", value="report"),
        app_commands.Choice(name="朝のフロー (理想形)", value="morning"),
        app_commands.Choice(name="ライティングルール", value="rules"),
        app_commands.Choice(name="削除リスク対策", value="risk"),
        app_commands.Choice(name="PC 24時間稼働設定", value="always_on"),
        app_commands.Choice(name="トラブル対処", value="troubleshoot"),
    ]
)
async def cmd_help(
    interaction: discord.Interaction,
    topic: Optional[app_commands.Choice[str]] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    if topic is None:
        # 全体ガイド
        embed = discord.Embed(
            title="📖 myCompany Bot 使い方ガイド",
            description=(
                "スマホから Threads 運用を完結させる Bot です。\n"
                "詳細は `/help <topic>` で項目を選んでください。"
            ),
            color=0x4A90E2,
        )
        embed.add_field(
            name="🔧 基本コマンド",
            value=(
                "`/review` - 未レビュー下書きをボタン付きで表示\n"
                "`/post_bulk` - AI に投稿を N 本まとめて生成\n"
                "`/create_post <topic>` - **単発1本生成 (テーマ/型/目的明示)**\n"
                "`/create_post_from_idea <id>` - **inbox のネタを消化して1本生成**\n"
                "`/post` - 即時投稿\n"
                "`/queue` - キュー追加 (時刻指定可・画像添付対応)\n"
                "`/list` - キュー一覧\n"
                "`/feedback` - 蓄積に追加\n"
                "`/status` - 現状サマリー"
            ),
            inline=False,
        )
        embed.add_field(
            name="🌅 朝の運用",
            value=(
                "`/morning` - 朝礼ダッシュボード (昨日の結果 + 今日の予定 + 推奨アクション)"
            ),
            inline=False,
        )
        embed.add_field(
            name="💬 Claude への直接指示",
            value=(
                "`/ask <message>` - **Claude にスマホから自由に指示。**\n"
                "ファイル変更 / 設計判断 / 分析を別 Claude が実行 (1〜10分)\n"
                "やり取りは inbox/ に永続化 → 次回の文脈として参照"
            ),
            inline=False,
        )
        embed.add_field(
            name="📚 投稿の型・フック集 (新)",
            value=(
                "`/hooks` - 冒頭バリエーション集 A〜H を一覧\n"
                "`/hooks A` - A 型の例 4 つ詳細\n"
                "`/hooks random` - **ランダム 1 つ提案 (思いつき即投稿のとっかかり)**"
            ),
            inline=False,
        )
        embed.add_field(
            name="🚨 リカバリ・運用",
            value=(
                "`/retry_post` - 自動投稿失敗時のリカバリ\n"
                "`/run task:metrics` - メトリクス即取得 + feedback 自動学習\n"
                "`/run task:nightly` - 夜パイプライン即実行\n"
                "`/run task:token_refresh` - Threadsトークン即更新\n"
                "`/run task:watchlist` - 自動リサーチ即実行\n"
                "`/sync` - コマンド再同期"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔬 リサーチ",
            value=(
                "`/research_youtube <url> [count]` - YouTube から字幕→要約→投稿ネタ\n"
                "`/research_web [theme]` - WebSearch で最新トレンド収集\n"
                "`/research_self` - 自分の過去投稿の数字分析 (伸びた要因)\n"
                "`/competitor_post <user> <text> <why>` - 他人の伸びてる投稿を登録 → AI 学習素材化\n"
                "`/watchlist` - 自動リサーチ対象の確認"
            ),
            inline=False,
        )
        embed.add_field(
            name="📝 note 連載 (新)",
            value=(
                "`/generate_article [date]` - **日報・意思決定ログから note 記事を自動生成 (3000〜5000字)**\n"
                "→ 開発しながら note の素材が同時にできるループ完成"
            ),
            inline=False,
        )
        embed.add_field(
            name="💡 ネタ蓄積 (/help ネタ蓄積)",
            value=(
                "`/idea <content>` - 思いつきを inbox に保存\n"
                "`/ideas` - ためたネタ一覧\n"
                "`/idea_use <id>` - 使用済みマーク\n"
                "`/generate_ideas` - AI にネタを N 本生成させる"
            ),
            inline=False,
        )
        embed.add_field(
            name="📓 日報管理 (/help 日報管理)",
            value=(
                "`/report` - 今日の日報を表示 (なければ作成)\n"
                "`/report_add <section> <content>` - セクション追記\n"
                "`/report_close [comment]` - 今日の日報を締める\n"
                "`/reports` - 過去 7 日の日報一覧"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎯 朝のフロー",
            value=(
                "02:00 AI が下書き 10 本生成\n"
                "→ Discord に「下書きできました」通知\n"
                "→ `/review` でボタン捌き\n"
                "→ 07:30 から自動投稿開始\n"
                "💡 日中も `/post_bulk count:N theme:〇〇` で随時追加生成OK。"
                "フィードバック蓄積を毎回読み込むので、書き足すほど精度UP。"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚠️ 守ること (詳細は /help risk)",
            value=(
                "・「収益化」「マネタイズ」「稼ぐ」を売り文句にしない\n"
                "・リンク投稿は 1/3 以下\n"
                "・有益9:誘導1 を死守"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔌 PC が寝てると Bot は止まります",
            value=(
                "深夜の自動投稿 / 出先からの `/idea` を動かすには PC 設定が必須。\n"
                "詳細: `/help PC 24時間稼働設定`"
            ),
            inline=False,
        )
        embed.set_footer(text="個別詳細: /help レビューフロー など")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # 個別トピック
    embed = discord.Embed(color=0x4A90E2)

    if topic.value == "commands":
        embed.title = "🔧 基本コマンド一覧"
        embed.add_field(
            name="/review [account]",
            value=(
                "未レビュー下書きを最大 10 本まで表示。\n"
                "各下書きに `✅承認` `✏️編集` `🔄再生成` `❌却下` ボタン付き。\n"
                "省略時は `gaku_ai_life` のみ表示。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/post <text>",
            value=(
                "即時投稿。500 字以内。\n"
                "下書きを経由せず Threads にすぐ流れます。テスト投稿や思いつき即投稿用。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/queue <text> [time]",
            value=(
                "キューに追加。time の形式:\n"
                "・`HH:MM` (今日中。すでに過ぎてれば翌日扱い)\n"
                "・ISO8601 (`2026-05-14T07:30:00+09:00`)\n"
                "・省略時は次の空き枠 (07:30 / 12:30 / 18:00 / 21:30 / 23:00)"
            ),
            inline=False,
        )
        embed.add_field(
            name="/list",
            value="キュー (queued/) を publish_at 順で最大 20 件表示。",
            inline=False,
        )
        embed.add_field(
            name="/feedback <category> <content>",
            value=(
                "`feedback/gaku_ai_life.md` に追記。\n"
                "category 例: `冒頭1行` / `本文` / `末尾` / `リスク` / `当たり訴求`\n"
                "AIスタッフが次回生成時に必ず読み込む。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/status",
            value="未レビュー / キュー / 本日投稿数 / 次の投稿予定をサマリー表示。",
            inline=False,
        )
        embed.add_field(
            name="/create_post <topic> [type] [purpose] [publish_at] [account]",
            value=(
                "**単発の下書きを 1 本生成。** テーマ・型・目的・時刻を明示指定。\n"
                "・topic: 必須 (例: `Day3 進捗` `AI 失敗談`)\n"
                "・type: 任意 (例: `#6 共感あるある` `#2 昼進捗`)\n"
                "・purpose: 任意 (`集客` / `信頼構築` / `教育` / `販売`)\n"
                "・publish_at: 任意 (ISO8601・省略時は次の空き枠)\n\n"
                "思いつき → 即下書きフローに最適。`/post_bulk` との違いは「単発・明示指定」"
            ),
            inline=False,
        )
        embed.add_field(
            name="/create_post_from_idea <idea_id> [type] [purpose] [publish_at]",
            value=(
                "**inbox の溜まったネタを消化して下書き生成。**\n"
                "・idea_id: `/ideas` で確認 (前方一致OK・例: `20260514_004622`)\n"
                "・生成成功時、ネタの status を unused → used に自動マーク\n"
                "・蓄積資産の死蔵を防ぐフロー"
            ),
            inline=False,
        )
        embed.add_field(
            name="/post_bulk [count] [account] [theme]",
            value=(
                "**AI に投稿下書きを N 本まとめて生成。** 直下保存 → 後で `/review` で承認。\n"
                "・count: 1〜10 (デフォルト 5)\n"
                "・account: 省略時は `gaku_ai_life`\n"
                "・theme: テーマヒント (任意・例: AI開発 / Day3進捗 / 失敗談)\n\n"
                "**フィードバック蓄積 + research/topics/inbox/ のネタを毎回必ず読み込む**ので、書き足すほど精度UP。\n"
                "生成時間: 2〜5 分 (10 本でも約 5 分)。\n\n"
                "使用例:\n"
                "`/post_bulk count:3` ← 3 本生成\n"
                "`/post_bulk count:10 theme:AI開発` ← 10 本生成・テーマ指定\n"
                "`/post_bulk theme:深夜SE` ← 5 本生成・テーマ指定"
            ),
            inline=False,
        )
        embed.add_field(
            name="/morning [account]",
            value=(
                "**朝礼ダッシュボード。** 1コマンドで以下を表示:\n"
                "・昨日の投稿数 + TOP1 メトリクス (一昨日比較)\n"
                "・今日のキュー (publish_at 順)\n"
                "・推奨アクション (未レビュー / メトリクス未取得 / 自動リサーチ結果)\n"
                "朝の稼働 5分 → 30秒 に短縮。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/retry_post [account]",
            value=(
                "**自動投稿失敗時のリカバリ。** キューから1本を即時投稿試行。\n"
                "DNS復帰待ち最大3分含む。スリープ復帰後でも安全。\n"
                "結果: ✅成功 / ℹ️対象なし / ❌失敗 を色付きEmbedで表示。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/run task:<choice> [account]",
            value=(
                "**バッチジョブを Discord から即起動。** task の選択肢:\n"
                "・📊 metrics - メトリクス取得 + feedback 自動学習\n"
                "・🌙 nightly - 夜パイプライン (10本生成)\n"
                "・🔑 token_refresh - Threadsトークン更新\n"
                "・📈 m2f - メトリクス→feedback 単独\n"
                "・📚 watchlist - 自動リサーチ全実行\n"
                "・📺 watchlist_youtube / 🔍 watchlist_web - 個別実行"
            ),
            inline=False,
        )
        embed.add_field(
            name="/research_youtube <url> [count]",
            value=(
                "YouTube チャンネルから字幕取得→要約→投稿ネタ抽出。\n"
                "結果は `.company/research/topics/youtube-YYYY-MM-DD.md` に保存。\n"
                "翌日の /post_bulk で自動参照される。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/research_web [theme]",
            value=(
                "WebSearch でトレンド情報収集 (Claude Code / AI / Threads / note 関連)。\n"
                "テーマ指定で絞れる。所要 3〜5 分。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/research_self [account]",
            value=(
                "自分の過去投稿の数字を分析。伸びた要因 + 次戦略の判断材料。\n"
                "結果は `.company/research/topics/post-pattern-YYYY-MM.md` に蓄積。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/competitor_post <user> <text> <why> [views] [likes] [url]",
            value=(
                "**他人の伸びてる投稿を AI 学習素材に登録。**\n"
                "オーナー分析 (なぜ伸びたか) を付けて feedback の「良かった例」に追記。\n"
                "次回 AI 生成からこの型が反映される。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/watchlist",
            value=(
                "自動リサーチのウォッチリスト (YouTube/Web) を表示。\n"
                "編集は `.company/research/watchlist.md` を直接。\n"
                "毎朝 06:00 (YouTube) / 06:30 (Web) で自動実行 (タスクスケジューラ)。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/generate_article [date]",
            value=(
                "**日報・意思決定ログから note 記事を物語化して自動生成 (3000〜5000字)。**\n"
                "・date: today / yesterday / YYYY-MM-DD (省略時 today)\n"
                "・保存先: `.company/products/articles/YYYY-MM-DD_<slug>.md`\n"
                "・オーナーのキャラ・ライティングルール厳守\n"
                "開発しながら note の素材が同時にできるループの核。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/queue (画像添付対応)",
            value=(
                "下書きをキューに追加。**スマホ画像をそのまま添付可能 (新)**:\n"
                "・text: 本文 (500字)\n"
                "・time: HH:MM / ISO8601 / 省略時は次の空き枠\n"
                "・image: スマホで直接添付 (Discord CDN URL 利用)\n"
                "・image_url: 外部 URL (添付がない時)"
            ),
            inline=False,
        )
        embed.add_field(
            name="/sync",
            value="新しいスラッシュコマンドが Discord に反映されない時に実行。",
            inline=False,
        )

    elif topic.value == "review":
        embed.title = "🔄 レビューフローの使い方"
        embed.description = (
            "Discord 上で 4 つのボタンを押すだけで投稿運用が完結します。\n"
            "`/review` を実行 → 下書き 1 件につき 1 つのカードが表示されます。"
        )
        embed.add_field(
            name="✅ 承認",
            value=(
                "下書きを `queued/` に移動し、`publish_at` を自動付与。\n"
                "枠は朝/昼/夕/夜/深夜の中から次に空いている時刻を選びます。\n"
                "**承認直後すぐ投稿されるわけではなく、指定時刻になるまで待機します**。"
            ),
            inline=False,
        )
        embed.add_field(
            name="✏️ 編集",
            value=(
                "モーダルが開いて本文を直接書き換えできます (500 字以内)。\n"
                "保存すると Discord 上のカードが即座に更新され、編集ログは feedback 蓄積にも残ります。\n"
                "編集後にもう一度内容を見て、`✅承認` を押してください。"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔄 再生成",
            value=(
                "「どこをどう直してほしいか」を具体的に書いて送ると、Claude Code が同じトピックで書き直します。\n"
                "例: 「冒頭1行に固有名詞と数字を入れて。当たり訴求公式に沿わせて」\n"
                "数十秒〜数分かかります。完了するとカードが新しい本文で再表示されます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="❌ 却下",
            value=(
                "理由を書いて送ると `rejected/` に移動。\n"
                "理由は feedback 蓄積にも自動追記されるので、AIスタッフが次回から同じパターンを避けます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="💡 推奨手順",
            value=(
                "1. 全 10 本ざっと目を通す\n"
                "2. 当たり訴求がついてるか確認 ((自分は何者か)×(気づき1つ))\n"
                "3. ベタ承認できるものから ✅\n"
                "4. 微修正したいものは ✏️\n"
                "5. 大きくズレてるものは 🔄 で指示出し\n"
                "6. ダメなものは ❌ で理由を残す"
            ),
            inline=False,
        )

    elif topic.value == "ideas":
        embed.title = "💡 ネタ蓄積の使い方"
        embed.description = (
            "投稿アイデア・気づき・観察を Discord から `.company/research/topics/inbox/` に保存。\n"
            "AI スタッフは下書き生成時にこの inbox を読みに行きます (※AI 側の参照ルールは `research/CLAUDE.md` で設定)。"
        )
        embed.add_field(
            name="/idea <content> [category]",
            value=(
                "思いつきを 1 行で投稿:\n"
                "`/idea 朝のスタバで AI 関連の本読んでる人みんな同じ表情してる category:観察`\n\n"
                "category 例: `AI` / `失敗` / `観察` / `当たり訴求` / `SE` / `note` / `深夜`"
            ),
            inline=False,
        )
        embed.add_field(
            name="/ideas [category] [used:True]",
            value=(
                "ためたネタの一覧。最大 20 件。\n"
                "category 指定でカテゴリ絞り込み。\n"
                "`used:True` で過去に使ったネタも見られます (再リライト用)。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/idea_use <id>",
            value=(
                "投稿に使ったネタを「使用済み」にマーク。\n"
                "ID は `/ideas` で見える `20260513_235812` みたいな形式。\n"
                "未使用ネタだけ次回 AI が拾うようになります。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/generate_ideas [category] [count]",
            value=(
                "**AI にネタを N 本生成させて inbox に直接追加。**\n"
                "Claude Code ヘッドレスで動くので 1〜3 分かかります。\n"
                "・count: 3〜10 (デフォルト 5)\n"
                "・category 指定でテーマ寄せられる\n"
                "・(自分は何者か)×(気づき1つ) 公式に沿ったネタが出ます\n"
                "・既存 inbox / feedback も参照するので重複は避けられる"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎯 こんな時に使う",
            value=(
                "・通勤中に気づいたネタを忘れずに残す\n"
                "・お客さんとの会話で出た言い回しをストック\n"
                "・別アカウントで伸びてた投稿の型をメモ\n"
                "・「これを 5/20 ぐらいに投稿したい」予約ネタ"
            ),
            inline=False,
        )
        embed.add_field(
            name="📁 保存場所",
            value=(
                "`.company/research/topics/inbox/YYYYMMDD_HHMMSS_<slug>.md`\n"
                "frontmatter: type / created / category / source / status (unused/used)"
            ),
            inline=False,
        )

    elif topic.value == "report":
        embed.title = "📓 日報管理の使い方"
        embed.description = (
            "1 日 1 ファイル形式で `.company/secretary/reports/YYYY-MM-DD.md` に保存。\n"
            "Discord から書き溜めて、夜に締める運用。"
        )
        embed.add_field(
            name="/report",
            value=(
                "今日の日報を表示します。\n"
                "存在しなければテンプレで自動作成 (KPI 速報には投稿数を自動セット)。\n"
                "再実行すれば最新の状態が見られます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/report_add <section> <content>",
            value=(
                "セクションに 1 行追記 (タイムスタンプ自動付与)。\n"
                "section の選択肢:\n"
                "・✅ 今日やったこと\n"
                "・📝 学び・気づき\n"
                "・⚠️ 失敗・つまずき\n"
                "・🎯 明日の重点\n"
                "・📊 KPI 速報\n"
                "・💭 自由メモ"
            ),
            inline=False,
        )
        embed.add_field(
            name="/report_close [comment]",
            value=(
                "今日の日報を `status: closed` にして締めます。\n"
                "`comment` を渡すと「🌙 締めコメント」セクションが末尾に追加されます。\n"
                "明日には自動で新しい日報が `/report` で立ち上がります。"
            ),
            inline=False,
        )
        embed.add_field(
            name="/reports",
            value="過去 7 日の日報一覧 (open / closed と最終更新時刻)",
            inline=False,
        )
        embed.add_field(
            name="🎯 おすすめの使い方",
            value=(
                "・朝起きたら `/report` でテンプレ立ち上げ\n"
                "・気づくたびに `/report_add 学び ...` で短く積む\n"
                "・夜 `/report_close 今日は当たり訴求が伸びた` で締める\n"
                "・週末に `/reports` で 1 週間振り返り\n"
                "・蓄積は AI スタッフが Phase レビュー時に参照"
            ),
            inline=False,
        )

    elif topic.value == "morning":
        embed.title = "🌅 朝のフロー (理想形)"
        embed.description = "理想的な 1 日の運用パターンです。"
        embed.add_field(
            name="02:00",
            value=(
                "`nightly_pipeline.py` が自動起動\n"
                "→ AIスタッフが下書き 10 本生成\n"
                "→ Discord に「下書きできました」通知"
            ),
            inline=False,
        )
        embed.add_field(
            name="起きたら",
            value=(
                "Discord で `/review` を打つ\n"
                "→ 10 本がボタン付きカルーセルで表示\n"
                "→ 布団の中でぽちぽち承認/編集/却下"
            ),
            inline=False,
        )
        embed.add_field(
            name="07:30 / 12:30 / 18:00 / 21:30 / 23:00",
            value=(
                "`threads_auto_post.py` が自動起動\n"
                "→ queued から `publish_at` が来たものを 1 本投稿\n"
                "→ posted/ に移動"
            ),
            inline=False,
        )
        embed.add_field(
            name="22:00",
            value=(
                "`threads_fetch_metrics.py` が自動起動\n"
                "→ 過去 30 日の投稿メトリクスを更新\n"
                "→ 翌日の戦略の素材に"
            ),
            inline=False,
        )
        embed.add_field(
            name="気が向いた時",
            value=(
                "`/feedback` で気づきを蓄積\n"
                "`/status` で現状確認\n"
                "`/queue` で思いつきを即キュー追加"
            ),
            inline=False,
        )

    elif topic.value == "rules":
        embed.title = "✍️ ライティングルール"
        embed.description = (
            "gaku_ai_life の全投稿に適用。\n"
            "詳細は `feedback/gaku_ai_life.md` 参照。"
        )
        embed.add_field(
            name="❌ 絶対 NG",
            value=(
                "・「〜かもしれません」「思います」 → 断定する\n"
                "・「みなさん」「皆様」 → 主語なし問いかけ\n"
                "・装飾系絵文字 (🔥✨🙌) を本文に\n"
                "・三点リーダー「、、、」で文末\n"
                "・「だ・である調」で全文 → 硬すぎる"
            ),
            inline=False,
        )
        embed.add_field(
            name="✅ 基本",
            value=(
                "・ですます調がベース\n"
                "・1 投稿 1 メッセージ\n"
                "・冒頭1行に固有名詞 + 数字 + ターゲット\n"
                "・1 か所は弱さ・本音を入れる (「自信ないです」など)\n"
                "・思考系絵文字は文末 1 個までOK (🤔😅😌)"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎯 当たり訴求公式",
            value=(
                "**(自分は何者か) × (気づき1つ)**\n\n"
                "例:\n"
                "「note 売上 0 円のぼくですが、AI に下書き 10 本作らせる方が、自分で 1 本書くより早いと気づきました。」\n\n"
                "投稿の 7 割はこの公式で作れます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="📏 文字数",
            value=(
                "AI 生成 220 字なら 120 字まで削る勇気。\n"
                "句読点ごとに改行。\n"
                "「ますか？」→「ます？」と切り詰める。"
            ),
            inline=False,
        )

    elif topic.value == "risk":
        embed.title = "⚠️ アカウント削除リスク対策"
        embed.description = (
            "あわを。が 1.5 万フォロワーを失った事例 (Threads7&8) から導入したルール。\n"
            "月 10 万円達成より先にアカウントを守る。"
        )
        embed.add_field(
            name="❌ 売り文句として連発禁止",
            value=(
                "・「月100万」「月7桁」「月◯円稼ぐ」\n"
                "・「収益化」「マネタイズ」「副業で稼ぐ」\n"
                "・「フォロワー少なくても売れる」\n"
                "・「初心者でも稼げる」\n\n"
                "→ 売り文句にしない。実体験の文脈で 1 投稿 1 個まで。"
            ),
            inline=False,
        )
        embed.add_field(
            name="📊 投稿バランス",
            value=(
                "・**有益 9 : 誘導 1** を死守\n"
                "・リンク投稿は全投稿の 1/3 以下\n"
                "・同じ note URL を 1 日 2 回以上貼らない"
            ),
            inline=False,
        )
        embed.add_field(
            name="🤖 偽アカウント対策",
            value=(
                "・固定投稿に「DM 勧誘しない」と明記\n"
                "・なりすまし発見時は即 Meta に通報\n"
                "・フォロワーからの「怪しいDM来た」報告は即記録"
            ),
            inline=False,
        )
        embed.add_field(
            name="💬 商品名",
            value=(
                "公開タイトルは「駆け出しSE × AI の note 実験記」。\n"
                "「実験記」「過程」が主軸。\n"
                "値上げを煽り文句にしない (「いまが最安」NG)。"
            ),
            inline=False,
        )

    elif topic.value == "always_on":
        embed.title = "🔌 PC 24 時間稼働設定 (深夜・出先でも Bot を動かす)"
        embed.description = (
            "Bot は PC 上の常駐プロセスです。PC がスリープすると Bot も止まり、"
            "Discord でコマンドを打っても反応しません。\n\n"
            "深夜の自動投稿 / 出先からの `/idea` などをちゃんと動かすには、"
            "PC を寝かさない設定が必須です。"
        )
        embed.add_field(
            name="❓ なぜ止まるのか",
            value=(
                "・スリープ = OS が CPU / ネットワーク / 全プロセスを停止\n"
                "・Discord Gateway 接続も切れる\n"
                "・休止状態・シャットダウンも同様\n"
                "・ノート PC は **蓋を閉じる = デフォでスリープ**"
            ),
            inline=False,
        )
        embed.add_field(
            name="① スリープ無効化 (GUI で)",
            value=(
                "**設定 → システム → 電源 & バッテリー → 画面とスリープ**\n\n"
                "・電源接続時、次の時間経過後にスリープ → **なし**\n"
                "・電源接続時、次の時間経過後に画面オフ → **10 分** など (画面だけはオフ OK)\n"
                "・バッテリ駆動時のスリープは残す (出先で持ち歩く時の節電)"
            ),
            inline=False,
        )
        embed.add_field(
            name="② 蓋を閉じても OK にする (ノート PC のみ)",
            value=(
                "**コントロールパネル → 電源オプション → カバーを閉じたときの動作の選択**\n\n"
                "・電源接続時: **何もしない** ← Bot を動かしたいので\n"
                "・バッテリ駆動時: スリープ (節電)\n\n"
                "PowerShell でやるなら:\n"
                "```\npowercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0\n"
                "powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 1\n"
                "powercfg /setactive SCHEME_CURRENT\n```"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚠️ 放熱の注意 (ノート PC は必読)",
            value=(
                "蓋を閉じたまま長時間稼働させると、キーボード裏の排熱面が机に密着して熱がこもります。"
                "PC 寿命を縮めるので下記必須:\n\n"
                "・**縦置きスタンド**に立てる (Amazon で 1,000〜3,000 円)\n"
                "・タオル・布の上に置かない\n"
                "・横と後ろの排気口を塞がない\n"
                "・「机に直置きで蓋閉じ」だけは絶対避ける"
            ),
            inline=False,
        )
        embed.add_field(
            name="③ Bot の自動起動 (Task Scheduler)",
            value=(
                "PC を再起動しても Bot が自動で立ち上がる設定:\n\n"
                "**管理者 PowerShell で実行**:\n"
                "```\n.\\scripts\\register_bot_task.ps1\n```\n"
                "これで PC ログオン時に Bot が自動起動。落ちたら 1 分後に最大 5 回再試行されます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="💡 さらに堅牢にしたいなら (将来)",
            value=(
                "Phase 3 (月 10 万到達) 後の検討:\n"
                "・Oracle Cloud Always Free に Bot を移植 (永久無料・24 時間稼働)\n"
                "・Raspberry Pi で自宅サーバー化\n"
                "・`.company/` を GitHub 管理にして PC との同期\n\n"
                "アカウントが資産化した段階では「PC 壊れたら全停止」リスク回避のため移行推奨。"
            ),
            inline=False,
        )

    elif topic.value == "troubleshoot":
        embed.title = "🔧 トラブル対処"
        embed.add_field(
            name="スラッシュコマンドが出ない",
            value=(
                "1. Discord クライアントを一度再起動\n"
                "2. それでも出ない → `/sync` を実行\n"
                "3. それでも出ない → Bot を再起動 (Task Scheduler から)"
            ),
            inline=False,
        )
        embed.add_field(
            name="「インタラクション失敗」が出る",
            value=(
                "Bot が落ちている可能性。\n"
                "PowerShell で:\n"
                "```\nStart-ScheduledTask -TaskName 'myCompany-DiscordBot'\n```"
            ),
            inline=False,
        )
        embed.add_field(
            name="承認したのに投稿されない",
            value=(
                "`publish_at` の時刻まで待機中の可能性。\n"
                "`/list` で publish_at を確認。\n"
                "`threads_auto_post` Task が 07:30 / 12:30 / 18:00 / 21:30 / 23:00 に動きます。"
            ),
            inline=False,
        )
        embed.add_field(
            name="再生成が遅い・失敗する",
            value=(
                "Claude Code をヘッドレスで呼んでいるので 1〜5 分かかります。\n"
                "10 分でタイムアウト。\n"
                "失敗時は ✏️編集 で手動修正に切り替えるのが早い場合あり。"
            ),
            inline=False,
        )
        embed.add_field(
            name="編集モーダルが 500 字制限",
            value=(
                "Threads の文字数上限と同じ。\n"
                "むしろ「半分まで削る勇気」がフィードバック蓄積の最重要ルールです。"
            ),
            inline=False,
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="report", description="今日の日報を表示 (なければ作成)")
async def cmd_report(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    today = dt.date.today()
    fpath = ensure_report(today)
    text = fpath.read_text(encoding="utf-8")
    # 4000 字以内に削る (Discord 制限)
    display = text if len(text) <= 3800 else text[:3800] + "\n\n…(省略)…"
    embed = discord.Embed(
        title=f"📓 日報 {today.isoformat()}",
        description=f"```markdown\n{display}\n```",
        color=0x9B59B6,
    )
    embed.set_footer(text=str(fpath.name))
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="report_add", description="日報のセクションに追記")
@app_commands.describe(
    section="どのセクションに書くか",
    content="内容 (1 行以上 OK・タイムスタンプ自動付与)",
)
@app_commands.choices(
    section=[
        app_commands.Choice(name="✅ 今日やったこと", value="done"),
        app_commands.Choice(name="📝 学び・気づき", value="learn"),
        app_commands.Choice(name="⚠️ 失敗・つまずき", value="fail"),
        app_commands.Choice(name="🎯 明日の重点", value="tomorrow"),
        app_commands.Choice(name="📊 KPI 速報", value="kpi"),
        app_commands.Choice(name="💭 自由メモ", value="memo"),
    ]
)
async def cmd_report_add(
    interaction: discord.Interaction,
    section: app_commands.Choice[str],
    content: str,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    try:
        today = dt.date.today()
        append_to_section(today, section.value, content)
        await interaction.response.send_message(
            f"📓 追記しました\n"
            f"セクション: **{section.name}**\n"
            f"内容: {content[:200]}",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(f"失敗: {e}", ephemeral=True)


@bot.tree.command(name="report_close", description="今日の日報を締める")
@app_commands.describe(comment="締めコメント (任意・1日の総括)")
async def cmd_report_close(
    interaction: discord.Interaction, comment: Optional[str] = None
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    try:
        today = dt.date.today()
        fpath = close_report(today, comment)
        msg = f"🌙 日報を締めました: `{fpath.name}`"
        if comment:
            msg += f"\n締めコメント: {comment[:150]}"
        await interaction.response.send_message(msg, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"失敗: {e}", ephemeral=True)


@bot.tree.command(name="reports", description="過去 7 日の日報一覧")
async def cmd_reports(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    reports = list_recent_reports(7)
    if not reports:
        await interaction.response.send_message(
            "過去 7 日に日報はありません。`/report` で今日の分を作れます。",
            ephemeral=True,
        )
        return
    lines = ["📚 直近 7 日の日報"]
    for r in reports:
        status_emoji = "🌙" if r["status"] == "closed" else "📝"
        lines.append(
            f"- {status_emoji} `{r['date']}` ({r['status']}) — 最終更新 {r['updated']}"
        )
    await interaction.response.send_message(
        "\n".join(lines), ephemeral=True
    )


@bot.tree.command(name="idea", description="投稿ネタをためる (思いつき / 観察 / 気づき)")
@app_commands.describe(
    content="ネタ本文 (短くてOK・思いつきレベル)",
    category="カテゴリ (任意・例: AI / 失敗 / 質問 / SE / 当たり訴求)",
)
async def cmd_idea(
    interaction: discord.Interaction,
    content: str,
    category: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    try:
        fpath = append_idea(content, category or "")
        await interaction.response.send_message(
            f"💡 ネタ追加しました\n"
            f"カテゴリ: `{category or '(なし)'}`\n"
            f"ID: `{fpath.stem}`\n\n"
            f"`/ideas` で一覧 / `/idea_use <ID>` で使用済みマーク",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            f"失敗: {e}", ephemeral=True
        )


@bot.tree.command(name="ideas", description="ためたネタの一覧")
@app_commands.describe(
    category="カテゴリで絞る (任意)",
    used="使用済みも見るか (デフォルト: 未使用のみ)",
)
async def cmd_ideas(
    interaction: discord.Interaction,
    category: Optional[str] = None,
    used: Optional[bool] = False,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    status = "used" if used else "unused"
    ideas = scan_ideas(category=category, status=status)
    if not ideas:
        await interaction.response.send_message(
            f"ネタはまだありません (status={status})。"
            "`/idea` で追加できます。",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=f"💡 ネタ一覧 ({len(ideas)} 件 / {status})",
        description=(
            f"カテゴリ: `{category or 'all'}`\n"
            "AI スタッフは下書き生成時にこのリストを参照します。"
        ),
        color=0xF5A623,
    )
    for i in ideas[:20]:
        snippet = i["content"][:180].replace("\n", " ")
        embed.add_field(
            name=f"`{i['id']}` [{i['category'] or '-'}]",
            value=snippet + ("…" if len(i["content"]) > 180 else ""),
            inline=False,
        )
    if len(ideas) > 20:
        embed.set_footer(text=f"残り {len(ideas) - 20} 件は省略")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="generate_ideas", description="AI にネタを N 本生成させて inbox に追加")
@app_commands.describe(
    category="カテゴリヒント (任意・例: AI / 失敗 / 観察 / 当たり訴求)",
    count="生成数 (3〜10・デフォルト 5)",
)
async def cmd_generate_ideas(
    interaction: discord.Interaction,
    category: Optional[str] = None,
    count: Optional[int] = 5,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    count_val = max(3, min(int(count or 5), 10))
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"🤖 AI にネタ {count_val} 本生成依頼中… (1〜3 分)", ephemeral=True
    )
    ok, ideas, log = await asyncio.to_thread(
        generate_ideas_via_claude, category or "", count_val
    )
    if not ok:
        await interaction.followup.send(
            f"❌ 生成失敗:\n```{log[:1500]}```", ephemeral=True
        )
        return
    if not ideas:
        await interaction.followup.send(
            f"⚠️ AI は応答したがネタが 0 件パースできました。"
            f"出力末尾:\n```{log[:1500]}```",
            ephemeral=True,
        )
        return

    saved_ids: list[str] = []
    for i in ideas:
        try:
            fpath = append_idea(
                i["content"], i.get("category", ""), source="claude_generate"
            )
            saved_ids.append(fpath.stem)
        except Exception:
            continue

    embed = discord.Embed(
        title=f"💡 ネタ {len(saved_ids)} 本生成 → inbox 保存",
        description=(
            f"カテゴリヒント: `{category or 'なんでも'}`\n"
            f"`/ideas` で一覧 / `/idea_use <id>` で使用済みマーク"
        ),
        color=0xF5A623,
    )
    for idx, idea in enumerate(ideas[:10]):
        embed.add_field(
            name=f"{idx + 1}. [{idea.get('category', '-')}]",
            value=idea["content"][:200]
            + ("…" if len(idea["content"]) > 200 else ""),
            inline=False,
        )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="idea_use", description="ネタを「使用済み」にマーク")
@app_commands.describe(idea_id="ネタ ID (/ideas で確認)")
async def cmd_idea_use(interaction: discord.Interaction, idea_id: str):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    inbox = PROJECT_ROOT / ".company" / "research" / "topics" / "inbox"
    fpath = inbox / f"{idea_id}.md"
    if not fpath.exists():
        await interaction.response.send_message(
            f"ネタが見つかりません: `{idea_id}`", ephemeral=True
        )
        return
    try:
        set_frontmatter(fpath, "status", "used")
        set_frontmatter(
            fpath,
            "used_at",
            dt.datetime.now().isoformat(timespec="seconds"),
        )
        await interaction.response.send_message(
            f"✅ 使用済みにマーク: `{idea_id}`", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"失敗: {e}", ephemeral=True
        )


@bot.tree.command(
    name="post_bulk",
    description="AI に投稿下書きを N 本まとめて生成させる (フィードバック蓄積を全部適用)",
)
@app_commands.describe(
    count="生成数 (1〜10・デフォルト 5)",
    account="アカウント名 (デフォルト: gaku_ai_life)",
    theme="テーマ指定 (任意・例: AI開発 / 失敗談 / Day3進捗)",
)
async def cmd_post_bulk(
    interaction: discord.Interaction,
    count: Optional[int] = 5,
    account: Optional[str] = "gaku_ai_life",
    theme: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    count_val = max(1, min(int(count or 5), 10))
    acct = account or "gaku_ai_life"
    theme_str = theme or ""

    await interaction.response.defer(thinking=True, ephemeral=True)
    msg = (
        f"🤖 `{acct}` の投稿下書きを **{count_val} 本** 生成中… (2〜5 分)\n"
        f"📚 フィードバック蓄積を全部読み込んでから生成します。"
    )
    if theme_str:
        msg += f"\n🎯 テーマ: `{theme_str}`"
    await interaction.followup.send(msg, ephemeral=True)

    # 生成前のファイル一覧スナップショット (新規生成分を後で抽出)
    drafts_dir = PROJECT_ROOT / ".company" / "marketing" / "drafts" / acct
    drafts_dir.mkdir(parents=True, exist_ok=True)
    before = {f.name for f in drafts_dir.glob("*.md")}

    ok, log = await asyncio.to_thread(
        generate_posts_via_claude, acct, count_val, theme_str
    )

    if not ok:
        await interaction.followup.send(
            f"❌ 生成失敗:\n```{log[:1500]}```", ephemeral=True
        )
        return

    # 生成後のファイル一覧 - 直下のみ (queued/posted/rejected は除外)
    after = {f.name for f in drafts_dir.glob("*.md")}
    new_files = sorted(after - before)
    if not new_files:
        await interaction.followup.send(
            "⚠️ Claude は応答したが新規ファイルが見つかりません。"
            f"出力末尾:\n```{log[:1500]}```",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=f"📝 投稿下書き {len(new_files)} 本生成 → drafts/{acct}/",
        description=(
            f"依頼: {count_val} 本 / 実績: {len(new_files)} 本\n"
            f"`/review` で承認 → `queued/` 移動 → 自動投稿対象"
        ),
        color=0x57F287,
    )
    for fname in new_files[:10]:
        fpath = drafts_dir / fname
        try:
            text = fpath.read_text(encoding="utf-8")
            topic_m = re.search(r'topic:\s*"?([^"\n]+)"?', text)
            topic = topic_m.group(1).strip() if topic_m else "(no topic)"
            pub_m = re.search(r"publish_at:\s*(\S+)", text)
            pub = pub_m.group(1).strip() if pub_m else "(未設定)"
            embed.add_field(
                name=f"📄 {fpath.stem[:80]}",
                value=f"**{topic[:60]}**\n📅 {pub}",
                inline=False,
            )
        except OSError:
            continue
    await interaction.followup.send(embed=embed, ephemeral=True)


def run_skill_via_claude(
    skill_name: str, args_str: str = "", timeout: int = 1800
) -> tuple[bool, str, str]:
    """Claude Code ヘッドレスで `/skill_name [args]` を実行.

    Returns: (ok, stdout_tail, log_path)
    """
    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"
    prompt = f"/{skill_name} {args_str}".strip()

    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]

    # 詳細ログ
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"skill_{skill_name.replace('/', '_')}_{ts}.log"

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        try:
            log_path.write_text(
                f"=== PROMPT ===\n{prompt}\n\n"
                f"=== EXIT ===\n{result.returncode}\n\n"
                f"=== STDOUT ===\n{result.stdout}\n\n"
                f"=== STDERR ===\n{result.stderr}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        if result.returncode != 0:
            return False, f"exit={result.returncode}\n{result.stderr[:800]}", str(log_path)
        return True, result.stdout[-2000:], str(log_path)
    except subprocess.TimeoutExpired:
        return False, f"タイムアウト ({timeout}秒)", str(log_path)
    except FileNotFoundError:
        return False, f"claude 見つからない: {claude_cmd}", str(log_path)


def run_claude_prompt(
    prompt: str, timeout: int = 1800
) -> tuple[bool, str, str]:
    """Claude Code ヘッドレスで自由なプロンプトを実行 (スキル発動ではない).

    /ask コマンドで使用. オーナーからの自由なテキスト指示を、
    別 Claude セッション (このプロセス外で起動) に投げる仕組み.

    Returns: (ok, full_stdout, log_path)
    """
    claude_cmd = os.getenv("CLAUDE_CMD", "claude").strip() or "claude"
    if claude_cmd.lower().endswith(".ps1"):
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]
    else:
        cmd = [
            claude_cmd,
            "-p",
            prompt,
            "--permission-mode",
            "bypassPermissions",
        ]

    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"ask_{ts}.log"

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        try:
            log_path.write_text(
                f"=== PROMPT ===\n{prompt}\n\n"
                f"=== EXIT ===\n{result.returncode}\n\n"
                f"=== STDOUT ===\n{result.stdout}\n\n"
                f"=== STDERR ===\n{result.stderr}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        if result.returncode != 0:
            return False, (
                f"exit={result.returncode}\n{result.stderr[:800]}"
            ), str(log_path)
        return True, (result.stdout or ""), str(log_path)
    except subprocess.TimeoutExpired:
        return False, f"タイムアウト ({timeout}秒)", str(log_path)
    except FileNotFoundError:
        return False, f"claude 見つからない: {claude_cmd}", str(log_path)


def _run_python_script(
    script_name: str, *args: str, timeout: int = 600
) -> tuple[int, str, str]:
    """scripts/<script_name> を subprocess で同期実行. (returncode, stdout_tail, stderr_tail)"""
    py_exe = os.getenv("PYTHON_EXE", "").strip() or sys.executable or "python"
    cmd = [py_exe, str(SCRIPT_DIR / script_name), *args]
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return (
            result.returncode,
            (result.stdout or "")[-1800:],
            (result.stderr or "")[-1000:],
        )
    except subprocess.TimeoutExpired:
        return -1, "", f"タイムアウト ({timeout}秒)"
    except FileNotFoundError as e:
        return -1, "", f"実行ファイルが見つからない: {e}"


@bot.tree.command(
    name="retry_post",
    description="キューから1本即時投稿 (自動投稿失敗のリカバリ用・ネット復帰後など)",
)
@app_commands.describe(
    account="アカウント名 (省略時: gaku_ai_life)",
)
async def cmd_retry_post(
    interaction: discord.Interaction,
    account: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    acct = account or DEFAULT_ACCOUNT
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"🔁 `{acct}` のキューから1本投稿を試行中…\n"
        f"(DNS復帰待ち最大3分含む・30秒〜2分)",
        ephemeral=True,
    )
    rc, out, err = await asyncio.to_thread(
        _run_python_script, "threads_auto_post.py", acct, timeout=400
    )
    body = (out or "").strip() or (err or "").strip() or "(no output)"

    # threads_auto_post.py の出力を解釈して結果を分かりやすく表示
    if rc == 0:
        if "投稿成功" in out or "media_id=" in out:
            color = 0x57F287
            title = "✅ 投稿成功"
        elif "投稿対象なし" in out:
            color = 0xFEE75C
            title = "ℹ️ 投稿対象なし (publish_at がまだ来ていない)"
        else:
            color = 0x57F287
            title = "✅ 完了"
    else:
        color = 0xED4245
        title = f"❌ 失敗 (exit={rc})"

    embed = discord.Embed(title=title, color=color)
    embed.add_field(
        name="出力", value=f"```\n{body[:1000]}\n```", inline=False
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="run",
    description="バッチジョブを即実行 (メトリクス取得 / 夜パイプライン / トークン更新)",
)
@app_commands.describe(
    task="実行するジョブ",
    account="アカウント名 (一部のジョブで使用・省略時 gaku_ai_life)",
)
@app_commands.choices(
    task=[
        app_commands.Choice(name="📊 メトリクス取得 + feedback自動学習", value="metrics"),
        app_commands.Choice(name="🌙 夜のパイプライン (10本生成)", value="nightly"),
        app_commands.Choice(name="🔑 Threadsトークン自動更新", value="token_refresh"),
        app_commands.Choice(name="📈 メトリクス→feedback 単独実行", value="m2f"),
        app_commands.Choice(name="📚 ウォッチリスト自動リサーチ", value="watchlist"),
        app_commands.Choice(name="📺 ウォッチリスト YouTubeだけ", value="watchlist_youtube"),
        app_commands.Choice(name="🔍 ウォッチリスト Webだけ", value="watchlist_web"),
        app_commands.Choice(name="⏰ メトリクスアラート即時チェック", value="post_alert"),
        app_commands.Choice(name="🔍 ファクトチェック (捏造検出)", value="fact_check"),
        app_commands.Choice(name="💡 リサーチ→inbox 化", value="research_to_inbox"),
    ]
)
async def cmd_run(
    interaction: discord.Interaction,
    task: app_commands.Choice[str],
    account: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    acct = account or DEFAULT_ACCOUNT
    await interaction.response.defer(thinking=True, ephemeral=True)

    # タスクごとの実行設定
    job_map = {
        "metrics": {
            "label": "📊 メトリクス取得",
            "script": "threads_fetch_metrics.py",
            "args": (acct, "30"),
            "timeout": 600,
            "eta": "1〜3 分",
        },
        "nightly": {
            "label": "🌙 夜パイプライン (10本生成)",
            "script": "nightly_pipeline.py",
            "args": (),
            "timeout": 1800,
            "eta": "3〜5 分",
        },
        "token_refresh": {
            "label": "🔑 Threadsトークン更新",
            "script": "refresh_threads_token.py",
            "args": (),
            "timeout": 120,
            "eta": "30 秒",
        },
        "m2f": {
            "label": "📈 メトリクス→feedback 単独",
            "script": "metrics_to_feedback.py",
            "args": (acct, "30"),
            "timeout": 120,
            "eta": "10 秒",
        },
        "watchlist": {
            "label": "📚 ウォッチリスト自動リサーチ (YouTube + Web)",
            "script": "run_watchlist.py",
            "args": (),
            "timeout": 3600,
            "eta": "5〜30 分",
        },
        "post_alert": {
            "label": "⏰ メトリクスアラート即時チェック (投稿後 15/30/60 分)",
            "script": "post_alert.py",
            "args": (),
            "timeout": 120,
            "eta": "10〜30 秒",
        },
        "fact_check": {
            "label": "🔍 ファクトチェック (drafts の捏造検出)",
            "script": "fact_check.py",
            "args": (acct,),
            "timeout": 60,
            "eta": "数秒",
        },
        "research_to_inbox": {
            "label": "💡 リサーチ結果を inbox 化 (collect.md → 個別ネタ)",
            "script": "research_to_inbox.py",
            "args": (),
            "timeout": 60,
            "eta": "数秒",
        },
        "watchlist_youtube": {
            "label": "📺 ウォッチリスト YouTube だけ",
            "script": "run_watchlist.py",
            "args": ("youtube",),
            "timeout": 3600,
            "eta": "5〜20 分",
        },
        "watchlist_web": {
            "label": "🔍 ウォッチリスト Web だけ",
            "script": "run_watchlist.py",
            "args": ("web",),
            "timeout": 1800,
            "eta": "3〜10 分",
        },
    }
    job = job_map.get(task.value)
    if not job:
        await interaction.followup.send(f"未知のタスク: {task.value}", ephemeral=True)
        return

    await interaction.followup.send(
        f"{job['label']} 実行中… (目安 {job['eta']})", ephemeral=True
    )
    rc, out, err = await asyncio.to_thread(
        _run_python_script, job["script"], *job["args"], timeout=job["timeout"]
    )
    body = (out or "").strip() or (err or "").strip() or "(no output)"

    color = 0x57F287 if rc == 0 else 0xED4245
    title = f"{job['label']}: {'✅ 完了' if rc == 0 else f'❌ 失敗 (exit={rc})'}"

    embed = discord.Embed(title=title, color=color)
    embed.add_field(
        name="出力", value=f"```\n{body[:1400]}\n```", inline=False
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="research_youtube",
    description="YouTube チャンネルの直近動画から字幕取得→要約→投稿ネタ抽出",
)
@app_commands.describe(
    channel_url="YouTube チャンネル URL (例: https://www.youtube.com/@example)",
    count="取得本数 (1〜20・デフォルト 10)",
)
async def cmd_research_youtube(
    interaction: discord.Interaction,
    channel_url: str,
    count: Optional[int] = 10,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    cnt = max(1, min(int(count or 10), 20))
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"📺 YouTube リサーチ実行中…\n"
        f"- チャンネル: `{channel_url}`\n"
        f"- 取得本数: {cnt}\n"
        f"- 所要: 字幕取得 2〜5 分 + 要約 1〜2 分",
        ephemeral=True,
    )
    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "youtube-research", f"{channel_url} {cnt}", 1800
    )
    color = 0x57F287 if ok else 0xED4245
    title = "📺 YouTube リサーチ完了" if ok else "❌ YouTube リサーチ失敗"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="出力", value=f"```\n{out[:1400]}\n```", inline=False)
    embed.set_footer(text=f"詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="research_web",
    description="Claude Code / AI / Threads / note の最新情報を WebSearch で収集",
)
@app_commands.describe(
    theme="特定テーマで絞る (任意・例: Claude Code 最新 / Threads アルゴリズム)",
)
async def cmd_research_web(
    interaction: discord.Interaction,
    theme: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    args = theme or ""
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"🔍 Web リサーチ実行中… (3〜5 分)\n"
        + (f"テーマ: `{theme}`" if theme else "デフォルト全テーマ巡回"),
        ephemeral=True,
    )
    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "research-collect", args, 1800
    )
    color = 0x57F287 if ok else 0xED4245
    title = "🔍 Web リサーチ完了" if ok else "❌ Web リサーチ失敗"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="出力", value=f"```\n{out[:1400]}\n```", inline=False)
    embed.set_footer(text=f"詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="research_self",
    description="自分の過去投稿の数字を分析 (伸びた要因 + 次戦略)",
)
@app_commands.describe(
    account="アカウント名 (省略時: gaku_ai_life)",
)
async def cmd_research_self(
    interaction: discord.Interaction,
    account: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    acct = account or DEFAULT_ACCOUNT
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"📈 自分の投稿分析実行中… (1〜3 分)\n対象アカウント: `{acct}`",
        ephemeral=True,
    )
    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "threads-analyze", acct, 600
    )
    color = 0x57F287 if ok else 0xED4245
    title = "📈 自己分析完了" if ok else "❌ 自己分析失敗"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="出力", value=f"```\n{out[:1400]}\n```", inline=False)
    embed.set_footer(text=f"詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="competitor_post",
    description="他人の伸びてる Threads 投稿を手動登録 → feedback の「他者の良かった例」に追加",
)
@app_commands.describe(
    username="同業者の @ユーザー名 (例: @soda_writing)",
    text="投稿本文 (コピペ)",
    why="なぜ伸びたかオーナー分析 (例: 冒頭の数字+弱さ開示が効いた)",
    views="表示数 (任意)",
    likes="いいね数 (任意)",
    url="投稿 URL (任意)",
)
async def cmd_competitor_post(
    interaction: discord.Interaction,
    username: str,
    text: str,
    why: str,
    views: Optional[int] = None,
    likes: Optional[int] = None,
    url: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    fb_path = (
        PROJECT_ROOT
        / ".company"
        / "marketing"
        / "feedback"
        / f"{DEFAULT_ACCOUNT}.md"
    )
    if not fb_path.exists():
        await interaction.response.send_message(
            f"feedback ファイルが無い: {fb_path}", ephemeral=True
        )
        return

    # feedback に追記するブロック構築
    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    metric_parts = []
    if views is not None:
        metric_parts.append(f"views={views}")
    if likes is not None:
        metric_parts.append(f"likes={likes}")
    metric_line = " / ".join(metric_parts) if metric_parts else "数字未取得"

    block = (
        f"\n### 他者の良かった例 {now_iso[:16]}: {username}\n"
        f"- メトリクス: {metric_line}\n"
        + (f"- URL: {url}\n" if url else "")
        + f"- 本文:\n"
        f"```\n{text}\n```\n"
        f"- オーナー分析 (なぜ伸びたか): {why}\n"
        f"- 登録日時: {now_iso}\n"
    )

    try:
        fb_text = fb_path.read_text(encoding="utf-8")
        # 「## 良かった例」セクションの直後に追記 (自分の良かった例と並ぶ場所)
        new_text, n = re.subn(
            r"(## 良かった例[^\n]*\n)",
            r"\1" + block,
            fb_text,
            count=1,
        )
        if n == 0:
            # セクションが無い場合は末尾追記
            new_text = fb_text + "\n## 良かった例（型として再利用する）\n" + block
        fb_path.write_text(new_text, encoding="utf-8")
    except Exception as e:
        await interaction.response.send_message(
            f"feedback への追記失敗: {e}", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"📌 同業者投稿を学習素材に登録: {username}",
        description=(
            f"次回 AI 生成から、この型・このトーンが反映されます。\n"
            f"`feedback/{DEFAULT_ACCOUNT}.md` の「良かった例」セクションに追記済み。"
        ),
        color=0x57F287,
    )
    embed.add_field(name="📝 オーナー分析", value=why[:200], inline=False)
    if metric_line != "数字未取得":
        embed.add_field(name="📊 メトリクス", value=metric_line, inline=True)
    if url:
        embed.add_field(name="🔗 URL", value=url, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="morning",
    description="朝礼ダッシュボード (昨日の結果 / 今日の予定 / 推奨アクション)",
)
@app_commands.describe(
    account="アカウント名 (省略時: gaku_ai_life)",
)
async def cmd_morning(
    interaction: discord.Interaction,
    account: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    acct = account or DEFAULT_ACCOUNT
    await interaction.response.defer(thinking=True, ephemeral=True)

    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    day_before = today - dt.timedelta(days=2)

    posted_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / acct / "posted"
    )
    queued_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / acct / "queued"
    )
    drafts_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / acct
    )

    # 昨日の投稿サマリ
    yesterday_posted = []
    if posted_dir.exists():
        yesterday_posted = list(
            posted_dir.glob(f"{yesterday.isoformat()}_*.md")
        )
    day_before_posted = []
    if posted_dir.exists():
        day_before_posted = list(
            posted_dir.glob(f"{day_before.isoformat()}_*.md")
        )

    # 昨日のメトリクス TOP3 (views ベース)
    metrics_summary = []
    for f in yesterday_posted:
        try:
            text = f.read_text(encoding="utf-8")
            views_m = re.search(r"\|\s*views\s*\|\s*(\d+)", text)
            likes_m = re.search(r"\|\s*likes\s*\|\s*(\d+)", text)
            topic_m = re.search(r'topic:\s*"?([^"\n]+?)"?$', text, re.MULTILINE)
            if views_m:
                metrics_summary.append(
                    {
                        "views": int(views_m.group(1)),
                        "likes": int(likes_m.group(1)) if likes_m else 0,
                        "topic": (topic_m.group(1).strip() if topic_m else "(no topic)")[:40],
                    }
                )
        except OSError:
            continue
    metrics_summary.sort(key=lambda x: x["views"], reverse=True)

    # 今日のキュー (publish_at 順)
    today_queue = []
    if queued_dir.exists():
        for f in sorted(queued_dir.glob("*.md")):
            try:
                text = f.read_text(encoding="utf-8")
                pub_m = re.search(r"publish_at:\s*(\S+)", text)
                topic_m = re.search(
                    r'topic:\s*"?([^"\n]+?)"?$', text, re.MULTILINE
                )
                if not pub_m:
                    continue
                pub_str = pub_m.group(1).strip()
                # 今日 or 明日朝のもののみ
                if today.isoformat() in pub_str or (
                    (today + dt.timedelta(days=1)).isoformat() in pub_str
                    and "T07" in pub_str
                ):
                    today_queue.append(
                        {
                            "publish_at": pub_str,
                            "topic": (topic_m.group(1).strip() if topic_m else "(no topic)")[:40],
                        }
                    )
            except OSError:
                continue

    # 未レビュー本数 (queued ではない直下の md)
    unreviewed_count = 0
    if drafts_dir.exists():
        unreviewed_count = len(list(drafts_dir.glob("*.md")))

    # 直近の自動リサーチ結果
    research_dir = PROJECT_ROOT / ".company" / "research" / "topics"
    today_research = []
    if research_dir.exists():
        today_research = [
            f.name
            for f in research_dir.glob("*.md")
            if today.isoformat() in f.name or yesterday.isoformat() in f.name
        ]

    # フォロワー数の最新 (.env 内の何か or accounts/<acct>.md から)
    follower_info = "(未取得)"

    # Embed 組立
    embed = discord.Embed(
        title=f"🌅 朝礼ダッシュボード ({today.isoformat()})",
        description=f"アカウント: `{acct}`",
        color=0xFEE75C,
    )

    # 昨日の結果
    y_summary = (
        f"投稿: **{len(yesterday_posted)} 本**"
        f" (一昨日: {len(day_before_posted)} 本)\n"
    )
    if metrics_summary:
        top = metrics_summary[0]
        y_summary += (
            f"TOP1: views **{top['views']}** / likes {top['likes']}\n"
            f"→ 「{top['topic']}」"
        )
    else:
        y_summary += "メトリクス未取得 (22:00 fetch_metrics 待ち)"
    embed.add_field(
        name=f"📊 昨日 ({yesterday.isoformat()}) の結果",
        value=y_summary,
        inline=False,
    )

    # 今日のキュー
    if today_queue:
        q_lines = "\n".join(
            f"- `{q['publish_at'][11:16]}` {q['topic']}" for q in today_queue[:8]
        )
        embed.add_field(
            name=f"⏰ 今日のキュー ({len(today_queue)} 本)",
            value=q_lines,
            inline=False,
        )
    else:
        embed.add_field(
            name="⏰ 今日のキュー",
            value="**空っぽ！`/post_bulk count:5` で生成推奨**",
            inline=False,
        )

    # 推奨アクション
    actions = []
    if unreviewed_count > 0:
        actions.append(f"📥 未レビュー下書き **{unreviewed_count} 本** → `/review`")
    if len(today_queue) < 3:
        actions.append("📝 今日のキュー薄い → `/post_bulk count:5`")
    if not metrics_summary and yesterday_posted:
        actions.append("📊 メトリクス未取得 → `/run task:metrics`")
    if today_research:
        actions.append(
            f"💡 自動リサーチ結果 {len(today_research)} 本あり → `/post_bulk` で活用される"
        )
    if not actions:
        actions.append("✅ 推奨アクションなし。順調です")
    embed.add_field(
        name="🎯 今日の推奨アクション",
        value="\n".join(actions),
        inline=False,
    )

    embed.set_footer(text="💡 /post_bulk で生成 / /review でレビュー / /retry_post で投稿リトライ")

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="create_post",
    description="単発の投稿下書きを 1 本生成 (テーマ/型/目的/時刻を明示指定)",
)
@app_commands.describe(
    topic="トピック (例: Day3 進捗 / AI 失敗談・必須)",
    template_type="型 (例: #6 共感あるある / #2 昼進捗 / #10 深夜起きてる・任意)",
    purpose="目的 (集客 / 信頼構築 / 教育 / 販売・任意)",
    publish_at="投稿時刻 ISO8601 (例: 2026-05-15T07:30:00+09:00・省略時は次の空き枠)",
    account="アカウント名 (省略時: gaku_ai_life)",
)
async def cmd_create_post(
    interaction: discord.Interaction,
    topic: str,
    template_type: Optional[str] = None,
    purpose: Optional[str] = None,
    publish_at: Optional[str] = None,
    account: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    acct = account or DEFAULT_ACCOUNT

    # スキル引数を組み立て
    args_parts = [f'topic="{topic}"', f"account={acct}"]
    if template_type:
        args_parts.append(f'template_type="{template_type}"')
    if purpose:
        args_parts.append(f"purpose={purpose}")
    if publish_at:
        args_parts.append(f"publish_at={publish_at}")
    args_str = " ".join(args_parts)

    await interaction.response.defer(thinking=True, ephemeral=True)
    msg_lines = [
        f"📝 単発下書き生成中… (1〜3 分)",
        f"トピック: `{topic}`",
        f"アカウント: `{acct}`",
    ]
    if template_type:
        msg_lines.append(f"型: `{template_type}`")
    if purpose:
        msg_lines.append(f"目的: `{purpose}`")
    if publish_at:
        msg_lines.append(f"投稿時刻: `{publish_at}`")
    await interaction.followup.send("\n".join(msg_lines), ephemeral=True)

    # 生成前スナップショット
    drafts_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / acct
    )
    drafts_dir.mkdir(parents=True, exist_ok=True)
    before = {f.name for f in drafts_dir.glob("*.md")}

    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "threads-create-post", args_str, 600
    )

    after = {f.name for f in drafts_dir.glob("*.md")}
    new_files = sorted(after - before)

    color = 0x57F287 if (ok and new_files) else 0xED4245
    title = (
        f"📝 下書き生成完了 ({len(new_files)} 本)"
        if ok and new_files
        else "❌ 下書き生成失敗"
    )
    embed = discord.Embed(title=title, color=color)
    if new_files:
        for fname in new_files[:3]:
            try:
                text = (drafts_dir / fname).read_text(encoding="utf-8")
                topic_m = re.search(r'topic:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
                pub_m = re.search(r"publish_at:\s*(\S+)", text)
                first_line_m = re.search(r"【本文】\s*\n(.+?)(?:\n|$)", text)
                topic_str = topic_m.group(1).strip() if topic_m else "(no topic)"
                pub_str = pub_m.group(1).strip() if pub_m else "(未設定)"
                first_line = (
                    first_line_m.group(1).strip()[:80] if first_line_m else "(本文未取得)"
                )
                embed.add_field(
                    name=f"📄 {fname}",
                    value=f"**{topic_str[:60]}**\n📅 {pub_str}\n💬 {first_line}",
                    inline=False,
                )
            except OSError:
                continue
    else:
        embed.add_field(
            name="出力ログ末尾", value=f"```\n{out[:1200]}\n```", inline=False
        )
    embed.set_footer(text=f"次は /review で承認 / 詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="create_post_from_idea",
    description="inbox のネタ ID を指定して投稿下書きを生成 (ネタ消化フロー)",
)
@app_commands.describe(
    idea_id="ネタ ID (/ideas で確認・前方一致でOK・例: 20260514_004622)",
    template_type="型 (任意)",
    purpose="目的 (集客/信頼構築/教育/販売・任意)",
    publish_at="投稿時刻 ISO8601 (任意・省略時は次の空き枠)",
)
async def cmd_create_post_from_idea(
    interaction: discord.Interaction,
    idea_id: str,
    template_type: Optional[str] = None,
    purpose: Optional[str] = None,
    publish_at: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    # ネタファイルを探す (前方一致対応)
    inbox = (
        PROJECT_ROOT / ".company" / "research" / "topics" / "inbox"
    )
    if not inbox.exists():
        await interaction.response.send_message(
            f"inbox がありません: {inbox}", ephemeral=True
        )
        return
    candidates = sorted(inbox.glob(f"{idea_id}*.md"))
    if not candidates:
        await interaction.response.send_message(
            f"ネタが見つかりません: `{idea_id}`\n"
            f"`/ideas` で ID を確認してください。",
            ephemeral=True,
        )
        return
    idea_path = candidates[0]

    # ネタ本文抽出
    try:
        idea_text = idea_path.read_text(encoding="utf-8")
    except OSError as e:
        await interaction.response.send_message(
            f"ネタファイル読み込み失敗: {e}", ephemeral=True
        )
        return
    body_m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)$", idea_text, re.DOTALL)
    body = (body_m.group(1) if body_m else idea_text).strip()
    if not body:
        await interaction.response.send_message(
            f"ネタが空です: `{idea_path.name}`", ephemeral=True
        )
        return

    # スキル引数組み立て (本文の冒頭をトピックとして使う)
    topic_for_skill = body.replace("\n", " ").strip()[:100]
    args_parts = [
        f'topic="{topic_for_skill}"',
        f"account={DEFAULT_ACCOUNT}",
        f"source_idea_id={idea_path.stem}",
        f'source_idea_body="{body[:300]}"',
    ]
    if template_type:
        args_parts.append(f'template_type="{template_type}"')
    if purpose:
        args_parts.append(f"purpose={purpose}")
    if publish_at:
        args_parts.append(f"publish_at={publish_at}")
    args_str = " ".join(args_parts)

    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"💡 ネタ `{idea_path.stem[:40]}` から下書き生成中… (1〜3 分)\n"
        f"ネタ本文: {body[:120]}…",
        ephemeral=True,
    )

    drafts_dir = (
        PROJECT_ROOT / ".company" / "marketing" / "drafts" / DEFAULT_ACCOUNT
    )
    drafts_dir.mkdir(parents=True, exist_ok=True)
    before = {f.name for f in drafts_dir.glob("*.md")}

    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "threads-create-post", args_str, 600
    )

    after = {f.name for f in drafts_dir.glob("*.md")}
    new_files = sorted(after - before)

    # 生成成功なら ネタを used に
    idea_marked = False
    if ok and new_files:
        try:
            set_frontmatter(idea_path, "status", "used")
            set_frontmatter(
                idea_path,
                "used_at",
                dt.datetime.now().isoformat(timespec="seconds"),
            )
            idea_marked = True
        except Exception as e:
            print(f"[create_post_from_idea] used マーク失敗: {e}", file=sys.stderr)

    color = 0x57F287 if (ok and new_files) else 0xED4245
    title = (
        "💡 ネタ消化 → 下書き生成完了"
        if ok and new_files
        else "❌ ネタ消化失敗"
    )
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="💡 元ネタ", value=body[:200], inline=False)
    if new_files:
        for fname in new_files[:3]:
            try:
                text = (drafts_dir / fname).read_text(encoding="utf-8")
                topic_m = re.search(r'topic:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
                first_line_m = re.search(r"【本文】\s*\n(.+?)(?:\n|$)", text)
                topic_str = topic_m.group(1).strip() if topic_m else "(no topic)"
                first_line = (
                    first_line_m.group(1).strip()[:80] if first_line_m else "(本文未取得)"
                )
                embed.add_field(
                    name=f"📄 {fname}",
                    value=f"**{topic_str[:60]}**\n💬 {first_line}",
                    inline=False,
                )
            except OSError:
                continue
        embed.add_field(
            name="🗂️ ネタの状態",
            value=(
                "`status: used` にマーク済み" if idea_marked else "マーク失敗"
            ),
            inline=False,
        )
    else:
        embed.add_field(
            name="出力ログ末尾", value=f"```\n{out[:1000]}\n```", inline=False
        )
    embed.set_footer(text=f"次は /review で承認 / 詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="generate_article",
    description="日報・意思決定ログから note 記事を物語化して自動生成 (3000〜5000字)",
)
@app_commands.describe(
    date="対象日 (today / yesterday / YYYY-MM-DD・省略時 today)",
)
async def cmd_generate_article(
    interaction: discord.Interaction,
    date: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    target = date or "today"
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"📝 note 記事生成中… (3〜5 分)\n"
        f"対象日: `{target}`\n"
        f"📚 日報 + 意思決定ログ + 投稿実績 + git log を読み込んで物語化します。",
        ephemeral=True,
    )
    ok, out, log_path = await asyncio.to_thread(
        run_skill_via_claude, "note-article-generate", target, 1800
    )
    color = 0x57F287 if ok else 0xED4245
    title = "📝 note 記事生成完了" if ok else "❌ note 記事生成失敗"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="出力", value=f"```\n{out[:1400]}\n```", inline=False)
    embed.set_footer(text=f"詳細: {log_path}")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="watchlist",
    description="自動リサーチのウォッチリスト (YouTube/Web) を表示",
)
async def cmd_watchlist(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    watchlist_path = (
        PROJECT_ROOT / ".company" / "research" / "watchlist.md"
    )
    if not watchlist_path.exists():
        await interaction.response.send_message(
            f"ウォッチリストが無い: {watchlist_path}\n"
            "雛形を作るか、`scripts/run_watchlist.py` の説明を参照してください。",
            ephemeral=True,
        )
        return

    # run_watchlist.py の parser を流用してパース
    py_exe = os.getenv("PYTHON_EXE", "").strip() or sys.executable or "python"
    try:
        result = subprocess.run(
            [py_exe, str(SCRIPT_DIR / "run_watchlist.py"), "--dry-run"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        out = (result.stdout or "").strip() or "(no output)"
    except Exception as e:
        await interaction.response.send_message(
            f"watchlist 表示失敗: {e}", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="📚 リサーチウォッチリスト",
        description=(
            f"編集は `{watchlist_path.relative_to(PROJECT_ROOT)}` を直接編集\n"
            "実行: `/run task:watchlist` で即時起動"
        ),
        color=0x4A90E2,
    )
    embed.add_field(
        name="現在の登録内容 (dry-run 出力)",
        value=f"```\n{out[:1500]}\n```",
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


def parse_hook_patterns(account: str = "gaku_ai_life") -> dict:
    """feedback ファイルから「冒頭1行のバリエーション集 A〜H」を抽出.

    Returns: {"A": {"title": "...", "examples": ["...", "..."]}, ...}
    """
    fb_path = (
        PROJECT_ROOT / ".company" / "marketing" / "feedback" / f"{account}.md"
    )
    if not fb_path.exists():
        return {}
    try:
        text = fb_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    # 「冒頭1行のバリエーション集」セクションを切り出し
    section_m = re.search(
        r"## 冒頭1行のバリエーション集.*?(?=^## (?!#))",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not section_m:
        return {}
    section = section_m.group(0)

    patterns = {}
    # ### A. 数字先行型 (...)
    # - 例1
    # - 例2
    for m in re.finditer(
        r"###\s+([A-H])\.\s+([^\n]+)\n((?:-\s+.+\n)+)",
        section,
    ):
        letter = m.group(1)
        title = m.group(2).strip()
        examples_raw = m.group(3)
        examples = [
            line.lstrip("-").strip()
            for line in examples_raw.splitlines()
            if line.strip().startswith("-")
        ]
        # 「**注意**:」など補足は除外
        examples = [e for e in examples if not e.startswith("**")]
        patterns[letter] = {
            "title": title,
            "examples": examples,
        }
    return patterns


@bot.tree.command(
    name="hooks",
    description="冒頭1行のバリエーション集 A〜H を表示 (投稿作成の即参考)",
)
@app_commands.describe(
    pattern="型を指定 (A〜H or 省略で全部 or random でランダム 1 つ)",
)
async def cmd_hooks(
    interaction: discord.Interaction,
    pattern: Optional[str] = None,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    patterns = parse_hook_patterns(DEFAULT_ACCOUNT)
    if not patterns:
        await interaction.response.send_message(
            "冒頭バリエーション集が見つかりません。\n"
            f"`.company/marketing/feedback/{DEFAULT_ACCOUNT}.md` の "
            "「冒頭1行のバリエーション集」セクションを確認してください。",
            ephemeral=True,
        )
        return

    # random モード
    if pattern and pattern.lower() == "random":
        import random
        letter = random.choice(list(patterns.keys()))
        data = patterns[letter]
        example = random.choice(data["examples"]) if data["examples"] else ""
        embed = discord.Embed(
            title=f"🎲 {letter}型: {data['title']}",
            description=f"💡 **{example}**",
            color=0xF5A623,
        )
        if len(data["examples"]) > 1:
            others = "\n".join(
                f"・{e}" for e in data["examples"] if e != example
            )[:1000]
            embed.add_field(name="他の例", value=others or "(なし)", inline=False)
        embed.set_footer(text="ヒント: /create_post topic:... template_type:..." )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # 特定の型詳細
    if pattern and pattern.upper() in patterns:
        letter = pattern.upper()
        data = patterns[letter]
        embed = discord.Embed(
            title=f"📌 {letter}型: {data['title']}",
            color=0x4A90E2,
        )
        for i, ex in enumerate(data["examples"][:6], start=1):
            embed.add_field(name=f"例 {i}", value=ex[:200], inline=False)
        embed.set_footer(
            text="他の型は /hooks (一覧) / /hooks random (ランダム)"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # 全体一覧 (デフォルト)
    embed = discord.Embed(
        title="📚 冒頭 1 行のバリエーション集 (A〜H)",
        description=(
            "投稿の冒頭で使える 8 種類の型。\n"
            "詳細は `/hooks A` 等で個別指定。\n"
            "ランダム提案は `/hooks random`。"
        ),
        color=0x4A90E2,
    )
    for letter in sorted(patterns.keys()):
        data = patterns[letter]
        # 最初の 2 例だけ
        examples_short = data["examples"][:2]
        value = "\n".join(f"・{e[:60]}" for e in examples_short)
        embed.add_field(
            name=f"{letter}: {data['title']}",
            value=value or "(例なし)",
            inline=False,
        )
    embed.set_footer(text="ルール: 10 本生成時に A〜H から最低 5 種類使い分け")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="ask",
    description="Claude に直接指示 (ファイル変更 / 分析 / 設計判断・1〜10分)",
)
@app_commands.describe(
    message="指示・質問の内容 (例: feedback の H 型に「電車で本を読む人を見た」を追加)",
    save="やり取りを inbox に保存 (デフォルト True)",
)
async def cmd_ask(
    interaction: discord.Interaction,
    message: str,
    save: Optional[bool] = True,
):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send(
        f"💬 Claude に指示中… (1〜10 分)\n"
        f"指示: `{message[:300]}`",
        ephemeral=True,
    )

    today_iso = dt.date.today().isoformat()
    yesterday_iso = (dt.date.today() - dt.timedelta(days=1)).isoformat()

    contextual_prompt = (
        "あなたは myCompany プロジェクトの AI 開発パートナーです。\n"
        "オーナー (gaku_ai_life の運営者・駆け出しSE) との 1 対 1 のやり取りで、\n"
        "コード変更・設計判断・ファイル分析・調査を担当します。\n\n"
        "# 必読 (応答前にすべて読む・スキップ禁止)\n"
        "- `BLUEPRINT.md` (基本設計書・v1.2)\n"
        "- `.company/CLAUDE.md` (全社ライティングルール・組織ルール)\n"
        "- `.company/marketing/CLAUDE.md` (マーケ部署ルール)\n"
        "- `.company/marketing/feedback/gaku_ai_life.md` "
        "(フィードバック蓄積・冒頭バリエーション A〜H 含む)\n"
        f"- `.company/secretary/notes/{today_iso}-decisions.md` (今日の意思決定ログ・あれば)\n"
        f"- `.company/secretary/notes/{yesterday_iso}-decisions.md` (昨日の意思決定ログ・あれば)\n"
        "- 直近の inbox `.company/secretary/inbox/*_ask_*.md` "
        "(過去の /ask やり取り・あれば、文脈の連続性のため最新3件まで)\n\n"
        "# 振る舞い\n"
        "- オーナーの指示を「文字通り」だけでなく「意図」も汲んで実行\n"
        "- コード変更が必要なら Edit / Write ツールで **直接** 行う (提案だけで終わらせない)\n"
        "- 完了後は「何をしたか」「どのファイルが変わったか」を箇条書きで報告\n"
        "- 設計判断を伴う場合は D-XXX 形式で "
        f"`.company/secretary/notes/{today_iso}-decisions.md` に追記 "
        "(ファイルが無ければ新規作成)\n"
        "- 生成系タスク (投稿生成 / 記事生成) では feedback/<account>.md を必ず参照\n"
        "- 不明点があれば「❓確認が必要」と明示する (推測で実行しない)\n"
        "- discord_bot.py を変更した場合は最後に `Bot 再起動が必要です` と注意書きを入れる\n\n"
        "# オーナーからの指示\n"
        f"{message}\n\n"
        "応答の最後に「✅ 完了」「❓ 確認が必要」「❌ 失敗 (理由)」のいずれかを明示してください。"
    )

    ok, out, log_path = await asyncio.to_thread(
        run_claude_prompt, contextual_prompt, 1800
    )

    # やり取りを secretary/inbox/ に保存 (次回 /ask の素材として再利用される)
    saved_path = None
    if save:
        try:
            inbox = PROJECT_ROOT / ".company" / "secretary" / "inbox"
            inbox.mkdir(parents=True, exist_ok=True)
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = re.sub(r"[\s/\\:*?\"<>|【】]+", "-", message[:30]).strip("-") or "ask"
            saved_path = inbox / f"{ts}_ask_{slug}.md"
            saved_path.write_text(
                f"---\n"
                f"type: discord-ask\n"
                f"created: {dt.datetime.now().isoformat(timespec='seconds')}\n"
                f"source: discord_bot_ask\n"
                f"status: {'success' if ok else 'failed'}\n"
                f"---\n\n"
                f"# /ask やり取り\n\n"
                f"## 🔹 指示\n\n{message}\n\n"
                f"## 🔹 Claude の応答\n\n{out}\n\n"
                f"## 🔹 詳細ログ\n\n`{log_path}`\n",
                encoding="utf-8",
            )
        except OSError as e:
            print(f"[ask] inbox 保存失敗: {e}", file=sys.stderr)

    # 応答を Embed で返す (長文は冒頭+末尾に分割)
    color = 0x57F287 if ok else 0xED4245
    title = "💬 Claude からの応答" if ok else "❌ 失敗"

    out_clean = (out or "").strip()
    if not out_clean:
        out_clean = "(no output)"
    if len(out_clean) <= 3800:
        desc_value = out_clean
    else:
        desc_value = (
            out_clean[:1700]
            + "\n\n... 中略 ...\n\n"
            + out_clean[-1700:]
        )

    embed = discord.Embed(
        title=title,
        description=desc_value[:4000],
        color=color,
    )
    embed.add_field(
        name="🔹 指示", value=message[:1000], inline=False
    )
    footer_lines = [f"ログ: {log_path}"]
    if saved_path:
        try:
            footer_lines.insert(
                0, f"保存: {saved_path.relative_to(PROJECT_ROOT)}"
            )
        except ValueError:
            footer_lines.insert(0, f"保存: {saved_path}")
    embed.set_footer(text="\n".join(footer_lines)[:2000])

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="sync", description="スラッシュコマンドを再同期")
async def cmd_sync(interaction: discord.Interaction):
    if OWNER_ID and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "オーナー以外は操作できません。", ephemeral=True
        )
        return
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
    else:
        synced = await bot.tree.sync()
    await interaction.response.send_message(
        f"同期: {len(synced)} コマンド", ephemeral=True
    )


def main():
    if not BOT_TOKEN:
        print("[bot] DISCORD_BOT_TOKEN 未設定。.env を確認してください。", file=sys.stderr)
        sys.exit(1)
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
