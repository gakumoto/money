---
created: "2026-06-03"
topic: "Cursor / Windsurf / Cline 最新動向（2026-06 アップデート）"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline", "cline-sdk", "swe-1-6"]
sources: 9件
post_ideas: 7件
related: ["2026-06-01-cursor-windsurf-cline-collect.md"]
---

# AI コーディングツール最新情報 2026-06-03

## 収集テーマ
Cursor / Windsurf / Cline の **2026年5月後半〜6月** の新規アップデート。
2026-06-01 の収集ファイル以降に判明した新情報のみを記録する。

---

### 【最重要・新規】Cline SDK 公開（2026-05-14）— OSSが Claude Code を抜いた
- ソース: https://www.marktechpost.com/2026/05/14/cline-releases-cline-sdk-an-open-source-agent-runtime-now-powering-its-cli-and-kanban-with-ide-extensions-being-migrated/
- 関連: https://cline.ghost.io/introducing-cline-sdk-the-upgraded-agent-runtime/
- 公開日: 2026-05-14
- 要点:
  - Cline がエージェントランタイムを `@cline/sdk` として抽出・OSS 公開（Apache 2.0）
  - **Cline CLI（Claude Opus 4.7）が Terminal Bench 2.0 で 74.2% を記録。同モデルの Claude Code は 69.4%**
  - Opus 4.6 では Cline 71.9% vs Claude Code 65.4%、Kimi K2.6 では Cline 55.1% vs OpenCode 37.1%
  - 8M+ developer に利用される規模に到達、`npm install @cline/sdk` で誰でも使える
  - VS Code / JetBrains / Cursor / Windsurf / Zed / Neovim / CLI 全部で動く
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「OSSの Cline が Claude Code をベンチで抜いた。74.2% vs 69.4%。"無料が有料を超える"はAI開発でも起き始めた」
  - キャラ補強: 「ぼくは Cursor 課金組だけど、Cline 触らないと損する空気になってきた」

---

### 【新規】Cursor 3.5 リリース — Shared Canvases と /loop Skill（2026-05-20）
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-20
- 要点:
  - **Shared Canvases**: レポート・ダッシュボードなどインタラクティブなアーティファクトをリンク共有
  - **/loop Skill**: ローカルで定期的にプロンプトを実行する仕組み（cron的）
  - チームでAI成果物を共有する流れが本格化
- 投稿アイデア:
  - 型: 教育目的 / 即使える
  - 切り口: 「Cursor 3.5 の /loop Skill が地味に効く。"毎朝7時にコード生成して PR 作る"が標準化する流れ」

---

### 【新規】Cursor Composer 2.5 — 長時間タスク特化（2026-05-18）
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-18
- 要点:
  - 長時間走らせるタスク向けに最適化された新モデル
  - 複雑な指示に対する追従性が改善（公式文言: "follows complex instructions more reliably"）
  - 初週は使用量2倍キャンペーンあり
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Cursor の Composer 2.5、3時間放置しても文脈飛ばない。"AI に丸投げ"の精度がまた1段上がった」

---

### 【再掲・追加情報】Cursor 3.6 — Auto-review Run Mode（2026-05-29）
- ソース: https://cursor.com/changelog
- 公開日: 2026-05-29
- 要点:
  - **Auto-review**: 承認プロンプトを減らしながら安全に長時間走らせる新モード
  - Shell / MCP / Fetch ツール呼び出しに適用
  - 許可リスト＝即実行、サンドボックス可能なものはサンドボックス内で実行
- 投稿アイデア（2026-06-01分から再利用可）:
  - 型: 教育目的
  - 切り口: 「Cursor 3.6 の Auto-review。"許可"連打が消える日が来た」

---

### 【新規】Windsurf SWE-1.5 公式情報（2025-10-29 リリース・改めて整理）
- ソース: https://devin.ai/blog/swe-1-5
- 公開日: 2025-10-29
- 要点:
  - 数千億パラメータのフロンティアサイズモデル、950 トークン/秒
  - **Haiku 4.5 の 6倍速、Sonnet 4.5 の 13倍速**
  - SWE-Bench Pro で近 SOTA 水準
  - 従来 20秒以上かかったタスクが 5秒未満で完了
  - Cerebras チップで推論
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Windsurf の SWE-1.5、20秒のタスクが5秒に。"考える"より"試す"が安くなった時代」

---

### 【新規】Windsurf SWE-1.6 + Cascade/Flow/Memory の3層構造
- ソース: https://uravation.com/media/windsurf-practical-guide-swe16-cascade-flow-2026/
- 公開日: 2026年
- 要点:
  - SWE-1.6 は精度改善版（Claude Opus 4.6 の80.8% には及ばないが、"速く試す"用途に最適化）
  - **Cascade**: コードベース全体を理解する計画・多ファイル編集エージェント
  - **Flow**: エディタ内のリアルタイム補完
  - **Memory**: プロジェクトルールを永続保存して次セッションに引き継ぐ知識層
  - Windsurf最大の差別化は Memory による「文脈の継続性」
- 投稿アイデア:
  - 型: 教育目的 / 深夜思考
  - 切り口: 「Windsurf の Memory 機能、毎回ゼロから説明し直す手間が消える。AI に"うちのルール"を覚えさせられる時代」

---

### 【新規】Cline は VS Code 以外（JetBrains/Cursor/Windsurf/Zed/Neovim）でも動く
- ソース: https://github.com/cline/cline
- 公開日: 2026年（最新リリース v3.82.0、v3.78.0 が 2026-04-10）
- 要点:
  - サイドバー型で多くのIDEに同居できる（Cursor の中で Cline を動かす構成も可能）
  - 30以上のプロバイダ対応（Anthropic / OpenAI / Gemini / Bedrock / Azure / OpenRouter…）
  - 直近の v3.78.0 で Spend Limit Reached の専用エラーUI、read-file 行範囲レポートのバグ修正
- 投稿アイデア:
  - 型: 朝学び型 / 即使える
  - 切り口: 「Cline は Cursor の中でも動く。"どっち選ぶか"じゃなく"両方使う"が正解だった」

---

## 注目トピック（即投稿化推奨）

1. **【最強】Cline CLI が Claude Code を上回る数字（74.2% vs 69.4%）** — OSSが本家を抜いた構図、「えっ？」を取れる固有数字
2. **Windsurf 20秒→5秒** — 速度の桁が変わる体感の話、深夜思考にも昼進捗にも刺さる
3. **Cline は Cursor の中でも動く** — 「使い分け」より「重ねがけ」という新発想

## 注意（gaku_ai_life で書くときの調整）

- ベンチ数字を語るときは「実体験じゃない」と明示する（嘘ついた扱いを避ける）
- 「Claude Code 派 vs Cline 派」みたいな対立構造は煽りすぎNG。「両方触ってみた所感」のスタンスで
- 「月いくら浮く」系は **危険ワード（収益化・稼ぐ・節約）連発NG** に該当しないか毎回チェック
- 数字は「ベンチ74.2%」より「2.4ポイント差」のほうが具体感が出る場合あり

## 使わなかった情報（ふーん止まり）

- Cline SDK の 4層アーキテクチャ詳細（読者の頭に入らない）
- Windsurf の Cascade UI の細かい操作（スクショなしでは伝わらない）
- Cursor の changelog の細かいバグ修正
