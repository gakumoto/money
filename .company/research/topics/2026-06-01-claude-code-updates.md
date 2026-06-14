---
created: "2026-06-01"
topic: "Claude Code / Anthropic 最新アップデート"
status: completed
tags: ["weekly-collect", "claude-code", "ai-tools", "anthropic-news"]
sources: 12件
post_ideas: 12件
---

# Claude Code 最新アップデート収集（2026-06-01）

---

### Week 22: Claude Opus 4.8 + Dynamic Workflows（2026-05-25〜05-29）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-05-29
- 要点:
  - Opus 4.8 が Max/Team Premium/Enterprise/API アカウントの新デフォルトモデルに
  - **Dynamic Workflows**: スクリプト1本でサブエージェント数十〜数百を並列オーケストレーション可能
  - Fast mode が Opus 4.8 で $10/$50 per MTok で利用可能（速度2.5倍、コスト大幅削減）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Codeが100体のAIを同時に動かす時代が来た。Dynamic Workflowsで何が変わるか」

---

### Week 21: Auto Mode on Pro + /code-review コマンド（2026-05-18〜05-22）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-05-22
- 要点:
  - Auto mode が Pro プランでも利用可能に（Sonnet 4.6 対応）
  - パーミッションプロンプトをバックグラウンド安全チェックに置き換え
  - `/code-review` コマンドで正確性バグを自動検出してレポート
  - `/usage` コマンドでスキル・サブエージェント・プラグイン別の使用状況を可視化
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「『許可しますか？』のポップアップが消えた日。Auto modeで開発体験がどう変わるか」

---

### Week 20: Agent View + /goal コマンド（2026-05-11〜05-15）
- ソース: https://code.claude.com/docs/en/whats-new / https://qiita.com/saitoko/items/bbafd1692c1cd825718a
- 公開日: 2026-05-15
- 要点:
  - `claude agents` で全セッションを1画面で管理（実行中/待機中/完了をひと目で把握）
  - `/goal [条件テキスト]` で条件達成まで Claude が複数ターン自律継続
  - Rewind メニューに「Summarize up to here」でコンテキスト圧縮が可能
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「『終わったら呼んで』が実現した。/goal コマンドで AIに仕事を任せて寝る話」

---

### Week 18: Windows 対応強化 + claude ultrareview（2026-04-27〜05-01）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-05-01
- 要点:
  - Git Bash 不要で Claude Code が Windows で動くように（PowerShell対応）
  - `claude ultrareview` でCIやスクリプトからクラウドコードレビューが呼び出し可能
  - PR URL を `/resume` に貼るとそのPRを作ったセッションを復元できる
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「WindowsユーザーにもClaude Codeの壁が1枚消えた話」

---

### Week 17: /ultrareview パブリックプレビュー（2026-04-20〜04-24）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-04-24
- 要点:
  - `/ultrareview`: クラウド上でバグハンティング専用エージェントの群れがコードレビュー
  - 結果はCLIまたはDesktopに自動返送
  - セッション再開時に「その間に何があったか」を要約するセッションリキャップ機能
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「AIがAIのコードをレビューする時代。/ultrareviewで何が変わるか試してみた」

---

### Week 16: Opus 4.7 + モバイルプッシュ通知 + Routines（2026-04-13〜04-17）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-04-17
- 要点:
  - Opus 4.7 が Max/Team Premium の新デフォルト（`xhigh` effort 推奨）
  - **Routines**: スケジュール・GitHub イベント・API コールでクラウドエージェントを自動起動
  - **モバイルプッシュ通知**: 長時間タスクの完了やClaude の入力待ちをスマホに通知
- 投稿アイデア:
  - 型: 深夜思考型
  - 切り口: 「スマホに『Claude がAIに相談中です』と通知が来た夜の話」

---

### Week 14: Computer Use CLI（2026-03-30〜04-03）
- ソース: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-04-03
- 要点:
  - CLIから実デスクトップのネイティブアプリを開いてクリック・操作が可能に（リサーチプレビュー）
  - GUIでしか確認できない変更のクローズ・ループに対応
  - `/powerup` インタラクティブレッスン機能も追加
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「ClaudeがマウスをクリックしてGUIを操作し始めた。Computer Use CLIが何者か」

---

## 追記: Anthropic 最新ニュース収集（2026-06-01 追記）

---

### Opus 4.8「最も正直なモデル」の中身
- ソース: https://www.inc.com/ben-sherry/anthropic-says-its-latest-claude-model-is-the-most-honest-yet/91351657
- 公開日: 2026-05-29
- 要点:
  - 自分が書いたコードの欠陥を見逃す確率がOpus 4.7比で約1/4に激減
  - 根拠の薄い主張をする傾向が大幅に低下（ハルシネーション対策）
  - 「Low/Medium/High/Max」のエフォートコントロールが追加され、ユーザーがトークン量を制御できる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claudeが『ぼく間違ってました』と言えるようになった。Opus 4.8の"正直さ"が何を意味するか」

---

### Mythos-class モデル予告（数週間以内リリース）
- ソース: https://gizmodo.com/anthropic-debuts-claude-opus-4-8-teases-upcoming-launch-of-mythos-class-models-2000764742
- 公開日: 2026-05-29
- 要点:
  - Anthropicが「Mythos」相当の能力を持つ新規モデルクラスを数週間以内にリリース予定と予告
  - サイバーセキュリティ評価・安全性テスト中（リリース前の最終チェック段階）
  - Opus 4.8 は「Mythos」ではなく、その前のつなぎモデルという位置づけ
- 投稿アイデア:
  - 型: 深夜思考型
  - 切り口: 「Anthropicが『次は別次元のモデルを出す』と予告した。Mythosとは何か」

---

### Claudeサブスク刷新：エージェント利用が別枠化（6月15日〜）
- ソース: https://www.techno-edge.net/article/2026/05/14/5064.html
- 公開日: 2026-05-14
- 要点:
  - 6月15日からAgent SDK・`claude -p`などの自動化利用が別枠クレジット消費に変更
  - 通常チャット用とエージェント用でクォータが分離される（使い方次第で実質値上げ）
  - Pro/Max/Team各プランで別枠クレジット量が異なる
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「6月15日からClaudeの料金体系が変わる。エージェント使いは今すぐ確認を」

---

### Claude Codeプラグイン自動ロード（v2.1.152）
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-05-26
- 要点:
  - `.claude/skills/` ディレクトリのプラグインが起動時に自動ロードされるように
  - `claude plugin init` で新規プラグインのスカフォルディングが可能
  - MCP対応強化：ページネーション対応・環境変数の自動渡し
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Claude Codeが『自分の武器』を自動で読み込むようになった。スキルファイルの使い方」
