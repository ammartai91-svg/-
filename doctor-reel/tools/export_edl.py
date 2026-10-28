"""Writes the pause-trimmed cut as a CMX 3600 EDL so the edit can be rebuilt in DaVinci Resolve
(File -> Import -> Timeline -> select the .edl, then point it at the original clip).

Run: python3 tools/export_edl.py [--reel DOCTOR] [--clip doctor-log.mov] -> project/doctor-cut.edl
Reads public/video/edl.json written by tools/tighten.py.
"""
import argparse
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FPS = 30


def tc(seconds):
    f = round(seconds * FPS)
    return f"{f // (3600 * FPS):02d}:{f // (60 * FPS) % 60:02d}:{f // FPS % 60:02d}:{f % FPS:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reel", default="DOCTOR")
    ap.add_argument("--clip", default=None, help="clip file name shown to Resolve (defaults to edl.json source)")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "public", "video", "edl.json")) as f:
        edl = json.load(f)
    clip = a.clip or edl["source"]
    lines = ["TITLE: DOCTOR TIPS REEL - PAUSES TRIMMED", "FCM: NON-DROP FRAME", ""]
    rec = 3600.0  # timeline starts at 01:00:00:00
    for i, (src_in, src_out) in enumerate(edl["segments"], 1):
        dur = src_out - src_in
        lines.append(f"{i:03d}  {a.reel:<8} AA/V  C        {tc(src_in)} {tc(src_out)} {tc(rec)} {tc(rec + dur)}")
        lines.append(f"* FROM CLIP NAME: {clip}")
        lines.append("")
        rec += dur
    os.makedirs(os.path.join(ROOT, "project"), exist_ok=True)
    out = os.path.join(ROOT, "project", "doctor-cut.edl")
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print("wrote", out, f"({len(edl['segments'])} events)")


if __name__ == "__main__":
    main()
