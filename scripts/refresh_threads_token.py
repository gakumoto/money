"""Threads 長期トークン (60日有効) を自動更新する.

Threads API の `refresh_access_token` エンドポイントを使って、
既存の長期トークンを新しい長期トークンに交換する。
新トークンを `.env` に書き戻し、`THREADS_TOKEN_EXPIRES` も更新する。

毎週日曜 03:00 にタスクスケジューラから実行する想定。
期限の数日前に余裕を持って更新するため、頻繁に走らせても問題ない
(Threads API のリフレッシュは冪等で、24時間以上経過したトークンに対して有効).

使い方:
    python scripts/refresh_threads_token.py            # 全アカウント
    python scripts/refresh_threads_token.py --dry-run  # 動作確認のみ

公式ドキュメント:
    https://developers.facebook.com/docs/threads/get-started/long-lived-tokens
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Windows の cp932 対策
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
load_dotenv(ENV_PATH)
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
from _discord import notify  # noqa: E402
from _net_wait import wait_for_network  # noqa: E402

REFRESH_URL = "https://graph.threads.net/refresh_access_token"


def refresh_token(current_token: str, timeout: int = 30) -> dict:
    """Threads API でトークンを refresh.

    Returns:
        {"access_token": "...", "expires_in": <seconds>}

    Raises:
        RuntimeError: API エラー or レスポンス異常時
    """
    params = {
        "grant_type": "th_refresh_token",
        "access_token": current_token,
    }
    r = requests.get(REFRESH_URL, params=params, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(
            f"refresh API エラー: HTTP {r.status_code} {r.text[:300]}"
        )
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"レスポンスに access_token なし: {data}")
    return data


def find_token_env_keys(env_text: str) -> list[str]:
    """`.env` から THREADS_ACCESS_TOKEN* のキー一覧を抽出 (順序維持)."""
    keys = []
    for line in env_text.splitlines():
        m = re.match(r"^(THREADS_ACCESS_TOKEN[A-Z_]*)\s*=", line)
        if m and m.group(1) not in keys:
            keys.append(m.group(1))
    return keys


def read_env_value(env_text: str, key: str) -> str:
    """`.env` の値を取得 (空欄やコメントは無視)."""
    m = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", env_text, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def write_env_value(env_text: str, key: str, value: str) -> str:
    """`.env` の値を書き換え (キーが無ければ末尾に追記)."""
    pattern = rf"^({re.escape(key)}\s*=\s*).*$"
    if re.search(pattern, env_text, re.MULTILINE):
        return re.sub(pattern, rf"\g<1>{value}", env_text, count=1, flags=re.MULTILINE)
    # 末尾に追記
    if not env_text.endswith("\n"):
        env_text += "\n"
    return env_text + f"{key}={value}\n"


def update_env_file(updates: dict[str, str], expires_iso: str) -> None:
    """`.env` を上書き (バックアップ付き)."""
    text = ENV_PATH.read_text(encoding="utf-8")
    # バックアップ (タイムスタンプ付き)
    backup_dir = SCRIPT_DIR / "logs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f".env.backup_{ts}"
    backup_path.write_text(text, encoding="utf-8")

    new_text = text
    for key, value in updates.items():
        new_text = write_env_value(new_text, key, value)
    new_text = write_env_value(new_text, "THREADS_TOKEN_EXPIRES", expires_iso)

    ENV_PATH.write_text(new_text, encoding="utf-8")


def main():
    dry_run = "--dry-run" in sys.argv

    if not wait_for_network():
        msg = "[refresh_token] ネット復帰待ちタイムアウト"
        print(msg, file=sys.stderr)
        notify(msg)
        sys.exit(1)

    if not ENV_PATH.exists():
        print(f".env が見つかりません: {ENV_PATH}", file=sys.stderr)
        sys.exit(1)

    env_text = ENV_PATH.read_text(encoding="utf-8")
    keys = find_token_env_keys(env_text)
    if not keys:
        print("[refresh_token] THREADS_ACCESS_TOKEN 系のキーが見つかりません")
        sys.exit(1)

    print(f"[refresh_token] 対象キー: {keys}")

    # 同じトークン値を持つキーをグループ化 (重複 API call を避ける)
    token_to_keys: dict[str, list[str]] = {}
    for k in keys:
        v = read_env_value(env_text, k)
        if not v or "YOUR_" in v:
            print(f"  - {k}: 空 or プレースホルダ → スキップ")
            continue
        token_to_keys.setdefault(v, []).append(k)

    if not token_to_keys:
        msg = "[refresh_token] 有効なトークンが.envに無し"
        print(msg)
        notify(msg)
        sys.exit(0)

    updates: dict[str, str] = {}
    expires_iso = ""
    success_groups = 0
    failed_groups: list[str] = []

    for current_token, group_keys in token_to_keys.items():
        label = ",".join(group_keys)
        print(f"\n[refresh_token] 更新中: {label}")
        if dry_run:
            print("  (dry-run: API call スキップ)")
            continue
        try:
            result = refresh_token(current_token)
            new_token = result["access_token"]
            expires_in = int(result.get("expires_in", 5_184_000))  # default 60 days
            new_expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)
            expires_iso = new_expires.date().isoformat()
            for k in group_keys:
                updates[k] = new_token
            success_groups += 1
            print(f"  ✅ 新トークン取得 (期限: {expires_iso})")
        except Exception as e:
            failed_groups.append(f"{label}: {e}")
            print(f"  ❌ 失敗: {e}", file=sys.stderr)

    if dry_run:
        print("\n[refresh_token] dry-run 完了. .env は変更されません.")
        return

    if updates:
        update_env_file(updates, expires_iso)
        print(f"\n[refresh_token] .env 更新完了 ({len(updates)} キー)")
    else:
        print("\n[refresh_token] 更新対象なし")

    # Discord 通知
    if success_groups > 0 and not failed_groups:
        notify(
            f"[Threadsトークン更新] 成功\n"
            f"- 更新キー数: {len(updates)}\n"
            f"- 新しい期限: {expires_iso}\n"
            f"- バックアップ: scripts/logs/.env.backup_*"
        )
    elif failed_groups:
        notify(
            f"[Threadsトークン更新] ⚠️ 部分失敗\n"
            f"成功: {success_groups} グループ\n"
            f"失敗:\n" + "\n".join(f"  - {f}" for f in failed_groups[:5])
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
