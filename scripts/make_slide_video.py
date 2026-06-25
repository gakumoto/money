"""投稿文 → 縦型スライドMP4 を生成（顔出しなし・テキスト＋生成BGM）.

Claude/ローカル内で完結。imageio-ffmpeg のバンドル ffmpeg を使うのでシステム導入不要。
Pillow でスライド画像を描画 → 生フレームを ffmpeg に流して H.264 mp4 にエンコード。
BGM は numpy で穏やかなアンビエントを合成（生成物＝著作権セーフ）。

使い方:
    python scripts/make_slide_video.py --spec scripts/_video_spec.json --out out.mp4
    python scripts/make_slide_video.py --demo 1 --out .company/video/assets/v1.mp4

spec(JSON) 形式:
    {
      "title": "v1",
      "bg": ["#11141c", "#1d2433"],          # 背景グラデ(上→下)
      "accent": "#8fb4ff",                    # フックの色
      "slides": [
        {"text": "Threads頑張ってる人、", "dur": 2.6, "hook": true},
        {"text": "ほんと好きです", "dur": 2.4},
        ...
      ],
      "bgm": "warm"                            # warm / calm / soft
    }
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

W, H = 1080, 1920
FPS = 30
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_MED = r"C:\Windows\Fonts\YuGothM.ttc"

# 絵文字・記号(非BMP等)を画面テキストから除去（フォント豆腐化対策）
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⌀-⏿️‍]"
)


def strip_emoji(s: str) -> str:
    return _EMOJI.sub("", s).rstrip()


def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


def make_bg(c1: str, c2: str) -> np.ndarray:
    """縦グラデ背景 + ごく薄いビネット."""
    top = np.array(hex2rgb(c1), dtype=np.float32)
    bot = np.array(hex2rgb(c2), dtype=np.float32)
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    grad = (top[None, :] * (1 - t) + bot[None, :] * t)  # (H,3)
    bg = np.repeat(grad[:, None, :], W, axis=1)  # (H,W,3)
    # 中央やや明るいビネット
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = np.clip(1.0 - 0.18 * d, 0.82, 1.0)[:, :, None]
    return np.clip(bg * vig, 0, 255).astype(np.uint8)


_NOBREAK = "。、！？!?,.…」』）)：；・"  # この文字の前では改行しない（句読点オーファン防止）


def wrap_lines(draw, text, font, max_w):
    """明示改行を尊重しつつ、長い行は幅で折り返す。句読点は前の行に残す."""
    out = []
    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
            out.append("")
            continue
        cur = ""
        for ch in raw:
            test = cur + ch
            over = draw.textlength(test, font=font) > max_w and cur
            if over and ch not in _NOBREAK:
                out.append(cur)
                cur = ch
            else:
                cur = test
        out.append(cur)
    # 1文字 or 句読点だけの行は前行に結合（オーファン除去）
    merged = []
    for ln in out:
        if merged and ln and (len(ln) <= 1 or all(c in _NOBREAK for c in ln)):
            merged[-1] += ln
        else:
            merged.append(ln)
    return merged


def render_slide(text: str, hook: bool, accent, sub=None) -> tuple[np.ndarray, np.ndarray]:
    """スライドのテキスト層(RGBA)を返す → (rgb float(H,W,3), alpha float(H,W) 0..1)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 86 if hook else 72
    font = ImageFont.truetype(FONT_BOLD if hook else FONT_MED, size, index=0)
    color = accent if hook else (242, 244, 250)
    lines = wrap_lines(d, strip_emoji(text), font, int(W * 0.84))
    line_h = int(size * 1.42)
    total_h = line_h * len(lines)
    y = (H - total_h) // 2
    for ln in lines:
        w = d.textlength(ln, font=font)
        x = (W - w) / 2
        # 影で可読性UP
        d.text((x + 3, y + 3), ln, font=font, fill=(0, 0, 0, 120))
        d.text((x, y), ln, font=font, fill=(*color, 255))
        y += line_h
    arr = np.asarray(img).astype(np.float32)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3] / 255.0
    return rgb, alpha


def fade_factor(i: int, n: int, fin: int, fout: int) -> float:
    if i < fin:
        return (i + 1) / fin
    if i >= n - fout:
        return max(0.0, (n - i) / fout)
    return 1.0


def synth_bgm(seconds: float, style: str) -> np.ndarray:
    """穏やかなアンビエント(生成＝著作権セーフ)。stereo float -1..1."""
    sr = 44100
    n = int(seconds * sr)
    t = np.arange(n) / sr
    chords = {
        "warm": [146.83, 220.0, 293.66],   # D3 A3 D4
        "calm": [130.81, 196.0, 261.63],   # C3 G3 C4
        "soft": [164.81, 246.94, 329.63],  # E3 B3 E4
    }
    freqs = chords.get(style, chords["calm"])
    sig = np.zeros(n, dtype=np.float32)
    for k, f in enumerate(freqs):
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (0.08 + 0.02 * k) * t)  # ゆっくり揺らぎ
        sig += (0.6 / len(freqs)) * np.sin(2 * np.pi * f * t) * lfo
        sig += (0.15 / len(freqs)) * np.sin(2 * np.pi * f * 2 * t) * lfo
    # 全体フェードイン/アウト
    fade = min(int(sr * 1.0), n // 2)
    env = np.ones(n, dtype=np.float32)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    sig = sig * env * 0.16
    stereo = np.stack([sig, sig], axis=1)
    return np.clip(stereo, -1, 1)


def write_wav(path: Path, audio: np.ndarray, sr=44100):
    a16 = (audio * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(a16.tobytes())


def build(spec: dict, out_path: Path):
    bg = make_bg(*(spec.get("bg") or ["#11141c", "#1d2433"]))
    bgf = bg.astype(np.float32)
    accent = hex2rgb(spec.get("accent", "#8fb4ff"))
    slides = spec["slides"]
    total_sec = sum(s.get("dur", 2.5) for s in slides)

    # BGM を一時wavに
    tmp_wav = out_path.with_suffix(".bgm.wav")
    write_wav(tmp_wav, synth_bgm(total_sec, spec.get("bgm", "calm")))

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(tmp_wav),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    fin = int(FPS * 0.45)
    fout = int(FPS * 0.45)
    for s in slides:
        rgb, alpha = render_slide(s["text"], s.get("hook", False), accent)
        nfr = max(1, int(s.get("dur", 2.5) * FPS))
        for i in range(nfr):
            g = fade_factor(i, nfr, fin, fout)
            a = (alpha * g)[:, :, None]
            frame = bgf * (1 - a) + rgb * a
            proc.stdin.write(frame.astype(np.uint8).tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    rc = proc.wait()
    try:
        tmp_wav.unlink()
    except OSError:
        pass
    if rc != 0:
        print(err[-1500:], file=sys.stderr)
        raise SystemExit(f"ffmpeg failed rc={rc}")
    print(f"[make_slide_video] OK -> {out_path}  ({total_sec:.1f}s, {len(slides)}slides)")


DEMOS = {
    "1": {
        "title": "v1_nakama", "bg": ["#10131b", "#1b2540"], "accent": "#9ec1ff", "bgm": "warm",
        "slides": [
            {"text": "Threads頑張ってる人、", "dur": 2.6, "hook": True},
            {"text": "ほんと好きです。", "dur": 2.2},
            {"text": "バズってなくても\n毎日こっそり続けてる人。", "dur": 3.0},
            {"text": "今日も絡みに\nいかせてください。", "dur": 3.0},
            {"text": "同じ駆け出しの記録、\nプロフに置いてます。", "dur": 2.8},
        ],
    },
    "2": {
        "title": "v2_1month", "bg": ["#0f1117", "#222a3a"], "accent": "#a8d8c0", "bgm": "calm",
        "slides": [
            {"text": "Threads始めて\n最初の1ヶ月、", "dur": 2.8, "hook": True},
            {"text": "ほんとに\n誰にも読まれなかった。", "dur": 3.0},
            {"text": "いいね0、コメント0。", "dur": 2.6},
            {"text": "それでも毎日続けた。", "dur": 2.6},
            {"text": "あのとき辞めなくて\nよかった。", "dur": 3.0},
            {"text": "今やっと、\nそう思えてます。", "dur": 2.8},
        ],
    },
    "3": {
        "title": "v3_zero", "bg": ["#12110f", "#2a2418"], "accent": "#f0c98b", "bgm": "soft",
        "slides": [
            {"text": "副業の収入、", "dur": 2.2, "hook": True},
            {"text": "いまだに0円です。", "dur": 2.6},
            {"text": "それでも辞めない理由は、", "dur": 2.8},
            {"text": "会社の外で「自分」を\n試せてる感じ。", "dur": 3.0},
            {"text": "これがちょっと\nクセになってきた。", "dur": 3.0},
            {"text": "0円の今を、\n記録してます。", "dur": 2.6},
        ],
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="JSON spec ファイル")
    ap.add_argument("--demo", help="内蔵デモ 1/2/3")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.spec:
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    elif a.demo:
        spec = DEMOS[a.demo]
    else:
        raise SystemExit("--spec か --demo を指定")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    build(spec, out)


if __name__ == "__main__":
    main()
