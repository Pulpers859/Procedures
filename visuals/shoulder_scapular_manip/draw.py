"""Shoulder reduction - scapular manipulation, patient prone (layout).

Owner, 2026-10-04: prone. A hanging arm cannot be seen from straight above,
so the camera stands at the patient's right side, raised about 45 degrees:
the patient lies face down across the frame with the head on the image
right and the hips on the left; the back faces up and away; the right arm
hangs straight down off the near edge of the stretcher toward the floor.
The right side is the house laterality (the record names no side).

Record: scapular manipulation; patient prone (or seated), the affected arm
hanging with gentle traction; rotate the scapular tip with slow, steady
traction using low force.

Added (standard technique, not in the record): the inferior tip is pushed
medially, toward the spine, while the upper scapula is held steady.

Code-drawn over the painting, traced on it: the right scapula as a
translucent outlined bone (medial border, inferior tip, spine and acromion);
a curved arrow at the tip toward the spine; a downward arrow along the arm
(gentle traction). No hands.

Perspective layout in canvas pixels, about 1.8 px/mm at the shoulder.

Run: python3 visuals/shoulder_scapular_manip/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "shoulder_scapular_manip"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

MATTRESS_FAR, MATTRESS_NEAR, MATTRESS_SIDE = 230.0, 580.0, 660.0
# Traced on the painting (Gemini lowered the camera to nearly level, so the back's top is the skyline).
BACK = [(-40, 330), (250, 305), (700, 290), (1050, 280), (1150, 300), (1210, 380), (1215, 520), (1100, 600),
        (960, 598), (700, 610), (300, 612), (-40, 610)]
NECK = [(1150, 330), (1250, 345), (1285, 420), (1250, 500), (1180, 470)]
HEAD = ((1400.0, 360.0), 110.0, 100.0)
EAR = ((1400.0, 470.0), 26.0, 38.0)
SHORTS = [(-40, 320), (230, 310), (250, 615), (-40, 610)]
ARM = [(1150, 380), (1207, 440), (1190, 667), (1080, 853), (1067, 1013), (1080, 1240), (933, 1240), (920, 1067),
       (907, 907), (933, 747), (960, 593), (1050, 480)]
SPINE = [(260, 312), (600, 300), (900, 292), (1080, 290), (1150, 300)]
SCAPULA = [(1090, 302), (980, 318), (860, 378), (930, 420), (1040, 470), (1130, 505), (1175, 450), (1150, 360)]
SCAP_SPINE = [(1075, 318), (1130, 370), (1190, 420)]
TIP = (860.0, 378.0)
DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDCDB8"/><stop offset="1" stop-color="#D9AE95"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E4E9EE"/><stop offset="1" stop-color="#F4F6F8"/></linearGradient>
<marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 Z" fill="#0E8C98"/></marker>
"""


def ell(el_id, e, attrs):
    return (f'<ellipse id="{el_id}" cx="{fmt(e[0][0])}" cy="{fmt(e[0][1])}" rx="{fmt(e[1])}" ry="{fmt(e[2])}" {attrs}/>')


def build() -> str:
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

    tip_arrow = f"M{fmt(TIP[0] + 20)},{fmt(TIP[1] + 92)} C{fmt(TIP[0] - 40)},{fmt(TIP[1] + 72)} {fmt(TIP[0] - 60)},{fmt(TIP[1] + 12)} {fmt(TIP[0] - 30)},{fmt(TIP[1] - 48)}"
    labels = [
        Label(["Rotate the tip", "toward the spine"], anchor=(300, 130), leader=[(560, 190), (821, 415)],
              target_id="tip-arrow", emphasis=True),
        Label(["Spine"], anchor=(40, 230), leader=[(140, 250), (260, 312)], target_id="spine-line"),
        Label(["Scapula"], anchor=(1100, 150), leader=[(1150, 170), (1040, 420)], target_id="scapula"),
        Label(["Arm hangs,", "gentle traction"], anchor=(440, 1060), leader=[(840, 1040), (1002, 1060)], target_id="traction"),
    ]
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#C9D3DC"/>
  <rect x="0" y="{fmt(MATTRESS_SIDE)}" width="1600" height="{fmt(1200 - MATTRESS_SIDE)}" fill="#9AA6B1"/>
  <rect id="mattress" x="-10" y="{fmt(MATTRESS_FAR)}" width="1620" height="{fmt(MATTRESS_NEAR - MATTRESS_FAR)}" fill="url(#sheet)" stroke="#B9C2CB" stroke-width="3"/>
  <rect x="-10" y="{fmt(MATTRESS_NEAR)}" width="1620" height="{fmt(MATTRESS_SIDE - MATTRESS_NEAR)}" fill="#5E6E7C"/>
  <path id="back" d="{smooth_path(BACK, closed=True, tension=0.5)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path d="{smooth_path(NECK, closed=True, tension=0.6)}" fill="#E3BCA4" stroke="#B98A74" stroke-width="3"/>
  {ell("head", HEAD, 'fill="#5A4234" stroke="#3E2C22" stroke-width="3"')}
  {ell("ear", EAR, 'fill="#D9A88C" stroke="#A9765F" stroke-width="3"')}
  <path id="shorts" d="{smooth_path(SHORTS, closed=True, tension=0.3)}" fill="#3F5F7F" stroke="#2E4660" stroke-width="3"/>
  <path id="arm" d="{smooth_path(ARM, closed=True, tension=0.5)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
</g>

<g class="marking">
  <path id="scapula" d="{smooth_path(SCAPULA, closed=True, tension=0.5)}" fill="#FFFFFF" fill-opacity="0.30" stroke="#8C7458" stroke-width="4" stroke-linejoin="round"/>
  <path d="{smooth_path(SCAP_SPINE, tension=0.6)}" fill="none" stroke="#8C7458" stroke-width="10" stroke-linecap="round" opacity="0.7"/>
  <path id="spine-line" d="{smooth_path(SPINE, tension=0.6)}" fill="none" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="18 12"/>
  <path id="tip-arrow" d="{tip_arrow}" fill="none" stroke="#0E8C98" stroke-width="12" stroke-linecap="round" marker-end="url(#arrow)"/>
  <line id="traction" x1="996" y1="930" x2="1004" y2="1170" stroke="#0E8C98" stroke-width="12" stroke-linecap="round" marker-end="url(#arrow)"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #C9D3DC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
