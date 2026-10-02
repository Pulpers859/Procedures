"""Needle decompression - the medial danger zone (torso, shared painting).

The same supine male torso photograph as needle_decompression_landmarks
(shared base, owner 2026-10-02: show the rib cage over an actual male
torso), with the rib cage drawn over it as translucent outlined bones.

Record (this slot): the internal mammary artery runs 1-2 cm lateral to the
sternum - stay in the midclavicular line to avoid it; the intercostal bundle
runs along the inferior rib margin. Steps: catheter over the rib,
perpendicular to the chest wall.

Code-drawn: the rib cage; the internal mammary arteries 1.2 cm lateral to
each sternal edge inside red bands 0-2 cm from the edge (they run deep to
the costal cartilages; drawn projected); the midclavicular line on the
right with the teal 2nd-space site; an inset (not to scale) of one
intercostal space in sagittal section: vein, artery and nerve in the costal
groove under the upper rib, the catheter passing perpendicular just over
the lower rib.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down) at 4 px/mm.

Run: python3 visuals/needle_decompression_danger/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "needle_decompression_danger"
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


# Fit to the painting (traced): the nipples land on the layout (MCL 8.4 cm),
# the sternal notch is 12.5 mm higher (canvas y 220) and the chest is
# narrower (lateral wall about 13.8 cm out). So y runs notch-to-nipple at
# 4.48 px/mm from y 220, and x is unchanged to the nipple line and compressed
# by 0.72 beyond it, so the ribs end at the painted chest wall.
FIT_ORIGIN_Y, FIT_PX_Y, FIT_X0, FIT_K = 220.0, 4.48, 84.0, 0.72


def fit_x(x):
    ax = abs(x)
    if ax > FIT_X0:
        ax = FIT_X0 + (ax - FIT_X0) * FIT_K
    return ax if x >= 0 else -ax


def c(p):
    if BASE.exists():
        return (ORIGIN[0] - fit_x(p[0]) * PX_MM, FIT_ORIGIN_Y + p[1] * FIT_PX_Y)
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


INSET = (30.0, 700.0, 590.0, 1170.0)


def inset() -> str:
    x0, y0, x1, y1 = INSET
    ur, lr = (300.0, 806.0), (300.0, 1076.0)
    return f"""
  <g id="inset">
    <rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28" fill="#FBF8F2" stroke="#9AA6B2" stroke-width="3"/>
    <rect x="{fmt(x0 + 70)}" y="{fmt(y0 + 14)}" width="40" height="{fmt(y1 - y0 - 28)}" fill="#E7A79A"/>
    <rect x="{fmt(x0 + 110)}" y="{fmt(y0 + 14)}" width="60" height="{fmt(y1 - y0 - 28)}" fill="#F2D27A"/>
    <rect id="inset-muscle" x="200" y="{fmt(y0 + 14)}" width="222" height="{fmt(y1 - y0 - 28)}" fill="#B65A55"/>
    <rect x="430" y="{fmt(y0 + 14)}" width="{fmt(x1 - 444)}" height="{fmt(y1 - y0 - 28)}" rx="6" fill="#F1C7C0"/>
    <line id="pleura" x1="426" y1="{fmt(y0 + 14)}" x2="426" y2="{fmt(y1 - 14)}" stroke="#8FA3B8" stroke-width="7"/>
    <ellipse id="upper-rib" cx="{fmt(ur[0])}" cy="{fmt(ur[1])}" rx="78" ry="56" fill="#EFE6D2" stroke="#A8977A" stroke-width="5"/>
    <ellipse id="lower-rib" cx="{fmt(lr[0])}" cy="{fmt(lr[1])}" rx="78" ry="56" fill="#EFE6D2" stroke="#A8977A" stroke-width="5"/>
    <circle cx="352" cy="872" r="13" fill="#5876B0" stroke="#34528A" stroke-width="3"/>
    <circle cx="356" cy="898" r="10" fill="#D8432A" stroke="#8E211D" stroke-width="3"/>
    <circle cx="352" cy="921" r="9" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"/>
    <rect id="bundle" x="336" y="856" width="34" height="76" fill="#000" opacity="0"/>
    <line id="catheter" x1="{fmt(x0 + 24)}" y1="1004" x2="450" y2="1004" stroke="#7B848C" stroke-width="12" stroke-linecap="round"/>
    <line x1="{fmt(x0 + 24)}" y1="1004" x2="450" y2="1004" stroke="#E6EAEE" stroke-width="4"/>
  </g>"""


def build() -> str:
    t2 = c(ics(2, MCL_X))
    mcl_top, mcl_bot = c((MCL_X, -14)), c((MCL_X, 130))
    bands, imas = [], []
    for side in (1, -1):
        e0, e1 = c((side * STERNUM_HALF, 8)), c((side * (STERNUM_HALF + 20), 186))
        x_lo, x_hi = sorted((e0[0], e1[0]))
        bid = ' id="danger-band"' if side == 1 else ""
        bands.append(f'<rect{bid} x="{fmt(x_lo)}" y="{fmt(e0[1])}" width="{fmt(x_hi - x_lo)}" height="{fmt(e1[1] - e0[1])}" '
                     f'fill="#D8432A" fill-opacity="0.20" stroke="#D8432A" stroke-width="3" stroke-dasharray="12 8"/>')
        pts = [c((side * (STERNUM_HALF + 12), y)) for y in (8, 40, 80, 120, 160, 186)]
        iid = ' id="ima"' if side == 1 else ""
        imas.append(f'<path{iid} d="{smooth_path(pts, tension=0.8)}" fill="none" stroke="#C8322B" stroke-width="8" stroke-linecap="round"/>')
    ima_r = c((STERNUM_HALF + 12, 60))
    labels = [
        Label(["Internal mammary artery"], anchor=(860, 1160), leader=[(980, 1112), c((-(STERNUM_HALF + 12), 175))], target_id="ima-left"),
        Label(["Midclavicular line"], anchor=(60, 120), leader=[(260, 140), (mcl_top[0], mcl_top[1] + 73)], target_id="mcl"),
        Label(["2nd ICS, MCL"], anchor=(40, 470), leader=[(330, 484), (t2[0] - 14, t2[1] + 2)], target_id="target-2ics", emphasis=True),
        Label(["Neurovascular", "bundle"], anchor=(640, 866), leader=[(630, 886), (370, 894)], target_id="bundle"),
        Label(["Rib below"], anchor=(640, 1060), leader=[(630, 1060), (378, 1076)], target_id="lower-rib"),
    ]
    base_attr, base_image, layout_attr = painting_attrs()
    imas[1] = imas[1].replace("<path d=", '<path id="ima-left" d=', 1)
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>{torso()}
</g>

<g class="marking">
  <g id="rib-cage">{rib_cage()}</g>
  {"".join(bands)}
  {"".join(imas)}
  <line id="mcl" x1="{fmt(mcl_top[0])}" y1="{fmt(mcl_top[1])}" x2="{fmt(mcl_bot[0])}" y2="{fmt(mcl_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  <ellipse id="target-2ics" cx="{fmt(t2[0])}" cy="{fmt(t2[1])}" rx="{fmt(5.5 * PX_MM)}" ry="{fmt(4 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.7" stroke="#0E8C98" stroke-width="5"/>
  {inset()}
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
