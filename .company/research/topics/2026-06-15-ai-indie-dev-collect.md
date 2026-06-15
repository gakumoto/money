---
created: "2026-06-15"
topic: "AI 個人開発"
status: completed
tags: ["weekly-collect", "ai-indie-dev", "claude-code", "vibe-coding", "monetize"]
sources: 6
post_ideas: 6
---

# 2026-06-15 AI 個人開発リサーチ

前回 (2026-06-14) は Claude Code 6/15 料金改定・猫多頭飼いアプリ・ニッチ勝ち事例を扱った。
今回は **Code with Claude Tokyo (6/10) 直後の温度感** と、**AI生成コードのリスク・収益分布のリアル** に振る。

## 探索したソース

1. mindstudio.ai - Code with Claude 2026 で出た5機能の整理 (Dreaming / Outcomes / Multi-Agent / Claude Finance / Add-ins)
2. Findy Tech Blog - Code w/ Claude Extended Tokyo 参加レポート (2026-06-12)
3. innovatopia.jp - Code with Claude 2026 東京 6/10 開催
4. shiftb.dev - バイブコーディング 2026年版 (AI生成コード40-62%脆弱性)
5. buildmvpfast - $602K Solo Indie Hacker App Revenue Breakdown 2026
6. zenn @ktg - AIで個人開発「作る」より「売る」が100倍難しい

---

## ネタ1: Code with Claude Tokyo の5機能、個人開発者にはほぼ刺さらなかった話

- ソース: https://www.mindstudio.ai/blog/code-with-claude-2026-new-agent-features
- 公開日: 2026-06頃
- 要点（3行以内）:
  - 発表5機能 (Dreaming / Outcomes / Multi-Agent Orchestration / Claude Finance / Add-ins) は全部エンタープライズ向け
  - 個人開発者に効くのは **Outcomes** だけ (採点エージェントで品質10.1%向上)
  - Multi-Agent Orchestration と Claude Finance は「チーム/金融機関」前提
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Code with Claude Tokyoで5機能発表されたけど、個人開発者に効くのは1個だけだった話」
  - 数字: 5機能のうち1個 (Outcomes) / 品質+10.1% / 6/10 Tokyo
  - ガク文脈: 「ぼくも見てたけど、エンタープライズ向けが多くて『個人開発者は次の発表待ちか』ってなった」

## ネタ2: AI生成コードの40〜62%に脆弱性、という具体的な数字

- ソース: https://shiftb.dev/articles/what-is-vibe-coding
- 公開日: 2026年
- 要点（3行以内）:
  - バイブコーディング (AIに自然言語で書かせる) で生成されたコードの **40〜62%に脆弱性** 報告
  - 「動く」と「安全」は別問題。本番投入前にチェックリスト必須
  - 顧客データ・個人情報を AI プロンプトに入れないが最低ライン
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「AIに書かせたコード、40〜62%に脆弱性入ってるって調査見て手が止まった話」
  - 数字: 40〜62% (具体的な範囲) / 「動く」と「安全」は別問題
  - ガク文脈: 副業で書いたコードを本業の会社で動かす時の不安に接続

## ネタ3: 個人開発の収益、中央値は月$3,000 (45万円)

- ソース: https://www.buildmvpfast.com/blog/602k-revenue-solo-indie-hacker-app-portfolio-breakdown-2026
- 公開日: 2026年
- 要点（3行以内）:
  - 海外 solo founder の **中央値は月$3,000** (年$36K ≒ 月45万円)
  - 分布: 40% が $1K MRR 未達で停滞 / 30% が $1-5K MRR / 20% が $5-20K MRR / 10% だけが $20K+
  - $1M ARR の人は実在するが、SNS で見えるのは生存者バイアス
- 投稿アイデア:
  - 型: 夕方学び型 / 信頼構築
  - 切り口: 「『個人開発で月100万』って情報ばかり見るけど、海外データだと中央値は月45万。40%は$1K MRR(15万円)に届かないって話」
  - 数字: 中央値$3,000 / 40%が$1K未満 / 10%だけが$20K+
  - ⚠️ リスクワード注意: 「月100万」を売り文句にしない、データの引用として1回使う

## ネタ4: 47日で月$10K MRR (150万円) の AI 個人開発事例

- ソース: https://www.buildmvpfast.com/blog/602k-revenue-solo-indie-hacker-app-portfolio-breakdown-2026
- 公開日: 2026年
- 要点（3行以内）:
  - solo founder が **47日で月$10K MRR (≒150万円) 到達**
  - AI でアプリ生成・ドキュメント執筆・サポート対応・広告運用まで全部回した
  - 本番運用コストは月$85〜$200 (≒1.3〜3万円) と劇的に下がっている
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「47日で月150万MRRに到達した個人開発者、コード書く時間より『AIに何を任せるか決める時間』の方が長かったらしい」
  - 数字: 47日 / $10K MRR / 月運用コスト$85-200
  - ガク文脈: 「ぼくはまだ0円だけど、AIに任せる作業の切り出しは見習える」

## ネタ5: 「作る」より「売る」が100倍難しい (zenn記事)

- ソース: https://zenn.dev/ktg/articles/518c880823ad4a
- 公開日: 2026年
- 要点（3行以内）:
  - AI で個人開発の **「作る」コストは下がったが「売る」コストは下がっていない**
  - むしろ AI で大量に生まれる類似アプリの中で埋もれるリスクが上がった
  - 集客チャネル (Threads / X / SEO / コミュニティ) を先に持っている人が圧倒的に有利
- 投稿アイデア:
  - 型: 深夜思考型 / 信頼構築
  - 切り口: 「AIで作るのは10倍速くなったけど、売るのは100倍難しくなったって話」
  - ガク文脈: **これはガクの note ＋ Threads 戦略そのもの**。「先にThreadsで認知作ってから商品出す」を裏付ける材料

## ネタ6: 本番運用コスト、月$85〜$200 (1.3〜3万円) で個人SaaS回る時代

- ソース: https://www.buildmvpfast.com/blog/602k-revenue-solo-indie-hacker-app-portfolio-breakdown-2026
- 公開日: 2026年
- 要点（3行以内）:
  - 個人開発SaaSのフル運用コストは **月$85〜$200** (DB / 認証 / メール / ホスティング込み)
  - 数年前は月$500〜$1,000かかっていた領域が、無料/従量プランの組み合わせで激減
  - 利益率 70〜90% (人件費ゼロ・サーバー激安) が当たり前
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「個人開発SaaSの月運用コスト、今って$85〜$200 (1.3〜3万円) で回るらしい。数年前の1/5以下」
  - 数字: $85-200 / 利益率70-90%
  - ガク文脈: 「ぼくの note も追加コストほぼゼロで運用できてるのと同じ構造」

---

## 注目トピック (即投稿化推奨)

**ネタ5「作るより売るが100倍難しい」** がガクの戦略 (Threads先・note後) と完全一致する。
今日の投稿候補として最有力。

## 次の動き

- `/threads-create-post ネタ5を朝学び型で` で即下書き化
- ネタ1 (Code with Claude Tokyo 5機能の冷静評価) は信頼構築型に強い。明日朝枠候補
- ネタ3 の収益分布は危険ワード注意 (月45万 / $20K MRR は1投稿1回まで)
