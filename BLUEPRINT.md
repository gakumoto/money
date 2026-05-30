# myCompany 基本設計書

**AI 半自動化 Threads 運用システム**  
*Threads 投稿の生成 / 配信 / 学習を AI に委ね、オーナーは意思決定だけに集中するための設計書*

---

## 0. このファイルの使い方（最重要・最初に読む）

このファイルは **Claude Code に読み込ませて使う「配布物の核」** です。

### 推奨ワークフロー

1. 配布パッケージ（zip）をダウンロード → 任意のディレクトリに展開
2. ターミナルで展開先に移動
3. `claude` で Claude Code を起動
4. 下記のプロンプトをそのまま投げる:

```
@BLUEPRINT.md を読み込んで、myCompany をセットアップしてください。

私の前提:
- OS: <Windows 11 / macOS / Linux>
- Python: <インストール済み or 未インストール>
- Claude Code: 起動中 (今ここ)
- これから準備するもの: Anthropic API キー / Threads API トークン / Discord Bot

進める順序:
1. ファイル構造と前提を確認、足りないものを教えて
2. .env を一緒に作る（値が必要になったら都度聞いて）
3. アカウント設計ファイルの初期生成を手伝って
4. タスクスケジューラ登録の管理者コマンドを提示
5. Discord で動作確認の手順を案内
```

Claude Code はこのファイルから順に対話的にセットアップを進めます。
詰まったら **§10 トラブルシューティング** を Claude に参照させてください。

### このシステムが解決すること

- Threads 投稿に毎日 30〜60 分とられる → **5〜10 分に短縮**
- 投稿クオリティが日によってブレる → **フィードバック蓄積で型を固定**
- フィードバックを次回に活かす仕組みがない → **AI が毎回必ず読み込む設計**
- 出先でも投稿運用したい → **Discord から完結**

### このシステムの中核思想

**オーナーは意思決定だけ、実行は AI。**

```
オーナーがフィードバック (Discord /feedback or 手動編集)
        ↓
.company/marketing/feedback/<account>.md に追記される
        ↓
次回 AI 生成時に「必ず読み込む」設計
        ↓
applied_feedback に「どれを適用したか」を記録
        ↓
出てきた投稿にまた /feedback
        ↓ (ループ)
書けば書くほど精度が上がる
```

これが myCompany の半自動化の本質。最初の 1 週間は AI の出力に違和感を感じるかもしれませんが、`/feedback` でガンガン指摘するほど 2 週目以降は明らかに精度が上がります。

---

## 1. システム全体アーキテクチャ

### レイヤー構造

```
┌─────────────────────────────────────────────────────┐
│ レイヤー 1: オーナー インターフェース (スマホ / PC)        │
│   ・Discord アプリ (主) / ターミナル (補)               │
└─────────────────────────────┬───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│ レイヤー 2: Discord Bot (scripts/discord_bot.py)     │
│   ・スラッシュコマンド 17 種                            │
│   ・PC ログオン時に自動起動（タスクスケジューラ）         │
└─────────────────────────────┬───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│ レイヤー 3: Claude Code (CLI / ヘッドレス)              │
│   ・スキル発動 (`/threads-daily-run` 等)               │
│   ・フィードバック蓄積を必ず読み込む                     │
└─────────────────────────────┬───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│ レイヤー 4: ファイルシステム (.company/)                │
│   ・CLAUDE.md (全社ルール)                            │
│   ・marketing/feedback/<account>.md (AI 育成の核)     │
│   ・marketing/drafts/<account>/ (生成物)              │
│   ・marketing/accounts/<account>.md (ペルソナ)         │
└─────────────────────────────┬───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│ レイヤー 5: 配信スクリプト (scripts/)                   │
│   ・nightly_pipeline.py (02:00)                      │
│   ・threads_auto_post.py (5枠/日)                     │
│   ・threads_fetch_metrics.py (22:00)                  │
└─────────────────────────────┬───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│ レイヤー 6: 外部 API                                   │
│   ・Threads API (Meta Graph)                          │
│   ・Discord API                                       │
│   ・Anthropic API (Claude Code が使う)                │
└─────────────────────────────────────────────────────┘
```

### データフロー（1日のサイクル）

| 時刻 | プロセス | 入力 | 出力 |
|------|---------|------|------|
| 02:00 | `nightly_pipeline.py` | feedback / accounts / 直近実績 | 翌日分10本の下書き |
| 07:30 | `threads_auto_post.py` | queued/ の `publish_at <= now` のもの | Threads投稿 + posted/移動 |
| 12:30 | 同上 | 同上 | 同上 |
| 18:00 | 同上 | 同上 | 同上 |
| 21:30 | 同上 | 同上 | 同上 |
| 23:00 | 同上 | 同上 | 同上 |
| 22:00 | `threads_fetch_metrics.py` → `metrics_to_feedback.py` | posted/ の過去30日 | 各ファイルにメトリクス追記 + feedback 自動学習 |
| 日曜 03:00 | `refresh_threads_token.py` | `.env` の長期トークン | 新60日トークンに自動交換 + `.env` 更新 + バックアップ |
| 常駐 | `discord_bot.py` | スラッシュコマンド | レビュー / 生成 / 通知 |

---

## 2. ディレクトリ構造

```
project-root/
├── BLUEPRINT.md                    ← このファイル（配布物のエントリポイント）
├── README.md                        ← 簡易版 README
│
├── .claude/                         ← Claude Code 設定
│   ├── settings.json               (任意)
│   └── skills/
│       ├── threads-create-post/SKILL.md
│       ├── threads-daily-run/SKILL.md
│       ├── threads-fetch-metrics/SKILL.md
│       ├── threads-publish/SKILL.md
│       ├── threads-analyze/SKILL.md
│       ├── feedback/SKILL.md
│       ├── research-collect/SKILL.md
│       ├── secretary-briefing/SKILL.md
│       └── youtube-research/SKILL.md
│
├── .company/                        ← 仮想組織ファイル群
│   ├── CLAUDE.md                   ← 全社ライティングルール（最重要）
│   ├── secretary/                   ← 秘書部屋
│   │   ├── CLAUDE.md
│   │   ├── todos/YYYY-MM-DD.md
│   │   ├── reports/YYYY-MM-DD.md    ← 日報
│   │   ├── notes/                   ← 意思決定ログ・壁打ち
│   │   └── inbox/                   ← クイックキャプチャ
│   ├── marketing/                   ← マーケ部屋
│   │   ├── CLAUDE.md
│   │   ├── accounts/<account>.md    ← アカウント設計
│   │   ├── feedback/<account>.md    ← ★AI 育成の核★
│   │   └── drafts/<account>/
│   │       ├── (直下) 生成直後の下書き
│   │       ├── queued/              ← 承認済み・自動投稿対象
│   │       ├── posted/              ← 投稿済み + メトリクス追記
│   │       └── rejected/            ← 却下
│   ├── research/                    ← リサーチ部屋
│   │   └── topics/inbox/            ← 投稿ネタ蓄積
│   ├── products/                    ← プロダクト部屋（note記事/教材）
│   └── pm/                          ← プロジェクト管理
│
├── scripts/                         ← Python / PowerShell 群
│   ├── .env                         ← API キー類（.gitignore）
│   ├── .env.example                 ← 雛形
│   ├── requirements.txt
│   ├── nightly_pipeline.py          ← 02:00 起動
│   ├── threads_auto_post.py          ← 5枠/日の投稿
│   ├── threads_fetch_metrics.py      ← 22:00 メトリクス取得
│   ├── discord_bot.py                ← Discord Bot 常駐
│   ├── _threads_api.py               ← Threads API ラッパー
│   ├── _discord.py                   ← Discord Webhook ヘルパー
│   ├── _net_wait.py                  ← DNS 復帰待ち
│   ├── fix_modern_standby.ps1        ← Windows 11 対策
│   ├── register_bot_task.ps1         ← Bot 永続登録
│   ├── register_threads_tasks.ps1   ← 投稿/メトリクス系登録（要作成）
│   ├── SETUP.md                      ← 詳細セットアップガイド
│   └── logs/                         ← 全ログ集約
│
└── memory/                          ← (任意) MEMORY.md 索引と詳細メモ
```

---

## 3. 必要なリソースと前提

### 3.1 ソフトウェア

| 名称 | バージョン | 用途 |
|------|----------|------|
| OS | Windows 11 (推奨) / macOS / Linux | ホスト |
| Python | 3.10 以上（推奨 3.12〜3.14） | スクリプト実行 |
| Node.js | 18 以上 | Claude Code CLI |
| Claude Code CLI | 最新 | スキル実行・ヘッドレスモード |
| Git | 任意 | バージョン管理 |
| Discord アプリ | モバイル + デスクトップ | Bot 操作 |

### 3.2 API キー / トークン（オーナーが用意）

| 名前 | 用途 | 取得元 | 期限 |
|------|------|-------|------|
| Anthropic API キー | Claude Code 実行 | console.anthropic.com | 無期限 |
| Threads User ID | 自分の Threads | Meta Developer | 無期限 |
| Threads Access Token | 投稿/取得 | Meta Developer | **60日** |
| Threads App ID / Secret | トークン更新 | Meta Developer | 無期限 |
| Discord Bot Token | Bot 動作 | discord.com/developers | 無期限 |
| Discord Webhook URL | 一方向通知 | サーバーの歯車設定 | 無期限 |
| Discord Owner ID | 自分の Discord ID | 開発者モード | 無期限 |
| Discord Guild ID | Bot を入れるサーバー | サーバー右クリック | 無期限 |

**※ Threads Access Token は 60 日で切れる**ので、期限の数日前にリフレッシュする運用ルールを `.company/secretary/todos/` にリマインダーとして入れること。

### 3.3 各 API の取得手順

詳細は **`scripts/SETUP.md`** に完全版あり。要約だけ:

- **Anthropic**: console.anthropic.com → API キー発行 → `claude --version` で疎通確認
- **Threads**: developers.facebook.com → アプリ作成 → Threads API 追加 → 短期トークン取得 → 長期トークン（60日）に交換
- **Discord**: discord.com/developers/applications → アプリ作成 → Bot タブ → トークン取得 → OAuth2 で必要権限つきの招待 URL を生成 → 自分のサーバーに招待

---

## 4. 核となるファイル群と役割

### 4.1 `.company/CLAUDE.md`（全社ライティングルール）

**全 AI スタッフが従う最上位のルール。** これを書き換えるとシステム全体の動きが変わる。

主な内容:
- ライティング全社ルール（断定 / 「皆さん」NG / 絵文字ルール）
- 「断定」ルールの正しい解釈（ですます調でもOK・だ・である強制ではない）
- アカウント削除リスク管理（危険ワード / リンク頻度 / 売り込み比率）
- 投稿の品質チェックリスト（冒頭1行 / 本文 / 末尾）
- フィードバック原則（AI スタッフは生成前に必ず feedback を読む）

### 4.2 `.company/marketing/CLAUDE.md`（マーケ部署ルール）

Threads 運用に特化したルール。

- 3要素の一貫性（コンセプト・投稿・オファー）
- 当たり訴求公式: `(自分は何者か) × (気づき1つ)`
- 時間帯別の役割（朝=共感 / 昼=質問 / 夕=失敗 / 夜=振り返り / 深夜=思考）
- 過程を見せる原則
- 未完型の投稿

### 4.3 `.company/marketing/feedback/<account>.md`（★ AI 育成の核 ★）

**このファイルが本システムの中核。** オーナーが入れたフィードバックがすべて蓄積される。

#### 構造

```markdown
# <account> フィードバック蓄積

## 使い方（AI スタッフへ）
- 生成前に必ず全文を読む
- 「繰り返し指摘されている項目」を最優先で守る
- 「良かった例」を型として再利用
- 「悪かった例」のパターンを繰り返さない

## 繰り返し指摘されている項目（最優先で守る）
### 冒頭1行
- 固有名詞を入れる（「大手企業」NG → 「パナソニック」OK）
- 数字を入れる（期間 / 人数 / 売上）
- ターゲットを明確に

### 本文
- 体験談・具体数字
- 弱さ開示を最低1か所
...

## 良かった例（型として再利用する）
### ★★★★★ 2026-MM-DD: 投稿X「○○」（伸びた）★★★★★
[投稿全文と、なぜ伸びたかの分析]

## 悪かった例（同じパターンを繰り返さない）
### 2026-MM-DD: 投稿Y「○○」（スベった）
[投稿全文と、なぜスベったかの分析]

## フィードバック履歴（時系列）
### 2026-MM-DD HH:MM - Discord 経由フィードバック
[内容]
```

#### 運用ルール

- **加算式**。同じ指摘を 10 回入れていい。回数が増えるほど精度が上がる
- 追加方法: Discord `/feedback` コマンド or 手動編集 or `/feedback` スキル経由
- AI スタッフ（threads-create-post / threads-daily-run / post_bulk）は **生成前に必ず全文読む**

### 4.4 `.company/marketing/accounts/<account>.md`（ペルソナ）

アカウント別の設定。

- コンセプト（誰が・何を・誰に向けて発信するか）
- ペルソナ詳細（年齢・職業・状況）
- KPI（フォロワー目標 / 投稿数 / エンゲージメント率）
- ピン留め投稿の文面
- オファー（最終的に売りたいもの）

### 4.5 スキル（`.claude/skills/`）

| スキル名 | 役割 |
|---------|------|
| `threads-create-post` | 1 投稿分の下書きを生成 |
| `threads-daily-run` | 1 日 5 投稿 × 2 日分 = 10 投稿を一括生成 |
| `threads-fetch-metrics` | Threads API から実績取得 |
| `threads-publish` | 即時投稿 |
| `threads-analyze` | 投稿実績を分析 |
| `feedback` | フィードバックを `feedback/<account>.md` に蓄積 |
| `secretary-briefing` | 朝礼 / TODO 整理 |
| `research-collect` | Web で最新トレンド収集 |
| `youtube-research` | YouTube から字幕→要約→投稿ネタ |
| **`note-article-generate`** | **日報・意思決定ログから note 記事を物語化して自動生成 (新)** |

各スキルの中身は `.claude/skills/<name>/SKILL.md` に記述。
**配布パッケージにはこれらの SKILL.md がすべて同梱される前提。**

### 4.6 スクリプト（`scripts/`）

| ファイル | 起動タイミング | 役割 |
|---------|------------|------|
| `nightly_pipeline.py` | 02:00 タスクスケジューラ | Claude Code ヘッドレスで `/threads-daily-run` を呼んで10本生成 |
| `threads_auto_post.py <account>` | 07:30/12:30/18:00/21:30/23:00 | キューから1本投稿 (画像付き対応・`image_url` frontmatter あり時) |
| `threads_fetch_metrics.py <account> [days]` | 22:00 | 過去N日のメトリクス取得 + `metrics_to_feedback` 自動連動 |
| **`metrics_to_feedback.py <account> [days]`** | 22:00 (`fetch_metrics` から自動呼出) | **★ 半自動化の核 ★** 投稿実績を分析し、伸びた/スベった例を feedback に自動転記 |
| **`refresh_threads_token.py`** | 毎週日曜 03:00 (タスクスケジューラ) | **★ 60日期限切れ防止 ★** Threads長期トークンを自動更新 + `.env` 書き換え + バックアップ |
| `run_watchlist.py [type]` | 毎日 06:00 / 06:30 (タスクスケジューラ) | **★ 自動リサーチ ★** watchlist.md を読んで YouTube + Web を一括リサーチ |
| `discord_bot.py` | PC ログオン時に常駐 | Discord コマンド応答 (**26 種** + `/queue` の画像添付対応) |
| `_threads_api.py` | (import) | Threads API ラッパー (テキスト/画像両対応) |
| `_discord.py` | (import) | Discord Webhook ヘルパー |
| `_net_wait.py` | (import) | スリープ復帰直後の DNS 待ち |
| `fix_modern_standby.ps1` | 1 回だけ管理者で実行 | Windows 11 Modern Standby 無効化 |
| `register_bot_task.ps1` | 1 回だけ管理者で実行 | Bot の永続タスク登録 |

---

## 5. Discord Bot コマンド一覧

Bot は常駐型で、PC ログオン時に自動起動する。**29 種**:

### 投稿運用
- **`/review [account]`** — 未レビュー下書きを ✅ ✏️ 🔄 ❌ ボタン付きで表示
- **`/post_bulk [count] [account] [theme]`** — AI に N 本生成依頼（feedback 蓄積 + inbox ネタを毎回読む）
- **`/create_post <topic> [type] [purpose] [publish_at]`** — 単発 1 本生成（テーマ/型/目的明示・思いつき即投稿）
- **`/create_post_from_idea <idea_id> [type] [purpose] [publish_at]`** — inbox のネタを消化して 1 本生成
- `/post <text>` — 即時投稿
- `/queue <text> [time] [image] [image_url]` — 任意キュー追加（**スマホ画像添付対応**）
- `/list` — キュー一覧
- `/status` — 現状サマリー

### 🌅 朝の運用 (新)
- **`/morning [account]`** — 朝礼ダッシュボード（昨日結果 / 今日のキュー / 推奨アクション）

### 🚨 リカバリ・運用 (新)
- **`/retry_post [account]`** — 自動投稿失敗時のリカバリ（スマホから即リトライ）
- **`/run task:<choice> [account]`** — バッチジョブ即起動:
  - `metrics` / `nightly` / `token_refresh` / `m2f`
  - `watchlist` / `watchlist_youtube` / `watchlist_web`

### 🔬 リサーチ (新)
- **`/research_youtube <url> [count]`** — YouTube から字幕→要約→投稿ネタ
- **`/research_web [theme]`** — WebSearch で最新トレンド収集
- **`/research_self [account]`** — 自分の過去投稿の数字分析
- **`/competitor_post <user> <text> <why> [views] [likes] [url]`** — 他人の伸びてる投稿を AI 学習素材化
- **`/watchlist`** — 自動リサーチのウォッチリスト確認

### 📝 note 連載 (新)
- **`/generate_article [date]`** — 日報・意思決定ログから note 記事を物語化して自動生成（3000〜5000 字）

### 💬 Claude への直接指示 (新)
- **`/ask <message> [save:True]`** — **スマホから Claude に自由な指示** (ファイル変更 / 設計判断 / 分析 / 調査)
  - 別 Claude (ヘッドレス) が起動し、プロジェクトを操作 (Edit / Write / Bash 全自動承認)
  - やり取りは `.company/secretary/inbox/<ts>_ask_*.md` に永続化
  - 次回 `/ask` の文脈として参照される (連続性確保)
  - 所要 1〜10 分

### フィードバックループ
- **`/feedback <category> <content>`** — `feedback/<account>.md` に追記
- `/idea <content> [category]` — 投稿ネタを inbox に保存
- `/ideas [category]` — ネタ一覧
- `/idea_use <id>` — ネタを使用済みマーク
- `/generate_ideas [category] [count]` — AI にネタを N 本生成依頼

### 日報運用
- `/report` — 今日の日報を表示（なければ作成）
- `/report_add <section> <content>` — セクション追記
- `/report_close [comment]` — 締める
- `/reports` — 過去 7 日一覧

### 管理
- `/help [topic]` — ガイド
- `/sync` — スラッシュコマンド再同期

---

## 6. セットアップ手順

### Step 1: Claude Code をインストール

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

### Step 2: このパッケージを展開

```bash
git clone <repo> myCompany
cd myCompany
```

### Step 3: Python 依存をインストール

```bash
pip install -r scripts/requirements.txt
```

### Step 4: `scripts/.env` を作成

```bash
cp scripts/.env.example scripts/.env
```

エディタで `.env` を開き、以下を埋める:

```env
# Anthropic（Claude Code 用）
ANTHROPIC_API_KEY=sk-ant-...   # ※Claude Code 経由なら別途設定済みの場合あり

# Discord
DISCORD_WEBHOOK_URL=...
DISCORD_BOT_TOKEN=...
DISCORD_OWNER_ID=...
DISCORD_GUILD_ID=...

# Threads
THREADS_USER_ID=...
THREADS_ACCESS_TOKEN=...
THREADS_APP_ID=...
THREADS_APP_SECRET=...

# Windows のみ（フルパス指定が必要な場合）
PYTHON_EXE=C:\Path\To\python.exe
CLAUDE_CMD=C:\Users\<user>\AppData\Roaming\npm\claude.ps1
```

API キーの取得は `scripts/SETUP.md` に完全版あり。Claude Code に「`@scripts/SETUP.md` を読んで、Threads API の取得手順を順番に案内して」と頼むと良い。

### Step 5: アカウント設定ファイルを作成

```
.company/marketing/accounts/<account>.md
```

最低限の中身:

```markdown
---
account: <account>
status: active
concept: <発信コンセプト 1 行>
target: <ペルソナ概要>
phase: 1
---

# <account>

## コンセプト
...

## ペルソナ
...

## KPI（Phase 1）
- フォロワー: 0 → 500（30日）
- 投稿数: 5/日 ×30 = 150 本
- エンゲージメント率: 3% 以上

## ピン留め投稿
...

## オファー
...
```

### Step 6: 初期フィードバックファイルを作成

```
.company/marketing/feedback/<account>.md
```

最初は空でOK。空でも AI は読みに行く設計。  
**運用開始後、Discord `/feedback` で蓄積していくのが正しい流れ。**

### Step 7: Windows タスクスケジューラ登録

**管理者 PowerShell** で:

```powershell
cd <project-root>
powershell -ExecutionPolicy Bypass -File scripts/fix_modern_standby.ps1
powershell -ExecutionPolicy Bypass -File scripts/register_bot_task.ps1
# Threads 投稿/メトリクス系も別途登録（手順は SETUP.md 参照）
```

実行後、**PC 再起動**で Modern Standby 設定を反映。

### Step 8: Bot を即起動

```powershell
Start-ScheduledTask -TaskName "myCompany-DiscordBot"
```

### Step 9: 動作確認

Discord で:
1. `/help` → ガイドが返ってくる
2. `/status` → サマリー表示
3. `/post_bulk count:1` → 1 本生成（2〜3 分待つ）
4. `/review` → 生成された 1 本がボタン付きで表示
5. ✅ ボタン → queued/ に移動、publish_at 自動付与
6. Discord 通知（Webhook 経由）が来れば全レイヤー疎通完了

---

## 7. カスタマイズ可能ポイント

### 7.1 投稿時間帯

タスクスケジューラの 5 タスク（`myCompany-ThreadsPost-XXXX`）を再登録すれば変更可。
合わせて `.company/marketing/CLAUDE.md` の「時間帯別の役割」セクションと、`.claude/skills/threads-daily-run/SKILL.md` の Day 1/Day 2 時間表も書き換える。

### 7.2 1 日の投稿本数

- 毎晩の生成本数を増やす: `nightly_pipeline.py` の Claude プロンプト内の「10 本」を変更
- 自動投稿の枠数を増やす: 上記の 5 タスクを増設

### 7.3 複数アカウント運用

1. `.company/marketing/accounts/<new>.md` を作成（status: active）
2. `.env` に `THREADS_USER_ID_<NEW>` / `THREADS_ACCESS_TOKEN_<NEW>` を追加
3. `nightly_pipeline.py` の `find_active_accounts()` が自動で拾う
4. 自動投稿タスクは複数アカウント分を別タスクで登録する必要あり（要拡張）

### 7.4 ライティングルールの変更

`.company/CLAUDE.md` と `.company/marketing/CLAUDE.md` を書き換える。  
全 AI スタッフは生成前にこれを読むので、即時反映される。

---

## 8. フィードバックループの育て方

### 8.1 最初の 1 週間

- AI の出力に違和感を感じても**怒らず**フィードバックを蓄積する
- Discord で `/feedback` を打つたびに具体的に書く:
  - ✅ 良い例: 「冒頭に固有名詞がない。実際のメーカー名（パナソニック、ユニクロなど）を入れて。数字も1つ入れて」
  - ❌ 悪い例: 「もっとフックを効かせて」「いい感じに直して」

### 8.2 2 週目以降

- 「繰り返し指摘されている項目」がだいぶ消化されて、明らかに精度が上がる
- 「良かった例」（伸びた投稿）を `★★★★★` で明示マークすると、AI がそれを最優先の手本にする

### 8.3 1 か月後

- フィードバックを毎日入れる必要はなくなる
- AI が「自分の文体」を理解した状態になる
- ここから「投稿の量」 × 「フィードバックの精度」で月7桁を狙うフェーズへ

---

## 9. 障害対応と運用知見

### 9.1 Windows 11 で自動化が止まる場合

**原因**: Modern Standby (S0 低電力アイドル) + Wi-Fi の省電力切断

**対策**:
1. `scripts/fix_modern_standby.ps1` を管理者で実行 → 再起動
2. Wi-Fi アダプタの「電源節約のためにこのデバイスをオフにできるようにする」を OFF
3. すべてのスクリプトは `_net_wait.py` で DNS 復帰を最大 3 分待ってから本処理に入る設計

### 9.2 Claude Code ヘッドレスが exit=0 で 0 本生成する場合

**原因の候補**:
- ネット未復帰の状態で Anthropic API 呼び出し失敗
- スキル内で AskUserQuestion など対話前提のツールに当たって早期終了

**対策**:
- `scripts/logs/claude_headless_<ts>.log` に生 stdout/stderr が残るので、そこから原因追跡
- Discord Bot の `/post_bulk` で再生成（こちらは subprocess を独立コンテキストで動かす）

### 9.3 Threads トークン期限切れ（60 日ごと）

- 期限の 1 週間前に `.company/secretary/todos/` にリマインダーが入る運用にする
- トークン更新は短期 → 長期の交換 API を使う（SETUP.md 参照）

---

## 10. トラブルシューティング

| 症状 | チェックポイント | 対処 |
|------|---------------|------|
| Bot が反応しない | `Get-Process python` でプロセスあるか / `scripts/logs/discord_bot.log` | プロセスなければ `Start-ScheduledTask -TaskName 'myCompany-DiscordBot'` |
| 自動投稿が動かない | タスクスケジューラの `LastTaskResult` / `scripts/logs/threads_auto_post.log` | DNS エラーなら `_net_wait` が効くか確認。Threads トークン期限も確認 |
| nightly_pipeline が 0 本 | `scripts/logs/claude_headless_<ts>.log` | `.env` の `CLAUDE_CMD` パス / アカウントの status: active 確認 |
| `/post_bulk` でファイル作られない | `scripts/logs/post_bulk_<ts>.log` | Claude Code ヘッドレスの出力を直接確認 |
| Modern Standby が悪さ | `Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Power PlatformAoAcOverride` | 0 でなければ `fix_modern_standby.ps1` を再実行 |
| Bot タスクが UAC で登録失敗 | スクリプトが Read-Host で止まってないか | ウィンドウを閉じる前にエラー文を確認・必要なら個別実行 |

---

## 11. Claude Code への指示プロンプト（コピペ用テンプレート）

### 11.1 セットアップ初回

```
@BLUEPRINT.md を読んで、myCompany をセットアップしてください。

進める順序:
1. 私の OS / Python / Claude Code の状態を聞いて、足りないものを教えて
2. .env を一緒に作る（聞いてくれれば値を渡す）
3. アカウント設計ファイルの雛形を作って
4. タスクスケジューラ登録の管理者コマンドを提示
5. Discord で動作確認の手順を案内

途中で詰まったら §10 のトラブルシューティングを参照しながら進めて。
```

### 11.2 アカウント追加

```
@BLUEPRINT.md §7.3 を読んで、新しいアカウント <name> を追加してください。
私の手で `.env` に入れる値は教えてください。
```

### 11.3 投稿時間帯の変更

```
@BLUEPRINT.md §7.1 を読んで、投稿時間帯を以下に変更してください:
朝: HH:MM / 昼: HH:MM / 夕: HH:MM / 夜: HH:MM / 深夜: HH:MM
```

### 11.4 障害対応

```
@BLUEPRINT.md §9 §10 を読んで、以下の症状を切り分けてください:
[症状を具体的に書く]
[エラーログがあれば貼る]
```

### 11.5 note 連載記事の自動生成

```
今日の出来事を note 記事にしてください。

実行内容:
1. `.claude/skills/note-article-generate/SKILL.md` の手順に従う
2. 今日の日報 (`.company/secretary/reports/<today>.md`) と
   意思決定ログ (`.company/secretary/notes/<today>-decisions.md`) を読み込む
3. 物語性ある記事 (3000〜5000字) を生成して
   `.company/products/articles/<today>_<slug>.md` に保存

オーナーのキャラ (ですます基本 / 固有名詞+数字 / 弱さ開示) は厳守してください。
```

または Discord で `/generate_article today` でも同じ動作。

---

## 12. 配布物に含まれるべきファイル一覧

このパッケージを zip 化して配布する際、最低限以下を含めること:

- `BLUEPRINT.md`（このファイル）
- `README.md`（簡易版）
- `.claude/skills/` 配下のすべての `SKILL.md`
- `.company/CLAUDE.md` + `.company/marketing/CLAUDE.md` + `.company/secretary/CLAUDE.md` (テンプレート版)
- `.company/marketing/accounts/<sample>.md`（サンプル・購入者がコピーして使う）
- `.company/marketing/feedback/<sample>.md`（空の雛形）
- `scripts/` 配下のすべての Python / PowerShell ファイル
- `scripts/.env.example`
- `scripts/requirements.txt`
- `scripts/SETUP.md`（外部API取得の完全版）

**含めてはいけないもの**:
- `scripts/.env`（実際の認証情報が入っている）
- `.company/marketing/drafts/`（個別の運用ログ）
- `.company/secretary/reports/`（個別の日報）
- `scripts/logs/`（ローカル運用ログ）

---

## 13. ライセンスと利用条件

- 配布元: <配布者名>
- 利用範囲: 購入者本人の個人運用に限る
- 改変: 自由（自分のアカウントで使う限り）
- 再配布: 禁止
- サポート: <連絡先 / Discord サーバー等>

---

## おわりに

本システムは **「フィードバックを書けば書くほど精度が上がる」** 設計です。

- 最初の 1 週間は AI 出力に違和感があっても、`/feedback` でガンガン指摘する
- 2 週目以降、精度の上昇を体感できる
- 1 か月後には、AI が自分の文体を理解した状態になる

ここから「投稿の量」 × 「フィードバックの精度」で、Threads 運用が AI 半自動の事業に変わる。

頑張ってください。

---

*最終更新: 2026-05-14 / Version 1.2*

### 変更履歴
- **v1.2 (2026-05-14 深夜)**:
  - 新スキル `note-article-generate` 追加 (日報→note記事 自動生成・3000〜5000字)
  - 新スクリプト `run_watchlist.py` 追加 (自動リサーチ実行)
  - Discord Bot コマンド: 17 → **26** (+9 種):
    - `/morning` (朝礼ダッシュボード)
    - `/retry_post` (投稿リトライ)
    - `/run` (バッチジョブ即起動・7 サブタスク対応)
    - `/research_youtube` / `/research_web` / `/research_self`
    - `/competitor_post` / `/watchlist` / `/generate_article`
  - `/queue` 拡張: スマホ画像添付対応 (Discord CDN URL)
  - ヘッドレス権限: `acceptEdits` → `bypassPermissions` (Bash も自動承認)
  - 再生成バグ修正: SHA-1 ハッシュ比較で「成功した気になる」を防止
  - 設定ファイル: `.company/research/watchlist.md` (自動リサーチ対象)
  - タスクスケジューラ: `register_research_tasks.ps1` (毎朝 06:00/06:30 自動リサーチ)
  - §11 に note 記事自動生成のプロンプトテンプレ追加
- **v1.1 (2026-05-14 午後)**:
  - `metrics_to_feedback.py` 追加 (投稿実績→feedback 自動転記・半自動化の核)
  - `refresh_threads_token.py` 追加 (60日期限切れ防止・自動更新)
  - `_threads_api.py` に `create_image_post` 追加 (画像投稿対応)
  - `threads_auto_post.py` で `image_url` frontmatter サポート
  - Discord Bot `/queue` に `image_url` パラメータ追加
  - データフロー表に日曜 03:00 のトークン自動更新を追記
- **v1.0 (2026-05-14)**: 初版
