"""Infraorbital nerve block - the right maxilla from the front (layout).

Front view of the skull, head at the top, the patient's right on the image
left (house laterality; the record names no side), zoomed on the right
midface: the lower orbit, the nasal aperture, the maxilla and the upper
teeth. Composition after the skull plates the owner shared (concept only,
not committed); drawn from scratch.

Record: the infraorbital foramen lies about 1 cm below the inferior orbital
rim, directly below the pupil. Intraoral approach: insert in the mucobuccal
fold above the canine/first premolar, advance toward the finger over the
foramen, roughly 1.5-2 cm, and stop short of the foramen.

Standard adult anatomy added: the canine eminence and premolar roots under
the maxilla, the zygoma lateral to the foramen. The nerve and its branches
(inferior palpebral, nasal, superior labial) are code-drawn over the
painting, as on the auricular plate.

Millimetres from the inferior orbital rim on the pupil line's level
(x toward the patient's left = image right, y down; the right pupil line is
x = -32) at 16 px/mm.

Run: python3 visuals/infraorbital_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import SYRINGE_DEFS, Label, document, fmt, smooth_path, syringe  # noqa: E402

ASSET_ID = "infraorbital_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 16.0
ORIGIN = (800.0 + 22 * 16.0, 22 * 16.0)   # canvas of x = 0 (midline), y = 0 (rim level)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


PUPIL_X = -32.0
FORAMEN = (-31.0, 9.0)                  # ~1 cm below the rim, under the pupil
FORAMEN_R = (2.2, 2.8)
ORBIT = [(-14, -14), (-16, -6), (-22, -1.2), (-32, 0.4), (-42, -1.6), (-49, -7), (-52, -16), (-50, -24), (-14, -24)]
NASAL = [(0, -4), (-5, -2), (-10, 6), (-12.6, 16), (-11.6, 24), (-6, 28), (0, 28.6)]
ZYGOMA_EDGE = [(-52, -10), (-58, 2), (-60, 16), (-56, 26)]
SKULL = [(-70, -24), (-70, 70), (24, 70), (24, -24)]
# Upper teeth crowns along the occlusal line (front view): centre x, half-width.
TEETH = [(-4.4, 4.2), (-12.6, 3.6), (-19.6, 3.6), (-26.0, 3.4), (-32.0, 3.4), (-38.6, 4.6), (-46.0, 4.4)]
TEETH_L = [(4.4, 4.2), (12.6, 3.6), (19.6, 3.6)]
GUM_Y, OCCLUSAL_Y = 40.0, 50.0
CANINE_X, PM1_X, PM2_X = -19.6, -26.0, -32.0
FOLD_Y = 33.0                            # mucobuccal fold level, above the roots' apices
ENTRY = (PM1_X + 1.0, FOLD_Y)            # above the first premolar
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(FORAMEN[0] - ENTRY[0], FORAMEN[1] - ENTRY[1])
DEPTH_MM = 18.0                          # record: roughly 1.5-2 cm, then stop
TIP = (ENTRY[0] + U[0] * DEPTH_MM, ENTRY[1] + U[1] * DEPTH_MM)
HUB = (ENTRY[0] - U[0] * 14.0, ENTRY[1] - U[1] * 14.0)
BARREL_END = (HUB[0] - U[0] * 40.0, HUB[1] - U[1] * 40.0)

# Branches fanning from the foramen (code-drawn on the plate).
BRANCHES = {
    "palpebral": [FORAMEN, (-31.6, 5.0), (-33.0, 1.4), (-35.0, -0.6)],
    "nasal": [FORAMEN, (-26.0, 9.6), (-20.0, 11.6), (-14.6, 15.0)],
    "labial-medial": [FORAMEN, (-27.6, 14.0), (-24.4, 21.0), (-21.6, 29.0)],
    "labial-lateral": [FORAMEN, (-31.6, 15.0), (-31.0, 22.0), (-30.0, 30.0)],
}

DEFS = SYRINGE_DEFS + """
<linearGradient id="bone" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EFE3C8"/><stop offset="1" stop-color="#DCCBA6"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def build() -> str:
    e, t, h, b0 = c(ENTRY), c(TIP), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 3.4 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]
    fx, fy = c(FORAMEN)
    teeth = "".join(
        f'<rect x="{fmt(c((x - w, 0))[0])}" y="{fmt(c((0, GUM_Y))[1])}" width="{fmt(2 * w * PX_MM)}" '
        f'height="{fmt((OCCLUSAL_Y - GUM_Y + (2 if abs(x) < 15 else 0)) * PX_MM)}" rx="{fmt(1.2 * PX_MM)}" '
        f'fill="#F6F1E4" stroke="#B9AE95" stroke-width="3"{" id=" + chr(34) + "first-premolar" + chr(34) if x == PM1_X else ""}/>'
        for x, w in TEETH + TEETH_L)
    roots = "".join(
        f'<path d="{path([(x - 1.6, GUM_Y), (x - 0.8, GUM_Y - (17 if x == CANINE_X else 13)), (x + 0.8, GUM_Y - (17 if x == CANINE_X else 13)), (x + 1.6, GUM_Y)], closed=True, tension=0.6)}" fill="#E4D6B6" stroke="#C8B790" stroke-width="2"/>'
        for x, _ in TEETH[1:6])

    labels = [
        Label(["Infraorbital", "foramen"], anchor=(40, 470), leader=[(250, 500), (fx - 8, fy)],
              target_id="foramen", emphasis=True),
        Label(["Orbital rim"], anchor=(40, 250), leader=[(240, 270), c((-40, -1.0))], target_id="orbit"),
        Label(["First premolar"], anchor=(40, 1150), leader=[(300, 1100), c((PM1_X - 1.0, 47))], target_id="first-premolar"),
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
  <path id="skull" d="{path(SKULL, closed=True, tension=0.1)}" fill="url(#bone)"/>
  <path id="orbit" d="{path(ORBIT, closed=True, tension=0.7)}" fill="#4B3B2E" stroke="#A8977A" stroke-width="5"/>
  <path id="nasal-aperture" d="{path(NASAL + [(-x, y) for x, y in reversed(NASAL)][1:-1], closed=True, tension=0.7)}" fill="#3E2F25" stroke="#A8977A" stroke-width="5"/>
  <path id="canine-eminence" d="{path([(CANINE_X - 2.4, GUM_Y), (CANINE_X - 1.6, GUM_Y - 18), (CANINE_X + 1.6, GUM_Y - 18), (CANINE_X + 2.4, GUM_Y)], closed=True, tension=0.6)}" fill="#E8DBBC" stroke="none"/>
  {roots}
  <ellipse id="foramen" cx="{fmt(fx)}" cy="{fmt(fy)}" rx="{fmt(FORAMEN_R[0] * PX_MM)}" ry="{fmt(FORAMEN_R[1] * PX_MM)}" fill="#3E2F25" stroke="#8C7A5E" stroke-width="3"/>
  <rect id="gum" x="{fmt(c((-70, 0))[0])}" y="{fmt(c((0, GUM_Y - 1.5))[1])}" width="{fmt(94 * PX_MM)}" height="{fmt(3 * PX_MM)}" fill="#D9C7A0"/>
  <g id="teeth">{teeth}</g>
</g>

<g class="marking">
  <g opacity="0.95">
  {"".join(f'<path d="{path(pts, tension=0.8)}" fill="none" stroke="#000" stroke-opacity="0.22" stroke-width="12" stroke-linecap="round" transform="translate(2 3)"/>' for pts in BRANCHES.values())}
  {"".join(f'<path d="{path(pts, tension=0.8)}" fill="none" stroke="#8F7414" stroke-width="10" stroke-linecap="round"/>' for pts in BRANCHES.values())}
  <path id="nerve" d="{path(BRANCHES['labial-medial'], tension=0.8)}" fill="none" stroke="#EFCF55" stroke-width="7" stroke-linecap="round"/>
  {"".join(f'<path d="{path(pts, tension=0.8)}" fill="none" stroke="#EFCF55" stroke-width="7" stroke-linecap="round"/>' for k, pts in BRANCHES.items() if k != 'labial-medial')}
  {"".join(f'<path d="{path(pts, tension=0.8)}" fill="none" stroke="#FFF6C8" stroke-opacity="0.7" stroke-width="2" stroke-linecap="round" transform="translate(-1.5 -1.5)"/>' for pts in BRANCHES.values())}
  </g>
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="#000" opacity="0"/>
  {syringe(h, U, PX_MM, shadow=True)}
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="7"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="3"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  <line id="pupil-line" x1="{fmt(c((PUPIL_X, -24))[0])}" y1="0" x2="{fmt(c((PUPIL_X, 0))[0])}" y2="1200" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.7"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    d = math.hypot(TIP[0] - FORAMEN[0], TIP[1] - FORAMEN[1])
    print(out, f"tip {d:.1f} mm short of the foramen centre")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
