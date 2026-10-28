"""Cuts the doctor out of her original video and writes a transparent WebM for the reel.

Usage:
  python3 tools/prepare_doctor.py <source.mov> [--start 0] [--end 30] [--fps 30]

Output: public/video/doctor-cutout.webm (VP9 + alpha) and public/video/doctor-voice.wav.
Then set content.doctor.src = 'video/doctor-cutout.webm' in src/content.ts.

Needs: ffmpeg, and `pip install rembg onnxruntime` (model downloads on first run).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image
from rembg import new_session, remove

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT_DIR = os.path.join(ROOT, "public", "video")


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--height", type=int, default=1920, help="output height in px")
    ap.add_argument("--model", default="u2net_human_seg")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    work = tempfile.mkdtemp(prefix="cutout-")
    frames, masked = os.path.join(work, "in"), os.path.join(work, "out")
    os.makedirs(frames)
    os.makedirs(masked)

    trim = ["-ss", str(args.start)] + (["-to", str(args.end)] if args.end else [])
    run(["ffmpeg", "-v", "error", "-y", *trim, "-i", args.source,
         "-vf", f"fps={args.fps},scale=-2:{args.height}", os.path.join(frames, "%05d.png")])
    run(["ffmpeg", "-v", "error", "-y", *trim, "-i", args.source, "-vn", "-ac", "2", "-ar", "48000",
         os.path.join(OUT_DIR, "doctor-voice.wav")])

    session = new_session(args.model)
    names = sorted(os.listdir(frames))
    for i, name in enumerate(names):
        img = Image.open(os.path.join(frames, name)).convert("RGB")
        cut = remove(img, session=session, post_process_mask=True)
        cut.save(os.path.join(masked, name))
        if i % 25 == 0:
            print(f"{i + 1}/{len(names)}", flush=True)

    out = os.path.join(OUT_DIR, "doctor-cutout.webm")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(args.fps), "-i", os.path.join(masked, "%05d.png"),
         "-i", os.path.join(OUT_DIR, "doctor-voice.wav"),
         "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-auto-alt-ref", "0",
         "-c:a", "libopus", "-b:a", "160k", "-shortest", out])
    shutil.rmtree(work)
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
