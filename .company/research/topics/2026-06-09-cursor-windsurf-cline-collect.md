---
created: "2026-06-09"
topic: "Cursor / Windsurf / Cline 最新動向"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 6
post_ideas: 7
---

# Cursor / Windsurf / Cline — 2026-06-09 リサーチ

ユーザー指定テーマで AI コーディングエディタ3強の直近2週間（5月下旬〜6月7日）の動きをまとめた。

---

## ① Cursor 3.7 — Design Mode に「音声」と「複数選択」が乗った

- ソース: [Cursor Changelog 公式](https://cursor.com/changelog)
- 公開日: 2026-06-05
- 要点:
  - ブラウザ内 Design Mode で UI 要素を**複数選択して一括変更**できるように
  - エージェント実行中に**音声でナレーション**を流して変更指示できる
  - Composer 2 → Composer 2.5 への自動ルーティングで後方互換維持
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor が"声で UI 直す"段階に入った。コード書くんじゃなくて、画面見て喋るだけ。これに慣れたら戻れない」

---

## ② Cursor 3.7 SDK — 入れ子サブエージェントが「深さ無制限」に

- ソース: [Cursor Changelog 公式](https://cursor.com/changelog)
- 公開日: 2026-06-04
- 要点:
  - `local.customTools` で関数定義を渡せる Custom tools API
  - サブエージェントの**ネスト深度に上限なし**（unlimited depth）
  - SQLite 以外に JSONL / カスタムストアでの永続化が可能に
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「サブエージェントの中にサブエージェントを無限に呼べる時代。"並列に走らせる"が普通になった瞬間、1人で会社作れる」

---

## ③ Cursor 3.6 — Auto-review Run Mode でサンドボックス実行

- ソース: [Cursor Changelog 公式](https://cursor.com/changelog)
- 公開日: 2026-05-29
- 要点:
  - Shell / MCP / Fetch ツール呼び出しを**分類器で自動審査**してルーティング
  - 適格な呼び出しはサンドボックス内で自動実行
  - Settings > Agents > Run Mode から設定可能
- 投稿アイデア:
  - 型: 昼進捗型 / 信頼構築
  - 切り口: 「危ない rm -rf を AI が勝手に判定して隔離してくれる。"AI に任せる"の最後の壁が下がった」

---

## ④ Windsurf → Devin Desktop に正式改名

- ソース: [Windsurf Release Notes (Releasebot)](https://releasebot.io/updates/windsurf)
- 公開日: 2026-06-02
- 要点:
  - Windsurf が **Devin Desktop** に正式改名（Cognition の Devin と統合）
  - コマンドパレットから「rerun the migration from Windsurf」で移行可能
  - Claude Opus 4.8 が 2026-05-28 から利用可能（標準 $5/$25、Fast Mode $10/$50）
- 投稿アイデア:
  - 型: 夕失敗型 / 信頼構築
  - 切り口: 「Windsurf が消えて Devin Desktop になった。エディタ戦争は"名前ごと買われる"フェーズに突入してる」

---

## ⑤ Devin Local — 開いてるファイルを勝手に読むようになった

- ソース: [Windsurf Release Notes (Releasebot)](https://releasebot.io/updates/windsurf)
- 公開日: 2026-05-28
- 要点:
  - エディタで開いている**ファイルを自動でコンテキストに含める**ように
  - 「Always Allow」の MCP 権限が**セッションをまたいで永続化**
  - OS サンドボックス内で Plan Mode が機能改善
- 投稿アイデア:
  - 型: 深夜思考型 / 教育目的
  - 切り口: 「"開いてる＝コンテキスト"が標準になった。@file タグ打つ手間がもうない。AI 側が"今あなたが何を見てるか"を当然知ってる」

---

## ⑥ Cline SDK 公開 — 拡張機能から「エージェント実行基盤」へ

- ソース: [Cline 公式ブログ "Introducing Cline SDK"](https://cline.ghost.io/introducing-cline-sdk-the-upgraded-agent-runtime/)
- 公開日: 2026-05-13
- 要点:
  - `@cline/sdk` として**ランタイムをオープンソース化**
  - VS Code / JetBrains / CLI で同じ Cline が動く
  - Claude Opus 4.7 で **Terminal Benchmark 74.2%**（Claude Code 69.4%）
- 投稿アイデア:
  - 型: 朝学び型 / 販売（自分の差別化）
  - 切り口: 「Cline がついに"ただの拡張機能"じゃなくなった。SDK 公開で、誰でも自分の AI エージェント作れる土台が無料で配られた」

---

## ⑦ Cline v3.88 — Kimi K2.6 がデフォルトに

- ソース: [Cline GitHub Releases](https://github.com/cline/cline/releases)
- 公開日: 2026-06-05
- 要点:
  - Fireworks AI 経由で**Kimi K2.6 がデフォルトモデル**に
  - 公式 Cline プラグインを `github.com/cline/plugins` からインストール可能（CLI v3.0.16）
  - プラグインがスキルをバンドルできる構造に変更
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Cline のデフォルトが Claude じゃなくなった日。中国系モデル Kimi K2.6 が標準。"無料で OSS"の Cline、選択肢の自由度が異常」

---

## 横串：3強の立ち位置（2026-06 時点）

- ソース: [AIコーディング5強比較 / Uravation](https://uravation.com/media/ai-coding-tools-5-comparison-2026/)
- 公開日: 2026-06 月初
- 要点（料金）:
  - **Cursor**: $20 Pro 〜 $200 Ultra（クレジット制）
  - **Windsurf/Devin Desktop**: $20 Pro（2026-03 に $15 から値上げ）
  - **Cline**: OSS 無料 + API 実費（月 $5〜$50 目安）
- ユースケース別:
  - VS Code 乗り換え → **Cursor**
  - UI/コンポーネント量産 → **Windsurf**
  - セキュリティ・オフライン → **Cline**

- 投稿アイデア（総括型）:
  - 型: 夜振り返り型 / 信頼構築
  - 切り口: 「2026-06、AI エディタ"全部試す"はもう間違い。Cursor で 2 週間使い込んでから他を試す。これが正解ルートになった」

---

## 横串の気づき（編集メモ）

- 5月下旬〜6月の動きは「**音声入力 / サブエージェント無限ネスト / SDK 公開 / 改名**」と派手すぎる
- 共通方向は **"エディタを超えて、エージェント実行基盤に化ける"**
- Threads 投稿で刺さりそうな順:
  1. Windsurf → Devin Desktop 改名（驚き＋感情）
  2. Cursor の音声 Design Mode（未来感）
  3. Cline SDK 公開（無料＋OSS の正義感）
