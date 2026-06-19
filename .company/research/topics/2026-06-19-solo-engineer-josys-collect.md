---
created: "2026-06-19"
topic: "社内エンジニア1人体制 / ひとり情シス × AIノウハウ"
status: completed
tags: ["weekly-collect", "solo-engineer", "hitori-josys", "claude-code", "productivity"]
sources: 8
post_ideas: 6
---

# 社内エンジニア 1 人体制 / ひとり情シス ノウハウ収集 (2026-06-19)

ユーザー指定テーマ。本人の現状(社内エンジニア1人体制)とリンクする投稿ネタを抽出。

---

### Claude Code でひとり開発が「4人×6ヶ月」を 2ヶ月で完了した実例
- ソース: https://www.aihero.dev/cohorts/claude-code-for-real-engineers-2026-04
- 補強: https://medium.com/@ahmadshafey/what-i-learned-using-claude-code-as-an-engineering-manager-during-focus-week-e9a4538c953a
- 公開日: 2026-05 頃
- 要点（3行以内）:
  - ソロ開発者が「4人×6ヶ月」スコープを 2ヶ月で完了 → 約 3x 倍率(タスク構成で重み付け済)
  - 計画モード(Shift+Tab)で「探索→計画→実装→コミット」を段階分離するのがコツ
  - 1 週間 Focus Week で 9 つのドキュメント不一致発見、5 ファイル修正、238 行違反検出、3 PR を捌いた実績
- 投稿アイデア:
  - 型: 朝学び型 / 信頼構築
  - 切り口: 「社内で1人だけのエンジニアやってる。4人×6ヶ月の仕事を 2ヶ月で終わらせた人の話を読んで、自分のやり方が間違ってなかったと確信した」

---

### Claude Code Productivity Paradox: 1人の速度 ≠ 組織の成果
- ソース: https://collinwilkins.com/articles/claude-code-productivity-paradox
- 公開日: 2026-05〜06
- 要点（3行以内）:
  - 個人の merged PR は「+67%/日」でも、組織のデリバリー指標は変わらないことが多い
  - ボトルネックが「コード作成」から「コードレビュー」へ移動しているだけ
  - boilerplate は 10x、複雑ロジックは 2x — 効果は不均等。設計判断は改善されない
- 投稿アイデア:
  - 型: 夕方の気づき型 / 教育目的
  - 切り口: 「AI 使えば 10 倍速くなるって聞いた? 嘘じゃないけど本当でもない。コピペ作業は 10 倍、頭使う設計は 2 倍。社内で1人やってる自分の体感もまさにこれ」

---

### ひとり情シス 4フェーズ変革ロードマップ (Google Workspace × Cloud)
- ソース: https://ximix.niandc.co.jp/column/the-optimal-solution-and-roadmap-for-business-efficiency-that-breaks-through-the-limits-of-solo-and-small-it-departments
- 公開日: 2026-05〜06
- 要点（3行以内）:
  - Phase1: SaaS 棚卸し + SSO 統合でパスワードリセット作業を撲滅
  - Phase2: VPN 廃止 → Google Cloud 移行でゼロトラスト化
  - Phase3: AppSheet + Gemini で申請/ヘルプデスク自動化 → Phase4 戦略業務へ
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「ひとり情シスの4段階ロードマップを読んだ。①SSO ②ゼロトラスト ③AI自動化 ④戦略業務。自分は今 ③ の入口。Claude Code で社内ツール量産中」

---

### 前田建設工業: DAPツール導入で問い合わせ 35% 削減
- ソース: https://techtouch.jp/media/management/information-systems-department-assignment
- 公開日: 2026 春
- 要点（3行以内）:
  - 経費精算システムへの問い合わせが情シスを圧迫
  - DAP ツール「テックタッチ」導入で問い合わせ数 35% 削減
  - 「マニュアル整備 + チャットボット + RPA」の三点セットが定石
- 投稿アイデア:
  - 型: 昼の小ネタ型 / 信頼構築
  - 切り口: 「社内の問い合わせ、1人で全部捌くのキツい。前田建設は DAP 導入で 35% 減らしたらしい。自分は社内ツールで同じことやろうとしてる」

---

### ソロ開発者が今日から使える Claude Code 10 Tips (2026 版)
- ソース: https://www.f22labs.com/blogs/10-claude-code-productivity-tips-for-every-developer/
- 公開日: 2026-04〜05
- 要点（3行以内）:
  - `/init` で CLAUDE.md 自動生成、Shift+Tab で計画モード、`/agents` でサブエージェント
  - `/rewind` で失敗ロールバック、`/compact` で長時間セッションを要約
  - `.claude/commands/` でカスタムスラッシュコマンド作って反復作業を自動化
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Code、社内で1人エンジニアやってる自分が毎日使ってる5機能。①/init ②計画モード(Shift+Tab) ③/agents ④/rewind ⑤カスタムコマンド」

---

### ひとり情シスの本質課題: 属人化と退職リスク
- ソース1: https://service.shiftinc.jp/column/13023/
- ソース2: https://www.fgl-ts.co.jp/blog/josys01
- ソース3: https://johsyskun.com/journal/158/
- 公開日: 2026 通年
- 要点（3行以内）:
  - 設定/運用/トラブルシュートが特定担当者に集中 → 退職で業務停止
  - 24時間稼働の現場ストレス、休めない、ノウハウが社内に残らない
  - 解決策: アウトソース / 顧問契約 / **ドキュメント化(AI で加速可)**
- 投稿アイデア:
  - 型: 夜の振り返り型 / 共感喚起
  - 切り口: 「社内で1人エンジニアやってる人、これ読んでほしい。属人化・退職リスク・休めない。同じ悩み? 自分は Claude Code で全部ドキュメント化することで延命中」

---

## 次のアクション
- 即投稿化推奨: **#1 (4人×6ヶ月を2ヶ月)** と **#5 (Claude Code 10 Tips)** が本人の文脈とほぼゼロ距離
- #6 は共感型として強い (社内エンジニア1人の人に刺さる)
- 投稿時は本人の生活ファクト (バス通勤・社内1人体制・noteは新規) と矛盾しないよう注意
