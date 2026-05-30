---
type: research-watchlist
purpose: "自動リサーチで毎日チェックする対象一覧"
updated: 2026-05-14
---

# リサーチウォッチリスト

このファイルは `scripts/run_watchlist.py` が読み込む。
毎朝定期実行され、ここに登録された対象から自動でネタを収集する。

---

## 📺 YouTube

形式: `- <channel_url> | count:<本数> | <メモ>`

- https://www.youtube.com/@example1 | count:5 | ここに同業者チャンネルを追加
- https://www.youtube.com/@example2 | count:5 | 例: あわを。 / ソーダ式の人 など

**編集ルール**:
- `count` は 1〜20 (デフォルト 10)
- 行頭の `-` を `#` にすると無効化 (削除せず一時停止)

---

## 🔍 Web Themes (2026-05-16 大幅拡張・15 → 20 テーマ)

形式: `- <検索テーマ>`

### コア (毎日)
- Claude Code 最新アップデート
- Threads アルゴリズム
- AI 個人開発
- note 収益化
- 駆け出しSE 副業

### Threads 戦略系
- Threads フォロワー 増やし方 最新
- Threads アカウント 削除 リスク 対策
- Threads vs X 移行
- Threads マネタイズ事例

### AI ツール最新
- Anthropic Claude 最新ニュース
- ChatGPT vs Claude 比較 最新
- Cursor Windsurf Cline AI コーディング
- Sora AI 動画生成 個人開発
- LangChain プロンプトエンジニアリング 実例

### note / クリエイター系
- note プレミアム マガジン 戦略
- note 無料 有料 線引き 売れる
- AI 副業 確定申告 個人事業主

### 駆け出しSE / 個人開発
- 駆け出し SE 転職 副業 両立
- 社内エンジニア 1 人 体制 ノウハウ
- 個人開発 月 1 万円 の壁

**編集ルール**:
- 1 行 1 テーマ
- 行頭の `-` を `#` にすると無効化 (削除せず一時停止)
- 4 階層に分類: コア / Threads / AI ツール / note / 駆け出しSE
- 増やしすぎると 1 回の実行時間が伸びる → 20 テーマ前後を目安

---

## ⏰ 実行頻度（参考・タスクスケジューラ側で設定）

- **YouTube リサーチ**: 毎日 06:00 (字幕取得が重いので 1 日 1 回)
- **Web リサーチ**: 毎日 06:30 (軽いので毎日でOK)

実際の頻度はタスクスケジューラの設定が正。詳細は `scripts/SETUP.md`。

---

## 🔄 結果の活用

リサーチ結果は以下に保存される:
- YouTube: `.company/research/topics/youtube-YYYY-MM-DD.md`
- Web: `.company/research/topics/YYYY-MM-DD-collect.md`

これらは `/post_bulk` 実行時、`research/topics/inbox/` の未使用ネタとして
AI が自動参照する設計 (D-006)。
