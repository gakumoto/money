---
created: "2026-06-01"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["langchain", "prompt-engineering", "ai-dev", "weekly-collect"]
sources: 7件
post_ideas: 6件
---

# LangChain プロンプトエンジニアリング 実例 — 収集まとめ

---

### PromptTemplate で「再利用できるプロンプト」を作る
- ソース: https://www.pinecone.io/learn/series/langchain/langchain-prompt-templates/
- 公開日: 継続更新（Pinecone 公式）
- 要点:
  - `PromptTemplate(input_variables=[...], template=...)` で固定部分と変数部分を分離
  - `FewShotPromptTemplate` で複数の例文をテンプレートに組み込める
  - `LengthBasedExampleSelector` でクエリ長に合わせて例文数を動的調整 → コスト削減
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「毎回コピペしてたプロンプト、LangChainの PromptTemplate に変えたら再利用できた話」

---

### LCEL（LangChain Expression Language）でチェーンを書く
- ソース: https://zenn.dev/yuta_enginner/articles/8707a2b818e3a9
- 公開日: 2025〜2026（Zenn記事）
- 要点:
  - `prompt | model | output_parser` のパイプ記法が現代の推奨スタイル（LCEL）
  - `ChatPromptTemplate.from_messages()` でシステムメッセージとユーザー入力を分離管理
  - `with_structured_output()` + Pydantic でJSON型の出力を強制できる
- 投稿アイデア:
  - 型: 教育目的 / 朝学び型
  - 切り口: 「LangChainのチェーンを `|` で繋ぐだけ。コード3行で構造化出力まで作れた」

---

### プロンプト最適化ベンチマーク（LangChain公式）
- ソース: https://www.langchain.com/blog/exploring-prompt-optimization
- 公開日: 2025〜2026（LangChain公式ブログ）
- 要点:
  - 5手法テスト：少数射撃 / メタプロンプティング / 反省付きメタ / プロンプト勾配 / 進化的最適化
  - Claude 3.5 Sonnet が最適化効果で最高スコア
  - 「最適化はプロンプトへの長期記憶書き込み」という考え方が新鮮
- 投稿アイデア:
  - 型: 深夜思考 / 教育目的
  - 切り口: 「LangChainがプロンプトを自動で改善する5つの手法を比較した。Claude Sonnetが一番伸びた」

---

### コンテキスト組み立てが2026年のプロンプト技術の核心
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年（推定）
- 要点:
  - 2026年時点の失敗の本質は「プロンプトの書き方」ではなく「コンテキストの組み立て方」
  - LangChainは4戦略を整理：write（外部保存）/ select（RAG）/ compress（要約）/ isolate（エージェント分離）
  - プロンプトエンジニアリングは独立職種として消滅しつつある（Fast Company 2025年報告）
- 投稿アイデア:
  - 型: 深夜思考 / 朝学び型
  - 切り口: 「AIエラーの原因はプロンプトじゃない。コンテキストの渡し方が9割、という話」

---

### Claude へのプロンプトは XML タグが最強という実証
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年
- 要点:
  - Claude への構造化は Markdown や番号リストより `<instructions>` `<context>` `<example>` タグが効果的
  - Few-shot例は `<example>` タグで囲む、参照は "Using the data in <context> tags..." と明示
  - Gemini は短い直接的プロンプトを好む → モデル別チューニングが必要
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claudeへのプロンプトに Markdown やめて XML タグ使い始めたら精度が上がった話」

---

### プロンプトエンジニアリング職の消滅とその後
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年
- 要点:
  - Fast Company: 2025年5月時点で「プロンプトエンジニア」の求人が68%減少
  - 生き残るスキル：コンテキスト設計 / 評価（eval）設計 / モデル差異の理解
  - 「プロンプトを書ける人」より「プロンプトを評価できる人」が希少に
- 投稿アイデア:
  - 型: 夜振り返り / 深夜思考
  - 切り口: 「プロンプトエンジニアという職種が消えた理由と、次に価値が上がるスキル」
