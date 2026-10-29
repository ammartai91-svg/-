#!/usr/bin/env python3
"""مكس «نبض ينتظره قلبك»: فويس + نبض قلب يتسارع + سكتة + Hit عند «اليوم».

الاستعمال:
    python3 mix.py voice.mp3                 # يكتشف «اليوم» تلقائياً
    python3 mix.py voice.mp3 --hit 8.4       # توقيت يدوي للضربة (بالثواني)
    python3 mix.py voice.mp3 --style cinematic
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------- معالجة الصوت ----------

VOICE_CHAINS = {
    # أقوى: تنظيف + ضغط + وضوح
    "strong": (
        "highpass=f=80,afftdn=nf=-25,"
        "equalizer=f=200:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.2:g=3,"
        "acompressor=threshold=-20dB:ratio=4:attack=5:release=80:makeup=4,"
        "alimiter=limit=0.95"
    ),
    # سينمائي: أعمق شوية + صدى قاعة خفيف
    "cinematic": (
        "highpass=f=70,afftdn=nf=-25,"
        "asetrate=48000*0.96,aresample=48000,atempo=1.0417,"
        "equalizer=f=120:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1.2:g=2,"
        "acompressor=threshold=-22dB:ratio=4:attack=5:release=100:makeup=5,"
        "aecho=0.8:0.5:60|120:0.18|0.10,alimiter=limit=0.95"
    ),
}


def process_voice(src, dst, style):
    run(["ffmpeg", "-y", "-i", src, "-af", VOICE_CHAINS[style],
         "-ac", "2", "-ar", str(SR), dst])


def speech_segments(path):
    """يرجع [(بداية، نهاية)] لمقاطع الكلام حسب السكتات."""
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-"],
        stderr=subprocess.PIPE, text=True).stderr
    starts, ends = [], []
    for line in out.splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].split()[0]))
        elif "silence_end:" in line:
            ends.append(float(line.split("silence_end:")[1].split("|")[0]))
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        stdout=subprocess.PIPE, text=True).stdout)
    segs, cur = [], 0.0
    if starts and starts[0] < 0.05 and ends:
        cur = ends.pop(0)
        starts.pop(0)
    for s, e in zip(starts, ends + [dur]):
        if s - cur > 0.1:
            segs.append((cur, s))
        cur = e
    if dur - cur > 0.1:
        segs.append((cur, dur))
    return segs, dur


# ---------- المؤثرات ----------

def lp(x, f):
    return sosfilt(butter(4, f, "low", fs=SR, output="sos"), x)


def beat(strength=1.0):
    """ضربة «لَب-دَب» وحدة."""
    def thump(dur, f0, f1, amp):
        t = np.arange(int(dur * SR)) / SR
        freq = f0 + (f1 - f0) * (t / dur)
        body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 18)
        click = lp(np.random.randn(len(t)), 900) * np.exp(-t * 120) * 0.25
        return (body + click) * amp
    lub = thump(0.22, 75, 42, 1.0 * strength)
    dub = thump(0.18, 85, 50, 0.7 * strength)
    out = np.zeros(int(0.5 * SR))
    out[:len(lub)] += lub
    off = int(0.17 * SR)
    out[off:off + len(dub)] += dub
    return out


def hit():
    """ضربة سينمائية: Boom عميق + انفجار ضوضاء + ذيل."""
    n = int(3.5 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-t * 1.5) + 28) / SR) * np.exp(-t * 1.6)
    noise = lp(np.random.randn(n), 2500) * np.exp(-t * 9) * 0.5
    impact = np.random.randn(n) * np.exp(-t * 60) * 0.3
    return boom + noise + impact


def riser(dur):
    """سحبة صاعدة قبل الضربة."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = (t / dur) ** 2.5
    noise = np.random.randn(n)
    out = np.zeros(n)
    for i in range(0, n, 2400):  # فلتر يفتح تدريجياً
        f = 300 + 5000 * (i / n) ** 2
        seg = noise[i:i + 2400]
        out[i:i + len(seg)] = lp(seg, f)
    return out * env * 0.35


def build_bed(dur, hit_at, gap=0.55):
    """نبض يبدأ 60 BPM ويتسارع لـ115، يوقف قبل الضربة بـ gap ثانية."""
    bed = np.zeros(int((dur + 4) * SR))
    t, stop = 0.15, hit_at - gap
    while t < stop:
        p = t / max(stop, 0.01)
        bpm = 60 + 55 * p ** 1.6
        b = beat(0.5 + 0.5 * p)
        i = int(t * SR)
        bed[i:i + len(b)] += b[:len(bed) - i]
        t += 60.0 / bpm
    r = riser(1.2)
    ri = int((hit_at - 1.2) * SR)
    if ri > 0:
        bed[ri:ri + len(r)] += r
    h = hit()
    hi = int(hit_at * SR)
    bed[hi:hi + len(h)] += h[:len(bed) - hi]
    return bed[:int((dur + 2.5) * SR)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice")
    ap.add_argument("--hit", type=float, help="توقيت الضربة بالثواني (افتراضي: بداية «اليوم»)")
    ap.add_argument("--style", choices=VOICE_CHAINS, default="strong")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    base = os.path.splitext(os.path.basename(a.voice))[0]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{base}-{a.style}-mix.mp3")
    with tempfile.TemporaryDirectory() as tmp:
        voice = os.path.join(tmp, "voice.wav")
        process_voice(a.voice, voice, a.style)
        segs, dur = speech_segments(voice)
        # «اليوم» = المقطع قبل الأخير
        hit_at = a.hit if a.hit is not None else (segs[-2][0] if len(segs) >= 2 else dur * 0.7)
        print(f"مقاطع الكلام: {[(round(s, 2), round(e, 2)) for s, e in segs]}")
        print(f"الضربة عند: {hit_at:.2f}s")

        bed = build_bed(dur, hit_at)
        bed = bed / np.max(np.abs(bed)) * 0.5
        bed_path = os.path.join(tmp, "bed.wav")
        wavfile.write(bed_path, SR, np.stack([bed, bed], 1).astype(np.float32))
        wavfile.write(os.path.join(os.path.dirname(out), "sfx-bed.wav"), SR,
                      np.stack([bed, bed], 1).astype(np.float32))

        run(["ffmpeg", "-y", "-i", voice, "-i", bed_path, "-filter_complex",
             "[1:a]volume=0.8[b];[b][0:a]sidechaincompress=threshold=0.05:ratio=3:attack=10:release=250[bd];"
             "[bd][0:a]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1:LRA=9",
             "-ar", str(SR), "-b:a", "320k", out])
    print(f"✅ {out}")


if __name__ == "__main__":
    sys.exit(main())
