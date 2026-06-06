---
type: index
---

# reading/

Obsidian で書く **人間の入力経路**。読書メモ・記事クリップ・思いつき・観察を放り込む場所。

## ルール

### ファイル命名
- `YYYY-MM-DD_topic.md` (例: `2026-06-06_payback-book-ch3.md`)
- スラッグは半角英数 + ハイフン。日本語可だが英数の方が後で扱いやすい
- フォルダは作らない。**タグで分類する**

### frontmatter
```yaml
---
date: 2026-06-06
tags: [book, payback, money-mindset]
source: "「payback」第3章"
---
```

- `date`: メモを書いた日 (記事生成のスコープに使う)
- `tags`: 必ず付ける。下記の語彙から
- `source`: 出典 (本・URL・YouTube タイトルなど)

### 推奨タグ語彙
**種別:** `#book` `#web` `#podcast` `#youtube` `#idea` `#observation` `#quote`
**テーマ:** `#fukugyou` `#ai-tool` `#note-strategy` `#money-mindset` `#productivity`

## 役割の分離

| フォルダ | 誰が書く | 用途 |
|---------|---------|-----|
| `.company/reading/` | **人間 (Obsidian経由)** | 外から仕入れた素材・思いつき |
| `.company/research/topics/inbox/` | AI (research-collect スキル) | Web リサーチの蓄積 |
| `.company/secretary/inbox/` | 秘書 (Claude Code 経由) | 雑多なメモ・クイックキャプチャ |

混ぜると後から「これ誰が書いた？」が分からなくなる。**必ず使い分ける**。

## AI からの読まれ方

- `note-article-generate` スキル: 記事生成時、日付 D の前後 7 日のメモを素材として読む
- タグが記事テーマと一致するメモは引用や挿話として優先採用される
- 大きいファイルは要約セクション (`## まとめ` `## 結論`) があればそこを優先

## ファイルテンプレート（最小）

```markdown
---
date: 2026-06-06
tags: [book]
source: ""
---

# タイトル

メモ本文。引用したい箇所は `>` で。

> ここは原文の引用。

ぼくの解釈：
- ...
```
