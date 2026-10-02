"""Pericardiocentesis - subxiphoid needle geometry, no-ultrasound fallback.

Reuses the approved supine male torso photograph and fitted rib-cage overlay
of needle_decompression_landmarks (owner, 2026-10-02: reuse solved anatomy;
rib cage over an actual torso). Head at the top, the patient's right on the
image left, so the patient's left (the side the record names) is on the
right.

Record: blind fallback route only, for when no machine is available. Needle
enters 1 cm below the costal margin just left of the xiphoid, tracks
shallowly under the costal margin at about 30-45 degrees, and aims toward
the left shoulder.

Code-drawn: the rib cage (as on the decompression plates), the xiphoid and
the costal margins (cartilages 7-10, standard anatomy), the entry zone 1 cm
below the left costal margin beside the xiphoid, a dashed arrow from it
toward the left shoulder, and an inset (not to scale): a sagittal section
with the needle passing at about 35 degrees to the skin, under the costal
margin, into a pericardial effusion.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down); the torso fit is the decompression plate's.

Run: python3 visuals/pericardiocentesis_needle_path/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

INSET_ANGLE = 35.0

ASSET_ID = "pericardiocentesis_needle_path"
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


XIPHOID = [(-5, 180), (-4, 196), (0, 204), (4, 196), (5, 180)]
MARGIN_L = [(-6, 188), (-20, 196), (-42, 206), (-70, 220), (-96, 236), (-112, 250)]
MARGIN_R = [(-x, y) for x, y in MARGIN_L]
ENTRY = (-15.0, 204.0)                      # 1 cm below the left costal margin, beside the xiphoid
LEFT_SHOULDER_PX = (1500.0, 175.0)          # the painted left shoulder (canvas px)
INSET = (30.0, 600.0, 640.0, 1170.0)


def inset() -> str:
    x0, y0, x1, y1 = INSET
    sk = y0 + 120.0
    e = (x0 + 150.0, sk)
    import math
    d = (math.cos(math.radians(INSET_ANGLE)), math.sin(math.radians(INSET_ANGLE)))
    tip = (e[0] + d[0] * 300, e[1] + d[1] * 300)
    back = (e[0] - d[0] * 90, e[1] - d[1] * 90)
    arc_r = 90
    a1 = (e[0] + arc_r * d[0], e[1] + arc_r * d[1])
    return f"""
  <g id="inset">
    <clipPath id="inset-clip"><rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28"/></clipPath>
    <rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28" fill="#FBF8F2" stroke="#9AA6B2" stroke-width="3"/>
    <g clip-path="url(#inset-clip)">
      <rect x="{fmt(x0)}" y="{fmt(sk)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - sk)}" fill="#F2D27A"/>
      <rect x="{fmt(x0)}" y="{fmt(sk - 6)}" width="{fmt(x1 - x0)}" height="12" fill="#E7A79A"/>
      <path id="inset-liver" d="M{fmt(x0)},{fmt(sk + 90)} C{fmt(x0 + 160)},{fmt(sk + 70)} {fmt(x0 + 260)},{fmt(sk + 160)} {fmt(x0 + 300)},{fmt(y1)} L{fmt(x0)},{fmt(y1)} Z" fill="#8E3B2E"/>
      <path id="inset-cartilage" d="M{fmt(x0 + 200)},{fmt(sk + 14)} C{fmt(x0 + 300)},{fmt(sk + 10)} {fmt(x0 + 420)},{fmt(sk + 12)} {fmt(x1)},{fmt(sk + 12)} L{fmt(x1)},{fmt(sk + 46)} C{fmt(x0 + 420)},{fmt(sk + 46)} {fmt(x0 + 300)},{fmt(sk + 46)} {fmt(x0 + 210)},{fmt(sk + 40)} Z" fill="#DDEAF0" stroke="#7F98A6" stroke-width="3"/>
      <ellipse id="effusion" cx="{fmt(x0 + 470)}" cy="{fmt(sk + 300)}" rx="200" ry="150" fill="#E9D58A" stroke="#B8962E" stroke-width="3"/>
      <ellipse id="heart" cx="{fmt(x0 + 490)}" cy="{fmt(sk + 320)}" rx="160" ry="115" fill="#B24A44" stroke="#7E2B27" stroke-width="3"/>
    </g>
    <path id="angle-arc" d="M{fmt(e[0] + arc_r)},{fmt(e[1])} A{arc_r},{arc_r} 0 0 1 {fmt(a1[0])},{fmt(a1[1])}" fill="none" stroke="#4A2F7A" stroke-width="5"/>
    <line x1="{fmt(e[0])}" y1="{fmt(e[1])}" x2="{fmt(e[0] + 140)}" y2="{fmt(e[1])}" stroke="#4A2F7A" stroke-width="3" stroke-dasharray="10 8"/>
    <line id="inset-needle" x1="{fmt(back[0])}" y1="{fmt(back[1])}" x2="{fmt(tip[0])}" y2="{fmt(tip[1])}" stroke="#5E6670" stroke-width="9" stroke-linecap="round"/>
    <line x1="{fmt(back[0])}" y1="{fmt(back[1])}" x2="{fmt(tip[0])}" y2="{fmt(tip[1])}" stroke="#D9DEE3" stroke-width="3"/>
    <circle id="inset-tip" cx="{fmt(tip[0])}" cy="{fmt(tip[1])}" r="4" fill="#000" opacity="0"/>
  </g>""", (a1[0] + e[0] + arc_r) / 2 + 4, (a1[1] + e[1]) / 2 + 8


def build() -> str:
    e = c(ENTRY)
    sh = LEFT_SHOULDER_PX
    dx, dy = sh[0] - e[0], sh[1] - e[1]
    n = (dx * dx + dy * dy) ** 0.5
    arrow_end = (e[0] + dx / n * 520, e[1] + dy / n * 520)
    on_dash = (e[0] + dx / n * 360, e[1] + dy / n * 360)
    inset_svg, ax, ay = inset()
    labels = [
        Label(["Xiphoid"], anchor=(560, 950), leader=[(700, 966), c((-3, 192))], target_id="xiphoid"),
        Label(["Entry site"], anchor=(1060, 1150), leader=[(1080, 1110), (e[0] + 18, e[1] + 8)], target_id="entry", emphasis=True),
        Label(["Toward left shoulder"], anchor=(1010, 560), leader=[(1180, 570), on_dash], target_id="direction"),
        Label(["30–45°"], anchor=(330, 700), leader=[(420, 710), (ax, ay)], target_id="angle-arc"),
        Label(["Effusion"], anchor=(330, 1150), leader=[(420, 1100), (500, 895)], target_id="effusion"),
    ]
    base_attr, base_image, layout_attr = painting_attrs()
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>{torso()}
</g>

<g class="marking">
  <defs><marker id="dir-head" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#0E8C98"/></marker></defs>
  <g id="rib-cage">{rib_cage()}</g>
  <path id="xiphoid" d="{path(XIPHOID, closed=True, tension=0.5)}" fill="#FFFFFF" fill-opacity="0.35" stroke="#8C7458" stroke-width="3"/>
  <path id="costal-margin-left" d="{path(MARGIN_L, tension=0.7)}" fill="none" stroke="#7F98A6" stroke-width="7" stroke-linecap="round"/>
  <path d="{path(MARGIN_R, tension=0.7)}" fill="none" stroke="#7F98A6" stroke-width="7" stroke-linecap="round"/>
  <line id="direction" x1="{fmt(e[0])}" y1="{fmt(e[1])}" x2="{fmt(arrow_end[0])}" y2="{fmt(arrow_end[1])}" stroke="#0E8C98" stroke-width="8" stroke-dasharray="20 12" marker-end="url(#dir-head)"/>
  <circle id="entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="22" fill="#6CCBD2" fill-opacity="0.75" stroke="#0E8C98" stroke-width="5"/>
  {inset_svg}
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
