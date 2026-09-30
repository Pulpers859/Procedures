"""Dialysis catheter tip position - anterior view of the neck and upper chest.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of the code-drawn layout (git history of this file, and
provenance.json), in the radiograph convention: head at the top, the patient's
right on the image left. The SVC runs down the right sternal border and meets
the right atrium beside the sternum.

Markings, drawn here so the path and tip are exact: the catheter from the right
IJ puncture (red dot) down the IJ and SVC to a tip at the cavoatrial junction,
not in the atrium, and the teal tip ring. Its in-body length is checked at true
scale (the layout's 5 px/mm canvas scale carries over; the painted veins and
junction sit on the layout's) against the record's right IJ depth of 12-15 cm.

Regions are hand-traced over the base in base-image pixels (DEBUG=1 shows
them). Re-trace everything if the base is replaced.

Run: python3 visuals/vascath_tip_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, pts, smooth_path  # noqa: E402

ASSET_ID = "vascath_tip_position"
BASE = "base.jpg"
BASE_SIZE = (1195.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2


def canvas(p):
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels: (centreline, painted width) for vessels.
RIGHT_IJ = ([(470, 40), (488, 200), (500, 285)], 40)
LEFT_IJ = ([(735, 40), (725, 200), (700, 285)], 40)
SVC = ([(515, 340), (522, 420), (526, 540), (525, 632)], 40)
AORTA = ([(700, 350), (745, 420), (760, 520)], 50)
RIGHT_ATRIUM = [(455, 655), (520, 645), (560, 662), (562, 890), (455, 890), (440, 760)]
STERNUM = [(540, 312), (672, 312), (655, 440), (590, 760), (560, 760), (560, 440)]
CAJ = (525.0, 640.0)
PUNCTURE = (486.0, 170.0)
CATHETER = [PUNCTURE, (490, 224), (500, 285), (515, 340), (522, 420), (526, 540), CAJ]


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    fill_region = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'
    stroke_region = 'stroke="#ff00ff" stroke-opacity="0.45"' if debug else 'stroke="#000" stroke-opacity="0"'
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()

    def poly(points):
        return pts([canvas(p) for p in points])

    def traced(element_id, structure):
        points, width = structure
        return (f'<path id="{element_id}" d="{smooth_path([canvas(p) for p in points])}" fill="none" '
                f'stroke-width="{fmt(width * SCALE)}" stroke-linecap="round" {stroke_region}/>')

    cath = smooth_path([canvas(p) for p in CATHETER])
    caj, puncture = canvas(CAJ), canvas(PUNCTURE)

    labels = [
        Label(["Superior", "vena cava"], anchor=(40, 640), leader=[(300, 652), canvas((512, 500))], target_id="svc"),
        Label(["Cavoatrial", "junction"], anchor=(40, 360), leader=[(390, 372), (560, 700), caj],
              target_id="cavoatrial-junction", emphasis=True),
        Label(["Right atrium"], anchor=(40, 1120), leader=[(390, 1110), canvas((490, 770))], target_id="right-atrium"),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  {traced("right-ij", RIGHT_IJ)}
  {traced("left-ij", LEFT_IJ)}
  {traced("svc", SVC)}
  {traced("aorta", AORTA)}
  <polygon id="right-atrium" points="{poly(RIGHT_ATRIUM)}" {fill_region}/>
  <polygon id="sternum" points="{poly(STERNUM)}" {fill_region}/>
  <circle id="cavoatrial-junction" cx="{fmt(caj[0])}" cy="{fmt(caj[1])}" r="{fmt(12 * SCALE)}" {fill_region}/>

  <g class="marking">
    <path id="catheter" d="{cath}" fill="none" stroke="#6E7780" stroke-width="15" stroke-linecap="round" opacity="0.9"/>
    <path d="{cath}" fill="none" stroke="#F4F6F6" stroke-width="10" stroke-linecap="round"/>
    <path d="{cath}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.9" transform="translate(-2 0)"/>
    <circle id="catheter-tip" cx="{fmt(caj[0])}" cy="{fmt(caj[1])}" r="26" fill="none" stroke="#0E8C98" stroke-width="6"/>
    <circle cx="{fmt(puncture[0])}" cy="{fmt(puncture[1])}" r="10" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  </g>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
