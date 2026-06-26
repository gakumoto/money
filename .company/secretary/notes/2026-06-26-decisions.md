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

## D-0626-03 動画PR部門を新設

**背景**: オーナー「次の事業＝動画でのPR部門。Threads主・いけたらInstagram・YouTubeにも流す」。

**ヒアリング結果（決定）**:
- 顔出し: **なし**（画面/スライド/テロップ中心・声も当面出さない）
- 動画タイプ: **テキスト＋BGMの縦型スライド**（最速・量産・既存投稿文を流用）
- PR対象: **既存のAI副業ブランド（gaku_ai_life）**＝note導線強化

**設計の核**: **1本の縦型ショートを Threads/IGリール/YTショートに流し回す（1アセット3配布）**。台本は♡が付いた投稿(hook型D/H/C)を流用＝ゼロから書かない。検証→形が決まったら「投稿文→MP4自動生成」スクリプトで量産（SEの強み）。

**作成物**:
- `.company/video/CLAUDE.md`（部門ルール・フォーマット仕様・パイプライン）
- `.company/video/strategy.md`（戦略・KPI・立ち上げ計画・次アクションA/B/C）
- `.company/video/plans/2026-06-26_first-batch.md`（勝ちネタ3本のスライド台本＝Threads頑張ってる人♡20/最初の1ヶ月♡16/0円♡14）
- `.company/CLAUDE.md` 組織構成・部署一覧に「動画PR」追加

**次アクション（保留・オーナー選択）**: A=フォーマット試作1本を一緒に詰める / B=3本台本を完成→まとめ制作 / C=自動生成スクリプト設計から。

関連: [[studio-ai-company]]

## D-0626-04 note収益化の導線をokurihito 500円に集約

**背景**: オーナー「note・収益化の種まき／固定→note導線／最初の有料記事の設計」。棚卸しの結果、**有料記事はokurihito 500円が既に公開済**・他は未公開ドラフト多数。0円の原因は「商品が無い」でなく「導線が繋がっていない・目立っていない」。

**決定（オーナー）**: 主力＝**okurihito 500円**。新規で作らず、無料リード→500円の導線を繋ぐ。

**やったこと**:
- 無料リード「AI会社を作らせた話」(`articles/2026-06-21_ai-company-build.md`)の末尾を **okurihitoへ橋渡しするCTAに改稿**（廃止名「実験記」除去・「また書きます」予告除去）。status→ready-to-publish。
- 導線設計図 `products/note-funnel-design-2026-06.md` を作成（①Threads→②プロフ→③固定→④無料(物語)→⑤okurihito(手順)）。

**gaku手作業（note UIはこちら不可）**: ④をnote公開／⑤実URLを④末尾に貼る／⑤をnoteで注目ピン留め／固定からも④へ一言。

**Threadsソフト誘導**: 1日1本まで・1/3以下・未完型・22:50か16:30に月数回・危険ワード禁止。

関連: [[note-funnel-playbook]]
