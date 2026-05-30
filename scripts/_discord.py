"""Discord Webhook 通知の共通ヘルパー."""
from __future__ import annotations

import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv

# Windows の cp932 対策
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def _project_root() -> str:
    """scripts/ の親ディレクトリ（プロジェクトルート）."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def notify(message: str, webhook_url: Optional[str] = None) -> bool:
    """Discord に通知を送る。webhook_url 未指定なら環境変数から取得。

    失敗時は False を返す（例外を投げない）。Webhook 未設定時はサイレントに無視。
    """
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not url or url.startswith("https://discord.com/api/webhooks/XXXXX"):
        print("[discord] Webhook URL 未設定。スキップ", file=sys.stderr)
        return False

    try:
        res = requests.post(url, json={"content": message}, timeout=10)
        res.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[discord] 通知失敗: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "test from _discord.py"
    ok = notify(msg)
    sys.exit(0 if ok else 1)
