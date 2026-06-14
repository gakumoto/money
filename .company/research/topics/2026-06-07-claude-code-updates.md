---
created: "2026-06-07"
topic: "Claude Code 最新アップデート"
status: completed
tags: ["weekly-collect", "claude-code", "anthropic", "ai-dev"]
sources: 7
post_ideas: 7
---

# Claude Code 最新アップデート (2026-06-07 収集)

## サマリ
- 直近で一番大きい話題は **Opus 4.8 がデフォルトモデルに昇格 + `/effort xhigh` の追加**。Max / Team Premium / Enterprise / Anthropic API 全部で「高 effort がデフォ」になり、Fast mode も Opus 4.8 ($10 / $50 per MTok = 2 倍料金で約 2.5 倍速) に切り替わった
- **Dynamic Workflows** が research preview で開放。1 つの会話で coordinate しきれない大規模タスク（コードベース全体監査 / 大規模マイグレーション / 横断調査）を、Claude が書いたオーケストレーションスクリプトで複数のサブエージェントに分散させる仕組み
- **security-guidance プラグイン** が公式に追加。各 edit で fast pattern check → ターン終了時に model review → commit / push 時に agentic review、と 3 段階で脆弱性を潰す
- **fallbackModel 設定**が新設。primary が overloaded / unavailable の時に最大 3 つまで順番に試す。`--fallback-model` フラグがインタラクティブセッションにも効くようになった
- v2.1.165 (6/05) はバグ修正のみ。直近 1 週間で機能追加ペースが少し落ち着いて、「6/15 のプラン改定」へ向けた地ならし期間に入った感触
- 2 日前 (6/06) と被らないように、今回は **Opus 4.8 / Dynamic Workflows / security-guidance / fallbackModel / Fast mode / /usage コマンド** に絞った

---

## 収集ネタ

### 1. Opus 4.8 がデフォルト + `/effort xhigh` が解禁
- ソース: [Claude Opus 4.8: 7 Changes + Dynamic Workflows (May 2026)](https://decodethefuture.org/en/claude-opus-4-8-explained/)
- 公開日: 2026 年 5 月下旬（Week 22 / 5 月 25〜29 日）
- 要点（3 行以内）:
  - Opus 4.8 が Max / Team Premium / Enterprise pay-as-you-go / Anthropic API のデフォルトモデルに昇格。**high effort がデフォ**で、最難関タスク用に `/effort xhigh` が追加
  - Fast mode は Opus 4.8 を $10 / $50 per MTok（標準の 2 倍）で提供。**約 2.5 倍速** が売り
  - Opus 4.7 1M コンテキストはまだ動くが、価格 / 性能比で 4.8 に乗り換える人が増える流れ
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「Claude Code、いつのまにか Opus 4.8 がデフォになってる。`/effort xhigh` 打つと一番難しいタスク用の頭になる。Fast mode の高速版は 2 倍払って 2.5 倍速」

### 2. Dynamic Workflows（research preview）
- ソース: [Claude Code News | June, 2026 (STARTUP EDITION)](https://blog.mean.ceo/claude-code-news-june-2026/)
- 公開日: 2026 年 6 月（直近）
- 要点（3 行以内）:
  - 1 つの会話で coordinate しきれない大規模タスク（コードベース全体監査 / 大規模マイグレーション / 横断調査）向けに、Claude がオーケストレーションスクリプトを書いてバックグラウンドの複数サブエージェントへ分散
  - CLI / Desktop / VS Code / API / 主要クラウドプラットフォームで使える。**ビルトイン verification と進捗保存**付き
  - 個人開発者でも「Notion + Threads + GitHub Actions の 3 系統を一気に直して」レベルが現実的になる
- 投稿アイデア:
  - 型: 夜振り返り / 教育目的
  - 切り口: 「Claude Code に Dynamic Workflows が来た。1 回の会話に収まらない『コードベース横断監査』を、Claude が自分でスクリプト書いて複数サブエージェントに投げる。個人開発者でも 1 人 5 人体制ができる」

### 3. security-guidance プラグイン — 3 段階の脆弱性チェック
- ソース: [Claude Code Updates by Anthropic | Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- 公開日: 2026 年 5 月下旬〜6 月初旬
- 要点（3 行以内）:
  - 各 edit で **fast pattern check**、ターン終了時に **model review**、commit / push 時に **agentic review** の 3 段階で脆弱性をチェック → 同じセッションで修正まで走る
  - 「あとで人がレビューしますね」ではなく **生成中に潰す** 方針。SQL injection / 認証バイパス / 秘密情報の混入を生成時点で止める
  - 個人開発者で「コードレビュー仲間がいない」人にとって、第三者レビュー代替として強い
- 投稿アイデア:
  - 型: 夕失敗 → 改善 / 信頼構築
  - 切り口: 「ぼくはレビュアーがいない個人開発者。`security-guidance` プラグイン入れたら、commit 前に Claude が勝手にエージェント走らせて脆弱性チェック → そのまま直してくれた」

### 4. fallbackModel 設定 — overload 対策に 3 つまで予備モデル
- ソース: [Claude Code Updates by Anthropic | Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- 公開日: 2026 年 6 月初旬
- 要点（3 行以内）:
  - primary モデルが overloaded / unavailable の時に試す予備モデルを **最大 3 つまで順番に**指定できる
  - `--fallback-model` フラグはインタラクティブセッションにも適用。CI / バッチだけでなく対話作業でも止まらない
  - Opus 4.8 → Sonnet 4.6 → Haiku 4.5 のような段階的劣化を 1 行設定で組める
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「Claude Code に `fallbackModel` が来た。Opus → Sonnet → Haiku を順番に試してくれる。深夜の自動投稿パイプラインが overload で死ぬ事故、これで激減した」

### 5. v2.1.149 / v2.1.150 — `/usage` コマンドで使用量が詳細表示
- ソース: [Major Updates in Claude Code v2.1.149 to v2.1.150 | DevelopersIO](https://dev.classmethod.jp/en/articles/20260524-claude-code-updates-v2-1-150/)
- 公開日: 2026-05-24
- 要点（3 行以内）:
  - `/usage` で現在のセッションのトークン消費・モデル別内訳・推定コストを詳細表示
  - PowerShell でのパーミッション回避バグ修正、`find` コマンド起因のホストクラッシュも解消
  - 6/15 のプラン分離（対話 vs 自動化クレジット）前に「自分が今いくら使ってるか」を可視化する流れの一部
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「Claude Code に `/usage` が来た。今のセッションでいくら使ってるかが秒で出る。6/15 のプラン分離（自動化が別枠化）前にこれで自分の消費を見える化しておく」

### 6. v2.1.165 (6/05) は安定化リリース — 機能追加ナシ
- ソース: [Claude Code v2.1.165 リリース｜毎日Changelog解説 | Qiita](https://qiita.com/moha0918_/items/c697a35ee9b8a8fa9805)
- 公開日: 2026-06-05
- 要点（3 行以内）:
  - 6/05 リリースの **v2.1.165 はバグ修正と信頼性向上のみ**。新機能は無し
  - `claude -p` が Bedrock / Vertex / Foundry で `ANTHROPIC_API_KEY required` を誤って吐く問題を修正
  - bazel と EDR 保護下の Go ワークフローで bash コマンドが落ちる事象、claude agents の background セッションが再アタッチ時に消える事象も修正
- 投稿アイデア:
  - 型: 昼進捗 / 教育目的
  - 切り口: 「Claude Code 6/05 のアプデは新機能ゼロ・バグ修正のみ。`claude -p` が Bedrock で落ちてた人、ここで治ってる。地味回が一番ありがたい」

### 7. 2026-06-15 プラン分離はまだ 8 日後 — リマインド枠
- ソース: [Claude有料プラン激変！2026年6月15日〜「対話」と「自動化」が完全分離 | あなたのAI顧問](https://ai-advisors.jp/media/ai-news/claude-plan-change-20260615/)
- 公開日: 2026 年 6 月（直近）
- 要点（3 行以内）:
  - 6/15 から「対話」と「自動化」のクレジットが完全分離。`claude -p` / Agent SDK / GitHub Actions は新設の **Agent SDK 月額クレジット**へ
  - Pro=$20 / Max 5x=$100 / Max 20x=$200。**初回手動有効化が必要**で、有効化しないと自動化が止まる可能性
  - 6/06 にも記事化済み。今回は「あと 8 日」のカウントダウン枠として 1 投稿だけ作っておく
- 投稿アイデア:
  - 型: 夕失敗予防 / 信頼構築
  - 切り口: 「Claude のプラン改定まであと 8 日。`claude -p` で夜中バッチ回してる人、6/15 までに『Agent SDK 月額クレジット』の有効化を忘れると朝起きたら全部止まってる」

---

## ネクストアクション
- 上記のうち **Opus 4.8 + `/effort xhigh`** と **Dynamic Workflows** は「教育目的」枠で即下書き化推奨
- **security-guidance プラグイン** は「ぼくはレビュアーがいない個人開発者」というキャラと噛み合うので gaku_ai_life の信頼構築投稿に向く
- **fallbackModel** は深夜パイプラインを回している前提のオーナー自身の体験談と紐づけられる
- 6/15 のプラン分離は **6/13〜6/14 にもう一度リマインド投稿** を予約推奨
