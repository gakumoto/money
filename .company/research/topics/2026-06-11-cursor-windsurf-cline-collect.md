---
created: "2026-06-11"
topic: "Cursor / Windsurf / Cline / AI コーディングツール"
status: completed
tags: ["weekly-collect", "ai-coding", "cursor", "windsurf", "cline"]
sources: 8件
post_ideas: 7件
---

# AI コーディングツール最新情報 2026-06-11

## 収集テーマ
Cursor / Windsurf / Cline の最新動向・比較・数字・選び方

---

### Cursor 3.1：Canvas 機能で AI が React UI を直接生成
- ソース: https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/
- 公開日: 2026-04-16（Cursor 3.1 リリース）
- 要点:
  - Agents Window 内に「永続的アーティファクト」として React UI を表示
  - ダッシュボード・チャート・テーブル・diff を AI が直接描画
  - 「コードを書いて → プレビュー」が「会話して UI が出る」に変わった
- 投稿アイデア:
  - 型: 朝学び型 / 教育目的
  - 切り口: 「Cursor 3.1 の Canvas、React の UI が AI から直接出てきた。"コード書いてプレビュー" の時代が終わった話」

---

### Composer 2.5（2026-05-18）
- ソース: https://tomyunser.com/cursor-ai-editor/
- 公開日: 2026-05-18
- 要点:
  - Cursor の Composer が 2 → 2.5 に進化
  - 複数ファイル横断の編集精度が上がった
  - GPT-5.5 と組み合わせて使えるモードが追加
- 投稿アイデア:
  - 型: 昼進捗型
  - 切り口: 「Composer 2.5、5 ファイル一括書き換えが 1 発で通った。"AI に任せる範囲" がまた一段広がった」

---

### Cursor 3.7：Design Mode で UI を音声で直す
- ソース: https://uravation.com/media/cursor-3-agent-ide-complete-guide-2026/
- 公開日: 2026 年（最新マイナー）
- 要点:
  - ブラウザの Design Mode で UI をクリック・描画・音声で修正指示できる
  - デザイナー的な操作で AI に変更を渡せる
  - エンジニアでない人が UI を直せる入口になりつつある
- 投稿アイデア:
  - 型: 夜振り返り型 / 教育目的
  - 切り口: 「Cursor の Design Mode、ボタン位置を口で言ったら動いた。"非エンジニアが UI を直せる入口" が来た」

---

### Windsurf：SWE-1.5 と Cognition AI 買収
- ソース: https://weavai.app/blog/en/2026/04/24/windsurf-ai-review-2026-cascade-agent-efficiency/
- 公開日: 2026-04-24
- 要点:
  - 2025-07 に Devin の Cognition AI が Windsurf を約 2.5 億ドルで買収
  - 独自モデル SWE-1.5 が「世界最速クラスのコーディングモデル」を名乗る
  - Cascade エージェントが「リアルタイムに開発者の動きを認識して一緒に動く」設計
- 投稿アイデア:
  - 型: 朝学び型
  - 切り口: 「Windsurf が Devin の会社に買収されてた。"AI エディタ" と "自律エージェント" の境目が消える流れ」

---

### Windsurf 料金体系：クレジット制 → クォータ制（2026-03）
- ソース: https://aipicks.jp/mag/windsurf-guide-2026
- 公開日: 2026-03
- 要点:
  - クレジット消費式から月額クォータ式に変更
  - Free: 月 50 Flow Action / Pro: $15 で無制限 Cascade
  - 新しい Max プランも追加された
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Windsurf がクレジット制やめてクォータ制に。"使うほど怖い" から "月額固定で全力" に変わった話」

---

### Cline v3.78：Spend Limit Reached UI（2026-04）
- ソース: https://kilo.ai/articles/coding-agents-for-vscode
- 公開日: 2026-04
- 要点:
  - 暴走エージェントが API クレジットを溶かす問題に対し専用 UI を実装
  - Settings → Spending Limits で日次/月次キャップを設定できる
  - 「AI に任せる怖さ」を仕組みで解決した最初の波
- 投稿アイデア:
  - 型: 夕失敗型 / 教育目的
  - 切り口: 「Cline が "Spend Limit Reached" UI を入れた。AI コーディングは "止める仕組み" がない方が事故る、という反省の話」

---

### Cline：30 プロバイダ対応・Plan/Act モード
- ソース: https://www.deployhq.com/guides/cline
- 公開日: 2026
- 要点:
  - 対応プロバイダが 30 を超えた（Anthropic / OpenAI / Gemini / Bedrock / Groq / Ollama 他）
  - Plan モード = 読み取り + 推論、Act モード = ステップ毎承認で実行
  - VS Code 以外に JetBrains / Cursor / Windsurf / Zed / Neovim でもサイドバーとして動く
- 投稿アイデア:
  - 型: 教育目的
  - 切り口: 「Cline、Cursor の上でも Windsurf の上でも動く。"エディタ戦争" の真ん中で "全部に乗る OSS" が静かに勝ち筋つくってる」

---

### 比較まとめ：Cursor / Windsurf / Cline の使い分け
- ソース: https://uravation.com/media/ai-coding-tools-5-comparison-2026/
- 公開日: 2026-11（最新比較）
- 要点:
  - Cursor: チーム展開しやすい No.1、リファクタ強い、初心者にも使いやすい
  - Windsurf: UI 量産・Cascade の文脈理解が強み、月 $15 で全部入り
  - Cline: OSS・ローカルモデル・自己コスト管理・高カスタマイズ
  - 推奨: 「日常は Cursor or Windsurf、大規模タスクは Cline」
- 投稿アイデア:
  - 型: 教育目的 / 朝学び型
  - 切り口: 「Cursor / Windsurf / Cline、どれが一番？って毎週聞かれるから一行で答える。"日常 = Cursor or Windsurf、しんどい時 = Cline"」

---

## 注目トピック（即投稿化推奨）

**Cline の Spend Limit Reached UI**：
「AI に任せる怖さ」を仕組みで解決した最初の波。失敗談として書きやすく、共感を取りやすい。
gaku_ai_life の「実体験 × 数字」で書ける素材。Threads 向きの "夕失敗型" にハマる。

## ネクストアクション
- 上記 7 つのうち、最低 2 つは今日の `/threads-create-post` で下書きに落とす
- Cline の Spend Limit UI → "AI 暴走で○○円飛ばした" 系の失敗談として再構成可能
- 比較まとめ → 「結局どれ？」系の質問返し投稿として再利用可能
