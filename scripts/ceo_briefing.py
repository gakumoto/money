"""社長サクラの自動経営: studio-data + キュー + 今日のリサーチ/意思決定を集計し、
「社長コメント＋明日の方針」を deterministic に生成して
.company/secretary/reports/YYYY-MM-DD-ceo.md に出す（同日は上書き）。

翌日の Threads ネタ / note 素材になる。LLM 非依存で堅牢に動く。
"""
from __future__ import annotations

import json
import re
import sys
import datetime as dt
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent


def jst_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def first_int(s: str) -> int:
    m = re.search(r"\d[\d,]*", s or "")
    return int(m.group(0).replace(",", "")) if m else 0


def main() -> None:
    now = jst_now()
    today = now.strftime("%Y-%m-%d")
    day = (now.date() - dt.date(2026, 5, 12)).days

    sd = load_json(ROOT / ".company" / "reports" / "studio-data.json") or {}
    kpi = sd.get("kpi", {})
    staff = sd.get("staff", [])
    by = {s.get("id"): s for s in staff}

    followers = kpi.get("followers")
    views7d = kpi.get("impressions", {}).get("recent7d")
    research_today = kpi.get("research", {}).get("today", 0)
    posted_today = first_int(by.get("erika", {}).get("kpiValue", "0"))
    articles = first_int(by.get("yui", {}).get("kpiValue", "0"))
    sales = kpi.get("sales", {})

    done = [s["name"] for s in staff if s.get("status") == "完了"]
    idle = [s["name"] for s in staff if s.get("status") == "待機"]

    # 明日の方針（ルールベース）
    plans = []
    if "ナナ" in idle:
        plans.append("ナナ(交流): アウトバウンド絡み5〜10件。唯一の手動の穴。最優先。")
    if posted_today < 3:
        plans.append("エリカ(発信): 勝負枠(朝6:30/夜22:50)の張り付きで初速を取る。")
    if research_today == 0:
        plans.append("ソラ(リサーチ): ネタ収集を1回まわす。")
    if (sales.get("count", 0) or 0) == 0:
        plans.append("アオイ(営業): プロフ/固定の導線を点検(転換率が最大の伸びしろ)。売り込みは9:1厳守。")
    plans.append("ユイ(制作): 今日の出来事を実験記noteに1本。")

    # 社長コメント（done/idle で分岐）
    if not idle:
        comment = "全員が今日の成果を出した。いい日だ。明日は質を一段上げる。"
    elif len(done) >= 3:
        comment = f"{('・'.join(done))}は動いた。あとは{('・'.join(idle))}。止まってる所を1つずつ灯す。"
    else:
        comment = "今日は手が足りなかった。明日は数より、勝負どころ1点に集中する。"

    lines = [
        f"# 社長日報（サクラ） {today} / Day {day}",
        "",
        "## 今日のスコア",
        f"- フォロワー: {followers if followers is not None else '—'}",
        f"- 7日閲覧: {views7d if views7d is not None else '—'}",
        f"- 今日の投稿(エリカ): {posted_today}本",
        f"- 今日のリサーチ(ソラ): {research_today}件",
        f"- 記事(ユイ): {articles}本",
        f"- 売上(アオイ): ¥{sales.get('yen', 0):,} / {sales.get('count', 0)}件",
        f"- 稼働: 完了={('・'.join(done) or 'なし')} / 待機={('・'.join(idle) or 'なし')}",
        "",
        "## 社長コメント",
        comment,
        "",
        "## 明日の方針",
        *[f"- {p}" for p in plans],
        "",
        "## 投稿/note の種（この日報自体がネタ）",
        "- 「AI社長に今日の進捗を詰められた」体で過程開示にできる。",
        f"- 数字の生々しさ(フォロワー{followers}/売上¥{sales.get('yen', 0):,})はそのまま使える。",
    ]

    out_dir = ROOT / ".company" / "secretary" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{today}-ceo.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ceo] {out} done={len(done)} idle={len(idle)} plans={len(plans)}")


if __name__ == "__main__":
    main()
