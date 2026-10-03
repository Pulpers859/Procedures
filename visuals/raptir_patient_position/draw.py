"""RAPTIR (retroclavicular infraclavicular) block - probe and needle on the patient (layout).

Reuses the approved supine male torso layout of needle_decompression_landmarks
(commit bb45dce; owner, 2026-10-02: reuse solved anatomy): head at the top,
the patient's right on the image left, arms adducted at the sides.

Record: supine, arm adducted; transducer sagittal over the infraclavicular
fossa; needle inserted posterior to the clavicle, aimed caudally, strictly
in-plane.

Owner, 2026-10-03: a handle lying flat looked wrong, and two oblique views
failed in Gemini; this is the overhead view that worked for the femoral,
PENG and interscalene plates, with the probe standing upright: its
footprint sagittal in the right infraclavicular fossa below the lateral
third of the clavicle, its handle rising toward the camera and drawn
foreshortened toward the feet, with the cable; the needle entering in the supraclavicular
fossa just above (behind) the clavicle, directly cranial to the probe and in
line with it, pointing caudally under the clavicle. The clavicle is marked in
code as a dashed line.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down) at 5.8 px/mm, zoomed to the right shoulder.

Run: python3 visuals/raptir_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "raptir_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 5.8
ORIGIN = (1252.0, 406.0)           # canvas of the sternal notch
SX = 0.88                          # the bone layout's ribs, narrowed to an average chest

RIB_W = 12.0
STERNUM_HALF = 16.0
MCL_X, AAL_X = 95.0 * SX, 140.0 * SX
_RIBS = {
    1: [(16, 18), (35, 22), (58, 14), (76, 6)],
    2: [(17, 50), (60, 52), (110, 40), (158, 32), (172, 40)],
    3: [(17, 75), (65, 80), (115, 66), (162, 56), (176, 66)],
    4: [(17, 100), (70, 106), (120, 90), (165, 80), (178, 92)],
    5: [(17, 122), (75, 130), (122, 114), (167, 104), (180, 117)],
    6: [(17, 142), (80, 152), (124, 138), (168, 128), (181, 142)],
    7: [(17, 160), (85, 172), (126, 160), (168, 152), (181, 166)],
}
RIBS = {k: [(max(STERNUM_HALF, x * SX), y) for x, y in pts] for k, pts in _RIBS.items()}
CARTILAGE_END = {k: v * SX for k, v in {1: 35, 2: 60, 3: 65, 4: 70, 5: 75, 6: 80, 7: 85}.items()}
CLAVICLE = [(8, 4), (40, 0), (80, -6), (120, -4), (150, -10), (162, -14)]
STERNUM = [(-STERNUM_HALF, 2), (-14, 50), (-13, 140), (-8, 175), (0, 186), (8, 175), (13, 140), (14, 50),
           (STERNUM_HALF, 2), (0, -2)]

# Torso (painted layer), right half; mirrored for the left.
TORSO_R = [(0, -130), (40, -130), (46, -80), (70, -52), (130, -42), (178, -30), (204, -6), (214, 40), (212, 120),
           (210, 200), (208, 260), (0, 260)]
ARM_GAP_R = [(176, 70), (178, 140), (180, 210)]
NIPPLE_R = (MCL_X, 103.0)
PEC_R = [(150, 66), (120, 112), (84, 124), (40, 118), (12, 108)]


def c(p):
    return (ORIGIN[0] - p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def mirror(pts):
    return [(-x, y) for x, y in pts]


def rib_y(k, x):
    pts = RIBS[k]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1 and x1 > x0:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def ics(k, x):
    """Centre of the intercostal space below rib k at lateral distance x."""
    return (x, (rib_y(k, x) + rib_y(k + 1, x)) / 2)


def catmull(pts, n=10):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        for s in range(n):
            t = s / n
            out.append(tuple(0.5 * ((2 * p[i][d]) + (-p[i - 1][d] + p[i + 1][d]) * t
                                    + (2 * p[i - 1][d] - 5 * p[i][d] + 4 * p[i + 1][d] - p[i + 2][d]) * t * t
                                    + (-p[i - 1][d] + 3 * p[i][d] - 3 * p[i + 1][d] + p[i + 2][d]) * t ** 3)
                             for d in (0, 1)))
    out.append(pts[-1])
    return out


def band(centre_mm, width_mm):
    """A bone drawn as a closed outline of the given width around a centreline."""
    pts = [c(q) for q in catmull(centre_mm)]
    half = width_mm * PX_MM / 2
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n * half, dx / n * half
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    ring = left + list(reversed(right))
    return "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in ring) + " Z"


BONE = 'fill="#FFFFFF" fill-opacity="0.30" stroke="#8C7458" stroke-width="3" stroke-linejoin="round"'
CART = 'fill="#DDEAF0" fill-opacity="0.30" stroke="#7F98A6" stroke-width="2.5" stroke-linejoin="round"'


def rib_cage() -> str:
    parts = []
    for side in (1, -1):
        sgn = (lambda pts: pts) if side == 1 else mirror
        for k, pts in RIBS.items():
            ce = CARTILAGE_END[k]
            y_ce = rib_y(k, ce)
            bone = [(ce, y_ce)] + [p for p in pts if p[0] > ce]
            cart = [p for p in pts if p[0] < ce] + [(ce, y_ce)]
            if len(cart) >= 2:
                parts.append(f'<path d="{band(sgn(cart), RIB_W * 0.8)}" {CART}/>')
            rid = f' id="rib-{k}"' if side == 1 else ""
            parts.append(f'<path{rid} d="{band(sgn(bone), RIB_W)}" {BONE}/>')
        cid = ' id="clavicle"' if side == 1 else ""
        parts.append(f'<path{cid} d="{band(sgn(CLAVICLE), 14)}" {BONE}/>')
    parts.append(f'<path id="sternum" d="{path(STERNUM, closed=True, tension=0.5)}" {BONE}/>')
    return "".join(parts)


TARGETS = {"target-2ics": ics(2, MCL_X), "target-4ics": ics(4, AAL_X), "target-5ics": ics(5, AAL_X)}


def painting_attrs():
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    scale = 1600 / BASE_SIZE[0]
    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if debug else 0}"'
    else:
        base_attr = base_image = layout_attr = ""
    return base_attr, base_image, layout_attr


def torso() -> str:
    nr = c(NIPPLE_R)
    nl = c((-NIPPLE_R[0], NIPPLE_R[1]))
    return f"""
  <rect x="0" y="0" width="1600" height="1200" fill="#D3DDE6"/>
  <path id="torso" d="{path(TORSO_R + list(reversed(mirror(TORSO_R)))[1:], closed=True, tension=0.5)}" fill="#E7BFA4" stroke="#B98A74" stroke-width="3"/>
  <path d="{path(ARM_GAP_R, tension=0.8)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  <path d="{path(mirror(ARM_GAP_R), tension=0.8)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  <path d="{path(PEC_R, tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="5" opacity="0.8"/>
  <path d="{path(mirror(PEC_R), tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="5" opacity="0.8"/>
  <ellipse cx="{fmt(c((0, 0))[0])}" cy="{fmt(c((0, 0))[1])}" rx="26" ry="16" fill="#D7A88E"/>
  <circle id="nipple-right" cx="{fmt(nr[0])}" cy="{fmt(nr[1])}" r="{fmt(12 * PX_MM / 2)}" fill="#B87F6C"/>
  <circle cx="{fmt(nl[0])}" cy="{fmt(nl[1])}" r="{fmt(12 * PX_MM / 2)}" fill="#B87F6C"/>"""


PROBE_X = 100.0
PROBE_Y0, PROBE_Y1 = 8.0, 50.0
PROBE_W = 9.0
NEEDLE_ENTRY = (PROBE_X, -17.0)
NEEDLE_HUB = (PROBE_X, -52.0)


def build() -> str:
    p0, p1 = c((PROBE_X + PROBE_W / 2, PROBE_Y0)), c((PROBE_X - PROBE_W / 2, PROBE_Y1))
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    mid_y = (p0[1] + p1[1]) / 2
    cx = (p0[0] + p1[0]) / 2
    handle = (f"M{fmt(cx - 34)},{fmt(mid_y)} L{fmt(cx + 34)},{fmt(mid_y)} L{fmt(cx + 26)},{fmt(mid_y + 230)} "
              f"L{fmt(cx - 26)},{fmt(mid_y + 230)} Z")
    clav = [c(q) for q in CLAVICLE]
    labels = [
        Label(["Clavicle"], anchor=(1020, 300), leader=[(1030, 320), c((40, 0))], target_id="clavicle-mark"),
        Label(["Linear probe"], anchor=(40, 860), leader=[(200, 820), (cx - 10, mid_y + 150)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(780, 150), leader=[(770, 170), (ne[0], (ne[1] + nh[1]) / 2)], target_id="needle"),
    ]
    base_attr, base_image, layout_attr = painting_attrs()
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>{torso()}
  <path id="clavicle-ridge" d="{path(CLAVICLE, tension=0.7)}" fill="none" stroke="#F0CFBA" stroke-width="22" stroke-linecap="round" opacity="0.7"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0])},{fmt(nh[1] - 40)} {fmt(nh[0] - 80)},{fmt(nh[1] - 50)} {fmt(nh[0] - 200)},-20" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 8)}" y="{fmt(nh[1] - 30)}" width="16" height="34" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path d="M{fmt(cx)},{fmt(mid_y + 220)} C{fmt(cx)},{fmt(mid_y + 330)} {fmt(cx - 120)},{fmt(mid_y + 380)} {fmt(cx - 300)},1240" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="16" fill="#E9ECEF" stroke="#7D868F" stroke-width="3"/>
  <path id="probe-handle" d="{handle}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <path id="clavicle-mark" d="{smooth_path(clav, tension=0.7)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #D3DDE6; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
