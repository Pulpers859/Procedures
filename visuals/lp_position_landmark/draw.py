"""Lumbar puncture - interspace landmarks (layout).

The lower back seen from behind, patient in the left lateral decubitus
position, back flexed: the spine runs across the image, the head off the
right edge, the buttocks at the left, the patient's right (upper) flank at
the top and the left flank on the bed at the bottom. The record measures
opening pressure in this position.

Record: Tuffier's line, joining the tops of the iliac crests, crosses at
about the L4 spinous process; the L3-L4 or L4-L5 interspace is the target,
below the conus.

Standard adult anatomy added: lumbar spinous processes about 3.8 cm apart,
the iliac crests reaching their highest point at the flanks, about 14 cm
either side of the spine, the posterior superior iliac spine dimples, the midline furrow
between the erector spinae.

Code-drawn markings: the palpated iliac crests (pen-style lines), Tuffier's line (dashed, perpendicular to the spine
through the crests' highest points), the spinous process dots L2-S1 with L4
ringed, and teal zones at the L3-L4 and L4-L5 interspaces.

Millimetres from the L4 spinous process (x toward the head = image right,
y toward the patient's right/upper side = image up is negative) at 3 px/mm.

Run: python3 visuals/lp_position_landmark/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "lp_position_landmark"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 3.0
ORIGIN = (800.0, 590.0)            # canvas of the L4 spinous process
SEG = 38.0                         # spinous process spacing, mm


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


TOP = [(280, -168), (200, -162), (120, -150), (50, -146), (-20, -158), (-90, -176), (-160, -180), (-230, -170), (-290, -160)]
BOTTOM = [(-290, 160), (-230, 168), (-160, 176), (-90, 170), (-20, 152), (50, 144), (120, 150), (200, 160), (280, 166)]
CREST_UP = [(-72, -36), (-62, -70), (-46, -102), (-24, -128), (-8, -140), (0, -142), (6, -143)]
CREST_DOWN = [(x, -y) for x, y in CREST_UP]
CLEFT = [(-104, 0), (-150, 2), (-200, 4), (-290, 6)]
FURROW = [(-80, 0), (0, 0), (80, 0), (180, 0), (280, 0)]
DIMPLES = [(-76, -30), (-76, 30)]
LEVELS = {"l2": 2, "l3": 1, "l4": 0, "l5": -1, "s1": -2}
GOWN = [(170, -200), (280, -200), (280, 200), (176, 200), (186, 120), (178, 0), (186, -120)]

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2B497"/><stop offset="0.5" stop-color="#EDC7AE"/>
  <stop offset="1" stop-color="#D9A88C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="gown-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A9C3D8"/><stop offset="1" stop-color="#8FAEC7"/></linearGradient>
"""


def build() -> str:
    dots = "".join(
        f'<circle id="{k}" cx="{fmt(c((n * SEG, 0))[0])}" cy="{fmt(c((n * SEG, 0))[1])}" r="{9 if k != "l4" else 11}" '
        f'fill="#4A2F7A" stroke="#F6F7F9" stroke-width="3"/>' for k, n in LEVELS.items())
    l4 = c((0, 0))
    z34, z45 = c((SEG / 2, 0)), c((-SEG / 2, 0))
    top, bot = c((0, -142)), c((0, 142))
    labels = [
        Label(["Iliac crest"], anchor=(250, 120), leader=[(420, 136), c((-46, -102))], target_id="crest-mark-upper"),
        Label(["Tuffier's line"], anchor=(860, 120), leader=[(870, 138), (top[0] + 1, top[1] + 81)], target_id="tuffier"),
        Label(["L4"], anchor=(700, 470), leader=[(740, 486), (l4[0] - 8, l4[1] - 8)], target_id="l4"),
        Label(["L3–L4"], anchor=(1000, 800), leader=[(1010, 760), (z34[0] + 6, z34[1] + 10)], target_id="target-l3l4", emphasis=True),
        Label(["L4–L5"], anchor=(470, 800), leader=[(640, 760), (z45[0] - 6, z45[1] + 10)], target_id="target-l4l5", emphasis=True),
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
  <rect x="0" y="0" width="1600" height="1200" fill="url(#sheet)"/>
  <path id="back" d="{path(TOP + BOTTOM, closed=True, tension=0.5)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="iliac-crest" d="{path(CREST_UP, tension=0.8)}" fill="none" stroke="#C99A80" stroke-width="7"/>
  <path id="iliac-crest-lower" d="{path(CREST_DOWN, tension=0.8)}" fill="none" stroke="#C99A80" stroke-width="7"/>
  <path id="midline-furrow" d="{path(FURROW, tension=0.8)}" fill="none" stroke="#CFA083" stroke-width="5"/>
  <path id="gluteal-cleft" d="{path(CLEFT, tension=0.8)}" fill="none" stroke="#A9765F" stroke-width="6"/>
  {"".join(f'<circle cx="{fmt(c(d)[0])}" cy="{fmt(c(d)[1])}" r="10" fill="#D2A084"/>' for d in DIMPLES)}
  <path id="gown" d="{path(GOWN, closed=True, tension=0.4)}" fill="url(#gown-grad)" stroke="#7896B0" stroke-width="3"/>
</g>

<g class="marking">
  <path id="crest-mark-upper" d="{path(CREST_UP, tension=0.8)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-linecap="round" opacity="0.85"/>
  <path id="crest-mark-lower" d="{path(CREST_DOWN, tension=0.8)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-linecap="round" opacity="0.85"/>
  <line id="tuffier" x1="{fmt(top[0])}" y1="{fmt(top[1])}" x2="{fmt(bot[0])}" y2="{fmt(bot[1])}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="22 14"/>
  <ellipse id="target-l3l4" cx="{fmt(z34[0])}" cy="{fmt(z34[1])}" rx="{fmt(6 * PX_MM)}" ry="{fmt(7 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="5"/>
  <ellipse id="target-l4l5" cx="{fmt(z45[0])}" cy="{fmt(z45[1])}" rx="{fmt(6 * PX_MM)}" ry="{fmt(7 * PX_MM)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="5"/>
  {dots}
  <circle cx="{fmt(l4[0])}" cy="{fmt(l4[1])}" r="26" fill="none" stroke="#4A2F7A" stroke-width="5"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #DDE5EC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
