---
created: "2026-06-03"
topic: "LangChain プロンプトエンジニアリング 実例"
status: completed
tags: ["langchain", "prompt-engineering", "ai-dev", "claude", "weekly-collect"]
sources: 6件
post_ideas: 6件
---

# LangChain プロンプトエンジニアリング 実例 — 収集まとめ（2026-06-03）

2026-06-01 の収集（同名ファイル）との差分: 今回は「数字で語れる Tips」「Claude 特化の言い方」「MCP × Caching の実例トークン数」など、**投稿1本に1ネタで刺せる粒度**を厚めに集めた。

---

### Claudeに「CRITICAL!」「YOU MUST」と書くと逆効果
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年（"2026 Best Practices"）
- 要点:
  - 新しい Claude モデルは「強い命令語」で精度が落ちる傾向（aggressive language actively hurts newer Claude models）
  - 「落ち着いた直接的な指示」が一番効く
  - Markdown より `<instructions>` `<context>` `<example>` の XML タグで構造化するのが Claude には最適
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claudeに『絶対！』『必ず！』って書くと逆に精度落ちるらしい。落ち着いて指示するのが一番効く」

---

### プロンプトは150〜300語が最適、3000トークンで性能が落ち始める
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年
- 要点:
  - 最適プロンプト長は 150〜300 語
  - 3,000 トークンを超えると推論性能が低下し始める
  - 「Lost in the Middle」現象で中間部分の情報は精度が 30% 以上落ちる
  - Chain-of-Thought で MMLU-Pro が 19 ポイント向上
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「プロンプトは『150〜300語』が最強らしい。長く書けば書くほど中間が無視されるって知ってた？」

---

### MCP × Prompt Caching で 21,786 → 519 トークン（97.5% カット）
- ソース: https://zenn.dev/ncdc/articles/26165a6fedd7e4
- 公開日: 2026年（Zenn ncdc）
- 要点:
  - MCP サーバー連携時、ツール定義だけで 1 ツール約 1,000 文字。複数サーバーで 10 万文字超になることも
  - Prompt Caching 導入前: `input_tokens: 21786` → 導入後: `input_tokens: 519, cache_read_input_tokens: 21097`
  - 全体の 97.5% がキャッシュヒット、コストは 75〜80% 削減
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「MCP繋いでたら毎回 2.1万トークン無駄に払ってた。Prompt Caching 入れたら 519 トークンになった話」

---

### LangChain 公式：5つの自動プロンプト最適化アルゴリズム比較
- ソース: https://www.langchain.com/blog/exploring-prompt-optimization
- 公開日: LangChain 公式ブログ
- 要点:
  - 5手法を比較: Few-shot / Meta-prompting / Reflection付きMeta / Prompt Gradients / Evolutionary（PhaseEvo）
  - 「ドメイン知識のない領域」では Evolutionary 系で約 200% 精度向上の場面あり
  - 単純な分類は Few-shot が依然強い
  - 最適化を回すための「ジャッジ役モデル」としては **Claude 3.5 Sonnet が最も安定**（OpenAI o1 より API 信頼性が高い）
- 投稿アイデア:
  - 型: 深夜思考 / 教育目的
  - 切り口: 「プロンプトを『自動で改善する』アルゴリズム5つを比較した結果、評価役は Claude 3.5 Sonnet が一番安定だった話」

---

### LangChain の「コンテキストエンジニアリング」4戦略
- ソース: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026/
- 公開日: 2026年
- 要点:
  - LangChain が体系化: **write（外部永続化）/ select（RAGで取り出し）/ compress（要約圧縮）/ isolate（エージェント別に分離）**
  - 「プロンプトが悪い」のではなく「コンテキストの組み立てが悪い」のが本番事故の主因
  - エージェント失敗の多くは『モデル失敗ではなくコンテキスト失敗』
- 投稿アイデア:
  - 型: 深夜思考 / 教育目的
  - 切り口: 「AIが失敗するのは『プロンプトが悪い』からじゃない。『コンテキストの組み立て』が悪いから。LangChainの4分類が腑に落ちた」

---

### PromptTemplate を「Base / Composition / Registry」で再利用すると工数 30〜50% 減
- ソース: https://t-cr.jp/article/2a71j4ogoa7s37k
- 公開日: 2026年（T-CREATOR）
- 要点:
  - 共通構造を持つ Base Template + ヘッダー/本文/フッターの Composition + 一元管理の Registry
  - 「新機能開発時の工数を 30〜50% 削減」と報告
  - セマンティックバージョニング（MAJOR/MINOR/PATCH）で出力フォーマット変更を管理
  - 評価は A/B テスト + Welch の t 検定で統計的に
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「プロンプトを『毎回コピペ』するのやめた。Base + Composition + Registry の3層に分けたら新機能のプロンプト書く時間が半分になった」

---

## 注目トピック（即投稿化推奨）

**「Claudeに『絶対！』『必ず！』って書くと逆効果」**

理由:
- 数字で語れる（Markdown vs XML、150〜300語、19ポイント上昇）
- AI使ってる人の常識を裏切る（強調するほど良いと思ってる人が多い）
- gaku_ai_life のキャラに合う（実体験ベースの気づき型として書ける）
- 「ぼくもやってた」と1人称で入れる導線が組める
