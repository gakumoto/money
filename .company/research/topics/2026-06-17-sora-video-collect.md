---
created: "2026-06-17"
topic: "Sora AI 動画生成 × 個人開発"
status: completed
tags: ["weekly-collect", "sora", "ai-video", "indie-dev"]
sources: 8
post_ideas: 6
---

# Sora AI 動画生成 × 個人開発 リサーチ（2026-06-17）

## サマリー
2026年6月時点で個人開発者にとって最大の論点は「Sora 2 の事実上の終了」。
- 2026-03-25 に OpenAI が Sora サービス終了を発表
- API 完全停止は 2026-09-24（残り約3ヶ月）
- 個人開発で Sora API に乗っていたプロダクトは強制的に乗り換え必要
- 代替は Veo 3.1（4K対応）/ Runway Gen-4.5 / Kling 2.6（音声同時生成）/ Pika 2.5 / Seedance 2.0
- OpenAI は「自律型エージェント」「ロボティクス」にリソース集中という戦略転換

これは個人開発者にとって「API依存リスク」「乗り換えのリアル」の両方を語れる旬ネタ。

---

## 収集情報

### 1. Sora 2 サービス終了（最重要）
- ソース: https://sogyotecho.jp/sora2/
- 公開日: 2026-03-26
- 要点:
  - 2026-03-25 OpenAI が Sora アプリ・API の提供終了を発表
  - 戦略転換：自律型AIエージェントとロボティクスへのリソース集中
  - ディズニーとの10億ドル提携にもかかわらず終了
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「OpenAIが動画生成を捨てた。エージェントとロボに全振り。個人開発で何に張るかの判断材料になる」

### 2. Sora API 完全停止スケジュール
- ソース: https://note.com/softcollect/n/nd08edaf135f8
- 公開日: 2026-03
- 要点:
  - API 完全停止予定日：2026-09-24
  - 個人開発で Sora API 使ってたサービスは3ヶ月で死ぬ
  - 移行先比較：Runway Gen-4.5 / Kling 2.6 / Pika 2.5 / Vidu / Google Veo 3.1
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Sora API、9月で完全停止。個人開発で動画生成に乗ってた人、いま乗り換え3ヶ月戦争に突入してる」

### 3. Sora 2 API の技術的ハマりどころ
- ソース: https://qiita.com/GeneLab_999/items/b67428ce9a0da2d3ec8f
- 公開日: 2025-10〜2026-01
- 要点:
  - 動画長は 4 / 8 / 12 秒のみ指定可能（任意秒数は不可）
  - ダウンロードURLの有効期限は生成後 24 時間
  - 人間の顔を含む入力画像は拒否される（肖像権対策）
  - 組織認証が必須（Verify Organization → 反映に最大15分）
- 投稿アイデア:
  - 型: 失敗型 / 教育目的
  - 切り口: 「Sora 2 API、動画長が 4/8/12 秒しか選べない。10秒で作ろうとしてた俺、ドキュメント見ずに半日溶かした」

### 4. Sora 料金体系（個人開発者の現実コスト）
- ソース: https://www.aquallc.jp/sora-2-complete-guide/
- 公開日: 2026-01以降
- 要点:
  - 2026-01-10 から無料プラン廃止、ChatGPT Plus/Pro に完全統合
  - ChatGPT Plus（月$20）：5秒・720p・1000クレジットの限定利用
  - ChatGPT Pro（月$200）：1080p・最大20秒・月500本生成
  - API は生成秒数ベースの従量課金
- 投稿アイデア:
  - 型: 数字提示型 / 信頼構築
  - 切り口: 「ChatGPT Plus の$20 でも Sora は 5秒・720p で詰む。フル機能は月$200。個人開発の検証コストの現実」

### 5. AI動画副業の現実値（月収のリアル）
- ソース: https://note.com/freelife_creator/n/n1ef3f7b30f4b
- 公開日: 2026
- 要点:
  - 「AI×ショート動画で月30万」は限定的、最初の月は5-10万が現実
  - 半年やって 20-30万 に到達するパターンが多い
  - YouTube 収益化条件：3000時間視聴 / 12ヶ月 または ショート300万再生/90日
- 投稿アイデア:
  - 型: 暴露型 / 信頼構築（弱さ枕詞）
  - 切り口: 「AI動画副業『月30万』の正体。最初の月は5万、半年で20-30万が現実。煽り記事に騙されないでくれ」

### 6. Sora 後の代替AI比較（Veo 3.1 / Runway / Kling）
- ソース: https://uravation.com/media/seedance-veo-runway-comparison-2026-post-sora/
- 公開日: 2026-03以降
- 要点:
  - Google Veo 3.1：ネイティブ 4K 出力対応
  - Kling 2.6：動画と音声を同時生成
  - Runway Gen-4.5：最高画質、Adobe 互換性
  - Seedance 2.0：複数モデル切替型
- 投稿アイデア:
  - 型: 比較型 / 教育目的
  - 切り口: 「Sora 後の動画AI、個人開発が触るなら Veo 3.1（4K）/ Kling 2.6（音声同時）/ Runway Gen-4.5（画質）どれ？用途別の使い分け1行で」

---

## 注目トピック（即投稿化推奨）

**「Sora API 9/24完全停止 × 個人開発の乗り換え判断」**

理由:
- 期限が具体的（残り99日）で投稿の切迫感が出る
- 自分は何者か（個人開発者）× 気づき1つ（API依存のリスク） の構図がきれいに作れる
- 「OpenAI に張るか他社に張るか」は個人開発者の永遠の話題
- 数字（9/24、$20、$200、4秒/8秒/12秒）が豊富で具体性◎

## 投稿の型マッピング

| 投稿時間帯 | 採用ネタ | 型 |
|---|---|---|
| 朝学び | #2 Sora API 9月停止 | 教育 |
| 昼進捗 | #3 動画長 4/8/12秒 ハマり | 失敗 |
| 夕 | #4 月$200 のコスト現実 | 数字提示 |
| 夜振り返り | #5 月30万の正体 | 暴露 |
| 深夜思考 | #1 OpenAI の戦略転換 | 思考 |
| 比較教育 | #6 Veo/Runway/Kling 比較 | 教育 |

---

## 出典一覧
- https://sogyotecho.jp/sora2/
- https://www.aquallc.jp/sora-2-complete-guide/
- https://qiita.com/GeneLab_999/items/b67428ce9a0da2d3ec8f
- https://note.com/softcollect/n/nd08edaf135f8
- https://uravation.com/media/seedance-veo-runway-comparison-2026-post-sora/
- https://uravation.com/media/openai-sora-shutdown-alternatives-guide-2026/
- https://note.com/freelife_creator/n/n1ef3f7b30f4b
- https://note.com/ai__worker/n/n699ad9afdc93
