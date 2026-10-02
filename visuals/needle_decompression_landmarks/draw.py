"""Needle decompression - the two sites on the chest (torso layout).

An adult male lying supine, photographed from directly above, head at the
top, the patient's right on the image left (house laterality; the record says
pick the side clinically): neck, shoulders, the arms at the sides, the bare
chest to the upper abdomen. Owner, 2026-10-02: show the drawn rib cage over
an actual male torso (after a clinical photo the owner shared, concept only,
not committed), replacing the bone-only atlas plate (commit e8d3263).

Record: 4th or 5th intercostal space at the anterior axillary line
(preferred, lateral); 2nd intercostal space at the midclavicular line as the
alternate; catheter over the rib, perpendicular to the chest wall.

Code-drawn over the painting: the rib cage as translucent outlined bones
(both sides: clavicles, sternum, ribs 1-7, costal cartilages), from the
approved bone layout's geometry (commit 42d1c7c) narrowed by 12% to an
average chest; the midclavicular and anterior axillary lines on the right;
teal zones in the 2nd space at the MCL and the 4th and 5th spaces at the
AAL. The nipples are drawn at the 4th space on the MCL (standard male
anatomy), so the painting carries a landmark the reader can check against.

The painting is shared with needle_decompression_danger.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down) at 4 px/mm.

Run: python3 visuals/needle_decompression_landmarks/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "needle_decompression_landmarks"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 4.0
ORIGIN = (800.0, 270.0)            # canvas of the sternal notch
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


def build() -> str:
    t = {k: c(v) for k, v in TARGETS.items()}
    mcl_top, mcl_bot = c((MCL_X, -14)), c((MCL_X, 200))
    aal_top, aal_bot = c((AAL_X, 20)), c((AAL_X, 200))
    labels = [
        Label(["Clavicle"], anchor=(60, 120), leader=[(260, 140), c((130, -6))], target_id="clavicle"),
        Label(["2nd ICS, MCL"], anchor=(1010, 430), leader=[(1020, 414), (t["target-2ics"][0] + 14, t["target-2ics"][1] + 2)],
              target_id="target-2ics", emphasis=True),
        Label(["4th–5th ICS, AAL"], anchor=(40, 1060), leader=[(300, 1010), (t["target-5ics"][0], t["target-5ics"][1] + 14)],
              target_id="target-5ics", emphasis=True),
        Label(["Midclavicular line"], anchor=(500, 1150), leader=[(560, 1100), (mcl_bot[0], 1060)], target_id="mcl"),
        Label(["Anterior axillary line"], anchor=(40, 340), leader=[(250, 356), (aal_top[0], 420)], target_id="aal"),
    ]
    base_attr, base_image, layout_attr = painting_attrs()
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>{torso()}
</g>

<g class="marking">
  <g id="rib-cage">{rib_cage()}</g>
  <line id="mcl" x1="{fmt(mcl_top[0])}" y1="{fmt(mcl_top[1])}" x2="{fmt(mcl_bot[0])}" y2="{fmt(mcl_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  <line id="aal" x1="{fmt(aal_top[0])}" y1="{fmt(aal_top[1])}" x2="{fmt(aal_bot[0])}" y2="{fmt(aal_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  {"".join(f'<ellipse id="{k}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(5.5 * PX_MM)}" ry="{fmt(4 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.7" stroke="#0E8C98" stroke-width="5"/>' for k, p in t.items())}
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
