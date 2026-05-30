"""全投稿のメトリクスをAPIから取得してHTMLレポートを生成する.

使い方:
    python scripts/fetch_all_metrics.py [account]
    python scripts/fetch_all_metrics.py gaku_ai_life
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from dotenv import load_dotenv
load_dotenv(SCRIPT_DIR / ".env")

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

from _threads_api import ThreadsClient
import requests

API_BASE = "https://graph.threads.net/v1.0"


def fetch_all_posts(client: ThreadsClient) -> list[dict]:
    all_posts = []
    params = {
        "fields": "id,text,timestamp,permalink,media_type",
        "limit": 100,
        "access_token": client.access_token,
    }
    url = f"{API_BASE}/{client.user_id}/threads"
    while True:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        all_posts.extend(data.get("data", []))
        nxt = data.get("paging", {}).get("next")
        if not nxt:
            break
        url = nxt
        params = {}
    return all_posts


def fetch_insights(client: ThreadsClient, media_id: str) -> dict:
    try:
        return client.get_insights(media_id)
    except Exception as e:
        print(f"  ⚠ {media_id}: {e}", file=sys.stderr)
        return {}


def jst(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone(tz=None).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def classify(text: str) -> str:
    t = text or ""
    if any(k in t for k in ["母の日", "コナン", "筋肉", "雨はきら", "排水溝", "マザコン", "髪切", "スタバ", "満員"]):
        return "日常共感"
    if any(k in t for k in ["Discord", "discord"]):
        return "Discord技術"
    if any(k in t for k in ["ぶっちゃけ", "0円", "全然読まれない", "ボロカス", "インサイト見れない", "あと20人"]):
        return "弱さ開示"
    if any(k in t for k in ["おはようございます", "おはよう"]):
        return "朝挨拶"
    if any(k in t for k in ["note投稿！", "連続", "けいぞく", "継続", "日！！", "日！"]):
        return "報告だけ"
    if any(k in t for k in ["Claude", "claude", "AI", "Threads", "note"]) and any(k in t for k in ["ですか", "いますか", "ません", "🤔", "🥹"]):
        return "問いかけ"
    if any(k in t for k in ["claudecode", "ClaudeCode", "Claudecode", "アプリ", "Discord Bot", "GeminiCLI", "シェア機能"]):
        return "技術実装"
    if any(k in t for k in ["Claude", "claude", "AI", "Threads", "note"]):
        return "AIノウハウ"
    return "その他"


def generate_daily_html(posts: list[dict]) -> tuple[str, str, str, str]:
    """日次投稿集計のHTMLとChart.js用データを返す.
    返り値: (table_rows_html, labels_js, counts_js, avg_views_js)
    """
    from collections import defaultdict
    daily = defaultdict(list)
    for p in posts:
        ts = p.get("timestamp", "")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz=None)
            date_str = dt.strftime("%Y-%m-%d")
            daily[date_str].append(p)
        except Exception:
            pass

    sorted_days = sorted(daily.items())
    labels = [d for d, _ in sorted_days]
    counts = [len(ps) for _, ps in sorted_days]
    avgs = [round(sum(p["views"] for p in ps) / len(ps)) for _, ps in sorted_days]

    # テーブル（新しい日付が上）
    rows = ""
    for date_str, ps_on_day in reversed(sorted_days):
        n = len(ps_on_day)
        total_v = sum(p["views"] for p in ps_on_day)
        avg_v = round(total_v / n)
        max_v = max(p["views"] for p in ps_on_day)
        # 投稿数によるバッジ色
        if n >= 8:
            badge_color = "#4ade80"
        elif n >= 5:
            badge_color = "#60a5fa"
        elif n >= 3:
            badge_color = "#fbbf24"
        else:
            badge_color = "#94a3b8"
        # 曜日
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            dow = ["月", "火", "水", "木", "金", "土", "日"][dt.weekday()]
        except Exception:
            dow = ""
        rows += (
            f'<tr style="border-bottom:1px solid #1e293b;">'
            f'<td style="padding:8px;color:#cbd5e1;">{date_str} <span style="color:#64748b;font-size:11px;">({dow})</span></td>'
            f'<td style="padding:8px;text-align:right;"><span style="background:{badge_color}22;color:{badge_color};border-radius:4px;padding:2px 10px;font-weight:700;">{n}本</span></td>'
            f'<td style="padding:8px;text-align:right;color:#94a3b8;">{avg_v:,}</td>'
            f'<td style="padding:8px;text-align:right;color:#94a3b8;">{max_v:,}</td>'
            f'<td style="padding:8px;text-align:right;color:#64748b;">{total_v:,}</td>'
            f'</tr>'
        )

    import json
    return rows, json.dumps(labels), json.dumps(counts), json.dumps(avgs)


def generate_roadmap_html(total_posts: int, avg_views: float) -> str:
    """60日ロードマップを今日の位置と一緒にHTMLで返す."""
    from datetime import date
    start = date(2026, 5, 14)
    goal = date(2026, 7, 13)
    today = date.today()

    total_days = (goal - start).days  # 60
    elapsed = max(0, (today - start).days)
    if elapsed > total_days:
        elapsed = total_days
    pct = elapsed / total_days * 100
    p1_end_pct = 14 / total_days * 100  # 23.3%
    p2_end_pct = 30 / total_days * 100  # 50.0%

    # 現在のフェーズ
    if elapsed <= 14:
        phase_num, phase_name, phase_color = 1, "信頼を貯める期", "#4ade80"
        phase_now_action = "「140本分析」を無料公開して、リーチと信頼を最大化する"
    elif elapsed <= 30:
        phase_num, phase_name, phase_color = 2, "30日実験期", "#60a5fa"
        phase_now_action = "弱さ開示 / 9時22時 / 未完型を設計通り運用。全データを記録する"
    else:
        phase_num, phase_name, phase_color = 3, "収益化期", "#f472b6"
        phase_now_action = "30日実験の全結果を有料記事として公開。月10万円を取りに行く"

    p1_class = "current" if phase_num == 1 else ("done" if phase_num > 1 else "")
    p2_class = "current" if phase_num == 2 else ("done" if phase_num > 2 else "")
    p3_class = "current" if phase_num == 3 else ""

    return f"""
<style>
.rm-progress{{position:relative;height:42px;background:#0f172a;border-radius:8px;margin:24px 0 8px;overflow:visible;}}
.rm-fill{{position:absolute;top:0;left:0;height:100%;background:linear-gradient(90deg,#4ade80,#60a5fa);border-radius:8px;}}
.rm-pdiv{{position:absolute;top:-6px;bottom:-6px;width:2px;background:#475569;}}
.rm-pdiv-label{{position:absolute;top:-22px;font-size:10px;color:#64748b;transform:translateX(-50%);white-space:nowrap;}}
.rm-now{{position:absolute;top:-10px;width:18px;height:62px;background:#fbbf24;border-radius:3px;transform:translateX(-50%);box-shadow:0 0 16px #fbbf24aa;z-index:2;}}
.rm-now-label{{position:absolute;top:-40px;font-size:11px;font-weight:700;color:#fbbf24;transform:translateX(-50%);white-space:nowrap;background:#1e293b;padding:2px 8px;border-radius:4px;border:1px solid #fbbf24;}}
.rm-phase-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:32px;}}
@media(max-width:700px){{.rm-phase-grid{{grid-template-columns:1fr;}}}}
.rm-phase{{background:#1e293b;border-radius:12px;padding:18px;border:2px solid #334155;transition:all .2s;}}
.rm-phase.current{{border-color:{phase_color};box-shadow:0 0 24px {phase_color}33;}}
.rm-phase.done{{opacity:0.5;}}
.rm-phase h3{{font-size:14px;color:#94a3b8;margin-bottom:4px;}}
.rm-phase .rm-pdate{{font-size:11px;color:#64748b;margin-bottom:12px;}}
.rm-phase .rm-pgoal{{font-size:15px;font-weight:700;color:#e2e8f0;margin-bottom:10px;line-height:1.5;}}
.rm-phase ul{{padding-left:16px;margin:0;}}
.rm-phase li{{font-size:12px;color:#cbd5e1;margin-bottom:5px;line-height:1.6;}}
.rm-now-action{{background:linear-gradient(135deg,#1e293b,#0f172a);border-left:4px solid {phase_color};border-radius:10px;padding:18px 22px;margin-top:24px;}}
.rm-now-action-label{{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;}}
.rm-now-action-text{{font-size:15px;font-weight:600;color:#e2e8f0;line-height:1.6;}}
.rm-snapshot{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:20px;}}
.rm-snap{{background:#0f172a;border-radius:8px;padding:14px;border-left:3px solid #334155;}}
.rm-snap-l{{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px;}}
.rm-snap-v{{font-size:22px;font-weight:700;color:#e2e8f0;}}
.rm-snap-s{{font-size:10px;color:#64748b;margin-top:2px;}}
</style>

<h2 style="font-size:18px;font-weight:700;margin:8px 0 16px;color:#e2e8f0;border-left:3px solid {phase_color};padding-left:12px;">60日ロードマップ <span style="font-size:13px;color:#64748b;font-weight:400;margin-left:12px;">月10万円までの道（2026-05-14 → 2026-07-13）</span></h2>

<div style="background:#1e293b;border-radius:12px;padding:24px 28px;">

  <!-- 進捗バー -->
  <div class="rm-progress">
    <div class="rm-fill" style="width:{pct:.1f}%;"></div>
    <div class="rm-pdiv" style="left:{p1_end_pct:.1f}%;"><div class="rm-pdiv-label">Day14 / 5/27</div></div>
    <div class="rm-pdiv" style="left:{p2_end_pct:.1f}%;"><div class="rm-pdiv-label">Day30 / 6/12</div></div>
    <div class="rm-now" style="left:{pct:.1f}%;"><div class="rm-now-label">今 Day {elapsed} / 60</div></div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:11px;color:#64748b;margin-top:14px;">
    <span>Day 0 / 5/14 開始</span>
    <span style="color:{phase_color};font-weight:700;">Phase {phase_num}: {phase_name}（{pct:.0f}%消化）</span>
    <span>Day 60 / 7/13 ゴール</span>
  </div>

  <!-- 現状スナップショット -->
  <div class="rm-snapshot">
    <div class="rm-snap" style="border-left-color:#60a5fa;">
      <div class="rm-snap-l">投稿数</div>
      <div class="rm-snap-v" style="color:#60a5fa;">{total_posts}</div>
      <div class="rm-snap-s">累計（API実数）</div>
    </div>
    <div class="rm-snap" style="border-left-color:#a78bfa;">
      <div class="rm-snap-l">平均views</div>
      <div class="rm-snap-v" style="color:#a78bfa;">{avg_views:.0f}</div>
      <div class="rm-snap-s">全期間平均</div>
    </div>
    <div class="rm-snap" style="border-left-color:#f472b6;">
      <div class="rm-snap-l">note売上</div>
      <div class="rm-snap-v" style="color:#f472b6;">0円</div>
      <div class="rm-snap-s">Phase 1 は売らない設計</div>
    </div>
    <div class="rm-snap" style="border-left-color:#fbbf24;">
      <div class="rm-snap-l">残り日数</div>
      <div class="rm-snap-v" style="color:#fbbf24;">{total_days - elapsed}日</div>
      <div class="rm-snap-s">月10万円達成まで</div>
    </div>
  </div>

  <!-- 今日のアクション -->
  <div class="rm-now-action">
    <div class="rm-now-action-label">今日やるべきこと（Phase {phase_num}）</div>
    <div class="rm-now-action-text">{phase_now_action}</div>
  </div>

  <!-- 3フェーズ -->
  <div class="rm-phase-grid">
    <div class="rm-phase {p1_class}">
      <h3>Phase 1 — 信頼を貯める</h3>
      <div class="rm-pdate">Day 1-14 / 5/14 〜 5/27</div>
      <div class="rm-pgoal">140本分析を無料公開し、リーチと信頼を最大化</div>
      <ul>
        <li>「データで殴る、盛らない人」というブランド確立</li>
        <li>当たり訴求を3パターン確定（弱さ開示 × 実数字 × 問いかけ）</li>
        <li>フォロワー増 + 30日実験の予告で次フェーズへ動線</li>
        <li><strong style="color:#4ade80;">売上目標：0円（売らない）</strong></li>
      </ul>
    </div>
    <div class="rm-phase {p2_class}">
      <h3>Phase 2 — 30日実験期</h3>
      <div class="rm-pdate">Day 15-44 / 5/28 〜 6/26</div>
      <div class="rm-pgoal">設計通り運用して、全データを記録する</div>
      <ul>
        <li>弱さ開示を週2本、9時/22時を優先、未完型を月1-2本</li>
        <li>views・likes・reply・フォロワー増加を毎日トラック</li>
        <li>仮説が当たったか／外れたかを正直に記録</li>
        <li><strong style="color:#60a5fa;">売上目標：0円（実験中・データ収集）</strong></li>
      </ul>
    </div>
    <div class="rm-phase {p3_class}">
      <h3>Phase 3 — 収益化期</h3>
      <div class="rm-pdate">Day 45-60 / 6/27 〜 7/13</div>
      <div class="rm-pgoal">30日実験の全結果を有料記事化して月10万円</div>
      <ul>
        <li>「設計通り運用したらこうなった」を有料で公開（C案続編）</li>
        <li>価格：1,980円 〜 2,980円（無料の名刺で十分育った後）</li>
        <li>成功も失敗も全部数字で出す。盛らない</li>
        <li><strong style="color:#f472b6;">売上目標：月10万円</strong></li>
      </ul>
    </div>
  </div>

  <!-- 戦略メモ -->
  <div style="margin-top:24px;padding:16px 20px;background:#0f172a;border-radius:10px;border-left:3px solid #94a3b8;">
    <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;">戦略変更ログ（2026-05-17）</div>
    <div style="font-size:12px;color:#cbd5e1;line-height:1.7;">
      評価フィードバックを受けて、Phase 2 の note 公開を「無料 + 30日後の有料続編」（C案）に切り替え。
      0円の今、有料で売る矛盾を解消し、無料記事を「データで殴る、盛らない人」というブランドの起爆剤として使う設計に。
      有料化は実験データという「答え」が出てから。
    </div>
  </div>

</div>
"""


def parse_note_article(project_root: Path) -> str:
    """note記事draft複数をinner-tabで返す (writing/review/draft/planning ステータス全部)."""
    import re
    articles_dir = project_root / ".company" / "products" / "articles"
    # 2026-05-22 修正: glob を全 *.md に拡張 (note-jikkenki-* など 2026-* 以外も拾う)
    all_files = sorted(articles_dir.glob("*.md"))

    # 2026-05-22 修正: C案フィルタを撤去。status ベースで実体のあるドラフトを抽出
    valid_status = {"writing", "review", "draft", "planning"}
    series = []
    for path in all_files:
        if path.name == "_template.md":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        fm_match = re.match(r'^---\n(.*?)\n---', raw, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        status_m = re.search(r'^status:\s*"?(\w+)"?\s*$', fm, re.MULTILINE)
        if not status_m or status_m.group(1) not in valid_status:
            continue
        title_m = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip().strip('"')
        else:
            # title が frontmatter になければ product フィールドを使用 (note-jikkenki-* シリーズ向け)
            product_m = re.search(r'^product:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
            title = product_m.group(1).strip().strip('"') if product_m else path.stem
        series.append({
            "path": path,
            "title": title,
            "raw": raw,
            "mtime": path.stat().st_mtime,
        })

    if not series:
        return ""

    # 古い順（第1弾 → 第2弾 → ...）
    series.sort(key=lambda a: a["mtime"])

    def md_to_html(md: str) -> str:
        lines = md.split('\n')
        html_parts = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # h1
            if line.startswith('# ') and not line.startswith('## '):
                html_parts.append(f'<h1 style="font-size:20px;font-weight:700;color:#e2e8f0;margin:20px 0 12px;line-height:1.4;">{line[2:].strip()}</h1>')
                i += 1
            # h2
            elif line.startswith('## '):
                html_parts.append(f'<h2 style="font-size:15px;font-weight:700;color:#a78bfa;margin:20px 0 10px;padding-bottom:4px;border-bottom:1px solid #334155;">{line[3:].strip()}</h2>')
                i += 1
            # h3
            elif line.startswith('### '):
                html_parts.append(f'<h3 style="font-size:13px;font-weight:700;color:#60a5fa;margin:14px 0 8px;">{line[4:].strip()}</h3>')
                i += 1
            # hr
            elif line.strip() == '---':
                html_parts.append('<hr style="border:none;border-top:1px solid #334155;margin:16px 0;">')
                i += 1
            # table
            elif line.strip().startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                thtml = '<table style="width:100%;border-collapse:collapse;font-size:12px;margin:10px 0;">'
                for ti, tl in enumerate(table_lines):
                    if re.match(r'\|[\s\-:]+\|', tl):
                        continue
                    cells = [c.strip() for c in tl.strip().strip('|').split('|')]
                    tag = 'th' if ti == 0 else 'td'
                    style = 'padding:6px 10px;border:1px solid #334155;' + ('color:#94a3b8;background:#0f172a;font-weight:600;' if ti == 0 else 'color:#cbd5e1;')
                    row = ''.join(f'<{tag} style="{style}">{c}</{tag}>' for c in cells)
                    thtml += f'<tr>{row}</tr>'
                thtml += '</table>'
                html_parts.append(thtml)
            # code block
            elif line.strip().startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1
                code = '\n'.join(code_lines)
                html_parts.append(f'<pre style="background:#0f172a;border-radius:8px;padding:12px;font-size:12px;color:#4ade80;overflow-x:auto;margin:10px 0;line-height:1.6;">{code}</pre>')
            # bullet list
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                items_list = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    item = re.sub(r'^\s*[-*] ', '', lines[i])
                    item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', item)
                    items_list.append(f'<li style="color:#cbd5e1;margin-bottom:5px;">{item}</li>')
                    i += 1
                html_parts.append(f'<ul style="padding-left:18px;margin:8px 0;">{"".join(items_list)}</ul>')
            # numbered list
            elif re.match(r'^\d+\. ', line.strip()):
                items_list = []
                while i < len(lines) and re.match(r'^\d+\. ', lines[i].strip()):
                    item = re.sub(r'^\d+\. ', '', lines[i].strip())
                    item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', item)
                    items_list.append(f'<li style="color:#cbd5e1;margin-bottom:5px;">{item}</li>')
                    i += 1
                html_parts.append(f'<ol style="padding-left:18px;margin:8px 0;">{"".join(items_list)}</ol>')
            # bold-only line (like **① やること**)
            elif line.strip() and not line.strip().startswith('#'):
                p = line.strip()
                if p:
                    p = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#fbbf24;">\1</strong>', p)
                    p = re.sub(r'\*(.+?)\*', r'<em style="color:#94a3b8;">\1</em>', p)
                    html_parts.append(f'<p style="color:#cbd5e1;font-size:13px;line-height:1.7;margin:6px 0;">{p}</p>')
                i += 1
            else:
                i += 1

        return '\n'.join(html_parts)

    PAID_MARKER = "※ここから先は有料です"

    # 各記事のパネル/ボタンHTML生成
    nav_buttons = ""
    panes = ""
    for i, art in enumerate(series):
        raw = re.sub(r'^---.*?---\s*', '', art["raw"], flags=re.DOTALL)
        paid_split = raw.split(PAID_MARKER)
        free_md = paid_split[0]
        paid_md = paid_split[1] if len(paid_split) > 1 else ""
        free_html = md_to_html(free_md)
        paid_html = md_to_html(paid_md) if paid_md else ""

        active = "note-pane-active" if i == 0 else ""
        btn_active = "note-btn-active" if i == 0 else ""
        # ボタンラベル：第N弾 + タイトル短縮
        short_title = art["title"]
        if len(short_title) > 30:
            short_title = short_title[:28] + "…"
        nav_buttons += (
            f'<button class="note-btn {btn_active}" onclick="switchNote({i})">'
            f'<span style="display:block;font-size:11px;color:#94a3b8;">第{i+1}弾</span>'
            f'<span style="display:block;font-size:12px;margin-top:2px;">{short_title}</span>'
            f'</button>'
        )

        body = f'<div style="font-family:\'Hiragino Kaku Gothic Pro\',sans-serif;">{free_html}'
        if paid_html:
            body += (
                '<div style="border:2px dashed #f59e0b;border-radius:10px;padding:16px;margin:16px 0;text-align:center;">'
                '<div style="color:#f59e0b;font-size:13px;font-weight:700;margin-bottom:4px;">💰 ここから有料エリア</div>'
                '<div style="color:#64748b;font-size:11px;">↓ noteに貼り付け時に「有料設定」にするライン</div>'
                f'</div>{paid_html}'
            )
        body += f'<div style="margin-top:12px;font-size:10px;color:#475569;text-align:right;">ソース: {art["path"].name}</div></div>'
        panes += f'<div class="note-pane {active}">{body}</div>'

    style_block = """<style>
.note-nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;border-bottom:1px solid #334155;padding-bottom:0;}
.note-btn{background:transparent;border:none;border-bottom:3px solid transparent;color:#64748b;padding:10px 16px;cursor:pointer;text-align:left;transition:all .15s;margin-bottom:-1px;border-radius:0;}
.note-btn:hover{color:#cbd5e1;}
.note-btn-active{color:#e2e8f0;border-bottom-color:#4ade80;}
.note-btn-active span:last-child{color:#e2e8f0;font-weight:700;}
.note-pane{display:none;}
.note-pane-active{display:block;}
</style>"""

    return (
        f'{style_block}'
        f'<div class="note-nav">{nav_buttons}</div>'
        f'{panes}'
    )


def parse_buzz_references(project_root: Path) -> list[dict]:
    """バズ投稿リファレンスファイルを解析して各投稿を構造化して返す."""
    import re
    topics_dir = project_root / ".company" / "research" / "topics"
    files = sorted(topics_dir.glob("*-buzz-references.md"), reverse=True)
    if not files:
        return []

    text = files[0].read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r'\n(?=## \d+\. )', text)
    items = []

    for block in blocks:
        m = re.match(r'## (\d+)\. (.+)', block.strip())
        if not m:
            continue
        num = int(m.group(1))
        header = m.group(2).strip()

        # アカウント
        acc_m = re.search(r'@([\w\.]+)', header)
        account = acc_m.group(1) if acc_m else ""

        # ★レーティング
        stars = header.count('★')

        # URL
        url_m = re.search(r'\*\*URL\*\*:\s*(\S+)', block)
        url = url_m.group(1) if url_m else ""

        # 実績（views/likes/replies）
        stats_m = re.search(r'\*\*実績\*\*:\s*\*?\*?([^*\n]+)', block)
        stats = stats_m.group(1).strip() if stats_m else ""

        # 投稿日
        date_m = re.search(r'\*\*投稿日\*\*:\s*([^\n]+)', block)
        post_date = date_m.group(1).strip() if date_m else ""

        # 本文（### 本文 の直後の引用ブロック）
        body = ""
        body_m = re.search(r'### 本文\n((?:>\s.*\n?)+)', block)
        if body_m:
            body = re.sub(r'^>\s?', '', body_m.group(1), flags=re.MULTILINE).strip()

        # 型（### 型 セクション最初の数行）
        pattern = ""
        pattern_m = re.search(r'### 型\n((?:.+\n?){1,6})', block)
        if pattern_m:
            lines = [l.strip() for l in pattern_m.group(1).split('\n') if l.strip().startswith('-')]
            pattern_parts = []
            for l in lines[:3]:
                clean = re.sub(r'^-\s*\*?\*?', '', l)
                clean = re.sub(r'\*\*', '', clean)
                clean = clean.split('：')[0] if '：' in clean else clean
                pattern_parts.append(clean.strip())
            pattern = ' / '.join(pattern_parts)

        # 自分への示唆（### 自分への示唆 から最初の段落）
        insight = ""
        insight_m = re.search(r'### 自分への示唆\n(.+?)(?=\n###|\n---|\Z)', block, re.DOTALL)
        if insight_m:
            raw_ins = insight_m.group(1).strip()
            # 最初の段落のみ
            insight = raw_ins.split('\n\n')[0].strip()
            insight = re.sub(r'\*\*(.+?)\*\*', r'\1', insight)

        # スキップ条件: 本文も洞察もない=不完全なエントリ
        if not body and not insight:
            continue

        items.append({
            'num': num,
            'account': account,
            'header': header,
            'url': url,
            'stats': stats,
            'date': post_date,
            'body': body,
            'pattern': pattern,
            'insight': insight,
            'stars': stars,
        })

    return items


def parse_collect_file(project_root: Path) -> list[dict]:
    """最新の collect.md からリサーチアイテムを解析する."""
    import re
    from datetime import date
    today = date.today().isoformat()
    topics_dir = project_root / ".company" / "research" / "topics"
    collect_path = topics_dir / f"{today}-collect.md"
    if not collect_path.exists():
        files = sorted(topics_dir.glob("*-collect.md"), reverse=True)
        if not files:
            return []
        collect_path = files[0]

    text = collect_path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r'\n(?=## \d+\. )', text)
    items = []

    for block in blocks:
        m = re.match(r'## (\d+)\. (.+)', block.strip())
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()

        src_m = re.search(r'- ソース: (https?://\S+)', block)
        source = src_m.group(1).rstrip("),") if src_m else ""

        date_m = re.search(r'- 公開日: (.+)', block)
        pub_date = date_m.group(1).strip() if date_m else ""

        pts_block = re.search(r'- 要点:\n(.*?)(?=- 投稿アイデア:|\Z)', block, re.DOTALL)
        points = []
        if pts_block:
            for line in pts_block.group(1).splitlines():
                line = line.strip().lstrip('- ').strip()
                if line:
                    line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                    points.append(line)

        idea_m = re.search(r'- 切り口: [「『]?(.+)', block)
        idea = idea_m.group(1).strip().rstrip('」』') if idea_m else ""

        type_m = re.search(r'- 型: (.+)', block)
        post_type = type_m.group(1).strip() if type_m else ""

        if any(k in title for k in ["Threads", "スレッズ", "シャドウバン", "エンゲージメント", "投稿時間", "時間帯"]):
            cat = "Threads"
        elif any(k in title for k in ["Claude", "Anthropic", "AWS", "Opus", "Marketplace", "Platform"]):
            cat = "Claude最新"
        elif any(k in title for k in ["note", "有料記事", "メンバーシップ"]):
            cat = "note収益化"
        elif any(k in title for k in ["副業", "案件", "クラウドソーシング", "コモディティ", "月収", "収入", "手数料"]):
            cat = "AI副業"
        elif any(k in title for k in ["読書", "NotebookLM", "忘却", "0秒読書", "スローリーディング"]):
            cat = "読書"
        else:
            cat = "その他"

        urgent = "★★★" in block or "鮮度が命" in block

        items.append({
            "num": num, "title": title, "source": source, "pub_date": pub_date,
            "points": points[:3], "idea": idea, "post_type": post_type,
            "category": cat, "urgent": urgent,
        })

    return items


def load_research_data(project_root: Path) -> dict:
    """リサーチデータを読み込む."""
    inbox = project_root / ".company" / "research" / "topics" / "inbox"
    inbox_files = list(inbox.glob("*.md")) if inbox.exists() else []
    unused = sum(1 for f in inbox_files if "status: used" not in f.read_text(encoding="utf-8", errors="replace"))
    used = len(inbox_files) - unused

    # バズ分析ファイル
    buzz_path = project_root / ".company" / "research" / "topics" / "2026-05-16-buzz-analysis.md"
    buzz_text = buzz_path.read_text(encoding="utf-8") if buzz_path.exists() else ""

    items = parse_collect_file(project_root)

    return {
        "inbox_total": len(inbox_files),
        "inbox_unused": unused,
        "inbox_used": used,
        "buzz_exists": buzz_path.exists(),
        "buzz_text": buzz_text,
        "research_items": items,
    }


def generate_html(posts: list[dict], account: str, research: dict | None = None) -> str:
    # 時系列ソート
    posts_time = sorted(posts, key=lambda x: x.get("timestamp", ""))

    # 時間帯別・曜日別集計
    from collections import defaultdict
    hour_views = defaultdict(list)
    hour_likes = defaultdict(list)
    dow_views = defaultdict(list)
    DOW_LABELS = ["月", "火", "水", "木", "金", "土", "日"]
    for p in posts:
        ts = p.get("timestamp", "")
        if not ts:
            continue
        try:
            dt_obj = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz=None)
            h = dt_obj.hour
            d = dt_obj.weekday()
            hour_views[h].append(p["views"])
            hour_likes[h].append(p["likes"])
            dow_views[d].append(p["views"])
        except Exception:
            pass

    # 時間帯ラベル（0〜23）
    hour_labels = [f"{h}時" for h in range(24)]
    hour_avg_v = [round(sum(hour_views[h]) / len(hour_views[h])) if hour_views[h] else 0 for h in range(24)]
    hour_count = [len(hour_views[h]) for h in range(24)]
    best_hour = max(range(24), key=lambda h: hour_avg_v[h])
    worst_hours = [h for h in range(24) if h >= 23 or h <= 4]  # 深夜帯

    # 曜日別
    dow_avg_v = [round(sum(dow_views[d]) / len(dow_views[d])) if dow_views[d] else 0 for d in range(7)]
    dow_count = [len(dow_views[d]) for d in range(7)]
    best_dow = max(range(7), key=lambda d: dow_avg_v[d])

    total = len(posts)
    total_views = sum(p["views"] for p in posts)
    total_likes = sum(p["likes"] for p in posts)
    total_replies = sum(p["replies"] for p in posts)
    avg_views = total_views / total if total else 0
    max_views = max(p["views"] for p in posts) if posts else 0
    over300 = sum(1 for p in posts if p["views"] >= 300)
    over100 = sum(1 for p in posts if p["views"] >= 100)
    under50 = sum(1 for p in posts if p["views"] < 50)

    # ビュー順
    posts_sorted = sorted(posts, key=lambda x: x["views"], reverse=True)
    top15 = posts_sorted[:15]
    bottom10 = posts_sorted[-10:]

    # カテゴリ別平均
    from collections import defaultdict
    cat_views = defaultdict(list)
    for p in posts:
        cat = classify(p.get("text", ""))
        cat_views[cat].append(p["views"])
    cat_avg = {c: sum(v)/len(v) for c, v in cat_views.items()}
    cat_count = {c: len(v) for c, v in cat_views.items()}
    cat_sorted = sorted(cat_avg.items(), key=lambda x: x[1], reverse=True)

    # 時間帯チャート用データ
    hour_labels_js = json.dumps(hour_labels)
    hour_avg_js = json.dumps(hour_avg_v)
    hour_count_js = json.dumps(hour_count)
    hour_colors_js = json.dumps([
        "#ef444488" if h >= 23 or h <= 4 else
        "#4ade8088" if hour_avg_v[h] >= max(hour_avg_v) * 0.6 else
        "#60a5fa88"
        for h in range(24)
    ])
    dow_labels_js = json.dumps(DOW_LABELS)
    dow_avg_js = json.dumps(dow_avg_v)
    dow_count_js = json.dumps(dow_count)

    # チャート用データ
    labels_js = json.dumps([jst(p.get("timestamp",""))[5:16] for p in posts_time])
    views_js = json.dumps([p["views"] for p in posts_time])
    likes_js = json.dumps([p["likes"] for p in posts_time])

    cat_labels_js = json.dumps([c for c, _ in cat_sorted])
    cat_vals_js = json.dumps([round(v) for _, v in cat_sorted])
    cat_counts_js = json.dumps([cat_count[c] for c, _ in cat_sorted])
    cat_colors_js = json.dumps([
        "#4ade80" if v >= 300 else "#60a5fa" if v >= 150 else "#f472b6" if v >= 80 else "#6b7280"
        for _, v in cat_sorted
    ])

    # TOP15テーブル
    top15_rows = ""
    for i, p in enumerate(top15):
        medal = ["🥇","🥈","🥉","4","5","6","7","8","9","10","11","12","13","14","15"][i]
        text = (p.get("text") or "").replace("\n", " ")[:55]
        lr = f"{p['likes']/p['views']*100:.1f}%" if p["views"] > 0 else "-"
        bar = int(p["views"] / max(max_views, 1) * 180)
        cat = classify(p.get("text", ""))
        cat_color = {"日常共感":"#f472b6","弱さ開示":"#fb923c","問いかけ":"#4ade80","AIノウハウ":"#60a5fa","技術実装":"#6b7280","Discord技術":"#6b7280","報告だけ":"#ef4444","朝挨拶":"#94a3b8","その他":"#94a3b8"}.get(cat,"#94a3b8")
        href = p.get("permalink","")
        link = f'<a href="{href}" target="_blank" style="color:#64748b;margin-left:6px;">↗</a>' if href else ""
        top15_rows += f"""
<tr style="border-bottom:1px solid #1e293b;">
  <td style="padding:10px 8px;font-size:16px;text-align:center;">{medal}</td>
  <td style="padding:10px 8px;max-width:320px;">
    <div style="font-size:13px;color:#e2e8f0;">{text}{link}</div>
    <span style="font-size:10px;color:{cat_color};margin-top:3px;display:inline-block;border:1px solid {cat_color};border-radius:4px;padding:1px 6px;">{cat}</span>
  </td>
  <td style="padding:10px 8px;text-align:right;">
    <div style="display:flex;align-items:center;gap:6px;justify-content:flex-end;">
      <div style="width:{bar}px;height:6px;background:#4ade80;border-radius:3px;opacity:0.7;"></div>
      <span style="color:#4ade80;font-weight:bold;font-size:15px;">{p["views"]:,}</span>
    </div>
  </td>
  <td style="padding:10px 8px;text-align:right;color:#f472b6;">{p["likes"]}</td>
  <td style="padding:10px 8px;text-align:right;color:#a78bfa;">{p["replies"]}</td>
  <td style="padding:10px 8px;text-align:right;color:#fbbf24;font-size:12px;">{lr}</td>
</tr>"""

    # ワースト10テーブル
    bottom_rows = ""
    for p in bottom10:
        text = (p.get("text") or "").replace("\n", " ")[:55]
        cat = classify(p.get("text", ""))
        cat_color = {"技術実装":"#ef4444","Discord技術":"#ef4444","報告だけ":"#ef4444"}.get(cat,"#6b7280")
        bottom_rows += f"""
<tr style="border-bottom:1px solid #1e293b;">
  <td style="padding:8px;"><span style="color:#ef4444;font-weight:bold;">{p["views"]}</span></td>
  <td style="padding:8px;color:#94a3b8;font-size:13px;">{text}</td>
  <td style="padding:8px;"><span style="font-size:10px;color:{cat_color};border:1px solid {cat_color};border-radius:4px;padding:1px 6px;">{cat}</span></td>
  <td style="padding:8px;text-align:right;color:#f472b6;">{p["likes"]}</td>
</tr>"""

    # 時間帯テーブル行を事前生成
    nonzero_avgs = [v for v in hour_avg_v if v > 0]
    avg_nonzero = sum(nonzero_avgs) / len(nonzero_avgs) if nonzero_avgs else 0
    max_hour_v = max(hour_avg_v)
    hour_table_rows = ""
    for h in range(24):
        if hour_count[h] == 0:
            continue
        v = hour_avg_v[h]
        c = "#4ade80" if v == max_hour_v else "#60a5fa" if v >= avg_nonzero else "#6b7280"
        if v == max_hour_v:
            badge = '<span style="color:#4ade80;font-size:11px;">★ 最強</span>'
        elif h >= 23 or h <= 4:
            badge = '<span style="color:#ef4444;font-size:11px;">⚠ 深夜帯（要検証）</span>'
        else:
            badge = ""
        hour_table_rows += f'<tr style="border-bottom:1px solid #1e293b;"><td style="padding:7px 8px;color:#e2e8f0;">{h}時台</td><td style="padding:7px 8px;text-align:right;color:#64748b;">{hour_count[h]}投稿</td><td style="padding:7px 8px;text-align:right;font-weight:bold;color:{c};">{v:,}</td><td style="padding:7px 8px 7px 12px;">{badge}</td></tr>'

    # リサーチデータ
    r = research or {}
    inbox_total = r.get("inbox_total", 0)
    inbox_unused = r.get("inbox_unused", 0)
    inbox_used = r.get("inbox_used", 0)
    inbox_pct = int(inbox_used / inbox_total * 100) if inbox_total else 0

    # リサーチカード（カテゴリ別フィルタ）
    from collections import Counter as _Counter
    _cat_colors = {
        "Threads": "#60a5fa", "Claude最新": "#a78bfa", "note収益化": "#4ade80",
        "AI副業": "#fbbf24", "読書": "#f472b6", "その他": "#6b7280",
    }
    research_items = r.get("research_items", [])
    _cat_counts = _Counter(it["category"] for it in research_items)
    _urgent_count = sum(1 for it in research_items if it["urgent"])

    _filter_btns = f'<button onclick="filterCat(\'all\')" class="rfilter active" data-cat="all">全て（{len(research_items)}）</button>'
    for _cat, _col in _cat_colors.items():
        if _cat in _cat_counts:
            _filter_btns += f'<button onclick="filterCat(\'{_cat}\')" class="rfilter" data-cat="{_cat}" style="border-color:{_col};color:{_col};">{_cat}（{_cat_counts[_cat]}）</button>'

    _cards_html = ""
    for it in research_items:
        _col = _cat_colors.get(it["category"], "#6b7280")
        _ub = '<span style="background:#ef4444;color:white;font-size:10px;border-radius:4px;padding:1px 6px;margin-left:6px;">即投稿</span>' if it["urgent"] else ""
        _pts = "".join(f'<li style="color:#cbd5e1;font-size:12px;margin-bottom:3px;">{p}</li>' for p in it["points"])
        _src_d = it["source"].split("/")[2] if it["source"] and it["source"].count("/") >= 2 else ""
        _src = f'<a href="{it["source"]}" target="_blank" style="color:#475569;font-size:10px;text-decoration:none;">↗ {_src_d}</a>' if _src_d else ""
        _idea = f'<div style="background:#0f172a;border-radius:6px;padding:8px 10px;margin-top:8px;border-left:2px solid {_col};"><div style="font-size:10px;color:#64748b;margin-bottom:3px;">{it["post_type"]}</div><div style="font-size:12px;color:#e2e8f0;line-height:1.5;">{it["idea"]}</div></div>' if it["idea"] else ""
        _cards_html += f'<div class="rcard" data-cat="{it["category"]}" style="background:#1e293b;border-radius:10px;padding:16px;border-top:2px solid {_col};"><div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap;"><span style="font-size:10px;border:1px solid {_col};color:{_col};border-radius:4px;padding:1px 6px;">{it["category"]}</span>{_ub}<span style="color:#475569;font-size:10px;margin-left:auto;">{it["pub_date"]}</span></div><div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:8px;line-height:1.5;">#{it["num"]} {it["title"]}</div><ul style="padding-left:14px;margin-bottom:4px;">{_pts}</ul>{_idea}<div style="margin-top:8px;">{_src}</div></div>'

    research_section_html = f"""
<style>
.rfilter{{background:transparent;border:1px solid #334155;color:#64748b;border-radius:20px;padding:5px 14px;font-size:12px;cursor:pointer;transition:all .15s;}}
.rfilter:hover{{background:#1e293b;}}
.rfilter.active{{background:#1e293b;font-weight:600;}}
.rcard.hidden{{display:none;}}
.rcards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;}}
</style>
<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;color:#e2e8f0;border-left:3px solid #60a5fa;padding-left:12px;">リサーチ DB（カテゴリ別）<span style="font-size:13px;color:#64748b;font-weight:400;margin-left:12px;">{len(research_items)}件収集 / 即投稿推奨 {_urgent_count}件</span></h2>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">{_filter_btns}</div>
<div class="rcards-grid">{_cards_html}</div>
<script>
function filterCat(cat) {{
  document.querySelectorAll('.rcard').forEach(el => {{
    el.classList.toggle('hidden', cat !== 'all' && el.dataset.cat !== cat);
  }});
  document.querySelectorAll('.rfilter').forEach(btn => {{
    btn.classList.toggle('active', btn.dataset.cat === cat);
  }});
}}
</script>
""" if research_items else ""

    # バズ参考カード
    buzz_items = parse_buzz_references(SCRIPT_DIR.parent)
    _buzz_cards = ""
    for it in buzz_items:
        star_str = "★" * it["stars"] if it["stars"] else ""
        star_color = "#fbbf24" if it["stars"] >= 3 else "#a78bfa" if it["stars"] >= 2 else "#64748b"
        # ボディは80文字で切る
        body_short = it["body"][:160] + ("…" if len(it["body"]) > 160 else "")
        url_link = f'<a href="{it["url"]}" target="_blank" style="color:#475569;font-size:10px;text-decoration:none;">↗ 元投稿を見る</a>' if it["url"] else ""
        insight_short = it["insight"][:200] + ("…" if len(it["insight"]) > 200 else "")
        _buzz_cards += (
            f'<div style="background:#1e293b;border-radius:10px;padding:16px;border-top:2px solid {star_color};">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">'
            f'<span style="font-size:14px;font-weight:700;color:#e2e8f0;">@{it["account"]}</span>'
            f'<span style="color:{star_color};font-size:11px;">{star_str}</span>'
            f'<span style="color:#64748b;font-size:10px;margin-left:auto;">{it["date"]}</span>'
            f'</div>'
            f'<div style="background:#0f172a;border-radius:6px;padding:6px 10px;margin-bottom:8px;font-size:11px;color:#a78bfa;font-weight:600;">{it["stats"]}</div>'
            f'<div style="font-size:12px;color:#cbd5e1;line-height:1.6;margin-bottom:10px;border-left:2px solid #334155;padding-left:10px;font-style:italic;">{body_short}</div>'
            f'<div style="background:#0f172a;border-radius:6px;padding:8px 10px;margin-bottom:8px;">'
            f'<div style="font-size:10px;color:#64748b;margin-bottom:3px;">型</div>'
            f'<div style="font-size:11px;color:#60a5fa;line-height:1.5;">{it["pattern"]}</div>'
            f'</div>'
            f'<div style="background:#0f172a;border-radius:6px;padding:8px 10px;border-left:2px solid #4ade80;">'
            f'<div style="font-size:10px;color:#64748b;margin-bottom:3px;">自分への示唆</div>'
            f'<div style="font-size:11px;color:#cbd5e1;line-height:1.6;">{insight_short}</div>'
            f'</div>'
            f'<div style="margin-top:8px;">{url_link}</div>'
            f'</div>'
        )

    buzz_section_html = f"""
<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;color:#e2e8f0;border-left:3px solid #fbbf24;padding-left:12px;">バズ投稿リファレンス（学習素材）<span style="font-size:13px;color:#64748b;font-weight:400;margin-left:12px;">{len(buzz_items)}本収集 / Phase 2 ルーチンの根拠</span></h2>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin-bottom:24px;">{_buzz_cards}</div>
""" if buzz_items else ""

    note_article_html = parse_note_article(SCRIPT_DIR.parent)
    roadmap_html = generate_roadmap_html(total, avg_views)
    daily_rows, daily_labels_js, daily_counts_js, daily_avgs_js = generate_daily_html(posts)
    daily_total_days = len(daily_labels_js.split(',')) if daily_labels_js != '[]' else 0
    daily_avg_per_day = round(total / daily_total_days, 1) if daily_total_days else 0

    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@{account} パフォーマンスレポート</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{background:#0f172a;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:28px;line-height:1.6;}}
  h1{{font-size:22px;font-weight:700;margin-bottom:4px;}}
  .sub{{color:#64748b;font-size:13px;margin-bottom:28px;}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-bottom:28px;}}
  .kpi{{background:#1e293b;border-radius:12px;padding:18px 20px;}}
  .kpi-label{{color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;}}
  .kpi-value{{font-size:30px;font-weight:700;}}
  .kpi-sub{{color:#64748b;font-size:11px;margin-top:4px;}}
  .section{{background:#1e293b;border-radius:12px;padding:24px;margin-bottom:20px;}}
  .section h2{{font-size:14px;color:#94a3b8;margin-bottom:18px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;}}
  table{{width:100%;border-collapse:collapse;}}
  thead th{{padding:8px;text-align:left;color:#64748b;font-size:11px;font-weight:normal;border-bottom:1px solid #334155;}}
  tbody tr:hover{{background:#ffffff08;}}
  .badge{{display:inline-block;font-size:10px;border-radius:4px;padding:2px 7px;border:1px solid;}}
  .card-row{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;}}
  .insight-card{{background:#1e293b;border-radius:12px;padding:20px;}}
  .insight-card h3{{font-size:13px;margin-bottom:14px;}}
  .insight-item{{display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;font-size:13px;color:#cbd5e1;}}
  .dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;margin-top:5px;}}
  .action-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px;}}
  .action-card{{background:#1e293b;border-radius:12px;padding:20px;border-left:3px solid;}}
  .action-num{{font-size:28px;font-weight:700;margin-bottom:8px;}}
  .action-title{{font-size:14px;font-weight:600;margin-bottom:8px;}}
  .action-body{{font-size:12px;color:#94a3b8;line-height:1.7;}}
  @media(max-width:700px){{.card-row,.action-grid{{grid-template-columns:1fr;}}}}
  .tab-nav{{display:flex;gap:6px;flex-wrap:wrap;margin:20px 0 24px;border-bottom:1px solid #334155;padding-bottom:0;}}
  .tab-btn{{background:transparent;border:none;border-bottom:3px solid transparent;color:#64748b;font-size:13px;font-weight:600;padding:10px 18px;cursor:pointer;transition:all .15s;white-space:nowrap;margin-bottom:-1px;}}
  .tab-btn:hover{{color:#cbd5e1;}}
  .tab-btn.active{{color:#e2e8f0;border-bottom-color:#60a5fa;}}
  .tab-pane{{display:none;}}
  .tab-pane.active{{display:block;}}
</style>
</head>
<body>

<h1>@{account} Threads パフォーマンスレポート</h1>
<p class="sub">取得: {fetched_at} JST ／ 全 {total} 投稿 ／ リアルタイムデータ (Threads API)</p>

<!-- KPI -->
<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-label">総投稿数</div>
    <div class="kpi-value" style="color:#60a5fa;">{total}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">最高ビュー</div>
    <div class="kpi-value" style="color:#4ade80;">{max_views:,}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">平均ビュー</div>
    <div class="kpi-value" style="color:#a78bfa;">{avg_views:,.0f}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">総いいね</div>
    <div class="kpi-value" style="color:#f472b6;">{total_likes:,}</div>
    <div class="kpi-sub">総返信 {total_replies}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">300超え</div>
    <div class="kpi-value" style="color:#fb923c;">{over300}</div>
    <div class="kpi-sub">全体の{over300/total*100:.0f}%</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">100超え</div>
    <div class="kpi-value" style="color:#34d399;">{over100}</div>
    <div class="kpi-sub">全体の{over100/total*100:.0f}%</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">50未満（死に投稿）</div>
    <div class="kpi-value" style="color:#ef4444;">{under50}</div>
    <div class="kpi-sub">全体の{under50/total*100:.0f}%</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">総ビュー</div>
    <div class="kpi-value" style="color:#fbbf24;">{total_views:,}</div>
  </div>
</div>

<!-- タブナビ -->
<nav class="tab-nav">
  <button class="tab-btn active" onclick="switchTab('roadmap')">ロードマップ</button>
  <button class="tab-btn" onclick="switchTab('dash')">ダッシュボード</button>
  <button class="tab-btn" onclick="switchTab('posts')">投稿分析</button>
  <button class="tab-btn" onclick="switchTab('time')">時間帯分析</button>
  <button class="tab-btn" onclick="switchTab('research')">リサーチ</button>
  <button class="tab-btn" onclick="switchTab('note')">note記事</button>
</nav>

<div class="tab-pane active" id="tab-roadmap">
{roadmap_html}
</div><!-- /tab-roadmap -->

<div class="tab-pane" id="tab-dash">

<!-- アクション3つ -->
<div class="action-grid">
  <div class="action-card" style="border-color:#4ade80;">
    <div class="action-num" style="color:#4ade80;">①</div>
    <div class="action-title">問いかけで終わらせる</div>
    <div class="action-body">「〜ですか？」「〜いますか？」で終わると<br>いいね率・返信率が約5倍。<br>最高いいね52、返信35はすべて問いかけ型。</div>
  </div>
  <div class="action-card" style="border-color:#fb923c;">
    <div class="action-num" style="color:#fb923c;">②</div>
    <div class="action-title">月3〜4本は日常ネタを入れる</div>
    <div class="action-body">AIと無関係の母の日・時事・あるあるが<br>全体2位のビュー数(1,804)。<br>Threadsユーザー全体にリーチできるから。</div>
  </div>
  <div class="action-card" style="border-color:#ef4444;">
    <div class="action-num" style="color:#ef4444;">③</div>
    <div class="action-title">技術実装・報告だけをやめる</div>
    <div class="action-body">Discord Bot/GeminiCLI/アプリ実装系は<br>平均15〜34views。ターゲット層に届かない。<br>「note N日連続！！」は0〜100views止まり。</div>
  </div>
</div>

<!-- チャート：ビュー推移 -->
<div class="section">
  <h2>ビュー推移（全投稿・時系列）</h2>
  <canvas id="timeChart" height="70"></canvas>
</div>

<!-- カテゴリ別平均 -->
<div class="section">
  <h2>カテゴリ別 平均ビュー（データ検証）</h2>
  <canvas id="catChart" height="60"></canvas>
</div>

<!-- インサイト -->
<div class="card-row">
  <div class="insight-card">
    <h3 style="color:#4ade80;">伸びる投稿の共通パターン</h3>
    <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>「ぶっちゃけ」「はっきり言うと」で始まる</div>
    <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>弱さ＋数字（0円、全然読まれない、あと20人）</div>
    <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>「〜ですか？」「🤔」「🥹」で終わる</div>
    <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>AI関係ない日常ネタ（季節・あるある・時事）</div>
    <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>Claude具体ノウハウ（トークン節約など）</div>
  </div>
  <div class="insight-card">
    <h3 style="color:#ef4444;">伸びない投稿のパターン</h3>
    <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>技術実装系（Discord Bot、GeminiCLI）</div>
    <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>報告だけ（note連続N日！！）</div>
    <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>アプリ作りました / テスト中です</div>
    <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>自分に閉じた話（ターゲットが共感できない）</div>
    <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>問いかけなし・返信を求めない構造</div>
  </div>
</div>

</div><!-- /tab-dash -->

<div class="tab-pane" id="tab-posts">

<!-- 日次投稿数 -->
<div class="section" style="margin-bottom:20px;">
  <h2>日次投稿数（{daily_total_days}日間 / 1日平均 {daily_avg_per_day}本）</h2>
  <canvas id="dailyChart" height="60"></canvas>
  <div style="margin-top:18px;overflow-x:auto;max-height:380px;overflow-y:auto;">
    <table style="min-width:560px;">
      <thead style="position:sticky;top:0;background:#1e293b;"><tr>
        <th style="text-align:left;">日付</th>
        <th style="text-align:right;">投稿数</th>
        <th style="text-align:right;">平均views</th>
        <th style="text-align:right;">最高views</th>
        <th style="text-align:right;">合計views</th>
      </tr></thead>
      <tbody>{daily_rows}</tbody>
    </table>
  </div>
  <div style="margin-top:12px;font-size:11px;color:#64748b;">
    バッジ色：<span style="color:#4ade80;">緑=8本以上</span> / <span style="color:#60a5fa;">青=5-7本</span> / <span style="color:#fbbf24;">黄=3-4本</span> / <span style="color:#94a3b8;">グレー=1-2本</span>
  </div>
</div>

<!-- TOP15 -->
<div class="section">
  <h2>TOP 15 投稿</h2>
  <table>
    <thead><tr>
      <th style="width:36px;"></th>
      <th>本文</th>
      <th style="text-align:right;">Views</th>
      <th style="text-align:right;">Likes</th>
      <th style="text-align:right;">返信</th>
      <th style="text-align:right;">いいね率</th>
    </tr></thead>
    <tbody>{top15_rows}</tbody>
  </table>
</div>

<!-- ワースト10 -->
<div class="section">
  <h2>WORST 10 投稿（なぜ伸びなかったかを確認）</h2>
  <table>
    <thead><tr>
      <th style="text-align:left;">Views</th>
      <th>本文</th>
      <th>カテゴリ</th>
      <th style="text-align:right;">Likes</th>
    </tr></thead>
    <tbody>{bottom_rows}</tbody>
  </table>
</div>

<!-- 全投稿チャート -->
<div class="section">
  <h2>全投稿一覧（ビュー数バー）</h2>
  <canvas id="allChart" height="120"></canvas>
</div>

</div><!-- /tab-posts -->

<div class="tab-pane" id="tab-time">

<!-- ========== 時間帯・曜日分析 ========== -->
<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;color:#e2e8f0;border-left:3px solid #60a5fa;padding-left:12px;">時間帯・曜日分析</h2>

<!-- 時間帯別 -->
<div class="section" style="margin-bottom:20px;">
  <h2>時間帯別 平均ビュー（全{total}投稿）</h2>
  <canvas id="hourChart" height="70"></canvas>
  <div style="margin-top:16px;display:flex;gap:24px;flex-wrap:wrap;">
    <div style="background:#0f172a;border-radius:8px;padding:12px 20px;border-left:3px solid #4ade80;">
      <div style="font-size:11px;color:#64748b;">最強時間帯</div>
      <div style="font-size:22px;font-weight:700;color:#4ade80;">{best_hour}時台</div>
      <div style="font-size:12px;color:#94a3b8;">平均 {hour_avg_v[best_hour]:,}views（{hour_count[best_hour]}投稿）</div>
    </div>
    <div style="background:#0f172a;border-radius:8px;padding:12px 20px;border-left:3px solid #ef4444;">
      <div style="font-size:11px;color:#64748b;">深夜帯（23時以降）の観察メモ</div>
      <div style="font-size:15px;font-weight:700;color:#ef4444;margin-top:4px;">2026-05-16 23:30以降 → リアクション激減</div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">本人観察。深夜帯は今後も検証を続ける。現時点では避けた方が無難。</div>
    </div>
  </div>

  <!-- 時間帯別サマリテーブル -->
  <div style="margin-top:16px;overflow-x:auto;">
    <table style="min-width:600px;">
      <thead><tr>
        <th>時間帯</th>
        <th style="text-align:right;">投稿数</th>
        <th style="text-align:right;">平均Views</th>
        <th style="text-align:left;padding-left:12px;">評価</th>
      </tr></thead>
      <tbody>{hour_table_rows}</tbody>
    </table>
  </div>
</div>

<!-- 曜日別 -->
<div class="section" style="margin-bottom:20px;">
  <h2>曜日別 平均ビュー</h2>
  <canvas id="dowChart" height="60"></canvas>
  <div style="margin-top:12px;font-size:12px;color:#64748b;">
    最強曜日: <strong style="color:#4ade80;">{DOW_LABELS[best_dow]}曜日</strong>（平均 {dow_avg_v[best_dow]:,}views・{dow_count[best_dow]}投稿）
  </div>
</div>

</div><!-- /tab-time -->

<div class="tab-pane" id="tab-research">

<!-- ========== リサーチデータベース ========== -->
<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;color:#e2e8f0;border-left:3px solid #a78bfa;padding-left:12px;">リサーチデータベース</h2>

<!-- ネタ inbox -->
<div class="section" style="margin-bottom:20px;">
  <h2>ネタ inbox 残弾数</h2>
  <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:48px;font-weight:700;color:#4ade80;">{inbox_unused}</div>
      <div style="color:#64748b;font-size:12px;">未使用（すぐ投稿化できる）</div>
    </div>
    <div style="flex:1;min-width:200px;">
      <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:6px;">
        <span>使用済 {inbox_used}件</span><span>合計 {inbox_total}件</span>
      </div>
      <div style="background:#334155;border-radius:8px;height:12px;overflow:hidden;">
        <div style="width:{inbox_pct}%;height:100%;background:linear-gradient(90deg,#60a5fa,#a78bfa);border-radius:8px;"></div>
      </div>
      <div style="color:#94a3b8;font-size:12px;margin-top:8px;">使用率 {inbox_pct}%｜残り {inbox_unused} 本が未投稿ネタとして待機中</div>
    </div>
  </div>
</div>

<!-- 発見した重要数字 -->
<div class="section" style="margin-bottom:20px;">
  <h2>リサーチで発見した重要な数字</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #4ade80;">
      <div style="font-size:28px;font-weight:700;color:#4ade80;">119万円</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">AI副業の年間平均収入</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">月換算で約10万円。ぼくの目標と一致</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #ef4444;">
      <div style="font-size:28px;font-weight:700;color:#ef4444;">9割</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">AI副業を3ヶ月以内にやめる人の割合</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">続けるだけで上位10%に入れる</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #f472b6;">
      <div style="font-size:28px;font-weight:700;color:#f472b6;">1,842円</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">noteノウハウ記事の平均価格</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">読み物系(983円)の約1.9倍</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #fb923c;">
      <div style="font-size:28px;font-weight:700;color:#fb923c;">+268%</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">noteのAI活用ジャンル売上前年比</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">今書くのが一番タイミングいい</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #a78bfa;">
      <div style="font-size:28px;font-weight:700;color:#a78bfa;">3.2倍</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">クラウドソーシングAI案件数(2024比)</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">月5,000〜30,000円の小口案件が増加</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #34d399;">
      <div style="font-size:28px;font-weight:700;color:#34d399;">+80%</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">noteメンバーシップ成長率（前年比）</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">単発販売より継続課金が主役化</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #60a5fa;">
      <div style="font-size:28px;font-weight:700;color:#60a5fa;">5〜24万</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">Claude Code受託副業の月収レンジ</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">初月5万〜月24万。詰まる原因は単価じゃなく契約</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;border-left:3px solid #fbbf24;">
      <div style="font-size:28px;font-weight:700;color:#fbbf24;">63%</div>
      <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">vibe codingユーザーが非エンジニア</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">ターゲット層がAIで開発参入している証拠</div>
    </div>
  </div>
</div>

<!-- Threadsアルゴリズム攻略メモ -->
<div class="section" style="margin-bottom:20px;">
  <h2>Threadsアルゴリズム攻略メモ（リサーチ済み・公式出典）</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
    <div>
      <div style="font-size:12px;color:#4ade80;margin-bottom:12px;font-weight:600;text-transform:uppercase;">やるべきこと</div>
      <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>投稿後<strong style="color:#4ade80;">30〜60分</strong>はリプ返しに集中（Stage1評価が決まる）</div>
      <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>Mosseri公式：「リプライ＝投稿と同等の価値」→ 投稿時間の半分をリプに使う</div>
      <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>「いいね」より「保存」「コメント」を促すCTAの方が拡散効率が高い</div>
      <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>1コメ目に体験談・根拠データを置く（2026/2アプデで本文＋コメントが評価対象化）</div>
      <div class="insight-item"><div class="dot" style="background:#4ade80;"></div>タグは1投稿1つに統一</div>
    </div>
    <div>
      <div style="font-size:12px;color:#ef4444;margin-bottom:12px;font-weight:600;text-transform:uppercase;">やめるべきこと</div>
      <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>本文に外部URLを直貼り → プロフィール経由に変える</div>
      <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>投稿してスマホを置く → 1時間張り付いてリプ返す</div>
      <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>24時間で50リプより<strong style="color:#ef4444;">30分で20リプ</strong>の方が拡散される（速度が命）</div>
      <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>「いいねしてください」→ アルゴリズム評価で不利</div>
      <div class="insight-item"><div class="dot" style="background:#ef4444;"></div>全投稿の50%が返信で構成 → 自分の投稿だけ頑張っても届かない</div>
    </div>
  </div>
</div>

<!-- バズ投稿分析 -->
<div class="section" style="margin-bottom:20px;">
  <h2>バズ投稿9本分析（参考アカウント）</h2>
  <table>
    <thead><tr>
      <th>アカウント</th>
      <th>冒頭</th>
      <th style="text-align:right;">Views</th>
      <th style="text-align:right;">Likes</th>
      <th style="text-align:right;">Replies</th>
      <th>パターン</th>
    </tr></thead>
    <tbody>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@kaoli___</td><td style="padding:8px;font-size:13px;">夫にコンビニ行くならカフェラテ買ってきてー！と言うと…</td><td style="padding:8px;text-align:right;font-weight:bold;color:#4ade80;">627K</td><td style="padding:8px;text-align:right;">1,800</td><td style="padding:8px;text-align:right;">69</td><td style="padding:8px;"><span class="badge" style="color:#f472b6;border-color:#f472b6;">日常情景</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@mihashi.keitaro</td><td style="padding:8px;font-size:13px;">Threadsを始めて18日！今まで180万閲覧 2.5万いいね</td><td style="padding:8px;text-align:right;font-weight:bold;color:#4ade80;">88.8K</td><td style="padding:8px;text-align:right;">542</td><td style="padding:8px;text-align:right;color:#a78bfa;font-weight:bold;">773</td><td style="padding:8px;"><span class="badge" style="color:#60a5fa;border-color:#60a5fa;">全公開截断</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@reen_aka._.nuke</td><td style="padding:8px;font-size:13px;">マジでやって良かった男磨きランキング10選</td><td style="padding:8px;text-align:right;font-weight:bold;color:#60a5fa;">69.6K</td><td style="padding:8px;text-align:right;">186</td><td style="padding:8px;text-align:right;">5</td><td style="padding:8px;"><span class="badge" style="color:#fbbf24;border-color:#fbbf24;">保存型リスト</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@suisuinote</td><td style="padding:8px;font-size:13px;">たった1ヶ月で万垢作りました。冒頭に命かけてます</td><td style="padding:8px;text-align:right;font-weight:bold;color:#60a5fa;">28.5K</td><td style="padding:8px;text-align:right;">107</td><td style="padding:8px;text-align:right;">3</td><td style="padding:8px;"><span class="badge" style="color:#60a5fa;border-color:#60a5fa;">実績+截断</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@llovefav</td><td style="padding:8px;font-size:13px;">カフェで小説読んでたけど、やっぱり静かで人がいないとこが好き</td><td style="padding:8px;text-align:right;font-weight:bold;color:#60a5fa;">12.9K</td><td style="padding:8px;text-align:right;">794</td><td style="padding:8px;text-align:right;">11</td><td style="padding:8px;"><span class="badge" style="color:#f472b6;border-color:#f472b6;">日常自己発見</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@renkinlabo01</td><td style="padding:8px;font-size:13px;">Threads始めて 23日→6,000人 24日→8,000人…</td><td style="padding:8px;text-align:right;font-weight:bold;color:#94a3b8;">6K</td><td style="padding:8px;text-align:right;">131</td><td style="padding:8px;text-align:right;">28</td><td style="padding:8px;"><span class="badge" style="color:#34d399;border-color:#34d399;">動く数字</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@mufufufufu22</td><td style="padding:8px;font-size:13px;">なんてこと！！！ たった5日でフォロワーさんが50人に😭</td><td style="padding:8px;text-align:right;font-weight:bold;color:#94a3b8;">6.9K</td><td style="padding:8px;text-align:right;">241</td><td style="padding:8px;text-align:right;">30</td><td style="padding:8px;"><span class="badge" style="color:#34d399;border-color:#34d399;">動く数字</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@ao_maru_ao</td><td style="padding:8px;font-size:13px;">勇気出して言うけど…30代なのに貯金100万円ありません🫠</td><td style="padding:8px;text-align:right;font-weight:bold;color:#94a3b8;">200K</td><td style="padding:8px;text-align:right;color:#f472b6;font-weight:bold;">2,900</td><td style="padding:8px;text-align:right;">288</td><td style="padding:8px;"><span class="badge" style="color:#fb923c;border-color:#fb923c;">弱さ開示</span></td></tr>
      <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">@iamami62</td><td style="padding:8px;font-size:13px;">本を読んでいたら、コーヒーの氷が溶けてた。</td><td style="padding:8px;text-align:right;font-weight:bold;color:#94a3b8;">1.2K</td><td style="padding:8px;text-align:right;">137</td><td style="padding:8px;text-align:right;">2</td><td style="padding:8px;"><span class="badge" style="color:#f472b6;border-color:#f472b6;">超短文情景</span></td></tr>
    </tbody>
  </table>
  <div style="margin-top:16px;padding:14px;background:#0f172a;border-radius:8px;font-size:13px;color:#94a3b8;line-height:1.8;">
    <strong style="color:#fbbf24;">最強の学び：</strong>
    「勇気出して言うけど」は最強の前置き。「同じような人いますか？」で返信率3倍。画像ありの投稿はなしの<strong style="color:#4ade80;">500倍以上のビュー差</strong>が出る（627K vs 1.2K）。
  </div>
</div>

<!-- note売れる方程式 -->
<div class="section" style="margin-bottom:20px;">
  <h2>note収益化の方程式（リサーチ済み）</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;">
    <div style="background:#0f172a;border-radius:10px;padding:16px;text-align:center;">
      <div style="font-size:22px;font-weight:700;color:#4ade80;margin-bottom:8px;">無料3：有料1</div>
      <div style="font-size:12px;color:#94a3b8;">黄金比。先に価値を体感させてから有料を出す</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;text-align:center;">
      <div style="font-size:22px;font-weight:700;color:#f472b6;margin-bottom:8px;">数字入りタイトル</div>
      <div style="font-size:12px;color:#94a3b8;">「月10万円」「3ステップ」で購入率約2倍</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;text-align:center;">
      <div style="font-size:22px;font-weight:700;color:#a78bfa;margin-bottom:8px;">500円→1,500円→3,000円</div>
      <div style="font-size:12px;color:#94a3b8;">段階的価格引き上げが定石。いきなり高単価はNG</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:16px;text-align:center;">
      <div style="font-size:22px;font-weight:700;color:#fbbf24;margin-bottom:8px;">文字数と売上は無相関</div>
      <div style="font-size:12px;color:#94a3b8;">30万記事の統計で相関ほぼゼロ。量より「無料エリアの価値提示」</div>
    </div>
  </div>
</div>

{research_section_html}

{buzz_section_html}

</div><!-- /tab-research -->

<div class="tab-pane" id="tab-note">
<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;color:#e2e8f0;border-left:3px solid #4ade80;padding-left:12px;">note記事プレビュー（下書き）</h2>
<div style="background:#1e293b;border-radius:12px;padding:24px;border:1px solid #334155;">{note_article_html}</div>
</div><!-- /tab-note -->

<script>
function switchTab(id) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b => {{
    if (b.getAttribute('onclick') === "switchTab('" + id + "')") b.classList.add('active');
  }});
}}

function switchNote(idx) {{
  document.querySelectorAll('.note-pane').forEach((p, i) => {{
    p.classList.toggle('note-pane-active', i === idx);
  }});
  document.querySelectorAll('.note-btn').forEach((b, i) => {{
    b.classList.toggle('note-btn-active', i === idx);
  }});
}}

// 日次投稿数
new Chart(document.getElementById('dailyChart'), {{
  type: 'bar',
  data: {{
    labels: {daily_labels_js},
    datasets: [
      {{
        type: 'bar',
        label: '投稿数',
        data: {daily_counts_js},
        backgroundColor: {daily_counts_js}.map(n => n>=8?'#4ade80':n>=5?'#60a5fa':n>=3?'#fbbf24':'#94a3b8'),
        borderRadius: 3,
        yAxisID: 'y',
      }},
      {{
        type: 'line',
        label: '平均views',
        data: {daily_avgs_js},
        borderColor: '#a78bfa',
        backgroundColor: '#a78bfa',
        tension: 0.3,
        yAxisID: 'y1',
        pointRadius: 3,
      }}
    ]
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    scales: {{
      x: {{ticks:{{color:'#64748b',maxRotation:60,font:{{size:10}}}}, grid:{{color:'#1e293b'}}}},
      y: {{type:'linear',position:'left',ticks:{{color:'#64748b',precision:0}}, grid:{{color:'#334155'}}, title:{{display:true,text:'投稿数',color:'#64748b',font:{{size:10}}}}}},
      y1: {{type:'linear',position:'right',ticks:{{color:'#a78bfa'}}, grid:{{display:false}}, title:{{display:true,text:'平均views',color:'#a78bfa',font:{{size:10}}}}}}
    }},
    plugins: {{
      legend: {{labels:{{color:'#cbd5e1',font:{{size:11}}}}}}
    }}
  }}
}});

// 時間帯別
new Chart(document.getElementById('hourChart'), {{
  type: 'bar',
  data: {{
    labels: {hour_labels_js},
    datasets: [{{
      label: '平均Views',
      data: {hour_avg_js},
      backgroundColor: {hour_colors_js},
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{
      x: {{ticks:{{color:'#64748b',font:{{size:10}}}}, grid:{{color:'#1e293b'}}}},
      y: {{ticks:{{color:'#64748b'}}, grid:{{color:'#334155'}}}}
    }},
    plugins: {{
      legend: {{display:false}},
      tooltip: {{
        callbacks: {{
          label: ctx => {{
            const counts = {hour_count_js};
            return ` 平均 ${{ctx.parsed.y}}views（${{counts[ctx.dataIndex]}}投稿）`;
          }}
        }}
      }}
    }}
  }}
}});

// 曜日別
new Chart(document.getElementById('dowChart'), {{
  type: 'bar',
  data: {{
    labels: {dow_labels_js},
    datasets: [{{
      label: '平均Views',
      data: {dow_avg_js},
      backgroundColor: {dow_avg_js}.map((v,i) => v === Math.max(...{dow_avg_js}) ? '#4ade8088' : '#60a5fa55'),
      borderColor: {dow_avg_js}.map((v,i) => v === Math.max(...{dow_avg_js}) ? '#4ade80' : '#60a5fa'),
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{
      x: {{ticks:{{color:'#64748b',font:{{size:13}}}}, grid:{{color:'#1e293b'}}}},
      y: {{ticks:{{color:'#64748b'}}, grid:{{color:'#334155'}}}}
    }},
    plugins: {{
      legend: {{display:false}},
      tooltip: {{
        callbacks: {{
          label: ctx => {{
            const counts = {dow_count_js};
            return ` 平均 ${{ctx.parsed.y}}views（${{counts[ctx.dataIndex]}}投稿）`;
          }}
        }}
      }}
    }}
  }}
}});

// 時系列
new Chart(document.getElementById('timeChart'), {{
  type: 'line',
  data: {{
    labels: {labels_js},
    datasets: [
      {{label:'Views', data:{views_js}, borderColor:'#60a5fa', backgroundColor:'#60a5fa22', tension:0.3, fill:true, yAxisID:'y'}},
      {{label:'Likes', data:{likes_js}, borderColor:'#f472b6', backgroundColor:'transparent', tension:0.3, yAxisID:'y2'}}
    ]
  }},
  options: {{
    responsive:true,
    scales:{{
      x:{{ticks:{{color:'#64748b',maxRotation:45,font:{{size:10}}}}, grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b'}}, grid:{{color:'#334155'}}, title:{{display:true,text:'Views',color:'#94a3b8'}}}},
      y2:{{position:'right', ticks:{{color:'#f472b6'}}, grid:{{drawOnChartArea:false}}, title:{{display:true,text:'Likes',color:'#f472b6'}}}}
    }},
    plugins:{{legend:{{labels:{{color:'#94a3b8'}}}}}}
  }}
}});

// カテゴリ別
new Chart(document.getElementById('catChart'), {{
  type: 'bar',
  data: {{
    labels: {cat_labels_js},
    datasets: [{{
      label: '平均Views',
      data: {cat_vals_js},
      backgroundColor: {cat_colors_js},
      borderRadius: 6,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    scales: {{
      x: {{ticks:{{color:'#64748b'}}, grid:{{color:'#334155'}}}},
      y: {{ticks:{{color:'#e2e8f0',font:{{size:12}}}}, grid:{{color:'#1e293b'}}}}
    }},
    plugins: {{
      legend: {{display:false}},
      tooltip: {{
        callbacks: {{
          label: function(ctx) {{
            const counts = {cat_counts_js};
            return ` 平均 ${{ctx.parsed.x}}views（${{counts[ctx.dataIndex]}}本）`;
          }}
        }}
      }}
    }}
  }}
}});

// 全投稿バー
const allData = {views_js};
const allLabels = {labels_js};
const avgV = {avg_views:.0f};
new Chart(document.getElementById('allChart'), {{
  type: 'bar',
  data: {{
    labels: allLabels,
    datasets: [{{
      label: 'Views',
      data: allData,
      backgroundColor: allData.map(v => v>=300?'#4ade8099':v>=100?'#60a5fa88':'#6b728066'),
      borderColor: allData.map(v => v>=300?'#4ade80':v>=100?'#60a5fa':'#6b7280'),
      borderWidth: 1,
      borderRadius: 3,
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{
      x: {{ticks:{{color:'#64748b',maxRotation:60,font:{{size:9}}}}, grid:{{color:'#1e293b'}}}},
      y: {{ticks:{{color:'#64748b'}}, grid:{{color:'#334155'}}}}
    }},
    plugins: {{
      legend: {{display:false}},
      annotation: {{}}
    }}
  }}
}});
</script>
</body>
</html>"""
    return html


def main():
    account = sys.argv[1] if len(sys.argv) > 1 else "gaku_ai_life"
    print(f"[fetch_all_metrics] {account} — 全投稿取得中...")
    client = ThreadsClient.from_env(account=account)

    posts = fetch_all_posts(client)
    print(f"  → {len(posts)} 投稿")

    print("  → インサイト取得中...")
    for i, p in enumerate(posts):
        m = fetch_insights(client, p["id"])
        p["views"] = m.get("views", 0) or 0
        p["likes"] = m.get("likes", 0) or 0
        p["replies"] = m.get("replies", 0) or 0
        p["reposts"] = m.get("reposts", 0) or 0
        print(f"  [{i+1}/{len(posts)}] views:{p['views']} likes:{p['likes']} | {(p.get('text') or '')[:30].replace(chr(10),' ')!r}")

    output_path = Path.home() / "Desktop" / "gaku_ai_life_report.html"
    project_root = SCRIPT_DIR.parent
    research = load_research_data(project_root)
    html = generate_html(posts, account, research)
    output_path.write_text(html, encoding="utf-8")

    max_v = max(p["views"] for p in posts) if posts else 0
    avg_v = sum(p["views"] for p in posts) / len(posts) if posts else 0
    print(f"\n✅ {output_path}")
    print(f"   投稿数:{len(posts)} 最高:{max_v:,}views 平均:{avg_v:.0f}views")


if __name__ == "__main__":
    main()
