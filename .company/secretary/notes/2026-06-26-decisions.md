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
