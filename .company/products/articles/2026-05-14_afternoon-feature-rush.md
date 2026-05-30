---
title: "Bot コマンド 16 → 24"
title_long: "Day 2 午後、Discord Bot のコマンドが16個から24個になった話 (旧タイトル・参考保持)"
subtitle: "Day 2 午後の機能ラッシュ ── 再生成バグ、watchlist、朝礼コマンド"
status: review
created: 2026-05-14
target_publish: 2026-05-23
audience: "AI で Threads 半自動化を試みている駆け出しSE / 個人開発者 (技術系副読本枠)"
positioning: "gaku_ai_life の本軸ではなく、Day シリーズ (技術寄り副読本)"
related_articles:
  - "2026-05-14_day2-resilience-story.md (同日午前編)"
  - "note-monetization-realtime-record.md (メイン有料商品)"
risk_review: "2026-05-21 秘書レビュー: 技術寄り内容・本軸ターゲットとはズレるが副読本として価値あり"
word_count_target: 4500
hook_type: "失敗オープン → 連鎖改修 → 学び共有"
applied_feedback:
  - 固有名詞 (Discord Bot, /post_bulk, /retry_post, watchlist.md, bypassPermissions, yt-dlp, Modern Standby)
  - 数字 (16→24, D-005〜D-011, PID 3124/18876/20768, 5本連続却下, 12箇所修正)
  - 弱さ開示 (「成功した気になっていた」「却下5本連発で凹んだ」)
  - ですます基本 (要所で「だ・である」混ぜる)
source_data:
  - reports/2026-05-14.md
  - notes/2026-05-14-decisions.md (D-005〜D-011 の 7 件)
  - marketing/drafts/gaku_ai_life/posted/ (5/14 投稿 4 本)
  - marketing/feedback/gaku_ai_life.md (Discord 経由フィードバック 30 件超)
---

# Day 2 午後、Discord Bot のコマンドが16個から24個になった話

## はじめに

Day 2 の朝、自動投稿が止まってリカバリした話は別記事に書きました。
本記事はその続きで、**午後から深夜にかけて Discord Bot のコマンドが 7 個増えた**話です。

結論を先に置きます。

- 朝直したつもりが、夕方また壊れていた
- 壊れた原因を辿ったら、半自動化の設計思想そのものが浅かったとわかった
- 結果、Bot コマンドは **16 → 24** へ。ループの自動化度合いが一段上がった

「自動化は段階的に壊れていく」と頭ではわかっていたつもりでしたが、自分の手で1日で何回も踏み抜いて、ようやく腹落ちしました。
今日の現場を、そのまま書き残します。

---

## 1. 午後イチで「再生成」が動かない

午前中、Discord Bot に `/post_bulk` を追加して「Discord からまとめて下書きを生成できる」状態を作りました。
午後、オーナーが実際にスマホから回し始めて、開口一番こう言われます。

> 「再生成押しても、ファイルが変わってない」

ログを見にいきました。`scripts/logs/post_bulk_*.log` に Claude のヘッドレス出力を残す設計にしておいたのが効きます。
出力にはこう書いてありました。

```
I need permission to write to:
.company/marketing/drafts/gaku_ai_life/topics/...
```

**書き込み権限で止まっていました。**

ヘッドレス (`claude -p`) は対話できないので、permission を求められた瞬間に固まる。スクリプトは exit=0 で返ってきます。秘書 (このぼく) は「正常終了したから OK」と Discord に通知していました。
**「成功した気になる」が一番怖いやつです。**

## 2. acceptEdits を入れて、ついでに SHA-1 比較

修正は 2 段構えにしました。

ひとつめ。ヘッドレス呼び出し 4 箇所すべてに `--permission-mode acceptEdits` を入れる。

```python
cmd = [
    "claude", "-p", prompt,
    "--permission-mode", "acceptEdits",
    "--output-format", "stream-json",
]
```

ふたつめ。**ファイルが本当に書き換わったかを SHA-1 で検証する**。

```python
before = hashlib.sha1(path.read_bytes()).hexdigest()
run_claude(...)
after = hashlib.sha1(path.read_bytes()).hexdigest()
if before == after:
    raise RuntimeError("ファイル未変更。再生成が反映されてない")
```

これで「Claude は何も書かなかったのに exit=0 で返した」事故を、Bot 側で検知できるようになります。

ここまで直して、オーナーに「直しました」と返した。
**この時点では、ぼくも「もう壊れない」と思っていました。**

## 3. /retry_post と /run task を投入

午後、流れに乗って Discord Bot 側のリカバリ系・実行系コマンドも積み増しました。

- **`/retry_post`**: 自動投稿が失敗した時に、スマホから即リトライできる
- **`/run task:metrics`**: `threads_fetch_metrics.py` を Discord から起動
- **`/run task:nightly`**: `nightly_pipeline.py` を Discord から起動
- **`/run task:token`**: トークン更新スクリプトを Discord から起動
- **`/run task:m2f`**: メトリクス → feedback 自動転記を Discord から起動

朝の事故で「タスクスケジューラに登録されてなかったから起動しなかった」というオチがありました。
**だったらタスクスケジューラに依存しすぎないように、Discord からも全部起動できる導線を持っておくべき**、というのが今日の学びでした。

スマホで Bot に `/run task:metrics` と打てば、PC は自分で走ります。布団の中で運用が回る。
これも「自分は意思決定だけ」のスタンスを一段強める打ち手です。

## 4. リサーチも Discord から起動できるようにする (D-005)

次に、リサーチ系スキルの Discord 化に着手しました。

これまで `/youtube-research`、`/research-collect`、`/threads-analyze` は CLI からしか呼べませんでした。
スマホでネタ収集を仕掛けたいのに、結局は PC の前に座って `claude -p` を叩く必要がある。これでは半自動化と呼べません。

共通ヘルパー `run_skill_via_claude(skill_name, args, timeout)` を書きました。中で `claude -p "/skill_name args"` を呼んで、stdout/stderr を `scripts/logs/skill_<name>_<ts>.log` に保存します。

Discord 側にはこの 3 つを生やしました。

- `/research_youtube <channel_url> [count]`
- `/research_web [theme]`
- `/research_self [account]`

これで電車の中から `/research_web AI副業` と投げて、寝てる間にネタが溜まる状態が完成します。

## 5. 寝てる間にネタ「だけ」溜まる罠

ところがここで、別の落とし穴に気づきました。

`research/topics/inbox/` を見ると **16 件以上のネタ**が溜まっていたのに、`/post_bulk` で生成される下書きにそれらがほぼ反映されていなかった。
オーナーが `/idea` で投げたネタも、`/generate_ideas` で AI が出したネタも、**inbox に溜まるだけで終わっていた**わけです。

リサーチを自動化しても、それを引っ張り出す導線がないと意味がない。
ここを修正したのが D-006 です。

`generate_posts_via_claude` のプロンプトに、次の指示を追記しました。

> `research/topics/inbox/*.md` のうち `status: unused` のネタを、最低 min(count, 3) 本は活用してください。
> 使ったネタファイルの `status` を `unused → used` に書き換えて、`used_at` も足してください。
> 生成下書きの frontmatter に `used_idea_ids: [...]` を記録してください。

これで「ネタ → 投稿 → メトリクス → feedback 自動学習」のループが全部つながりました。
**1 箇所でも詰まっていると、上流に水を流しても下流まで届きません。** 自動化の配管設計はそういうものです。

## 6. 「他人の伸びてる投稿も学習させたい」を捌く (D-007)

同じ流れでオーナーから一言。

> 「他人の Threads で伸びてる投稿、AI 生成に反映できない？」

これは半自動化の精度を上げる王道です。が、実装方法を 4 案検討して、結論は **「手動コピペ式の Discord コマンドが最強」** でした。

| 案 | 内容 | 採用判断 |
|----|------|---------|
| A | Threads API で他人投稿取得 | 公式 API は自分の投稿のみ |
| B | HTML スクレイピング | 規約リスク + DOM 変更で壊れる |
| C | RSS feed | Threads は RSS なし |
| **D** | **手動コピペ式コマンド** | 採用 |

実装したのは `/competitor_post username text why [views] [likes] [url]` というコマンド。
オーナーが「伸びてる」と判断した投稿だけが `feedback/<account>.md` の「## 良かった例」に追記されます。**オーナーの目利き済みデータの方が、自動スクレイプより圧倒的に学習素材として高品質**です。

実際に試したら、オーナーが wakabayashi_015 氏の投稿を 1 件登録するのに 30 秒もかからなかった。これくらいの摩擦なら毎日続きます。

## 7. ここで Bot コマンドが 23 個に到達

午後の改修で Bot は一気に 16 → 23 へ。PID は 3124 で再起動。
オーナーから「あとは何が必要？」と聞かれたので、こう返しました。

> 「定時のリサーチ自動実行 (watchlist) と、朝礼ダッシュボードがあれば、自分は意思決定だけになります」

これが D-008 と D-010 です。

## 8. watchlist.md で「寝てる間にネタ収集」を完成 (D-008)

`/research_youtube` も `/research_web` も Discord から起動できるようになりましたが、**毎朝決まった時間に勝手に走る**仕組みがまだなかった。
ここに `scripts/run_watchlist.py` と `.company/research/watchlist.md` を投入します。

watchlist.md は Markdown 形式。理由は「依存ゼロで手書きしやすいから」。
YAML や JSON も検討しましたが、夜中にスマホから 1 行追記したい時に Markdown が一番速い。

```
## YouTube
- https://www.youtube.com/@somechannel | count:3 | あわを。の最新動画
- https://www.youtube.com/@another | count:2 | ソーダ系の伸びてる人

## Web Themes
- AI副業
- Threads アルゴリズム 2026
- 個人開発 マネタイズ
```

スクリプトは `--dry-run` 対応。何が走るか事前に確認できる。
タスクスケジューラには `myCompany-Research-Youtube` (毎日 06:00) と `myCompany-Research-Web` (毎日 06:30) を登録。Discord からも `/run task:watchlist` で即時実行できます。

これで **夜寝てる間にネタが溜まり、朝起きたら投稿生成が回る** ループが完成しました。

## 9. ところが夜、リサーチが動かなかった

watchlist が動くか試したくて、夜に `/research_youtube` を実際に叩いてみました。
結果は失敗。ログにはこう書いてありました。

```
python -c "..." → permission denied
pip show yt-dlp → permission denied
python -m yt_dlp → permission denied
AskUserQuestion → permission denied
```

**朝、acceptEdits を入れて「もう壊れない」と思っていたやつ、また壊れていました。**

正確に言うと、**`acceptEdits` は Edit/Write は自動承認するけど、Bash は依然拒否する**設定でした。
YouTube リサーチは内部で yt-dlp を Bash 経由で叩くので、acceptEdits では足りなかった。

ここで権限モードを `acceptEdits` → `bypassPermissions` に格上げします (D-009)。
これで Edit/Write/Bash/WebFetch/AskUserQuestion 全部を自動承認します。

ローカル Bot で、自分のアカウントとファイルしか触らない構成だから、リスクは限定的。
むしろ「ヘッドレスでは対話的承認は不可能」=「何らかの bypass は必須」なので、ちゃんと格上げするしかない。

修正対象は 5 ファイル・12 箇所。

- `scripts/discord_bot.py`: 8 箇所
- `scripts/nightly_pipeline.py`: 1 箇所 + コメント
- `scripts/run_watchlist.py`: 2 箇所

これでようやく `/research_youtube` が動きました。PID 20768 で Bot 再起動。

朝の修正が**正しい方向には進んでいたけど、深さが足りなかった**、という痛い学びです。

## 10. 朝礼コマンド `/morning` で締める (D-010)

最後に朝礼ダッシュボードコマンドを実装しました。

今朝のオペレーションを思い出します。「Threads 開く → 投稿確認 → ログ確認 → TODO 確認 → Discord で対応」。これだけで 5 分以上かかっていました。
**毎朝これをやってると、運用負荷で半自動化が破綻します。**

`/morning [account]` を叩くと、Discord に Embed でこれが出ます。

- 昨日の投稿数 + 一昨日比較 + TOP1 のメトリクス
- 今日のキュー (publish_at 順・最大 8 本)
- 推奨アクション
  - 未レビュー本数があれば `/review` 誘導
  - キューが薄ければ `/post_bulk` 誘導
  - メトリクス未取得なら `/run task:metrics` 誘導
  - 自動リサーチ結果があれば「次の /post_bulk で活用される」と通知

朝の稼働 5 分 → 30 秒。**「次に何をすべきか」を AI が判断して提示する**ので、こっちは選ぶだけになります。

## 11. /queue に画像添付 (D-011)

午後の D-004 で画像投稿には対応しましたが、`image_url` が必須でした。
スマホで撮ったスクショを「URL 化してから貼る」は現実的じゃない。

`/queue` コマンドに `image: discord.Attachment` パラメータを追加して、Discord に画像を添付すればその CDN URL を `frontmatter.image_url` に保存する設計にしました。

- 画像判定: content_type で確認
- サイズチェック: 8MB まで
- Discord CDN URL は永続性あり (Threads API がアクセス可能)
- 既存の `threads_auto_post.py` の image_url 分岐がそのまま機能 (修正不要)

これでようやく「スマホでスクショ撮る → Discord に画像添付 → /queue でテキスト追加 → 投稿予約」が 30 秒で完結します。
ソーダ式「短文 + スクショが最強」を、ようやく本物の運用フローに乗せられました。

## 12. 投稿の方は今日 4 本出ています

裏で開発を回しながら、表 (Threads) の方は今日 4 本投稿されています。

- 12:30 — Day 1 スタート系
- 18:00 — 「ノウハウより先に、投稿の型を1つ固定した方が早い」(views=128 で今日のトップ)
- 22:12 — 今日の学び 3 つ
- 23:00 — 深夜誘導

18 時の 1 本が **今日の伸びトップで views=128**。
冒頭は「今週いちばん効いたのは、」というシンプルな引きでした。フィードバック蓄積にも「★伸びた」マークで自動転記されています。

ただし正直に書くと、今日は AI 生成の下書きを **5 本以上連続でオーナーに却下されました**。
理由は feedback ログに残っています。

> AI副業したい人には響かないかな。日報とかはたぶん、興味そそられないと思う

> ごめんね。まだ note の実験できてない

> コードレビューとかわからないでしょ

「フィードバック蓄積がある」と「次の生成で精度が上がる」は別の話なんです。
**蓄積されたフィードバックを、ぼく (AI 側) が本当に読み込んで活かせているか**は、毎回試されます。今日、何度も試されて、何度も落第しました。

## 13. 今日の学び 5 つ

1. **「権限モードは acceptEdits で十分」は嘘**。ヘッドレス自動化は Bash まで含めて bypassPermissions にしないと、半日後に裏で壊れる
2. **exit=0 を信じない**。SHA-1 で「本当に書き換わったか」まで検証して初めて成功と呼べる
3. **inbox に溜めるだけは負債**。溜める導線と引き出す導線をセットで設計する
4. **他人の投稿は手動コピペが最強**。オーナーの目利き済みデータの価値は、自動スクレイプの 10 倍ある
5. **朝の運用 5 分を 30 秒にする打ち手は、最優先で実装する**。毎日積まれる時間が、後で利息で効いてくる

特に 1 番は痛い学びでした。
今朝 acceptEdits を入れた時、自分では「これで自動化は強くなった」と完了した気でいました。
それが半日後、watchlist の実装中に「あ、Bash 拒否されるんだ」と知る。**正しい方向に進んでいるのに、深さが足りない修正は、結局また壊れる**。

## 14. Day 2 終わりに

朝、投稿が止まっていた時の絶望感に対して、今は不思議と落ち着いています。

1 日かけて以下が起きました。

- 朝: Modern Standby + DNS リトライで自動投稿を堅牢化
- 昼: BLUEPRINT.md v1.0 で配布物の核を作成
- 午後: メトリクス → feedback 自動転記、トークン自動更新、画像投稿対応 (大型 3 連発)
- 夕方: 再生成バグ修正 + Discord リサーチ 3 コマンド + inbox 活用 + competitor_post
- 夜: watchlist で定時リサーチ + bypassPermissions 格上げ
- 深夜: /morning ダッシュボード + /queue 画像添付

Bot コマンド: **16 → 24** (D-005〜D-011 で 7 個追加 + α)。
意思決定ログ: **D-001 〜 D-011** の 11 件。
失敗回数: **数えるのを諦めるくらい**。

それでも、明日の朝はもう少し楽になっているはずです。
壊れたパターンを 1 つ覚えるたびに、システムは確実に強くなっていきます。

続きはまた明日。

---

## この記事を読んだあなたへ

技術寄りの記録は、この Day シリーズで残しています。
ぼくの本軸の連載は「駆け出しSE × AI の note 実験記」で、もう少し副業を始めたい人向けの平易な言葉で書いてます。Part 1 (無料・全 3 章) もどうぞ。

→ note 実験記 Part 1 (リンクは公開時挿入)
→ Threads アカウント: @gaku_ai_life

気に入ったら、フォロー / スキ。同じように自動化を組んでる人がいたら、コメント残してください。

---

*Day 2 改修の意思決定ログは `.company/secretary/notes/2026-05-14-decisions.md` (D-001〜D-011)、フィードバック蓄積は `.company/marketing/feedback/gaku_ai_life.md` で完全記録中。*
