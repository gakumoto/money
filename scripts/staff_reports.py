"""各AI社員の個別日報を生成する。studio-data.json の feed/timecard/status から、
社員ごとに「役割・今日やったこと・稼働・一言」を deterministic に組み立てて
.company/secretary/reports/YYYY-MM-DD-staff.md に書き出す（同日上書き）。
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

ROLE = {
    "sakura": ("社長 / 統括", "全体を見て各社員に確認・指示を出し、毎晩の方針を決める。"),
    "sora": ("リサーチ", "競合・トレンド・最新情報を調べ、投稿ネタを供給する。"),
    "erika": ("発信", "Threadsに投稿し、流入(閲覧)をつくる。"),
    "nana": ("交流", "リプ・引用・絡みでフォロワーと関係を築く（実務はgakuが手動）。"),
    "yui": ("制作", "無料note・記事を書いて教育し、有料への導線をつくる。"),
    "aoi": ("営業", "有料note・ファネルで収益化する。"),
}


def jst_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)


def comment(sid: str, worked: bool) -> str:
    if sid == "sakura":
        return "今日も社内を見て回りました。止まってる所を明日灯します。"
    if worked:
        return {
            "sora": "今日はネタを供給できました。明日はもっと尖った切り口を狙います。",
            "erika": "今日も投稿を出しました。勝負枠の初速づくりを続けます。",
            "nana": "絡みリストは用意済み。あとはgakuの手で5〜10件、関係を作ります。",
            "yui": "今日も記事を進めました。読まれる冒頭を磨きます。",
            "aoi": "導線を整えます。まずは母数を増やすのが先。",
        }.get(sid, "今日の分は動けました。")
    return {
        "nana": "まだ動けていません。絡みは手動なので、今日5件いきましょう。",
        "aoi": "売上はまだ0。プロフ/固定の転換率改善が先決です。",
        "sora": "今日はまだリサーチが0件。1回まわします。",
    }.get(sid, "今日はまだ成果がありません。")


def main() -> None:
    now = jst_now()
    today = now.strftime("%Y-%m-%d")
    sd = json.loads((ROOT / ".company" / "reports" / "studio-data.json").read_text(encoding="utf-8"))
    staff = sd.get("staff", [])

    lines = [f"# 社員日報 {today}", "", "AI社員それぞれの今日の動き（自動生成）。", ""]
    for s in staff:
        sid = s.get("id")
        role, mission = ROLE.get(sid, (s.get("role", ""), s.get("detail", "")))
        tc = s.get("timecard") or {}
        worked = bool(s.get("feed")) and s.get("status") in ("完了", "巡回中")
        if tc.get("in"):
            clock = f"{tc['in']}出勤"
            if tc.get("out") and tc["out"] != tc["in"]:
                clock += f"〜{tc['out']}"
            if tc.get("count"):
                clock += f"・本日{tc['count']}{tc.get('unit', '')}"
        else:
            clock = "未出勤"

        lines.append(f"## {s.get('name')}（{role}）　[{s.get('status')}]")
        lines.append(f"- 役割: {mission}")
        lines.append(f"- 稼働: {clock}")
        lines.append("- 今日やったこと:")
        for f in (s.get("feed") or ["（記録なし）"]):
            lines.append(f"  - {f}")
        lines.append(f"- 一言: {comment(sid, worked)}")
        lines.append("")

    out = ROOT / ".company" / "secretary" / "reports" / f"{today}-staff.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[staff_reports] {out} ({len(staff)}名)")


if __name__ == "__main__":
    main()
