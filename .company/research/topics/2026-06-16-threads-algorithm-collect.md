---
created: "2026-06-16"
topic: "Threads アルゴリズム"
status: completed
tags: ["weekly-collect", "threads-algorithm"]
sources: 8
post_ideas: 8
---

# Threads アルゴリズム 最新リサーチ (2026-06-16)

## 全体サマリ (3行)
- 2026 年の Threads は**「返信の連鎖速度」**を最強シグナルに据えた。いいねは弱い。
- Mosseri 本人が「全リプライの総和 ≒ 全投稿の総和」と公言。**投稿より返信が伸ばす**。
- **早期エンゲージメント（投稿後 30〜90 分）** が勝負。後追いの伸びは効かない。

---

## 集めた一次情報

### 1. Buffer 12.8 万件分析: リプライ返信でエンゲ +42%
- ソース: https://buffer.com/resources/threads-comments-engagement/
- 公開日: 2026-02-24
- 要点:
  - 12.8 万件以上の Threads 投稿を分析、約 3 分の 2 のアカウントでリプライ返信がエンゲ向上に寄与
  - **+42% は全プラットフォーム最高**（LinkedIn +30、Insta +21、FB +9、X +8、Bluesky +5）
  - Mosseri 引用: "The sum of all your replies is about as valuable as the sum of all your posts"
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threads で伸びない人の共通点。投稿しかしてない。返信したほうが 42% 伸びるってBuffer のデータが出てる」

### 2. 会話 Velocity モデル: 30 分で 50いいね > 24時間で100いいね
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works
- 公開日: 2026-03-23 (2026-05 更新)
- 要点:
  - "50 likes in 30 mins outperforms 100 likes over 24 hours" — 投稿後 30〜90 分が決定窓
  - Mosseri 確認: URL付き投稿は本文のみより +17% エンゲ（過去のリンクペナルティを反転）
  - 画像 +60%、動画 +59%、リンク +17%、テキストのみ＝ベースライン
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「朝に投稿して放置するの一番もったいない。30 分で 50いいね > 24時間で 100いいね、が今のThreads」

### 3. 4ステージ評価モデル (AdnessLab)
- ソース: https://addness.co.jp/media/threads-algorithms/
- 公開日: 2026-01-16 (2026-02-25 更新)
- 要点:
  - Stage 1: フォロワーの一部に配信→1時間以内の初動反応で次へ
  - Stage 2: 全フォロワーに展開→継続反応が必要
  - Stage 3: 非フォロワー（発見）へ→トピックタグ1つだけ
  - Stage 4: 外部プラットフォーム共有（自然発生のみ、狙わない）
  - 推奨頻度: 週2〜5回（Meta 推奨）、テキストは「アルゴリズムが投稿の地図を読むための言語」
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「Threads には4ステージあって、1ステージ目（1時間以内の初動）で死ぬ投稿が全体の8割」

### 4. 伸びる型 / 伸びない型 (Postory 2026-04)
- ソース: https://postory.io/blog/what-works-on-threads-2026
- 公開日: 2026-04-15
- 要点:
  - **伸びる**: 質問型 / 画像+短いキャプション / 個人的な気づき / リプライチェーン（自己返信で継続）/ 1〜2文の単独投稿
  - **伸びない**: マイクドロップ型強い意見 / 長編スレッド（講演に見える）/ 純粋な自己宣伝 / エンゲベイト / テキストのみ視覚なし
  - 投稿は「返信できる時間帯」に。**60〜90分の初動枠**で本人がリアクションを返せること
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threads で『マイクドロップ』した瞬間アルゴリズムが冷える。返事を呼ばない断定は罰されるようになった」

### 5. 「Dear Algo」明示パーソナライズ機能 (2026 新)
- ソース: https://recurpost.com/blog/threads-algorithm/, https://embedsocial.com/blog/new-threads-features-2026/
- 要点:
  - 2026 年に "Dear Algo" 投入。ユーザーが For You に「もっと/減らす」を直接指示できる
  - 2025 夏に Fediverse フィード（Mastodon等連携）を追加
  - 2025年内に Meta は **「フォロー中アカウント優先・コールド推薦を減らす」** 方向に再調整
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Threads の『Dear Algo』知ってる？For You に直接『これ見せて』『これ見たくない』が言える機能が今年から入った」

### 6. リプライ＞投稿の運用論 (Mosseri)
- ソース: https://www.spicycreatortips.com/replying-to-your-threads-comments-can-boost-engagement-by-42/
- 要点:
  - Mosseri 本人発言: 「投稿するより返信したほうが伸びる」
  - エンゲベイト返信（"Nice post!" や絵文字のみ）は down-rank 対象に
  - 「会話の往復回数」が直接シグナル化
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「フォロワー欲しい人ほど投稿してる。Mosseri が公式に『返信＞投稿』って言ってるのを知らない」

### 7. ハッシュタグ衰退 / DeepText 文脈理解
- ソース: https://ebiz-create.co.jp/emagazine/1230/, https://mangaiti.com/threads-growth-2026/
- 要点:
  - ハッシュタグより「本文の文脈」を DeepText が読む
  - トピックタグは 1 つだけ、それ以上は逆効果
  - 推奨アクション「保存して」「あなたの意見も返信で」が「いいねください」より有利
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threads でタグ盛ってる人、もう逆効果。本文の文脈を AI が読んでる。タグは1個まで」

### 8. リーチ率データ
- ソース: https://posteverywhere.ai/blog/how-the-threads-algorithm-works, https://miraflow.ai/blog/threads-algorithm-2026-how-to-grow-meta-text-platform
- 要点:
  - 1万フォロワー以下アカウントのリーチ率 8〜12%（X の平均より高い）
  - 中央値エンゲ率 6.25%（X の 3.6% より 73.6% 高い）
  - MAU 4.5億（2026 年初）、DAU は 1.415億で X を超過（2026-01）
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「フォロワー千人いない人ほど今 Threads やったほうがいい。リーチ率 8〜12%、X の倍以上残ってる」

---

## 既存メモリとの整合性チェック

- ✅ `buzz-element-templates.md`（未完語尾・命令型・2-4行）→ Postory の「1〜2文の短い投稿が強い」と完全一致
- ✅ `threads-deletion-risk.md`（9:1 ルール）→ 「投稿より返信」が Meta 公式論理と一致、リスク方向と矛盾なし
- ✅ `hit-pitch-formula.md`（自分は何者か×気づき）→「個人的な気づき」が伸びる型と一致
- ⚠️ `note-funnel-playbook.md`（URLは減衰）→ **要更新**。Mosseri が URL を +17% に再評価したのは 2025 年なので、過度な URL 警戒は古い。ただし「毎回外部 URL」は依然 NG（エンゲベイト判定）

## 注目: 即投稿化推奨トピック
**「30 分で 50いいね > 24時間で 100いいね」** — 数字一発、Mosseri ソース、運用が変わる気づき。朝学び型の即下書きに最適。

---

## Sources (一次)
- [Buffer: Replying to Threads Comments +42%](https://buffer.com/resources/threads-comments-engagement/)
- [PostEverywhere: How the Threads Algorithm Works in 2026](https://posteverywhere.ai/blog/how-the-threads-algorithm-works)
- [Postory: What's Actually Working on Threads in 2026](https://postory.io/blog/what-works-on-threads-2026)
- [AdnessLab: 2026年最新Threadsアルゴリズム完全攻略](https://addness.co.jp/media/threads-algorithms/)
- [RecurPost: Meta Threads Algorithm Explained 2026](https://recurpost.com/blog/threads-algorithm/)
- [EmbedSocial: New Threads Features in 2026](https://embedsocial.com/blog/new-threads-features-2026/)
- [Spicy Creator Tips: Replying Boosts Engagement 42%](https://www.spicycreatortips.com/replying-to-your-threads-comments-can-boost-engagement-by-42/)
- [eBIZ Create: 2026年Threadsアルゴリズム運用](https://ebiz-create.co.jp/emagazine/1230/)
