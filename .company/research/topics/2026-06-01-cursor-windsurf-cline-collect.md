---
created: "2026-06-01"
topic: "Cursor / Windsurf / Cline / AI コーディングツール"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 8件
post_ideas: 6件
---

# AI コーディングツール最新情報 2026-06-01

## 収集テーマ
Cursor / Windsurf / Cline の最新動向・比較・数字

---

### Cursor 3.6 リリース（2026-05-29）
- ソース: https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/
- 公開日: 2026-05-29
- 要点:
  - Auto-review Run Mode が追加（AIがコードを自動レビューして走らせるモード）
  - Cursor 3.0（2026-04-02）からUIを根本設計し直し「AIがコードを書くことを前提」にした
  - ARR 20億ドル突破、Fortune 500の50%以上に在籍開発者が使用
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor 3.6が出た。ARR20億ドル。もう"AIで補助"じゃなく"AIが主"の時代に完全移行した」

---

### Cursor 3.0 の UI 刷新——エージェントUI革命（2026-04-02）
- ソース: https://gihyo.jp/article/2026/04/cursor-3
- 公開日: 2026-04-02
- 要点:
  - Agents Window：複数AIエージェントを並列管理（ローカル/Git worktree/クラウド/SSH）
  - Design Mode：ブラウザUI要素に直接アノテーションして指示できる
  - プラグインマーケットプレイス：MCP・スキル・サブエージェントが数百種類
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Cursorが変わった。エディタにAIを"追加した"時代が終わり、AIがコードを書く前提でUIを作り直した」

---

### Windsurf：SWE-1.5 は Claude Sonnet の 13 倍速い
- ソース: https://1van.net/windsurf/
- 公開日: 2026年（記事内データ）
- 要点:
  - 独自モデル SWE-1.5（Cerebras チップ使用）が 950 トークン/秒
  - Claude Sonnet 4.6 の約13倍のスピード
  - Arena Mode：同じタスクを複数AIに競わせて比較できる
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「WindsurfのAIはClaudeの13倍速い。でも"速さ"だけで選ぶ時代でもない」

---

### Windsurf 料金改定（2026-03）：クレジット制→クォータ制
- ソース: https://ai-tools-navi.jp/guide/windsurf-pricing
- 公開日: 2026-03
- 要点:
  - クレジット制（月500クレジット）を廃止、日次・週次の使用量上限に移行
  - Maxプラン新設：$200/月（旧プランより大幅値上げ）
  - 40以上のIDEに対応（JetBrains, Vim, Neovim, Emacs, Xcode）
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Windsurfが$200プラン出した。ガチ勢向けのAI IDEが一気に高価格帯に突入」

---

### Cline v3.81：OSSが有料を食う、月1000円以下の現実
- ソース: https://github.com/cline/cline
- 公開日: 2026年（最新バージョン情報）
- 要点:
  - GitHub Stars 61.2k・累計 500万インストール（完全無料 Apache 2.0）
  - 自動モデルルーティング（v3.2, 2026-03）：タスクに応じて最安モデルを自動選択
  - 月のAPI費用が$8〜12程度（Cursor $20/月や Copilot $10/月より安い場合も）
- 投稿アイデア:
  - 型: 朝学び型 / 即使える
  - 切り口: 「Clineって知ってる？月1000円以下でAIコーディング。OSSが有料を本気で脅かしてる」

---

### 2026年の「使い分け」最適解：バイブコーディング時代
- ソース: https://syncode.jp/articles/cursor-vs-windsurf-2026-comparison/
- 公開日: 2026年
- 要点:
  - 2026年は「バイブコーディング」が標準——AIに高レベル目標を与えて複数ファイル実装させる
  - 使い分け推奨：日常開発=Cursor、バックエンド新規実装=Windsurf、大規模タスク=Cline
  - チーム開発はCursor一択、個人予算を抑えるならCline/Windsurf
- 投稿アイデア:
  - 型: 教育目的 / 深夜思考
  - 切り口: 「2026年の正解。Cursor・Windsurf・Clineは"どれか1つ"じゃなくて使い分けが答えだった」

---

## 注目トピック（即投稿化推奨）
1. **Cline月1000円以下** — 数字が具体的で「えっ？」を取れる
2. **Cursor ARR20億ドル** — スケール感で「AIコーディング市場が本物」を示せる
3. **Windsurf 13倍速い** — 比較数字で即バズれる構造

## 使わなかった情報（ふーん止まり）
- Clineの具体的なタスクリスト・設定変更系UI改善（読者が今日使えない）
- WindsurfのSSO/RBAC（企業向けすぎてgaku_ai_lifeの読者に刺さらない）
