---
created: "2026-06-04"
topic: "Cursor / Windsurf / Cline / AI コーディング"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 5
post_ideas: 7
---

# Cursor / Windsurf / Cline 最新動向リサーチ（2026-06-04）

AIコーディングツール三強（Cursor / Windsurf / Cline）に Claude Code を加えた市場最新の動きを収集。
個人開発・AI副業の文脈で「今日から使えるネタ」に絞る。

---

### Cursor 3.6 で Auto-review モード追加（2026-05-29 リリース）
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-29
- 要点（3行以内）:
  - 3.6 で「Auto-review」実行モードが追加。承認プロンプトを減らしつつより安全に長時間タスクを走らせる方針。
  - 2026-05 に Jira 連携も追加されチケット駆動開発と統合。
  - 3.1 で導入された Canvas（インタラクティブReact UI出力）が定着、ダッシュボード生成が標準になった。
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor 3.6 の Auto-review、承認を省く=危険じゃないか試した結果」体験ベース1投稿に変換可能

### Cursor 3 系列は「AIが書く前提」のIDE再設計
- ソース: https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/
- 公開日: 2026-04-02（初出）
- 要点（3行以内）:
  - Cursor 3 は VS Code 派生から「AIエージェントがコードを書く前提」へUIを根本から再設計。
  - 補完中心の旧Cursorとは別物。エージェント中心になりプロンプト/承認のUXが主役に。
  - 「コードを書く時間」より「指示と承認の質」で成果が決まる構造に変わった。
- 投稿アイデア:
  - 型: 夜振り返り / 思考整理
  - 切り口: 「Cursor 3 を1週間使って気づいた、エンジニアの仕事の中身が変わったこと3つ」

### Windsurf $15 で Cursor $20 を下から削る価格戦略
- ソース: https://aurant-technologies.com/blog/comparison-how-to-choose-utilization-strategy-tools-2220/
- 公開日: 2026-05（推定）
- 要点（3行以内）:
  - Windsurf は $15/月。Cursor $20、Copilot $10 のあいだに刺してきた。
  - 売りは Cascade（プロジェクト全体把握＋マルチファイル一括編集）。リネーム系リファクタが圧倒的に速い。
  - 50万人開発者が利用。Cursor 一強だった市場が割れてきた。
- 投稿アイデア:
  - 型: 比較型 / 教育目的
  - 切り口: 「Cursor $20 と Windsurf $15、結局どっち得か。1日試して数字で出した」

### Cascade 機能：自然文1行でマルチファイルリファクタ
- ソース: https://zenn.dev/aimasaou/articles/14c724056f2cd5
- 公開日: 2026-04（推定）
- 要点（3行以内）:
  - Windsurf Cascade は「この変数名をプロジェクト全体で統一して」で全ファイル一括変更。
  - リアルタイムで開発者の操作を認識して提案を出す＝ペアプロに近い。
  - Cursor のチャットエージェントとは別物の「並走型」UX。
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Windsurf Cascade で 30 分かかるリファクタが 3 分になった話」

### Cline、VS Code マーケットで 500万インストール突破
- ソース: https://aipicks.jp/mag/cline-complete-guide-2026
- 公開日: 2026-04（推定）
- 要点（3行以内）:
  - Cline は VS Code 拡張で導入。500万 install 突破（2026-04 時点）。
  - Human-in-the-loop 設計：ファイル変更/コマンド実行は毎回ユーザー承認が必須。
  - 高精度には Claude Sonnet 4.5 or Gemini 3 Pro、コスパには DeepSeek V3 or Gemini 2.5 Flash が推奨構成。
- 投稿アイデア:
  - 型: 教育目的 / 失敗共有
  - 切り口: 「Cline で勝手にファイル消されないのは Human-in-the-loop のおかげ。Cursor の Auto-run との違いを実体験で」

### Cline CLI 2.0：ターミナルがAIコントロールプレーンに（2026-02）
- ソース: https://www.ai-souken.com/article/what-is-cline
- 公開日: 2026-02
- 要点（3行以内）:
  - Cline CLI 2.0 で CI/CD パイプラインから直接 Cline を叩けるようになった。
  - 「IDEで触る AI」から「シェルから叩く AI」へ用途拡大。
  - GitHub Actions の中で Cline がコードレビューや修正PR作成を担えるようになる。
- 投稿アイデア:
  - 型: 夜の深掘り / 教育目的
  - 切り口: 「Cline CLI を GitHub Actions に組んだら、PR が朝勝手にレビューされてた」

### Cursor vs Windsurf vs Claude Code 使い分け論
- ソース: https://dev.to/pockit_tools/cursor-vs-windsurf-vs-claude-code-in-2026-the-honest-comparison-after-using-all-three-3gof
- 公開日: 2026-05（推定）
- 要点（3行以内）:
  - Cursor＝既存ワークフローに AI を載せたい人向け（補完UX磨きが世界一）。
  - Windsurf＝AI と並走したい人向け（Cascade/Flows の往復が前提のUX）。
  - Claude Code＝IDEではない。ターミナル常駐エージェント。複雑なリポジトリで深く考えるのが得意。
- 投稿アイデア:
  - 型: 教育目的 / 比較型
  - 切り口: 「Cursor / Windsurf / Claude Code、3つ全部1年使った人の結論を3行で」

### AIコーディング副業：個人で月10〜50万のレンジ
- ソース: https://uravation.com/media/ai-side-job-beginners-guide-2026/
- 公開日: 2026-05
- 要点（3行以内）:
  - Cursor / Claude Code を使った Web 制作で月10〜50万のレンジが現実的（初心者帯でも）。
  - 初期費用は AI ツール代の月3,000〜6,000円のみ。参入障壁が崩れた。
  - 2026の勝ち筋は「AI × 専門領域」。汎用Web制作はコモディティ化が進む。
- 投稿アイデア:
  - 型: 集客 / 教育目的
  - 切り口: 「Cursor だけで月10万まで来る人と、来ない人の差は『専門領域を持っているか』だけ」

---

## 即投稿化推奨 TOP3

1. **「Cursor 3.6 Auto-review 体験」**（朝学び）— 1〜2週内のホット案件、まだ書いてる人少ない
2. **「Cursor / Windsurf / Cline / Claude Code 使い分け3行」**（教育）— 4ツール時代の整理需要が爆増中
3. **「AI × 専門領域でしか月10万抜けない」**（集客）— 自分の体験談（gaku_ai_life）と直結できる

## 投稿テンプレ流用メモ
- 弱さ枕詞：「正直 Cursor 3 系列にすぐ慣れなかった」「Cline は最初こわかった」が刺さりやすい
- 千円単位：$20 vs $15、月3,000円のツール代、月10万 → そのまま使える
- 2-4行 + 未完語尾：上記アイデアはどれも 4 行以内に圧縮できる温度感
