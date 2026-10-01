"""Inferior alveolar nerve block - needle entry on the patient (layout).

The open mouth seen from the front, as the operator faces the seated
patient: head at the top, the patient's right on the image left (house
laterality; the record names no side). Composition after the clinical
photograph the owner shared (concept only, not committed); drawn from
scratch.

Record: thumb on the coronoid notch (the deepest point of the ramus's
anterior border, felt through the cheek), the pterygomandibular raphe as a
vertical fold medial to it; insert at the midpoint between them, about 1 cm
above the occlusal plane of the lower molars, with the barrel over the
opposite premolars.

Code-drawn markings: the syringe and needle (from the patient's left lower
premolars across the mouth), the entry point and the coronoid-notch ring.
The raphe and the mouth are in the painted layer.

Millimetres from the centre of the mouth opening (x toward the patient's
left = image right, y down) at 14.5 px/mm. Adult proportions; a front view
foreshortens everything that runs back into the mouth.

Run: python3 visuals/inferior_alveolar_patient_position/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "inferior_alveolar_patient_position"
PX_MM = 14.5
ORIGIN = (800.0, 610.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def oval(center, rx, ry, n=48):
    return [(center[0] + rx * math.cos(2 * math.pi * k / n), center[1] + ry * math.sin(2 * math.pi * k / n))
            for k in range(n)]


MOUTH = ((0.0, 0.0), 29.0, 22.0)                   # the open mouth's inner opening
LIPS = [(-33, 0), (-28, -16), (-14, -27), (-4, -27.5), (0, -26), (4, -27.5), (14, -27), (28, -16), (33, 0),
        (28, 18), (14, 28.5), (0, 30), (-14, 28.5), (-28, 18)]

# Teeth, front view: centre, half-width, half-height. Posterior teeth sit
# nearer the centre line and smaller, as they recede into the mouth.
UPPER = [((-2.3, -17.0), 2.2, 4.6), ((-6.6, -16.6), 2.0, 4.2), ((-10.6, -15.8), 1.9, 4.0), ((-14.0, -15.0), 1.9, 3.4),
         ((-17.0, -14.4), 1.9, 3.0), ((-20.0, -14.0), 2.2, 2.7), ((-22.8, -13.8), 2.0, 2.4)]
LOWER = [((-2.0, 16.4), 1.9, 4.0), ((-5.8, 15.8), 1.9, 3.9), ((-9.6, 14.2), 2.0, 3.8), ((-13.2, 11.8), 2.1, 3.3),
         ((-16.4, 9.6), 2.2, 3.0), ((-19.6, 7.6), 2.6, 2.8), ((-22.4, 6.2), 2.3, 2.4)]
LOWER_MOLARS_OCCLUSAL_Y = 4.0                       # top of the lower molars
TONGUE = [(-15, 13), (-14, 5), (-8, 1.6), (0, 0.6), (8, 1.6), (14, 5), (15, 13), (8, 16.4), (0, 17), (-8, 16.4)]
PHARYNX = ((0.0, -4.0), 8.6, 7.2)
UVULA = [(-1.6, -11.4), (1.6, -11.4), (1.4, -6.0), (0, -4.6), (-1.4, -6.0)]
RAPHE = [(-19.0, -10.6), (-19.4, -6), (-19.4, -1), (-18.8, 3.4)]
CHEEK_RIGHT = [(-28.6, -11), (-26.4, -5), (-25.8, 2), (-27.6, 9), (-28.6, 11)]

CORONOID_NOTCH = (-26.4, -5.0)                      # felt through the cheek; the thumb's place
ENTRY = ((CORONOID_NOTCH[0] + RAPHE[1][0]) / 2, LOWER_MOLARS_OCCLUSAL_Y - 10.0)
PREMOLAR_REST = (16.4, 9.4)                         # the patient's left lower premolars
U = (lambda dx, dy: (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)))(PREMOLAR_REST[0] - ENTRY[0],
                                                                        PREMOLAR_REST[1] - ENTRY[1])
NEEDLE_SEEN_MM = 22.0                               # foreshortened: the needle runs back into the mouth
HUB = (ENTRY[0] + U[0] * NEEDLE_SEEN_MM, ENTRY[1] + U[1] * NEEDLE_SEEN_MM)
BARREL_END = (HUB[0] + U[0] * 60.0, HUB[1] + U[1] * 60.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7BFA4"/><stop offset="1" stop-color="#DDB094"/></linearGradient>
<linearGradient id="lip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C77A72"/><stop offset="1" stop-color="#B9665F"/></linearGradient>
<radialGradient id="cavity" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#7A2E2E"/><stop offset="1" stop-color="#B4524C"/></radialGradient>
<linearGradient id="tongue-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9776F"/><stop offset="1" stop-color="#C45F58"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
"""


def teeth(rows, attrs_id):
    out = []
    for i, (ct, w, h) in enumerate(rows):
        for sx in (1, -1):
            p = c((ct[0] * sx, ct[1]))
            tid = f' id="{attrs_id}"' if (attrs_id and sx == -1 and i == 4) else ""
            out.append(f'<rect{tid} x="{fmt(p[0] - w * PX_MM)}" y="{fmt(p[1] - h * PX_MM)}" width="{fmt(2 * w * PX_MM)}" '
                       f'height="{fmt(2 * h * PX_MM)}" rx="{fmt(0.8 * PX_MM)}" fill="#F6F1E4" stroke="#B9AE95" stroke-width="3"/>')
    return "".join(out)


def build() -> str:
    e, h, b0 = c(ENTRY), c(HUB), c(BARREL_END)
    nx, ny = -U[1], U[0]
    bw = 3.6 * PX_MM
    barrel = [(h[0] + nx * bw * 0.35, h[1] + ny * bw * 0.35), (h[0] + U[0] * 14 + nx * bw, h[1] + U[1] * 14 + ny * bw),
              (b0[0] + nx * bw, b0[1] + ny * bw), (b0[0] - nx * bw, b0[1] - ny * bw),
              (h[0] + U[0] * 14 - nx * bw, h[1] + U[1] * 14 - ny * bw), (h[0] - nx * bw * 0.35, h[1] - ny * bw * 0.35)]
    notch = c(CORONOID_NOTCH)
    lower_molars = [((ct[0], ct[1]), w, hh) for ct, w, hh in LOWER[-2:]]
    lm_box = (c((lower_molars[0][0][0] - 3, 3.6)), c((lower_molars[1][0][0] + 3, 9.6)))

    labels = [
        Label(["Coronoid notch"], anchor=(40, 260), leader=[(200, 290), (notch[0] - 18, notch[1] - 12)],
              target_id="coronoid-notch"),
        Label(["Pterygomandibular", "raphe"], anchor=(40, 980), leader=[(230, 930), c((-19.6, -1.0))], target_id="raphe",
              emphasis=True),
    ]

    body = f"""
<g id="anatomy">
  <rect id="face" x="0" y="0" width="1600" height="1200" fill="url(#skin-grad)"/>
  <path id="lips" d="{path(LIPS, closed=True, tension=0.7)}" fill="url(#lip)" stroke="#9E554F" stroke-width="3"/>
  <path id="oral-cavity" d="{path(oval(*MOUTH), closed=True)}" fill="url(#cavity)" stroke="#8E4A45" stroke-width="3"/>
  <path id="cheek-mucosa" d="{path(CHEEK_RIGHT, tension=0.7)}" fill="none" stroke="#C97069" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
  <path d="{path([(-x, y) for x, y in CHEEK_RIGHT], tension=0.7)}" fill="none" stroke="#C97069" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
  <path id="pharynx" d="{path(oval(*PHARYNX), closed=True)}" fill="#5E2424"/>
  <path id="uvula" d="{path(UVULA, closed=True, tension=0.6)}" fill="#C86A63" stroke="#9E4E48" stroke-width="2"/>
  <path id="raphe" d="{path(RAPHE, tension=0.8)}" fill="none" stroke="#E9B4AC" stroke-width="16" stroke-linecap="round"/>
  <path d="{path([(-x, y) for x, y in RAPHE], tension=0.8)}" fill="none" stroke="#E9B4AC" stroke-width="16" stroke-linecap="round"/>
  <path id="tongue" d="{path(TONGUE, closed=True, tension=0.8)}" fill="url(#tongue-grad)" stroke="#A84E48" stroke-width="3"/>
  <g id="upper-teeth">{teeth(UPPER, "")}</g>
  <g id="lower-teeth">{teeth(LOWER, "premolar-left")}</g>
  <rect id="lower-molars-right" x="{fmt(lm_box[0][0])}" y="{fmt(lm_box[0][1])}" width="{fmt(lm_box[1][0] - lm_box[0][0])}" height="{fmt(lm_box[1][1] - lm_box[0][1])}" fill="none"/>
</g>

<g class="marking">
  <circle id="coronoid-notch" cx="{fmt(notch[0])}" cy="{fmt(notch[1])}" r="20" fill="none" stroke="#4A2F7A" stroke-width="6"/>
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="url(#barrel)" stroke="#7D868F" stroke-width="3"/>
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" stroke="#5E6670" stroke-width="6" stroke-linecap="butt"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" stroke="#D9DEE3" stroke-width="2.5" stroke-linecap="butt"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #E2B497; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out, f"entry {ENTRY[0]:.1f},{ENTRY[1]:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
