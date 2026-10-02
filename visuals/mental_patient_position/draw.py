"""Mental nerve block - needle entry on the patient (layout).

The face from the front, head at the top, the patient's right on the image
left (house laterality). The face, eyes, brows and nose reuse the approved
infraorbital_patient_position layout (same frame of reference); its
approved painting is attached to the repaint for the same patient, glove
and light. Here the operator's gloved thumb comes up from below and pulls
the lower lip down, everting it and opening the lower mucobuccal fold below
the premolars on the patient's right.

Record: supine or seated; retract the lower lip to expose the mucobuccal
fold; needle into the fold below the first/second premolar, directed
inferiorly toward the foramen; stop before bone or the foramen.

Code-drawn markings: the syringe and needle (the shared true-size syringe,
foreshortened to 45% along its axis because it points toward the camera),
the entry point, the pupil line and the foramen ring.

Millimetres from the inferior orbital rim's level on the midline (x toward
the patient's left = image right, y down) at 10 px/mm.

Run: python3 visuals/mental_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import SYRINGE_DEFS, Label, document, fmt, smooth_path, syringe  # noqa: E402

ASSET_ID = "mental_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 10.0
ORIGIN = (1060.0, 330.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def oval(center, rx, ry, n=40):
    return [(center[0] + rx * math.cos(2 * math.pi * k / n), center[1] + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


PUPIL_X = -32.0
FORAMEN = (-29.5, 69.0)                 # mental foramen, below the premolars toward the pupil line
FACE = [(-62, -70), (-70, -10), (-70, 14), (-66, 36), (-58, 58), (-46, 74), (-22, 86), (0, 88), (22, 86), (46, 74),
        (58, 58), (66, 36), (70, 14), (70, -10), (62, -70)]
EYE_R = [(-47, -10), (-40, -15), (-32, -16.5), (-24, -15), (-18, -10.6), (-24, -7.4), (-32, -6.4), (-40, -7.2)]
BROW_R = [(-50, -24), (-40, -28.5), (-28, -28.5), (-17, -25), (-18, -23), (-29, -26), (-40, -26), (-49, -22)]
NOSE = [(-7, -26), (-8, 4), (-12, 12), (-17, 18), (-16, 24), (-9, 26.4), (0, 25), (9, 26.4), (16, 24), (17, 18),
        (12, 12), (8, 4), (7, -26)]
UPPER_LIP = [(-25, 40.6), (-16, 34.0), (-6, 33.0), (0, 34.4), (6, 33.0), (16, 34.0), (25, 40.6), (12, 41.6), (0, 42.0),
             (-12, 41.6)]
MOUTH = [(-25, 40.6), (-12, 41.6), (0, 42.0), (12, 41.6), (25, 40.6), (20, 50), (0, 51), (-20, 50)]
TEETH = [(-22.6, 2.3), (-17.8, 2.4), (-12.8, 2.5), (-7.6, 2.6), (-2.6, 2.5), (2.6, 2.5), (7.6, 2.6), (12.8, 2.5),
         (17.8, 2.4), (22.6, 2.3)]
TEETH_TOP, TEETH_BOTTOM = 42.0, 49.0
PM2 = (-22.6, 45.5)
GUM = [(-26, 48.4), (-14, 48.8), (0, 49.2), (14, 48.8), (26, 48.4), (26, 53.6), (0, 54.0), (-26, 53.6)]
VESTIBULE = [(-28, 53.4), (-14, 53.8), (0, 54.0), (14, 53.8), (24, 53.4), (14, 57.4), (0, 57.8), (-14, 57.6), (-27, 57.0)]
LOWER_LIP = [(-29, 52.6), (-14, 57.4), (0, 57.8), (14, 57.4), (27, 52.6), (24, 64), (12, 69), (0, 70), (-12, 69),
             (-26, 64)]
LIP_MUCOSA = [(-27, 57.0), (-14, 57.6), (0, 57.8), (14, 57.4), (24, 56.6), (20, 63), (0, 65.2), (-20, 63)]
FOLD = (-21.0, 55.6)                    # mucobuccal fold below the first/second premolars
ENTRY = FOLD
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(FORAMEN[0] - ENTRY[0], FORAMEN[1] - ENTRY[1])
FORESHORTEN = 0.45                      # the syringe points toward the camera
HUB = (ENTRY[0] - U[0] * 14.0 * FORESHORTEN, ENTRY[1] - U[1] * 14.0 * FORESHORTEN)
BARREL_END = (HUB[0] - U[0] * 60.0 * FORESHORTEN, HUB[1] - U[1] * 60.0 * FORESHORTEN)
# The operator's gloved thumb, up from below the chin, pulling the lower lip down.
THUMB = [(-26, 120), (-22, 96), (-15, 78), (-10, 69.6), (-3, 67.4), (3, 69.2), (3.6, 76), (-1, 96), (-4, 120)]
INDEX = [(-4, 120), (2, 100), (10, 92), (20, 90), (26, 94), (22, 104), (14, 120)]

DEFS = SYRINGE_DEFS + """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9C2A6"/><stop offset="1" stop-color="#DDAE90"/></linearGradient>
<linearGradient id="glove" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F4F7"/><stop offset="1" stop-color="#D5DCE4"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def foreshortened(svg: str) -> str:
    """Shorten the shared syringe along its own axis only (it points toward the camera)."""
    i = svg.index(')">') + 1
    return svg[:i] + f' scale({FORESHORTEN} 1)' + svg[i:]


def build() -> str:
    e, h, b0 = c(ENTRY), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 4.0 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]
    fx, fy = c(FORAMEN)
    teeth = "".join(
        f'<rect{" id=" + chr(34) + "second-premolar" + chr(34) if x == PM2[0] else ""} x="{fmt(c((x - w, 0))[0])}" '
        f'y="{fmt(c((0, TEETH_TOP))[1])}" width="{fmt(2 * w * PX_MM)}" height="{fmt((TEETH_BOTTOM - TEETH_TOP) * PX_MM)}" '
        f'rx="{fmt(0.9 * PX_MM)}" fill="#F6F1E4" stroke="#B9AE95" stroke-width="2"/>' for x, w in TEETH)

    labels = [
        Label(["Mental", "foramen"], anchor=(80, 900), leader=[(300, 930), (fx - 24, fy)], target_id="foramen-mark", emphasis=True),
        Label(["Mucobuccal", "fold"], anchor=(1190, 1000), leader=[(1200, 970), c((14, 55.8))], target_id="vestibule"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="#5C6670"/>
  <path id="face" d="{path(FACE, closed=True, tension=0.6)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="brow" d="{path(BROW_R, closed=True, tension=0.6)}" fill="#6B4E3A"/>
  <path d="{path([(-x, y) for x, y in BROW_R], closed=True, tension=0.6)}" fill="#6B4E3A"/>
  <path id="eye" d="{path(EYE_R, closed=True, tension=0.7)}" fill="#F4F1EC" stroke="#8C6A58" stroke-width="3"/>
  <circle cx="{fmt(c((PUPIL_X, -11.4))[0])}" cy="{fmt(c((PUPIL_X, -11.4))[1])}" r="{fmt(5 * PX_MM)}" fill="#6A4E36"/>
  <circle id="pupil" cx="{fmt(c((PUPIL_X, -11.4))[0])}" cy="{fmt(c((PUPIL_X, -11.4))[1])}" r="{fmt(2 * PX_MM)}" fill="#1E1A18"/>
  <path d="{path([(-x, y) for x, y in EYE_R], closed=True, tension=0.7)}" fill="#F4F1EC" stroke="#8C6A58" stroke-width="3"/>
  <circle cx="{fmt(c((-PUPIL_X, -11.4))[0])}" cy="{fmt(c((-PUPIL_X, -11.4))[1])}" r="{fmt(5 * PX_MM)}" fill="#6A4E36"/>
  <circle cx="{fmt(c((-PUPIL_X, -11.4))[0])}" cy="{fmt(c((-PUPIL_X, -11.4))[1])}" r="{fmt(2 * PX_MM)}" fill="#1E1A18"/>
  <path id="nose" d="{path(NOSE, tension=0.7)}" fill="#E2B193" stroke="#B98A74" stroke-width="3"/>
  <path d="{path(oval((-7.6, 22.6), 3.4, 1.8), closed=True)}" fill="#7A4E3E"/>
  <path d="{path(oval((7.6, 22.6), 3.4, 1.8), closed=True)}" fill="#7A4E3E"/>
  <path id="lower-lip" d="{path(LOWER_LIP, closed=True, tension=0.6)}" fill="#C27A70" stroke="#9E554F" stroke-width="3"/>
  <path id="lip-mucosa" d="{path(LIP_MUCOSA, closed=True, tension=0.6)}" fill="#E07F78" stroke="#C0625C" stroke-width="2"/>
  <path id="mouth" d="{path(MOUTH, closed=True, tension=0.6)}" fill="#5A2626"/>
  <g id="teeth">{teeth}</g>
  <path id="gum" d="{path(GUM, closed=True, tension=0.5)}" fill="#E39A93" stroke="#C47A72" stroke-width="2"/>
  <path id="vestibule" d="{path(VESTIBULE, closed=True, tension=0.6)}" fill="#D9786F" stroke="#B85C55" stroke-width="2"/>
  <path id="upper-lip" d="{path(UPPER_LIP, closed=True, tension=0.6)}" fill="#C47C72" stroke="#9E554F" stroke-width="3"/>
  <path id="index-finger" d="{path(INDEX, closed=True, tension=0.6)}" fill="url(#glove)" stroke="#9AA6B2" stroke-width="3"/>
  <path id="thumb" d="{path(THUMB, closed=True, tension=0.6)}" fill="url(#glove)" stroke="#9AA6B2" stroke-width="3"/>
</g>

<g class="marking">
  <line id="pupil-line" x1="{fmt(c((PUPIL_X, 0))[0])}" y1="{fmt(c((0, -4))[1])}" x2="{fmt(c((PUPIL_X, 0))[0])}" y2="{fmt(fy + 40)}" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.8"/>
  <circle id="foramen-mark" cx="{fmt(fx)}" cy="{fmt(fy)}" r="30" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="10 7"/>
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="#000" opacity="0"/>
  {foreshortened(syringe(h, U, PX_MM, shadow=True))}
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" stroke="#5E6670" stroke-width="6"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" stroke="#D9DEE3" stroke-width="2.5"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #5C6670; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
