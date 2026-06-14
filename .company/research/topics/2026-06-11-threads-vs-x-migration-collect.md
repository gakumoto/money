---
created: "2026-06-11"
topic: "情報収集: Threads vs X 移行（ユーザー数逆転と運用思想の違い）"
status: completed
tags: ["weekly-collect", "threads-vs-x", "migration", "threads-algorithm", "platform-shift"]
sources: 8
post_ideas: 7
---

# Threads vs X 移行 (2026-06-11 時点)

2026 年 1 月以降、Threads がモバイル DAU で X を逆転。日本市場でも Threads ユーザー 1,230 万人（2026-04 時点）まで成長。
本リサーチは「数字の事実」と「Threads ならではの勝ち筋（X とのアルゴリズム/設計思想の違い）」の 2 層で整理する。

---

## 1. 数字の事実（投稿フックに直接使える）

### Threads がモバイル DAU で X を逆転（2026 年 1 月初, Similarweb）
- ソース: https://www.gizmodo.jp/article/threads-is-now-clearly-more-popular-than-x/
- 公開日: 2026-01
- 要点:
  - モバイルアプリ DAU: Threads **1 億 4,150 万人** vs X **1 億 2,500 万人**
  - 前年比: Threads **+37.8%**, X **-11.9%**
  - 半年前にも「迫る勢い」報告あり = 一時の流行ではなく着実な利用シェア拡大
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「2026 年、モバイルではついに Threads が X を抜いた。+37.8% vs -11.9%。じゃあ僕らはどう動くか」

### ブラウザ利用ではまだ X が圧倒的（同 Similarweb）
- ソース: https://www.gizmodo.jp/article/threads-is-now-clearly-more-popular-than-x/
- 公開日: 2026-01
- 要点:
  - ブラウザ DAU: X.com **1 億 4,070 万人** vs Threads.com **770 万人**（約 18 倍差）
  - 仕事の合間にデスクトップで開くのは依然 X
  - Threads は「スマホで読む文化」が定着、X は「PC でも生きる」
- 投稿アイデア:
  - 型: 昼進捗型 / 観察
  - 切り口: 「Threads は X に勝ったって言うけど、ブラウザだと 18 倍の差で X が勝ってる。読まれる場所が違うってだけの話」

### 日本国内 Threads ユーザー 1,230 万人（2026-04）
- ソース: https://prx.dentsuprc.co.jp/blog/threads_pr
- 公開日: 2026
- 要点:
  - 世界 MAU 4 億超、日本 1,230 万人（2026-04 時点）
  - MAU 4 億公式発表は 2025-08-12（Meta）
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「日本で 1,230 万人が Threads にいる。X からの避難民じゃなく、Threads でしか会えない人たちの市場」

### X からの移行理由（プラットフォーム要因）
- ソース: https://www.gizmodo.jp/article/threads-is-now-clearly-more-popular-than-x/
- ソース: https://www.nikkei.com/article/DGXZQOUC10B2R0Q3A710C2000000/
- 要点:
  - X 専用 AI「Grok」の悪用問題（他人の写真をヌード加工して投稿）が深刻化
  - 各国が取り締まり強化 → ユーザーが Threads / Bluesky に流出
  - 国連機関・公共放送・医療団体が X から Mastodon/Threads/公式 Web に発信主軸を移転
- 投稿アイデア:
  - 型: 夕失敗型 / 観察（押し売りせず社会観察として）
  - 切り口: 「国連も公共放送も X から離れた 2026 年。個人の発信者がそろそろ動かない理由ある？」

---

## 2. アルゴリズム / 設計思想の違い（運用者の判断軸）

### X = 速さ × 初速、Threads = 会話深さ × 1 時間集中
- ソース: https://zenn.dev/7788/articles/a3afd95ff657a3
- 公開日: 2026 年（毎週更新）
- 要点:
  - X For You: 「プロフィールクリック」「長文返信」が最高評価 ★★★★★。投稿後 **30 分の初速** が命
  - Threads: 「返信数そのもの」が最重要、いいね・再投稿・引用が高評価。**最初の 1 時間** での集中エンゲージメントが判定基準
  - Threads は「見えないエンゲージメント」（リンククリック・プロフィール訪問）も評価対象
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「X は 30 分、Threads は 1 時間。同じ SNS のつもりで運用してたら片方は伸びない理由」

### 投稿フォーマットの最適解が真逆
- ソース: https://zenn.dev/7788/articles/a3afd95ff657a3
- 要点:
  - X: スレッド形式 / 動画（6〜60 秒）/ 長文テキストが強い
  - Threads: **500 文字以内 + 問いかけ** のテキストが効果的
  - X はリンク本文含有で拡散低下、Threads はテキスト主体なら許容範囲
- 投稿アイデア:
  - 型: 昼進捗型 / 教育
  - 切り口: 「Threads で長文書いて伸びないのは、長文がダメだからじゃなくて『問いかけがない』から。500 文字 + 1 つの問いが標準装備」

### Meta 公式: Threads の 4 評価ステージ
- ソース: https://addness.co.jp/media/threads-algorithms/
- 要点:
  - Stage 1: フォロワーの一部に配信 → 初動反応速度
  - Stage 2: 全フォロワー → 反応の一貫性
  - Stage 3: 非フォロワー → トピック関連性 / トレンド適合
  - Stage 4: 外部プラットフォーム共有 → シェア価値
  - 多くの投稿は **Stage 1 で止まる**（初動の返信が足りない）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Threads 伸びない投稿の 9 割は『Stage 1 で止まってる』。最初の 30 人のフォロワーが返信しない投稿は次に進めない仕組み」

### 「会話の深さ」が Threads の評価軸
- ソース: https://addness.co.jp/media/threads-algorithms/
- ソース: https://ebiz-create.co.jp/emagazine/1265/
- 要点:
  - X は「リアルタイム速度」、Threads は「会話がどれだけ続くか」
  - いいねより返信が重視される。一方通行の発信より双方向対話
  - Meta 推奨投稿頻度: 週 2〜5 回（毎日でなくていい / 短くてもいい）
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「Threads は週 2〜5 回でいいって Meta が言ってる。毎日 10 本上げてた自分、何やってたんだろう」

---

## 3. 観察まとめ（自分の運用への落とし込み）

| 観点 | X | Threads | 自分の運用ですぐ変えること |
|------|---|---------|--------------------------|
| 初速の窓 | 30 分 | 1 時間 | 投稿直後 1 時間は他アカウントへ返信周回 |
| 強い形式 | スレッド・長文 | 500 字 + 問いかけ | 長文 note への引用は Threads 本文ではなく返信欄に |
| 評価の主役 | 拡散（リポスト） | 会話（返信） | いいね目的の煽りより「返したくなる問い」を優先 |
| 読まれる場所 | スマホ + PC | スマホほぼ全部 | 改行 / 余白を「親指スクロール基準」で設計 |
| 投稿頻度 | 毎日複数本前提 | 週 2〜5 回で OK | 「数」より「会話が起きるか」を優先 |

---

## 4. 注目トピック（即投稿化推奨 Top 3）

1. **「X は 30 分、Threads は 1 時間」初速の窓の違い** — 教育型で 1 本作れる。実例 + 自分の運用変化セットで強い
2. **「Stage 1 で 9 割が止まる」Meta 公式 4 ステージ** — 数字 (1/9) + 仕組みの暴露でフック強い
3. **「ブラウザでは X が 18 倍勝ってる」逆転の中の負け** — 観察型。「移行した方がいい」と煽らずに事実だけで考えさせる構造

---

## 5. ソース一覧

- https://www.gizmodo.jp/article/threads-is-now-clearly-more-popular-than-x/ — ギズモード「加速する脱 X の動き」
- https://prx.dentsuprc.co.jp/blog/threads_pr — 電通 PRC「Threads がアクティブユーザー数で X を超えた」
- https://addness.co.jp/media/threads-algorithms/ — アドネスラボ「Meta 公式発表から読み解く Threads アルゴリズム」
- https://zenn.dev/7788/articles/a3afd95ff657a3 — Zenn「SNS アルゴリズム完全解析 2026 年版（毎週更新）」
- https://ebiz-create.co.jp/emagazine/1265/ — eBIZ「2026 Threads アルゴリズム攻略」
- https://www.nikkei.com/article/DGXZQOUC10B2R0Q3A710C2000000/ — 日経「メタの Threads, Twitter からの移行は限定的か」
- https://www.comnico.jp/we-love-social/sns-users — comnico「2026 年 6 月版 主要 SNS ユーザー数」
- https://www.walkerplus.com/article/1148919/ — ウォーカープラス「X 離れが加速、Threads も候補に」
