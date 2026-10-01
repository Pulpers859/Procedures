"""Infraorbital nerve block - needle entry on the patient (layout).

The face from the front, head at the top, the patient's right on the image
left (house laterality). The operator's non-dominant gloved hand comes in
from the patient's right: the index fingertip rests on the infraorbital
foramen and the thumb lifts the upper lip, opening the mucobuccal fold
above the canine and first premolar. The syringe comes up from below, the
needle entering the fold and pointing at the fingertip. Composition after
the clinical sheet the owner shared (concept only, not committed); drawn
from scratch.

Record: palpate the foramen with the non-dominant index finger and keep it
there for the whole injection; retract the upper lip; insert in the
mucobuccal fold above the canine/first premolar, directed superiorly
toward the finger.

Code-drawn markings: the syringe and needle, the entry point, the pupil
line and the foramen ring at the fingertip. The hand is in the layout so
the painting renders it where drawn.

Millimetres from the inferior orbital rim's level on the midline (x toward
the patient's left = image right, y down) at 10 px/mm, the same frame of
reference as infraorbital_anatomy.

Run: python3 visuals/infraorbital_patient_position/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "infraorbital_patient_position"
PX_MM = 10.0
ORIGIN = (1060.0, 440.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def oval(center, rx, ry, n=40):
    return [(center[0] + rx * math.cos(2 * math.pi * k / n), center[1] + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


PUPIL_X = -32.0
FORAMEN = (-31.0, 9.0)
FACE = [(-62, -70), (-70, -10), (-70, 14), (-66, 36), (-58, 56), (-46, 70), (-20, 80), (0, 82), (20, 80), (46, 70),
        (58, 56), (66, 36), (70, 14), (70, -10), (62, -70)]
EYE_R = [(-47, -10), (-40, -15), (-32, -16.5), (-24, -15), (-18, -10.6), (-24, -7.4), (-32, -6.4), (-40, -7.2)]
BROW_R = [(-50, -24), (-40, -28.5), (-28, -28.5), (-17, -25), (-18, -23), (-29, -26), (-40, -26), (-49, -22)]
NOSE = [(-7, -26), (-8, 4), (-12, 12), (-17, 18), (-16, 24), (-9, 26.4), (0, 25), (9, 26.4), (16, 24), (17, 18),
        (12, 12), (8, 4), (7, -26)]
# The upper lip, lifted by the thumb on the patient's right.
UPPER_LIP = [(-27, 40), (-24.4, 31), (-20, 25.4), (-12, 24.4), (-5, 28.4), (-1.6, 33.6), (4, 33.6), (14, 34.6),
             (26, 39.4), (14, 41.0), (2, 40.8), (-2.6, 37.6), (-5.6, 31.4), (-12, 28.4), (-20, 29.2), (-24, 32.4)]
VESTIBULE = [(-25.4, 38.4), (-24, 32.4), (-20, 29.2), (-12, 28.4), (-5.6, 31.4), (-2.6, 37.6), (-1.0, 39.4), (-10, 38.4),
             (-18, 38.4)]
GUM = [(-25.6, 38.6), (-18, 37.6), (-8, 37.8), (0, 39.4), (8, 39.6), (16, 40), (24, 41.4), (24, 43), (-25.6, 43)]
TEETH = [(-23.6, 2.2), (-18.6, 2.6), (-13.4, 2.8), (-7.6, 3.0), (-2.8, 3.0), (2.8, 3.0), (7.6, 3.0), (13.4, 2.8),
         (18.6, 2.6)]
TEETH_TOP, TEETH_BOTTOM = 42.0, 50.4
MOUTH = [(-26, 41), (-12, 50.6), (0, 51.4), (12, 50.6), (26, 41), (12, 54), (0, 55), (-12, 54)]
LOWER_LIP = [(-26, 41), (-12, 53.6), (0, 54.6), (12, 53.6), (26, 41), (16, 59), (0, 62), (-16, 59)]
PM1 = (-23.6, 46.0)
FOLD = (-21.0, 31.6)                    # mucobuccal fold above the first premolar
ENTRY = FOLD
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(FORAMEN[0] - ENTRY[0], FORAMEN[1] - ENTRY[1])
HUB = (ENTRY[0] - U[0] * 14.0, ENTRY[1] - U[1] * 14.0)
BARREL_END = (HUB[0] - U[0] * 60.0, HUB[1] - U[1] * 60.0)
# The operator's gloved hand, from the patient's right (image left).
INDEX = [(-115, -6), (-60, -2.6), (-40, 2.6), (-33, 4.6), (-28.6, 8.4), (-29.6, 13.0), (-34, 14.4), (-42, 12.8),
         (-62, 12.4), (-115, 14)]
THUMB = [(-115, 30), (-60, 28.4), (-38, 25.6), (-24, 22.2), (-17, 22.8), (-14.6, 26.4), (-17, 29.6), (-24, 31.4),
         (-40, 37), (-62, 42.6), (-115, 46)]

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9C2A6"/><stop offset="1" stop-color="#DDAE90"/></linearGradient>
<linearGradient id="glove" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F4F7"/><stop offset="1" stop-color="#D5DCE4"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def build() -> str:
    e, h, b0 = c(ENTRY), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 4.0 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]
    fx, fy = c(FORAMEN)
    teeth = "".join(
        f'<rect{" id=" + chr(34) + "first-premolar" + chr(34) if x == PM1[0] else ""} x="{fmt(c((x - w, 0))[0])}" '
        f'y="{fmt(c((0, TEETH_TOP))[1])}" width="{fmt(2 * w * PX_MM)}" height="{fmt((TEETH_BOTTOM - TEETH_TOP) * PX_MM)}" '
        f'rx="{fmt(0.9 * PX_MM)}" fill="#F6F1E4" stroke="#B9AE95" stroke-width="2"/>' for x, w in TEETH)

    labels = [
        Label(["Infraorbital", "foramen"], anchor=(1240, 150), leader=[(1250, 120), (fx + 12, fy - 12)],
              target_id="foramen-mark", emphasis=True),
        Label(["Mucobuccal", "fold"], anchor=(1240, 1010), leader=[(1230, 980), (e[0] + 18, e[1] + 6)], target_id="vestibule"),
    ]

    body = f"""
<g id="anatomy">
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
  <path id="mouth" d="{path(MOUTH, closed=True, tension=0.6)}" fill="#5A2626"/>
  <path id="gum" d="{path(GUM, closed=True, tension=0.5)}" fill="#E39A93" stroke="#C47A72" stroke-width="2"/>
  <g id="teeth">{teeth}</g>
  <path id="upper-lip" d="{path(UPPER_LIP, closed=True, tension=0.6)}" fill="#C47C72" stroke="#9E554F" stroke-width="3"/>
  <path id="vestibule" d="{path(VESTIBULE, closed=True, tension=0.6)}" fill="#D9786F" stroke="#B85C55" stroke-width="2"/>
  <path id="index-finger" d="{path(INDEX, closed=True, tension=0.6)}" fill="url(#glove)" stroke="#9AA6B2" stroke-width="3"/>
  <path id="thumb" d="{path(THUMB, closed=True, tension=0.6)}" fill="url(#glove)" stroke="#9AA6B2" stroke-width="3"/>
</g>

<g class="marking">
  <line id="pupil-line" x1="{fmt(c((PUPIL_X, 0))[0])}" y1="{fmt(c((0, -4))[1])}" x2="{fmt(c((PUPIL_X, 0))[0])}" y2="{fmt(fy)}" stroke="#C8322B" stroke-width="4" stroke-dasharray="14 10" opacity="0.8"/>
  <circle id="foramen-mark" cx="{fmt(fx)}" cy="{fmt(fy)}" r="24" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="10 7"/>
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="url(#barrel)" stroke="#7D868F" stroke-width="3"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(h[0] - U[0] * 8 * PX_MM)}" y2="{fmt(h[1] - U[1] * 8 * PX_MM)}" stroke="#6E7780" stroke-width="{fmt(2 * bw + 2)}"/>
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
