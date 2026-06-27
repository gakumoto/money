"""自分の投稿への返信(返信者ユーザー名+文面)を取得する。N1分析用.

使い方:
    python scripts/fetch_replies.py <account> <media_id> [<media_id> ...]
返信は GET /{media_id}/replies（自分の投稿のみ取得可）。
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")
sys.path.insert(0, str(SCRIPT_DIR))
from _threads_api import ThreadsClient, API_BASE  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def fetch(account: str, media_ids: list[str]) -> str:
    c = ThreadsClient.from_env(account=account)
    lines = []
    for mid in media_ids:
        lines.append(f"\n===== media_id={mid} =====")
        try:
            r = requests.get(
                f"{API_BASE}/{mid}/replies",
                params={
                    "fields": "id,username,text,timestamp,has_replies,hide_status",
                    "access_token": c.access_token,
                    "reverse": "false",
                },
                timeout=30,
            )
            r.raise_for_status()
            data = r.json().get("data", [])
            if not data:
                lines.append("  (返信データなし or 取得不可)")
            for d in data:
                u = d.get("username", "?")
                t = (d.get("text") or "").replace("\n", " ").strip()
                lines.append(f"  @{u}: {t}")
        except Exception as e:
            lines.append(f"  取得失敗: {e}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    acct = sys.argv[1]
    mids = sys.argv[2:]
    out = fetch(acct, mids)
    Path(SCRIPT_DIR / "_replies_out.txt").write_text(out, encoding="utf-8")
    print("done ->", SCRIPT_DIR / "_replies_out.txt")
