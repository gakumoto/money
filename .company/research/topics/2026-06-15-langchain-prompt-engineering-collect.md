---
created: "2026-06-15"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering", "lcel", "few-shot", "context-engineering"]
sources: 7件
post_ideas: 7件
---

# LangChain プロンプトエンジニアリング実例 収集 2026-06-15

---

### Prompt Optimization 5手法 — ~200% 精度向上 / 最強の最適化モデルは Claude Sonnet
- ソース: https://www.langchain.com/blog/exploring-prompt-optimization
- 公開日: 2025-01-28（LangChain 公式ブログ）
- 要点:
  - 検証された 5 手法: ①Few-shot prompting（最大50例埋め込み）②Meta-prompting（LLM に失敗分析させて改善案生成）③Meta-prompting + reflection（think/critique ツール追加）④Prompt gradients（失敗ごとに具体フィードバック）⑤Evolutionary optimization（突然変異・組合せ）
  - モデルが「知らないドメイン」のタスクで **約200% の精度向上** を確認
  - 最適化を回す「オプティマイザモデル」として **Claude Sonnet が o1 より一貫して安定**。これが LangChain 公式の推奨
  - 重要なのは「Few-shot は微妙なユーザー好みを伝えるのに強い、最適化は隠れたルール発見に強い」という補完関係。両方使うのが正解
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「プロンプト最適化に Claude Sonnet を使うと精度2倍になった LangChain 公式実験」「Few-shot と最適化は別物だった話」

---

### Few-shot プロンプティングで Tool Calling 精度が 11% → 75% に
- ソース: https://www.langchain.com/blog/few-shot-prompting-to-improve-tool-calling-performance
- 公開日: 2024-07-24
- 要点:
  - Multiverse Math（add 関数が `a+b+1.2` を返すなど演算を改変したベンチ）で **Claude 3 Haiku が 11%（ゼロショット） → 75%（3例 few-shot, メッセージ形式）**
  - Query Analysis（DocQuery/BlogQuery など適切なツールを選ばせる）で **Claude 3 Sonnet が 16% → 52%（3 例セマンティック検索で例選択）**
  - 「例を string ではなく messages 配列として渡す」「セマンティック類似で動的に例選択」が決定的に効く。静的 few-shot より高い
  - Few-shot を9例まで増やすと、Multiverse Math で全モデル最高性能
- 投稿アイデア:
  - 型: 朝学び型 / 失敗→学び型
  - 切り口: 「Tool Calling が動かない時、3例 few-shot 入れるだけで精度7倍」「Few-shot は string じゃなく messages 配列で渡せ」

---

### PromptTemplate / FewShotPromptTemplate / LengthBasedExampleSelector のコード雛形
- ソース: https://www.pinecone.io/learn/series/langchain/langchain-prompt-templates/
- 公開日: Pinecone Learn シリーズ（継続更新中、2026 でも参照される定番）
- 要点:
  - **PromptTemplate**: `template = "Context: ...\nQuestion: {query}\nAnswer:"` を `PromptTemplate(input_variables=["query"], template=template)` で包む。`.format(query=...)` で埋め込み
  - **FewShotPromptTemplate**: `examples=[{"query":..., "answer":...}]` のリストに `example_prompt`, `prefix`, `suffix`, `example_separator` を組み合わせる
  - **LengthBasedExampleSelector**: 入力クエリの単語数に応じて埋め込む例の数を自動調整。`max_length=50` で長いクエリの時は例を減らしトークン節約。短いクエリの時は例を増やす
  - これが LangChain のプロンプト 3 階層（静的 → Few-shot → 動的 Few-shot）の最小実装
- 投稿アイデア:
  - 型: 朝学び型 / コード共有型
  - 切り口: 「LangChain の Few-shot を “動的” にする LengthBasedExampleSelector が地味に強い」「プロンプトテンプレート 3 階層の使い分け早見表」

---

### Context Engineering — 2026 はチェーンからグラフへ、コンテキスト管理が主役
- ソース: https://www.langchain.com/blog/context-engineering-for-agents / https://github.com/langchain-ai/context_engineering
- 公開日: 2025-07（LangChain 公式提唱）
- 要点:
  - 「コンテキストウィンドウを各ステップで適切な情報で埋める技術」を Context Engineering と定義
  - 戦略は 4 つ: **write**（外部に永続化）/ **select**（RAG で取り出す）/ **compress**（要約圧縮）/ **isolate**（エージェントごとに分離）
  - LangGraph には short-term（checkpoint）と long-term の 2 種類のメモリが組み込まれていて、これが「スクラッチパッド」として機能
  - 「2024 = RAG の年 / 2025 = Agent の年 / 2026 = Stateful Orchestration の年」が業界の共通認識
- 投稿アイデア:
  - 型: 夜振り返り型 / 思考型
  - 切り口: 「プロンプトエンジニアリングはもう古い、これからは Context Engineering」「LangChain 公式が定義した 4 戦略 write/select/compress/isolate」

---

### LangSmith 流プロンプト運用 — Git ライクなバージョン管理を前提に組む
- ソース: https://docs.langchain.com/langsmith/prompt-engineering-concepts
- 公開日: LangChain 公式ドキュメント（2026 最新）
- 要点:
  - **Chat 形式（system/user/assistant）をデフォルトに**。Completion 形式より構造化されていてマルチターンに強い
  - プロンプトはコードから分離して **テンプレ + 変数 `{variable}`** で運用。F-string がデフォルト、条件分岐やループが必要なら Mustache
  - **ハッシュでフルバージョン管理 + `production`/`staging`/`v1` のヒューマンタグ**。コード変更なしで本番プロンプトを差し替えられる
  - 「PdM や非エンジニアこそが最良のプロンプトエンジニアになる」が LangSmith の思想 — ツールでサポートする前提
- 投稿アイデア:
  - 型: 教育目的 / 仕事 Tips
  - 切り口: 「プロンプトをコードに埋め込むのをやめた話」「LangSmith でプロンプトに git タグつけたら本番運用が楽になった」

---

### LCEL — `prompt | model | parser` のパイプ記法で宣言的に組む
- ソース: https://zenn.dev/umi_mori/books/prompt-engineer/viewer/lcel / https://book.st-hakky.com/en/data-science/langchain-lcel
- 公開日: 継続更新中、2026 でも有効
- 要点:
  - LCEL（LangChain Expression Language）= 宣言的にチェーンを書くための DSL
  - 基本形は **`chain = prompt | llm | output_parser`** の `|` 連結。Unix パイプ感覚
  - `Runnable` インターフェースに統一されていて、`.invoke()` / `.batch()` / `.stream()` / `.ainvoke()`（非同期）が全部使える
  - 3 種のテンプレートを `|` で組み込む: **PromptTemplate**（単純）/ **ChatPromptTemplate**（system/user/assistant）/ **FewShotPromptTemplate**（例埋め込み）
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「LangChain は `|` でつなぐだけになった件（LCEL 入門）」「`.invoke()` 覚えれば `.stream()` も `.batch()` も同じ。Runnable は強い」

---

### Chaining Prompts — 1 つのメガプロンプトより小さいプロンプトの連鎖が強い
- ソース: https://medium.com/@kaushalsinh73/chaining-prompts-in-langchain-best-practices-970abc937517
- 公開日: 2026 春時点で参照される best practice 系記事
- 要点:
  - 1 つの LLM 呼び出しに全部詰める「メガプロンプト」より、**1 タスク 1 プロンプト で連鎖** させる方がモジュール化・テスト・デバッグが楽
  - Claude 4.x 系は **指示を文字通り解釈** する傾向が強い。`<instructions>`, `<context>`, `<example>` の **XML タグ** で構造化するのが Claude 公式推奨（Markdown や番号付きより効く）
  - チェーン単位で評価データセットを用意して回帰テストを回せるのが LCEL/LangSmith の強み
- 投稿アイデア:
  - 型: 失敗→学び型
  - 切り口: 「メガプロンプト書くのやめてプロンプト連鎖にしたらデバッグが10倍楽になった」「Claude には Markdown より XML タグの方が効く（公式推奨）」

---

## 注目トピック（即投稿化推奨）

**「Few-shot を string ではなく messages 配列で渡せ」**（2 番目のエントリ）。
Claude 3 Haiku 11% → 75% の数字が衝撃的で、SE/AI 副業層が今日から試せる「朝学び」型として完璧。LangChain 公式ブログ出典なので信頼度も高い。

サブで「Context Engineering の 4 戦略（write/select/compress/isolate）」も "プロンプトエンジニアリングはもう古い" 切り口で深夜思考型に向く。
