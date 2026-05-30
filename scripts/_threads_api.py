"""Threads API (Meta Graph API) の共通ラッパー.

Threads API ドキュメント: https://developers.facebook.com/docs/threads

使用前に必要な準備:
1. Meta Developer 登録: https://developers.facebook.com
2. アプリ作成 → Threads API 追加
3. 長期アクセストークン取得
4. scripts/.env に THREADS_USER_ID と THREADS_ACCESS_TOKEN を設定
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import requests
from dotenv import load_dotenv

# Windows の cp932 対策: stdout/stderr を UTF-8 に固定
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_BASE = "https://graph.threads.net/v1.0"


@dataclass
class ThreadsClient:
    user_id: str
    access_token: str

    @classmethod
    def from_env(cls, account: Optional[str] = None) -> "ThreadsClient":
        """環境変数から認証情報を取得.

        account 指定があればアカウント別env (THREADS_USER_ID_<ACCOUNT> 等) を優先.
        無ければ THREADS_USER_ID / THREADS_ACCESS_TOKEN をデフォルトに.
        """
        suffix = f"_{account.upper()}" if account else ""
        user_id = (
            os.getenv(f"THREADS_USER_ID{suffix}")
            or os.getenv("THREADS_USER_ID", "")
        ).strip()
        access_token = (
            os.getenv(f"THREADS_ACCESS_TOKEN{suffix}")
            or os.getenv("THREADS_ACCESS_TOKEN", "")
        ).strip()
        if not user_id or not access_token or "YOUR_" in access_token:
            raise RuntimeError(
                f"Threads API 認証情報が未設定 (account={account!r}). "
                "scripts/.env に THREADS_USER_ID / THREADS_ACCESS_TOKEN を設定して"
            )
        return cls(user_id=user_id, access_token=access_token)

    # ---------- 投稿 ----------

    def create_text_post(self, text: str, *, reply_to_id: Optional[str] = None) -> str:
        """テキスト投稿を作成 → 公開. 公開された media_id を返す.

        手順: 1) media container 作成 → 2) publish.
        """
        # Step 1: container 作成
        params = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self.access_token,
        }
        if reply_to_id:
            params["reply_to_id"] = reply_to_id
        r = requests.post(f"{API_BASE}/{self.user_id}/threads", data=params, timeout=30)
        r.raise_for_status()
        creation_id = r.json()["id"]

        # 推奨: container 作成後数秒待ってから publish (Meta公式ベストプラクティス)
        time.sleep(3)

        # Step 2: publish
        publish_params = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        r2 = requests.post(
            f"{API_BASE}/{self.user_id}/threads_publish",
            data=publish_params,
            timeout=30,
        )
        r2.raise_for_status()
        return r2.json()["id"]

    def create_image_post(
        self,
        text: str,
        image_url: str,
        *,
        reply_to_id: Optional[str] = None,
    ) -> str:
        """画像 + テキスト投稿を作成 → 公開. 公開された media_id を返す.

        画像は **パブリックにアクセスできる URL** が必要 (ローカルファイル不可).
        Threads API 仕様:
            - 対応形式: JPEG / PNG
            - 最大サイズ: 8 MB
            - 推奨アスペクト比: 1.91:1 〜 4:5
        """
        # Step 1: media container 作成 (画像付き)
        params = {
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": text,
            "access_token": self.access_token,
        }
        if reply_to_id:
            params["reply_to_id"] = reply_to_id
        r = requests.post(
            f"{API_BASE}/{self.user_id}/threads", data=params, timeout=30
        )
        r.raise_for_status()
        creation_id = r.json()["id"]

        # 画像処理を Threads 側が完了するまで少し長めに待つ (テキストより重い)
        time.sleep(5)

        # Step 2: publish
        publish_params = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        r2 = requests.post(
            f"{API_BASE}/{self.user_id}/threads_publish",
            data=publish_params,
            timeout=30,
        )
        r2.raise_for_status()
        return r2.json()["id"]

    # ---------- 投稿一覧 ----------

    def list_recent_posts(self, *, limit: int = 50, since: Optional[str] = None) -> list[dict]:
        """直近の投稿一覧を取得.

        since: ISO8601 日時。指定があればそれ以降のみ。
        """
        params = {
            "fields": "id,text,timestamp,permalink",
            "limit": min(limit, 100),
            "access_token": self.access_token,
        }
        if since:
            params["since"] = since
        r = requests.get(f"{API_BASE}/{self.user_id}/threads", params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("data", [])

    # ---------- インサイト ----------

    def get_insights(self, media_id: str) -> dict:
        """投稿のメトリクス (インプレッション・いいね・返信・シェア等) を取得."""
        params = {
            "metric": "views,likes,replies,reposts,quotes,shares",
            "access_token": self.access_token,
        }
        r = requests.get(f"{API_BASE}/{media_id}/insights", params=params, timeout=30)
        r.raise_for_status()
        data = r.json().get("data", [])
        out: dict = {}
        for item in data:
            name = item.get("name")
            values = item.get("values", [])
            if values:
                out[name] = values[0].get("value")
        return out


if __name__ == "__main__":
    # 認証情報の動作確認
    try:
        client = ThreadsClient.from_env()
        posts = client.list_recent_posts(limit=3)
        print(f"OK: 認証成功。直近{len(posts)}投稿取得")
        for p in posts:
            print(f"  - {p.get('timestamp', '?')} | {(p.get('text') or '')[:40]}")
    except Exception as e:
        print(f"NG: {e}", file=sys.stderr)
        sys.exit(1)
