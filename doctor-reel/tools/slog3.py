"""Technical Sony S-Log3 / S-Gamut3.Cine -> Rec.709 transform as a 3D LUT, with exposure,
white balance and a gentle filmic tone map. Used to test whether the flat clip behaves like
genuine S-Log3, and as the technical first node of the grade (load it in Resolve before the look).

Run: python3 tools/slog3.py --stops 1.7 --wb 1.115,1,0.906          -> technical transform only
     python3 tools/slog3.py --stops 1.7 --wb 1.115,1,0.906 --look \
            --name nabd-medical-premium.cube                       -> transform + premium look
Input is Rec.709-legal video read as full-range RGB (what ffmpeg and Resolve hand a LUT for
"video level" clips): IRE v maps to 10-bit code 64 + 876*v, the scale Sony's formulas use.
"""
import argparse
import os

import numpy as np

N = 33
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "luts")

# Sony S-Gamut3.Cine -> CIE XYZ (D65), then XYZ -> Rec.709 primaries
SG3C_TO_XYZ = np.array([
    [0.599083920, 0.248925516, 0.102446490],
    [0.215075820, 0.885068502, -0.100144322],
    [-0.032065850, -0.027658391, 1.148781594],
])
XYZ_TO_709 = np.array([
    [3.2404542, -1.5371385, -0.4985314],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0556434, -0.2040259, 1.0572252],
])
SG3C_TO_709 = XYZ_TO_709 @ SG3C_TO_XYZ


def slog3_to_linear(v):
    code = 64 + 876 * np.asarray(v, dtype=float)
    return np.where(
        code >= 171.2102946929,
        10 ** ((code - 420) / 261.5) * (0.18 + 0.01) - 0.01,
        (code - 95) * 0.01125 / (171.2102946929 - 95),
    )


def filmic(x):
    # ACES-fitted tone curve (Narkowicz) — smooth toe and highlight shoulder, no hard clip
    x = np.maximum(x, 0) * 0.8
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)


def look(disp):
    """Premium medical commercial look, applied after the technical transform (display space).
    Controlled contrast, clean un-clipped whites, neutral shadows, a faint cool accent on the
    bright neutral background only, and protected skin."""
    import colorsys
    # gentle S-contrast around mid-grey, then set a clean black point without crushing
    s_ = disp * disp * (3 - 2 * disp)
    y = disp + (s_ - disp) * 0.5
    y = np.clip((y - 0.06) / (0.985 - 0.06), 0, 1)
    # soft highlight roll-off: whites approach ~0.93 instead of clipping
    y = np.where(y > 0.82, 0.82 + (1 - np.exp(-(y - 0.82) * 3.2)) * 0.11 / (1 - np.exp(-0.18 * 3.2)), y)
    h, l, sat = colorsys.rgb_to_hls(*np.clip(y, 0, 1))
    skin = 0.0 <= h <= 0.11 and sat > 0.08
    if skin:
        sat *= 0.97  # keep reds/oranges from running hot
    elif sat < 0.14:
        sat *= 0.5  # near-neutral wall: kill the yellow/green compression fringes, keep it clean white
    else:
        sat *= 1.06
    out = np.array(colorsys.hls_to_rgb(h, l, min(sat, 1)))
    # faint cool accent on bright, low-saturation surfaces (walls, coat whites) — not on skin
    if not skin and sat < 0.15:
        w = np.clip((l - 0.55) / 0.35, 0, 1) * (1 - sat / 0.15)
        out = out + np.array([-0.010, 0.002, 0.014]) * w
    return np.clip(out, 0, 1)


def transform(rgb, stops, wb, sat, creative=False):
    lin = slog3_to_linear(rgb)
    lin = SG3C_TO_709 @ lin
    lin = lin * (2 ** stops) * wb
    disp = filmic(lin) ** (1 / 2.2)
    luma = 0.2126 * disp[0] + 0.7152 * disp[1] + 0.0722 * disp[2]
    disp = np.clip(luma + (disp - luma) * sat, 0, 1)
    return look(disp) if creative else disp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stops", type=float, default=1.3, help="exposure correction in stops")
    ap.add_argument("--wb", default="1,1,1", help="linear R,G,B white-balance gains")
    ap.add_argument("--sat", type=float, default=1.0)
    ap.add_argument("--name", default="slog3-sgamut3cine-to-rec709.cube")
    ap.add_argument("--look", action="store_true", help="add the premium medical look after the transform")
    a = ap.parse_args()
    wb = np.array([float(x) for x in a.wb.split(",")])
    grid = np.linspace(0, 1, N)
    lines = ['TITLE "S-Log3/SGamut3.Cine to Rec709 (+exposure, WB)"', f"LUT_3D_SIZE {N}",
             "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    for b in grid:
        for g in grid:
            for r in grid:
                o = transform(np.array([r, g, b]), a.stops, wb, a.sat, a.look)
                lines.append(f"{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, a.name)
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
