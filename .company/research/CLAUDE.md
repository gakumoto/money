# リサーチ

## 役割
市場調査、競合分析、トレンド調査を行う。Threadsの投稿ネタや、有料記事・教材のテーマ仕入れを担当する。
**過去の高反応投稿・低反応投稿のパターン分析もここで蓄積する**（AIスタッフの精度UP用）。

## 書いてはいけないこと
レポート本文も以下を守る：
- ❌ 「〜かもしれません」 → **断定する**（推測なら「仮説」と明示）
- ❌ 「皆さん」 → **1人称**
- ❌ 本文中の絵文字

## ルール
- 調査ファイルは `topics/topic-name.md`
- ステータス: planning → in-progress → completed
- 情報源は必ずURLまたは出典を記載
- 調査結果には必ず「結論」と「ネクストアクション」を含める
- 調査完了時は秘書のTODOに報告を追記
- 競合のThreadsアカウント分析は `topics/competitor-アカウント名.md` で管理
- 投稿パフォーマンス分析は `topics/post-pattern-YYYY-MM.md` で月次蓄積

## フォルダ構成
- `topics/` - 調査トピック（1トピック1ファイル）
- `topics/inbox/` - **ネタ inbox**（Discord `/idea` コマンドが自動投入する場所）

## ネタ inbox の使い方（2026-05-13 追加・最重要）

`topics/inbox/` には Discord の `/idea` コマンド経由でオーナーが「思いつき・観察・気づき」を蓄積する。
AI スタッフ（特に **threads-create-post** と **threads-daily-run**）は、下書き生成前に必ずこのフォルダを読み込む。

### AI スタッフが守ること

1. **生成前に inbox をスキャン**: `status: unused` のネタを優先素材として扱う
2. **使ったネタはマーク**: 下書きで採用したネタの frontmatter を `status: used` + `used_in: <draft_path>` に更新
3. **重複利用しない**: `status: unused` のものだけを 1 回の生成で 1 度使う
4. **カテゴリ偏り防止**: 同じ category のネタばかり連続して使わない
5. **ネタが少なければ**: 過去の高反応投稿 / `feedback/<account>.md` の「良かった例」から型を借りる

### ファイル形式

```markdown
---
type: idea
created: 2026-05-13T23:50:00+09:00
category: "観察"      # 任意。AI / 失敗 / 観察 / 当たり訴求 / SE / note / 深夜 など
source: discord_bot   # discord_bot / yt-research / manual など
status: unused        # unused → used
used_in: ""           # 採用された下書きのパス (used 時)
used_at: ""           # 使用時刻 (used 時)
---

ネタ本文（1〜数行）
```

### ファイル名規約

`YYYYMMDD_HHMMSS_<slug>.md` （Discord 経由は自動）

オーナーが手動で追加する場合も同じ規約を守る。`research-collect` Skill 経由で YouTube リサーチ結果が流れ込む時も同様。
