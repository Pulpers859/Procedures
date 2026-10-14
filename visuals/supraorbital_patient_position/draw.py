"""Supraorbital nerve block - needle entry on the patient (layout).

The upper face from the front, head at the top, the patient's right on the
image left (house laterality; the record names no side), zoomed on the
right brow: forehead, eyebrows, eyes and the bridge of the nose. Same
camera style as the approved infraorbital plate (commit 10a790a), drawn
from scratch for this level.

Record: palpate the superior orbital rim for the notch, in line with the
pupil; insert subcutaneously just above the eyebrow, aiming medially over
the notch; stay subcutaneous at the rim, never seek or enter the notch;
for the supratrochlear nerve advance medially toward the bridge of the
nose in the same plane; keep a finger along the orbital rim below the
needle throughout, never toward the orbit.

Drawn: the operator's gloved index finger from the patient's right (image
left) lying along the orbital rim just under the brow, the eye below it
still visible. Code-drawn markings: the syringe and needle from above and
lateral, its tip over the notch; a dashed redirect medially to the
supratrochlear point; the pupil line and the notch ring. Added (standard
anatomy, not in the record): the supratrochlear nerve exits about 12 mm
medial to the notch.

Millimetres from the superior orbital rim's level on the midline
(x toward the patient's left = image right, y down) at 12 px/mm, the same
frame of reference as supraorbital_anatomy.

Run: python3 visuals/supraorbital_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "supraorbital_patient_position"
BASE = Path(__file__).with_name("base.jpg")
PX_MM = 12.0
ORIGIN = (900.0, 540.0)           # canvas of the midline at the superior rim's level


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def oval(center, rx, ry, n=40):
    return [(center[0] + rx * math.cos(2 * math.pi * k / n), center[1] + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


PUPIL_X = -32.0
EYE_Y = 22.0
NOTCH = (-31.0, 0.0)                    # on the rim, in line with the pupil
SUPRATROCHLEAR = (-19.0, 0.8)           # about 12 mm medial (added)
FACE = [(-70, -60), (-72, -20), (-71, 10), (-68, 40), (-64, 60), (64, 60), (68, 40), (71, 10), (72, -20), (70, -60)]
BROW_R = [(-53, -5), (-44, -9.5), (-32, -10.5), (-20, -8.5), (-13, -5.5), (-13.5, -2.0), (-21, -3.0), (-32, -4.6),
          (-44, -3.6), (-52, -1.4)]
EYE_R = [(-47, 22), (-40, 17.4), (-32, 16), (-24, 17.4), (-17.5, 21.6), (-24, 25.4), (-32, 26.6), (-40, 25.6)]
LID_CREASE = [(-45, 15.6), (-38, 11.6), (-30, 10.8), (-22, 12.2), (-17, 16)]
NOSE = [(-7, 4), (-6.6, 20), (-8.6, 40), (-10, 60), (10, 60), (8.6, 40), (6.6, 20), (7, 4)]
# The operator's gloved index finger along the rim, from the patient's right.
FINGER = [(-90, 1.6), (-50, 2.4), (-30, 2.6), (-18, 3.0), (-13.6, 5.0), (-13.4, 9.0), (-17, 11.6), (-30, 12.4),
          (-50, 12.8), (-90, 13.6)]
if BASE.exists():
    # Placed in code (2026-10-14, owner: fingertip pointing right at the notch,
    # below the brow): the photographed glove finger cut from the first photo,
    # scaled 0.85 and tilted up 20 deg onto the finger-free repaint (place_finger.py).
    FINGER = [(-90, 12.2), (-84.8, 8.7), (-66.4, 4.3), (-47.9, 0.2), (-38.4, -1.2), (-34.3, -0.5), (-31.6, 2.6), (-31.6, 6.6), (-35.3, 8.9), (-52.9, 16.1), (-80.1, 24.1), (-90, 27.8)]
ENTRY = (-42.0, -12.0)                  # just above the eyebrow, lateral to the notch
TIP = (-31.0, -7.0)                     # subcutaneous, over the notch, clear of it (the painted notch grooves the rim)
REDIRECT_TIP = (-19.0, -5.0)            # same plane, medially to the supratrochlear point
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(TIP[0] - ENTRY[0], TIP[1] - ENTRY[1])
HUB = (ENTRY[0] - U[0] * 12.0, ENTRY[1] - U[1] * 12.0)
BARREL_END = (HUB[0] - U[0] * 60.0, HUB[1] - U[1] * 60.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9C2A6"/><stop offset="1" stop-color="#DDAE90"/></linearGradient>
<linearGradient id="glove" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F4F7"/><stop offset="1" stop-color="#D5DCE4"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def build() -> str:
    e, t, r, h, b0 = c(ENTRY), c(TIP), c(REDIRECT_TIP), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 4.0 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]
    nxy, sxy = c(NOTCH), c(SUPRATROCHLEAR)
    pupil = c((PUPIL_X, EYE_Y))
    labels = [
        Label(["Supraorbital", "notch"], anchor=(1060, 150), leader=[(1060, 210), (nxy[0] + 16, nxy[1] - 14)],
              target_id="notch-mark", emphasis=True),
        Label(["Supratrochlear", "nerve"], anchor=(1060, 1010), leader=[(1080, 960), (sxy[0] + 12, sxy[1] + 12)],
              target_id="supratrochlear-mark"),
    ]
    painted = BASE.exists()
    if painted:
        from PIL import Image
        bw_, bh_ = Image.open(BASE).size
        height = 1600 * bh_ / bw_
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - height) / 2)}" width="1600" '
                      f'height="{fmt(height)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if os.environ.get("DEBUG") == "1" else 0}"'
    else:
        base_attr = base_image = layout_attr = ""
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#5C6670"/>
  <path id="face" d="{path(FACE, closed=True, tension=0.4)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="brow" d="{path(BROW_R, closed=True, tension=0.6)}" fill="#6B4E3A"/>
  <path d="{path([(-x, y) for x, y in BROW_R], closed=True, tension=0.6)}" fill="#6B4E3A"/>
  <path d="{path(LID_CREASE, tension=0.7)}" fill="none" stroke="#C2957C" stroke-width="4"/>
  <path d="{path([(-x, y) for x, y in LID_CREASE], tension=0.7)}" fill="none" stroke="#C2957C" stroke-width="4"/>
  <path id="eye" d="{path(EYE_R, closed=True, tension=0.7)}" fill="#F4F1EC" stroke="#8C6A58" stroke-width="3"/>
  <circle cx="{fmt(pupil[0])}" cy="{fmt(pupil[1])}" r="{fmt(5 * PX_MM)}" fill="#6A4E36"/>
  <circle id="pupil" cx="{fmt(pupil[0])}" cy="{fmt(pupil[1])}" r="{fmt(2 * PX_MM)}" fill="#1E1A18"/>
  <path d="{path([(-x, y) for x, y in EYE_R], closed=True, tension=0.7)}" fill="#F4F1EC" stroke="#8C6A58" stroke-width="3"/>
  <circle cx="{fmt(c((-PUPIL_X, EYE_Y))[0])}" cy="{fmt(pupil[1])}" r="{fmt(5 * PX_MM)}" fill="#6A4E36"/>
  <circle cx="{fmt(c((-PUPIL_X, EYE_Y))[0])}" cy="{fmt(pupil[1])}" r="{fmt(2 * PX_MM)}" fill="#1E1A18"/>
  <path id="nose" d="{path(NOSE, tension=0.6)}" fill="#E2B193" stroke="#B98A74" stroke-width="3"/>
  <path id="finger" d="{path(FINGER, closed=True, tension=0.6)}" fill="url(#glove)" stroke="#9AA6B2" stroke-width="3"/>
</g>

<g class="marking">
  <line id="pupil-line" x1="{fmt(pupil[0])}" y1="{fmt(pupil[1] - 6 * PX_MM)}" x2="{fmt(pupil[0])}" y2="{fmt(nxy[1] - 30)}" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.8"/>
  <circle id="notch-mark" cx="{fmt(nxy[0])}" cy="{fmt(nxy[1])}" r="24" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="10 7"/>
  <circle id="supratrochlear-mark" cx="{fmt(sxy[0])}" cy="{fmt(sxy[1])}" r="18" fill="none" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="8 6"/>
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="url(#barrel)" stroke="#7D868F" stroke-width="3"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(h[0] - U[0] * 8 * PX_MM)}" y2="{fmt(h[1] - U[1] * 8 * PX_MM)}" stroke="#6E7780" stroke-width="{fmt(2 * bw + 2)}"/>
  <line id="redirect" x1="{fmt(e[0])}" y1="{fmt(e[1])}" x2="{fmt(r[0])}" y2="{fmt(r[1])}" stroke="#5E6670" stroke-width="5" stroke-dasharray="14 10" opacity="0.85"/>
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="6"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="2.5"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="4" fill="#5E6670"/>
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
