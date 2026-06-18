---
created: "2026-06-18"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering", "claude", "gemini"]
sources: 8
post_ideas: 8
---

# LangChain プロンプトエンジニアリング 実例（2026-06 最新リサーチ）

ユーザー指定テーマ「LangChain プロンプトエンジニアリング 実例」を WebSearch + WebFetch で深掘り。
2026年の最新ベスプラと、すぐコードに落とせる実装例を中心に整理。
gaku_ai_life の「AIで稼ぐ・AIを使いこなす実況」軸に直結する一次情報を優先。

---

### 1. Claude には XML タグが最強。Markdown でも箇条書きでもない

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - Claude は `<instructions>` `<context>` `<example>` の XML タグで構造化すると測定可能なほど精度上昇
  - Few-shot 例は `<example>` タグで囲うのが推奨
  - 命令文側からも「Using the data in <context> tags...」とタグ名で参照すると効く
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claudeに『**』とか**太字**で強調してたけど、公式ベスプラ読んだら XML タグが正解だった。`<example>` で囲うだけで体感で違う。」
  - もう1パターン: 「Claudeのプロンプト、Markdown で書いてたら損してました。」

---

### 2. Claude に「CRITICAL!」「YOU MUST」は逆効果

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - 新しい Claude モデルでは aggressive language が性能を下げる（過剰反応で精度落ちる）
  - 「CRITICAL!」「YOU MUST」「NEVER EVER」は冷静で直接的な指示より結果が悪い
  - 同じ手法は GPT-5 のルーター型でも逆効果（「think step by step」明示が裏目）
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「プロンプトに『絶対に！』『**重要**』入れまくってた1ヶ月前の自分、逆効果だった。Anthropic 公式が言ってる。」

---

### 3. Few-shot は 3〜5 個が黄金。1個でも10個でもない

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- ソース: https://book.st-hakky.com/data-science/langchain-fewshot-prompt-template
- 公開日: 2026-02-21 / Hakky 解説
- 要点（3行）:
  - Few-shot 例は 3〜5 個の「多様な例」がベスト
  - LangChain の `FewShotPromptTemplate` で `examples / example_prompt / prefix / suffix` を分けて管理する
  - 動的に選ぶなら `SemanticSimilarityExampleSelector` で `k=3` 前後で類似例を選択
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Few-shot 例、適当に1個だけ入れてた。3個に増やしただけで出力が安定した話。」
  - もう1パターン: 「LangChain の `FewShotPromptTemplate` 使うと、例を増やしても prompt がぐちゃらない。」

---

### 4. プロンプトキャッシングで API コスト90%減、レイテンシ85%減

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - Anthropic / OpenAI のプロンプトキャッシュ機能でコスト最大 **90%削減**、レイテンシ **85%短縮**
  - 「変わらない部分（システムプロンプト・大量例）」を先頭、「変わる部分（ユーザー入力）」を後ろに置くのが鉄則
  - LangChain でも `cache_control` を指定して同じ恩恵が受けられる
- 投稿アイデア:
  - 型: 夕進捗型 / 教育目的
  - 切り口: 「Claude API のコスト、月3万→3千円に落ちた。プロンプトキャッシュONにしただけ。」

---

### 5. Lost in the Middle：長文の中央に置いた情報は3割精度落ちる

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - 長いプロンプトの中央に埋め込まれた重要情報は **30%以上の精度低下**
  - 大事な指示・データは「先頭」か「末尾」に置く
  - 推論性能は 3,000 トークンを超えるあたりから低下、推奨は 150〜300 語
- 投稿アイデア:
  - 型: 夜思考型 / 教育目的
  - 切り口: 「プロンプトの真ん中に大事なこと書いてた人、自分です。中央に置くと3割精度落ちるらしい。」

---

### 6. Gemini はゼロショットNG、必ず Few-shot で。質問は最後

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - Google 公式の Gemini プロンプト白書は「ゼロショットは非推奨」と明記
  - 質問は **最後に**、データ・コンテキストの後に配置
  - Gemini は Claude / GPT より短く直接的なプロンプトを好む（コンテキスト窓は200万トークン）
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Gemini を Claude と同じ書き方で使ってた。ゼロショットNG、質問は最後、らしい。」

---

### 7. LangSmith Hub の `push_prompt` でプロンプトを Git みたいに管理

- ソース: https://docs.langchain.com/langsmith/prompt-engineering-quickstart
- 公開日: 2026年最新ドキュメント
- 要点（3行）:
  - `client.push_prompt("my-prompt", ChatPromptTemplate.from_messages(...))` で Hub にアップロード
  - 同名で `push_prompt` を繰り返すと自動で **新 commit** として履歴が残る
  - Playground から「Run an evaluation」でデータセット全体の性能テストができる
- 投稿アイデア:
  - 型: 制作ログ型 / 教育目的
  - 切り口: 「プロンプトを `.txt` で管理してた頃の自分にバイバイ。LangSmith Hub に push してから戻れない。」

---

### 8. 「役割プロンプト」は創造系だけ有効。分類・事実QAでは効かない

- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026-02-21
- 要点（3行）:
  - 「あなたは敏腕マーケターです」系の役割設定は **創造的タスクでのみ** 効果あり
  - 分類タスク・事実QAでは無効、もしくはむしろノイズになる
  - Tree-of-Thought / LATS は **99%のユースケースで不要**、CoT で十分
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「『あなたはプロのエンジニアです』を全プロンプトに入れてた。実は分類タスクでは無効、創造系限定だったらしい。」

---

## 追加参照ソース（深掘り用）

- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview — Zenn の体系本（日本語の入り口に最適）
- https://book.st-hakky.com/data-science/langchain-fewshot-prompt-template — FewShotPromptTemplate コード付き解説
- https://www.pinecone.io/learn/series/langchain/langchain-prompt-templates/ — Pinecone 公式のプロンプトテンプレ解説
- https://www.ibm.com/think/tutorials/prompt-chaining-langchain — IBM のプロンプトチェーン実装チュートリアル
- https://techblog.cccmkhd.co.jp/entry/2024/01/31/100712 — CCCMK ホールディングスの LCEL 実装事例
- https://terrierscript.com/ai/121/ — LangChain 完全実践ガイド（LCEL / Agent / LangGraph / LangSmith）

---

## 結論

2026年6月時点で「プロンプトエンジニアリング」は **モデル別の作法戦争** に入っている。
Claude=XMLタグ・冷静な命令、Gemini=Few-shot必須・質問最後、GPT-5=会話的・ゼロショット好み。
LangChain は「モデル切り替え」と「プロンプト履歴管理 (LangSmith Hub)」の両方を吸収する位置にいる。

ネタとして強いのは **数字付きで断定できる5本**：
- Few-shot は 3〜5 個
- キャッシュで コスト90%減 / レイテンシ85%減
- 中央配置で30%精度低下
- プロンプト長 150〜300 語が黄金
- aggressive language は逆効果

## ネクストアクション

- /threads-create-post で「数字付き5本」のうち1本を即下書き化する
- gaku_ai_life の「教育目的」枠に最適 → 翌日キューへ
- 有料note のネタとしても活用可（「LangChain 実装で詰まる箇所100選」系）
