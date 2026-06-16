---
created: "2026-06-17"
topic: "Cursor / Windsurf / Cline AI コーディング最新動向"
status: completed
tags: ["weekly-collect", "cursor", "windsurf", "cline", "ai-coding", "claude-code-compare"]
sources: 6件
post_ideas: 9件
---

# Cursor / Windsurf / Cline 最新動向 (2026-06-17 収集)

ユーザー指定テーマ「Cursor Windsurf Cline AI コーディング」を WebSearch で巡回。過去2週間〜1ヶ月以内のアップデート + Claude Code との比較を中心に整理した。Claude Code 推しアカウント（gaku_ai_life）から見て「乗り換え誘発系」「比較ネタ」「他ツールの不満点」が刺さる文脈で抽出している。

---

### Cursor、Teams 課金ルールを 6月に大幅刷新 — 7/1 適用
- ソース: https://releasebot.io/updates/cursor / https://blog.promptlayer.com/cursor-changelog-whats-coming-next-in-2026/
- 公開日: 2026-06 (新規顧客は即時、既存顧客は 7/1 以降の billing cycle から)
- 要点:
  - Teams プランの usage limit を引き上げ、ヘビーエージェント利用者向けに新「Premium seat」を追加
  - Standard seat と Premium seat で usage pool を分離 → コスト見通しが立てやすく
  - リアルタイム可視化 + 賢いアラートで「気づいたら $300 飛んでた」事故を抑制
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor が Teams 課金を 7/1 から変える。1ヶ月で $300 溶かしたあなたへ」/「『使った人が払う』に変わった話」

---

### Cursor v3.0 + Composer 2.5 — Background / Cloud Agents が標準装備に
- ソース: https://anycap.ai/page/en-US/blog/cursor-ai-2026-new-features-guide / https://daily.dev/blog/cursor-ai-everything-you-should-know-about-the-new-ai-code-editor-in-one-place/
- 公開日: 2026年初頭リリース、現行は Composer 2.5
- 要点:
  - Background Agents / Cloud Agents / Composer 2.0 UI の3点で「自動補完ツール → 自律エージェント」へ進化
  - Composer 2.5 は「frontier 性能を 1/数のコストで」が謳い文句
  - `.cursorrules` を「project constitution」と再定義、AI 推論レイヤーが主役・エディタは UI
- 投稿アイデア:
  - 型: 夕失敗型 / 深夜思考型
  - 切り口: 「Cursor が `.cursorrules` を『憲法』と呼び始めた件」/「エディタが UI に成り下がる時代」

---

### Windsurf Wave 13 — Cascade Memory + Multi-Model Routing
- ソース: https://www.programming-helper.com/tech/windsurf-2026-codeium-ai-editor-cascade-agent-revolution / https://myengineeringpath.dev/tools/windsurf-ai/
- 公開日: 2026年（Wave 13）
- 要点:
  - Cascade Memory がコードベース構造と好みを「会話を跨いで」記憶
  - Multi-Model Routing がタスクに応じてベストモデルを自動選択（Gemini 3 Pro / GPT-5.1 / GPT-5.1-Codex / SWE-1.6 まで対応）
  - Supercomplete の予測精度を強化、関数・クラス実装の予測ヒット率が上がる
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Windsurf が『会話を跨いで覚える』ようになった。Claude Code の `CLAUDE.md` と何が違う？」

---

### Windsurf × Devin 統合、Pro $20/月で Cursor と同価
- ソース: https://www.fundesk.io/windsurf-ide-review-codeium-ai-editor-2026 / https://windsurf.com/changelog
- 公開日: 2026 (v2.12.23 は 2026-05-11)
- 要点:
  - Cognition の Devin クラウドエージェント + 自社 SWE-1.6 モデルを Cascade に統合
  - 価格は credit 制 → quota 制に移行、Pro $15→$20 で Cursor と完全同価
  - Cascade auto-fetch の web request allowlist 設定が v2.12.23 で追加（情シスが嫌がるやつ対策）
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「Cursor も Windsurf も Pro $20/月で並んだ。差分は『モデルの選び方』だけになった話」

---

### Cline v3.82.0 + インストール 500万突破 (2026-05)
- ソース: https://dev.to/jovan_chan_9500711396d4e6/cline-review-2026-is-the-best-free-ai-coding-agent-actually-free-447p / https://www.deployhq.com/guides/cline
- 公開日: 2026-05-01 (v3.82.0) / 2026-05 (5M installs 達成)
- 要点:
  - VS Code Marketplace + Open VSX 合計で 5,000,000 install 突破、GitHub Stars は 61,000+
  - 2026 は VS Code 以外に JetBrains / Cursor / Windsurf / Zed / Neovim へ拡張、macOS/Linux CLI も preview
  - v1.1.58 (2026-05-19) で SAP AI Core サポート追加 — 「会社の AI ゲートウェイ」をそのまま使える企業向け
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Cline が VS Code を出て、Cursor の中でも動く時代。『AI エディタ戦争』そのものが空中分解しつつある」

---

### Cline は「拡張は無料、API は自分で払う」モデル — 隠れコスト構造
- ソース: https://aicoderscope.com/blog/cline-claude-dev-review/ / https://codersera.com/blog/self-hosted-ai-coding-agent-2026/
- 公開日: 2026
- 要点:
  - 拡張は完全無料、課金は Anthropic / OpenAI / OpenRouter / Bedrock / Azure / Gemini / Ollama / LM Studio に直接行く
  - 24GB GPU 1枚で Ollama + Cline の「自律コーディングループ」がローカル完結可能 (ソースが社外に出ない)
  - 「無料」と言いつつ、結局 Anthropic 課金が乗るので、Claude Code 直契約と総額が変わらない罠
- 投稿アイデア:
  - 型: 夕失敗型
  - 切り口: 「Cline は無料じゃない。『API は自分で払って』が小さく書いてある」/「ローカルで動く Cline で社外秘コードを触る選択肢、思ったより現実的だった」

---

### Claude Code vs Cursor vs Windsurf — 2026年の正直な比較
- ソース: https://dev.to/pockit_tools/cursor-vs-windsurf-vs-claude-code-in-2026-the-honest-comparison-after-using-all-three-3gof / https://www.aibuilderclub.com/blog/claude-code-vs-cursor-vs-windsurf
- 公開日: 2026
- 要点:
  - 複数ファイル絡む複雑タスクで Claude Code 23 分 vs Cursor 47 分 / SWE-bench Pro 51.8% vs 49.8% — Claude Code が勝つ
  - ただし「スコープが切られた小タスク」では Cursor / Windsurf の方が速い
  - 用途別: end-to-end でフィーチャを出すなら Claude Code、最速エディタなら Cursor、企業ガバナンス込みなら Windsurf
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Code が Cursor に 2 倍速で勝つ条件 = 『複数ファイルを跨ぐ』時だけ。逆に言うと小タスクなら負ける」

---

### Cursor が「credit 制」継続、Windsurf は「quota 制」へ — 価格モデルの分岐
- ソース: https://www.shareuhack.com/en/posts/cursor-vs-claude-code-vs-windsurf-2026 / https://prommer.net/en/tech/guides/claude-code-vs-cursor-vs-windsurf/
- 公開日: 2026
- 要点:
  - Cursor Pro $20 → $20 credit pool 制（Agent モード使うと一気に焼ける）
  - Windsurf は credit → quota（rate limit）に移行、「予測しやすい」を売りに
  - Claude Code は Anthropic Max / Team Premium のサブスク前提 → 別軸
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Cursor で月末『残りクレジット 0』食らった人へ。Windsurf は quota に逃げた」

---

### Cursor / Windsurf / Cline はすべて「VS Code フォーク or 拡張」、Claude Code だけ違う
- ソース: https://www.mindstudio.ai/blog/windsurf-vs-cursor-vs-claude-code / https://dextralabs.com/blog/claude-code-vs-cursor-vs-windsurf/
- 公開日: 2026
- 要点:
  - Cursor / Windsurf は VS Code フォーク、Cline は VS Code/JetBrains 拡張
  - Claude Code は terminal-based CLI、IDE ではない
  - 「画面なし・AI が深く読む」を選ぶ vs 「画面あり・自分も触る」を選ぶ、の二極化
- 投稿アイデア:
  - 型: 深夜思考型
  - 切り口: 「IDE を捨てた Claude Code と、IDE を抱きしめる Cursor。3 年後、どっちが残ってる？」

---

## まとめ・次の一手

- **6月の旬ネタ**: Cursor の Teams 課金変更 (7/1 適用) と Windsurf Wave 13 + Devin 統合の2本が時事性最高
- **比較系の即投稿化候補**: 「Claude Code 23分 vs Cursor 47分」「Pro $20 で同価になった」「IDE フォーク vs CLI」の3パターン
- **Cline は『無料』の文脈で2投稿作れる**: 「拡張は無料 / API は自分で払う」と「ローカル完結 24GB GPU 1枚」は別ネタとして分離可
- **危険ワード注意**: 「稼ぐ」「収益化」は不要。AI ツール比較は事実・数字で勝負、煽り不要
