# 2026-06-26 意思決定ログ

## D-0626-01 投稿取りこぼしゼロ化（A案・恒久対策）

**背景**: PCがオフ/スリープだとボットが発火せず、遅れた投稿は鮮度ガード(D-053)で `expired/` に捨てられていた。これが毎日の取りこぼしの主因。6/26朝も v1/v3 が埋もれていた。

**決定（オーナー承認: A）**: 2系統で対策。

1. **捨てずにスライド**（`scripts/threads_auto_post.py`）
   - `move_to_expired` で捨てる代わりに `reschedule_stale()` を新設。
   - 遅延下書きは元の時刻(HH:MM)を保ったまま、次の空き枠（衝突は20分以内で判定）へ publish_at を書き換えて queued に残す。
   - 朝枠は朝のまま・深夜は深夜のまま流れる（帯を維持）。
   - `reschedule_count` を刻み、`MAX_RESCHEDULE`(6)超で初めて expired に退避（無限延命防止）。

2. **ログオン追いつき**（Windowsタスク `myCompany-ThreadsCatchup-Logon`）
   - schtasks /Create /XML で登録（Register-ScheduledTask は 0x80070005 で拒否されたため）。
   - LogonTrigger（Delay PT1M）/ InteractiveToken / LeastPrivilege / StartWhenAvailable。
   - PCが朝オフでも、起動・ログオン1分後に1回 threads_auto_post を走らせ寝てた間の枠を拾う。

**検証**: 隔離テストで朝枠(7:00,2.5h遅れ)→翌々日7:00へスライド・queued維持を確認。実機でログオンタスクが v1(07:00) を実投稿（media_id 18044179082592547）。

**留意点**: status が `expired` のまま queued/ に手戻しするとボットが拾わない（`status: queued` に直す）。

関連: [[threads-autopost-schedule]]

## D-0626-02 投稿を1日15→7本に削減・型D/H/C主軸に（型別実数で決定）

**背景**: オーナーが「本数を減らしたい・どの型で投稿するか決めたい」。型別（hook_pattern A〜H）に実数集計（n=155）。

**判明**: ♡が付くのは **D（質問・呼びかけ／views中央151・♡20,16）/ H（動作・観察／♡率75%）/ C（失敗オープン・本音/節目／♡16,14）** の3型のみ。**E（対比・逆張り/警告）は最弱＝切る**。A（数字ノウハウ）はリーチは出るが♡11%＝1本のみ。死に枠＝13/19/21時。

**決定（オーナー: 7本/日）**: 固定の7枠×型に集約（既存タスク時刻に整合＝遅延ゼロ）。
06:30 B / 08:10 D / 10:30 A / 12:00 H / 16:30 F / 19:30 D / 22:50 C（06:30と22:50がgolden）。

**反映先**:
- `content-plan/gaku_ai_life-daily-post-framework.md`（post_per_day:7・新標準時間割）
- `.claude/skills/threads-daily-run/SKILL.md`（15→7本・§3を型固定表に・各枠のhook_pattern固定）
- `feedback/gaku_ai_life.md`（型別実数ルール・total_feedbacks 29）
- `research/topics/post-pattern-2026-06.md` 追記②（型別n=155の集計）
- `nightly_pipeline.py`（MAX_QUEUE 24→14・消費7本/日コメント）

**留意**: 既存の6/27バッチ(14本・旧15本構成)は土曜/時刻が本文に埋まるため温存。新7本構成は次の夜間生成分から適用。

関連: [[threads-autopost-schedule]]
