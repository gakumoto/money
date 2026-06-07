---
title: Discord Bot 運用ロードマップ
created: 2026-06-07
audience: オーナー (am.0719.5220@gmail.com)
purpose: Discord Bot 14+ コマンドの使い分け / 朝昼晩のフロー / 段階別習熟プラン
---

# Discord Bot 運用ロードマップ

仮想会社の指令室を「PC の Claude Code」から「スマホの Discord」に移すための実用ガイド。
スマホで Discord 開けば、寝起きで投稿レビューも、外出先でネタ追加も、夜のリサーチ起動も全部できる状態を目指す。

---

## 全体地図

### 18+ コマンドのカテゴリマップ

```
[投稿生成系]              [レビュー・配信系]         [素材・ネタ系]
/create_post              /review                     /idea
/create_post_from_idea    /post                       /ideas
/post_bulk                /queue                      /generate_ideas
/morning                  /list                       /idea_use
                          /feedback
                                                      [リサーチ系]
[記事生成系]              [日報系]                    /research_youtube
/generate_article         /report                     /research_web
                          /report_add                 /research_self
[管理系]                  /report_close               /competitor_post
/status                   /reports                    /watchlist
/sync                     
/retry_post               
/run task:<choice>        [ガイド]
                          /help [トピック選択]
```

### 1 つだけ覚えるなら

`/help` 。全 7 トピック (基本 / レビュー / ネタ / 日報 / 朝フロー / ライティング / リスク / 24h 稼働 / トラブル) のガイドが Discord 内で見える。迷ったらまずこれ。

---

## 1 日の標準フロー (理想形)

### 🌅 朝 (起きた時 / 通勤前)

**目的**: 昨日の結果確認 → 今日の予定セット → 投稿レビュー&キュー入れ

```
1. /morning              ← 朝礼ダッシュボード
                          (昨日の伸び / 今日の予定 / 推奨アクション)
                          ※ 寝起きの 1 タップで状況把握

2. /review               ← 未レビューの下書きを順番表示
                          ✅ で承認 → /queue に流れる
                          ✏️ で編集 → 部分修正
                          🔄 で再生成 → AI が書き直し
                          ❌ で却下 → rejected/ に

3. /list                 ← 今日のキューを確認
                          配信時刻が問題ないか目視チェック
```

朝のフローを **5 〜 10 分で完了**できれば運用は回る。

### 🌞 昼 (休憩中 / 移動中)

**目的**: 思いつきをロスせず蓄積 / 追加の投稿生成

```
1. /idea <思いついたこと>     ← 即蓄積 (1 行で OK)
   例: /idea "通勤中、Claude Code が指示なしで動いてる時の不思議さ"

2. /create_post <topic>      ← その場で投稿 1 本生成したい時
   例: /create_post "AI が勝手に投稿作る違和感について"

3. /post <text>              ← 即時投稿したい時 (キューを通さない)
                              ※ オーナー限定・緊急時用
```

「ネタは思いついた瞬間に `/idea` で投げる」が肝。後で AI が `/create_post_from_idea` で消化する。

### 🌙 夜 (寝る前)

**目的**: 1 日の振り返り / 明日の準備

```
1. /report                ← 今日の日報を表示 (なければ作成)
2. /report_add <section> <content>  ← セクション別に追記
   例: /report_add "学び" "Threads は朝の弱さ枕詞が一番伸びる"
3. /report_close [comment]          ← 締めコメント付きで完了マーク

4. (自動) 02:00 に nightly_pipeline.py が走る
          → /threads-daily-run スキルを実行
          → 明朝までに 10 本の下書き完成
          ※ PC が起動してる前提
```

`/report_add` を 1 日 3〜5 回繰り返すと、note 記事の素材が勝手に溜まる。

### 📅 週次 (週末・気が向いた時)

**目的**: パフォーマンス分析 / リサーチ蓄積 / 戦略見直し

```
1. /research_self                  ← 自分の伸びた投稿を AI 分析
2. /research_youtube <url>         ← 同業 YouTuber から字幕→要約→ネタ抽出
3. /research_web [theme]           ← WebSearch でトレンド収集
4. /competitor_post <user> ...     ← 他人の伸びてる投稿を登録 → 学習素材化
5. /watchlist                      ← 自動リサーチ対象を確認・調整
6. /generate_article [date]        ← 1 週間分の日報・実績から note 記事自動生成
7. /reports                        ← 過去 7 日の日報一覧で振り返り
```

---

## 段階別 習熟プラン

### Phase A: 最初の 1 週間 (Day 1〜7)

**目標**: スマホで「レビューと配信」ができる状態

覚える必須コマンド (5 個だけ):

| コマンド | 用途 | 頻度 |
|---------|------|------|
| `/help` | 迷ったら | 都度 |
| `/morning` | 朝の状況把握 | 1 日 1 回 |
| `/review` | 下書き承認 | 1 日 1〜2 回 |
| `/queue` | 配信時刻指定 | review 後に都度 |
| `/status` | 現状サマリー | 気が向いた時 |

Phase A の完成系: **朝 5 分で投稿配信の準備が終わる**。

### Phase B: 1 〜 4 週目 (Day 8〜30)

**目標**: ネタ蓄積と日報運用が回る状態

追加で覚える (5 個):

| コマンド | 用途 |
|---------|------|
| `/idea <内容>` | 思いつき即蓄積 |
| `/ideas` | 蓄積一覧を見る |
| `/create_post <topic>` | 単発で 1 本生成 |
| `/report` `/report_add` | 日報運用 |
| `/feedback <category> <内容>` | AI に育成指示 |

Phase B の完成系: **AI スタッフが日々精度上がっていく感覚を持てる**。`/feedback` の蓄積が効いてくるのがこのフェーズ。

### Phase C: 2 ヶ月目以降

**目標**: 半自動運用 / リサーチ起点で新ネタを自動生成

追加で覚える (応用系):

| コマンド | 用途 |
|---------|------|
| `/post_bulk count:N theme:〇〇` | テーマ指定で N 本一気生成 |
| `/create_post_from_idea <id>` | 蓄積ネタから 1 本消化 |
| `/generate_ideas count:N` | AI にネタを N 本自動生成させる |
| `/research_youtube <url>` | YouTube から学ぶ |
| `/research_self` | 自分の数字から学ぶ |
| `/generate_article [date]` | note 記事を日報から自動生成 |
| `/run task:<choice>` | 各種パイプライン即実行 |

Phase C の完成系: **「自分が休んでる時間も会社が回ってる」状態**。

---

## 判断フロー (どのコマンドを使うか)

### 「投稿を作りたい」時

```
ネタが明確？ ── Yes ── 1 本だけ? ── Yes → /create_post <topic>
                                  └ No  → /post_bulk count:N
                  └ 蓄積ネタから? → /create_post_from_idea <id>
       └ No → 朝のルーチン? ── Yes → /morning (一括フロー)
                          └ No → /generate_ideas で先にネタ生成
```

### 「思いついた」時

```
すぐ投稿? ── Yes → /create_post <topic>
       └ No → /idea <内容>     (後で消化)
```

### 「何かを確認したい」時

```
現状全体?      → /status
今日のキュー?  → /list
未レビュー?    → /review
過去日報?      → /reports
蓄積ネタ?      → /ideas
```

### 「リサーチしたい」時

```
特定 YouTuber  → /research_youtube <url>
ジャンルトレンド → /research_web [theme]
自分の数字      → /research_self
他人の伸び投稿  → /competitor_post <user> <text> <why>
定期チェック   → /watchlist
```

### 「不調 / トラブル」時

```
投稿失敗?      → /retry_post
コマンド消失?  → /sync
パイプライン?  → /run task:nightly
トークン切れ?  → /run task:token_refresh
```

---

## 守るべきルール (アンチパターン)

### ❌ 絶対やらないこと

- **`/post <text>` で長文を即時投稿**: 危険ワード・絵文字ルール違反のリスク。必ず `/create_post` で生成 → `/review` → `/queue` の経路を通す
- **`/feedback` で曖昧な指示**: 「もっと良くして」「フックを効かせて」は意味なし。「冒頭1行目に固有名詞がない、ユニクロみたいな実在企業名に置き換えて」のように **具体的に**書く
- **/post_bulk で同じテーマ連発**: 10 本中 8 本が「AI 副業」だと飽きられる。テーマを変えて分散
- **危険ワード連投**: 「月 100 万」「月 7 桁」を売り文句で使わない (詳細: `/help risk`)

### ✅ 基本姿勢

- 迷ったら `/help` で該当トピック確認
- 投稿生成 → 必ず `/review` でチェック (AI 出力を信用しすぎない)
- 良い反応の投稿は `/feedback "良かった例" "..."` で蓄積 (AI が学習)
- 悪い反応も `/feedback "悪かった例" "..."` で蓄積

---

## 「半自動化」の最終形

このロードマップを完走すると、**1 日の労働時間が 30〜60 分**になる:

| 時間帯 | やること | 所要時間 |
|--------|---------|---------|
| 朝 | `/morning` → `/review` → `/queue` | 5〜10 分 |
| 昼 | 思いついたら `/idea` (Discord 通知から即入力) | 1 〜 2 分 × 数回 |
| 夜 | `/report_add` で 1 行ずつ追記 | 5 分 × 数回 |
| 週末 | `/research_self` + `/generate_article` | 30 分 |

**残りの時間は本業 / 家族 / 別のクリエイティブに使える**。これがこのシステムの目標。

---

## 参考ファイル

- 詳細実装: `scripts/discord_bot.py`
- セットアップ: `scripts/SETUP.md` Section 6
- ライティングルール: `.company/CLAUDE.md`
- 原理集: `.company/marketing/writing-principles.md` (今日追加)
- フィードバック蓄積: `.company/marketing/feedback/gaku_ai_life.md`
- 削除リスク管理: `.company/CLAUDE.md` の「アカウント削除リスク管理」
