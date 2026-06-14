---
created: "2026-06-02"
topic: "Cursor / Windsurf / Cline 動向（AIコーディングエディタ）"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 11
post_ideas: 7
---

# Cursor / Windsurf / Cline — 2026年5〜6月の動向まとめ

## 全体像（30秒で読める要約）

- **Cursor 3.x** が4〜5月で大型連発：マルチエージェント並列実行・Canvas・クラウド開発環境・Auto-review。
- **Windsurf** は Cognition（Devin の会社）に **$250M で買収**（2025/12）→ SWE-1.5（Sonnet 4.5 比 13倍速）と Workflows / Codemaps を投入。
- **Cline** は VSCode 拡張で完全無料、30+ LLM 切替可、世界500万人。Plan/Act 分離が「2026年の標準パラダイム」と評される。
- **使い分けの定番化**：日常は Cursor or Windsurf、重い大規模タスクで Cline を呼ぶ、というハイブリッドが定着しつつある。
- **Cursor 料金問題**：2025年6月のリクエスト→トークン課金変更で炎上→2026年4月に年払い20%OFFで再整理（Pro $20 / Pro+ $60 / Ultra $200）。

---

## 個別トピック

### Cursor 3.6（2026-05-29リリース） Auto-review
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-29
- 要点:
  - 承認プロンプトが少なく、安全に長時間エージェントを走らせ続けられる新実行モード
  - 「Cursor で長く作業し続ける」ことを目的とした設計
  - 寝ている間にエージェントを走らせるユースケースに直結
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「寝てる間にエージェントが PR まで作る時代になった。Cursor 3.6 Auto-review が変えたこと」

### Cursor 3.4（2026-05-13リリース） クラウド開発環境
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-13
- 要点:
  - クローン済みリポ・依存インストール済み・内部ツールチェーン認証込みの環境をエージェントに渡せる
  - 「最初から最後まで」タスクをやり切るための土台
- 投稿アイデア:
  - 型: 夕失敗型
  - 切り口: 「ローカルで詰まるのはもう古い。Cursor 3.4 のクラウド環境に投げたら、自分の Mac より速かった話」

### Cursor 3.1（2026-04-16リリース） Canvas
- ソース: https://cursor.com/ja/changelog/3-0
- 公開日: 2026-04-16
- 要点:
  - エージェントが React UI を直接生成、Agents Window 内に永続アーティファクト化
  - ダッシュボード・チャート・テーブル・diff 表示を Cursor 内で完結
- 投稿アイデア:
  - 型: 昼進捗型
  - 切り口: 「Cursor の Canvas、もう v0 いらないかも。ダッシュボードまで Cursor 内で完結した」

### Windsurf SWE-1.5 / SWE-1.6
- ソース: https://vibecoding.app/blog/windsurf-review
- 公開日: 2026-05
- 要点:
  - 独自モデル SWE-1.5 が Sonnet 4.5 比 **13倍速** を主張
  - Cognition AI が 2025/12 に Windsurf を約 **$250M で買収**
  - MCP 対応で外部ツール・DB・APIに接続可能
- 投稿アイデア:
  - 型: 深夜思考型
  - 切り口: 「13倍速のモデルに乗り換えなかった理由。速度より、僕は『説明できる遅さ』を選んだ」

### Windsurf Workflows（再利用エージェントレシピ）
- ソース: https://www.digitalapplied.com/blog/windsurf-2-deep-dive-cascade-agents-flows-2026
- 公開日: 2026-05
- 要点:
  - Markdown プロンプト + ツール + スコープを束ねた「Workflow」を `/workflow-name` で呼べる
  - Cascade のエージェント実行を「定型化」できる
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「毎回同じプロンプト書いてる人へ。Windsurf の Workflows、これ Claude Code の slash command と同じ思想」

### Cline CLI 2.0（2026年2月リリース）
- ソース: https://aipicks.jp/mag/cline-complete-guide-2026
- 公開日: 2026-04
- 要点:
  - ターミナルを AI 開発のコントロールプレーン化する大規模アップデート
  - VSCode 外でも Cline のエージェント機能を呼び出せる
  - Plan/Act モード分離が 2026年標準パラダイムへ
- 投稿アイデア:
  - 型: 夕失敗型 / 教育
  - 切り口: 「Cline は無料。ただし API 課金で先月 ¥18,000 飛んだ。Plan/Act を分けないと地獄」

### Cursor 料金改定（2025/06 → 2026/04）
- ソース: https://blog.lai.so/cursor-pricing/
- ソース: https://www.masatoman.net/articles/cursor-pricing-plans-guide-2026
- 公開日: 2026-04
- 要点:
  - 2025/06：リクエスト数課金 → トークン課金に変更、不明瞭な説明で炎上・返金対応
  - 2026/04：年払い20%OFF適用（Pro $16、Pro+ $48、Ultra $160）
  - 月払いは Pro $20 / Pro+ $60 / Ultra $200
  - 個人プランの「Composer 2 Auto モード」が実質無制限で最強コスパ枠
- 投稿アイデア:
  - 型: 教育 / 比較
  - 切り口: 「Cursor、Pro $20 / Pro+ $60 / Ultra $200。副業エンジニアの分岐点は『毎日エージェント回すか』だけ」

---

## 投稿の型に当てはめると

| 型 | テーマ | 想定タイトル |
|---|---|---|
| 朝学び | Cursor 3.6 Auto-review | 「Cursor が『一晩中ひとりで作業』を始めた朝、自分の役割を考え直した」 |
| 朝学び | Windsurf Workflows | 「同じプロンプトを毎回打ってる人、Workflows 1個書くだけで時間が戻ってくる」 |
| 昼進捗 | Cursor Canvas | 「ダッシュボードまで Cursor 内で完結。v0 とのスイッチが減った」 |
| 夕失敗 | Cline 課金事故 | 「Cline 無料につられて API ¥18,000 飛ばした失敗から学んだ Plan/Act 分離」 |
| 夜振り返り | エディタ使い分け | 「結論：日常 Cursor、重いタスクで Cline。2026年のエディタ戦争はこれで終戦」 |
| 深夜思考 | Windsurf SWE-1.5 | 「13倍速いモデルに乗り換えなかった理由。AI の速度より、自分の理解速度に揃える」 |
| 教育 | Cursor 料金 | 「副業エンジニア向け Cursor プラン早見表：$20 / $60 / $200 の分岐点」 |

---

## 注目（即投稿化推奨）

**「Cursor 3.6 Auto-review = 寝てる間に PR ができる」** — 新しさ・具体性・実用性が揃ってる。アカウントの「個人開発の実況」軸とも噛み合う。深夜思考枠か朝学び枠で 1 本即出せる。
