"""studio ダッシュボード用データを集計して .company/reports/studio-data.json に書き出す.

KPI(リサーチ/発信インプ/交流/フォロワー/販売) と スタッフ状態 と アクティビティを
.company 配下のファイル数 + Threads API から計算する。トークンは出力しない。
売上は .company/reports/sales-manual.json があれば読む(手入力)。なければ 0。

使い方: python scripts/build_studio_data.py [--push]
"""
from __future__ import annotations

import json
import os
import re
import sys
import datetime as dt
import subprocess
from pathlib import Path

from dotenv import load_dotenv

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")
PROJECT_ROOT = SCRIPT_DIR.parent
ACCOUNT = "gaku_ai_life"

sys.path.insert(0, str(SCRIPT_DIR))


def jst_today() -> str:
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)).strftime("%Y-%m-%d")


def jst_now_iso() -> str:
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)).strftime(
        "%Y-%m-%dT%H:%M:%S+09:00"
    )


def count_md(d: Path, prefix: str | None = None) -> int:
    if not d.exists():
        return 0
    n = 0
    for f in d.glob("*.md"):
        if f.name.lower() in ("readme.md", "_template.md"):
            continue
        if prefix and not f.name.startswith(prefix):
            continue
        n += 1
    return n


def fetch_threads() -> dict:
    """followers / views(7d,today) / replies(7d) / likes(7d) を取得。失敗は None。"""
    out = {"followers": None, "views7d": None, "viewsToday": None, "replies7d": None, "likes7d": None}
    try:
        import requests
        from _threads_api import ThreadsClient, API_BASE

        c = ThreadsClient.from_env(account=ACCOUNT)
        now = int(dt.datetime.now().timestamp())
        since = now - 7 * 86400

        r = requests.get(
            f"{API_BASE}/{c.user_id}/threads_insights",
            params={"metric": "followers_count", "access_token": c.access_token},
            timeout=30,
        )
        if r.ok:
            out["followers"] = r.json()["data"][0]["total_value"]["value"]

        for metric in ("views", "replies", "likes"):
            rr = requests.get(
                f"{API_BASE}/{c.user_id}/threads_insights",
                params={"metric": metric, "since": since, "until": now, "access_token": c.access_token},
                timeout=30,
            )
            if not rr.ok:
                continue
            vals = (rr.json().get("data") or [{}])[0].get("values") or []
            total = sum(int(v.get("value", 0)) for v in vals)
            if metric == "views":
                out["views7d"] = total
                out["viewsToday"] = int(vals[-1]["value"]) if vals else None
            elif metric == "replies":
                out["replies7d"] = total
            elif metric == "likes":
                out["likes7d"] = total
    except Exception as e:
        print(f"[studio] Threads取得スキップ: {e}", file=sys.stderr)
    return out


def recent_activity(posted: Path, limit: int = 6) -> list[dict]:
    if not posted.exists():
        return []
    files = sorted(posted.glob("*.md"), reverse=True)[:limit]
    acts = []
    for f in files:
        m = re.match(r"\d{4}-\d{2}-\d{2}_(\d{2})(\d{2})", f.name)
        at = f"{m.group(1)}:{m.group(2)}" if m else "--:--"
        try:
            t = f.read_text(encoding="utf-8")
            bm = re.search(r"【本文】\s*\n(.+)", t)
            first = (bm.group(1).strip() if bm else "")[:24]
        except OSError:
            first = ""
        acts.append({"who": "エリカ", "action": "投稿", "what": first, "at": at})
    return acts


def load_outbound_today(today: str) -> dict | None:
    """build_outbound_targets.py の当日分があれば概要を返す。"""
    p = PROJECT_ROOT / ".company" / "reports" / "outbound-today.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if d.get("date") != today:
        return {"ready": False, "queries": [], "frames": []}
    return {
        "ready": True,
        "queries": d.get("queries", []),
        "frames": d.get("frames", []),
        "checklist": d.get("checklist", []),
    }


def read_title(f: Path) -> str:
    try:
        t = f.read_text(encoding="utf-8")
    except OSError:
        return f.stem
    m = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^#\s+(.+)$", t, re.M)
    if m:
        return m.group(1)
    return f.stem


def research_titles(research_dir: Path, today: str, limit: int = 6) -> list[str]:
    f = research_dir / f"{today}-collect.md"
    if not f.exists():
        return []
    return re.findall(r"^###\s+(.+)$", f.read_text(encoding="utf-8"), re.M)[:limit]


def article_titles(articles_dir: Path, limit: int = 6) -> list[str]:
    if not articles_dir.exists():
        return []
    fs = sorted(articles_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: list[str] = []
    for f in fs:
        if f.name.lower() in ("readme.md", "_template.md"):
            continue
        out.append(read_title(f))
        if len(out) >= limit:
            break
    return out


def paid_status(articles_dir: Path) -> str | None:
    if not articles_dir.exists():
        return None
    for f in articles_dir.glob("*.md"):
        if "paid" not in f.name.lower():
            continue
        try:
            t = f.read_text(encoding="utf-8")
        except OSError:
            continue
        pm = re.search(r"price:\s*([0-9]+)", t)
        price = f"{pm.group(1)}円" if pm else "有料"
        return f"有料note: {read_title(f)}（{price}）"
    return None


def ceo_summary(today: str) -> list[str]:
    f = PROJECT_ROOT / ".company" / "secretary" / "reports" / f"{today}-ceo.md"
    if not f.exists():
        return []
    t = f.read_text(encoding="utf-8")
    out: list[str] = []
    cm = re.search(r"## 社長コメント\s*\n(.+)", t)
    if cm:
        out.append("💬 " + cm.group(1).strip())
    for m in re.findall(r"^- (.+)$", t.split("## 明日の方針")[-1], re.M)[:4]:
        out.append("→ " + m)
    return out


def load_json_safe(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def mtime_hm(p: Path) -> str | None:
    try:
        return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%H:%M")
    except OSError:
        return None


def posted_times_today(posted_dir: Path, today: str) -> list[str]:
    out: list[str] = []
    if not posted_dir.exists():
        return out
    for f in posted_dir.glob(f"{today}_*.md"):
        m = re.match(r"\d{4}-\d{2}-\d{2}_(\d{2})(\d{2})", f.name)
        if m:
            out.append(f"{m.group(1)}:{m.group(2)}")
    return sorted(out)


def files_today(d: Path, today: str) -> list[Path]:
    if not d.exists():
        return []
    return [f for f in d.glob("*.md")
            if dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d") == today
            and f.name.lower() not in ("readme.md", "_template.md")]


def main() -> None:
    today = jst_today()
    mk = PROJECT_ROOT / ".company" / "marketing" / "drafts" / ACCOUNT
    research_dir = PROJECT_ROOT / ".company" / "research" / "topics"
    articles_dir = PROJECT_ROOT / ".company" / "products" / "articles"
    posted_dir = mk / "posted"
    queued_dir = mk / "queued"

    research_today = count_md(research_dir, prefix=today)
    research_total = count_md(research_dir)
    posted_today = count_md(posted_dir, prefix=today)
    queued_n = count_md(queued_dir)
    articles_n = count_md(articles_dir)

    th = fetch_threads()

    # 売上は手入力ファイルがあれば読む
    sales = {"yen": 0, "count": 0}
    sm = PROJECT_ROOT / ".company" / "reports" / "sales-manual.json"
    if sm.exists():
        try:
            sales.update(json.loads(sm.read_text(encoding="utf-8")))
        except Exception:
            pass

    def fmt(v):
        return v if v is not None else None

    staff = [
        {"id": "sakura", "name": "サクラ", "role": "社長 / 統括", "status": "巡回中",
         "detail": "全体を統括・確認・指示", "kpiLabel": "統括", "kpiValue": "稼働"},
        {"id": "sora", "name": "ソラ", "role": "リサーチ",
         "status": "完了" if research_today > 0 else "待機",
         "detail": "競合・トレンドを調査しネタを供給",
         "kpiLabel": "リサーチ", "kpiValue": f"{research_today}件"},
        {"id": "erika", "name": "エリカ", "role": "発信",
         "status": "完了" if posted_today > 0 else "待機",
         "detail": "Threadsで発信・流入をつくる",
         "kpiLabel": "投稿", "kpiValue": f"{posted_today}本"},
        {"id": "nana", "name": "ナナ", "role": "交流",
         "status": "完了" if (th["replies7d"] or 0) > 0 else "待機",
         "detail": "リプ・引用でフォロワーと関係構築",
         "kpiLabel": "交流", "kpiValue": (f"{th['replies7d']}件" if th["replies7d"] is not None else "—")},
        {"id": "yui", "name": "ユイ", "role": "制作",
         "status": "完了" if articles_n > 0 else "待機",
         "detail": "無料note・記事で教育→導線へ",
         "kpiLabel": "記事", "kpiValue": f"{articles_n}本"},
        {"id": "aoi", "name": "アオイ", "role": "営業",
         "status": "完了" if sales["count"] > 0 else "待機",
         "detail": "有料note・ファネルで収益化",
         "kpiLabel": "売上", "kpiValue": f"¥{sales['yen']:,}"},
    ]

    # 各社員の成果詳細（Webパネル表示用 feed）
    acts = recent_activity(posted_dir)
    ob = load_outbound_today(today)
    feeds: dict[str, list[str]] = {
        "sakura": ceo_summary(today) or ["社内を巡回・統括中"],
        "sora": ([f"今日のネタ: {t}" for t in research_titles(research_dir, today)]
                 or ["今日のリサーチはまだ"]) + [f"ネタ総数 {research_total}本"],
        "erika": ([f"{a['at']} {a['what']}" for a in acts[:5]]
                  or ["今日の投稿はまだ"]) + [f"投稿済 {count_md(posted_dir)}本 / キュー {queued_n}本"],
        "nana": ([f"絡みクエリ {len(ob['queries'])}・返信フレーム {len(ob['frames'])} 用意済"]
                 if ob and ob.get("ready") else ["今日の絡みリスト未生成（ボタンで作成）"])
                + ["実際の絡みは手作業で5〜10件"],
        "yui": [f"記事: {t}" for t in article_titles(articles_dir)] or ["記事なし"],
        "aoi": [paid_status(articles_dir) or "有料note未検出",
                f"購入 {sales['count']}件 / 売上 ¥{sales['yen']:,}"],
    }
    for s in staff:
        s["feed"] = feeds.get(s["id"], [])

    # タイムカード（実イベントの時刻から打刻を作る）
    ptimes = posted_times_today(posted_dir, today)
    research_files = files_today(research_dir, today)
    article_files = files_today(articles_dir, today)
    ceo_file = PROJECT_ROOT / ".company" / "secretary" / "reports" / f"{today}-ceo.md"
    ob_file = PROJECT_ROOT / ".company" / "reports" / "outbound-today.json"

    def card(status, cin=None, cout=None, count=0, unit="", note=""):
        return {"status": status, "in": cin, "out": cout, "count": count, "unit": unit, "note": note}

    tc: dict[str, dict] = {
        "sakura": card("巡回中", mtime_hm(ceo_file) if ceo_file.exists() else None, None, 0, "", "統括"),
        "erika": card("出勤", ptimes[0], ptimes[-1], len(ptimes), "投稿") if ptimes else card("未出勤", unit="投稿"),
        "sora": card("出勤", mtime_hm(research_files[0]), None, len(research_files), "リサーチ") if research_files else card("未出勤", unit="リサーチ"),
        "yui": card("出勤", mtime_hm(article_files[0]), None, len(article_files), "記事") if article_files else card("未出勤", unit="記事"),
        "nana": card("出勤", mtime_hm(ob_file), None, 0, "絡み", "リスト準備済・実務は手動") if (outbound := load_outbound_today(today)) and outbound.get("ready") else card("未出勤", unit="絡み"),
        "aoi": card("出勤", None, None, sales["count"], "売上") if sales["count"] > 0 else card("未出勤", unit="売上"),
    }
    for s in staff:
        s["timecard"] = tc.get(s["id"], card("未出勤"))

    # 目標・社訓（company-config.json）
    cfg = load_json_safe(PROJECT_ROOT / ".company" / "company-config.json")
    goals = []
    cur_map = {
        "followers": th["followers"] or 0,
        "sales_month": sales["yen"],
        "posts_today": len(ptimes),
        "research_today": research_today,
    }
    for key, meta in (cfg.get("goals") or {}).items():
        target = meta.get("target") or 0
        c = cur_map.get(key, 0)
        pct = min(100, round(c / target * 100)) if target else 0
        goals.append({"key": key, "label": meta.get("label", key), "current": c,
                      "target": target, "unit": meta.get("unit", ""), "pct": pct, "note": meta.get("note", "")})

    # 次の採用マイルストーン（D: 成長イベント）
    HIRES = [(300, "カイ", "アナリスト"), (500, "ミオ", "デザイナー"),
             (1000, "レン", "コミュニティ"), (2000, "ツカサ", "プロダクト")]
    next_hire = None
    f_now = th["followers"]
    if f_now is not None:
        for at, name, role in HIRES:
            if f_now < at:
                next_hire = {"at": at, "name": name, "role": role, "remaining": at - f_now}
                break

    # 今日の絡み候補（A: ナナ半自動化）
    outbound = load_outbound_today(today)

    data = {
        "generated_at": jst_now_iso(),
        "kpi": {
            "research": {"today": research_today, "total": research_total},
            "impressions": {"recent7d": fmt(th["views7d"]), "today": fmt(th["viewsToday"])},
            "engagement": {"replies7d": fmt(th["replies7d"]), "likes7d": fmt(th["likes7d"])},
            "followers": fmt(th["followers"]),
            "sales": sales,
            "queued": queued_n,
        },
        "staff": staff,
        "activity": recent_activity(posted_dir),
        "company": {
            "name": cfg.get("name", "サクラStudio"),
            "mission": cfg.get("mission", ""),
            "creed": cfg.get("creed", []),
            "goals": goals,
            "next_hire": next_hire,
            "outbound": outbound,
        },
        "note": "数字は実データ。取れない値はnull(画面で「—」)。売上は sales-manual.json で手入力可。",
    }

    out_path = PROJECT_ROOT / ".company" / "reports" / "studio-data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[studio] 書き出し: {out_path}")
    print(f"  followers={th['followers']} views7d={th['views7d']} research今日={research_today} 投稿今日={posted_today} 記事={articles_n} 売上=¥{sales['yen']}")

    if "--push" in sys.argv:
        rel = ".company/reports/studio-data.json"
        for cmd in (["git", "add", rel],
                    ["git", "commit", "-m", "chore: studio-data 更新"],
                    ["git", "push"]):
            r = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
            print(f"  $ {' '.join(cmd)} -> {r.returncode}")


if __name__ == "__main__":
    main()
