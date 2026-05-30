# scripts/

myCompany の自動化スクリプト群。
全部 Python 3.10+ で書かれている。Windows / Mac / Linux 対応。

## ファイル構成

| ファイル | 役割 | 外部依存 |
|---------|------|---------|
| `_discord.py` | Discord Webhook 通知ヘルパー (内部用) | `DISCORD_WEBHOOK_URL` |
| `_threads_api.py` | Threads API ラッパー (内部用) | `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN` |
| `youtube_research.py` | YouTube字幕取得 | yt-dlp |
| `nightly_pipeline.py` | 夜の `/threads-daily-run` 実行 + Discord通知 | Claude Code CLI, Discord |
| `threads_auto_post.py` | Threads自動投稿 (queued→posted) | Threads API |
| `threads_fetch_metrics.py` | 投稿メトリクス取得 | Threads API |

## 初回セットアップ

### 1. Python 依存関係をインストール

```bash
pip install -r scripts/requirements.txt
```

これで `yt-dlp`, `requests`, `python-dotenv` が入る。

### 2. .env を作る

```bash
cp scripts/.env.example scripts/.env
```

エディタで `scripts/.env` を開き、値を埋める。詳細は `scripts/SETUP.md`。

### 3. 動作確認

```bash
# Discord 接続確認
python scripts/_discord.py "テスト通知"

# Threads API 認証確認
python scripts/_threads_api.py
```

## 個別の使い方

### YouTube リサーチ

```bash
python scripts/youtube_research.py https://www.youtube.com/@example 10
# → .company/research/topics/youtube-YYYY-MM-DD.md に保存
```

### 夜パイプライン (手動実行)

```bash
python scripts/nightly_pipeline.py
# → /threads-daily-run を実行 → Discord通知
```

### Threads 自動投稿 (queueから1本投稿)

```bash
python scripts/threads_auto_post.py gaku_ai_life
# → queued/ から1本投稿 → posted/ に移動
```

ドライラン (実際には投稿しない):
```bash
python scripts/threads_auto_post.py gaku_ai_life --dry-run
```

### メトリクス取得 (過去30日)

```bash
python scripts/threads_fetch_metrics.py gaku_ai_life 30
# → posted/ の各ファイルにメトリクスを追記
```

## 自動化 (スケジューリング)

`SETUP.md` を見る。Windows Task Scheduler / cron 両対応。

## トラブルシューティング

- **yt-dlp not found**: `pip install yt-dlp` で再インストール
- **Threads API 401**: アクセストークンが期限切れ。再取得して `.env` 更新
- **Discord 通知なし**: `DISCORD_WEBHOOK_URL` が未設定 or 無効。`python scripts/_discord.py test` で確認
- **Claude CLI not found**: `CLAUDE_CMD` を `.env` に絶対パスで指定
