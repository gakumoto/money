---
created: "2026-06-07"
topic: "Cursor / Windsurf / Cline ─ 直近2週間の差分"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 4件
post_ideas: 6件
---

# Cursor / Windsurf / Cline 最新動向（2026-06-07 差分）

昨日（2026-06-06）の同テーマ収集と重複しない、**直近2週間で出た新事実**だけを拾った。
ユーザー指定テーマ「Cursor Windsurf Cline AI コーディング」。

---

## 1. Cursor Composer 2.5（2026-05 リリース、安定運用フェーズ入り）

- ソース:
  - [Cursor Changelog](https://cursor.com/changelog)
  - [Meet the new Cursor](https://cursor.com/blog/cursor-3)
- 公開日: 2026-05（5月後半）
- 要点（3行以内）:
  - Composer 2 → 2.5 で「長尺タスクを途中で諦めない」性能が改善。複雑な指示を素直に追える
  - Background Agents（クラウド側で走らせるエージェント）と組み合わせて使う想定
  - Tab 補完は **100,000 トークン** のコンテキストで複数行先読み（Supermaven 由来エンジン）
- 投稿アイデア:
  - **型**: 朝学び型 / 教育目的
  - **切り口**: 「Cursor の Tab 補完、コンテキスト 10 万トークンに伸びてる。長いファイルでも『次に直したい場所』を先読みする精度が別物になった」

---

## 2. Cursor Design Mode（2026-06、ブラウザ版で導入）

- ソース:
  - [Cursor Changelog](https://cursor.com/changelog)
  - [Cursor Release Notes - June 2026](https://releasebot.io/updates/cursor)
- 公開日: 2026-06
- 要点（3行以内）:
  - ブラウザ版 Cursor に「Design Mode」追加。**クリック / 線を描く / 声で指示**で UI を編集できる
  - エージェントが対象 DOM を理解した上でコードに反映
  - 「Figma 開いてコード書き直す」往復が要らなくなる方向の機能
- 投稿アイデア:
  - **型**: 夕失敗型 / 教育目的
  - **切り口**: 「Cursor の Design Mode 触った。UI を直すのに『この余白を 8px 詰めて』を声で言うだけで Tailwind のクラスが書き換わる。Figma に戻る時間がなくなる」

---

## 3. Cursor が Jira に常駐（2026-06）

- ソース:
  - [Cursor Changelog](https://cursor.com/changelog)
- 公開日: 2026-06
- 要点（3行以内）:
  - Jira のチケット内で **@Cursor をメンション**するとクラウドエージェントが起動
  - 「チケット切る → 担当 Cursor → 自動で PR」の動線
  - チームでの分業が前提のアップデート。個人開発でも GitHub Issue 連携に応用可
- 投稿アイデア:
  - **型**: 昼進捗型 / 信頼構築
  - **切り口**: 「Cursor が Jira に常駐するようになった。チケットに @Cursor 書くだけで PR まで来る。一人会社でも GitHub Issue でやれば近いことができる」

---

## 4. Windsurf 改め Devin Desktop。Cognition が $25B 評価で Codeium 買収（2026 春）

- ソース:
  - [Devin Desktop（旧 Windsurf）](https://windsurf.com/editor)
  - [Windsurf 2026 ガイド｜Programming Helper](https://www.programming-helper.com/tech/windsurf-2026-codeium-ai-editor-cascade-agent-revolution)
- 公開日: 2026-04 〜 2026-06
- 要点（3行以内）:
  - Cognition（Devin の会社）が Codeium を買収、4 月時点で **評価額 $25B**（Bloomberg 報）
  - Windsurf は **Devin Desktop** にリブランディング。Agent Command Center（Spaces / Kanban）が前面に
  - 価格はクレジット制から **クォータ制**へ。Pro は $20/月で Claude 4 Sonnet / Opus 利用可
- 投稿アイデア:
  - **型**: 深夜思考型 / 信頼構築
  - **切り口**: 「Windsurf が Devin Desktop に名前変わってた。$25B でクライン買収って世界線、一人会社で AI 使ってる側からするとちょっと怖い」

---

## 5. Cline SDK 化。Cursor / Windsurf / JetBrains / Zed / Neovim でも動く（2026）

- ソース:
  - [Introducing Cline SDK](https://cline.ghost.io/introducing-cline-sdk-the-upgraded-agent-runtime/)
  - [Cline GitHub](https://github.com/cline/cline)
- 公開日: 2026（v3.81 系）
- 要点（3行以内）:
  - Cline のコア（エージェントランタイム）が **@cline/sdk** として切り出された。VS Code 専用じゃなくなった
  - JetBrains / Cursor / Windsurf / Zed / Neovim / macOS・Linux 用 CLI で動作
  - UI 再起動でセッション死ぬ問題が解消。長尺タスクが端末をまたいで継続
- 投稿アイデア:
  - **型**: 朝学び型 / 教育目的
  - **切り口**: 「Cline、VS Code 拡張じゃなく『エージェントランタイム』になってた。Cursor の中で Cline 動かす日が来てる。BYOK 派の選択肢が一気に広がった」

---

## 6. Cline Plan/Act モードと 30+ プロバイダ対応

- ソース:
  - [Cline 公式](https://cline.bot/)
  - [Cline VS Code Guide｜DeployHQ](https://www.deployhq.com/guides/cline)
- 公開日: 2026 通年
- 要点（3行以内）:
  - **Plan モード**で読むだけ・**Act モード**で実行という二段切替。誤爆を減らす設計
  - Anthropic / OpenAI / Gemini / Bedrock / Azure / OpenRouter / Cerebras / DeepSeek / Qwen / Grok / Mistral / Groq / Ollama 等 **30+ プロバイダ**
  - 拡張機能インストール **5M+**、GitHub Star **61.2k**。OSS で最大規模
- 投稿アイデア:
  - **型**: 夕失敗型 / 教育目的
  - **切り口**: 「Cline で勝手に消されたファイルを救った話。Plan モードで先に『何をやるか』読んでから Act に切り替える、これだけで事故が半分になる」

---

## 結論

- **直近の主役**: Cursor の Design Mode（声でUI編集）と Cline の SDK 化（他IDEに進出）が「触感の変わるアップデート」。投稿の入口にしやすい
- **見出し用の固有名詞・数字**: Composer 2.5 / 100,000 トークン / Design Mode / Jira @mention / Devin Desktop / $25B / SDK / 5M+ install / 30+ プロバイダ
- **gaku_ai_life との相性**: 「Cursor / Windsurf / Cline どれ？」より、**1ツール × 1新機能 × 自分の失敗** の弱さ枕詞型が一番刺さる。比較投稿はリンク貼らずに本文だけで完結させる

## ネクストアクション

1. 上記 6 案のうち、**「Cursor Design Mode を声で触った」** と **「Cline SDK 化で Cursor の中で動く」** を /threads-create-post で即下書き化する
2. 比較記事（Cursor vs Windsurf vs Cline）は note の有料枠ネタとしてキープ。Threads では出さない（リンク投稿比率が上がるため）
3. 今週中に Windsurf → Devin Desktop の名称変更を実体験して、次の収集で「使ってみた」型に格上げ
