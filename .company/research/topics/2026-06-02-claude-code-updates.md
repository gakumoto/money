---
created: "2026-06-02"
topic: "Claude Code 最新アップデート（W22 詳細掘り下げ + W23 差分）"
status: completed
tags: ["weekly-collect", "claude-code", "anthropic-news", "security-guidance", "dynamic-workflows"]
sources: 7件
post_ideas: 7件
---

# Claude Code 最新アップデート収集（2026-06-02）

> 昨日 2026-06-01-claude-code-updates.md でカバー済の情報（Opus 4.8 概要 / Mythos 予告 / 6-15 サブスク変更 / Skills 自動ロード v2.1.152）は除外。
> 本日は **W22 公式ダイジェストの中身** と **W22 → W23 で出た細かい新機能** を掘る。

---

### Security-guidance プラグイン — 3 段階レビューで「書きながら脆弱性を潰す」
- ソース: https://code.claude.com/docs/en/security-guidance / https://www.helpnetsecurity.com/2026/05/27/anthropic-claude-code-security-guidance-plugin/
- 公開日: 2026-05-27
- 要点（3行以内）:
  - 全プラン無料。`/plugin install security-guidance@claude-plugins-official` → `/reload-plugins` で即有効
  - 3 段階レビュー：①編集ごとのパターンチェック（モデル不要・無料）②各ターン終了時に git diff をモデルレビュー ③コミット/プッシュ時に周辺ファイルまで深堀り検査
  - `.claude/claude-security-guidance.md` に脅威モデルルール、`.claude/security-patterns.yaml` にカスタム正規表現を置ける（v2.1.144+ / Python 3.8+ 必須）
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「『AIにコード書かせるとセキュリティが不安』を Anthropic 自身が無料プラグインで潰しに来た。1行で入る」

---

### Dynamic Workflows — `workflow` という単語が「JS スクリプトを書く合図」になる
- ソース: https://code.claude.com/docs/en/workflows / https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- 公開日: 2026-05-28
- 要点（3行以内）:
  - プロンプトに `workflow` という単語を入れると、Claude が **JavaScript のオーケストレーションスクリプトを自動生成** → 数十〜数百のサブエージェントを並列実行
  - `/effort ultracode` にすると、`workflow` と書かなくても実質的な作業すべてでワークフローを自動計画
  - 実行中も会話セッションは応答可能。`/workflows` で進捗・キャンセル管理
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Claudeに『workflow』って単語を入れるだけで、100体のAIが裏で動き始める仕様だった」

---

### Fast Mode 価格改定 — Opus 4.8 で「3倍安く、2.5倍速く」
- ソース: https://code.claude.com/docs/en/whats-new/2026-w22
- 公開日: 2026-05-29
- 要点（3行以内）:
  - Fast mode のデフォルトが Opus 4.8 に。価格は **$10/$50 per MTok**（4.7/4.6 の $30/$150 から 1/3）
  - 速度は通常の約 2.5 倍、コストは通常レートの 2 倍（速度 ÷ コスト効率は事実上 1.25 倍）
  - Opus 4.6 の fast mode は **deprecated**（廃止予定）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Code の fast mode が突然 1/3 の値段になっていた話。`/fast` 押すだけ」

---

### MessageDisplay フック — アシスタントの返答を「表示直前に書き換えられる」
- ソース: https://code.claude.com/docs/en/whats-new/2026-w22
- 公開日: 2026-05-29
- 要点（3行以内）:
  - 新フックイベント `MessageDisplay`：アシスタントが返したテキストを、ユーザーに表示する直前に変換・非表示にできる
  - 機密マスキング・社内用語の置換・「えっへん」みたいな口癖の付与など、表示層だけのカスタムが可能に
  - 一緒に `SessionStart` フックが `reloadSkills: true` を返せるように → セッション内で動的にインストールしたスキルがそのターンから使える
- 投稿アイデア:
  - 型: 教育目的（技術寄り）
  - 切り口: 「AIの返答を『口調だけ』カスタマイズするフックが追加された。MessageDisplay の使い道3つ」

---

### Skill / Command 側の `disallowed-tools` ＋ プラグイン `defaultEnabled: false`
- ソース: https://code.claude.com/docs/en/whats-new/2026-w22
- 公開日: 2026-05-29
- 要点（3行以内）:
  - スキル・コマンドの frontmatter に `disallowed-tools` を書けるように → そのスキル発動中だけ特定ツールをモデルから隠せる（例：レビュースキル中は Bash 禁止）
  - プラグインの `plugin.json` or マーケット側で `defaultEnabled: false` 指定可能 → インストールしてもオフ状態で待機 → 必要時だけ有効化
  - `/reload-skills` で再起動なしで `.claude/skills/` を再スキャン（昨日カバーした自動ロードの兄弟機能）
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「『このスキル中は Bash 禁止』をフロントマターに1行で書けるようになった。事故防止に効く」

---

### 背景ジョブ実行：`!` 接頭辞 + `claude --bg --exec`
- ソース: https://code.claude.com/docs/en/whats-new/2026-w22
- 公開日: 2026-05-29
- 要点（3行以内）:
  - `claude agents` 内でシェルコマンドの頭に `!` を付けるとバックグラウンドジョブ化（attach / detach 可）
  - 同じことを `claude --bg --exec 'pytest -x'` で CLI から起動できる
  - ストリーミング tool 実行が **常時有効化**（テレメトリ OFF や Bedrock/Vertex/Foundry でも動く）
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「`! pytest -x` だけでテストをバックグラウンド化できる。長時間タスクに張り付かなくていい」

---

### 「workflow」という単語の暴発を止める設定（W22 → W23 の後追い修正）
- ソース: https://releasebot.io/updates/anthropic/claude-code / https://code.claude.com/docs/en/whats-new
- 公開日: 2026-05-30〜2026-06-02 のリリースで段階的に
- 要点（3行以内）:
  - Dynamic Workflows のキーワード `workflow` が誤発火しすぎる声を受けて、`/config` に **Workflow keyword trigger** ON/OFF が追加
  - ワークフロー提案が出た直後に **Backspace** で却下できるショートカットも実装
  - 同時に `claude agents` の tmux 内コピー、`--resume` のセッション選択、`/model` のバージョンヒントなど細かい修正多数
- 投稿アイデア:
  - 型: 失敗共有型（昼進捗系）
  - 切り口: 「『workflow』って書いただけで AI が暴走するバグ、Anthropic が3日で潰しに来た速さ」

---

## 今日収集して投稿への落とし方

- 一番のホット：**Security-guidance プラグイン**（無料・1コマンド・「AIに書かせると不安」を一発解決）
- 数字が強い：**Fast Mode 1/3 値下げ**（$30/$150 → $10/$50）
- ニッチで刺さる：**MessageDisplay フック**（フック使う人にはマニアックに刺さる）
- 即下書き化推奨：**Security-guidance + Fast Mode 値下げ** の2本立てで、朝学び型として gaku_ai_life 向けに走らせるのが筋がいい
