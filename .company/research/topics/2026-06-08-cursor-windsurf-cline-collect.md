---
created: "2026-06-08"
topic: "Cursor / Windsurf / Cline 最新動向"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline", "editor-wars"]
sources: 4
post_ideas: 8
---

# Cursor / Windsurf / Cline 最新情報（2026-06-08 収集）

AIコーディングエディタ三強の最新アップデート。テーマは「2026年春〜初夏の進化」と「個人開発者がどれを選ぶか」。

---

## 1. Cursor 3.7（2026年6月リリース）に Design Mode 追加

- ソース: https://releasebot.io/updates/cursor
- 公開日: 2026-06（June 2026 アップデート）
- 要点:
  - Cursor browser 内で「クリック・描画・音声」で UI 修正指示が可能に
  - エージェントが UI を更新する設計→コード往復ループの短縮
  - Enterprise Organization Management も同月追加（Groups、予算管理）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor が"描いて伝える"段階に入った。文章で説明する時代の終わり」
  - 切り口: 「画面を指で囲って『ここ直して』が成立する。UI 修正のコスト 1/10」

---

## 2. Composer 2.5 / Cursor 3.0 のエージェント化

- ソース: https://cursor.com/blog/cursor-3
- 公開日: 2026-04（Cursor 3.0 リリース）/ 5月以降 Composer 2.5
- 要点:
  - Background Agents / Cloud Agents で長時間タスクを裏で走らせる
  - Postgres・Supabase を直接クエリしてスキーマ推論
  - Linear / GitHub / Jira とネイティブ統合（チケット読み、PR 起票、Issue 更新）
  - ブラウザを実際に操作して E2E テスト実行
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「Cursor がもう IDE じゃない。"裏で勝手にPRを上げる同僚"になっていた」
  - 切り口: 「個人開発者が1人で複数の Background Agent を回せる時代。手は2本のまま」

---

## 3. Windsurf 2.0 → Devin Desktop に名称統合（Cognition 買収後）

- ソース: https://www.fundesk.io/windsurf-ide-review-codeium-ai-editor-2026
- ソース: https://vibecoding.app/blog/windsurf-review
- 公開日: 2026-04-15（Windsurf 2.0 出荷）
- 要点:
  - Cognition（Devin の親会社）に買収済み、IDE 名は Devin Desktop へ
  - Agent Command Center（Kanban で全エージェント管理）、Spaces（context 束）追加
  - 自社モデル SWE-1.5 が Sonnet 4.5 比 13倍速、SWE-grep で context 取得 10倍速
  - Codemaps：AI 注釈付きビジュアルコードナビ（他に無い独自機能）
  - Pro $20/月（Cursor と同額になった）
- 投稿アイデア:
  - 型: 深夜思考型 / 信頼構築
  - 切り口: 「Windsurf が Devin の中に吸収された。AI IDE 戦争はもう"買収フェーズ"」
  - 切り口: 「『Devin が IDE の中に住んでる』は便利。でも IDE が誰の持ち物か気にする時代に」

---

## 4. Cline v3.78〜v3.81：Spend Limit と CLI 2.0

- ソース: https://cline.bot/
- ソース: https://devops.com/cline-cli-2-0-turns-your-terminal-into-an-ai-agent-control-plane/
- 公開日: 2026-04（v3.78）〜 2026年6月時点で v3.81
- 要点:
  - GitHub 61.2k star / 5M+ install / Apache 2.0 オープンソース
  - 30+ プロバイダー対応（Anthropic, OpenAI, Gemini, Bedrock, Cerebras, DeepSeek, Moonshot, Qwen, Grok, Mistral, Groq, Ollama, LM Studio…）
  - v3.78 で「Spend Limit Reached」UI 追加（日/月キャップ）→ 暴走で残高ゼロ防止
  - Cline CLI 2.0：ターミナル UI で Plan/Act タブ切替、IDE 不要
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Cline に"今月3,000円まで"って枠を設定できるようになった。暴走怖い人へ」
  - 切り口: 「Cline は VS Code 拡張で無料。API キーだけ刺せば $20/月の壁が消える」

---

## 5. Plan / Act モードがエージェント開発の標準パラダイムに

- ソース: https://cline.bot/blog/plan-smarter-code-faster-clines-plan-act-is-the-paradigm-for-agentic-coding
- 公開日: 2026年（Cline 公式記事）
- 要点:
  - Plan モード = 非破壊的に「何をどう作るか」を対話で固めるフェーズ
  - Act モード = 実行フェーズ。1ファイル・1コマンドごとに承認、もしくは自動承認
  - 「合意 → 実行」の分離が、暴走と再設計コストを最小化
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「AI コーディングの正解は『計画と実行を分けること』。Cline の Plan/Act が答え」
  - 切り口: 「Vibe coding で詰む人は Plan を飛ばしてる。最初の10分の対話で8割決まる」

---

## 6. ソロプレナー視点の三択：価格と思想で選ぶ

- ソース: https://f3fundit.com/cursor-vs-windsurf-vs-cline-best-ai-code-editor-solopreneurs-2026/
- ソース: https://uibakery.io/blog/cursor-vs-windsurf-vs-cline
- 公開日: 2026年（比較記事複数）
- 要点:
  - Cursor $20/月：プロ・チーム最強。エンタープライズ機能厚い
  - Windsurf $15〜20/月：Cascade / Devin cloud agent、SWE-1.5 で爆速
  - Cline 無料（OSS）：API トークン課金のみ。プロンプトもルーティングも自分で握れる
  - 「Cline は hackers の選択肢、Cursor は企業の選択肢、Windsurf はその中間」
- 投稿アイデア:
  - 型: 夕失敗型 / 共感
  - 切り口: 「AI エディタ $20/月 × 3 本契約してた頃の自分に言いたい。Cline で十分だった」
  - 切り口: 「『どれが一番か』じゃない。"自分で握りたい範囲"で選ぶ。Cline / Windsurf / Cursor の正体」

---

## 注目トピック（即投稿化推奨）

1. **Cursor 3.7 の Design Mode**：個人開発の UI ループが激変する話題性。朝の教育投稿に最適
2. **Cline の Spend Limit**：「暴走で課金破産」恐怖を持つ層に刺さる、共感系の昼投稿向け
3. **Windsurf が Devin に吸収**：業界変動として深夜思考型でストック投稿に化ける
