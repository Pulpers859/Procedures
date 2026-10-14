"""Supraorbital nerve block - the right upper face of the skull from the front (layout).

Front view of the skull, head at the top, the patient's right on the image
left (house laterality; the record names no side), zoomed on the right
superior orbital rim: the lower forehead, both orbits' upper halves and the
nasal bones. Same style and frame as the approved infraorbital skull plate
(commit 10a790a), drawn from scratch for this level.

Record: the supraorbital notch lies on the superior orbital rim in line with
the pupil; the supratrochlear nerve exits slightly medial to it. Inject 2 mL
subcutaneously over the notch, staying in the subcutaneous plane at the rim
(do not seek or enter the notch), then advance medially in the same plane
toward the bridge of the nose for the supratrochlear nerve; never direct the
needle into the orbit.

Standard adult anatomy added: the supratrochlear notch about 12 mm medial to
the supraorbital notch; the supraorbital nerve dividing into medial and
lateral branches and the supratrochlear nerve running up the forehead. The
nerves, needle, syringe and pupil line are code-drawn over the painting.

Millimetres from the superior orbital rim's level on the midline (x toward
the patient's left = image right, y down; the right pupil line is x = -32)
at 16 px/mm.

Run: python3 visuals/supraorbital_anatomy/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "supraorbital_anatomy"
PX_MM = 16.0
ORIGIN = (1120.0, 640.0)          # canvas of x = 0 (midline), y = 0 (superior rim level)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


PUPIL_X = -32.0
NOTCH = (-31.0, 0.6)
NOTCH_R = (1.8, 1.3)
SUPRATROCHLEAR = (-19.0, 1.6)
TROCHLEAR_R = (1.2, 0.9)
# Right orbit opening: the superior rim arches, highest near its middle.
ORBIT = [(-12.5, 10), (-15.5, 4.0), (-21, 1.6), (-31, 0.6), (-41, 1.4), (-49, 4.6), (-54, 11), (-56, 20),
         (-55, 34), (-12, 34)]
ORBIT_L = [(-x, y) for x, y in ORBIT]
NASAL = [(-5.5, 8), (-6.5, 20), (-8.5, 34), (8.5, 34), (6.5, 20), (5.5, 8), (0, 5.5)]
SKULL = [(-75, -60), (-75, 60), (35, 60), (35, -60)]
ENTRY = (-42.0, -12.0)                  # just above the eyebrow, lateral to the notch
TIP = (-31.0, -4.6)                     # subcutaneous over the notch, short of the rim
REDIRECT_TIP = (-19.0, -5.0)            # same plane, medially to the supratrochlear point
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(TIP[0] - ENTRY[0], TIP[1] - ENTRY[1])
HUB = (ENTRY[0] - U[0] * 12.0, ENTRY[1] - U[1] * 12.0)
BARREL_END = (HUB[0] - U[0] * 40.0, HUB[1] - U[1] * 40.0)
NERVES = {
    "supraorbital-medial": [NOTCH, (-30.4, -6), (-28.6, -18), (-26.6, -40)],
    "supraorbital-lateral": [NOTCH, (-32.4, -6), (-36.0, -18), (-40.6, -40)],
    "supratrochlear": [SUPRATROCHLEAR, (-18.6, -6), (-17.4, -20), (-16.4, -40)],
}

DEFS = """
<linearGradient id="bone" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EFE3C8"/><stop offset="1" stop-color="#DCCBA6"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def build() -> str:
    e, t, r, h, b0 = c(ENTRY), c(TIP), c(REDIRECT_TIP), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 3.4 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]
    n, s = c(NOTCH), c(SUPRATROCHLEAR)
    labels = [
        Label(["Supraorbital", "notch"], anchor=(40, 900), leader=[(260, 860), (n[0] - 6, n[1] + 4)],
              target_id="notch", emphasis=True),
        Label(["Supratrochlear", "nerve"], anchor=(1110, 150), leader=[(1120, 190), c(NERVES["supratrochlear"][2])],
              target_id="supratrochlear"),
        Label(["Orbit"], anchor=(560, 1150), leader=[(640, 1100), c((-36, 22))], target_id="orbit"),
    ]
    nerves = "".join(
        f'<path{" id=" + chr(34) + k + chr(34) if k == "supratrochlear" else ""} d="{path(pts, tension=0.8)}" '
        f'fill="none" stroke="#E8C547" stroke-width="{7 if k == "supratrochlear" else 6}" stroke-linecap="round"/>'
        for k, pts in NERVES.items())
    body = f"""
<g id="anatomy">
  <path id="skull" d="{path(SKULL, closed=True, tension=0.1)}" fill="url(#bone)"/>
  <path id="orbit" d="{path(ORBIT, closed=True, tension=0.7)}" fill="#4B3B2E" stroke="#A8977A" stroke-width="5"/>
  <path d="{path(ORBIT_L, closed=True, tension=0.7)}" fill="#4B3B2E" stroke="#A8977A" stroke-width="5"/>
  <path id="nasal-bones" d="{path(NASAL, closed=True, tension=0.6)}" fill="#E6D7B6" stroke="#B9A884" stroke-width="3"/>
  <ellipse id="notch" cx="{fmt(n[0])}" cy="{fmt(n[1])}" rx="{fmt(NOTCH_R[0] * PX_MM)}" ry="{fmt(NOTCH_R[1] * PX_MM)}" fill="#3E2F25" stroke="#8C7A5E" stroke-width="3"/>
  <ellipse id="trochlear-notch" cx="{fmt(s[0])}" cy="{fmt(s[1])}" rx="{fmt(TROCHLEAR_R[0] * PX_MM)}" ry="{fmt(TROCHLEAR_R[1] * PX_MM)}" fill="#5A4636" stroke="#8C7A5E" stroke-width="2"/>
</g>

<g class="marking">
  <line id="pupil-line" x1="{fmt(c((PUPIL_X, 0))[0])}" y1="{fmt(n[1])}" x2="{fmt(c((PUPIL_X, 0))[0])}" y2="1200" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.7"/>
  {nerves}
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="url(#barrel)" stroke="#7D868F" stroke-width="3"/>
  <line id="redirect" x1="{fmt(e[0])}" y1="{fmt(e[1])}" x2="{fmt(r[0])}" y2="{fmt(r[1])}" stroke="#5E6670" stroke-width="6" stroke-dasharray="16 12" opacity="0.85"/>
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="7"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="3"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="5" fill="#5E6670"/>
  <circle id="redirect-tip" cx="{fmt(r[0])}" cy="{fmt(r[1])}" r="5" fill="#5E6670" opacity="0.85"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
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
