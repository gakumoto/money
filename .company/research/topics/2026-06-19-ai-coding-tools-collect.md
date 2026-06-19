---
created: "2026-06-19"
topic: "AIコーディングエディタ最新動向 (Cursor / Windsurf / Cline / Claude Code)"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline", "claude-code"]
sources: 6
post_ideas: 7
---

# AIコーディングエディタ最新動向 (2026年6月時点)

## 全体マップ (3〜4強体制に再編)

2026年に入ってから、AIコーディングエディタ市場は Cursor の独走から、Windsurf (旧Codeium / 現Devin Desktop) と Claude Code を加えた **3強体制** に再編された。Cline は「VSCode拡張・無料・BYO API key」のポジションで4番手として存在感を出している。

| ツール | 形態 | 料金 (Pro) | 強み |
|---|---|---|---|
| Cursor | VSCodeフォーク | $20/mo | Composer・Agents Window・成熟したエコシステム |
| Windsurf (Devin Desktop) | VSCodeフォーク | $15/mo | Cascade・Flow・自律エージェント思想 |
| Cline | VSCode拡張 | 無料 + API従量 | BYO key・Claude/OpenAI/Gemini/Ollama対応 |
| Claude Code | ターミナルCLI | API従量 | SWE-bench Verified 80.8% (ベンチ首位) |

---

## 1. Cursor 3.0 (2026年4月2日リリース)

- ソース: [【2026年5月最新】Cursor 3.0完全ガイド](https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/)
- ソース: [Cursor AI機能まとめ 2026年版](https://aipicks.jp/mag/cursor-ai-features-guide-2026)
- 公開日: 2026-04-02 (リリース日)
- 要点:
  - **Agents Window** (`Cmd+Shift+P`)で複数エージェントを並列実行
  - **Design Mode** (`⌘+Shift+D`)でブラウザUIを直接指定してエージェントに伝える
  - **Composer 2** (2026年3月19日): Cursor自前のコーディングモデルを搭載
  - 料金はリクエストベース → クレジットベース (2025/6) → 5プラン体制 (2026/3)
- 投稿アイデア:
  - 型: 夕思考型 / 教育目的
  - 切り口: 「Cursor 3.0 が AI エージェント前提で UI 再設計された件。Claude Code 派の自分が触って思ったこと」

---

## 2. Windsurf → Devin Desktop へリブランド

- ソース: [Windsurfとは？Devin Desktopへリブランド](https://ai-revolution.co.jp/media/what-is-windsurf/)
- ソース: [Windsurf vs Cursor vs Claude Code 2026](https://www.worktypeslab.com/windsurf-cursor-claude-code-comparison-2026/)
- 公開日: 2026年 (Cognition AI傘下で再ブランド)
- 要点:
  - Codeium → Windsurf → **Devin Desktop** へ改名 (Cognition AI傘下)
  - **Cascade** がプロジェクト全体を理解する自律エージェント
  - **Flow** の思想: 開発者は意図を伝えるだけで AI が探索→実行→デバッグまで自律
  - Pro $15/mo は Cursor より安く、無料枠もより寛大
- 投稿アイデア:
  - 型: 朝学び型 / 信頼構築目的
  - 切り口: 「Windsurf が Devin Desktop に名前変わってた。AI コーディング界の動きが速すぎる件」(短文・気づき型)

---

## 3. Cline 3.88.0 (2026年6月最新版)

- ソース: [Cline完全ガイド v3.88.0](https://warokai.com/2026/06/06/cline-complete-guide-2026-v3-88-autonomous-ai-coding-vscode/)
- ソース: [Cline VSCode拡張 Claude Code比較](https://genai-ai.co.jp/ai-kanri/blog/cc-cline-vscode-guide/)
- 公開日: 2026-06-06
- 要点:
  - VSCode拡張機能自体は**完全無料**、API キーだけで動く (BYOK)
  - 世界 500 万人以上が利用、GitHub Star 3 万超 (2026年4月時点)
  - Anthropic / OpenAI / Gemini / AWS Bedrock / Ollama / LM Studio 対応
  - **2026年2月: CLI 2.0 とネイティブサブエージェント追加** → CI/CD 統合・並列タスク実行可
  - 全操作に承認フローあり (意図しない変更を防ぐ)
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Cline、VSCode 拡張で無料・API キーだけで Claude も Gemini も呼べる。Cursor 月 $20 払えない人の現実解」
  - 型: 朝学び型
  - 切り口: 「Cline がサブエージェント並列実行に対応してた。Claude Code とどう使い分けるか考えた」

---

## 4. Claude Code がベンチで首位 (SWE-bench Verified 80.8%)

- ソース: [Best AI Coding Agents 2026](https://admix.software/blog/best-ai-coding-agents)
- ソース: [Cursor vs Windsurf vs Claude Code 2026](https://dev.to/pockit_tools/cursor-vs-windsurf-vs-claude-code-in-2026-the-honest-comparison-after-using-all-three-3gof)
- 公開日: 2026年 (継続更新)
- 要点:
  - **SWE-bench Verified 80.8%** で Cursor/Windsurf より上
  - ただし IDE ではなくターミナル CLI
  - IDE 派から見ると「ターミナルに戻る」という心理的ハードルがある
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築目的
  - 切り口: 「Claude Code がベンチ首位なのに伸び悩むのは、ターミナル文化に戻る怖さがあるからかもしれない」

---

## 5. 4ツール使い分け論

- ソース: [The 2026 AI Coding Assistant Showdown](https://dev.to/linou518/the-2026-ai-coding-assistant-showdown-cursor-vs-copilot-vs-windsurf-vs-cline-vs-claude-code-64e)
- 公開日: 2026年
- 要点:
  - Cursor = 成熟エコシステム、お金払える人の標準
  - Windsurf = Cursor より安く同等機能、自律性で勝負
  - Cline = ベンダーロックされたくない人・BYOK 派
  - Claude Code = ベンチ最強、CLI 慣れた人
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「AI コーディングツール、結局どれ？を 3 行でまとめる」(リスト型・保存される投稿)

---

## 注目度ランキング (即投稿化推奨)

1. **Cline 無料 + BYOK** (副業層への実用情報、競合比で具体数字あり) ★★★
2. **Cursor 3.0 Agents Window / Design Mode** (新しさ・具体機能) ★★★
3. **Windsurf → Devin Desktop 改名** (短文気づき型に最適) ★★
4. **4ツール使い分け 3 行まとめ** (保存される投稿) ★★

## 心得メモ
- gaku は Claude Code 派 → 他ツール紹介は「触ってないけど調べた」体で書くこと (体験捏造禁止)
- 数字 (SWE-bench 80.8% / GitHub Star 3 万 / 月 $20 vs 無料) は使い回せるので投稿で活用
