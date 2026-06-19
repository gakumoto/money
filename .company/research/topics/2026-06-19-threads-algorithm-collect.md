---
created: "2026-06-19"
topic: "Threads アルゴリズム"
status: completed
tags: ["weekly-collect", "threads-algorithm"]
sources: 8
post_ideas: 8
---

# Threads アルゴリズム 最新リサーチ (2026-06-19)

## 全体サマリ (3行)
- **初動30分のリプライ速度**が最強シグナル。「30分で20リプ」が「24時間で50リプ」より配信が爆発する。
- **「Dear Algo」が2026年2月正式リリース**。ユーザーが For You に「もっと/減らす」を直接指示できる。効果は約3日で減衰。
- **ニッチ一貫性**がアカウント評価の前提に。雑多投稿は「専門家不明」と判定され配信減。

---

## 集めた一次情報

### 1. 初動 reply velocity モデル: 「30分で20リプ」が決定窓
- ソース: https://recurpost.com/blog/threads-algorithm/
- 公開日: 2026-04 系（継続更新）
- 要点:
  - 「投稿後30分で20リプ」のほうが「24時間で50リプ」より積極配信される
  - "early engagement matters more than cumulative engagement" — 累積より初速が重い
  - thoughtful reply（中身ある返信）と滞在時間が passive view より重く評価される
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threadsで『24時間で50リプ』より『30分で20リプ』のほうが伸びる仕様になった。投稿時間より初動の30分どう動けるかで決まる」

### 2. 「Dear Algo」2026年2月正式リリース・効果3日減衰
- ソース: https://blacktwist.app/blog/threads-engagement-bait
- 公開日: 2026-02（リリース日）
- 要点:
  - "Dear Algo" は For You に「これ見せて/これ見たくない」を直接指示する機能
  - 指示の効果は約3日で減衰してリセット
  - 自分のフィードを「読みたい人だけ」に整える運用で、投稿者側のリーチ前提も変わる
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Threadsの『Dear Algo』、効果は3日で消える設計だった。一度設定して放置じゃ意味ない。週2回チューニングが現実解」

### 3. エンゲベイト返信のダウンランクが本格化
- ソース: https://recurpost.com/blog/threads-algorithm/, https://blacktwist.app/blog/threads-engagement-bait
- 要点:
  - "Nice post" や絵文字だけの返信は down-rank 対象
  - 「いいねしてください」「フォローしてください」も同様に評価減
  - Meta は「本物の往復会話」だけを評価対象にする方向へチューニング継続中
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「『ナイスポスト』『🔥』だけの返信、もうアルゴリズムが弾いてる。返信稼ぎのつもりが自分の投稿のスコアも落とす」

### 4. リンク評価の反転 (Mosseri 確認)
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works
- 要点:
  - 過去の「リンク投稿はペナルティ」が反転。Mosseri 本人が「URL付き投稿の評価を引き上げた」と明言
  - 同時に「リンクだけポイ投げ」はエンゲベイト扱いで別途減点
  - 結論: 1投稿1リンクで本文の文脈と接続している場合のみ評価される
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「Threadsで『URL貼ると伸びない』はもう古い。Mosseriが評価を引き上げた。ただし"URLだけポイ投げ"は逆に減点される設計」

### 5. ニッチ一貫性: AI がアカウントをテーマ・グルーピング
- ソース: https://mangaiti.com/threads-growth-2026/
- 要点:
  - 2026 年から AI が「アカウント=何の専門家か」をテーマで自動グルーピング
  - 雑多投稿は「何の専門家か分からない」判定→配信減
  - 1アカウント1テーマで投稿一貫性を保つほど Stage 2→3 への昇格率が上がる
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「Threads、雑多投稿してる人ほど伸びない設計に変わってる。AI が『この人何の専門家?』を判定するから、テーマブレが致命傷になる」

### 6. タグ機能は1投稿1個まで・本文文脈の DeepText 解釈
- ソース: https://ebiz-create.co.jp/emagazine/1230/
- 要点:
  - 公式タグ機能は1投稿1個までの仕様
  - 本文中の `#` 連打はスパム判定リスク
  - DeepText が本文の文脈を直接読むので、タグより本文に固有名詞・数字を入れたほうが配信が伸びる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threadsで#を5個6個並べてる人、もうアルゴリズム的にスパム判定されてる。タグは1個まで。本文に固有名詞入れるほうがDeepTextに刺さる」

### 7. 「フォロー優先・コールド推薦減」の2025リバランス継続
- ソース: https://recurpost.com/blog/threads-algorithm/
- 要点:
  - 2025 年に Meta が「フォロー中アカウントの表示を増やし、コールド推薦を減らす」方向で再調整
  - 2026 年もこの方向は維持。「初対面ユーザーのバズ」より「既存フォロワーとの会話継続」が評価軸
  - 新規流入は「既存フォロワーが返信した投稿のリプ欄」から発生する設計に
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「Threadsでフォロワー伸びない人、コールド配信狙いすぎ。今は『既存フォロワーが返信したリプ欄』から新規が来る設計。先に味方を温めたほうが早い」

### 8. いいね100/返信0 < いいね30/返信20 の比率原則
- 一次ソース: https://mangaiti.com/threads-growth-2026/, https://addness.co.jp/media/threads-algorithms/
- 要点:
  - 「いいね100/返信0」の投稿より「いいね30/返信20」の投稿のほうがおすすめ表示される
  - 「いいねください」より「コメントで意見教えて」の CTA のほうが配信が伸びる
  - 「会話のキャッチボール」が滞在時間を伸ばす→アルゴリズム評価がさらに上がる正のループ
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「いいね100/返信0より、いいね30/返信20のほうが伸びる仕様。『いいねください』はもう罠。『コメントで意見教えて』のほうが配信3倍違う」

---

## 既存メモリとの整合性チェック

- ✅ `2026-06-16-threads-algorithm-collect.md`（初動30分・返信velocity・Dear Algo）→ 完全に一致。継続して同じ方向の運用が正解
- ✅ `buzz-element-templates.md`（命令型・2-4行）→ 「コメントで意見教えて」型 CTA と一致
- ✅ `threads-deletion-risk.md`（9:1 / リンク日2回まで）→ 「リンクだけポイ投げ」が減点される今回の発見と整合
- ⚠️ `note-funnel-playbook.md` → URL の扱いを「リンクだけポイ投げは別途減点」で補強したい（次回更新候補）
- ✅ `hit-pitch-formula.md`（自分は何者か×気づき）→ ニッチ一貫性ルールが追い風

## 注目: 即投稿化推奨トピック

**「Dear Algo は3日で減衰」** — 数字が一つ、運用が変わる気づき、競合が知らない情報。昼進捗型または夕失敗型の即下書きに向く。

次点候補: **「いいね100/返信0 < いいね30/返信20」** — 比較数字一発で「いいねください」CTA を直接否定できる。夜振り返り型に。

---

## Sources (一次)
- [RecurPost: Meta Threads Algorithm Explained for Better Reach in 2026](https://recurpost.com/blog/threads-algorithm/)
- [PostEverywhere: How the Threads Algorithm Works in 2026 (3x Reach)](https://posteverywhere.ai/blog/how-the-threads-algorithm-works)
- [Postory: What's Actually Working on Threads in 2026](https://postory.io/blog/what-works-on-threads-2026)
- [Blacktwist: Engagement Bait on Threads — What Works in 2026](https://blacktwist.app/blog/threads-engagement-bait)
- [Metricool: How Does The Threads Algorithm Work in 2026?](https://metricool.com/threads-algorithm/)
- [Miraflow: Threads Algorithm 2026 — How to Grow on Meta's Text Platform](https://miraflow.ai/blog/threads-algorithm-2026-how-to-grow-meta-text-platform)
- [AdnessLab: 2026年最新Threadsアルゴリズム完全攻略](https://addness.co.jp/media/threads-algorithms/)
- [eBIZ Create: 2026年Threadsアルゴリズム運用ノウハウ完全ガイド](https://ebiz-create.co.jp/emagazine/1230/)
- [Mangaiti: 2026年版Threadsの伸ばし方](https://mangaiti.com/threads-growth-2026/)
