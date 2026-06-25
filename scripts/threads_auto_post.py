"""Threads に自動投稿.

drafts/<account>/queued/ にある下書きを時刻指定で投稿し、
投稿後は posted/<account>/YYYY-MM-DD_HHMM_<media_id>.md に移動する.

使い方:
    python scripts/threads_auto_post.py <account> [--dry-run]
    python scripts/threads_auto_post.py gaku_ai_life

Windows Task Scheduler で 1日3回 (07:00 / 12:00 / 18:00) 実行する想定.
キュー内で投稿時刻が来ているもの (publish_at <= now) を1本投稿する.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

# Windows の cp932 対策
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")
PROJECT_ROOT = SCRIPT_DIR.parent

# 鮮度ガード（2026-06-16 D-053）: publish_at から STALE_MINUTES 以上遅れた下書きは
# 「時間帯がズレた」とみなして投稿せず expired/ に退避する。
# 例: PC が寝てて深夜枠が出せず、朝のタスクで深夜投稿が繰り上がって流れる事故を防ぐ。
# 帯内のズレ(同帯で +30〜60分遅れ)は許容し、帯をまたぐ大遅延(深夜→朝=6h+)だけ落とす。
import os  # noqa: E402

STALE_MINUTES = int(os.getenv("THREADS_STALE_MINUTES", "120"))

sys.path.insert(0, str(SCRIPT_DIR))
from _threads_api import ThreadsClient  # noqa: E402
from _discord import notify  # noqa: E402
from _net_wait import wait_for_network  # noqa: E402


def parse_draft(path: Path) -> dict:
    """下書きファイルからfrontmatterと本文を抽出.

    本文は 【本文】 と 【コメント欄】 の間を取得.
    publish_at が frontmatter にあれば dt として返す.
    """
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        raise ValueError(f"frontmatter が見つからない: {path}")
    fm_str, body = m.group(1), m.group(2)

    fm: dict = {}
    for line in fm_str.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")

    # 本文抽出: 【本文】 〜 (【コメント欄】 / 【補足...】 等のメタ見出し or EOF)
    # ★2026-06-14: 生成スキルが【補足/分析】を本文の後ろに付けるため境界に含める。
    #   含めないと内部メモごと投稿される事故になる（6/16-17分の queued で検出）。
    body_match = re.search(
        r"【本文】\s*\n(.*?)(?=\n【コメント欄】|\n【補足|\Z)", body, re.DOTALL
    )
    main_text = body_match.group(1).strip() if body_match else body.strip()

    # コメント欄
    comment_match = re.search(r"【コメント欄】.*?\n(.*)", body, re.DOTALL)
    comment_text = comment_match.group(1).strip() if comment_match else ""

    return {
        "frontmatter": fm,
        "main_text": main_text,
        "comment_text": comment_text,
    }


def find_due_drafts(account: str, now: dt.datetime) -> list[Path]:
    """queued/ の中で publish_at が now 以前のものを返す.

    publish_at が無いものはファイル名先頭の日時 (YYYY-MM-DD_NN_...) を使う.
    """
    queued = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "queued"
    if not queued.exists():
        return []
    due = []
    for f in sorted(queued.glob("*.md")):
        try:
            d = parse_draft(f)
            pub = d["frontmatter"].get("publish_at", "").strip()
            if pub:
                try:
                    pub_dt = dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))
                    if pub_dt.tzinfo is None:
                        pub_dt = pub_dt.replace(tzinfo=dt.timezone.utc).astimezone()
                except ValueError:
                    continue
                if pub_dt <= now.astimezone(pub_dt.tzinfo):
                    due.append(f)
            else:
                # publish_at が無いものは即時OK扱い
                due.append(f)
        except (ValueError, OSError):
            continue
    return due


def move_to_posted(
    path: Path, account: str, media_id: str, posted_at: dt.datetime
) -> Path:
    """投稿済みファイルを posted/<account>/ に移動し、frontmatter を更新."""
    posted_dir = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "posted"
    posted_dir.mkdir(parents=True, exist_ok=True)
    ts = posted_at.strftime("%Y-%m-%d_%H%M")
    new_name = f"{ts}_{media_id}_{path.name}"
    new_path = posted_dir / new_name

    text = path.read_text(encoding="utf-8")
    # frontmatter に status を published に変える + 投稿情報を追記
    text = re.sub(
        r"(status:\s*)\w+",
        r"\1published",
        text,
        count=1,
    )
    posted_info = (
        f"posted_at: {posted_at.isoformat(timespec='seconds')}\n"
        f"threads_media_id: {media_id}\n"
    )
    # frontmatter の末尾 (--- の直前) に追記
    text = re.sub(r"\n---\s*\n", f"\n{posted_info}---\n", text, count=1)

    new_path.write_text(text, encoding="utf-8")
    path.unlink()  # 元の queued を削除
    return new_path


def publish_dt_of(path: Path):
    """下書きの publish_at を tz 付き datetime で返す。無ければ None。"""
    try:
        d = parse_draft(path)
    except (ValueError, OSError):
        return None
    pub = d["frontmatter"].get("publish_at", "").strip()
    if not pub:
        return None
    try:
        pub_dt = dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))
    except ValueError:
        return None
    if pub_dt.tzinfo is None:
        pub_dt = pub_dt.replace(tzinfo=dt.timezone.utc).astimezone()
    return pub_dt


def move_to_expired(path: Path, account: str, reason: str) -> Path:
    """時間帯がズレた下書きを expired/<account>/ に退避（投稿しない）."""
    expired_dir = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "expired"
    expired_dir.mkdir(parents=True, exist_ok=True)
    new_path = expired_dir / path.name
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(status:\s*)\w+", r"\1expired", text, count=1)
    note = f"expired_reason: \"{reason}\"\nexpired_at: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}\n"
    text = re.sub(r"\n---\s*\n", f"\n{note}---\n", text, count=1)
    new_path.write_text(text, encoding="utf-8")
    path.unlink()
    return new_path


# スライド時の衝突判定幅（分）: 既存キューの publish_at とこの幅以内なら同枠とみなす。
SLOT_COLLISION_MIN = 20
# 1本のスライド上限。これを超えても枠が空かない場合だけ expired に落とす（無限延命防止）。
MAX_RESCHEDULE = 6


def queued_publish_times(account: str, exclude: Path | None = None) -> list[dt.datetime]:
    """queued/ 内の publish_at(tz付き) 一覧。exclude は自分自身を除外用."""
    queued = PROJECT_ROOT / ".company" / "marketing" / "drafts" / account / "queued"
    out: list[dt.datetime] = []
    if not queued.exists():
        return out
    for f in queued.glob("*.md"):
        if exclude is not None and f.resolve() == exclude.resolve():
            continue
        pd = publish_dt_of(f)
        if pd is not None:
            out.append(pd.astimezone())
    return out


def reschedule_stale(path: Path, account: str, now_aware: dt.datetime, orig_pub: dt.datetime) -> Path:
    """鮮度切れの下書きを捨てず、時間帯(時刻)を保ったまま次の空き枠へスライドする.

    - 元の時刻(HH:MM:SS)を維持 → 朝の投稿は朝のまま、深夜は深夜のまま流れる
    - now+30分より後で、既存キューと SLOT_COLLISION_MIN 以内に重ならない最初の日を探す
    - MAX_RESCHEDULE 回スライドしても枠が無ければ expired/ に退避（無限延命防止）
    """
    # スライド回数をカウント（規定超で諦める）
    try:
        d = parse_draft(path)
        count = int(d["frontmatter"].get("reschedule_count", "0") or "0")
    except (ValueError, OSError):
        count = 0
    if count >= MAX_RESCHEDULE:
        return move_to_expired(
            path, account, f"{MAX_RESCHEDULE}回スライドしても枠が空かず・退避"
        )

    target_time = orig_pub.astimezone().timetz()  # 維持する時刻(tz付き)
    occupied = queued_publish_times(account, exclude=path)
    buffer = now_aware + dt.timedelta(minutes=30)

    cand_date = now_aware.date()
    chosen = None
    for _ in range(0, 21):  # 最大3週間先まで空き枠を探す
        cand = dt.datetime.combine(cand_date, target_time)
        collides = cand <= buffer or any(
            abs((cand - o).total_seconds()) < SLOT_COLLISION_MIN * 60 for o in occupied
        )
        if not collides:
            chosen = cand
            break
        cand_date += dt.timedelta(days=1)

    if chosen is None:
        return move_to_expired(path, account, "3週間先まで空き枠なし・退避")

    text = path.read_text(encoding="utf-8")
    new_iso = chosen.isoformat(timespec="seconds")
    # publish_at を書き換え
    if re.search(r"^publish_at:.*$", text, re.MULTILINE):
        text = re.sub(r"^publish_at:.*$", f"publish_at: {new_iso}", text, count=1, flags=re.MULTILINE)
    else:
        text = re.sub(r"\n---\s*\n", f"\npublish_at: {new_iso}\n---\n", text, count=1)
    # status は queued のまま維持（expired にしない）
    text = re.sub(r"(status:\s*)\w+", r"\1queued", text, count=1)
    # reschedule_count を更新 / 追記
    if re.search(r"^reschedule_count:.*$", text, re.MULTILINE):
        text = re.sub(r"^reschedule_count:.*$", f"reschedule_count: {count + 1}", text, count=1, flags=re.MULTILINE)
    else:
        text = re.sub(r"\n---\s*\n", f"\nreschedule_count: {count + 1}\n---\n", text, count=1)
    path.write_text(text, encoding="utf-8")
    return path


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    account = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # スリープ復帰直後の DNS 不安定対策: ネット復帰まで最大3分待つ
    if not dry_run:
        if not wait_for_network():
            msg = f"[auto_post] ネット復帰待ちタイムアウト ({account}): 投稿をスキップ"
            print(msg, file=sys.stderr)
            notify(msg)
            sys.exit(1)

    now = dt.datetime.now()
    due = find_due_drafts(account, now)

    if not due:
        print(f"[auto_post] {account}: 投稿対象なし ({now.strftime('%H:%M')})")
        sys.exit(0)

    # 鮮度ガード (D-053 → 2026-06-26 改修): 古い順に見て、STALE_MINUTES 以上
    # 遅れたものは「時間帯がズレた」とみなす。ただし捨てずに、時刻を保ったまま
    # 次の空き枠へスライドして queued に残す（取りこぼしゼロ化・A案）。
    # 最初の「鮮度OK」な1本を投稿する。
    now_aware = now.astimezone()
    target = None
    for f in due:
        pub_dt = publish_dt_of(f)
        if pub_dt is not None:
            late_min = (now_aware - pub_dt.astimezone()).total_seconds() / 60
            if late_min > STALE_MINUTES:
                if dry_run:
                    print(f"[auto_post] (dry-run) 鮮度切れ→スライド対象: {f.name} ({int(late_min)}分遅れ)")
                else:
                    moved = reschedule_stale(f, account, now_aware, pub_dt)
                    if moved.parent.name == "expired":
                        print(f"[auto_post] スライド上限/枠無し→退避: {f.name} -> expired/")
                    else:
                        new_pub = publish_dt_of(moved)
                        when = new_pub.strftime("%m/%d %H:%M") if new_pub else "?"
                        print(f"[auto_post] 鮮度切れ→次の空き枠へスライド: {f.name} ({int(late_min)}分遅れ) -> {when}")
                continue
        target = f
        break

    if target is None:
        print(f"[auto_post] {account}: 鮮度OKな投稿なし（全て退避） ({now.strftime('%H:%M')})")
        sys.exit(0)

    print(f"[auto_post] 対象: {target.name}")
    d = parse_draft(target)

    if dry_run:
        print("=== DRY RUN ===")
        print(f"アカウント: {account}")
        print(f"本文:\n{d['main_text']}")
        if d["comment_text"]:
            print(f"\nコメント欄:\n{d['comment_text']}")
        sys.exit(0)

    try:
        client = ThreadsClient.from_env(account=account)
        image_url = d["frontmatter"].get("image_url", "").strip()
        if image_url:
            media_id = client.create_image_post(d["main_text"], image_url)
            print(f"[auto_post] 画像投稿成功: media_id={media_id} (image={image_url[:60]})")
        else:
            media_id = client.create_text_post(d["main_text"])
            print(f"[auto_post] テキスト投稿成功: media_id={media_id}")

        # メトリクスアラート予約 (15/30/60 分後にチェック)
        # Threads アルゴリズム 2026: 投稿後 30〜60 分のリプ速度が配信幅を決定
        try:
            from post_alert import schedule_alert
            first_line = (d.get("main_text") or "").splitlines()[0] if d.get("main_text") else ""
            schedule_alert(account, media_id, now, first_line)
            print(f"[auto_post] メトリクスアラート予約: 15/30/60 分後にチェック")
        except Exception as e:
            print(f"[auto_post] アラート予約失敗 (続行): {e}", file=sys.stderr)

        # コメント欄が指定されていれば返信として投稿
        if d["comment_text"]:
            try:
                client.create_text_post(d["comment_text"], reply_to_id=media_id)
                print(f"[auto_post] コメント返信成功")
            except Exception as e:
                print(f"[auto_post] コメント返信失敗 (本文は投稿済み): {e}")

        new_path = move_to_posted(target, account, media_id, now)
        print(f"[auto_post] 移動先: {new_path}")

        notify(
            f"[Threads投稿] {account}\n"
            f"本文(40字): {d['main_text'][:40]}...\n"
            f"残り{len(due)-1}本キュー中"
        )
        sys.exit(0)

    except Exception as e:
        msg = f"[auto_post] 失敗 ({account}): {e}"
        print(msg, file=sys.stderr)
        notify(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
