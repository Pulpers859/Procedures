"""Needle decompression - the two sites (layout).

The right hemithorax's bony cage from the front, head at the top, the
patient's right on the image left (house laterality; the record says to
pick the side clinically): clavicle, sternum, ribs 1-7 with their costal
cartilages, the upper humerus at the shoulder. This painting is shared with
needle_decompression_danger.

Record: 4th or 5th intercostal space at the anterior axillary line
(preferred, lateral); 2nd intercostal space at the midclavicular line as the
alternate; catheter over the rib, perpendicular to the chest wall.

Standard adult anatomy added: sternal angle at the 2nd costal cartilage;
the clavicle about 15 cm long, the midclavicular line through its midpoint
about 9.5 cm from the midline; the anterior axillary line about 14 cm from
the midline; rib shafts about 12 mm deep.

Code-drawn markings: the midclavicular and anterior axillary lines, teal
zones in the 2nd intercostal space at the MCL and the 4th and 5th spaces at
the AAL.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down) at 6 px/mm.

Run: python3 visuals/needle_decompression_landmarks/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "needle_decompression_landmarks"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 6.0
ORIGIN = (1230.0, 130.0)           # canvas of the sternal notch

RIB_W = 12.0
STERNUM_HALF = 16.0
MCL_X, AAL_X = 95.0, 140.0
# Rib centrelines, sternum to lateral wall (x lateral, y down), mm.
RIBS = {
    1: [(16, 18), (35, 22), (58, 14), (76, 6)],
    2: [(17, 50), (60, 52), (110, 40), (158, 32), (172, 40)],
    3: [(17, 75), (65, 80), (115, 66), (162, 56), (176, 66)],
    4: [(17, 100), (70, 106), (120, 90), (165, 80), (178, 92)],
    5: [(17, 122), (75, 130), (122, 114), (167, 104), (180, 117)],
    6: [(17, 142), (80, 152), (124, 138), (168, 128), (181, 142)],
    7: [(17, 160), (85, 172), (126, 160), (168, 152), (181, 166)],
}
CARTILAGE_END = {1: 35, 2: 60, 3: 65, 4: 70, 5: 75, 6: 80, 7: 85}
CLAVICLE = [(8, 4), (40, 0), (80, -6), (120, -4), (150, -10), (166, -14)]
STERNUM = [(-STERNUM_HALF, 2), (-14, 50), (-13, 140), (-8, 175), (0, 186), (8, 175), (13, 140), (14, 50), (STERNUM_HALF, 2),
           (0, -2)]
HUMERUS = [(176, -24), (196, -30), (214, -18), (212, 4), (204, 40), (196, 90), (182, 92), (186, 40), (180, 2)]


def c(p):
    return (ORIGIN[0] - p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def rib_y(k, x):
    pts = RIBS[k]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def ics(k, x):
    """Centre of the intercostal space below rib k at lateral distance x."""
    return (x, (rib_y(k, x) + rib_y(k + 1, x)) / 2)


DEFS = """
<linearGradient id="bone" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EFE3C8"/><stop offset="1" stop-color="#DCCBA6"/></linearGradient>
"""

TARGETS = {"target-2ics": ics(2, MCL_X), "target-4ics": ics(4, AAL_X), "target-5ics": ics(5, AAL_X)}


def anatomy() -> str:
    parts = []
    for k, pts in RIBS.items():
        ce = CARTILAGE_END[k]
        bone = [p for p in pts if p[0] >= ce]
        cart = [p for p in pts if p[0] <= ce]
        y_ce = rib_y(k, ce)
        bone = [(ce, y_ce)] + [p for p in bone if p[0] > ce]
        cart = cart + [(ce, y_ce)]
        parts.append(f'<path d="{path(cart, tension=0.6)}" fill="none" stroke="#C9D6DC" stroke-width="{fmt(RIB_W * PX_MM * 0.8)}" stroke-linecap="round"/>')
        parts.append(f'<path id="rib-{k}" d="{path(bone, tension=0.6)}" fill="none" stroke="#E8DCC0" stroke-width="{fmt(RIB_W * PX_MM)}" stroke-linecap="round"/>')
    return "".join(parts)


def build() -> str:
    t = {k: c(v) for k, v in TARGETS.items()}
    mcl_top, mcl_bot = c((MCL_X, -14)), c((MCL_X, 190))
    aal_top, aal_bot = c((AAL_X, 20)), c((AAL_X, 190))
    labels = [
        Label(["Clavicle"], anchor=(560, 90), leader=[(700, 106), c((100, -5))], target_id="clavicle"),
        Label(["2nd ICS, MCL"], anchor=(980, 420), leader=[(990, 404), (t["target-2ics"][0] + 34, t["target-2ics"][1] + 6)],
              target_id="target-2ics", emphasis=True),
        Label(["4th–5th ICS, AAL"], anchor=(40, 1090), leader=[(300, 1040), (t["target-5ics"][0], t["target-5ics"][1] + 18)],
              target_id="target-5ics", emphasis=True),
        Label(["Midclavicular line"], anchor=(560, 1150), leader=[(700, 1100), (mcl_bot[0], 1080)], target_id="mcl"),
        Label(["Anterior axillary line"], anchor=(40, 300), leader=[(300, 320), (aal_top[0], 360)], target_id="aal"),
    ]
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

    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#F4F1EA"/>
  <path id="humerus" d="{path(HUMERUS, closed=True, tension=0.6)}" fill="url(#bone)" stroke="#A8977A" stroke-width="4"/>
  {anatomy()}
  <path id="sternum" d="{path(STERNUM, closed=True, tension=0.5)}" fill="url(#bone)" stroke="#A8977A" stroke-width="4"/>
  <path id="clavicle" d="{path(CLAVICLE, tension=0.7)}" fill="none" stroke="#E8DCC0" stroke-width="{fmt(14 * PX_MM)}" stroke-linecap="round"/>
</g>

<g class="marking">
  <line id="mcl" x1="{fmt(mcl_top[0])}" y1="{fmt(mcl_top[1])}" x2="{fmt(mcl_bot[0])}" y2="{fmt(mcl_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  <line id="aal" x1="{fmt(aal_top[0])}" y1="{fmt(aal_top[1])}" x2="{fmt(aal_bot[0])}" y2="{fmt(aal_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  {"".join(f'<ellipse id="{k}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(6 * PX_MM)}" ry="{fmt(4.5 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="5"/>' for k, p in t.items())}
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
