---
created: "2026-06-15"
topic: "Cursor / Windsurf / Cline 最新動向"
status: completed
tags: ["weekly-collect", "cursor", "windsurf", "cline", "ai-coding"]
sources: 9
post_ideas: 9
---

# Cursor / Windsurf / Cline 最新動向 (2026-06-15 収集)

過去 6 週間 (4/24〜6/11) の AI コーディングエディタ 3 強の主要アップデートを公式 changelog + 比較記事から抽出。投稿で「具体的な機能名・日付・数字」を出せるネタを優先。

最大の衝撃は **Windsurf が Devin Desktop にリブランド (2026-06-02)**。次に Cursor Bugbot の高速化、Cline の月コスト $8〜12 化が続く。

---

### Windsurf → Devin Desktop へリブランド
- ソース: https://releasebot.io/updates/windsurf
- 公開日: 2026-06-02
- 要点（3行以内）:
  - Windsurf という製品名が消えて「Devin Desktop」に統一された
  - 4/28 リリースの Devin for Terminal、5/6 の Devin Review、6/10 の Devin Local v2026.5.26-8 と、Cognition 買収後ずっと Devin 寄りに寄せていた延長
  - 既存ユーザーは Windows ショートカットの移行や `.devinignore` 対応など実務的な作業が増えた
- 投稿アイデア:
  - 型: 夜思考型 / 教育目的
  - 切り口:「Windsurf が静かに消えて『Devin Desktop』になった。Cognition 買収から半年で完全に Devin ブランドに飲まれた。AI コーディングエディタの淘汰、もう始まってる」

### Cursor Bugbot が 3 倍速・22% 安く
- ソース: https://releasebot.io/updates/cursor
- 公開日: 2026-06-10
- 要点（3行以内）:
  - レビュー時間が ~5分 → ~90秒（約 3 倍速）、コストは 22% ダウン
  - バグ検出精度も 0.56 → 0.62 (10% 改善)
  - `/review` コマンドで「push 前レビュー」「前回レビュー以降の差分だけレビュー」が選べる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口:「Cursor の Bugbot、6/10 のアプデで 5分→90秒に短縮。コストも 22%下がって精度も 10%上がった。PR 投げる前に `/review` 叩く運用が現実的になってきた」

### Cursor の Auto-review、エンタープライズの中断率 40%→7%
- ソース: https://releasebot.io/updates/cursor
- 公開日: 2026-06-11
- 要点（3行以内）:
  - エージェント実行をコンテキスト分類器で判定。アクション全体の約 4% だけブロック
  - 結果としてユーザー中断率は約 7%（以前のエンタープライズ顧客で 40% だったところ）
  - 「自動承認はしたいけど暴走が怖い」というエージェント運用の最大の摩擦が、6 倍近く下がった
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口:「Cursor の Auto-review、エンタープライズで 40% あった『エージェント中断率』が 7% まで下がった。AI に任せ切れない最大の理由は『止まる』ことだった。これが解消されつつある」

### Cursor Teams 値上げ (7/1〜) と Premium 席の新設
- ソース: https://releasebot.io/updates/cursor
- 公開日: 2026-06-01
- 要点（3行以内）:
  - Standard 席: $32/月 (年払い) / $40/月 (月払い)
  - 新設の Premium 席: $96/月 (年払い) / $120/月 (月払い)、Standard の 5 倍枠
  - 新規顧客は即時、更新顧客は 2026-07-01 以降の請求サイクルから適用
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口:「Cursor Teams、7 月から Standard $32・Premium $96 に値上げ。エージェント運用ガチ勢に Premium 席を作って来た。チーム導入してる人、6 月中に席数見直さないと請求が跳ねる」

### Cline v3.2 の自動モデルルーティングで月コスト $8〜12 に
- ソース: https://www.deployhq.com/guides/cline
- 公開日: 2026-03 リリース (2026-06 時点で v3.81)
- 要点（3行以内）:
  - 自動モデルルーティングが、タスク毎に「捌ける最安モデル」を選ぶ
  - 中程度の使用で月 API 課金 $8〜12（≒ 1,200〜1,800 円）に収まる
  - Cursor の $20/月 や Copilot の $10/月 と違って月額固定ではなく、API 直叩きの実費
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口:「Cline、月コストが $8〜12 まで下がってる。自動モデルルーティングが『このタスクなら Haiku で十分』を勝手に選ぶ。Cursor 解約して Cline に逃げる人が増える理由これ」

### Windsurf の Devin Local エージェントが Cascade より 30% トークン効率
- ソース: https://releasebot.io/updates/windsurf
- 公開日: 2026-04-28
- 要点（3行以内）:
  - 既存の Cascade エージェントよりトークン使用が 30% 少ない
  - ローカル CLI として動き、コードベース・ツール・環境にフルアクセス、クラウドへの引き継ぎも可能
  - フロークレジット (1,500/月) を浪費していた問題への実質的な答え
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口:「Windsurf の新 Devin Local、Cascade よりトークン 30% 効率。フロークレジット 1,500 で足りない問題、ここでようやく実害が減る」

### Cursor の `/loop` スキル（プロンプトを目標達成まで繰り返す）
- ソース: https://releasebot.io/updates/cursor
- 公開日: 2026-05-20 (v3.5)
- 要点（3行以内）:
  - プロンプトを「目標達成まで」または「明示的に止めるまで」反復実行できる
  - 同タイミングで Marketplace テンプレ 5 種、複数リポ・無リポでの Automations 対応も追加
  - Claude Code 側の `/loop` と思想が完全に被ってきている（自走 AI の時代）
- 投稿アイデア:
  - 型: 夜思考型 / 教育目的
  - 切り口:「Cursor も v3.5 で `/loop` 入れた。プロンプトを目標達成まで自動で繰り返す。Claude Code と全く同じ方向、もうコーディング AI は『一発回答』じゃなく『自走』が前提になった」

### 複雑タスクは Claude Code 有利・簡単タスクは Cursor 有利の逆転構造
- ソース: https://techcreate.balubo.jp/articles/claude-code-vs-cursor-comparison-2026
- 公開日: 2026-06 (記事)
- 要点（3行以内）:
  - 複雑タスクで $1 あたり精度: Claude Code 8.5pt / Cursor 6.2pt
  - 簡単タスク（Tab 補完など）: Cursor 42pt / Claude Code 31pt
  - Claude Code は Cursor の約 5.5 倍のトークン効率（同等タスクで比較）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口:「Claude Code と Cursor、コスパが完全に逆転してる。複雑な実装は Claude Code、Tab 補完だけなら Cursor。両方契約して『重い時は CC、軽い時は Cursor』が結論」

### Cline、Cursor / Windsurf / JetBrains / Zed / Neovim にも対応へ
- ソース: https://www.deployhq.com/guides/cline
- 公開日: 2026 (現行 v3.81)
- 要点（3行以内）:
  - 元は VS Code 拡張だった Cline が、Cursor / Windsurf / JetBrains / Zed / Neovim、macOS/Linux 用プレビュー CLI まで対応を拡張
  - 5M+ インストール、GitHub 61.2k スター、Apache 2.0 ライセンス
  - 「IDE 縛りなしの自走エージェント」が完成しつつある
- 投稿アイデア:
  - 型: 夜思考型 / 教育目的
  - 切り口:「Cline、もう VS Code 拡張じゃなくなってきた。Cursor / Windsurf / JetBrains / Zed / Neovim 全部で動く。エディタ選びがエージェント選びから切り離されつつある」

---

## 注目トピック（即投稿化推奨）

1. **Windsurf → Devin Desktop リブランド (6/2)** — 既知の人少ない。先に出すと「早い」と評価される
2. **Cursor Teams 7/1 値上げ** — 期限ありネタは反応取りやすい (Premium 新設 $96)
3. **Cline 月 $8〜12** — Cursor 課金キツい層に刺さる副業向けネタ
