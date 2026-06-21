"""ナナ(交流)半自動化: 今日のアウトバウンド絡み候補(検索クエリ)＋返信フレーム＋チェックリストを生成。

出力: .company/reports/outbound-today.json
実際の返信は gaku が手作業(Bot/シャドバン回避)。本スクリプトは「探す入口」と「埋める枠」を毎日用意する。
クエリは日付でローテーションして毎日変える。
"""
from __future__ import annotations

import json
import sys
import datetime as dt
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

QUERY_POOL = [
    "未経験 エンジニア", "駆け出し エンジニア", "プログラミング 勉強中",
    "AI 副業", "ChatGPT 副業", "個人開発", "ノーコード",
    "note 書いた", "Threads 始めました", "発信 始めた",
    "AIエージェント", "AIで自動化", "副業 はじめたて",
]

FRAMES = [
    {"situation": "未経験で勉強中・心折れそう",
     "frame": "分かります、ぼくも最初コード見て固まってました。いまはAIに書かせて動かす方に振ってます。今はどの言語さわってますか？"},
    {"situation": "note初投稿した",
     "frame": "初投稿おめでとうございます。ぼくも有料1本出すまで公開ボタンが怖かったです。テーマは何で書いたんですか？"},
    {"situation": "AIで副業始めたい",
     "frame": "ぼくはThreads自動投稿をAIに組ませるところから始めました。作りたいツールの当たりはついてますか？"},
    {"situation": "毎日発信つづけてる人",
     "frame": "毎日続けてるの、ほんとすごいです。ぼくもDay{day}でまだ手探りです。続けるコツってありますか？"},
]


def jst_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)


def main() -> None:
    now = jst_now()
    day = (now.date() - dt.date(2026, 5, 12)).days  # Threads Day
    ordinal = now.toordinal()

    k = 6
    start = (ordinal * k) % len(QUERY_POOL)
    queries = [QUERY_POOL[(start + i) % len(QUERY_POOL)] for i in range(k)]
    frames = [{"situation": f["situation"], "frame": f["frame"].replace("{day}", str(day))} for f in FRAMES]

    data = {
        "date": now.strftime("%Y-%m-%d"),
        "day": day,
        "target_count": "5〜10件",
        "queries": queries,
        "frames": frames,
        "checklist": [
            "genuine返信 5〜10件",
            "自スレのコメントに2往復返信",
            "22:50勝負枠の張り付き",
        ],
        "rule": "お世辞/絵文字だけはNG(down-rank)。相手の具体に触れる＋自分の実体験＋本物の質問の3要素で。",
        "note": "実際の返信は手作業(Bot回避)。これは探す入口と返信フレーム。",
    }

    out = ROOT / ".company" / "reports" / "outbound-today.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[outbound] {out} queries={len(queries)} frames={len(frames)} day={day}")


if __name__ == "__main__":
    main()
