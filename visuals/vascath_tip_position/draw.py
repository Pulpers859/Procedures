"""Dialysis catheter tip position - anterior view of the neck and upper chest.

Confirmation view, so the radiograph convention: head at the top, the
patient's right on the image left. Skin and chest wall are see-through,
showing the right internal jugular, the brachiocephalic veins, the superior
vena cava and the right atrium, with the clavicles, first ribs, sternum,
trachea, aorta and pulmonary trunk for orientation.

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
CAJ = (792.0, 862.0)               # cavoatrial junction, about 7 cm of SVC below its origin
SVC_ORIGIN = (792.0, 520.0)        # behind the first right costal cartilage

# Vessel centrelines and widths (mm).
RIGHT_IJ = ([(628, -20), (650, 150), (676, 300), (700, 385)], 12)
RIGHT_SUBCLAVIAN = ([(300, 420), (500, 405), (700, 385)], 11)
RIGHT_BCV = ([(700, 385), (745, 450), (792, 520)], 13)
LEFT_IJ = ([(1012, -20), (990, 150), (964, 300), (940, 372)], 12)
LEFT_SUBCLAVIAN = ([(1340, 420), (1140, 400), (940, 372)], 11)
LEFT_BCV = ([(940, 372), (880, 440), (792, 520)], 12)
SVC = ([SVC_ORIGIN, (794, 700), CAJ], 20)
CATHETER = [(688, 228), (676, 300), (700, 385), (745, 450), (792, 520), (794, 700), CAJ]

RIGHT_ATRIUM = [(770, 866), (700, 890), (640, 960), (622, 1060), (650, 1170), (720, 1240), (860, 1240), (880, 1060), (850, 900)]
HEART = [(770, 866), (700, 890), (640, 960), (622, 1060), (650, 1170), (720, 1240), (1280, 1240), (1290, 1130), (1230, 1010), (1120, 920), (1000, 880), (900, 860)]
AORTA = [(880, 940), (866, 780), (870, 640), (900, 560), (960, 530), (1015, 560)]
DESCENDING_AORTA = [(1015, 560), (1035, 640), (1040, 800), (1035, 1000), (1030, 1240)]
PULMONARY_TRUNK = [(990, 960), (975, 850), (985, 760)]
LEFT_PA = [(985, 760), (1060, 730), (1140, 740)]
TRACHEA = [(CX, -20), (CX, 540)]
CARINA_L, CARINA_R = [(CX, 540), (870, 610), (930, 680)], [(CX, 540), (770, 610), (720, 690)]
CLAVICLE_R = [(770, 425), (690, 405), (560, 395), (420, 375), (300, 335), (180, 310)]
CLAVICLE_L = [(2 * CX - x, y) for x, y in CLAVICLE_R]
FIRST_RIB_R = [(760, 480), (660, 455), (560, 430), (480, 440), (430, 490)]
FIRST_RIB_L = [(2 * CX - x, y) for x, y in FIRST_RIB_R]
MANUBRIUM = [(750, 420), (890, 420), (910, 470), (880, 640), (760, 640), (730, 470)]
STERNUM = [(760, 640), (880, 640), (870, 1230), (770, 1230)]


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
        Label(["Superior", "vena cava"], anchor=(40, 640), leader=[(300, 652), (794, 700)],
              target_id="svc"),
        Label(["Cavoatrial", "junction"], anchor=(1200, 330), leader=[(1210, 342), (1100, 520), CAJ],
              target_id="cavoatrial-junction", emphasis=True),
        Label(["Right atrium"], anchor=(40, 1050), leader=[(390, 1040), (700, 1040)],
              target_id="right-atrium"),
    ]

    bone = 'fill="url(#bone)" fill-opacity="0.75" stroke="#A8977A" stroke-width="2.5"'
    rib = 'fill="none" stroke="#E2D6BD" stroke-width="30" stroke-linecap="round" opacity="0.8"'
    body = f"""
<g id="anatomy">
  <rect id="torso" x="-10" y="-10" width="1620" height="1220" fill="url(#skin)"/>
  <path d="{smooth_path(TRACHEA)}" stroke="#D9E3EA" stroke-width="{fmt(mm(18))}" stroke-linecap="round" opacity="0.8"/>
  <path d="{smooth_path(CARINA_L)}" fill="none" stroke="#D9E3EA" stroke-width="{fmt(mm(12))}" stroke-linecap="round" opacity="0.8"/>
  <path d="{smooth_path(CARINA_R)}" fill="none" stroke="#D9E3EA" stroke-width="{fmt(mm(13))}" stroke-linecap="round" opacity="0.8"/>

  <path d="{smooth_path(FIRST_RIB_R)}" {rib}/>
  <path d="{smooth_path(FIRST_RIB_L)}" {rib}/>
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
  <circle id="cavoatrial-junction" cx="{fmt(CAJ[0])}" cy="{fmt(CAJ[1])}" r="{fmt(mm(9))}" fill="#000" fill-opacity="0"/>

  <path id="manubrium" d="{smooth_path(MANUBRIUM, closed=True, tension=0.5)}" {bone} opacity="0.45"/>
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
