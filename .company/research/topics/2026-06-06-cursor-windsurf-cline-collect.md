---
created: "2026-06-06"
topic: "Cursor / Windsurf / Cline ─ AIコーディングツール最新動向"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 4件
post_ideas: 7件
---

# Cursor / Windsurf / Cline 最新動向（2026-06 時点）

ユーザー指定テーマ「Cursor Windsurf Cline AI コーディング」で WebSearch を実行。
過去 1〜2 ヶ月の固有名詞・数字・新機能を中心に拾い、Threads 投稿に直結できる切り口に整理した。

---

## 1. Cursor 3.7（2026-06-04 リリース）に Canvases 機能

- ソース:
  - [Cursor Changelog](https://cursor.com/changelog)
  - [【2026年5月最新】Cursor 3.0完全ガイド｜Uravation](https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/)
  - [Cursorのchangelog完全ガイド｜.AI TIMES](https://dot-ai.myuuu.co.jp/times/212)
- 公開日: 2026-06-04
- 要点（3行以内）:
  - バージョン 3.7 で **Canvases** を実装。エージェントがダッシュボード・レポート・内部ツールを「永続的アーティファクト」として作成し、チーム共有可能に
  - 5/18 に **Composer 2 → 2.5** へ進化。Agents Window で複数エージェント並列、Background Agents でクラウド側に長尺タスクを投げられる
  - 利用可モデルは GPT-5.5 / Claude Opus 4.7 / Composer 2 など最新ライン
- 投稿アイデア:
  - **型**: 朝学び型 / 教育目的
  - **切り口**: 「Cursor が今週ダッシュボード作れるようになった話。3.7 の Canvases で『AI に内部ツール頼む』が現実になった」
  - **2 本目**: 弱さ枕詞型「コード補完しか使ってなかった僕が、Cursor 3.7 の Canvas でレポート吐かせて 30 分浮いた話」

---

## 2. Windsurf：Devin 統合 + SWE-1.5（Sonnet 4.5 の 13 倍速）

- ソース:
  - [Windsurf 2026: Codeium's Cascade and Agentic IDE](https://www.programming-helper.com/tech/windsurf-2026-codeium-ai-editor-cascade-agent-revolution)
  - [Windsurf Review (2026): SWE-1.5, Codemaps, Cascade, Pricing｜vibecoding.app](https://vibecoding.app/blog/windsurf-review)
  - [Windsurf AI Guide｜MyEngineeringPath](https://myengineeringpath.dev/tools/windsurf-ai/)
- 公開日: 2026 Q1〜Q2
- 要点（3行以内）:
  - **Devin が Windsurf 内に統合**。クラウド上に自分の VM を立て自律タスク処理。Cascade 2.0 はマルチステップ推論強化
  - 自社モデル **SWE-1.5 は Sonnet 4.5 の約 13 倍速** で「準フロンティア級コード品質」を主張
  - **Codemaps**：AI 注釈つき視覚的コードマップ。SWE-1.5 + Sonnet 4.5 駆動でグループ表示／トレース／行リンクまで出す。他社にない機能
  - **料金体系がクレジット制に移行**：Free 25 cr/月、Pro $15/月で 500 cr/月（旧 Pro の無制限は廃止）
- 投稿アイデア:
  - **型**: 夕失敗型 / 信頼構築
  - **切り口**: 「Windsurf Pro の課金、無制限じゃなくなったの気づいてた？2026 春からクレジット制 500 cr/月。Cursor から戻った僕の財布の話」
  - **2 本目**: 教育目的「Codemaps っていう Windsurf 限定機能、コードを地図にしてくれる。Cursor にも Cline にも無い、地味だけど効く 1 機能」

---

## 3. Cline v3.81：SDK 化と自動モデルルーティング（月額 $8〜12 で済む）

- ソース:
  - [Cline for VS Code: Free AI Coding Agent — 2026 Setup Guide｜DeployHQ](https://www.deployhq.com/guides/cline)
  - [GitHub - cline/cline](https://github.com/cline/cline)
  - [Introducing Cline SDK｜cline.ghost.io](https://cline.ghost.io/introducing-cline-sdk-the-upgraded-agent-runtime/)
  - [Cline Review 2026｜OpenAIToolsHub](https://www.openaitoolshub.org/en/blog/cline-review-free-ai-coding)
- 公開日: 2026 春〜（v3.81 系）
- 要点（3行以内）:
  - **@cline/sdk を切り出してオープンソース化**。VS Code / JetBrains / CLI で同じ agent runtime が動く設計に。サードパーティが Cline 上に積める
  - **v3.2（3月）で自動モデルルーティング**：タスク難度に応じて最安モデルを自動選択。**中量級ユーザーの月額 API コストが $8〜12 に収束** という実測
  - プロバイダ 30 超：Anthropic / OpenAI / Gemini / Bedrock / DeepSeek / Moonshot / Qwen / Grok / Mistral / Groq / Ollama / LM Studio など。Apache 2.0、61.2k ⭐、500 万 install 超
- 投稿アイデア:
  - **型**: 昼進捗型 / 教育目的
  - **切り口**: 「Cline の月額、ガチで $10 切ってきた。3.2 の自動ルーティングが『簡単なタスクは Haiku、重いやつだけ Opus』を自動でやる」
  - **2 本目**: 弱さ枕詞型「Cursor の $20/月が高いと感じてた僕が、Cline + DeepSeek で月 $8 まで落ちた話。設定 3 つだけ」

---

## 4. 立ち位置整理：Cursor / Windsurf / Cline をどう使い分けるか（2026 版）

- ソース:
  - [Cline時代のエディタ戦争🧨｜zenn (oumi0804)](https://zenn.dev/oumi0804/articles/758aaab196ce68)
  - [AIコーディング5強比較｜Uravation](https://uravation.com/media/ai-coding-tools-5-comparison-2026/)
  - [Cursor vs Windsurf vs Cline｜UI Bakery Blog](https://uibakery.io/blog/cursor-vs-windsurf-vs-cline)
  - [Cursor vs Windsurf 完全比較｜syncode.jp](https://syncode.jp/articles/cursor-vs-windsurf-2026-comparison/)
- 公開日: 2026 上半期
- 要点（3行以内）:
  - 2026 の論点は「補完精度」ではなく「**プロジェクト全体のコンテキスト理解**」にシフト
  - 推奨構成: **日常開発は Cursor or Windsurf、特定の大型タスクだけ Cline を呼ぶ** という併用パターンが定着
  - 5 強は **Cursor / Windsurf / Cline / Codex / Claude Code**。Windsurf は「0→1（内部ツール生成）寄り」、Cursor は「補完＋エージェント」、Cline は「中〜上級者・節約・自由度」
- 投稿アイデア:
  - **型**: 夜振り返り型 / 信頼構築
  - **切り口**: 「Cursor / Windsurf / Cline のどれを選ぶか問題、2026 年の答えは『1 個に絞らない』。僕の使い分けマップ晒します」
  - **2 本目**: 教育目的「『AI コーディング 5 強』2026 年版は Cursor / Windsurf / Cline / Codex / Claude Code。それぞれ得意領域が違うので 1 枚図にした」

---

## 注目トピック（即投稿化推奨）

**Cline v3.2 の自動モデルルーティングで月額 $8〜12** ─
コスト数字が具体的（千円単位ルール適合）／読者が今日から試せる／Cursor Pro $20 と直接比較できる。
バズ要素 5 つのうち「千円単位」「具体数字」「実用」を満たす最有力ネタ。

次点で **Cursor 3.7 Canvases**（6/4 リリース、鮮度高い）、**Windsurf クレジット制移行**（既存ユーザーの不満を拾える）。

---

## 補足メモ

- 今回拾わなかったテーマ：Claude Code 本体の最新動向（別ファイル `2026-06-06-claude-code-updates.md` に既存あり）、GitHub Copilot Workspace（指定外）
- 次回深掘り候補：Devin 単体の評価記事、Codemaps 実画面レビュー、Cline SDK で何が作れるか実例
