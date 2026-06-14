---
created: "2026-06-04"
topic: "Sora AI 動画生成 × 個人開発"
status: completed
tags: ["weekly-collect", "ai", "video", "sora", "indie-dev"]
sources: 9
post_ideas: 8
---

# 調査: Sora AI 動画生成と個人開発の今

## 目的
- 投稿ネタ仕入れ（gaku_ai_life）
- 「Sora終了 → 次どこへ？」は個人開発・副業層が今いちばん検索する文脈
- Threads で「AI 動画 × 個人」の文脈で先に旗を立てる

## 調査内容

### 情報源 1: Sora API サンセット日程の確定
- URL: https://costgoat.com/pricing/sora
- 公開日: 2026-05 頃更新
- 要点:
  - OpenAI が 2026-03-24 に Sora 終了を発表
  - 消費者アプリ（web + iOS）は 2026-04-26 にシャットダウン済み
  - API は 2026-09-24 にサンセット、以降は新規リクエストを受け付けない
  - 理由: OpenAI のリソースを「エージェント / ロボティクス」に集中させる戦略転換

### 情報源 2: Sora 2 API 料金構造
- URL: https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas
- 公開日: 2026 年版
- 要点:
  - Sora 2 Standard: $0.10/秒（720p）/ Batch なら $0.05/秒
  - Sora 2 Pro: 720p $0.30/秒、1024p $0.50/秒、1080p $0.70/秒
  - Pro の Batch はおよそ半額（$0.15/$0.25/$0.35）
  - 10 秒動画 1 本 = $1〜$7 のレンジ。検証で焼きやすい価格帯

### 情報源 3: Sora 2 プラン側の変更
- URL: https://help.apiyi.com/en/openai-sora-2-policy-change-plus-pro-only-en.html
- 公開日: 2026-01-10 施行
- 要点:
  - 2026-01-10 から無料ユーザーは Sora で動画生成不可
  - 残るのは ChatGPT Plus（$20/月）と Pro（$200/月）のみ
  - 「無料で試した → 有料に課金 → 数ヶ月後に終了通告」の流れ
  - 個人開発者目線では「短期で元を取る」読みが必須だった

### 情報源 4: 代替ツールの本命比較（Veo / Kling / Runway）
- URL: https://www.veo3ai.io/blog/best-sora-alternatives-2026-shutdown
- 公開日: 2026 年版
- 要点:
  - Google Veo 3.1: 4K 出力 + ネイティブ音声生成（Sora 未実装機能）
  - Kling AI 3.0: 単発で最大 3 分の長尺生成、$0.12-0.15/秒、量産向け
  - Runway Gen-4.5: 動作制御の Elo 1247 で首位、CM/物語系で強い
  - 「Sora を短期で使い、本命は Veo か Kling に寄せる」が主流

### 情報源 5: Sora 終了後の AI 動画副業ルート
- URL: https://aimonetizelab.com/sora-ai/
- 公開日: 2026 年（Sora 終了対応版）
- 要点:
  - Sora 終了後の本命: Runway Gen-4.5 / Kling AI / Veo 3 の 3 択
  - YouTube ショート + 長尺誘導が最も再現性が高い導線
  - Adobe Stock 等への素材販売はストック型で寝てる間も売れる
  - AI 動画大量投稿は YouTube 側で「繰り返しコンテンツ」判定リスクあり

### 情報源 6: 個人クリエイターの月 10 万到達パターン
- URL: https://media.brain-market.com/short-ai-brain/
- 公開日: 2026 年版
- 要点:
  - ChatGPT で台本 → DALL·E で画像 → Runway で動画化 → CapCut で編集
  - 顔出しなし・スマホ 1 台で 1 本 10〜20 分
  - 月 30 万円のクリエイターも出てきている
  - ジャンル偏在: 歴史 POV / 都市伝説 / 動物擬人化が突出

### 情報源 7: 歴史 POV というニッチ
- URL: https://media.brain-market.com/ai-history-brain/
- 公開日: 2026 年版
- 要点:
  - 「AI 動画で月 10 万を超えた人の多くが歴史 POV ジャンル」
  - 史実 + 一人称視点 + 短尺で完結という型
  - 顔出し不要・ナレ AI でフルパイプ自動化が効く

### 情報源 8: 公式 Sora 2 ガイド（一次情報）
- URL: https://openai.com/index/sora-2/
- 公開日: 2025-09 公開
- 要点:
  - text-to-video + image-to-video + 同期音声がデフォルト
  - Sora 2 / Sora 2 Pro の 2 階建て構成
  - 720p までが Sora 2、1080p が必要なら Pro
  - 商用利用は許諾範囲内で可。組織認証必須

### 情報源 9: Sora 2 商用利用と著作権
- URL: https://taskhub.jp/useful/sora2-shouyou-riyou/
- 公開日: 2026 年
- 要点:
  - 商用利用は OK だが、生成物の中に既存 IP が混入するリスクは残る
  - 終了に向けて生成済みアセットの保管 / バックアップは早めに
  - 学習データの取り扱い変更が今後の代替ツール選定でも論点になる

## 結論（断定で）
- Sora API は 2026-09-24 に止まる。個人開発で組み込むなら今からは無理に追わない
- 本命の乗り換え先は Veo 3.1（音声同梱）か Kling AI 3.0（長尺・安価）
- 「個人 × AI 動画 × 収益化」は歴史 POV / 都市伝説の量産が一番再現性が高い
- 料金感覚は 10 秒 = $1〜$7。1 日 100 本焼いて勝負するレベル感で見ておく
- Sora 終了の真因は「エージェント / ロボティクス集中」というメッセージ。個人開発者は AI エージェント側に流れる仮説が立つ

## 投稿アイデア（8 件）

### 1. Sora API 9 月終了の衝撃
- 型: 朝学び型 / 教育目的
- 切り口: 「Sora 2 API が 2026-09-24 で終わる。個人開発で動画 AI を組む人は乗り換え準備に入る時期」
- 数字: 終了日 2026-09-24 / 消費者アプリは 2026-04-26 終了済み

### 2. AI 動画 1 本いくらか
- 型: 教育目的（コスト感）
- 切り口: 「Sora 2 で 10 秒動画は $1。Pro 1080p なら $7。1 日 100 本焼いても 1 万円台」
- 数字: $0.10/秒 〜 $0.70/秒

### 3. OpenAI が Sora を切る理由
- 型: 深夜思考型
- 切り口: 「Sora を切ってまでエージェントとロボティクスに寄せる OpenAI。個人開発の風向きも変わる」
- 共感ポイント: 個人で AI 動画やってた人にとっての「ハシゴ外し」

### 4. Sora 後の乗り換え先 3 つ
- 型: 朝学び型
- 切り口: 「Sora が止まった後の本命は Veo 3.1 / Kling 3.0 / Runway Gen-4.5。使い分けはこう」
- 数字: Veo=4K + 音声 / Kling=3 分 + $0.12 / Runway=Elo 1247

### 5. 歴史 POV が月 10 万の最短ルート
- 型: 教育目的
- 切り口: 「AI 動画副業で月 10 万到達者の共通点は『歴史 POV』。顔出しゼロで再現性が一番高い」
- 数字: 月 10 万 / 顔出し 0

### 6. 顔出しゼロのワークフロー
- 型: 昼進捗型
- 切り口: 「ChatGPT → DALL·E → Runway → CapCut。1 本 20 分。スマホで完結する型」
- 具体: 4 ツール / 20 分

### 7. 無料 Sora の終わりが教える教訓
- 型: 夕失敗型
- 切り口: 「2026-01-10 に Sora 無料プランが消えた。AI 副業は『無料が消える前提』で動かないと焼ける」
- 警鐘: $20 → $200 → API 終了の流れ

### 8. ストック販売という地味で強い導線
- 型: 教育目的
- 切り口: 「AI 動画は Adobe Stock に置くと寝てる間も売れる。再生数より資産化を狙う方が個人向き」
- 補足: YouTube ショートは「繰り返しコンテンツ」判定リスクあり

## ネクストアクション
- [ ] 投稿アイデア 1〜2 件を `/threads-create-post` で即下書き化 | 優先度: 高 | 期限: 2026-06-05
- [ ] 「Sora 終了 + 乗り換え」を 1 本 note 教材化できるか検討（products へ提案） | 優先度: 通常
- [ ] 9 月 24 日のサンセット日を Threads でリアタイ実況できるか PM に共有 | 優先度: 低

## マーケ/プロダクトへの共有
- 共有先: marketing/gaku_ai_life, products
- 反映タスク:
  - gaku_ai_life: 上記 8 ネタを inbox 化候補として queue
  - products: 「Sora 終了で動く AI 動画個人開発の選び方」教材ネタを評価

## 参考リンク
- https://costgoat.com/pricing/sora
- https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas
- https://help.apiyi.com/en/openai-sora-2-policy-change-plus-pro-only-en.html
- https://www.veo3ai.io/blog/best-sora-alternatives-2026-shutdown
- https://aimonetizelab.com/sora-ai/
- https://media.brain-market.com/short-ai-brain/
- https://media.brain-market.com/ai-history-brain/
- https://openai.com/index/sora-2/
- https://taskhub.jp/useful/sora2-shouyou-riyou/
