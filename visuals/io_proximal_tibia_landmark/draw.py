"""Intraosseous access - the proximal tibia insertion site (layout).

The right knee and upper shin from the front, patient supine, leg extended:
the knee at the top, the foot off the bottom edge, the patient's right on
the image left, so lateral is left and medial is right (house laterality).

Record: palpate the tibial tuberosity; move 1-2 cm distal and medial onto
the flat anteromedial tibial surface; needle at 90 degrees to the bone.

Standard adult anatomy added: the patella and its tendon running to the
tuberosity, the tibial crest running down from the tuberosity, the flat
anteromedial surface medial to the crest, the fibular head laterally.

Code-drawn markings: the tuberosity ring, the teal 1 cm target zone 1-2 cm
distal and medial to it, and a 2 cm bracket from the tuberosity.

Millimetres from the tibial tuberosity (x medial = image right, y distal =
image down) at 8 px/mm. Adult proportions.

Run: python3 visuals/io_proximal_tibia_landmark/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "io_proximal_tibia_landmark"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 8.0
ORIGIN = (780.0, 560.0)            # canvas of the tibial tuberosity


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Leg outline: thigh above, knee, shin below.
LATERAL = [(-62, -80), (-60, -50), (-58, -25), (-52, 0), (-46, 30), (-42, 60), (-40, 90)]
MEDIAL = [(62, 90), (60, 60), (58, 30), (62, 0), (68, -25), (70, -50), (70, -80)]
PATELLA = ((4.0, -50.0), 22.0, 25.0)
TENDON = [(-6, -27), (6, -27), (5, -4), (-5, -4)]
TUBEROSITY = ((0.0, 0.0), 6.0, 5.0)
CREST = [(-1, 5), (-3, 30), (-5, 60), (-6, 90)]
FIBULAR_HEAD = ((-44.0, -6.0), 8.0, 7.0)
TARGET = (14.0, 15.0)              # 1.5 cm distal and 1.4 cm medial
TARGET_R = 5.0                     # a 1 cm zone

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.5" stop-color="#EDC7AE"/>
  <stop offset="1" stop-color="#DDAE92"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    t = c(TARGET)
    tub = c(TUBEROSITY[0])
    br0, br1 = c((TARGET[0] + 9, 0)), c((TARGET[0] + 9, 20))
    labels = [
        Label(["Tibial tuberosity"], anchor=(80, 640), leader=[(330, 600), (tub[0] - 44, tub[1])], target_id="tuberosity"),
        Label(["Insertion site"], anchor=(1060, 820), leader=[(1090, 780), (t[0] + TARGET_R * PX_MM, t[1] + 6)],
              target_id="target", emphasis=True),
        Label(["Patella"], anchor=(1060, 200), leader=[(1080, 220), c((24, -50))], target_id="patella"),
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
  <path id="leg" d="{path(LATERAL + MEDIAL, closed=True, tension=0.6)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  {ell("fibular-head", FIBULAR_HEAD, 'fill="#E2B497" stroke="#C49478" stroke-width="3"')}
  {ell("patella", PATELLA, 'fill="#EFCBB3" stroke="#C49478" stroke-width="3"')}
  <path id="patellar-tendon" d="{path(TENDON, closed=True, tension=0.4)}" fill="#E8C0A6" stroke="#C49478" stroke-width="2"/>
  {ell("tuberosity-bump", TUBEROSITY, 'fill="#EFCBB3" stroke="#C49478" stroke-width="3"')}
  <path id="tibial-crest" d="{path(CREST, tension=0.8)}" fill="none" stroke="#C99A80" stroke-width="5"/>
</g>

<g class="marking">
  <circle id="tuberosity" cx="{fmt(tub[0])}" cy="{fmt(tub[1])}" r="44" fill="none" stroke="#4A2F7A" stroke-width="6"/>
  <circle id="target" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="{fmt(TARGET_R * PX_MM)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="5"/>
  <circle cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="6" fill="#0E8C98"/>
  <g id="bracket" stroke="#4A2F7A" stroke-width="4" fill="none">
    <line x1="{fmt(br0[0])}" y1="{fmt(br0[1])}" x2="{fmt(br1[0])}" y2="{fmt(br1[1])}"/>
    <line x1="{fmt(br0[0] - 10)}" y1="{fmt(br0[1])}" x2="{fmt(br0[0] + 10)}" y2="{fmt(br0[1])}"/>
    <line x1="{fmt(br0[0] - 6)}" y1="{fmt(c((0, 10))[1])}" x2="{fmt(br0[0] + 6)}" y2="{fmt(c((0, 10))[1])}"/>
    <line x1="{fmt(br1[0] - 10)}" y1="{fmt(br1[1])}" x2="{fmt(br1[0] + 10)}" y2="{fmt(br1[1])}"/>
  </g>
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
