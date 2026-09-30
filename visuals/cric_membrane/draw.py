"""Cricothyrotomy landmarks - anterior (A-P) view, the operator's view.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of the earlier code-drawn layout (see provenance.json). The anatomy
regions below are hand-traced over the base in base-image pixels; the
incisions, the membrane highlight and the labels are drawn here so they are
exact. Re-trace everything if the base is replaced.

Incisions: the horizontal membrane incision (solid), and the vertical midline
skin incision (dashed = skin layer), 4 cm, beginning over the thyroid cartilage
and running distally - the owner's specification (3-5 cm). Base scale is about
9.5 px/mm (the membrane is about 90 px tall).

Run: python3 visuals/cric_membrane/draw.py   (DEBUG=1 shows the traced regions)
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, pts  # noqa: E402

ASSET_ID = "cric_membrane"
BASE = "base.jpg"
BASE_SIZE = (1195.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2
PX_PER_MM = 9.5            # in base pixels
CX = 597.0                 # midline in base pixels


def canvas(p):
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels.
THYROID = [(402, 140), (600, 180), (790, 140), (770, 250), (720, 330), (600, 352), (478, 330), (425, 250)]
MEMBRANE = [(492, 354), (702, 354), (712, 440), (480, 440)]
CRICOID = [(476, 443), (720, 443), (716, 497), (480, 497)]
RINGS = [(496, 505), (700, 505), (700, 890), (496, 890)]
ISTHMUS = [(520, 565), (675, 565), (700, 640), (680, 690), (515, 690), (495, 640)]

SKIN_INCISION_START_Y = 290.0
SKIN_INCISION_MM = 40.0
MEMBRANE_CUT = ((545.0, 405.0), (650.0, 405.0))


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    region = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()

    def poly(points):
        return pts([canvas(p) for p in points])

    top = canvas((CX, SKIN_INCISION_START_Y))
    bottom = canvas((CX, SKIN_INCISION_START_Y + SKIN_INCISION_MM * PX_PER_MM))
    cut_a, cut_b = canvas(MEMBRANE_CUT[0]), canvas(MEMBRANE_CUT[1])

    labels = [
        Label(["Thyroid", "cartilage"], anchor=(40, 250), leader=[(290, 290), canvas((470, 230))],
              target_id="thyroid-cartilage"),
        Label(["Cricothyroid", "membrane"], anchor=(30, 560), leader=[(400, 548), canvas((505, 400))],
              target_id="cricothyroid-membrane", emphasis=True),
        Label(["Cricoid", "cartilage"], anchor=(1290, 560), leader=[(1280, 590), canvas((705, 470))],
              target_id="cricoid-cartilage"),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  <polygon id="thyroid-cartilage" points="{poly(THYROID)}" {region}/>
  <polygon id="cricothyroid-membrane" points="{poly(MEMBRANE)}" fill="#0E8C98" fill-opacity="{0.35 if debug else 0.22}" stroke="#0E8C98" stroke-width="3" stroke-opacity="0.8"/>
  <polygon id="cricoid-cartilage" points="{poly(CRICOID)}" {region}/>
  <polygon id="tracheal-rings" points="{poly(RINGS)}" {region}/>
  <polygon id="thyroid-isthmus" points="{poly(ISTHMUS)}" {region}/>

  <line id="vertical-skin-incision" x1="{fmt(top[0])}" y1="{fmt(top[1])}" x2="{fmt(bottom[0])}" y2="{fmt(bottom[1])}"
        stroke="#D8432A" stroke-width="7" stroke-dasharray="22 15" stroke-linecap="round" opacity="0.92"/>
  <line id="membrane-incision" x1="{fmt(cut_a[0])}" y1="{fmt(cut_a[1])}" x2="{fmt(cut_b[0])}" y2="{fmt(cut_b[1])}"
        stroke="#D8432A" stroke-width="12" stroke-linecap="round"/>
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
