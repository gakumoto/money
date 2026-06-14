---
created: "2026-06-10"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering"]
sources: 8
post_ideas: 6
---

# LangChain プロンプトエンジニアリング 実例 (2026-06-10 収集)

## サマリ
- LangChain は 2025-10-22 に **1.0 GA** が出た。これに伴い 2026 年は `create_agent` / `ChatPromptTemplate` + LCEL + 構造化出力 という「3点セット」が事実上の標準。
- 過去の `LLMChain` / `SequentialChain` は **deprecated**。`.pipe()` または `prompt | llm | parser` の LCEL 記法に移行が必要。
- Few-shot は「セレクタで動的に例を選ぶ」 (`SemanticSimilarityExampleSelector`) が伸びてる。固定の Few-shot は古くなりつつある。
- 構造化出力は `response_format=ToolStrategy(YourSchema)` を渡す形が新標準。Pydantic ベース。

---

## 注目情報

### LangChain 1.0 Deep Dive (digitalapplied / 2026-05-14 公開)
- ソース: https://www.digitalapplied.com/blog/langchain-1-deep-dive-agent-protocol-runtime-2026
- 公開日: 2026-05-14
- 要点（3行以内）:
  - `create_agent` が新標準入口。AgentExecutor は legacy 扱い。LangGraph ベースで Middleware で拡張する設計に変わった。
  - Middleware は 6 フック：`before_agent`, `before_model`, `wrap_model_call`, `wrap_tool_call`, `after_model`, `after_agent`。サブクラス化はもう要らない。
  - プロバイダ統合は `@langchain/<provider>` パッケージに分離。リリースサイクルがコアと切り離された。
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChain 1.0 で AgentExecutor は卒業。`create_agent` + Middleware の時代になった」 (古い記事を見てハマってる人向け)

### LangChain in 2026: 5 Concepts (Medium / 2026-02-27 公開)
- ソース: https://medium.com/@vapbooksfeedback/tech-54-langchain-in-2026-the-5-concepts-that-handle-90-of-real-use-cases-19a96f654ba2
- 公開日: 2026-02-27
- 要点（3行以内）:
  - 「素の openai.chat.completions.create」と LangChain 版の差分が体感できるサンプル付き。
  - 推奨インポートは `from langchain_openai import ChatOpenAI` / `from langchain_core.prompts import ChatPromptTemplate` / `from langchain_core.output_parsers import StrOutputParser`。
  - 5 概念で実用例の 90% が回るという主張：Chains / Prompts / Memory / Tools / Structured Output。
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「LangChain を全部覚えようとして挫折した。実は 5 つだけで 90% 回る」

### Prompt Engineering Quickstart (LangChain公式ドキュメント)
- ソース: https://docs.langchain.com/langsmith/prompt-engineering-quickstart
- 公開日: (継続更新)
- 要点（3行以内）:
  - プロンプトエンジニアリングを「LLM への指示を **作る → テストする → 直す** ループ」と公式が定義。
  - LangSmith でプロンプトを版管理する流れが公式推奨に。「書きっぱなし」をやめる発想。
  - LangSmith Playground で評価データセットを回してから本番に出す。
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「プロンプトを Git にコミットせず LangSmith で版管理してみたら、過去のベスト版に 1 クリックで戻せた」

### Few-Shot Prompting with LangChain (IBM / Pinecone)
- ソース: https://www.ibm.com/think/tutorials/few-shot-prompting-langchain
- 公開日: 2025-下半期 (継続更新)
- 要点（3行以内）:
  - `FewShotPromptTemplate` に examples リスト (dict) と `example_prompt` (PromptTemplate) を渡すだけで動く。
  - チャットモデル用は `FewShotChatMessagePromptTemplate` を使い分ける。input/output で `HumanMessage/AIMessage` 形に揃う。
  - 例が増えたら `SemanticSimilarityExampleSelector` で「入力に似た例だけ」動的に注入できる。トークン節約と精度両取り。
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Few-shot プロンプト、例を 20 個ベタ書きしてた。`SemanticSimilarityExampleSelector` で 3 個に絞ったら精度上がった」

### LangChain 1 構造化出力ベストプラクティス (公式 / Mirascope ブログ)
- ソース1: https://docs.langchain.com/oss/python/langchain/structured-output
- ソース2: https://mirascope.com/blog/langchain-structured-output
- 公開日: 2026 上半期
- 要点（3行以内）:
  - スキーマ型 (Pydantic) を `create_agent(response_format=...)` に渡すと、モデルが native 構造化出力対応なら自動で `ProviderStrategy` が走る。
  - `ToolStrategy(YourSchema)` を使うと、モデルが間違ったツールを呼んだとき自動で ToolMessage で再試行を促してくれる。
  - 「ツール記述は **ドキュメントではなくプロンプトの一部** 」。命名より説明文の語彙の選び方が精度に効く。
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「LangChain のツール `description` を雑に書いてたら、Agent が違うツール呼びまくった。命名より説明文が効く」

### LCEL 入門 (Zenn / os1ma)
- ソース: https://zenn.dev/os1ma/articles/acd3472c3a6755
- 公開日: 2023-10〜 (LCEL の標準化記事として今も参照される)
- 要点（3行以内）:
  - LCEL の核は `prompt | llm | StrOutputParser()` の **パイプ記法**。`invoke / stream / batch / ainvoke` を自動で実装してくれる。
  - `PromptTemplate` の `partial_variables` で「固定の指示文」と「動的な変数」を分離。テンプレ汚染を防ぐ。
  - LCEL に乗せておくと、後で `LangSmith` トレース / 並列実行 / リトライ がほぼ無料で付いてくる。
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「LangChain の `|` (パイプ) を「Linux のパイプと同じ」って気づいた瞬間、LCEL が一気に腑に落ちた」

---

## 投稿化推奨ランキング

1. **「AgentExecutor は卒業した」** — 1.0 移行ネタは「古い記事で詰まってる人」に刺さる。具体名 `create_agent` が入るので教育系で強い。
2. **「ツール description は命名より重要」** — 失敗談として書きやすい。夕失敗型のフォーマットにそのまま乗る。
3. **「LangChain は 5 概念で 90% 回る」** — 全体感を一枚で見せられるので保存される率が高い。

## 心得メモ
- 今回は「実例」がテーマなので、抽象的な「プロンプトエンジニアリングとは」系の記事は意図的に外した。
- LangChain 1.0 GA (2025-10-22) を知らない読者がまだ多い。「最新化された型」を出すと教育コンテンツとして強い。
- gaku_ai_life の主軸は副業/Claude 寄りなので、LangChain ネタは「教育目的」枠で月 1〜2 本にとどめるのが安全。週次連投はテーマがブレる。
