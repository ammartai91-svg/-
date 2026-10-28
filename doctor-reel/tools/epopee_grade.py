"""Epopée-style split grade: teal environment with a key-light glow, clean natural subject.

Like a Resolve node tree with a person matte (Magic Mask): the background gets
luts/epopee-background.cube + vignette + luts/epopee-glow.png (screen), the doctor gets
luts/epopee-subject.cube, and a per-frame person matte (rembg) blends them.

Usage:
  python3 tools/epopee_grade.py public/video/doctor-tight-raw.mp4 public/video/doctor-tight.mp4
Needs: ffmpeg, rembg + onnxruntime. Build the LUTs first with tools/slog3.py (--look subject /
--look background --size 65) and the glow with this script's --glow flag if it is missing.
"""
import argparse
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LUTS = os.path.join(ROOT, "luts")


def make_glow(path, w=1080, h=1920):
    y, x = np.mgrid[0:h, 0:w]
    # key-light spill upper right (as in the reference) plus a soft halo behind the head
    g = np.exp(-(((x - 820) / 520) ** 2 + ((y - 620) / 700) ** 2)) * 0.85
    g += np.exp(-(((x - 540) / 420) ** 2 + ((y - 760) / 420) ** 2)) * 0.45
    g = np.clip(g, 0, 1)
    Image.fromarray((np.stack([g * 0.92, g * 0.98, g], -1) * 255).astype(np.uint8)).save(path)


def mattes(src, out_mp4, work):
    from rembg import new_session, remove

    frames = os.path.join(work, "f")
    os.makedirs(frames)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale=540:960",
                    os.path.join(frames, "%05d.png")], check=True)
    masks = os.path.join(work, "m")
    os.makedirs(masks)
    session = new_session("u2net_human_seg")
    names = sorted(os.listdir(frames))
    for i, n in enumerate(names):
        m = remove(Image.open(os.path.join(frames, n)).convert("RGB"), session=session,
                   only_mask=True, post_process_mask=True)
        # pull the edge in slightly and feather, so no bright wall rim is graded as "subject"
        m = m.resize((1080, 1920), Image.BICUBIC).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(4))
        m.save(os.path.join(masks, n))
        if i % 100 == 0:
            print(f"matte {i + 1}/{len(names)}", flush=True)
    # tmix smooths frame-to-frame matte flicker
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(masks, "%05d.png"),
                    "-vf", "format=gray,tmix=frames=3", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p",
                    out_mp4], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--glow-opacity", type=float, default=0.5)
    a = ap.parse_args()

    glow = os.path.join(LUTS, "epopee-glow.png")
    if not os.path.exists(glow):
        make_glow(glow)
    work = tempfile.mkdtemp(prefix="epopee-")
    matte = os.path.join(work, "matte.mp4")
    mattes(a.src, matte, work)

    bg_lut = os.path.join(LUTS, "epopee-background.cube")
    fg_lut = os.path.join(LUTS, "epopee-subject.cube")
    graph = (
        f"[0:v]split[a][b];"
        f"[a]hqdn3d=1.5:7:3:7,format=gbrp16le,lut3d={bg_lut},format=rgb48le,vignette=PI/4.5,format=gbrp[bg0];"
        f"[2:v]format=gbrp[gl];"
        # screen blend is only reliable in 8-bit here; deband afterwards hides any stepping
        f"[bg0][gl]blend=all_mode=screen:all_opacity={a.glow_opacity},format=gbrp16le[bg];"
        f"[b]hqdn3d=1.5:7:3:7,format=gbrp16le,lut3d={fg_lut},format=gbrp16le[fg];"
        f"[1:v]format=gray,format=gbrp16le[m];"
        f"[bg][fg][m]maskedmerge,format=gbrp16le,deband,format=yuv420p[v]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-i", matte, "-loop", "1", "-i", glow,
                    "-filter_complex", graph, "-map", "[v]", "-map", "0:a", "-shortest",
                    "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", a.out], check=True)
    shutil.rmtree(work)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
