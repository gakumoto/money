"""YouTube リサーチ自動化.

指定チャンネルの直近N本の動画から字幕を取得し、
.company/research/topics/youtube-YYYY-MM-DD.md に保存する.

要約と投稿ネタ抽出は Claude Code の skill (/youtube-research) 側で実施する.

使い方:
    python scripts/youtube_research.py <channel_url> [count]
    python scripts/youtube_research.py https://www.youtube.com/@example 10
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows の cp932 対策
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _ensure_yt_dlp() -> str:
    """yt-dlp の実行コマンドを返す. 無ければエラー."""
    path = shutil.which("yt-dlp")
    if not path:
        raise RuntimeError(
            "yt-dlp が見つからない. 以下でインストール:\n"
            "  pip install -r scripts/requirements.txt\n"
            "またはグローバルに:\n"
            "  pip install yt-dlp"
        )
    return path


def fetch_channel_videos(channel_url: str, count: int) -> list[dict]:
    """チャンネルから直近 count 本の動画メタデータを取得."""
    yt_dlp = _ensure_yt_dlp()
    cmd = [
        yt_dlp,
        "--flat-playlist",
        "--print",
        "%(id)s\t%(title)s\t%(upload_date)s\t%(url)s",
        "--playlist-end",
        str(count),
        channel_url,
    ]
    out = subprocess.check_output(cmd, encoding="utf-8", errors="replace")
    videos = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        videos.append(
            {
                "id": parts[0],
                "title": parts[1],
                "upload_date": parts[2],
                "url": parts[3],
            }
        )
    return videos


def fetch_subtitles(video_url: str, *, lang_priority: tuple[str, ...] = ("ja", "en")) -> str:
    """動画の字幕を取得. 優先順位は ja → en → auto."""
    yt_dlp = _ensure_yt_dlp()
    with tempfile.TemporaryDirectory() as tmp:
        out_template = os.path.join(tmp, "%(id)s.%(ext)s")
        for lang in lang_priority:
            cmd = [
                yt_dlp,
                "--write-sub",
                "--write-auto-sub",
                "--sub-lang",
                lang,
                "--sub-format",
                "vtt",
                "--skip-download",
                "-o",
                out_template,
                video_url,
            ]
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                continue
            # 取得できたファイルを探す
            for f in os.listdir(tmp):
                if f.endswith(".vtt"):
                    with open(os.path.join(tmp, f), encoding="utf-8") as fp:
                        return _vtt_to_text(fp.read())
    return ""


def _vtt_to_text(vtt: str) -> str:
    """VTT 字幕からタイムスタンプ除去して本文だけ抽出."""
    lines = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s:
            continue
        if s == "WEBVTT" or s.startswith("NOTE"):
            continue
        if "-->" in s:
            continue
        if s.isdigit():
            continue
        # cue settings line (Kind: captions など)
        if s.startswith("Kind:") or s.startswith("Language:"):
            continue
        lines.append(s)
    # 連続する重複行を削除
    out = []
    prev = None
    for line in lines:
        if line != prev:
            out.append(line)
        prev = line
    return "\n".join(out)


def save_research(channel_url: str, videos_with_subs: list[dict]) -> Path:
    """研究結果を .company/research/topics/youtube-YYYY-MM-DD.md に保存."""
    today = dt.date.today().isoformat()
    out_dir = _project_root() / ".company" / "research" / "topics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"youtube-{today}.md"

    lines = []
    if not out_file.exists():
        lines.append(
            f"""---
created: "{today}"
topic: "YouTubeリサーチ"
status: in-progress
tags: ["youtube", "research", "raw-data"]
---

# YouTubeリサーチ - {today}

このファイルは scripts/youtube_research.py が生成した **生字幕** を含む.
要約と投稿ネタ抽出は /youtube-research スキルで実施する.

"""
        )
    lines.append(f"\n---\n\n## 取得実行: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"- チャンネル: {channel_url}\n")
    lines.append(f"- 動画数: {len(videos_with_subs)}\n\n")

    for i, v in enumerate(videos_with_subs, 1):
        sub_preview = (v.get("subtitle") or "").strip()
        lines.append(f"### {i}. {v['title']}\n")
        lines.append(f"- ID: {v['id']}\n")
        lines.append(f"- URL: {v['url']}\n")
        lines.append(f"- 公開: {v['upload_date']}\n")
        lines.append(f"- 字幕長: {len(sub_preview)}文字\n\n")
        lines.append("```\n")
        # 字幕は長いので最初の3000文字だけ
        if len(sub_preview) > 3000:
            lines.append(sub_preview[:3000])
            lines.append(f"\n... (省略: 全{len(sub_preview)}文字)\n")
        else:
            lines.append(sub_preview if sub_preview else "(字幕取得失敗)")
            lines.append("\n")
        lines.append("```\n\n")

    # 追記モード
    mode = "a" if out_file.exists() else "w"
    with open(out_file, mode, encoding="utf-8") as f:
        f.write("".join(lines))

    return out_file


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    channel_url = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"[1/3] チャンネル動画一覧取得: {channel_url} (count={count})")
    videos = fetch_channel_videos(channel_url, count)
    print(f"  → {len(videos)} 本見つかった")

    print(f"[2/3] 各動画の字幕取得 (これは時間がかかる)")
    for i, v in enumerate(videos, 1):
        print(f"  ({i}/{len(videos)}) {v['title'][:50]}...")
        v["subtitle"] = fetch_subtitles(v["url"])

    print(f"[3/3] 保存")
    out = save_research(channel_url, videos)
    print(f"  → {out}")

    # Discord 通知 (任意)
    try:
        from _discord import notify

        notify(
            f"YouTubeリサーチ完了\n"
            f"- チャンネル: {channel_url}\n"
            f"- 取得: {len(videos)}本\n"
            f"- 保存先: {out.relative_to(_project_root())}"
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
