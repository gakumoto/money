---
created: "2026-06-15"
topic: "Claude Code 最新アップデート"
status: completed
tags: ["weekly-collect", "claude-code", "anthropic"]
sources: 6
post_ideas: 8
---

# Claude Code 最新アップデート (2026-06-15 収集)

過去 2 週間 (5/28〜6/12) の Claude Code 関連の主要アップデートを WebSearch + 公式 changelog から抽出。投稿で「具体的な機能名・コマンド・数字」を出せるネタを優先。

---

### Nested Sub-Agents (深さ5まで)
- ソース: https://code.claude.com/docs/en/changelog
- ソース2: https://ofox.ai/blog/claude-code-nested-subagents-2026/
- 公開日: 2026-06-10 (v2.1.172)
- 要点（3行以内）:
  - サブエージェントがさらにサブエージェントを呼べるようになった (最大5階層)
  - 動機は「コンテキスト管理」: 各 subagent が新しい context window を持つので、親が詰まる前に子に逃がせる
  - これまで Plan→Explore の2階層が限界だった大型タスクが、深い分解で走れる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口:「Claude Code が 5 階層のネストエージェント対応した。何が嬉しいかを 1 行で言うと『親 AI のコンテキスト窓を子 AI に逃がせる』。これでドキュメント横断系の重いタスクが走る」

### `--safe-mode` フラグ (全カスタマイズを切って起動)
- ソース: https://code.claude.com/docs/en/changelog
- ソース2: https://jangwook.net/en/blog/en/claude-code-june-2026-new-features-changelog-developer-guide/
- 公開日: 2026-06-08 (v2.1.169)
- 要点（3行以内）:
  - CLAUDE.md / plugins / skills / hooks / MCP / custom commands / agents / output styles 全部無効化して素の Claude Code を起動できる
  - 認証とモデル選択は通常通り動く
  - 「設定盛りすぎて挙動おかしい」時の切り分けに即使える
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口:「Claude Code の挙動おかしいって時、`--safe-mode` で起動すると CLAUDE.md・skills・hooks・MCP 全部切れる。設定盛ってる人ほど切り分け作業が一瞬で終わる」

### `/cd` コマンド (プロンプトキャッシュを壊さずディレクトリ移動)
- ソース: https://code.claude.com/docs/en/changelog
- 公開日: 2026-06-08 (v2.1.169)
- 要点（3行以内）:
  - セッションの作業ディレクトリを `/cd` で変更できる
  - プロンプトキャッシュを壊さない=モノレポ内で別パッケージに移動しても課金的に得
  - 従来は一度終了してまた起動だったので、コンテキスト引き継ぎたい時に便利
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口:「モノレポで Claude Code 使ってる人、`/cd` で作業ディレクトリ動かせる様になった。プロンプトキャッシュ壊さないからフロント→バックの移動が無課金で済む」

### `/usage` カテゴリ別ブレイクダウン (VS Code)
- ソース: https://code.claude.com/docs/en/changelog
- 公開日: 2026-06-12 (v2.1.174)
- 要点（3行以内）:
  - `/usage` で「cache miss / long context / subagents / skill別 / agent別 / plugin別 / MCP別」のトークン消費が見える化
  - どの skill / plugin / MCP がコスト食ってるか初めて可視化された
  - 結論「重い MCP は外そう」「subagent 増やすと爆発する」が数字で言える
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口:「Claude Code の `/usage` がカテゴリ別になった。どの skill / MCP がトークン食ってるか初めて数字で出る。重い MCP 抱えてる人は今日見ろ」

### Plugin マーケットプレイス検索バー
- ソース: https://code.claude.com/docs/en/changelog
- 公開日: 2026-06-10 (v2.1.172)
- 要点（3行以内）:
  - `/plugin` 画面に検索バーが追加。マーケットプレイスから plugin を絞り込める
  - これまで一覧スクロールで探していたのが解消
  - skill だけでなく plugin エコシステムが膨らんできた証拠
- 投稿アイデア:
  - 型: 朝学び型 / 集客目的
  - 切り口:「Claude Code の `/plugin` に検索バーきた。マーケットプレイスから絞り込めるようになって、初めて plugin エコシステムの存在感が出てきた」

### Opus 4.8 リリース (2026-05-28)
- ソース: https://simonwillison.net/2026/May/28/claude-opus-4-8/
- ソース2: https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8
- 公開日: 2026-05-28
- 要点（3行以内）:
  - Opus 4.7 比でコーディング・エージェント能力・推論が改善
  - 自分が書いたコードのバグを見逃す確率が前世代の約 1/4
  - Pro 以上で利用可能。6月初旬から Claude Code のデフォルトモデルに昇格
- 投稿アイデア:
  - 型: 朝学び型 / 信頼構築
  - 切り口:「Opus 4.8 が Claude Code のデフォルトになった。Anthropic 公式の数字で『自分のコードのバグを見逃す率が 4.7 の 1/4』。レビューが楽になる体感ある」

### Safe Mode + Opus 4.8 + `/cd` の同時着地
- ソース: https://jangwook.net/en/blog/en/claude-code-june-2026-new-features-changelog-developer-guide/
- 公開日: 2026-06-08 前後
- 要点（3行以内）:
  - 6月初旬に Safe Mode / `/cd` / Opus 4.8 デフォルト化 / `/usage` カテゴリ別がほぼ同時に来た
  - 「設定爆発→切り分け困難」になっていたヘビーユーザーへの救済パック
  - 開発者向け運用ツールとしての成熟が進んでいるフェーズ
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口:「Claude Code の 6 月初旬アップデート、地味だけど『重課金ヘビーユーザー救済パック』だと思う。Safe Mode で切り分け、/usage でコスト可視化、/cd でキャッシュ温存、Opus 4.8 でバグ見逃し減。設定盛ってきた人ほど効く」

### レート制限 2 倍化 (5/6 確定済)
- ソース: https://www.morphllm.com/claude-code-usage-limits
- ソース2: https://claudefa.st/blog/guide/development/higher-usage-limits
- 公開日: 2026-05-06
- 要点（3行以内）:
  - Pro / Max / Team / 座席型 Enterprise の 5 時間レート制限が 2 倍化
  - Pro / Max はピーク時間帯のスロットリングも撤廃
  - これで「夕方〜夜に制限引っかかって止まる」問題が大きく改善
- 投稿アイデア:
  - 型: 朝学び型 / 信頼構築
  - 切り口:「Claude Code の 5 時間レート制限、5/6 から 2 倍になってる。Pro / Max はピーク時間の絞りもなくなった。『夜やってると止まる』理由でやめてた人、戻ってきていい」

---

## 注目順 (即投稿化推奨 Top3)

1. **`/usage` カテゴリ別ブレイクダウン** — 数字を出せる、即実用、競合スキル系アカウントがまだ拾ってない
2. **Nested Sub-Agents (深さ5)** — 「コンテキスト窓を子AIに逃がせる」というメタ理解で 1 個刺さる
3. **`--safe-mode`** — 設定盛ってる人ほど刺さる、明日朝の投稿向け

## メモ
- v2.1.176 (6/12) が現時点 (6/15) 最新の公式リリース。今週中に v2.1.177 以降が出る可能性高い
- Claude Fable 5 という新シリーズ名 (Mythos クラス) も 6/9 に出ているが、まだ実機体感が薄いので投稿化はもう少し待つ
- Anthropic 公式 changelog: https://code.claude.com/docs/en/changelog
