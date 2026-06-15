---
created: "2026-06-16"
topic: "Claude Code 最新アップデート"
status: completed
tags: ["weekly-collect", "claude-code", "anthropic", "agent-sdk", "fable5"]
sources: 7
post_ideas: 8
---

# Claude Code 最新アップデート (2026-06-16 収集)

昨日 (2026-06-15) の収集ファイルは v2.1.169〜174 (nested-subagent / --safe-mode / /cd / /usage) を扱った。
今日は **昨日カバーできなかった「6/15 施行の Agent SDK 課金変更」「Claude Fable 5」「fallback model / post-session hook / Bedrock region 自動読込」など見落としネタ** を補強する。

---

### 【最重要】Claude Agent SDK 課金変更が 2026-06-15 施行 (= 昨日から)
- ソース: https://ai-revolution.co.jp/media/claude-agent-sdk-billing-june-2026/
- ソース2: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-06-15 施行
- 要点 (3行以内):
  - チャット/IDE 対話は従来通り、`claude -p` / Agent SDK / GitHub Actions は **別プールの月次クレジット制** に分離
  - Pro=$20/月、Max 5x=$100/月、Max 20x=$200/月のクレジット枠を超えると停止
  - 業界分析では「軽量で12倍、重量自動化で150倍以上のコスト増」と試算
- 投稿アイデア:
  - 型: 朝学び型 / 夕失敗型 / 教育目的
  - 切り口: 「Claude Agent SDK の課金、昨日から完全に別枠になりました。Pro=$20/月クレジットを超えると止まる。CI で `claude -p` 回してた人は今日中に枠確認した方がいい」

---

### Claude Fable 5 が一般公開 (Mythos-class 初の汎用モデル)
- ソース: https://code.claude.com/docs/en/whats-new
- ソース2: https://aismiley.co.jp/ai_news/claude-code-update-summary-2026/
- 公開日: 2026-06-09 (Claude Code v2.1.170 で利用可能化)
- 要点 (3行以内):
  - Anthropic が Mythos クラス (Opus 4.8 の上位帯) の初の一般公開モデル「Fable 5」を発表
  - Claude Code v2.1.170 で `[1m]` 接尾辞の自動正規化を含む対応を追加
  - 「Mythos クラス = 安全性レビュー済みで一般利用 OK」になった最初の世代
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Anthropic、Opus 4.8 の上に Fable 5 を出してた。Mythos クラス初の一般公開モデル。Claude Code でも 2.1.170 から触れる。Opus シリーズが頭打ちじゃなかった」

---

### fallback model 設定 (落ちた時に自動で次のモデルへ)
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-06-06 (v2.1.166)
- 要点 (3行以内):
  - 設定で **最大3つまでフォールバック先モデルを順序指定** できるようになった
  - メインモデルが過負荷/エラー時に自動で 2 番目、3 番目へフェイルオーバー
  - 「Opus が混んでて止まる」あるある問題が設定 1 行で消える
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Claude Code、fallback model 3つまで設定できるようになってた。Opus → Sonnet → Haiku で並べとけば落ちない。設定 1 行で開発止まらなくなる」

---

### `post-session` フック (セッション終了時に自動アクション)
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-06-09 (v2.1.169)
- 要点 (3行以内):
  - セッション終了時に発火する `post-session` hook が追加
  - テスト一括実行・lint・slack通知・commit草案などの「終了後ワーク」を仕込める
  - 既存の pre-tool / post-tool フックの「セッション粒度版」
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Code に post-session フックが来てた。セッション閉じる時に自動で全テスト走らせて Slack に投げる、みたいなのが書ける。`/exit` 後に何が起きてるか把握してる人ほぼいない」

---

### Bedrock の AWS リージョンを `~/.aws` から自動読込
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-06-10 (v2.1.172)
- 要点 (3行以内):
  - Amazon Bedrock 経由で Claude Code を使う時、リージョン設定を `~/.aws` 設定ファイルから自動で拾うように
  - 環境変数で都度指定 (`AWS_REGION=...`) が要らなくなった
  - 社内で AWS Bedrock 経由で Claude 入れてる開発者の地味だけど効くやつ
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Claude Code on Bedrock、リージョンを `~/.aws/config` から自動で読むようになってた。AWS_REGION 環境変数いちいち書かなくていい。社内導入勢に効く」

---

### 否定ルール (deny pattern) で glob 対応 - `"*"` で全ツール拒否
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-06-06 (v2.1.166)
- 要点 (3行以内):
  - permission の deny ルールで glob パターン (`"*"` `"Bash(*)"` など) が使えるように
  - 「全ツール拒否しつつ allow リストで明示許可」の引き締め運用が書ける
  - 監査が厳しい職場向け = 「デフォルト deny + 明示 allow」の安全側設定が現実的に
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Claude Code の permission、deny ルールに glob 入った。`"*"` で全部止めて allow で明示開放、が一発で書ける。情シスにツッコまれてる人ほど効く」

---

### マーケットプレイスにプラグイン検索バー追加
- ソース: https://releasebot.io/updates/anthropic/claude-code
- 公開日: 2026-06-10 (v2.1.172)
- 要点 (3行以内):
  - プラグインマーケットプレイス閲覧時に検索バーが追加
  - 数百あるプラグインから目的のものを名前で絞れる
  - 5月の `/plugin` プロンプト内フィルタ機能のマーケット版
- 投稿アイデア:
  - 型: 昼進捗型 / 教育目的
  - 切り口: 「Claude Code のマーケットプレイスにやっと検索バーついた。プラグイン数百ある時代に『一覧スクロール』はキツかった。地味アップデートだが触る頻度は最強クラス」

---

### Pro/Max のレート制限 2 倍化 + ピーク時無制限化
- ソース: https://aismiley.co.jp/ai_news/claude-code-update-summary-2026/
- ソース2: https://code.claude.com/docs/en/whats-new
- 公開日: 2026-06 (週次でロールアウト)
- 要点 (3行以内):
  - Claude Code の 5 時間あたり利用上限が 2 倍化
  - Pro/Max でピーク時間帯のレート制限が撤廃された (ピーク時の頭打ちが消えた)
  - 一方で Agent SDK は別プール化で実質値上げ → 「対話は緩和 / 自動化は厳格化」の二極化
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「Claude Code、対話モードのレート上限 2 倍 + ピーク無制限。一方で Agent SDK は別プール。Anthropic は『人間が手で書く分は緩く、AI が AI を回す分は絞る』方向にハッキリ舵切った」

---

## まとめ・観察

今週の動きを 1 行で言うと:
- **対話モードは緩和 (上限 2 倍 + ピーク無制限)**
- **自動化モードは絞り込み (Agent SDK 別プール化、$20/$100/$200 のクレジット制)**
- **モデル階層が深くなる (Opus 4.8 の上に Fable 5 / Mythos-class)**

投稿戦略への含意:
- 「Agent SDK 課金変更」は昨日 (6/15) 施行で **時事性が最高** → 今日〜明日中の投稿が勝ち筋
- 「Fable 5」は Anthropic ファンの間で知名度低い→ 早めに触れた人が情報優位
- fallback model / post-session hook / Bedrock 自動読込 は **使ってる人が少ない地味機能** → 「実は出てる」型の朝学び投稿に最適

## ソース URL 一覧 (再掲)
- https://code.claude.com/docs/en/whats-new
- https://releasebot.io/updates/anthropic/claude-code
- https://ai-revolution.co.jp/media/claude-agent-sdk-billing-june-2026/
- https://aismiley.co.jp/ai_news/claude-code-update-summary-2026/
- https://www.ai-souken.com/article/claude-code-updates-2026
- https://cryptul.co.jp/insights/articles/009-claude-evolution-timeline
- https://uravation.com/media/claude-code-v2-1-101-30-releases-5-weeks-guide-2026/
