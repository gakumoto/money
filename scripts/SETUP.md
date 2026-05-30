# scripts/ セットアップガイド

このドキュメントは、自動化スクリプトを動かすために必要な外部準備を1つずつ案内する。

## 必須: Python 依存関係

```bash
pip install -r scripts/requirements.txt
```

これで完了。`yt-dlp`, `requests`, `python-dotenv` が入る。

---

## ① Discord Webhook (5分)

夜パイプラインの通知用 (一方向: スクリプト→Discord)。無くてもスクリプトは動くが、結果通知が来ない。
※ 双方向 (スマホ→Threads 指示出し) は ⑥ Discord Bot を参照。

### 手順

1. Discord アプリを開く
2. 通知を受け取りたいサーバー → 任意のチャンネル
3. チャンネル名の **歯車アイコン** → **連携サービス** → **ウェブフック**
4. **新しいウェブフック** → 名前 (例: `myCompany Bot`) → **ウェブフック URL をコピー**
5. `scripts/.env` の `DISCORD_WEBHOOK_URL` に貼り付け

### 動作確認

```bash
python scripts/_discord.py "セットアップ完了テスト"
```

Discord に通知が来れば成功。

---

## ② Threads API (Meta Developer) - 30〜60分

Threads 自動投稿とメトリクス取得に必須。少しめんどう。

### 手順

#### 2-1. Meta Developer アカウント作成

1. https://developers.facebook.com にアクセス
2. **始める** → Facebook アカウントでログイン
3. **My Apps** → **Create App** → 用途は **Other** → 種類は **Business**
4. アプリ名 (例: `myCompany-Threads`) → 連絡先メール

#### 2-2. Threads API 追加

1. アプリのダッシュボード左メニュー → **Add Product**
2. **Threads API** を見つけて **Set Up**
3. **Threads Permissions and Features** で必要な権限を有効化:
   - `threads_basic` (自分の投稿読み取り)
   - `threads_content_publish` (投稿作成)
   - `threads_read_replies` (返信読み取り)
   - `threads_manage_insights` (メトリクス取得)

#### 2-3. アクセストークン取得

1. **Threads API** → **Use cases** → **Generate Token**
2. 自分の Threads アカウントを連携 (OAuth フロー)
3. **短期トークン** が発行される (1時間で期限切れ)
4. これを **長期トークン (60日有効)** に変換:
   ```
   GET https://graph.threads.net/access_token?
       grant_type=th_exchange_token&
       client_secret=YOUR_APP_SECRET&
       access_token=SHORT_LIVED_TOKEN
   ```
5. レスポンスの `access_token` をコピー

#### 2-4. ユーザーID取得

```
GET https://graph.threads.net/v1.0/me?fields=id&access_token=YOUR_TOKEN
```

レスポンスの `id` がユーザーID。

#### 2-5. .env に設定

```env
THREADS_USER_ID=<上記で取得したID>
THREADS_ACCESS_TOKEN=<上記の長期トークン>
```

複数アカウントを管理する場合は account 別 env も追加:

```env
THREADS_USER_ID_GAKU_AI_LIFE=...
THREADS_ACCESS_TOKEN_GAKU_AI_LIFE=...
```

### 動作確認

```bash
python scripts/_threads_api.py
# → OK: 認証成功。直近X投稿取得
```

### 注意

- **長期トークンは60日で期限切れ**。リフレッシュエンドポイントで延長する仕組みを別途必要 (本スクリプトには未実装。後日追加可)
- API レート制限あり。1時間に投稿可能なのは250件まで (2025年時点)
- ビジネス認証が必要な場合がある (発見性向上に推奨)

---

## ③ Windows Task Scheduler でスケジューリング

### 夜パイプライン (毎日 02:00)

PowerShell を **管理者として実行** し、以下:

```powershell
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money\scripts\nightly_pipeline.py" `
    -WorkingDirectory "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"

$trigger = New-ScheduledTaskTrigger -Daily -At 02:00

Register-ScheduledTask `
    -TaskName "myCompany-NightlyPipeline" `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest
```

### Threads 自動投稿 (1日3回: 07:00 / 12:00 / 18:00)

```powershell
foreach ($t in @("07:00", "12:00", "18:00")) {
    $action = New-ScheduledTaskAction `
        -Execute "python" `
        -Argument "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money\scripts\threads_auto_post.py gaku_ai_life" `
        -WorkingDirectory "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"
    $trigger = New-ScheduledTaskTrigger -Daily -At $t
    Register-ScheduledTask `
        -TaskName "myCompany-ThreadsPost-$($t.Replace(':',''))" `
        -Action $action `
        -Trigger $trigger
}
```

### メトリクス取得 (毎日 22:00)

```powershell
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money\scripts\threads_fetch_metrics.py gaku_ai_life 30" `
    -WorkingDirectory "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"

$trigger = New-ScheduledTaskTrigger -Daily -At 22:00

Register-ScheduledTask -TaskName "myCompany-FetchMetrics" -Action $action -Trigger $trigger
```

### スケジュール一覧確認

```powershell
Get-ScheduledTask -TaskName "myCompany-*" | Format-Table TaskName, State, NextRunTime
```

### 削除

```powershell
Unregister-ScheduledTask -TaskName "myCompany-NightlyPipeline" -Confirm:$false
```

---

## ④ cron (Mac/Linux) でスケジューリング

`crontab -e` で以下を追加:

```cron
# 夜パイプライン (02:00)
0 2 * * * cd /path/to/project && /usr/bin/python3 scripts/nightly_pipeline.py >> scripts/logs/nightly.log 2>&1

# Threads 自動投稿 (07:00, 12:00, 18:00)
0 7,12,18 * * * cd /path/to/project && /usr/bin/python3 scripts/threads_auto_post.py gaku_ai_life >> scripts/logs/post.log 2>&1

# メトリクス取得 (22:00)
0 22 * * * cd /path/to/project && /usr/bin/python3 scripts/threads_fetch_metrics.py gaku_ai_life 30 >> scripts/logs/metrics.log 2>&1
```

ログディレクトリも作る:
```bash
mkdir -p scripts/logs
```

---

## ⑤ 投稿キューの運用

下書きフォルダ構造:

```
.company/marketing/drafts/<account>/
├── 2026-05-14_01_xxx.md      ← まだ承認前。here で生成される
├── queued/
│   └── 2026-05-14_01_xxx.md  ← 承認後に手動 or skill で移動
└── posted/
    └── 2026-05-14_0730_<media_id>_2026-05-14_01_xxx.md  ← 投稿後自動移動
```

承認の流れ:
1. `/threads-daily-run` で `drafts/<account>/` に10本生成
2. オーナーがレビュー
3. OK出したものを `queued/` に移動 (手動 or `/threads-publish-approve` 等で自動化)
4. cron が `threads_auto_post.py` を起動 → `queued/` から1本投稿 → `posted/` に移動

`queued/` のファイル frontmatter に `publish_at: 2026-05-14T07:30:00+09:00` を入れておけば、時刻指定で投稿される。

無ければ「キューに入っている順から即時投稿」になる。

---

## ⑥ Discord Bot (双方向・スマホからのレビュー / 指示出し)

夜パイプラインで生成された 10 本を **スマホで承認 / 編集 / 再生成 / 却下** できる仕組み。
ボタン UI なので布団から出ずに 10 本捌ける。

### 6-1. Bot Application 作成 (Discord Developer Portal)

1. https://discord.com/developers/applications にアクセス
2. **New Application** → 名前: `myCompany Bot` (任意)
3. 左メニュー **Bot** タブ → **Reset Token** → トークンをコピー (一度しか見えない)
4. 同じ画面の **Privileged Gateway Intents** で **`MESSAGE CONTENT INTENT`** を ON
5. 左メニュー **OAuth2** → **URL Generator**
   - **Scopes**: `bot` と `applications.commands` の 2 つ ON
   - **Bot Permissions**: `Send Messages` / `Read Message History` / `Embed Links` / `Attach Files` / `Use Slash Commands`
6. 一番下の生成 URL をブラウザで開く → 自分の Discord サーバーに招待
7. Discord 設定 → 詳細設定 → **開発者モード** ON
8. 自分のユーザー名右クリック → **ユーザー ID をコピー** (Owner ID)
9. サーバーアイコン右クリック → **サーバー ID をコピー** (Guild ID)

### 6-2. .env に 3 つ追加

```env
DISCORD_BOT_TOKEN=<step 3 でコピーしたトークン>
DISCORD_OWNER_ID=<step 8 のユーザー ID>
DISCORD_GUILD_ID=<step 9 のサーバー ID>
```

### 6-3. 依存追加 + 動作確認

```bash
pip install -r scripts/requirements.txt
python scripts/discord_bot.py
```

Discord で「[myCompany Bot] 起動完了」通知が来れば成功。
動かしっぱなしにして、Discord で `/status` を打ってみる。

### 6-4. 使えるスラッシュコマンド

| コマンド | 用途 |
|---------|------|
| `/review` | 未レビューの下書きを最大 10 本まで表示。各下書きに承認 / 編集 / 再生成 / 却下ボタン |
| `/post <text>` | 即時投稿 (500 字以内) |
| `/queue <text> [time]` | キューに追加。time は `HH:MM` (今日中) or ISO8601。省略時は次の空き枠 |
| `/list` | キュー一覧 (publish_at 順) |
| `/feedback <category> <content>` | feedback/gaku_ai_life.md に追加 |
| `/status` | 未レビュー / キュー / 本日投稿数のサマリー |
| `/sync` | コマンドを再同期 (新機能追加時) |

### 6-5. PC 起動時に自動立ち上げ (Task Scheduler)

PowerShell を **管理者として実行**:

```powershell
$projectRoot = "C:\Users\新日本エネックス岳本\Desktop\アプリ開発\money"
$pythonExe = "C:\Users\新日本エネックス岳本\AppData\Local\Python\pythoncore-3.14-64\python.exe"

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "$projectRoot\scripts\discord_bot.py" `
    -WorkingDirectory $projectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName "myCompany-DiscordBot" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest
```

ログオン時に自動起動し、落ちたら 1 分後に最大 3 回まで再起動。

### 6-6. 朝のフロー (理想形)

```
02:00 nightly_pipeline が走る → drafts に 10 本生成
02:30 Discord に「下書き 10 本できました」通知 + 「/review で開始」案内
朝   スマホで /review → 10 本がボタン付きで表示
     ✅ 承認 → publish_at 自動付与 → queued に移動
     ✏️ 編集 → モーダルで本文修正 → 保存
     🔄 再生成 → 「冒頭に固有名詞入れて」と指示 → AI が直す
     ❌ 却下 → 理由入力 → rejected/ に移動 + feedback 蓄積
07:30〜 threads_auto_post が queued から順次投稿
```

布団から出ずに 1 日分の運用が完了します。

### 6-7. トラブル

- **スラッシュコマンドが見えない**: Discord クライアントを再起動 → それでも見えなければ `/sync`
- **「インタラクション失敗」**: Bot が落ちている。Task Scheduler の `myCompany-DiscordBot` を起動
- **編集モーダルが 500 字制限**: Threads の文字数上限。短く削るのは正解 (フィードバック蓄積参照)
