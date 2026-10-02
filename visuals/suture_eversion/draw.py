"""Laceration repair - the everting interrupted suture (layout).

Two cut-away sections through skin across a laceration, one above the other:
the bite placed with the wound open (top), and the same suture tied (bottom).
Skin surface up; the cut runs into the page.

Record: needle entry angle and bite depth set the edge eversion that gives a
tension-free closure; approximate the edges with everting interrupted
sutures.

Standard technique drawn (not stated in the record): the needle enters at
90 degrees to the skin about 4 mm from the edge, the bite is wider at its
base than at the surface (flask-shaped) and reaches the same depth on both
sides, through the dermis into the top of the fat; tied, the wider base
pushes the edges up into a slight ridge.

Code-drawn markings: the suture (blue monofilament), the right-angle mark at
entry, the knot.

Millimetres from the wound centre (x across the wound, y deep from the
skin) at 40 px/mm. Dermis 2.5 mm.

Run: python3 visuals/suture_eversion/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "suture_eversion"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 40.0
CX = 800.0
SKIN_A, BOTTOM_A = 200.0, 560.0   # canvas y of the skin surface and panel floor, open wound
SKIN_B, BOTTOM_B = 820.0, 1200.0  # tied
DERMIS = 2.5
W = 25.0                           # mm beyond the frame edge


def c(p, y0):
    return (CX + p[0] * PX_MM, y0 + p[1] * PX_MM)


def path(points, y0, closed=False, tension=1.0):
    return smooth_path([c(p, y0) for p in points], closed=closed, tension=tension)


# Open wound: a V through the dermis into the fat.
GAP_TOP, GAP_DEPTH = 1.6, 6.0
LEFT_SKIN_A = [(-W, 0), (-GAP_TOP, 0), (-0.25, GAP_DEPTH), (-W, GAP_DEPTH)]
BITE_A = [(-5.6, -1.6), (-5.6, 0), (-5.9, 1.6), (-7.3, 3.6), (-5.6, 5.1), (0, 5.4), (5.6, 5.1), (7.3, 3.6),
          (5.9, 1.6), (5.6, 0), (5.6, -1.6)]
# Tied: the edges meet and rise into a ridge.
SURFACE_B = [(-W, 0), (-8, 0), (-5, -0.15), (-2.5, -0.55), (-0.8, -0.9), (-0.15, -0.75), (0, -0.55),
             (0.15, -0.75), (0.8, -0.9), (2.5, -0.55), (5, -0.15), (8, 0), (W, 0)]
DERMIS_B = [(W, DERMIS), (8, DERMIS), (4, DERMIS - 0.2), (1.2, DERMIS - 0.55), (0, DERMIS - 0.6),
            (-1.2, DERMIS - 0.55), (-4, DERMIS - 0.2), (-8, DERMIS), (-W, DERMIS)]
LOOP_B = [(4.3, -0.45), (4.3, 0.6), (4.6, 1.8), (5.4, 3.5), (4.0, 4.6), (0, 5.0), (-4.0, 4.6), (-5.4, 3.5),
          (-4.6, 1.8), (-4.3, 0.6), (-4.3, -0.45)]
TOP_B = [(-4.3, -0.45), (-3.0, -1.35), (0, -1.55), (3.0, -1.35), (4.3, -0.45)]

DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def tissue_a() -> str:
    y0 = SKIN_A
    fat = f'<rect id="fat-a" x="0" y="{fmt(y0 + DERMIS * PX_MM)}" width="1600" height="{fmt(BOTTOM_A - y0 - DERMIS * PX_MM)}" fill="url(#fat)"/>'
    dermis = f'<rect id="dermis-a" x="0" y="{fmt(y0)}" width="1600" height="{fmt(DERMIS * PX_MM)}" fill="#E7A79A"/>'
    epi = f'<rect x="0" y="{fmt(y0 - 3)}" width="1600" height="8" fill="#D98F7E"/>'
    gap = (f'<path id="wound" d="M{fmt(c((-GAP_TOP, 0), y0)[0])},{fmt(y0 - 4)} L{fmt(c((GAP_TOP, 0), y0)[0])},{fmt(y0 - 4)} '
           f'L{fmt(c((0.25, GAP_DEPTH), y0)[0])},{fmt(c((0, GAP_DEPTH), y0)[1])} L{fmt(c((-0.25, GAP_DEPTH), y0)[0])},{fmt(c((0, GAP_DEPTH), y0)[1])} Z" '
           f'fill="#F6F4F0"/>')
    return fat + dermis + epi + gap


def tissue_b() -> str:
    y0 = SKIN_B
    skin_top = path(SURFACE_B, y0, tension=0.6)
    body = (f'<path id="fat-b" d="{skin_top} L{fmt(1600)},{fmt(BOTTOM_B)} L0,{fmt(BOTTOM_B)} Z" fill="url(#fat)"/>'
            f'<path id="dermis-b" d="{path(SURFACE_B + DERMIS_B, y0, closed=True, tension=0.6)}" fill="#E7A79A"/>'
            f'<path d="{skin_top}" fill="none" stroke="#D98F7E" stroke-width="8"/>'
            f'<line id="wound-line" x1="{fmt(CX)}" y1="{fmt(c((0, -0.55), y0)[1])}" x2="{fmt(CX)}" y2="{fmt(c((0, 4.0), y0)[1])}" '
            f'stroke="#B0675C" stroke-width="5"/>')
    return body


def build() -> str:
    ya, yb = SKIN_A, SKIN_B
    sq = 34
    e = c((-5.6, 0), ya)
    labels = [
        Label(["90° entry"], anchor=(170, 120), leader=[(420, 140), (e[0] - sq, e[1] - sq / 2)], target_id="entry-angle"),
        Label(["Dermis"], anchor=(1220, 120), leader=[(1250, 140), c((10, 1.2), ya)], target_id="dermis-a"),
        Label(["Wider at depth"], anchor=(1150, 520), leader=[(1160, 476), c((7.3, 3.6), ya)], target_id="bite-a", emphasis=True),
        Label(["Everted edges"], anchor=(1110, 730), leader=[(1120, 748), c((1.0, -0.35), yb)], target_id="dermis-b", emphasis=True),
        Label(["Knot"], anchor=(130, 740), leader=[(270, 756), c((-4.4, -0.7), yb)], target_id="knot"),
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
    sq = 34
    knot = c((-4.4, -0.75), yb)
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <rect x="0" y="0" width="1600" height="1200" fill="#F6F4F0"/>
  {tissue_a()}
  {tissue_b()}
  <rect x="0" y="{fmt(BOTTOM_A)}" width="1600" height="{fmt(SKIN_B - BOTTOM_A - 140)}" fill="#F6F4F0"/>
</g>

<g class="marking">
  <path id="bite-a" d="{path(BITE_A, ya, tension=0.7)}" fill="none" stroke="#2F4FA8" stroke-width="9" stroke-linecap="round"/>
  <path id="entry-angle" d="M{fmt(e[0] - sq)},{fmt(e[1])} L{fmt(e[0] - sq)},{fmt(e[1] - sq)} L{fmt(e[0])},{fmt(e[1] - sq)}" fill="none" stroke="#4A2F7A" stroke-width="5"/>
  <path id="loop-b" d="{path(LOOP_B, yb, tension=0.7)}" fill="none" stroke="#2F4FA8" stroke-width="9" stroke-linecap="round"/>
  <path id="top-b" d="{path(TOP_B, yb, tension=0.8)}" fill="none" stroke="#2F4FA8" stroke-width="9" stroke-linecap="round"/>
  <ellipse id="knot" cx="{fmt(knot[0])}" cy="{fmt(knot[1])}" rx="26" ry="18" fill="#2F4FA8" stroke="#1C2F66" stroke-width="3"/>
  <path d="M{fmt(knot[0] - 10)},{fmt(knot[1] - 12)} l-34,-40 M{fmt(knot[0] - 4)},{fmt(knot[1] - 14)} l-10,-48" stroke="#2F4FA8" stroke-width="7" stroke-linecap="round"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F6F4F0; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
