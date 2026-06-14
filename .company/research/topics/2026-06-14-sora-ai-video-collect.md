---
created: "2026-06-14"
topic: "Sora AI 動画生成 × 個人開発"
status: completed
tags: ["weekly-collect", "sora", "ai-video", "indie-dev"]
sources: 14
post_ideas: 6
---

# Sora AI 動画生成 × 個人開発 リサーチ (2026-06-14)

## 全体サマリ

2026年3月25日、OpenAI が Sora のサービス終了を発表。dedicated アプリと API の提供が打ち切られ、**Sora 2 API は 2026年9月24日に shutdown** される。つまり今 Sora で何か作っている個人開発者には「あと3ヶ月で乗り換え or 死」のタイムラインが切られている状態。

代替候補は Veo 3 / Kling 2 / Runway Gen-4 / Seedance Pro。コスパは Kling (月$5で3分)、品質は Runway Gen-4.5 / Veo 3.1、低コスト路線は Google が出した Veo 3.1 Lite。

個人開発者にとって今週インプットすべきは「Sora 終了」というニュースそのものよりも、**"なぜ終了するのか (計算コスト + 著作権)" と "次に何を使うか" のセット**。

---

## ネタ1: Sora 2 API、2026年9月24日に shutdown

- ソース: [Sora 2 Pricing 2026 (Magic Hour)](https://magichour.ai/blog/sora-2-pricing) / [Sora 2 API Sunset Guide (Cost Goat)](https://costgoat.com/pricing/sora)
- 公開日: 2026-04 〜 2026-06
- 要点（3行以内）:
  - OpenAI が Sora の dedicated アプリと API 終了を 2026年3月25日に発表
  - Sora 2 API は 2026年9月24日以降、新規リクエストを受け付けない
  - 終了背景は「計算コストの負担」と「著作権周りの戦略再構築」
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Sora が消える日が決まった。9月24日。個人開発者がやることは2つだけ」
  - もう一案: 弱さ枕詞型「Sora 推しで動画生成サービス作ろうとしてた。OpenAI 終了発表で全部白紙になった話」

---

## ネタ2: Sora 2 API の実料金 — 10秒で $1〜$5

- ソース: [Sora 2 API Pricing Compared (GLB GPT)](https://www.glbgpt.com/hub/sora-2-api-pricing-compared-official-vs-unofficial-providers-costs-and-developer-reactions/) / [Sora 2 API Pricing & Quotas Complete 2026 Guide (AI Free API)](https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas)
- 公開日: 2026-05 〜 2026-06
- 要点（3行以内）:
  - Sora 2 Standard: $0.10/秒 (720p)、Pro: $0.30〜$0.70/秒
  - Batch tier なら $0.05/秒 (50%引・24h SLA)
  - 「本当のコストは最終 export ではなく iteration」— 採用1本に対して何本も生成する前提
- 投稿アイデア:
  - 型: 夕失敗型 / 信頼構築
  - 切り口: 「AI動画で副業しようと Sora API 触ってみた。10秒で500円消えた。3本目で気づいたこと」
  - 数字を入れた「副業のリアル」枠

---

## ネタ3: 代替モデル4社比較 — Veo 3 / Kling 2 / Runway Gen-4 / Seedance Pro

- ソース: [AI動画モデル5社最新比較 2026年5月版 (CREATORS POST)](https://torihada.co.jp/creatorspost/4314/) / [Runway Gen-4.5 vs Kling AI 2.6 VS VEO3.1 徹底比較 (GIRL-PC)](https://girl-pc.com/runway-vs-kling-vs-veo/)
- 公開日: 2026-04 〜 2026-05
- 要点（3行以内）:
  - コスパ最強: Kling = 月$5で3分動画
  - 映像品質: Runway Gen-4.5 / Veo 3.1
  - 低コスト枠の新顔: Google が Veo 3.1 Lite を発表
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Sora 終了で乗り換え先 3つ試した結果ランキング。Kling が異常にコスパいい」
  - 短く結論先出しでテンプレ化しやすい

---

## ネタ4: Sora 終了後の AI動画副業ツール5選

- ソース: [Soraが終了…でも大丈夫。AI動画で副業できるツール5選 (note・フク)](https://note.com/fuku_engineer/n/n5b37e26bb2a9)
- 公開日: 2026-03-26
- 要点（3行以内）:
  - Runway Gen-3 ($15〜) / Veo 2 / Pika ($8〜) / HeyGen ($29〜) / Seedance 2.0
  - 稼ぎ方の3本柱: 制作代行・コンテンツ販売・アフィリエイト
  - 月3万円達成を最初の目標に
- 投稿アイデア:
  - 型: 朝学び型 / 集客
  - 切り口: 「Sora 終了でも AI動画副業は死んでない。月3万までの 5ツール棚卸し」
  - note 誘導の入口に使える (一覧→note で深堀り)

---

## ネタ5: 全自動 AI動画 YouTube で月数万ドルの個人クリエイター

- ソース: [生成AIでマネタイズできる？副業として稼ぐ方法を解説 (デジハクmagazine)](https://digital-hacks.jp/blog/archives/19647) / [週刊AI時代に月100万円以上稼ぐ海外個人開発者 (みんなのニュースレター)](https://umatan.m-newsletter.com/)
- 公開日: 2026-04 〜 2026-06
- 要点（3行以内）:
  - AI 全自動の YouTube チャンネルで月数万ドルの海外個人クリエイターが存在
  - 顔出し・声出し不要、プライバシー守りつつ収益化
  - 海外個人開発アプリ「Once」が5ヶ月で月500万、「Jungle」が月1500万到達例も
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「AI動画 YouTube で月数万ドルの個人がいる。自分との差分を3つ書き出した」
  - 「凄い人を出して自分との距離を測る」枠 — 弱さ枕詞と相性◎

---

## ネタ6: Sora が終わる本当の理由 = 計算コスト + 著作権

- ソース: [動画生成AI「Sora」はいつ提供終了する？ (C-NAPS)](https://fungry.co.jp/cnaps/blog/sora-ai/) / [Sora2の終了発表 (ヒューコネクト)](https://www.hu-connect.co.jp/blog/2026/04/content.html)
- 公開日: 2026-04
- 要点（3行以内）:
  - 公開から半年で撤退発表
  - 背景は「膨大な計算コスト負担」と「著作権問題周りの戦略再構築」
  - OpenAI ですら畳む領域 = 個人開発が動画生成"基盤"側で戦うのは現実的でない
- 投稿アイデア:
  - 型: 深夜思考型 / 信頼構築
  - 切り口: 「OpenAI ですら Sora 畳んだ。個人開発が"AI動画基盤"で戦うのが無理な理由を3行でまとめた」
  - 短文で言い切る系、深夜投稿向け

---

## 心得メモ

- Sora 関連は今 過去1週間で何回もネタ化されており飽和気味 → 「終了発表」そのものより「9月24日shutdown までの3ヶ月で何する？」という時限性のある切り口が刺さりそう
- gaku の本業 (Threads × note × Claude Code) からは Sora 動画生成は遠い → 自分の文脈に落とすなら「動画生成"を使う側"ではなく、AI 全般の流れとして個人開発者が学ぶレッスン」枠
- 競合 note 含めて Sora 解説記事は飽和、深堀りより「個人開発者目線の1スライス」で勝負
