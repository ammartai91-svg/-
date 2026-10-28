"""Synthesises the reel's music bed and sound effects (royalty-free, generated locally).

Run: python3 tools/make_sounds.py   -> writes public/music/*.wav and public/sfx/*.wav
Swap any file for a licensed track with the same name to change the sound.
"""
import os
import wave

import numpy as np

SR = 44100
ROOT = os.path.join(os.path.dirname(__file__), "..", "public")
rng = np.random.default_rng(7)


def write(path, x, peak=0.89):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    m = np.abs(x).max() or 1.0
    x = x / m * peak
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def t(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a, d, curve=4.0):
    """Attack (s) then exponential decay over the rest."""
    a_n = max(1, int(a * SR))
    e = np.ones(n)
    e[:a_n] = np.linspace(0, 1, a_n)
    rest = n - a_n
    e[a_n:] = np.exp(-np.linspace(0, curve, rest)) if rest > 0 else 1
    return e[:n] * (np.linspace(1, 0, n) ** 0.2 if d else 1)


def onepole_lp(x, cutoff):
    """Time-varying one-pole low-pass; cutoff may be an array."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def bandsweep(x, f0, f1):
    f = np.geomspace(f0, f1, len(x))
    return onepole_lp(x, f * 1.6) - onepole_lp(x, f * 0.6)


def reverb(x, mix=0.25, decay=0.45):
    out = x.copy()
    for d, g in [(0.029, 0.7), (0.037, 0.6), (0.053, 0.5), (0.071, 0.45), (0.11, 0.35), (0.17, 0.25)]:
        n = int(d * SR)
        y = np.zeros_like(x)
        y[n:] = x[:-n] * g * decay * 2
        out += y * mix
    return out


def pan(x, p):
    return np.stack([x * (1 - p) ** 0.5, x * (1 + p) ** 0.5], 1) / 1.2


# ---------------------------------------------------------------- SFX
def whoosh(dur=0.55, f0=300, f1=4500, rev=False):
    n = int(dur * SR)
    x = bandsweep(rng.standard_normal(n), f0, f1)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    x *= shape
    if rev:
        x = x[::-1]
    l = x
    r = np.roll(x, int(0.006 * SR))
    return np.stack([l, r], 1)


def pop():
    tt = t(0.14)
    f = 900 * np.exp(-tt * 28) + 380
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 38)
    return x


def click():
    tt = t(0.05)
    x = rng.standard_normal(len(tt)) * np.exp(-tt * 260)
    x = x - onepole_lp(x, 2500)
    x += 0.4 * np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300)
    return x


def ding(base=1318.5):
    tt = t(1.6)
    x = sum(a * np.sin(2 * np.pi * base * m * tt) * np.exp(-tt * d)
            for m, a, d in [(1, 1, 3.2), (2.01, 0.45, 5), (2.76, 0.25, 7), (4.07, 0.12, 10)])
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return reverb(x, 0.35)


def riser(dur=1.2):
    tt = t(dur)
    n = len(tt)
    x = bandsweep(rng.standard_normal(n), 200, 7000) * 0.6
    f = np.geomspace(180, 1400, n)
    x += 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    x *= np.linspace(0, 1, n) ** 2.2
    return x


def impact():
    tt = t(1.4)
    f = 110 * np.exp(-tt * 6) + 38
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    nz = rng.standard_normal(len(tt)) * np.exp(-tt * 18)
    nz = onepole_lp(nz, 1800)
    return reverb(sub + 0.5 * nz, 0.3)


def shimmer():
    tt = t(1.3)
    notes = [1760, 2217.5, 2637, 3520]
    x = np.zeros(len(tt))
    for i, fr in enumerate(notes):
        st = int(i * 0.06 * SR)
        seg = tt[: len(tt) - st]
        x[st:] += np.sin(2 * np.pi * fr * seg) * np.exp(-seg * 4.5) * 0.5
    return reverb(x, 0.4)


def glitch():
    tt = t(0.32)
    x = np.sign(np.sin(2 * np.pi * 140 * tt)) * 0.3
    x += rng.standard_normal(len(tt)) * 0.5
    gate = (np.floor(tt * 45) % 2).astype(float)
    x = onepole_lp(x * gate, 5000) * np.exp(-tt * 6)
    return x


def typing(dur=1.0, rate=14):
    n = int(dur * SR)
    out = np.zeros(n)
    k = click()
    pos = 0.0
    while pos < dur - 0.06:
        i = int(pos * SR)
        g = 0.6 + 0.4 * rng.random()
        out[i:i + len(k)] += k[: n - i] * g
        pos += (1 / rate) * (0.7 + 0.6 * rng.random())
    return out


def heartbeat():
    """lub-dub: two soft low thumps."""
    out = np.zeros(int(0.9 * SR))
    for off, f0, g in [(0.0, 62, 1.0), (0.22, 72, 0.7)]:
        tt = t(0.32)
        f = f0 * (1 + 0.6 * np.exp(-tt * 40))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * g
        x += onepole_lp(rng.standard_normal(len(tt)), 300) * np.exp(-tt * 30) * 0.4 * g
        i = int(off * SR)
        out[i:i + len(x)] += x[: len(out) - i]
    return out


def tick():
    tt = t(0.08)
    x = np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 90) * 0.6
    x += np.sin(2 * np.pi * 1200 * tt) * np.exp(-tt * 60) * 0.4
    return x


sfx = {
    "heartbeat": heartbeat(),
    "tick": tick(),
    "whoosh": whoosh(),
    "whoosh-soft": whoosh(0.7, 200, 2500) * 0.6,
    "whoosh-reverse": whoosh(0.6, 400, 5000, rev=True),
    "pop": pop(),
    "click": click(),
    "ding": ding(),
    "riser": riser(),
    "impact": impact(),
    "shimmer": shimmer(),
    "glitch": glitch(),
    "typing": typing(),
}
for name, x in sfx.items():
    write(os.path.join(ROOT, "sfx", f"{name}.wav"), x)


# ---------------------------------------------------------------- MUSIC
BPM = 112
BEAT = 60 / BPM
DUR = 64.0  # long enough for any edit; the composition trims/fades it
N = int(DUR * SR)
L = np.zeros(N)
R = np.zeros(N)


def add(x, start, p=0.0, g=1.0):
    i = int(start * SR)
    if i >= N:
        return
    x = x[: N - i] * g
    l, r = pan(x, p).T
    L[i:i + len(x)] += l
    R[i:i + len(x)] += r


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def pluck(freq, dur=0.5):
    tt = t(dur)
    x = sum(np.sin(2 * np.pi * freq * h * tt) / h ** 1.4 for h in range(1, 7))
    x *= np.exp(-tt * 7)
    x[: 80] *= np.linspace(0, 1, 80)
    return onepole_lp(x, 3800)


def pad(freqs, dur):
    tt = t(dur)
    x = np.zeros(len(tt))
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            x += np.sign(np.sin(2 * np.pi * ff * tt + rng.random() * 6)) * 0.08
    x = onepole_lp(x, 1100)
    a = int(0.4 * SR)
    e = np.ones(len(tt))
    e[:a] = np.linspace(0, 1, a)
    e[-a:] = np.linspace(1, 0, a)
    return x * e


def kick():
    tt = t(0.45)
    f = 140 * np.exp(-tt * 30) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)


def hat(open_=False):
    tt = t(0.25 if open_ else 0.06)
    x = rng.standard_normal(len(tt))
    x = x - onepole_lp(x, 7000)
    return x * np.exp(-tt * (18 if open_ else 90)) * 0.5


def clap():
    tt = t(0.25)
    x = rng.standard_normal(len(tt))
    x = bandsweep(x, 1200, 1500) * 3
    e = np.exp(-tt * 22)
    for o in (0.0, 0.011, 0.022):
        e += np.roll(np.exp(-tt * 140), int(o * SR)) * 0.6
    return reverb(x * e, 0.3)


# Cmaj7 - G/B - Am7 - Fmaj9  (bright, trustworthy, a little cinematic)
chords = [
    [60, 64, 67, 71],
    [59, 62, 67, 74],
    [57, 60, 64, 67],
    [53, 57, 60, 64, 67],
]
bass = [36, 35, 33, 29]
bar = BEAT * 4
bars = int(DUR / bar)
arp_pattern = [0, 2, 1, 3, 2, 1, 3, 2]
k, h, ho, c = kick(), hat(), hat(True), clap()
for b in range(bars):
    ch = chords[b % 4]
    t0 = b * bar
    section = 0 if b < 2 else 1  # intro is pad+pluck only
    add(pad([midi(m) for m in ch], bar + 0.4), t0, 0, 0.55)
    for s, idx in enumerate(arp_pattern):
        note = ch[idx % len(ch)] + 12
        add(pluck(midi(note)), t0 + s * BEAT / 2, 0.35 if s % 2 else -0.35, 0.33)
    if section:
        tt = t(bar)
        bs = np.sin(2 * np.pi * midi(bass[b % 4]) * tt) * 0.5
        bs *= np.minimum(1, (tt % BEAT) * 30) * np.exp(-(tt % BEAT) * 2.2)
        add(bs, t0, 0, 0.8)
        for q in range(4):
            add(k, t0 + q * BEAT, 0, 0.9 if q in (0, 2) else 0.55)
            if q in (1, 3):
                add(c, t0 + q * BEAT, 0.05, 0.35)
            add(h, t0 + q * BEAT + BEAT / 2, 0.4, 0.45)
            add(h, t0 + q * BEAT + BEAT / 4 * 3, 0.4, 0.2)
        if b % 4 == 3:
            add(ho, t0 + 3.5 * BEAT, -0.3, 0.5)

mix = np.stack([L, R], 1)
mix = np.tanh(mix / (np.abs(mix).max() / 1.6)) # gentle saturation / glue
write(os.path.join(ROOT, "music", "bed.wav"), mix, 0.8)
print("bpm", BPM, "bars", bars, "sfx", list(sfx))
