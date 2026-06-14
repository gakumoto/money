---
created: "2026-06-02"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["langchain", "prompt-engineering", "ai-dev", "weekly-collect"]
sources: 8件
post_ideas: 7件
---

# LangChain プロンプトエンジニアリング 実例 — 2026-06-02 収集

前日（2026-06-01）の同テーマファイルとは別軸で、**実装コード・Runnable 系・Few-shot の具体例** に絞って収集した。

---

### PromptTemplate と ChatPromptTemplate の使い分け
- ソース: https://medium.com/@thakur.rana/prompttemplate-vs-chatprompttemplate-understanding-and-invoking-them-in-langchain-b5fe5b203ec5
- 公開日: 2026 年継続更新（Medium）
- 要点:
  - `PromptTemplate` は単発のテキスト補完用。テンプレ文字列＋プレースホルダ
  - `ChatPromptTemplate` はロール付き（system / human / ai）。会話の構造化用
  - `.format()` は文字列を返すだけ、`.invoke()` は Runnable インターフェースなので `prompt | model | parser` の縦パイプに繋がる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChain で `PromptTemplate` と `ChatPromptTemplate` を間違えてた話。`.invoke()` を覚えた瞬間にチェーンが組めた」

---

### Few-shot で JSON を必ず吐かせる定番パターン
- ソース: https://python.langchain.com/docs/how_to/few_shot_examples/
- 公開日: LangChain 公式 docs（継続更新）
- 要点:
  - `FewShotPromptTemplate` は example list を prefix / suffix で挟んで自動展開する
  - `examples = [{"input": "...", "output": '{"name":"..."}'}]` で「自然文 → JSON」を 3〜5 例見せれば、未学習タスクでもフォーマットが揃う
  - `ExampleSelector`（semantic / length-based）で例文選びも自動化できる → 入力に近い例だけ送り、トークンを節約
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「『JSONで返して』と書いても崩れるなら Few-shot を3個入れる。LangChain なら 10 行で書ける」

---

### Few-shot prompting 入門の最小コード
- ソース: https://dev.to/aiengineering/a-beginners-guide-to-few-shot-prompting-in-langchain-2ilm
- 公開日: 2026 年（DEV Community / AI Engineering Bootcamp）
- 要点:
  - 「タスク説明 → 例 1 → 例 2 → 例 3 → 実入力」の 5 ブロック構造
  - 例文は「クラス分類 / フォーマット変換 / 文体模倣」の 3 用途で特に効く
  - 例を増やしすぎると逆効果。3〜5 件で打ち止め推奨
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Few-shot の最適数は 3〜5。それ以上は精度が下がるという地味に重要な話」

---

### LCEL の `prompt | model | StrOutputParser()` が最小単位
- ソース: https://www.netjstech.com/2026/03/chain-using-lcel.html
- 公開日: 2026-03（Tech Tutorials）
- 要点:
  - LCEL の最小チェーン: `chain = prompt | model | StrOutputParser()` → `chain.invoke({"topic": "..."})`
  - `|`（パイプ）は左から右へデータが流れる。bash パイプと同じ感覚
  - sync / async / streaming / batch の 4 モードを Runnable が自動で持つ
- 投稿アイデア:
  - 型: 教育目的 / 朝学び型
  - 切り口: 「LangChain は `prompt | model | parser` の 3 連パイプを覚えれば 8 割いける」

---

### RunnableParallel で要約とクイズを同時生成
- ソース: https://www.netjstech.com/2026/04/runnableparallel-in-langchain-example.html
- 公開日: 2026-04（Tech Tutorials）
- 要点:
  - `RunnableParallel({"summary": chain_a, "quiz": chain_b})` で同一入力に対し 2 つのチェーンを並列実行
  - 同じ文書を入れて「要約」と「クイズ」を同時に返す、みたいな構成が 1 ブロックで書ける
  - LCEL に同期 / 非同期の差異がないので、Web リクエストでも CLI でもそのまま使える
- 投稿アイデア:
  - 型: 昼進捗 / 教育目的
  - 切り口: 「同じ文書から要約とクイズを並列で生成する LangChain コード。10 行で書けた」

---

### RunnableLambda で「Python 関数」をチェーンに差し込む
- ソース: https://www.netjstech.com/2026/04/runnablelambda-langchain-with-examples.html
- 公開日: 2026-04（Tech Tutorials）
- 要点:
  - 自作の Python 関数を `RunnableLambda(func)` でラップすれば LCEL チェーンに混ぜられる
  - 「LLM 出力 → 正規表現でクレンジング → DB 保存」みたいな前後処理を全て `|` で繋げる
  - エージェントを使うほどでもない小さな変換に最適
- 投稿アイデア:
  - 型: 夕失敗 / 教育目的
  - 切り口: 「LangChain の出力を毎回後処理で書いてたけど、RunnableLambda で全部チェーン内に押し込めた」

---

### Production レベルの LCEL パイプライン構築
- ソース: https://medium.com/@sajo02/building-production-ready-ai-pipelines-with-langchain-runnables-a-complete-lcel-guide-2f9b27f6d557
- 公開日: 2026-02（Medium）
- 要点:
  - 本番運用では `RunnablePassthrough` で入力を後段に温存しつつ前段で派生情報を作る構成が定番
  - `with_retry()` / `with_fallbacks()` をチェーンに付けるだけでリトライ・フォールバックが入る
  - ストリーミング応答（`chain.stream()`）が標準。トークン課金時代に必須
- 投稿アイデア:
  - 型: 深夜思考 / 教育目的
  - 切り口: 「LangChain のチェーンに `.with_fallbacks()` を 1 行足すだけで本番耐性が上がる、地味で強い機能」

---

### Prompt chaining（複雑タスクを段階分解）
- ソース: https://www.ibm.com/think/tutorials/prompt-chaining-langchain
- 公開日: IBM Think（継続更新）
- 要点:
  - 1 つの大きなプロンプトで全部やらせず、「抽出 → 分類 → 整形」など段階に分けて連結する
  - 各ステップの出力を次ステップの入力に渡す `RunnableSequence` が中核
  - 単発プロンプトより精度・デバッグ性が上がる
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「プロンプトを1本に詰め込まずに3段に分けたら精度が一段上がった。LangChainのチェーン分割の話」

---

## ネクストアクション

- 投稿化候補（即下書きにできる粒度）:
  1. 「LangChain の最小チェーン `prompt | model | parser` の話」（朝学び）
  2. 「Few-shot は 3〜5 個で十分。それ以上は精度が下がる」（教育）
  3. 「`.with_fallbacks()` 1 行で本番耐性が上がる地味技」（深夜思考）
- 次の動き: `/threads-create-post` で 1〜2 を gaku_ai_life の朝枠下書きに回す

## 結論

前日の調査は「思想・職種論」中心だったので、本日は **手を動かす実装側のネタ** を 8 件揃えた。LCEL の Runnable 三種（Parallel / Lambda / Passthrough）が 2026 年の中核で、ここを抑えれば AI 開発系の投稿は当面ネタ切れしない。
