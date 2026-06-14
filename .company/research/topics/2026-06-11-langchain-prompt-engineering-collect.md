---
created: "2026-06-11"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering"]
sources: 6
post_ideas: 5
---

# LangChain プロンプトエンジニアリング 実例 — 収集メモ

## 収集テーマ
LangChain × プロンプトエンジニアリングの「実装例つき」最新情報。コード片・数字・固有名詞を持つものを優先。

---

### 1. Context Engineering の4戦略 (write / select / compress / isolate)
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行以内）:
  - LangChain が 2026 年のプロンプト戦略を「Context Engineering」として4つに整理 (write=外部永続化 / select=RAG で関連だけ取得 / compress=要約圧縮 / isolate=エージェント別に分離)
  - 「プロンプトエンジニアリング」は古い、これからは「コンテキストエンジニアリング」が主語になる
  - XML 形式は Claude に最適、バージョン管理とテストセット構築が必須
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChain が公式に発表した『Context Engineering 4戦略』を1枚にまとめた」→ Threads で図解スレッド化

---

### 2. LLM 推論性能は 3,000 トークンで劣化、実用は 150〜300 語
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行以内）:
  - 研究結果として LLM の推論性能は約 3,000 トークンを超えると低下し始める
  - 実用上のスイートスポットは 150〜300 語
  - 長いプロンプトを最初から書かず「必要な部分のみ反復的に追加」する設計に
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「俺がプロンプトを 2,000 字書いてた頃の話」→「実は 300 語が最適だった」反転構造

---

### 3. FewShotPromptTemplate の最小コード（英単語→日本語訳の例）
- ソース: https://takuya-genai.com/langchain-prompt-template/
- 公開日: 2025-02-11
- 要点（3行以内）:
  - 例ペア (apple→りんご / book→本 / dog→犬) を渡すと "cat" の訳が安定する
  - `examples` + `example_prompt` + `prefix` / `suffix` の4点セットでテンプレ化
  - 「出力形式を固定したい」場面で PromptTemplate より圧倒的に強い
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Few-shot って何？って言われたから、3行で答える」→ 3 例 + 質問 で十分という話

```python
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
examples = [
    {"word": "apple", "translation": "りんご"},
    {"word": "book", "translation": "本"},
    {"word": "dog", "translation": "犬"},
]
example_prompt = PromptTemplate(
    input_variables=["word", "translation"],
    template="英単語：{word}\n日本語訳：{translation}\n",
)
fewshot = FewShotPromptTemplate(
    examples=examples, example_prompt=example_prompt,
    prefix="以下の英単語の日本語訳を答えてください。\n",
    suffix="英単語：{word}\n日本語訳：",
    input_variables=["word"],
)
```

---

### 4. Dynamic Few-shot：SemanticSimilarityExampleSelector で「入力に近い例だけ」自動選択
- ソース: https://zenn.dev/tsuzukia/articles/8fc74bdb8770a5
- 公開日: 2023-08-26 (※古い記事だが概念は健在)
- 要点（3行以内）:
  - 例を全部渡すのではなく、ベクトル DB (Chroma/FAISS) に埋め込み、入力に近い `k` 件だけ動的に選ぶ
  - `k=2` が「コスト × 効果」の経験則ベスト (例を増やすほどトークンが膨らみ、矛盾も増える)
  - 「Few-shot を入れすぎて精度が落ちた」問題への直接の解答
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「Few-shot は多いほどいい、と思ってた俺へ。2 件で十分」→ k=2 という数字が刺さる

---

### 5. LangChain 0.3 で ChatPromptTemplate が「タプル直接渡し」になった
- ソース: https://reference.langchain.com/python/langchain-core/prompts/chat/ChatPromptTemplate
- 公開日: 0.3 系現行版
- 要点（3行以内）:
  - 0.2.24 以降、`("system", "...")` / `("human", "...")` のタプルを配列で直渡し可能に
  - `MessagesPlaceholder` で会話履歴を差し込める
  - 過去の `SystemMessagePromptTemplate.from_template(...)` のボイラープレートが消えた
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「LangChain のコード、半分の長さで書けるようになってた」→ Before/After 6 行で比較

```python
from langchain_core.prompts import ChatPromptTemplate
template = ChatPromptTemplate([
    ("system", "You are a helpful AI bot. Your name is {name}."),
    ("human", "{user_input}"),
])
prompt_value = template.invoke({"name": "Bob", "user_input": "What is your name?"})
```

---

## 注目トピック (即投稿化推奨)
- **Context Engineering 4戦略** (write / select / compress / isolate)
  - 概念が新しい (2026-02 発表)
  - 「プロンプトエンジニアリングは終わった」系の煽りタイトルで強い
  - 1 投稿に収まる粒度 (4 つ × 1 行)

## 補助ソース (本文未取得・参考リンク)
- https://docs.langchain.com/langsmith/prompt-engineering-concepts (公式コンセプト整理)
- https://jp.findy-team.io/blog/ai-casestudy/prompt-engineering/ (2026 年最新版 日本語解説)
- https://www.netjstech.com/2026/03/prompt-templates-langchain-example.html (2026-03 チュートリアル)

## 心得メモ
- Dynamic Few-shot の元記事 (#4) は 2023 年で古いが、`k=2 が経験則ベスト` という数字は今でも生きてる
- Context Engineering と「3,000 トークンで劣化」は同じソースなので、別投稿に分けて使う
