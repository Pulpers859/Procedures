"""Mental nerve block - the right face skull from the front (layout).

Front view of the skull, head at the top, the patient's right on the image
left (house laterality; the record names no side): the right orbit and the
nasal aperture above, both dental arches, and the mandible to the chin. The
upper half reuses the approved infraorbital_anatomy layout's geometry
(commit 10a790a) in the same frame of reference; the painting is asked to
match that plate's approved rendering.

Record: the mental foramen lies on the anterior mandible, below the first or
second premolar, in line with the pupil, the supraorbital notch and the
infraorbital foramen. Intraoral approach: needle into the mucobuccal fold
below the first/second premolar, directed inferiorly toward the foramen,
stopping before bone or the foramen.

Standard adult anatomy added: the mental foramen midway between the
alveolar crest and the lower border of the mandible; the mental nerve's
branches to the lower lip and chin (code-drawn).

Code-drawn markings: the pupil line through the three foramina, the mental
nerve branches, the needle from the fold toward the foramen, stopping short.

Millimetres from the midline (x toward the patient's left = image right) and
the inferior orbital rim's level (y down) at 8 px/mm.

Run: python3 visuals/mental_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "mental_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 8.0
ORIGIN = (1010.0, 380.0)           # canvas of the midline at the inferior rim's level


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def mirror(pts):
    return [(-x, y) for x, y in pts]


PUPIL_X = -32.0
SUPRAORBITAL = (-31.2, -40.4)
INFRAORBITAL = (-31.0, 9.0)
MENTAL = (-30.0, 72.0)
ORBIT = [(-14, -14), (-16, -6), (-22, -1.2), (-32, 0.4), (-42, -1.6), (-49, -7), (-52, -16), (-51, -26), (-46, -34),
         (-36, -39), (-24, -39.4), (-16, -34), (-13, -24)]
NASAL = [(0, -4), (-5, -2), (-10, 6), (-12.6, 16), (-11.6, 24), (-6, 28), (0, 28.6)]
CRANIUM = [(-76, -50), (76, -50), (76, 14), (68, 30), (58, 40), (-58, 40), (-68, 30), (-76, 14)]
MANDIBLE = [(-61, 6), (-61, 30), (-58, 52), (-52, 68), (-42, 79), (-27, 85.5), (-12, 88.4), (0, 89)]
MANDIBLE_TOP = [(0, 59), (-30, 58.6), (-46, 57), (-50, 44), (-53, 6)]
UPPER_TEETH = [(-4.4, 4.2), (-12.6, 3.6), (-19.6, 3.6), (-26.0, 3.4), (-32.0, 3.4), (-38.6, 4.6), (-46.0, 4.4)]
LOWER_TEETH = [(-3.0, 2.8), (-8.8, 3.0), (-15.0, 3.2), (-21.6, 3.3), (-28.2, 3.3), (-36.0, 4.4), (-45.0, 4.4)]
GUM_U, OCCLUSAL, GUM_L = 40.0, 50.0, 60.0
PM1_L, PM2_L = -21.6, -28.2
FOLD_Y = 64.0
ENTRY = (-26.5, FOLD_Y)            # the fold below the first/second premolars
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(MENTAL[0] - ENTRY[0], MENTAL[1] - ENTRY[1])
STOP_MM = 2.6                      # stop short of the foramen
TIP = (MENTAL[0] - U[0] * STOP_MM, MENTAL[1] - U[1] * STOP_MM)
HUB = (ENTRY[0] - U[0] * 9.0, ENTRY[1] - U[1] * 9.0)
BRANCHES = [
    [MENTAL, (-27.0, 69.0), (-22.0, 66.6), (-15.0, 66.0)],
    [MENTAL, (-26.6, 72.4), (-20.0, 74.0), (-12.0, 76.6)],
    [MENTAL, (-28.6, 76.0), (-25.0, 81.0), (-19.0, 85.0)],
]

DEFS = """
<linearGradient id="bone" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EFE3C8"/><stop offset="1" stop-color="#DCCBA6"/></linearGradient>
"""


def foramen(el_id, p, rx, ry):
    q = c(p)
    return (f'<ellipse id="{el_id}" cx="{fmt(q[0])}" cy="{fmt(q[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'fill="#3E2F25" stroke="#8C7A5E" stroke-width="3"/>')


def teeth(row, top, bottom, el):
    out = []
    for side in (1, -1):
        for x, w in row:
            x = x * side
            tid = ""
            if side == 1 and el and abs(x - PM2_L) < 0.01:
                tid = ' id="second-premolar"'
            a, b = c((x - w, top)), c((x + w, bottom))
            out.append(f'<rect{tid} x="{fmt(a[0])}" y="{fmt(a[1])}" width="{fmt(b[0] - a[0])}" height="{fmt(b[1] - a[1])}" '
                       f'rx="{fmt(1.0 * PX_MM)}" fill="#F6F1E4" stroke="#B9AE95" stroke-width="2"/>')
    return "".join(out)


def build() -> str:
    e, t, h = c(ENTRY), c(TIP), c(HUB)
    mx, my = c(MENTAL)
    ix, iy = c(INFRAORBITAL)
    sx, sy = c(SUPRAORBITAL)
    labels = [
        Label(["Supraorbital", "notch"], anchor=(40, 90), leader=[(250, 170), (sx - 10, sy)], target_id="supraorbital"),
        Label(["Infraorbital", "foramen"], anchor=(40, 380), leader=[(250, 410), (ix - 12, iy)], target_id="infraorbital"),
        Label(["Mental", "foramen"], anchor=(40, 900), leader=[(250, 930), (mx - 14, my)], target_id="mental", emphasis=True),
        Label(["Second premolar"], anchor=(1060, 1150), leader=[(1060, 1100), c((PM2_L + 1.0, GUM_L - 3.0))], target_id="second-premolar"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="#F4F1EA"/>
  <path id="mandible" d="{path(MANDIBLE + list(reversed(mirror(MANDIBLE)))[1:] + mirror(list(reversed(MANDIBLE_TOP)))[1:] + MANDIBLE_TOP[1:], closed=True, tension=0.4)}" fill="url(#bone)" stroke="#A8977A" stroke-width="4"/>
  <path id="cranium" d="{path(CRANIUM, closed=True, tension=0.3)}" fill="url(#bone)" stroke="#A8977A" stroke-width="3"/>
  <path id="orbit" d="{path(ORBIT, closed=True, tension=0.7)}" fill="#4B3B2E" stroke="#A8977A" stroke-width="5"/>
  <path d="{path(mirror(ORBIT), closed=True, tension=0.7)}" fill="#4B3B2E" stroke="#A8977A" stroke-width="5"/>
  <path id="nasal-aperture" d="{path(NASAL + mirror(list(reversed(NASAL)))[1:-1], closed=True, tension=0.7)}" fill="#3E2F25" stroke="#A8977A" stroke-width="5"/>
  {foramen("supraorbital", SUPRAORBITAL, 1.8, 1.4)}
  {foramen("infraorbital", INFRAORBITAL, 2.2, 2.8)}
  {foramen("mental", MENTAL, 2.2, 1.8)}
  <g id="upper-teeth">{teeth(UPPER_TEETH, GUM_U, OCCLUSAL, False)}</g>
  <g id="lower-teeth">{teeth(LOWER_TEETH, OCCLUSAL, GUM_L, True)}</g>
</g>

<g class="marking">
  <line id="pupil-line" x1="{fmt(c((PUPIL_X, 0))[0])}" y1="0" x2="{fmt(c((PUPIL_X, 0))[0])}" y2="1200" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.75"/>
  {"".join(f'<path d="{path(b, tension=0.8)}" fill="none" stroke="#E8C547" stroke-width="6" stroke-linecap="round"/>' for b in BRANCHES)}
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(h[0] - U[0] * 40)}" y2="{fmt(h[1] - U[1] * 40)}" stroke="#E7EEF3" stroke-width="18" stroke-linecap="round"/>
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="7"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="3"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="8" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="3" fill="#000" opacity="0"/>
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
