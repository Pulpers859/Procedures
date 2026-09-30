"""Dialysis catheter tip position - anterior view of the neck and upper chest.

Confirmation view, so the radiograph convention: head at the top, the
patient's right on the image left. Skin and chest wall are see-through,
showing the right internal jugular, the brachiocephalic veins, the superior
vena cava and the right atrium, with the clavicles, first ribs, sternum,
trachea, aorta and pulmonary trunk for orientation. The SVC runs along the right
sternal border (about 2 cm right of midline), as on a chest X-ray; an earlier
version had it near the midline, where the sternum hid the junction.

Marking (drawn again in code over the painted base): the catheter, from the
right IJ puncture down the IJ, brachiocephalic vein and SVC, to a tip at the
cavoatrial junction - not in the atrium. At true scale its in-body length is
about 13 cm, inside the record's right IJ depth of 12-15 cm.

Scale: 5 px per mm.

Run: python3 visuals/vascath_tip_position/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "vascath_tip_position"
PX_PER_MM = 5.0
CX = 820.0                         # midline
CAJ = (718.0, 862.0)               # cavoatrial junction, about 7 cm of SVC below its origin
SVC_ORIGIN = (722.0, 520.0)        # behind the first right costal cartilage, about 2 cm right of midline

# Vessel centrelines and widths (mm). The SVC runs along the right sternal
# border and forms the right upper mediastinal edge, as on a chest X-ray.
RIGHT_IJ = ([(610, -20), (640, 150), (668, 300), (690, 395)], 12)
RIGHT_SUBCLAVIAN = ([(300, 425), (500, 410), (690, 395)], 11)
RIGHT_BCV = ([(690, 395), (702, 455), (722, 520)], 13)
LEFT_IJ = ([(1030, -20), (1000, 150), (972, 300), (950, 390)], 12)
LEFT_SUBCLAVIAN = ([(1340, 425), (1140, 410), (950, 390)], 11)
LEFT_BCV = ([(950, 390), (860, 440), (722, 520)], 12)
SVC = ([SVC_ORIGIN, (720, 700), CAJ], 20)
CATHETER = [(688, 228), (668, 300), (690, 395), (702, 455), (722, 520), (720, 700), CAJ]

RIGHT_ATRIUM = [(700, 866), (650, 900), (610, 980), (600, 1070), (628, 1170), (700, 1240), (820, 1240), (830, 1060), (770, 900)]
HEART = [(700, 866), (650, 900), (610, 980), (600, 1070), (628, 1170), (700, 1240), (1280, 1240), (1290, 1130), (1230, 1010), (1120, 920), (1000, 880), (860, 860)]
AORTA = [(835, 940), (812, 780), (815, 640), (850, 555), (920, 525), (975, 560)]
DESCENDING_AORTA = [(975, 560), (990, 700), (995, 1000), (990, 1240)]
PULMONARY_TRUNK = [(905, 960), (895, 860), (905, 770)]
LEFT_PA = [(905, 770), (990, 735), (1080, 745)]
TRACHEA = [(CX, -20), (CX, 540)]
CARINA_L, CARINA_R = [(CX, 540), (870, 610), (930, 680)], [(CX, 540), (770, 610), (720, 690)]
CLAVICLE_R = [(700, 432), (620, 410), (500, 395), (380, 372), (270, 338), (170, 318)]
CLAVICLE_L = [(2 * CX - x, y) for x, y in CLAVICLE_R]
MANUBRIUM = [(690, 425), (770, 418), (820, 428), (870, 418), (950, 425), (925, 530), (905, 640), (735, 640), (715, 530)]
STERNUM = [(745, 640), (895, 640), (888, 1000), (880, 1240), (760, 1240), (752, 1000)]
# Anterior ribs 1-7, right side: sternal end y, as (sternal end, end of cartilage, lateral points).
RIB_Y = [470, 575, 690, 805, 920, 1035, 1150]


def rib(y, side):
    """One anterior rib: cartilage from the sternal edge, then bone sweeping laterally and upward."""
    sx = 745 if side < 0 else 895
    flip = (lambda x: x) if side < 0 else (lambda x: 2 * CX - x)
    cart = [(flip(sx) if side < 0 else sx, y), (flip(660), y - 12)]
    bone = [(flip(660), y - 12), (flip(540), y - 40), (flip(420), y - 95), (flip(320), y - 165), (flip(250), y - 250), (flip(215), y - 330)]
    return cart, bone


def mm(v):
    return v * PX_PER_MM


def vessel(element_id, structure, colour, opacity=0.7, extra=""):
    points, width = structure
    cap = "butt" if element_id == "svc" else "round"      # the SVC ends exactly at the junction
    return (f'<path id="{element_id}" d="{smooth_path(points)}" fill="none" stroke="{colour}" '
            f'stroke-width="{fmt(mm(width))}" stroke-linecap="{cap}" stroke-opacity="{opacity}" {extra}/>')


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#EBCBB7"/><stop offset="0.5" stop-color="#F7E6DA"/>
  <stop offset="1" stop-color="#EBCBB7"/></linearGradient>
<radialGradient id="heart" cx="0.45" cy="0.4" r="0.7"><stop offset="0" stop-color="#E4A597"/><stop offset="1" stop-color="#C47566"/></radialGradient>
<linearGradient id="bone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6F0E2"/><stop offset="1" stop-color="#D8CBAE"/></linearGradient>
<filter id="lift" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1800" height="1400"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#6B4A3C" flood-opacity="0.2"/></filter>
"""


def build() -> str:
    labels = [
        Label(["Superior", "vena cava"], anchor=(40, 640), leader=[(300, 652), (720, 700)],
              target_id="svc"),
        Label(["Cavoatrial", "junction"], anchor=(1200, 330), leader=[(1210, 342), (1100, 520), CAJ],
              target_id="cavoatrial-junction", emphasis=True),
        Label(["Right atrium"], anchor=(40, 1120), leader=[(390, 1110), (680, 1060)],
              target_id="right-atrium"),
    ]

    bone = 'fill="url(#bone)" fill-opacity="0.75" stroke="#A8977A" stroke-width="2.5"'
    ribs = ""
    for y in RIB_Y:
        for side in (-1, 1):
            cart, bone_pts = rib(y, side)
            ribs += (f'<path d="{smooth_path(cart)}" fill="none" stroke="#DCE6EC" stroke-width="{fmt(mm(9))}" stroke-linecap="round"/>'
                     f'<path d="{smooth_path(bone_pts)}" fill="none" stroke="#E6DAC0" stroke-width="{fmt(mm(11))}" stroke-linecap="round"/>')
    body = f"""
<g id="anatomy">
  <rect id="torso" x="-10" y="-10" width="1620" height="1220" fill="url(#skin)"/>
  <g id="rib-cage" opacity="0.7">{ribs}</g>
  <path d="{smooth_path(TRACHEA)}" stroke="#D9E3EA" stroke-width="{fmt(mm(18))}" stroke-linecap="round" opacity="0.8"/>
  <path d="{smooth_path(CARINA_L)}" fill="none" stroke="#D9E3EA" stroke-width="{fmt(mm(12))}" stroke-linecap="round" opacity="0.8"/>
  <path d="{smooth_path(CARINA_R)}" fill="none" stroke="#D9E3EA" stroke-width="{fmt(mm(13))}" stroke-linecap="round" opacity="0.8"/>

  <path d="{smooth_path(DESCENDING_AORTA)}" fill="none" stroke="#C8423A" stroke-width="{fmt(mm(20))}" stroke-linecap="round" opacity="0.3"/>
  <path d="{smooth_path(DESCENDING_AORTA)}" fill="none" stroke="#8E2A24" stroke-width="3" stroke-dasharray="14 10" opacity="0.5"/>
  <path d="{smooth_path(LEFT_PA)}" fill="none" stroke="#6E8FC4" stroke-width="{fmt(mm(16))}" stroke-linecap="round" opacity="0.85"/>
  <path id="pulmonary-trunk" d="{smooth_path(PULMONARY_TRUNK)}" fill="none" stroke="#6E8FC4" stroke-width="{fmt(mm(24))}" stroke-linecap="round" opacity="0.9"/>
  <path id="aorta" d="{smooth_path(AORTA)}" fill="none" stroke="#C8423A" stroke-width="{fmt(mm(24))}" stroke-linecap="round" opacity="0.9" filter="url(#lift)"/>
  <path id="heart" d="{smooth_path(HEART, closed=True, tension=0.7)}" fill="url(#heart)" stroke="#A85A4C" stroke-width="3" filter="url(#lift)"/>
  <path id="right-atrium" d="{smooth_path(RIGHT_ATRIUM, closed=True, tension=0.7)}" fill="#9AA6CF" fill-opacity="0.85" stroke="#6E6F9E" stroke-width="2.5"/>

  {vessel("right-subclavian", RIGHT_SUBCLAVIAN, "#5277B8")}
  {vessel("left-subclavian", LEFT_SUBCLAVIAN, "#5277B8")}
  {vessel("left-ij", LEFT_IJ, "#5277B8")}
  {vessel("left-bcv", LEFT_BCV, "#5277B8", 0.8)}
  {vessel("right-ij", RIGHT_IJ, "#5277B8", 0.85)}
  {vessel("right-bcv", RIGHT_BCV, "#5277B8", 0.85)}
  {vessel("svc", SVC, "#4F74B6", 0.95)}
  <circle cx="{fmt(SVC_ORIGIN[0])}" cy="{fmt(SVC_ORIGIN[1])}" r="{fmt(mm(10))}" fill="#4F74B6" fill-opacity="0.95"/>
  <circle id="cavoatrial-junction" cx="{fmt(CAJ[0])}" cy="{fmt(CAJ[1])}" r="{fmt(mm(9))}" fill="#000" fill-opacity="0"/>

  <g id="sternum" fill="url(#bone)" stroke="#A8977A" stroke-width="2.5" opacity="0.42">
    <path d="{smooth_path(MANUBRIUM, closed=True, tension=0.3)}"/>
    <path d="{smooth_path(STERNUM, closed=True, tension=0.3)}"/>
  </g>
  <path id="clavicle-right" d="{smooth_path(CLAVICLE_R)}" fill="none" stroke="url(#bone)" stroke-width="{fmt(mm(14))}" stroke-linecap="round" filter="url(#lift)" opacity="0.9"/>
  <path d="{smooth_path(CLAVICLE_L)}" fill="none" stroke="url(#bone)" stroke-width="{fmt(mm(14))}" stroke-linecap="round" filter="url(#lift)" opacity="0.9"/>

  <g class="marking">
    <path id="catheter" d="{smooth_path(CATHETER)}" fill="none" stroke="#F4F5F2" stroke-width="18" stroke-linecap="round"/>
    <path d="{smooth_path(CATHETER)}" fill="none" stroke="#2B3440" stroke-width="3" stroke-dasharray="1 0" opacity="0.6"
          transform="translate(-4 0)"/>
    <circle id="catheter-tip" cx="{fmt(CAJ[0])}" cy="{fmt(CAJ[1])}" r="{fmt(mm(6))}" fill="none" stroke="#0E8C98" stroke-width="6"/>
    <circle cx="688" cy="228" r="9" fill="#D8432A"/>
  </g>
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
