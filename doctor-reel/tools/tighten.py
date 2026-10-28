"""Removes long silences from a talking-head clip and writes a tightened copy plus its edit list.

Usage:
  python3 tools/tighten.py <source> [--keep-gap 0.22] [--min-gap 0.45] [--db -32]

Writes public/video/doctor-tight.mp4 (1080x1920, 30fps) and public/video/edl.json:
  {"segments": [[srcStart, srcEnd], ...], "cuts": [newTime, ...]}
`cuts` are the jump-cut points on the new timeline; the reel punches the camera there.
"""
import argparse
import json
import os
import re
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "public", "video")


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def silences(path, db, min_len):
    log = subprocess.run(["ffmpeg", "-i", path, "-af", f"silencedetect=n={db}dB:d={min_len}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--keep-gap", type=float, default=0.22, help="pause left in place of a long silence (s)")
    ap.add_argument("--min-gap", type=float, default=0.45, help="silences shorter than this stay untouched (s)")
    ap.add_argument("--db", type=float, default=-32)
    ap.add_argument("--lead", type=float, default=0.25, help="silence kept before the first word (s)")
    args = ap.parse_args()

    total = duration(args.source)
    half = args.keep_gap / 2
    segments, cursor = [], 0.0
    for s, e in silences(args.source, args.db, args.min_gap):
        e = total if e is None else e
        if s <= 0.01:  # leading silence
            cursor = max(0.0, e - args.lead)
            continue
        segments.append([cursor, min(total, s + half)])
        cursor = max(s + half, e - half)
    if cursor < total - 0.05:
        segments.append([cursor, total])
    segments = [[round(a, 3), round(b, 3)] for a, b in segments if b - a > 0.2]

    parts, labels, t, cuts = [], [], 0.0, []
    for i, (a, b) in enumerate(segments):
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,"
                     f"afade=t=out:st={max(0, b - a - 0.015)}:d=0.015[a{i}];")
        labels.append(f"[v{i}][a{i}]")
        if i:
            cuts.append(round(t, 3))
        t += b - a
    graph = "".join(parts) + "".join(labels) + f"concat=n={len(segments)}:v=1:a=1[v][a];" \
        "[v]fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6[vo]"

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "doctor-tight.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.source, "-filter_complex", graph,
                    "-map", "[vo]", "-map", "[a]", "-c:v", "libx264", "-crf", "21", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    with open(os.path.join(OUT, "edl.json"), "w") as f:
        json.dump({"source": os.path.basename(args.source), "segments": segments, "cuts": cuts,
                   "duration": round(t, 3)}, f, indent=1)
    print(f"{total:.2f}s -> {t:.2f}s, {len(segments)} segments")


if __name__ == "__main__":
    main()
