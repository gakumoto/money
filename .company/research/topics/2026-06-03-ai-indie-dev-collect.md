---
created: "2026-06-03"
topic: "AI 個人開発"
status: completed
tags: ["weekly-collect", "ai-indie-dev", "claude-code", "vibe-coding", "agent-sdk-pricing"]
sources: 12
post_ideas: 8
---

# AI 個人開発 リサーチ収集 (2026-06-03)

## 📌 今日の注目（即投稿化推奨・期限あり）

### Claude Agent SDK が 6/15 から有料クレジット制に分離（残り12日）
- ソース:
  - https://devtoolpicks.com/blog/anthropic-splits-claude-subscriptions-agent-sdk-credit-june-2026
  - https://claudefa.st/blog/guide/development/agent-sdk-credit
  - https://www.alexcloudstar.com/blog/claude-june-2026-pricing-survival-guide/
- 公開日: 2026-05-13 発表 / 2026-06-15 施行
- 要点（3行以内）:
  - **Agent SDK / `claude -p` / Claude Code GitHub Actions / OpenClaw 等のプログラム経由実行**がサブスクのプールから外れる。ターミナル対話の Claude Code は影響なし
  - クレジット枠は **Pro=$20、Max 5x=$100、Max 20x=$200**（API 換算、月次・繰越なし）
  - 本番自動化やチーム共有ワークフローで月数百ドル以上トークン消費していたユースケースは、Developer Platform で直接 API キーを使う方が安定する
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的（時限ニュース）
  - 切り口: 「Claude Code 使ってる個人開発勢、6/15 から `claude -p` とか GitHub Actions 経由の自動化は別枠課金になる。Pro なら月 $20 クレジットまで。ターミナルで打つ分は変わらない。"知らずに自動化止まる" 事故が一番もったいない」

---

## ✅ 投稿ネタ候補

### 1. Marc Lou が AI で 1 日で作った TrustMRR、過去3プロダクトを足したより MRR が出た
- ソース:
  - https://quasa.io/media/how-youtuber-and-indie-hacker-marc-lou-tackled-the-fake-revenue-screenshot-problem
  - https://startupseries.io/how-indie-hacker-marc-lou-monetised-mrr-bragging/
- 公開日: 2025-10-30 リリース、2026 にかけて伸長
- 要点:
  - TrustMRR = Stripe API キーを read-only で繋いで「本物の MRR」を証明するページを生成するサービス
  - **1日で構築**したプロダクトが、数ヶ月かけた過去3つを足したより MRR が出ている
  - Marc Lou は ShipFast (~$54K MRR) も持つ。"作る難易度を下げるツール" 自体がビジネスになる構造
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Marc Lou が 1 日で作った "Stripe で MRR を証明するサービス"、過去3つの月単位開発を足したより売れてる。"何ヶ月かけたか" は売上と関係ない、を体現してて怖い」

### 2. 18ヶ月 $2K MRR で停滞 → AI 機能を追加した第1週で $8K、8ヶ月で $50K
- ソース: https://www.indiehackers.com/post/from-2k-mrr-to-50k-in-8-months-how-one-indie-hacker-cracked-the-ai-code-30d5ace166
- 公開日: 2025-09-10
- 要点:
  - 既存 B2B SaaS に LLM 機能（AI データ分析・ドキュメント処理・サポート Bot・分析ダッシュボード）を統合
  - 初期実装コストは API + ホスティング込みで **$497**
  - 第1-2月 で離脱率 -40%、サポートチケット -70%、$8K MRR 到達。価格を 3 倍に上げた
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「18ヶ月 $2K で止まってたインディーハッカーが、$497 だけ使って AI 機能を後乗せしたら 8ヶ月で $50K に化けた話。"作り直さなくていい"が一番救い」

### 3. Vibe coding は "ニッチ" じゃない。$4.7B 市場、利用者の 63% が非エンジニア
- ソース:
  - https://superframeworks.com/articles/vibe-coding-tipping-point-what-founders-need-to-know
  - https://vibecoding.app/blog/vibe-coding-debate
- 公開日: 2026-05
- 要点:
  - Vibe coding 市場は **$4.7B**。Collins Dictionary の Word of the Year に選出
  - 利用者の **63% が非開発者**。フルスタックアプリ・UI・個人用ソフトを「コードを書かずに」作っている
  - "AI でガワだけ作る人" は珍しくなくなった = "作る" 競争はすでに終わってる
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「Vibe coding の利用者、すでに 63% が非エンジニア。"作れるかどうか" で勝負する時代はもう終わってる。残ってるのは "誰に届けるか"」

### 4. Anthropic 社内マーケは 1 人 + Claude Code。広告監査が 4-8 時間 → 5 分
- ソース:
  - https://meta-heroes.co.jp/news/marketing-ai-only-claude-code
  - https://x.com/commte/status/2024771301538435201
  - https://note.com/ayumi_ai/n/nc20e639aa4c6
- 公開日: 2026-05
- 要点:
  - Anthropic 自社マーケチームの **非エンジニア 1 名**が検索広告・SNS 広告・メール・SEO を全部 Claude Code で回している
  - Claude Ads スキルで広告監査が **4-8時間 → 5分以内** に短縮
  - Google Ads CSV を読み込ませて成果の悪い広告を自動抽出、Figma プラグインも自作
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Anthropic 公式が "社内マーケは非エンジニア 1 人だけ、全部 Claude Code" って事例出してた。広告監査 4 時間 → 5 分。個人開発者の "売る側" がやっと安く回せるようになった」

### 5. Richard Wang の Leadmore AI、Vibe coding で MVP 1-2 週間 → $30K MRR
- ソース: https://www.indiehackers.com/post/tech/hitting-30k-mrr-with-an-ai-marketing-product-n59ORJCYjnZC61Q096UL
- 公開日: 2026 前半
- 要点:
  - AI マーケティングプロダクト Leadmore AI を Vibe coding でリリース、MVP は **1-2 週間**
  - 早期ユーザーの手に渡してフィードバックでイテレーション、$30K MRR 到達
  - 「凝った MVP より、早く触らせて直す」型
- 投稿アイデア:
  - 型: 朝学び型 / 集客
  - 切り口: 「$30K MRR まで伸びた AI マーケアプリの作者が言ってた "MVP は 1-2 週間で出す、凝るな、早くユーザーの手元に渡せ"。これ、自分が一番苦手なやつだ」

### 6. AI オーケストレーションの Meerkats.ai、4 週で $3K MRR の "ニッチ攻め" 教訓
- ソース: https://www.indiehackers.com/post/tech/growing-an-ai-orchestration-platform-to-3k-mrr-in-4-weeks-gK3zYDqQjXYG9ANwmxzA
- 公開日: 2026 前半
- 要点:
  - 「ジェネリックな AI ツールをもう一つ作る」ではなく、**既に金が動いている業務**（リード生成・アウトリーチ・営業 ops）を AI で置換
  - 4 週間で $3K MRR
  - "新しい行動を作る" より "既存の支出を置き換える" 方が売れる
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「個人開発の "売れない" の正体、ここ。"AI で何か新しいことやろう" は売れない。"今すでに金払ってる作業" を AI で安く置き換える方が、4 週で $3K 出る」

### 7. ペパボ社例: 同じレビュー指摘を Claude Code に繰り返させない "失敗学習ループ"
- ソース: https://zenn.dev/pepabo/articles/claude-code-failure-learning-loop
- 公開日: 2026 前半
- 要点:
  - リポジトリに `.claude/` を置き、CLAUDE.md とコマンドで「過去のレビュー指摘」を AI が読む構造に
  - **3 ヶ月運用で同種のレビュー指摘がほぼゼロ**
  - 個人開発でも応用可能。"AI に同じことを 2 回言わせない" 仕組み
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「ペパボの事例、めっちゃ参考になった。"Claude Code に同じ指摘を 2 回させない仕組み" を `.claude/` に置くだけで、3 ヶ月でレビュー指摘がほぼゼロに。個人開発でも今日できる」

### 8. Claude Code で 1 人で 40 万行のフルスタック + インフラ、2 年運用の知見
- ソース: https://zenn.dev/shusuke_o/articles/f63e1bf61363b8
- 公開日: 2026 前半
- 要点:
  - Claude Code と組んで **40 万行規模** のフルスタック + インフラを 1 人で構築
  - "AI に任せきり" だと破綻する。設計と協働のやり方が肝
  - 2 年間の試行錯誤を体系化
- 投稿アイデア:
  - 型: 深夜思考型 / 信頼構築
  - 切り口: 「Claude Code と 2 年組んで 40 万行のフルスタック + インフラを 1 人で書いた人の知見。"AI に任せきりだと破綻する" って結論、これが一番リアル」

---

## 🧭 今週の構成メモ（運用への活かし方）

- **時限ニュース**（Agent SDK 6/15）: 残り 12 日なので「気づかず損する」型で 1 投稿、6/14 にリマインド型でもう 1 投稿
- **"作る vs 売る" の比率**: 今週の投稿、TrustMRR / Leadmore / Meerkats / Anthropic マーケ の 4 本は全部「**売る側がボトルネック**」に収束する。Phase 2 のテーマ "実験記" と接続できる
- **数字の固有性**: $2K→$50K、$497、4h→5min、40万行、63% など強い数字が複数取れた。冒頭1行用に温存
- **inbox 連携**: 上記うち 3-4 個は `topics/inbox/` に状態 unused で落としておく価値あり（threads-daily-run 用）

---

## 📚 参考リンク（補強用）

- Vibe coding 中級者向け 10 ステップ: https://blog.vibecoder.me/indie-hacker-intermediate-path-building-and-shipping-solo
- Anthropic 6/15 価格変更 決定表: https://findskill.ai/blog/claude-code-pricing-after-june-15-decision-table/
- Marc Lou の $1M/年 ソロ SaaS コンパウンド分析: https://www.indiehackers.com/post/what-marc-lou-s-1m-year-reveals-about-solo-saas-compounding-Kd7SbxGXTYn5gMdfoY8R
- 個人開発 "1 人マーケ部門" (KAWAI 氏): https://note.com/kawaidesign/n/n229818b75aa1
