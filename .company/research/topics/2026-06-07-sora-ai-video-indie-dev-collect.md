---
created: "2026-06-07"
topic: "Sora AI 動画生成 個人開発"
status: completed
tags: ["weekly-collect", "sora", "video-ai", "indie-dev"]
sources: 6
post_ideas: 6
---

# Sora AI 動画生成 × 個人開発 リサーチ（2026-06-07）

## 全体サマリー（投稿者向けの一行）

**「Sora 2 API は 2026/09/24 で完全終了」** — Sora アプリは 4/26 にすでに終了済み、残された API も 9/24 で打ち切り。個人開発で動画生成 AI を組み込んでいる人は、**残り 3.5 ヶ月で Veo 3.1 / Kling 3.0 / Runway Gen-4.5 への移行を完了させる必要がある**。今日いちばん刺さるネタはこの「移行ラッシュ」。

---

## 注目情報

### 1. Sora 2 API は 2026年9月24日で完全終了
- ソース: https://openai.com/sora/  (OpenAI Help Center)
- 公開日: 2026年内（OpenAI 公式アナウンスメント）
- 要点（3行以内）:
  - Sora の Web/アプリ体験は **2026年4月26日にすでに終了**
  - 開発者向け Sora 2 API は **2026年9月24日に終了**（残り約3.5ヶ月）
  - 終了後は OpenAI からの後継動画モデルは現時点で未発表
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Sora API、9月24日で死ぬ。動画AI組み込み勢、移行の3.5ヶ月カウントダウン始まった」

### 2. Sora 2 API の正規料金（720p 1秒 = $0.10、1080p Pro = $0.70/秒）
- ソース: https://platform.openai.com/docs/guides/video-generation, https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas
- 公開日: 2026年（複数情報源で確認）
- 要点（3行以内）:
  - Sora 2 Standard: **720p $0.10/秒、Batch は $0.05/秒**
  - Sora 2 Pro: **720p $0.30 / 1024p $0.50 / 1080p $0.70 per second**（Batch は半額）
  - 16秒〜20秒生成対応。Plus契約は 5 RPM、Pro 契約で 50 RPM
- 投稿アイデア:
  - 型: 夕失敗 / 昼進捗
  - 切り口: 「Sora 2 で 20秒の動画 1本 = $14（約2,100円）。個人開発で5本作ったら1万円飛んだ」

### 3. 非公式 Sora API 経由なら 50〜85% 安く叩ける
- ソース: https://kie.ai/sora-2, https://www.aifreeapi.com/en/posts/cheapest-sora-2-api
- 公開日: 2026年
- 要点（3行以内）:
  - 非公式プロバイダ（Kie.ai、LaoZhang、Apiyi 等）が Sora 2 を $0.015〜$0.10/秒で提供
  - 公式比で 50〜85% 安い。残り 3.5 ヶ月の駆け込み開発に最適
  - ただし 9/24 シャットダウン後は全プロバイダ同時に死ぬので、長期パイプは組まないのが鉄則
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「Sora 2、非公式 API なら 1/10 の値段で叩ける。終わるまでの 3.5 ヶ月、ここで遊び尽くす」

### 4. Sora ポスト時代の本命は Veo 3.1（Google）と Kling 3.0
- ソース: https://www.opus.pro/blog/best-sora-2-alternatives-after-openai-shutdown, https://www.atlascloud.ai/blog/guides/seedance-vs-kling-vs-sora-vs-veo
- 公開日: 2026年
- 要点（3行以内）:
  - **Veo 3.1（Google）**: Sora 2 Pro 相当の品質。映像と同期した音声・効果音を1パスで生成
  - **Kling 3.0**: 短尺シネマティック動画では Sora 2 の最も近い代替
  - Runway Gen-4.5、Luma Dream Machine、Pika、Seedance 2.0 が次点
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「Sora 終わるけど慌てるな。Veo 3.1 / Kling 3.0 触ってる人いる？俺は今から両方つなぐ」

### 5. AI動画副業の現実値は「月3万円スタート」
- ソース: https://aimonetizelab.com/sora-ai/, https://www.matrixflow.net/case-study/162/
- 公開日: 2026年
- 要点（3行以内）:
  - 副業で動画 AI 単体で食うのは現実的じゃない。月3万円が最初の現実的ターゲット
  - YouTube は「繰り返しコンテンツ判定」で AI 大量投下が収益化停止リスク
  - 制作代行（toC は厳しい、toB の単発案件）と組み合わせて柱を2本にするのが定石
- 投稿アイデア:
  - 型: 夕失敗 / 教育目的
  - 切り口: 「AI動画で月100万、は嘘。最初の壁は月3万。YouTube収益停止くらった人多数」

### 6. ChatGPT Plus($20)で 1,000 クレジット、Pro($200)で 10,000 クレジット
- ソース: https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas, https://openai.com/sora/
- 公開日: 2026年
- 要点（3行以内）:
  - Plus（$20/月）は Sora 1,000 クレジット込み（720p で約 62 秒分）
  - Pro（$200/月）は 10,000 クレジット + Relaxed モード夜間無制限
  - 2026/01/10 から **無料ユーザーは Sora 動画生成不可**
- 投稿アイデア:
  - 型: 朝学び / 販売目的
  - 切り口: 「Sora 触るなら ChatGPT Plus の $20 が一番コスパいい。Pro $200 は法人以外いらない」

---

## 個人開発者として今すぐ動くべきこと（投稿の切り口）

1. **「9月24日カウントダウン」シリーズ** — 残り日数を毎週カウントしながら、Sora で遊んでみた進捗を投稿
2. **「Veo 3.1 / Kling 3.0 触ってみた」** — Sora 移行先を実際に叩いて、組み込み手順を晒す
3. **「AI動画副業の現実」** — 月3万円という現実値、YouTube 収益化停止リスクを正直に書く
4. **「OpenAI なぜ Sora を捨てたか」** — コンシューマビジネスの難しさという考察軸（impress watch ソースあり）

---

## ソース一覧（全URL）

- [Sora 2 is here | OpenAI](https://openai.com/index/sora-2/)
- [Video generation with Sora | OpenAI API](https://platform.openai.com/docs/guides/video-generation)
- [What to know about the Sora discontinuation](https://openai.com/sora/)
- [Sora 2 API Pricing & Quotas 2026 - AI Free API](https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas)
- [Sora-2 API shutdown date announced - Apiyi.com](https://help.apiyi.com/en/sora-2-api-shutdown-alternatives-2026-en.html)
- [Best Sora 2 Alternatives After 2026 Shutdown - OpusClip](https://www.opus.pro/blog/best-sora-2-alternatives-after-openai-shutdown)
- [Sora終了…AI動画で副業できるツール5選 - note/フク](https://note.com/fuku_engineer/n/n5b37e26bb2a9)
- [Soraが終了した今こそ乗り換えるべき動画AI3選 - AIマネタイズラボ](https://aimonetizelab.com/sora-ai/)
- [Seedance vs Kling vs Sora vs Veo - Atlas Cloud](https://www.atlascloud.ai/blog/guides/seedance-vs-kling-vs-sora-vs-veo)
- [Cheapest Sora 2 API in 2026 - AI Free API](https://www.aifreeapi.com/en/posts/cheapest-sora-2-api)
