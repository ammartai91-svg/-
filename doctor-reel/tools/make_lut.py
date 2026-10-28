"""Builds the reel's cinematic grade as a 33-point 3D LUT (.cube).

The same file loads in DaVinci Resolve (Color page -> LUTs, or a node's LUT), Premiere
(Lumetri -> Creative -> Look) and After Effects (Apply Color LUT), so the grade can be
finished there by hand. tools/tighten.py bakes it into the reel footage.

Run: python3 tools/make_lut.py        -> luts/nabd-cinematic.cube        (normal Rec.709 footage)
     python3 tools/make_lut.py --log  -> luts/nabd-log-cinematic.cube    (flat / Log footage:
                                          expands levels to Rec.709 first, then the same look)
"""
import argparse
import colorsys
import os

import numpy as np

N = 33
LUTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "luts")

# --- Log -> Rec.709 (measured on the doctor's flat clip) ---------------------
LOG_BLACK = 0.15  # deepest blacks in the flat clip (suit, monitor ~0.17)
LOG_WHITE = 0.47  # brightest highlights (wall peaks ~0.46)
LOG_GAMMA = 0.95  # <1 opens mids slightly after the stretch
LOG_SAT = 1.3  # extra colour after the stretch (the stretch itself restores most of it)

# --- look controls -----------------------------------------------------------
CONTRAST = 1.18  # S-curve strength around the pivot
PIVOT = 0.40
EXPOSURE = -0.05  # pull the bright wall down before the curve
SHOULDER = 0.78  # highlights above this roll off softly instead of clipping
BLACK_LIFT = 0.025  # matte floor so blacks stay filmic, not crushed flat
SHADOW_TINT = np.array([-0.020, 0.000, 0.045])  # navy shadows (campaign colour)
HIGHLIGHT_TINT = np.array([0.022, 0.008, -0.018])  # warm highlights for skin
SKIN_HUE = (0.02, 0.11)  # hue band (0..1) treated as skin — protected and warmed
SKIN_SAT = 1.04
BG_DESAT_HUES = [(0.68, 0.98, 0.2), (0.18, 0.47, 0.3), (0.45, 0.62, 0.55)]  # lilac, green and cyan banding on the wall
GLOBAL_SAT = 1.0


def s_curve(x):
    # logistic S-curve normalised to keep 0->0 and 1->1
    k = CONTRAST * 6
    f = lambda v: 1 / (1 + np.exp(-k * (v - PIVOT)))
    x = np.clip(x + EXPOSURE, 0, 1)
    y = (f(x) - f(0)) / (f(1) - f(0))
    y = np.where(y > SHOULDER, SHOULDER + (y - SHOULDER) * 0.55, y)
    return BLACK_LIFT + y * (1 - BLACK_LIFT)


def log_to_rec709(rgb):
    v = (np.asarray(rgb) - LOG_BLACK) / (LOG_WHITE - LOG_BLACK)
    v = np.clip(v, 0, 1) ** LOG_GAMMA
    h, l, s = colorsys.rgb_to_hls(*v)
    return np.array(colorsys.hls_to_rgb(h, l, min(1.0, s * LOG_SAT)))


def grade(rgb, log=False):
    if log:
        rgb = log_to_rec709(rgb)
    r, g, b = rgb
    # tone
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    out = np.array([s_curve(r), s_curve(g), s_curve(b)])
    # split toning by luminance
    w_sh = np.clip(1 - luma / 0.5, 0, 1) ** 1.5
    w_hi = np.clip((luma - 0.5) / 0.5, 0, 1) ** 1.2
    out = out + SHADOW_TINT * w_sh + HIGHLIGHT_TINT * w_hi
    out = np.clip(out, 0, 1)
    # hue-selective saturation
    h, l, s = colorsys.rgb_to_hls(*out)
    sat = GLOBAL_SAT
    if SKIN_HUE[0] <= h <= SKIN_HUE[1]:
        sat *= SKIN_SAT
    for lo, hi, amt in BG_DESAT_HUES:
        if lo <= h <= hi:
            centre = (lo + hi) / 2
            width = (hi - lo) / 2
            sat *= 1 - (1 - amt) * (1 - abs(h - centre) / width)
    s = min(1.0, s * sat)
    return np.clip(colorsys.hls_to_rgb(h, l, s), 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", action="store_true", help="input is flat/Log footage")
    args = ap.parse_args()
    out = os.path.join(LUTS, "nabd-log-cinematic.cube" if args.log else "nabd-cinematic.cube")
    os.makedirs(LUTS, exist_ok=True)
    lines = [f'TITLE "Nabd cinematic{" (Log in)" if args.log else ""}"', f"LUT_3D_SIZE {N}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    grid = np.linspace(0, 1, N)
    # .cube order: red changes fastest, then green, then blue
    for b in grid:
        for g in grid:
            for r in grid:
                o = grade((r, g, b), args.log)
                lines.append(f"{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
