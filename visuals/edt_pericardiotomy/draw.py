"""Resuscitative thoracotomy - the incision and the pericardial opening (torso with a cutaway window).

Owner, 2026-10-04: reuse the approved male torso (the needle decompression
painting) and open a window over the left chest. An adult male supine, from
directly above, head at the top, the patient's right on the image left
(house laterality); the left chest is on the image right.

Record: left anterolateral incision at the 4th-5th intercostal space along
the superior rib margin, from the sternal edge to the table; the pericardium
opened longitudinally and anterior to the phrenic nerve, which runs along
its lateral surface.

Layout (for the paint): the decompression photograph with a flat-colour
window over the left chest, its lower edge on the incision: the left lung
retracted laterally, the pericardium over the heart, its left border from
the 2nd space near the sternum out to the apex at the 5th space near the
midclavicular line (standard anatomy), and the phrenic nerve running down
that lateral border.

Code-drawn over the painting: the rib cage as translucent outlined bones
(the decompression plate's fitted geometry, imported), left out inside the
window; the incision along the
5th intercostal space on the upper edge of the 6th rib, from the left
sternal edge to the lateral chest wall; the pericardiotomy as a dashed
longitudinal line from the apex toward the great vessels, about 2 cm
anterior (medial in this view) to the phrenic nerve.

Known limit: the torso's arms are at the sides (the record raises the left
arm); the incision runs to the edge of the visible chest wall.

Millimetres from the sternal notch (x toward the patient's right = image
left, y down), mapped onto the painting with the decompression plate's fit.

Run: python3 visuals/edt_pericardiotomy/draw.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

TORSO_DIR = Path(__file__).resolve().parents[1] / "needle_decompression_landmarks"
_spec = importlib.util.spec_from_file_location("torso_fit", TORSO_DIR / "draw.py")
torso = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(torso)
c, rib_cage = torso.c, torso.rib_cage

ASSET_ID = "edt_pericardiotomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
TORSO_PHOTO = "../needle_decompression_landmarks/base.jpg"

INCISION = [(-18, 133), (-45, 139), (-70, 143), (-90, 137), (-109, 129), (-130, 123), (-148, 119)]
WINDOW = [(-17, 34), (-50, 28), (-88, 42), (-108, 74), (-112, 108), (-108, 127), (-90, 134), (-70, 140),
          (-45, 136), (-17, 130)]
PERICARDIUM = [(-17, 36), (-30, 37), (-48, 52), (-66, 82), (-82, 112), (-92, 140), (-80, 160), (-17, 160)]
PHRENIC = [(-33, 36), (-48, 57), (-64, 87), (-78, 115), (-86, 140)]
PERICARDIOTOMY = [(-66, 126), (-34, 60)]


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def build() -> str:
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    scale = 1600 / BASE_SIZE[0]
    photo_y = (1200 - BASE_SIZE[1] * scale) / 2
    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt(photo_y)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if debug else 0}"'
    else:
        base_attr = base_image = layout_attr = ""

    p0, p1 = c(PERICARDIOTOMY[0]), c(PERICARDIOTOMY[1])
    labels = [
        Label(["Incision, 4th–5th ICS"], anchor=(860, 1080), leader=[(1000, 1030), c((-100, 133))], target_id="incision",
              emphasis=True),
        Label(["Phrenic nerve"], anchor=(1190, 330), leader=[(1270, 350), c((-64, 87))], target_id="phrenic"),
        Label(["Pericardiotomy"], anchor=(330, 560), leader=[(700, 580), c((-50, 93))], target_id="pericardiotomy",
              emphasis=True),
        Label(["Pericardium"], anchor=(330, 1000), leader=[(640, 960), c((-30, 115))], target_id="pericardium"),
    ]
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <image href="{TORSO_PHOTO}" x="0" y="{fmt(photo_y)}" width="1600" height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>
  <clipPath id="window-clip"><path d="{path(WINDOW, closed=True, tension=0.5)}"/></clipPath>
  <path id="lung" d="{path(WINDOW, closed=True, tension=0.5)}" fill="#D7A3A6" stroke="#A9765F" stroke-width="4"/>
  <g clip-path="url(#window-clip)">
    <path id="pericardium" d="{path(PERICARDIUM, closed=True, tension=0.5)}" fill="#E6D3C2" stroke="#B9A08A" stroke-width="4"/>
    <path id="phrenic" d="{path(PHRENIC, tension=0.8)}" fill="none" stroke="#E9C44E" stroke-width="9" stroke-linecap="round"/>
  </g>
  <path id="window" d="{path(WINDOW, closed=True, tension=0.5)}" fill="none" stroke="#A9765F" stroke-width="5"/>
</g>

<mask id="outside-window" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200"><rect width="1600" height="1200" fill="#fff"/>
  <path d="{path(WINDOW, closed=True, tension=0.5)}" fill="#000"/></mask>
<g class="marking">
  <g id="rib-cage" mask="url(#outside-window)">{rib_cage()}</g>
  <path id="incision" d="{path(INCISION, tension=0.7)}" fill="none" stroke="#B3261E" stroke-width="9" stroke-linecap="round"/>
  <line id="pericardiotomy" x1="{fmt(p0[0])}" y1="{fmt(p0[1])}" x2="{fmt(p1[0])}" y2="{fmt(p1[1])}" stroke="#0E8C98" stroke-width="8"
        stroke-dasharray="22 12" stroke-linecap="round"/>
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
