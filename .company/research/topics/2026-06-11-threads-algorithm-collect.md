---
created: "2026-06-11"
topic: "Threads アルゴリズム（差分収集）"
status: completed
tags: ["weekly-collect", "threads-algorithm"]
sources: 7件
post_ideas: 7件
---

# Threads アルゴリズム差分収集 2026-06-11

6/8 の `2026-06-08-threads-algorithm-collect.md` で「会話速度」「Mosseri reply more than post」「Dear Algo」「4 配信ステージ」「ニッチ一貫性」「いいね回り無効化」「昼夜評価軸」を網羅済み。
今回は **6/8 に含まれていない差分情報** に絞って収集。dwell time / シャドウバン3原因 / Your Algo 拡張 / Mosseri 年末メモ / 数字比較が中心。

---

### dwell time 8秒 — Threads が裏で見ている「読み止まり」シグナル
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works
- 公開日: 2026 年（記事更新）
- 要点:
  - 投稿に8秒以上滞在＝強いポジティブシグナルとしてカウント
  - スクロールせずに2.1秒で止まる＝弱いポジティブ（passive interest）として加算
  - 90分以内の再エンゲージメントも別シグナルとして評価
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「Threads は『8秒止まったか』を裏で測ってる」「スクロール途中で2秒止まっただけで採点されてる事実」

---

### 10件の深いリプライ > 100件の浅いいいね — 数字で示された配信差
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works
- 公開日: 2026 年（記事更新）
- 要点:
  - Threads は「いいね最大化」ではなく「会話最大化」を目的関数に置いている
  - 「いいね100・返信0」より「いいね30・返信20」のほうがおすすめ配信される（日本ブログ複数で同じ事例）
  - 投稿後 30〜60分の engagement velocity で勝敗が決まる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「いいね100より返信20が勝つ理由」「Threadsの目的関数を勘違いしてると一生伸びない」

---

### シャドウバンの3大原因 — 短時間大量アクション/コピペ連投/外部リンク過多
- ソース: https://mangaiti.com/threads-shadowban-check/ , https://fy-enterprise.com/contents/threads-shadowban/
- 公開日: 2026 年（記事更新）
- 要点:
  - 「アプリ外に逃がしたくない」プラットフォームの方針で外部リンク過多は配信減
  - Amazon・楽天アフィリリンク直貼りはシャドウバン誘発（明示）
  - ツール的な高速いいね・フォローはスパム判定
  - 回復策は **24〜48時間の完全放置** が唯一の確実手段
- 投稿アイデア:
  - 型: 夕失敗型
  - 切り口: 「アフィリリンク直貼りした次の日に配信が消えた話」「シャドウバンを治す唯一の方法は『48時間触らない』」

---

### 投稿後30〜60分が勝負 — engagement velocity の具体ウィンドウ
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works , https://addness.co.jp/media/threads-algorithms/
- 公開日: 2026 年（記事更新）
- 要点:
  - 配信判定の最重要因子は「投稿後 30〜60分の蓄積スピード」
  - Stage1 抜けはこの初動次第（6/8 ノートの「4 配信ステージ」と接続）
  - 投稿者の自リプライも初動内に行うと「会話の深さ」シグナルとして加算
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「投稿後30分にスマホを触れるかどうかで配信が3倍変わる」「初動60分を捨てる人は投稿する意味がない」

---

### Your Algo が英語圏グローバル展開 — Reels タブから直接チューニング可能に
- ソース: https://www.threads.com/@mosseri/post/DTdelJPj3yC
- 公開日: 2026 年初頭（Mosseri 公式投稿）
- 要点:
  - Reels タブからトピックを追加/削除して For You を直接チューニングできる仕様を英語圏全体に拡張
  - 年初限定で「2026 年に見たいトップ3トピック」を直接指定可能
  - 6/8 ノートの "Dear Algo" は文字投稿経由、Your Algo は UI 直叩きで別系統
  - 日本未対応（英語圏先行）
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「ユーザーがアルゴリズムを直接いじれる時代がもう来てる」「英語圏で先行する SNS チューニング機能、日本は半年後にくる」

---

### Mosseri 年末メモ — クレデンシャル＆オリジナル投稿の優遇方針
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works
- 公開日: 2026 年初頭（Mosseri 年末メモ言及）
- 要点:
  - 2026 年は「credibility signals（信頼度シグナル）」を強化すると公式言及
  - オリジナル投稿（コピー・転載でないもの）を優先表示する方向
  - リサイクル投稿（他SNSからの転用文）は配信が落ちる傾向
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Mosseri が年末メモで宣言した『信頼できるアカウント』優遇」「X からコピペして Threads に貼る人が今年から伸びなくなる」

---

### Instagram プロフィール閲覧回数まで Threads のシグナルになっている
- ソース: https://metricool.com/threads-algorithm/ , https://buffer.com/resources/threads-algorithm/
- 公開日: 2026 年（記事更新）
- 要点:
  - Threads のランキングは Instagram 行動と結合: 「相手の Instagram プロフィールを何回見たか」を投稿表示の重みに使う
  - プロフィール訪問は「high-friction action」として高評価
  - 結論: Threads と Instagram のプロフィール文・アイコンは揃えるべき（リンクの心理的摩擦を下げる）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threadsの裏で Instagram の閲覧履歴まで使われてる事実」「プロフィールが Threads と Instagram で違う人は損してる」

---

## 結論

2026 年 6 月時点で 6/8 にない差分情報は以下7点に集約できる:

1. **8秒 dwell time** が裏シグナル
2. **「いいね100・返信0」より「いいね30・返信20」** が配信される具体比較
3. **シャドウバン3原因（大量アクション/コピペ/リンク過多）と48時間放置**
4. **投稿後30〜60分の engagement velocity ウィンドウ**
5. **Your Algo の英語圏全展開**（Dear Algo とは別系統）
6. **Mosseri 年末メモ: credibility & original content 優遇**
7. **Instagram プロフィール訪問が Threads シグナル**

## ネクストアクション

- 即投稿化推奨: 「いいね100・返信0より、いいね30・返信20が勝つ」（朝学び型 / 数字で語れる）
- 「投稿後30分にスマホ触れるかどうかで配信3倍」もシンプルで強い（昼進捗型）
- gaku_ai_life の Instagram プロフィール統一が未対応なら、ここを揃えるだけで Threads のシグナルが増える（運用 TODO）
