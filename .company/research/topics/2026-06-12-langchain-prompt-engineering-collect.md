---
created: "2026-06-12"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["weekly-collect", "langchain", "prompt-engineering", "claude"]
sources: 6
post_ideas: 7
---

# LangChain プロンプトエンジニアリング — 2026 実例まとめ

「LangChain × プロンプトエンジニアリング」を 2026 視点で再整理。**具体数値・コード設計・Claude 特化のコツ** だけ抽出した。「ふーん」で終わるやつは外している。

---

## 1. Claude 3 Haiku は few-shot で 11% → 75% に跳ねる（LangChain 公式実測）
- ソース: https://www.langchain.com/blog/few-shot-prompting-to-improve-tool-calling-performance
- 公開日: 2024-Q2（2026 でも引用され続けている定番ベンチ）
- 要点:
  - 0-shot 11% → 3 例を **messages 形式** で渡すと **75%**（Claude 3 Haiku, tool calling）
  - Claude 3 Sonnet も Query Analysis で 16% → 52%（意味的類似 3 例 / messages）
  - 例は **3 個で頭打ち**。9 個入れてもほぼ伸びない → コスパは「3 例」一択
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude にプロンプト 3 例足しただけで精度 11% → 75%。LangChain の検証データの話」

---

## 2. Claude は「文字列で system に貼る」より「messages で渡す」が圧勝
- ソース: https://www.langchain.com/blog/few-shot-prompting-to-improve-tool-calling-performance
- 公開日: 2024-Q2
- 要点:
  - 同じ 3 例でも、system プロンプトに文字列連結だと **改善ほぼなし**
  - `HumanMessage` / `AIMessage` を交互に並べる messages 形式に変えるだけで精度ジャンプ
  - GPT 系はこの差が出にくい → **Claude 固有の特性**
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Claude にお手本見せる時、system に書いてない？それやめて messages で渡すと別物になる」

---

## 3. Claude に効く構造化は Markdown じゃなく XML タグ
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026
- 要点:
  - Claude 向けは `<instructions>` `<context>` `<example>` の XML タグが「測定可能に」最良
  - few-shot 例も `<example>` で包むと差が出る
  - Markdown 見出し（`##`）でいいやと思いがちだが、Claude には XML を選ぶ
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude に Markdown でプロンプト書いてる人、XML タグに変えるだけで精度上がる」

---

## 4. LangChain が 2026 に整理した「コンテキスト管理 4 戦略」
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/ , https://blog.langchain.com/exploring-prompt-optimization/
- 公開日: 2026
- 要点:
  - **Write**（外部に逃がす）/ **Select**（RAG で取ってくる）/ **Compress**（要約圧縮）/ **Isolate**（エージェント毎に分離）
  - もう「上手い言い回し」じゃなく「コンテキストを設計する」フェーズ
  - Phil Schmid (Hugging Face) 発 → LangChain がフォーマライズ
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「2026 のプロンプトエンジニアリング、上手い文章書く時代は終わった。コンテキストを 4 つに分けて設計する話」

---

## 5. LCEL の最小実例「PromptTemplate ｜ LLM ｜ Parser」
- ソース: https://medium.com/@sajo02/building-production-ready-ai-pipelines-with-langchain-runnables-a-complete-lcel-guide-2f9b27f6d557 , https://www.netjstech.com/2026/03/chain-using-lcel.html
- 公開日: 2026-02 / 2026-03
- 要点:
  - LCEL（LangChain Expression Language）= パイプ `|` で部品を繋ぐ宣言的記法
  - `prompt | model | parser` の 3 行が「Hello World」レベル
  - **batch / streaming / async が無料でついてくる** = プロトタイプそのまま本番投入できる設計
  - `RunnableBranch` で分岐 → 監査・トレースしやすい（規制対応に強い）
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「LangChain LCEL、3 行で書ける。`prompt ｜ model ｜ parser` これだけで batch/stream/async 全部もらえる」

---

## 6. Reasoning は 3000 トークンで劣化する — 短く保つ理由
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026
- 要点:
  - Levy, Jacoby, Goldberg (2024) の実証 → **3000 トークン超で推論精度が落ちる**
  - 実践レンジは **150〜300 語**
  - 「全部入れれば賢くなる」は誤解。RAG で削るほうが精度出る
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「プロンプト長くするほど賢くなる、は嘘。3000 トークンで推論落ちる。150-300 語が黄金帯」

---

## 7. Few-shot は「正解例の質」より「入力空間の多様性」
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026（引用元 Min et al. 2022）
- 要点:
  - ラベル（出力）が完璧に正しくなくても、**入力例が多様**なら効く
  - 似た例 3 つより、**バラついた例 3 つ**
  - 「完璧な例集めるまで動けない」病に対する処方箋
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「Few-shot の例、完璧じゃなくていい。バラついた 3 例のほうが効く。Min らの研究で出てる」

---

## 結論（断定で）

- **Claude を LangChain で使うなら**、`FewShotChatMessagePromptTemplate` で messages 形式・3 例・XML タグ — この 3 点セットで効率最大化
- **2026 のフェーズは「言い回し最適化」から「コンテキスト設計」へ**。Write/Select/Compress/Isolate を意識する
- **LCEL の `prompt | model | parser` は最小で覚える**。あとは RunnableBranch で分岐すれば本番品質になる
- **長く詰めるな・例は多様に・XML で構造化** — この 3 つだけで多くのプロンプトは直る

## ネクストアクション
- [ ] 上記 7 ネタを `topics/inbox/` に投入（threads-create-post が拾える形に）
- [ ] 「Claude 3 Haiku 11% → 75%」だけ単独で朝学び型に即下書き化（数字インパクト最強）
- [ ] LCEL `prompt | model | parser` を gaku_ai_life で「コード見せ系」の昼進捗投稿として試作

## 参考リンク
- https://www.langchain.com/blog/few-shot-prompting-to-improve-tool-calling-performance
- https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- https://blog.langchain.com/exploring-prompt-optimization/
- https://medium.com/@sajo02/building-production-ready-ai-pipelines-with-langchain-runnables-a-complete-lcel-guide-2f9b27f6d557
- https://www.netjstech.com/2026/03/chain-using-lcel.html
- https://docs.langchain.com/langsmith/prompt-engineering-quickstart
