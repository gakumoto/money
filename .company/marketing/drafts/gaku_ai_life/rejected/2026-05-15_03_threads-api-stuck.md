---
topic: "Threads API の投稿フローで詰まった話"
status: rejected
template_type: "#3 夕・失敗オープン型"
purpose: "信頼構築"
account: "gaku_ai_life"
created_at: 2026-05-14
target_publish: "2026-05-15T18:00:00+09:00"
publish_at: 2026-05-15T18:00:00+09:00
applied_feedback: ["失敗→学び型 (あわを。)", "固有名詞 (Threads API)", "数字 (3時間, 2ステップ)", "弱さ開示", "ですます基本"]
quality_check:
  hook_proper_noun: true
  hook_number: true
  hook_target_implied: true
  body_authority: true
  body_concrete: true
  body_vulnerability: true
  desumasu_basic: true
rejected_at: 2026-05-14T11:18:54
rejected_reason: これもAI副業してる人には難しい内容。 コードとか一度も触ったことのない人向けに 発信してる。
---

【本文】
Threads API の投稿で3時間ハマりました。

下書きをそのまま投げたら、
ずっと「処理中」のまま返ってこない。

正解は2ステップで、
コンテナ作成 → 公開、を分けて呼ぶ仕様でした。

ドキュメント読まずに飛び込んだぼくが悪いです。
明日からは公式読んでから書きます。
