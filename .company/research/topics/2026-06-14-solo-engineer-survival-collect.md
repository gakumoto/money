---
created: "2026-06-14"
topic: "社内エンジニア1人体制ノウハウ"
status: completed
tags: ["weekly-collect", "hitori-josys", "solo-engineer", "claude-code", "shikumika"]
sources: 8
post_ideas: 7
---

# 社内エンジニア 1 人体制 ノウハウ collect (2026-06-14)

## 収集テーマ
「社内に自分しかエンジニアがいない」状態で生き残る・成果を出すためのノウハウ。
ひとり情シス / ソロデベロッパー / 属人化対策 / AI 活用 の 4 角度。

---

## ソース別ファクト

### 1. ひとり情シス企業の AI 導入率は 17%（複数人体制の半分以下）
- ソース: https://news.neoscorp.jp/news-officebot-itsupport-survey/
- 公開日: 2026 年（調査期間 2025-09-22 〜 2025-12-12）
- 要点（3 行）:
  - ひとり情シス AI 導入率 **17%** / 複数人体制 **37%** / 関心あり **65%**
  - 導入予算は 71% が 300 万円以下、42% は 100 万円未満でスタート
  - 障壁は「人材不足」(**61%**)、目的は「人手不足の解消」(**71%**)
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「ひとり情シスの AI 導入率 17%。残り 83% は『何から始めればいいか分からない』で止まってる。月 2 万のツール 1 個から始めれば、それだけで上位 17% に入れる時代」

### 2. ITリテラシー教育を実施した企業の 86% が「期待以上の効果」を実感
- ソース: https://news.neoscorp.jp/news-officebot-itsupport-survey/
- 公開日: 2026 年
- 要点:
  - ツール導入だけでなく社内教育とセットで導入した企業の効果実感は 86%
  - 既存デジタル基盤（グループウェア等）の活用実績がある企業ほど成功率が高い
- 投稿アイデア:
  - 型: 夕失敗型 / 信頼構築
  - 切り口: 「AI 導入だけでは 86% の効果は出ない。社内教育とセットの企業だけが『期待以上』と答えてる。ツールより教育に金を使え」

### 3. Claude Code 利用で週 4.1 時間の節約、Anthropic 社内は出荷量 8 倍
- ソース: https://stormy.ai/blog/solo-founder-playbook-claude-code-startup
- ソース 2: https://blog.mean.ceo/the-solo-founder-ai-agent-stack-that-is-replacing-entire-startup-teams/
- 公開日: 2026 年
- 要点:
  - 日次ユーザーで **週 4.1 時間** 節約。自然言語で書いた機能が初回コードで動く確率 80%
  - Anthropic 社内のエンジニアは 2021-2025 比で **四半期出荷量 8 倍**、2026/5 時点でコードの 80% が自動化
  - MVP 到達時間が 4-6 ヶ月 → **4-8 週間**に短縮
- 投稿アイデア:
  - 型: 朝学び型 / 教育
  - 切り口: 「社内エンジニア 1 人でも Claude Code を入れると週 4 時間浮く。月 16 時間 = 丸 2 営業日。これを学習と仕組み化に回すと半年後に別人になる」

### 4. ソロ開発者の Plan-Execute Loop（Shift+Tab → TODO.md → 検証）
- ソース: https://stormy.ai/blog/solo-founder-playbook-claude-code-startup
- 公開日: 2026 年
- 要点:
  - `Shift+Tab` で Plan Mode 起動 → 詳細 `TODO.md` を出力させる → 開発責任者として計画レビュー → 1 タスクずつ実行・検証
  - `/compact` `/clear` でセッション最適化、`--chrome` で UI 確認、`.claude/CLAUDE.md` でプロジェクト DNA 定義
- 投稿アイデア:
  - 型: 昼進捗型 / 教育
  - 切り口: 「ひとりエンジニアの Claude Code 4 ステップ — ① Shift+Tab で計画モード ② TODO.md 出させる ③ レビュー ④ 1 個ずつ実行。これだけで自分が PdM 化できる」

### 5. 社内SE 属人化脱却の PDCA（テンプレ化 → MTTR 測定 → 改善）
- ソース: https://note.com/yukikkoaimanabi/n/n2da6813f31c1
- 公開日: 2026 年
- 要点:
  - Plan: 問い合わせフロー / 障害対応プロセスを明文化「誰でも同じ流れで動ける状態」
  - Do: 回答文・手順のテンプレ化、チェックリスト、ナレッジ蓄積
  - Check: **MTTR**（平均復旧時間）、再発率、一次解決率を数値で追う
  - Act: 再発障害の原因分析 → 手順書更新
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育
  - 切り口: 「ひとり社内SE が属人化から逃れる唯一の方法は MTTR を計ること。数字がないと改善のしようがない。エクセル 1 枚から始めればいい」

### 6. ドキュメント 4 点セット（チケット / 標準手順書 / ナレッジ / 運用設計書）
- ソース: https://note.com/yukikkoaimanabi/n/n2da6813f31c1
- ソース 2: https://www.lanscope.jp/tips/8797/
- 公開日: 2026 年
- 要点:
  - **チケット管理テンプレ**: 基本情報 / 内容 / 対応記録 / KPI 用データ
  - **標準手順書**: フロー図 + ステップ + チェックリスト + ハマりポイント
  - **ナレッジ記事**: 事象 / 原因 / 対応 / 再発防止 / 確認方法
  - **運用設計書**: 目的 / 対象システム / 体制 / SLA / KPI
- 投稿アイデア:
  - 型: 朝学び型 / 教育
  - 切り口: 「ひとり情シスのドキュメントは 4 枚で足りる — チケット・手順書・ナレッジ・運用設計書。これ以上書こうとすると続かない」

### 7. ソロファウンダー AI スタック（Cursor / Claude Code / Copilot で MVP は社内エンジニア採用不要）
- ソース: https://blog.mean.ceo/the-solo-founder-ai-agent-stack-that-is-replacing-entire-startup-teams/
- 公開日: 2026 年
- 要点:
  - 2026 年のブートストラップ標準スタック: Cursor + Claude Code + GitHub Copilot
  - MVP / 初期プロダクトイテレーションで **エンジニア採用が不要**になっている
  - 従来の月 $15,000（採用費）→ AI 駆動で **月 $500 未満**（API 利用料）に
- 投稿アイデア:
  - 型: 深夜思考型 / 教育
  - 切り口: 「社内エンジニア 1 人体制が成立する条件が変わった。2025 までは『無理してでも 2 人目を採れ』、2026 は『2 人目より Claude Code に $500 払え』。費用対効果が 30 倍違う」

### 8. AI を「アンプリファイア」と捉える 2025 DORA フレーム
- ソース: https://jellyfish.co/library/engineering-efficiency/
- 公開日: 2026 年
- 要点:
  - DORA は AI を「増幅器（amplifier）」と定義。土台のシステム・運用が悪いと AI でも成果は出ない
  - 1 人エンジニアでも「個人を計らず、チーム成果（スループット / 品質 / 安定性 / 満足度）で計れ」
- 投稿アイデア:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「AI は増幅器。スパゲッティコードに Claude Code を入れたらスパゲッティが 8 倍速で増えるだけ。先に仕組み化が要る」

---

## 注目トピック（即投稿化推奨）
**「ひとり情シス AI 導入率 17%」の数字は強い。**
- 競合データ（複数人体制 37%）
- 障壁の固有数字（人材不足 61%）
- 「上位 17% に入る」というポジティブ提示
の 3 点が揃っていて、朝学び型 1 本 + 教育目的 note 1 本のセットが組める。

## 投稿の型マッピング
- 朝学び型: #1（17% 数字）/ #3（週 4.1 時間）/ #6（4 枚ドキュメント）
- 昼進捗型: #4（Plan-Execute Loop 4 ステップ）
- 夕失敗型: #2（教育セットでないと 86% 出ない）
- 夜振り返り型: #5（MTTR 計測）/ #8（増幅器論）
- 深夜思考型: #7（採用費 vs API 費 30 倍差）

## 全ソース URL
- https://news.neoscorp.jp/news-officebot-itsupport-survey/
- https://stormy.ai/blog/solo-founder-playbook-claude-code-startup
- https://blog.mean.ceo/the-solo-founder-ai-agent-stack-that-is-replacing-entire-startup-teams/
- https://note.com/yukikkoaimanabi/n/n2da6813f31c1
- https://www.lanscope.jp/tips/8797/
- https://jellyfish.co/library/engineering-efficiency/
- https://qiita.com/op_yamaguchi/items/00790c15556f26c6e549
- https://prtimes.jp/main/html/rd/p/000000045.000153035.html
