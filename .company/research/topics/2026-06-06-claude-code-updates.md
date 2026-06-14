---
created: "2026-06-06"
topic: "Claude Code 最新アップデート"
status: completed
tags: ["weekly-collect", "claude-code", "anthropic", "ai-dev"]
sources: 6
post_ideas: 6
---

# Claude Code 最新アップデート (2026-06-06 収集)

## サマリ
- **2026-06-15 から Claude 有料プランの利用枠が「対話」と「自動化」に分離される**。Agent SDK / `claude -p` / GitHub Actions は新設の「Agent SDK 月額クレジット」から消費。これが最大の話題。
- v2.1.157 (5/29) → v2.1.165 (6/05) まで 9 リリースが連続投入された。テーマは「Skills の自動ロード」「セキュリティ強化（startup file 書き込み防止）」「Hooks の additionalContext 対応」。
- Auto mode が Bedrock / Vertex / Foundry でも使えるようになった（`CLAUDE_CODE_ENABLE_AUTO_MODE=1`）。企業勢の選択肢が広がる。
- 個人開発者ネタとしては「`.claude/skills/` 自動ロード → `claude plugin init` で雛形」と「`/plugin list` で導入済み確認」が小ネタとして使いやすい。
- 2 日前 (6/04) の収集と被らないように、今回は **プラン分離 / 6 月前半の細かい新機能 / Hooks 強化** に絞った。

---

## 収集ネタ

### 1. 2026-06-15「対話」と「自動化」のクレジット完全分離
- ソース: [Claude有料プラン激変！2026年6月15日〜「対話」と「自動化」が完全分離 | あなたのAI顧問](https://ai-advisors.jp/media/ai-news/claude-plan-change-20260615/)
- 公開日: 2026 年 6 月（直近）
- 要点（3 行以内）:
  - 「対話」(Claude.ai / Claude Code 対話 / Cowork) は従来のサブスク枠のまま。「自動化」(Agent SDK / `claude -p` / GitHub Actions) は新設の **Agent SDK 月額クレジット** へ移行
  - 付与額は Pro=$20、Max 5x=$100、Max 20x=$200。**個人単位・毎月リセット・繰り越しなし・初回手動有効化必要**
  - クレジット優先で消費し、超過後は設定に応じて課金 or 停止。自動化を回している人は 6/15 までに上限と消費先を把握しないと止まる
- 投稿アイデア:
  - 型: 朝学び型 / 教育 + 警告
  - 切り口: 「6 月 15 日から Claude の枠が 2 つに割れる。`claude -p` で夜中バッチを回してる人は、Pro $20 / Max 5x $100 / Max 20x $200 の Agent SDK クレジットを今から把握しておく」

### 2. v2.1.163 (6/04) — `/plugin list` と Hooks の additionalContext
- ソース: [Claude Code changelog | Claude Code Docs](https://code.claude.com/docs/en/changelog)
- 公開日: 2026-06-04
- 要点（3 行以内）:
  - `/plugin list` コマンドが追加。`--enabled` / `--disabled` フィルタで導入済みプラグインを一覧できる
  - Hooks の `Stop` / `SubagentStop` が `hookSpecificOutput.additionalContext` を返せるように。エラーにせず Claude に追加情報を渡してターンを継続できる
  - `requiredMinimumVersion` / `requiredMaximumVersion` 管理設定が追加。古い CLI で動かしちゃう事故を組織側で塞げる
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「`/plugin list --enabled` で今入ってるスキルを一覧。自分の Claude Code がどれだけブクブク太ってるか分かる」

### 3. v2.1.160 (6/02) — shell startup ファイルと build-tool 設定の書き込み前に確認プロンプト
- ソース: [Claude Code Updates by Anthropic | Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- 公開日: 2026-06-02
- 要点（3 行以内）:
  - `.zshenv` / `.zlogin` / `.bash_login` / `~/.config/git/` への書き込みは確認プロンプトを挟む
  - `acceptEdits` モードでも、build-tool 設定（コード実行を許す系）への書き込みは止まって確認する
  - ノーチェックで `acceptEdits` を有効にしていた人は、ここで一拍止まるようになった。「気付かず lifecycle hook 仕込まれる」リスクを下げる動き
- 投稿アイデア:
  - 型: 夕失敗 → 改善 / 信頼構築
  - 切り口: 「Claude Code が勝手に `.zshenv` 触らなくなった話。`acceptEdits` を脳死で有効にしてる人ほど、この変更を知っておいた方がいい」

### 4. v2.1.158 (5/30) — Auto mode が Bedrock / Vertex / Foundry で解禁
- ソース: [Claude Code changelog | Claude Code Docs](https://code.claude.com/docs/en/changelog)
- 公開日: 2026-05-30
- 要点（3 行以内）:
  - `CLAUDE_CODE_ENABLE_AUTO_MODE=1` で Bedrock / Vertex / Foundry でも Opus 4.7 / 4.8 の Auto mode が使える
  - これまで「会社が AWS / GCP / Azure 経由でしか Claude 使えない」勢は Auto mode を諦めていた。その壁が消えた
  - 個人勢の直接契約と企業勢のクラウド経由で、機能差がほぼなくなる方向に揃っている
- 投稿アイデア:
  - 型: 昼進捗 / 教育目的
  - 切り口: 「Auto mode、ついに Bedrock 経由でも動く。社内 Claude しか触れない人にはここから差がつき始める」

### 5. v2.1.162 (6/03) — `claude agents --json` の waitingFor と Grep/Glob ネイティブツール
- ソース: [Claude Code changelog | Claude Code Docs](https://code.claude.com/docs/en/changelog)
- 公開日: 2026-06-03
- 要点（3 行以内）:
  - `claude agents --json` の出力に `waitingFor` フィールドが入った。詰まってるセッションが「何で詰まってるのか」を機械可読で取れる
  - `--tools` に Grep / Glob を明示するとネイティブ実装の専用ツールが使われる（=軽くて速い）
  - 複数エージェント運用が増えるほど、`agents --json | jq` で監視する流れが現実的になる
- 投稿アイデア:
  - 型: 夜思考 / 教育目的
  - 切り口: 「3 人の AI 部下が止まってる、を朝に検知する。`claude agents --json` の waitingFor を Discord に投げるだけ」

### 6. v2.1.157 (5/29) — `.claude/skills` 自動ロード & `claude plugin init`
- ソース: [Claude Code changelog | Claude Code Docs](https://code.claude.com/docs/en/changelog)
- 公開日: 2026-05-29
- 要点（3 行以内）:
  - `.claude/skills/` 配下のプラグインは marketplace 不要で自動ロードされる
  - `claude plugin init <name>` で新規プラグインの雛形を生成
  - 「自分の作業を再現するだけのスキル」を作る心理的ハードルが消えた。秘書スキルや日報スキルがここから量産可能
- 投稿アイデア:
  - 型: 朝学び / 教育 + 集客
  - 切り口: 「`claude plugin init secretary` だけで自分専用の秘書スキルの土台が出来る。あとは SKILL.md に手順を貼るだけ」

---

## 即投稿化の最有力候補

**「6/15 プラン分離」** が今回ぶっちぎりで強い。
- 日付が確定している（6/15）→ 緊急性が出せる
- 数字が具体的（$20 / $100 / $200、Pro / Max 5x / Max 20x）→ 断定で書ける
- 「`claude -p` で夜間バッチ回してる人」「GitHub Actions で動かしてる人」は確実に巻ける
- 知らずに止まるリスクがあるので、教えること自体に価値が出る

次点は **「`.zshenv` への書き込み前プロンプト」**（v2.1.160）。信頼構築型の「Claude Code が安全側に倒れた話」として書ける。

---

## 参考リンク
- [Claude Code changelog (公式・英語)](https://code.claude.com/docs/en/changelog)
- [新機能 - Claude Code Docs (公式・日本語)](https://code.claude.com/docs/ja/whats-new)
- [Claude Code Updates by Anthropic | Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- [Claude有料プラン激変！2026年6月15日〜 | あなたのAI顧問](https://ai-advisors.jp/media/ai-news/claude-plan-change-20260615/)
- [Claude Updates by Anthropic - June 2026 | Releasebot](https://releasebot.io/updates/anthropic/claude)
- [Anthropic Release Notes - June 2026 Latest Updates | Releasebot](https://releasebot.io/updates/anthropic)
