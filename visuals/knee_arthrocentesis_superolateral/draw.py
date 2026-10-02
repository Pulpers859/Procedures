"""Knee arthrocentesis - the superolateral approach (layout).

The right knee and lower thigh from the front, patient supine, knee nearly
straight: the thigh at the top, the shin off the bottom edge, the patient's
right on the image left, so lateral is left and medial is right (house
laterality).

Record: 1 cm superior and 1 cm lateral to the superolateral pole of the
patella; direct the needle medially beneath the patella into the
suprapatellar recess.

Standard adult anatomy added: the patella (about 4.4 x 5 cm), the quadriceps
tendon running up from it, the vastus medialis bulge above and medial to it,
the vastus lateralis along the outer thigh, the patellar tendon below. The
suprapatellar recess is drawn as the pouch about 5 cm deep above the patella
under the quadriceps tendon.

Code-drawn markings: the teal 7 mm insertion zone, the 1 cm lateral + 1 cm
superior dimension from the superolateral pole, the dashed outline of the recess and the needle
direction arrow, medially under the patella.

Millimetres from the patella's centre (x medial = image right, y distal =
image down) at 9.5 px/mm. Adult proportions.

Run: python3 visuals/knee_arthrocentesis_superolateral/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, ellipse_point, fmt, smooth_path  # noqa: E402

ASSET_ID = "knee_arthrocentesis_superolateral"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 9.5
ORIGIN = (820.0, 850.0)            # canvas of the patella's centre


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Leg outline: thigh above, knee, upper shin below.
LATERAL = [(-63, -110), (-62, -80), (-60, -50), (-57, -20), (-54, 0), (-50, 25), (-47, 50), (-46, 70)]
MEDIAL = [(54, 70), (55, 50), (58, 25), (62, 0), (68, -25), (73, -50), (75, -80), (75, -110)]
PATELLA = ((0.0, 0.0), 22.0, 25.0)
QUAD_TENDON = [(-14, -20), (-16, -60), (-18, -100), (18, -100), (16, -60), (14, -20)]
VMO = [(16, -22), (30, -26), (44, -40), (54, -62), (58, -90), (36, -96), (22, -70), (18, -44)]
VASTUS_LAT = [(-30, -110), (-26, -60), (-28, -34), (-42, -38), (-54, -60), (-58, -110)]
PATELLAR_TENDON = [(-8, 23), (8, 23), (7, 60), (-7, 60)]
POLE = ellipse_point((0.0, 0.0), 22.0, 25.0, 225.0)   # superolateral pole
TARGET = (POLE[0] - 10.0, POLE[1] - 10.0)             # 1 cm superior, 1 cm lateral
TARGET_R = 3.5                                        # a 7 mm zone
RECESS = [(-20, -21), (-23, -44), (-18, -66), (0, -76), (18, -66), (23, -44), (20, -21), (0, -25)]
ARROW_END = (-2.0, -14.0)                             # under the patella's upper half

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.5" stop-color="#EDC7AE"/>
  <stop offset="1" stop-color="#DDAE92"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<marker id="arrowhead" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 Z" fill="#0E8C98"/></marker>
"""


def build() -> str:
    t = c(TARGET)
    pole = c(POLE)
    corner = c((TARGET[0], POLE[1]))
    r = TARGET_R * PX_MM
    labels = [
        Label(["Insertion site"], anchor=(60, 430), leader=[(320, 452), (t[0] - r, t[1])], target_id="target", emphasis=True),
        Label(["1 cm superior"], anchor=(corner[0] - 44, corner[1] - 6), leader=[(corner[0] - 38, corner[1] - 28), (corner[0] - 2, corner[1] - 30)],
              target_id="dim-superior", align="end"),
        Label(["1 cm lateral"], anchor=(300, corner[1] + 170), leader=[(560, corner[1] + 124), ((corner[0] + pole[0]) / 2, corner[1] + 3)],
              target_id="dim-lateral"),
        Label(["Patella"], anchor=(1190, 1010), leader=[(1196, 968), c((14, 8))], target_id="patella"),
        Label(["Suprapatellar", "recess"], anchor=(1190, 100), leader=[(1220, 188), c((14, -60))], target_id="recess"),
    ]
    a0 = c(TARGET)
    a1 = c(ARROW_END)
    dx, dy = a1[0] - a0[0], a1[1] - a0[1]
    n = (dx * dx + dy * dy) ** 0.5
    a0 = (a0[0] + dx / n * (r + 8), a0[1] + dy / n * (r + 8))
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
  <path id="vastus-lateralis" d="{path(VASTUS_LAT, closed=True, tension=0.6)}" fill="#E4B89D"/>
  <path id="vastus-medialis" d="{path(VMO, closed=True, tension=0.6)}" fill="#E9C0A6"/>
  <path id="quadriceps-tendon" d="{path(QUAD_TENDON, closed=True, tension=0.4)}" fill="#EBC6AE"/>
  <path id="patellar-tendon" d="{path(PATELLAR_TENDON, closed=True, tension=0.4)}" fill="#E8C0A6" stroke="#C49478" stroke-width="2"/>
  <ellipse id="patella" cx="{fmt(ORIGIN[0])}" cy="{fmt(ORIGIN[1])}" rx="{fmt(PATELLA[1] * PX_MM)}" ry="{fmt(PATELLA[2] * PX_MM)}" fill="#F0CDB5" stroke="#C49478" stroke-width="3"/>
</g>

<g class="marking">
  <path id="recess" d="{path(RECESS, closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.14" stroke="#0E8C98" stroke-width="4" stroke-dasharray="14 12" stroke-opacity="0.8"/>
  <g id="dimension" stroke="#4A2F7A" stroke-width="4" fill="none">
    <line id="dim-lateral-line" x1="{fmt(pole[0])}" y1="{fmt(pole[1])}" x2="{fmt(corner[0])}" y2="{fmt(corner[1])}"/>
    <line id="dim-superior-line" x1="{fmt(corner[0])}" y1="{fmt(corner[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}"/>
  </g>
  <circle cx="{fmt(pole[0])}" cy="{fmt(pole[1])}" r="7" fill="#4A2F7A"/>
  <rect id="dim-superior" x="{fmt(corner[0] - 8)}" y="{fmt(t[1])}" width="16" height="{fmt(corner[1] - t[1])}" fill="#000" opacity="0"/>
  <rect id="dim-lateral" x="{fmt(corner[0])}" y="{fmt(corner[1] - 8)}" width="{fmt(pole[0] - corner[0])}" height="16" fill="#000" opacity="0"/>
  <line id="needle-direction" x1="{fmt(a0[0])}" y1="{fmt(a0[1])}" x2="{fmt(a1[0])}" y2="{fmt(a1[1])}"
        stroke="#0E8C98" stroke-width="8" stroke-linecap="round" marker-end="url(#arrowhead)"/>
  <circle id="target" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="{fmt(TARGET_R * PX_MM)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="5"/>
  <circle cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="6" fill="#0E8C98"/>
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
