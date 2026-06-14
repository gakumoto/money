---
created: "2026-06-04"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering", "ai-dev"]
sources: 10
post_ideas: 7
---

# LangChain プロンプトエンジニアリング 実例 (2026-06-04 収集)

## サマリ
- 2026年の主流は「賢いプロンプト1本」から「文脈を組み立てる4戦略（write / select / compress / isolate）」に完全シフト。LangChain がこの4つを正式に整理した。
- Claude には XML タグ（`<instructions>` `<context>` `<example>`）が公式に最良。Markdown でも数字付き箇条書きでもない。
- LCEL（LangChain Expression Language）の `|` パイプ記法に乗ると、同じ機能のコード量が **約70%減**・streaming/async が自動で付いてくる。
- 2024 → 2026 の現場で「agentic RAG プロジェクトの90%が本番で失敗」したという数字が出回っている。原因は「モデルではなくコンテキスト組み立ての失敗」。
- FewShotPromptTemplate は依然強い手段だが、件数が多くなるとスケールしない（ExampleSelector で動的に選ぶ流れ）。

---

## 収集ネタ

### 1. プロンプトの主役は「文脈の組み立て」になった（4戦略）
- ソース: [Prompt Engineering Best Practices 2026 | Thomas Wiegold Blog](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/)
- 公開日: 2026年
- 要点（3行以内）:
  - LangChain が文脈管理を 4 つに整理: **write**（外部保存）/ **select**（RAGで取り出す）/ **compress**（要約圧縮）/ **isolate**（エージェント別に分離）
  - 本番のエージェント失敗の大半は「モデルが悪い」ではなく「文脈の組み立てが悪い」
  - 「賢いプロンプトを1本書く」時代は終わり、「どの情報を、いつ、どこに置くか」が勝負
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChainが2026年に整理した『プロンプトの新しい4戦略』。1本の名プロンプトを書くフェーズはもう終わった」

### 2. Claude を使うなら Markdown より XML タグ（公式推奨）
- ソース: [Prompt engineering concepts - Docs by LangChain](https://docs.langchain.com/langsmith/prompt-engineering-concepts) / [Prompt Engineering Best Practices 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/)
- 公開日: 2026年
- 要点（3行以内）:
  - Claude には `<instructions>` `<context>` `<example>` の XML タグでセクション分けする方法が最良という結論
  - Markdown 見出し / 数字付き箇条書きより精度が出る
  - Few-shot は 3〜5 例を `<example>` タグで囲むのが鉄板
- 投稿アイデア:
  - 型: 朝学び / 教育目的（即実践系）
  - 切り口: 「Claudeに『# 指示』と書いてる人、損してる。公式が薦めてるのは `<instructions>` タグ。これだけで再現性が変わった」

### 3. LCEL（パイプ記法）でコードが70%減る
- ソース: [LangChain Expression Language Explained | Pinecone](https://www.pinecone.io/learn/series/langchain/langchain-expression-language/) / [LangChain LCEL in Practice 2026 | BetterLink Blog](https://eastondev.com/blog/en/posts/ai/20260504-langchain-lcel-practice/)
- 公開日: 2026-05-04 ほか
- 要点（3行以内）:
  - `rag_chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm)` の一行で RAG が組める
  - 同等機能を従来の Chain クラスで書くより **約 70% コード減**
  - streaming レスポンスと async が「書かずに」勝手に効く
- 投稿アイデア:
  - 型: 昼進捗 / 教育目的
  - 切り口: 「LangChainのLCEL、最初は『パイプいる？』と思ってたけど、RAGを1行で書けた瞬間に宗旨替えした話」

### 4. FewShotPromptTemplate は強い、でも件数増えるとスケールしない
- ソース: [FewShotPromptTemplate | LangChain Reference](https://reference.langchain.com/python/langchain-core/prompts/few_shot/FewShotPromptTemplate) / [Exploring Few-Shot Prompts with LangChain | Medium](https://medium.com/donato-story/exploring-few-shot-prompts-with-langchain-852f27ea4e1d)
- 公開日: 2026年（公式リファレンス）
- 要点（3行以内）:
  - `FewShotPromptTemplate(examples=[...], example_prompt=..., suffix=..., input_variables=[...])` の4点セットで定義
  - 例を増やしすぎるとコンテキスト爆発、`ExampleSelector` で動的に「近い例だけ」選ぶのが今の作法
  - 「2〜3例で動かして、効かなければ ExampleSelector」が経済的
- 投稿アイデア:
  - 型: 夕失敗 → 改善 / 教育目的
  - 切り口: 「Few-shotで例を20個入れたら逆に精度が落ちた。理由は『近い例を選ぶ仕組み』が抜けてたから」

### 5. PromptTemplate vs ChatPromptTemplate の使い分け
- ソース: [PromptTemplate vs ChatPromptTemplate | Medium - Thakur Rana](https://medium.com/@thakur.rana/prompttemplate-vs-chatprompttemplate-understanding-and-invoking-them-in-langchain-b5fe5b203ec5) / [ChatPromptTemplate | LangChain Reference](https://reference.langchain.com/python/langchain-core/prompts/chat/ChatPromptTemplate)
- 公開日: 2026年
- 要点（3行以内）:
  - `PromptTemplate` はプレーンテキスト1本専用（旧 LLaMA・GPT-3 のような completion API 向き）
  - `ChatPromptTemplate.from_messages([("system", ...), ("human", ...)])` がチャット形式（マルチターン）用
  - 今の GPT-4 / Claude / Gemini を叩くなら ChatPromptTemplate 一択
- 投稿アイデア:
  - 型: 朝学び / 教育目的
  - 切り口: 「LangChainで `PromptTemplate` 使ってる人、たぶん古い記事を読んでる。今の Claude 叩くなら `ChatPromptTemplate` が正解」

### 6. Prompt Chaining: 1本のメガプロンプトより複数の小プロンプト
- ソース: [Prompt chaining with LangChain | IBM Think](https://www.ibm.com/think/tutorials/prompt-chaining-langchain) / [Chaining Prompts in LangChain: Best Practices | Medium](https://medium.com/@kaushalsinh73/chaining-prompts-in-langchain-best-practices-970abc937517)
- 公開日: 2026年
- 要点（3行以内）:
  - 1本のメガプロンプトに全部詰めるより、「1タスク1プロンプト」を `|` で繋ぐ方がテストもデバッグも楽
  - 各段の出力をそのまま次段の入力に渡せる（モジュール化される）
  - 「賢いプロンプトを書く競技」から「役割ごとに分解する設計」に評価軸が変わった
- 投稿アイデア:
  - 型: 夜振り返り / 教育目的
  - 切り口: 「『1本の神プロンプト』を書くのは、もう古い。役割ごとに5本に分けて繋いだ方が、デバッグもテストも全部ラクになる話」

### 7. 90%の Agentic RAG が本番で死ぬ理由
- ソース: [Building Production RAG Systems in 2026 | Likhon's Gen AI Blog](https://brlikhon.engineer/blog/building-production-rag-systems-in-2026-complete-tutorial-with-langchain-pinecone) / [Prompt Engineering Best Practices 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/)
- 公開日: 2026年
- 要点（3行以内）:
  - 2024 → 2026 で「agentic RAG プロジェクトの 90% が本番で失敗」というデータが出ている
  - 各層の精度が 95% でも 4 段重ねれば全体は 81% に落ちる（複利で死ぬ）
  - 解は「各層の評価を分離して可視化する」（LangSmith でトレース）
- 投稿アイデア:
  - 型: 夕失敗 / 信頼構築
  - 切り口: 「『LangChainで作ったAI、ローカルでは動いてたのに本番で死ぬ』の正体は精度の複利。各層95%でも全体81%まで落ちる」

---

## 即投稿化の最有力候補

**「Claude には XML タグ」**（ネタ2）が一番引きが強い。
- 「知らないと損してる」型の構成で 1 投稿に綺麗に収まる
- `<instructions>` `<example>` という固有のコードが入るので具体性◎
- gaku_ai_life の「AI に詳しいおじさん」キャラと完全に一致
- Claude Code を毎日使ってる本人だから書ける温度感がある

次点は **「LCELで70%減」**（ネタ3）。数字が強く、コード片を1行貼れるので説得力が高い。

---

## 参考リンク
- [Prompt Engineering and LLMs with Langchain | Pinecone](https://www.pinecone.io/learn/series/langchain/langchain-prompt-templates/)
- [LangChain Prompt Templates: Complete Guide with Examples - Latenode Blog](https://latenode.com/blog/ai-frameworks-technical-infrastructure/langchain-setup-tools-agents-memory/langchain-prompt-templates-complete-guide-with-examples)
- [LangChainの概要と使い方 | Zenn umi_mori](https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview)
- [LangChainとは？再現性を生むプロンプトエンジニアリング | 株式会社SP](https://s-p-net.com/knowledge/tech-knowledge/langchain-prompt-template-engineering)
- [LangChain プロンプトテンプレート徹底解説 | Takuyaの生成AIラーニングラボ](https://takuya-genai.com/langchain-prompt-template/)
- [LangChain Tutorial: Build a RAG Chatbot in 13 Steps [2026]](https://tech-insider.org/langchain-tutorial-rag-chatbot-python-2026/)
- [Exploring Prompt Optimization | LangChain Blog](https://blog.langchain.com/exploring-prompt-optimization/)
- [プロンプトエンジニアリングとは？2026年最新版 | Findy](https://jp.findy-team.io/blog/ai-casestudy/prompt-engineering/)
