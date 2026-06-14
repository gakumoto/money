"""リサーチINDEXをWebブラウザで閲覧・状態管理するローカルサーバー.

依存ライブラリなし（標準ライブラリのみ）。

起動:
  python scripts/research_viewer.py
ブラウザ:
  http://localhost:8765/
スマホ（同一LAN）:
  http://<PCのIP>:8765/

API:
  GET  /                → HTML
  GET  /api/items       → index.json
  POST /api/status      → {id, status} を受けて index.json を更新
  GET  /healthz         → "ok"
"""
from __future__ import annotations

import http.server
import json
import socketserver
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = ROOT / ".company" / "research" / "index.json"
PORT = 8765
JST = timezone(timedelta(hours=9))

_lock = threading.Lock()


def load() -> dict:
    with _lock:
        return json.loads(INDEX_JSON.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    with _lock:
        INDEX_JSON.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


HTML = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>リサーチINDEX</title>
<style>
  :root {
    --bg: #f7f7f5;
    --panel: #ffffff;
    --text: #1a1a1a;
    --muted: #6b6b6b;
    --border: #e3e3e0;
    --accent: #2563eb;
    --used: #10b981;
    --dropped: #ef4444;
    --unused: #6b7280;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Yu Gothic", sans-serif;
    line-height: 1.5;
  }
  header {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 12px 16px;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }
  h1 { font-size: 16px; margin: 0; font-weight: 700; }
  .stats { display: flex; gap: 8px; font-size: 12px; color: var(--muted); }
  .stats b { color: var(--text); }
  .filters {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--panel);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .filter-row {
    display: flex;
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
  }
  .filter-label {
    font-size: 11px;
    color: var(--muted);
    min-width: 44px;
  }
  input[type="search"] {
    flex: 1;
    padding: 8px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    font-size: 14px;
    min-width: 200px;
  }
  input[type="search"]:focus { outline: 2px solid var(--accent); }
  .chip {
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    cursor: pointer;
    user-select: none;
  }
  .chip.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }
  .chip-count {
    margin-left: 4px;
    opacity: 0.6;
    font-size: 10px;
  }
  main {
    padding: 12px 16px 80px;
    max-width: 920px;
    margin: 0 auto;
  }
  .empty {
    text-align: center;
    color: var(--muted);
    padding: 40px 16px;
    font-size: 14px;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-left: 4px solid var(--unused);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    transition: opacity 0.15s;
  }
  .card.status-used { border-left-color: var(--used); opacity: 0.55; }
  .card.status-dropped { border-left-color: var(--dropped); opacity: 0.45; }
  .card-title {
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 4px;
    line-height: 1.4;
  }
  .card.status-used .card-title,
  .card.status-dropped .card-title {
    text-decoration: line-through;
    text-decoration-thickness: 1px;
  }
  .card-hook {
    font-size: 13px;
    color: var(--text);
    background: var(--bg);
    border-left: 2px solid var(--border);
    padding: 6px 10px;
    margin: 4px 0 8px;
    border-radius: 4px;
    line-height: 1.5;
  }
  .card-meta {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .card-meta a { color: var(--accent); text-decoration: none; }
  .card-meta a:hover { text-decoration: underline; }
  .card-meta .tag {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1px 6px;
  }
  .card-meta .source { font-family: monospace; font-size: 11px; }
  .card-actions {
    display: flex;
    gap: 6px;
    justify-content: flex-end;
  }
  .btn {
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
  }
  .btn:hover { background: var(--bg); }
  .btn-used { color: var(--used); border-color: var(--used); }
  .btn-dropped { color: var(--dropped); border-color: var(--dropped); }
  .btn-reset { color: var(--muted); }
  .btn.disabled { opacity: 0.3; pointer-events: none; }
  @media (max-width: 600px) {
    h1 { font-size: 14px; }
    .stats { font-size: 11px; }
    .card-title { font-size: 14px; }
    .filter-label { min-width: 36px; font-size: 10px; }
  }
</style>
</head>
<body>
<header>
  <div class="header-row">
    <h1>📚 リサーチINDEX</h1>
    <div class="stats" id="stats">読み込み中...</div>
  </div>
</header>

<div class="filters">
  <div class="filter-row">
    <input type="search" id="search" placeholder="🔍 タイトルで検索" />
  </div>
  <div class="filter-row">
    <span class="filter-label">状態</span>
    <span id="status-chips"></span>
  </div>
  <div class="filter-row">
    <span class="filter-label">ジャンル</span>
    <span id="genre-chips"></span>
  </div>
  <div class="filter-row">
    <span class="filter-label">型</span>
    <span id="type-chips"></span>
  </div>
</div>

<main id="items"><div class="empty">読み込み中...</div></main>

<script>
let ALL = [];
const FILTERS = { search: "", status: "unused", genre: "", type: "" };
const STATUS_LABELS = { unused: "未使用", used: "使った", dropped: "ボツ", "": "全部" };

async function fetchAll() {
  const r = await fetch("/api/items");
  const data = await r.json();
  ALL = data.items || [];
  setupChips();
  render();
}

function uniqValues(key) {
  const set = new Set();
  ALL.forEach(it => set.add(it[key]));
  return Array.from(set).sort();
}

function setupChips() {
  // 状態
  const statusEl = document.getElementById("status-chips");
  statusEl.innerHTML = "";
  ["unused", "used", "dropped", ""].forEach(s => {
    const c = document.createElement("span");
    c.className = "chip" + (FILTERS.status === s ? " active" : "");
    c.textContent = STATUS_LABELS[s];
    c.onclick = () => { FILTERS.status = s; setupChips(); render(); };
    statusEl.appendChild(c);
  });
  // ジャンル
  const genreEl = document.getElementById("genre-chips");
  genreEl.innerHTML = "";
  const allGenres = [""].concat(uniqValues("genre"));
  allGenres.forEach(g => {
    const c = document.createElement("span");
    c.className = "chip" + (FILTERS.genre === g ? " active" : "");
    c.textContent = g || "全て";
    c.onclick = () => { FILTERS.genre = g; setupChips(); render(); };
    genreEl.appendChild(c);
  });
  // 型
  const typeEl = document.getElementById("type-chips");
  typeEl.innerHTML = "";
  const allTypes = [""].concat(uniqValues("type"));
  allTypes.forEach(t => {
    const c = document.createElement("span");
    c.className = "chip" + (FILTERS.type === t ? " active" : "");
    c.textContent = t || "全て";
    c.onclick = () => { FILTERS.type = t; setupChips(); render(); };
    typeEl.appendChild(c);
  });
}

function applyFilters() {
  return ALL.filter(it => {
    if (FILTERS.status && it.status !== FILTERS.status) return false;
    if (FILTERS.genre && it.genre !== FILTERS.genre) return false;
    if (FILTERS.type && it.type !== FILTERS.type) return false;
    if (FILTERS.search) {
      const q = FILTERS.search.toLowerCase();
      const hay = ((it.title || "") + " " + (it.hook || "")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function render() {
  // stats
  const total = ALL.length;
  const used = ALL.filter(it => it.status === "used").length;
  const dropped = ALL.filter(it => it.status === "dropped").length;
  const unused = total - used - dropped;
  document.getElementById("stats").innerHTML =
    `全 <b>${total}</b> / 未使用 <b>${unused}</b> / 使った <b>${used}</b> / ボツ <b>${dropped}</b>`;

  // items
  const filtered = applyFilters();
  const main = document.getElementById("items");
  if (filtered.length === 0) {
    main.innerHTML = '<div class="empty">該当するネタがありません</div>';
    return;
  }
  main.innerHTML = filtered.map(it => {
    const isUsed = it.status === "used";
    const isDropped = it.status === "dropped";
    const hookHtml = it.hook ? `<div class="card-hook">${escapeHtml(it.hook)}</div>` : "";
    const urlHtml = it.source_url ? ` ／ <a href="${escapeHtml(it.source_url)}" target="_blank" rel="noopener">🔗 ソース</a>` : "";
    return `
      <div class="card status-${it.status}" data-id="${escapeHtml(it.id)}">
        <div class="card-title">${escapeHtml(it.title)}</div>
        ${hookHtml}
        <div class="card-meta">
          <span class="tag">${escapeHtml(it.genre)}</span>
          <span class="tag">${escapeHtml(it.type)}</span>
          <span class="source">${escapeHtml(it.source_file)}:${it.source_line}${urlHtml}</span>
        </div>
        <div class="card-actions">
          <button class="btn btn-used ${isUsed ? "disabled" : ""}" onclick="setStatus('${escapeHtml(it.id)}', 'used')">✅ 使った</button>
          <button class="btn btn-dropped ${isDropped ? "disabled" : ""}" onclick="setStatus('${escapeHtml(it.id)}', 'dropped')">❌ ボツ</button>
          <button class="btn btn-reset ${it.status === "unused" ? "disabled" : ""}" onclick="setStatus('${escapeHtml(it.id)}', 'unused')">↩ 戻す</button>
        </div>
      </div>
    `;
  }).join("");
}

async function setStatus(id, status) {
  const r = await fetch("/api/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, status })
  });
  if (!r.ok) {
    alert("更新失敗: " + r.status);
    return;
  }
  const it = ALL.find(x => x.id === id);
  if (it) {
    it.status = status;
    it.used_at = status === "used" ? new Date().toISOString() : "";
  }
  render();
}

document.getElementById("search").addEventListener("input", (e) => {
  FILTERS.search = e.target.value;
  render();
});

fetchAll();
</script>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, body: bytes, status: int = 200, content_type: str = "text/plain"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj, status: int = 200):
        self._send(
            json.dumps(obj, ensure_ascii=False).encode("utf-8"),
            status,
            "application/json; charset=utf-8",
        )

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(HTML.encode("utf-8"), 200, "text/html; charset=utf-8")
            return
        if path == "/api/items":
            try:
                self._send_json(load())
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return
        if path == "/healthz":
            self._send(b"ok", 200, "text/plain")
            return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/status":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            item_id = payload["id"]
            new_status = payload["status"]
            if new_status not in ("unused", "used", "dropped"):
                raise ValueError(f"invalid status: {new_status}")
        except Exception as e:
            self._send_json({"error": f"bad request: {e}"}, 400)
            return

        data = load()
        now = datetime.now(JST).isoformat()
        found = False
        for it in data["items"]:
            if it["id"] == item_id:
                it["status"] = new_status
                it["used_at"] = now if new_status == "used" else ""
                found = True
                break
        if not found:
            self._send_json({"error": "id not found"}, 404)
            return
        save(data)
        self._send_json({"ok": True})

    def log_message(self, fmt, *args):
        sys.stderr.write("[research_viewer] " + (fmt % args) + "\n")


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> int:
    if not INDEX_JSON.exists():
        print(f"[research_viewer] not found: {INDEX_JSON}", file=sys.stderr)
        print("先に: python scripts/build_research_index.py", file=sys.stderr)
        return 1
    httpd = ThreadingServer(("0.0.0.0", PORT), Handler)
    print(f"[research_viewer] http://localhost:{PORT}/")
    print(f"[research_viewer] スマホからは http://<PCのIP>:{PORT}/ （同一LAN）")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[research_viewer] stopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
