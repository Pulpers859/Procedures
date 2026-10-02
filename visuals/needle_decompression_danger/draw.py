"""Needle decompression - the medial danger zone (plate on a shared painting).

The right hemithorax's bony cage from the front, head at the top, the
patient's right on the image left (house laterality; the record says to
pick the side clinically): clavicle, sternum, ribs 1-7 with their costal
cartilages, the upper humerus at the shoulder. The painting is
the approved needle_decompression_landmarks base (same layout, commit
42d1c7c), reused here (owner, 2026-10-02: reuse solved anatomy).

Record (this slot): the internal mammary artery runs 1-2 cm lateral to the
sternum - stay in the midclavicular line to avoid it; the intercostal bundle
runs along the inferior rib margin. Steps: catheter over the rib,
perpendicular to the chest wall.

Standard adult anatomy added: sternal angle at the 2nd costal cartilage;
the clavicle about 15 cm long, the midclavicular line through its midpoint
about 9.5 cm from the midline; the anterior axillary line about 14 cm from
the midline; rib shafts about 12 mm deep.

Code-drawn markings: the internal mammary artery 1.2 cm lateral to the
sternal edge inside a red band 0-2 cm from the edge, the midclavicular line
with the teal 2nd-space site, and an inset (not to scale) of one intercostal
space in sagittal section: vein, artery and nerve in the costal groove
under the upper rib, the catheter passing perpendicular just over the lower
rib.

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

ASSET_ID = "needle_decompression_danger"
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


INSET = (30.0, 690.0, 600.0, 1170.0)


def inset() -> str:
    x0, y0, x1, y1 = INSET
    ur, lr = (300.0, 800.0), (300.0, 1072.0)
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
    <circle id="iv-vein" cx="352" cy="866" r="13" fill="#5876B0" stroke="#34528A" stroke-width="3"/>
    <circle id="iv-artery" cx="356" cy="892" r="10" fill="#D8432A" stroke="#8E211D" stroke-width="3"/>
    <circle id="iv-nerve" cx="352" cy="915" r="9" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"/>
    <rect id="bundle" x="336" y="850" width="34" height="76" fill="#000" opacity="0"/>
    <line id="catheter" x1="{fmt(x0 + 24)}" y1="1000" x2="450" y2="1000" stroke="#7B848C" stroke-width="12" stroke-linecap="round"/>
    <line x1="{fmt(x0 + 24)}" y1="1000" x2="450" y2="1000" stroke="#E6EAEE" stroke-width="4"/>
  </g>"""


def build() -> str:
    t2 = c(ics(2, MCL_X))
    mcl_top, mcl_bot = c((MCL_X, -14)), c((MCL_X, 120))
    band0, band1 = c((STERNUM_HALF, 8)), c((STERNUM_HALF + 20, 190))
    ima = [c((STERNUM_HALF + 12, y)) for y in (8, 40, 80, 120, 160, 190)]
    labels = [
        Label(["Internal mammary artery"], anchor=(900, 1160), leader=[(1060, 1112), (ima[4][0] + 2, ima[4][1])], target_id="ima"),
        Label(["Midclavicular line"], anchor=(560, 90), leader=[(700, 106), (mcl_top[0], 160)], target_id="mcl"),
        Label(["2nd ICS, MCL"], anchor=(700, 560), leader=[(710, 520), (t2[0] + 30, t2[1] + 10)], target_id="target-2ics", emphasis=True),
        Label(["Neurovascular", "bundle"], anchor=(640, 860), leader=[(630, 880), (370, 888)], target_id="bundle"),
        Label(["Rib below"], anchor=(640, 1110), leader=[(630, 1090), (378, 1072)], target_id="lower-rib"),
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
  <rect id="danger-band" x="{fmt(band1[0])}" y="{fmt(band0[1])}" width="{fmt(band0[0] - band1[0])}" height="{fmt(band1[1] - band0[1])}" fill="#D8432A" fill-opacity="0.22" stroke="#D8432A" stroke-width="3" stroke-dasharray="12 8"/>
  <path id="ima" d="{smooth_path(ima, tension=0.8)}" fill="none" stroke="#C8322B" stroke-width="9" stroke-linecap="round"/>
  <line id="mcl" x1="{fmt(mcl_top[0])}" y1="{fmt(mcl_top[1])}" x2="{fmt(mcl_bot[0])}" y2="{fmt(mcl_bot[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  <ellipse id="target-2ics" cx="{fmt(t2[0])}" cy="{fmt(t2[1])}" rx="{fmt(6 * PX_MM)}" ry="{fmt(4.5 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="5"/>
  {inset()}
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
