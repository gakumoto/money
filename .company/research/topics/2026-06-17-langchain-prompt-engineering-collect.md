---
created: "2026-06-17"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering"]
sources: 5
post_ideas: 5
---

# LangChain プロンプトエンジニアリング 実例（2026-06-17 収集）

### LCEL の pipe 演算子で「prompt | model | parser」が標準形になった
- ソース: https://medium.com/@sajo02/building-production-ready-ai-pipelines-with-langchain-runnables-a-complete-lcel-guide-2f9b27f6d557
- 公開日: 2026-02-16
- 要点（3行以内）:
  - 旧 Chains オブジェクトはもう書かない。`chain = prompt | llm | parser` が 2026 の書き方
  - `RunnableParallel` で複数チェーン並列化 → 処理時間 40〜50% 削減の実測
  - `.invoke()` `.batch()` `.stream()` `.ainvoke()` の4実行モードを使い分け
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChain、もう Chains オブジェクト書かなくていい。 / `prompt | llm | parser` の1行で済むようになってた / 古い記事のコピペで詰まってた人、自分です」

### PromptTemplate.from_template() は変数を {} で埋めるだけ
- ソース: https://www.guvi.in/blog/langchain-prompt-templates/
- 公開日: 2026 年（GUVI ブログ、月不明）
- 要点（3行以内）:
  - `PromptTemplate.from_template("Suggest 3 must-visit places in {city} for a {traveller_type}.")` だけで再利用可
  - `.format(city="Jaipur", traveller_type="budget")` で穴埋め実行
  - 「アプリ全体で同じプロンプトを書き直さなくて済む」のが2026 の標準的な使い方
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「プロンプトを毎回コピペしてた頃の自分に教えたい。 / `PromptTemplate.from_template` で穴埋め式にすると、書き直しゼロ。」

### ChatPromptTemplate は system / human を分けて書くのが2026 のベストプラクティス
- ソース: https://www.guvi.in/blog/langchain-prompt-templates/
- 公開日: 2026 年
- 要点（3行以内）:
  - `ChatPromptTemplate.from_messages([("system", "..."), ("human", "{q}")])` で役割分離
  - system にキャラ設定、human に変数入力、というレイヤー分けがトーン安定の鍵
  - `MessagesPlaceholder(variable_name="chat_history")` を挟むと記憶付きチャットになる
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Claude / GPT に喋らせるとき、system と human を分けるだけで返答の安定感が変わる。 / `ChatPromptTemplate` の話。」

### RunnableParallel + RunnableBranch で「並列抽出 → 条件分岐」のパイプラインを組める
- ソース: https://medium.com/@sajo02/building-production-ready-ai-pipelines-with-langchain-runnables-a-complete-lcel-guide-2f9b27f6d557
- 公開日: 2026-02-16
- 要点（3行以内）:
  - 実例: 医療データ抽出で `symptom_chain` と `lab_chain` を `RunnableParallel` で同時実行
  - `RunnableBranch` でリスクレベル別にルーティング、最後に Supervisor Chain で安全性チェック
  - パイプライン全体を `clean_input | parallel_extract | memory | risk | branch | supervisor` の1式で書ける
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「AI に1個ずつ質問してた頃、レスポンス40秒待ってた。 / `RunnableParallel` で並列化したら半分。 / 知らないと損する系。」

### Findy-team が2026 年版でまとめた「実例×チーム導入」のガイド
- ソース: https://jp.findy-team.io/blog/ai-casestudy/prompt-engineering/
- 公開日: 2026 年（最新版表記）
- 要点（3行以内）:
  - LangChain を使ったコードレビュー・テスト生成の実例が日本語で整理されている
  - RAG / AI エージェント / プロンプトチェーンを「再現性」軸で説明
  - 個人実装だけでなく「チーム導入」までスコープが入っている数少ない日本語ソース
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「LangChain の日本語記事、Findy が出してるやつ良かった。 / 個人開発と組織導入の両方が同じ目線で書かれてる。」

---

## 注目トピック（即投稿化推奨）

**LCEL の `prompt | model | parser` が新標準** — 「古いLangChain入門記事のコピペで詰まる」という体験を持ってる人が多いはず。gaku の「ツール制作で詰まった話」と相性が良い。型は朝学び型 or 夕失敗型。

## 取捨選択メモ
- 「LangChain とは何か」みたいな入門解説は捨てた（読者は知ってる前提）
- 数字が無いまとめ系は除外、コード例が出てるソースだけ採用
- 「2026 年版」と書いてあるだけで中身が古い記事も除外（中身を WebFetch で確認したものに限定）
