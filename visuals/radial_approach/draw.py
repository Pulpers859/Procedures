"""Radial arterial line - volar wrist from above, the operator's view.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of the code-drawn layout (git history of this file, and
provenance.json). Right wrist, palm up, over a rolled towel; forearm left,
hand right, thumb side at the top.

The regions below are hand-traced over the base in base-image pixels
(DEBUG=1 shows them). The target zone and the bracket are drawn here so the
distance is exact: 1-2 cm proximal to the painted wrist crease, over the
radial artery. Scale is carried over from the layout (8 px/mm on the 1600 px
canvas, so about 5.97 px/mm in the 1195 px base); the painted artery, FCR,
styloid and pisiform sit within a few pixels of the layout. Re-trace
everything if the base is replaced.

Run: python3 visuals/radial_approach/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "radial_approach"
BASE = "base.jpg"
BASE_SIZE = (1195.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2
PX_PER_MM = 8.0 / SCALE          # in base pixels

ZONE_NEAR_MM, ZONE_FAR_MM = 10.0, 20.0          # record: 1-2 cm proximal to the wrist crease


def canvas(p):
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels: centrelines, and each structure's painted width.
RADIAL_ARTERY = ([(0, 512), (100, 502), (200, 492), (300, 480), (400, 467), (460, 458), (495, 451)], 15)
FCR = ([(0, 536), (200, 530), (400, 521), (490, 512)], 24)
MEDIAN_NERVE = ([(0, 566), (200, 562), (400, 556), (490, 552)], 18)
CREASE = ([(503, 405), (498, 470), (498, 560), (492, 650), (482, 730)], 6)
CREASE_X_AT_ARTERY = 498.0


def artery_y(x: float) -> float:
    pts_ = RADIAL_ARTERY[0]
    for (x0, y0), (x1, y1) in zip(pts_, pts_[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()
    region = 'stroke="#ff00ff" stroke-opacity="0.5"' if debug else 'stroke="#000" stroke-opacity="0"'

    def traced(element_id, structure):
        points, width = structure
        return (f'<path id="{element_id}" d="{smooth_path([canvas(p) for p in points])}" fill="none" '
                f'stroke-width="{fmt(width * SCALE)}" stroke-linecap="round" {region}/>')

    near_x = CREASE_X_AT_ARTERY - ZONE_NEAR_MM * PX_PER_MM
    far_x = CREASE_X_AT_ARTERY - ZONE_FAR_MM * PX_PER_MM
    mid_x = (near_x + far_x) / 2
    zone_c = canvas((mid_x, artery_y(mid_x)))
    zone_rx = (near_x - far_x) / 2 * SCALE
    crease_c = canvas((CREASE_X_AT_ARTERY, 0))[0]
    far_c = canvas((far_x, 0))[0]
    near_c = canvas((near_x, 0))[0]
    bracket_y = canvas((0, 360))[1]        # on the towel, just above the radial border
    tick = 12

    labels = [
        Label(["Radial artery"], anchor=(40, 140), leader=[(300, 162), canvas((200, 492))],
              target_id="radial-artery", emphasis=True),
        Label(["FCR tendon"], anchor=(40, 1150), leader=[(300, 1100), canvas((200, 530))],
              target_id="fcr-tendon"),
        Label(["Wrist crease"], anchor=(880, 1156), leader=[(900, 1106), canvas((492, 650))],
              target_id="wrist-crease"),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  {traced("radial-artery", RADIAL_ARTERY)}
  {traced("fcr-tendon", FCR)}
  {traced("median-nerve", MEDIAN_NERVE)}
  {traced("wrist-crease", CREASE)}

  <ellipse id="target-zone" class="marking" cx="{fmt(zone_c[0])}" cy="{fmt(zone_c[1])}" rx="{fmt(zone_rx)}" ry="24"
           fill="#0E8C98" fill-opacity="0.3" stroke="#0E8C98" stroke-width="5"/>
  <g class="marking" stroke-linecap="round">
    <line id="crease-guide" x1="{fmt(crease_c)}" y1="{fmt(bracket_y)}" x2="{fmt(crease_c)}" y2="{fmt(zone_c[1] - 30)}" stroke="#1C2530" stroke-width="2" stroke-dasharray="6 7" opacity="0.7"/>
    <line x1="{fmt(far_c)}" y1="{fmt(bracket_y)}" x2="{fmt(far_c)}" y2="{fmt(zone_c[1] - 30)}" stroke="#1C2530" stroke-width="2" stroke-dasharray="6 7" opacity="0.7"/>
    <g stroke="#F6F7F9" stroke-width="9" opacity="0.9">
      <line x1="{fmt(crease_c)}" y1="{fmt(bracket_y)}" x2="{fmt(far_c)}" y2="{fmt(bracket_y)}"/>
    </g>
    <g stroke="#1C2530" stroke-width="3.5">
      <line id="crease-to-zone" x1="{fmt(crease_c)}" y1="{fmt(bracket_y)}" x2="{fmt(far_c)}" y2="{fmt(bracket_y)}"/>
      <line x1="{fmt(crease_c)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(crease_c)}" y2="{fmt(bracket_y + tick)}"/>
      <line x1="{fmt(near_c)}" y1="{fmt(bracket_y - tick / 2)}" x2="{fmt(near_c)}" y2="{fmt(bracket_y + tick / 2)}"/>
      <line x1="{fmt(far_c)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(far_c)}" y2="{fmt(bracket_y + tick)}"/>
    </g>
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
