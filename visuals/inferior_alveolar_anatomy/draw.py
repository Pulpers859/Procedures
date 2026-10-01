"""Inferior alveolar nerve block - axial section at the mandibular foramen (layout).

The owner chose an axial section seen from above (2026-10-01): it shows the
needle's whole course, from the syringe over the opposite premolars to bone
on the medial ramus, and why a needle that misses bone lands in the parotid
(record, troubleshooting). Composition after the classic dental-anaesthesia
plate the owner shared (concept only, not committed); drawn from scratch.

House orientation for a section, as on CT: anterior (the lips) at the top,
the patient's right on the image left. The block is drawn on the right.

Record: insert at the midpoint between the coronoid notch and the
pterygomandibular raphe, about 1 cm above the lower occlusal plane, barrel
over the opposite premolars; advance to bone, usually 20-25 mm. The lingual
nerve lies just anterior and medial to the inferior alveolar nerve.

Standard adult anatomy added: the ramus with the masseter lateral and the
medial pterygoid medial, the pterygomandibular space between ramus and
medial pterygoid holding the inferior alveolar nerve and vessels at the
foramen, the raphe joining buccinator and superior constrictor, the parotid
behind the ramus, the tongue inside the lower arch and the oropharynx.
The section is schematic in height: the lower crowns are drawn in it so the
needle can be read against the arch, as on the classic plate.

Millimetres from the midline at the front of the lower incisors (x toward
the patient's left = image right, y posterior = image down) at 11.4 px/mm.

Run: python3 visuals/inferior_alveolar_anatomy/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "inferior_alveolar_anatomy"
PX_MM = 1600 / 140.0
ORIGIN = (800.0, 5 * PX_MM)       # canvas of the midline at the incisors


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def mirror(points):
    return [(-x, y) for x, y in points]


def both(points):
    """A right-side outline (negative x) and its mirror, as one closed path of
    the right half then the left half reversed."""
    return points + list(reversed(mirror(points)))


# Outer face: lips at the front, cheeks, to the back of the frame.
FACE_RIGHT = [(0, -2.5), (-12, -2.0), (-24, 2), (-38, 11), (-50, 26), (-58, 44), (-62, 62), (-63, 80), (-64, 98), (-64, 112)]
# The lower lip's inner surface and the oral vestibule.
LIP_INNER = [(0, 4.5), (-10, 5.0), (-18, 8.5)]

# Lower teeth: centre, mesiodistal and buccolingual half-sizes, axis angle.
TEETH = [((-2.6, 6.2), 2.6, 3.0, 8), ((-7.6, 7.6), 2.8, 3.1, 25), ((-12.2, 10.6), 3.4, 3.8, 45),
         ((-15.6, 15.6), 3.6, 4.2, 65), ((-18.0, 22.4), 3.7, 4.4, 75), ((-20.6, 30.6), 5.4, 5.2, 82),
         ((-22.4, 41.0), 5.0, 5.0, 85)]
ARCH_OUT = [(0, 2.6), (-8, 3.6), (-14, 7.6), (-19, 14), (-22.6, 22), (-25.6, 31), (-27.6, 41), (-27.6, 47)]
ARCH_IN = [(-17.0, 47), (-16.6, 41), (-15.6, 31), (-13.6, 23), (-11.2, 16.6), (-8.4, 12.0), (-4.4, 9.8), (0, 9.4)]

TONGUE_RIGHT = [(0, 11.0), (-8, 12.5), (-12.6, 18), (-14.2, 28), (-15, 40), (-15, 52), (-13, 62), (-8, 68), (0, 70)]

# Ramus in section: anterior border (coronoid notch level) to posterior border.
RAMUS = [(-31.0, 47.6), (-36.0, 47.0), (-41.8, 52), (-48.0, 66), (-53.2, 83), (-51.6, 88), (-47.4, 85),
         (-41.6, 67), (-35.0, 53)]
FORAMEN_TIP = (-41.7, 66.4)        # needle tip on bone, on the medial surface just above the foramen
MASSETER = [(-36.6, 46.2), (-44.6, 44), (-52.6, 54), (-58.8, 68), (-61.0, 84), (-56.6, 89), (-53.6, 83), (-48.6, 66),
            (-42.4, 51.6)]
MED_PTERYGOID = [(-24.6, 63), (-29.6, 64.4), (-38.4, 72.8), (-46.6, 84.6), (-47.6, 92.6), (-42.6, 94.6), (-34.6, 86),
                 (-25.6, 74), (-21.6, 67)]
PAROTID = [(-50.6, 89.6), (-55.0, 89.4), (-59.4, 87.6), (-61.8, 92), (-62.0, 112), (-44.0, 112), (-45.6, 102), (-48.0, 95)]
BUCCINATOR = [(-21.0, 58.4), (-26.0, 52.6), (-30.2, 45), (-31.6, 36), (-31.0, 26), (-27.6, 17), (-22.6, 10)]
CONSTRICTOR = [(-21.0, 58.4), (-18.8, 66), (-16.4, 74), (-12.0, 80.6), (-5.0, 83.6), (0, 84.2)]
RAPHE = (-21.0, 58.4)
PHARYNX = ((0.0, 88.6), 10.6, 4.4)
IAN = (-40.4, 70.0)                # inferior alveolar nerve at the foramen, with its artery and vein
IAN_R = 1.5
IA_ARTERY = (-39.2, 72.6)
IA_VEIN = (-41.6, 73.0)
LINGUAL = (-33.8, 63.0)            # anterior and medial to the inferior alveolar nerve
LINGUAL_R = 1.2

# The syringe barrel rests over the opposite (left) premolars; the needle runs
# straight from there to bone, entering the mucosa between the ramus's
# anterior border and the raphe.
PREMOLAR_REST = (17.0, 22.6)
DEPTH_MM = 21.0                    # entry to bone (record: usually 20-25 mm)


def unit(a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


U = unit(PREMOLAR_REST, FORAMEN_TIP)
ENTRY = (FORAMEN_TIP[0] - U[0] * DEPTH_MM, FORAMEN_TIP[1] - U[1] * DEPTH_MM)
NEEDLE_MM = 35.0                   # long dental needle, hub to tip
HUB = (FORAMEN_TIP[0] - U[0] * NEEDLE_MM, FORAMEN_TIP[1] - U[1] * NEEDLE_MM)
BARREL_END = (HUB[0] - U[0] * 62.0, HUB[1] - U[1] * 62.0)
NEEDLE_LEN_MM = math.hypot(FORAMEN_TIP[0] - HUB[0], FORAMEN_TIP[1] - HUB[1])


def tooth(center, a, b, angle, attrs):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(a * PX_MM)}" ry="{fmt(b * PX_MM)}" '
            f'transform="rotate({fmt(angle)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


def circle(center, r, attrs):
    p = c(center)
    return f'<circle cx="{fmt(p[0])}" cy="{fmt(p[1])}" r="{fmt(r * PX_MM)}" {attrs}/>'


DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBC2A9"/><stop offset="1" stop-color="#E2B497"/></linearGradient>
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4D98C"/><stop offset="1" stop-color="#EBC86A"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<linearGradient id="tongue-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9766E"/><stop offset="1" stop-color="#B9524C"/></linearGradient>
<linearGradient id="gland" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8C9A0"/><stop offset="1" stop-color="#D9B386"/></linearGradient>
<linearGradient id="barrel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F6F8"/><stop offset="1" stop-color="#C9D1D8"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    face = both(FACE_RIGHT)
    oral = both([(0, 4.5), (-10, 5.0), (-18, 8.5), (-24, 14), (-29, 22), (-32.6, 34), (-33, 46), (-26, 56), (-20, 62),
                 (-16, 72), (-10, 80), (0, 82)])
    e, t, h, b0 = c(ENTRY), c(FORAMEN_TIP), c(HUB), c(BARREL_END)
    dx, dy = U[0], U[1]
    nx, ny = -dy, dx
    bw = 4.6 * PX_MM
    barrel = [(h[0] + nx * bw, h[1] + ny * bw), (b0[0] + nx * bw, b0[1] + ny * bw),
              (b0[0] - nx * bw, b0[1] - ny * bw), (h[0] - nx * bw, h[1] - ny * bw)]

    labels = [
        Label(["Inferior alveolar", "nerve"], anchor=(40, 1050), leader=[(230, 1000), c((IAN[0] - 0.4, IAN[1] + 0.6))],
              target_id="ian", emphasis=True),
        Label(["Lingual nerve"], anchor=(560, 1060), leader=[(620, 1010), c(LINGUAL)], target_id="lingual-nerve"),
        Label(["Medial pterygoid"], anchor=(560, 960), leader=[(640, 920), c((-31.0, 72.0))], target_id="medial-pterygoid"),
        Label(["Parotid"], anchor=(40, 870), leader=[(140, 900), c((-56.0, 94.0))], target_id="parotid"),
        Label(["Ramus"], anchor=(40, 520), leader=[(150, 545), c((-45.6, 66.0))], target_id="ramus"),
    ]

    teeth = "".join(tooth(ct, a, b_, ang, 'class="tooth" fill="#F7F3E8" stroke="#B9AE95" stroke-width="3"')
                    + tooth((-ct[0], ct[1]), a, b_, -ang, 'fill="#F7F3E8" stroke="#B9AE95" stroke-width="3"')
                    for ct, a, b_, ang in TEETH)

    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="face" d="{path(face, closed=True, tension=0.7)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="4"/>
  <path id="subcutaneous-fat" d="{path(both([(0, -0.6), (-12, 0), (-24, 4), (-37, 13), (-48.6, 27.6), (-56.4, 45), (-60.4, 62), (-61.4, 80), (-62.4, 98), (-62.4, 112)]), closed=True, tension=0.7)}" fill="url(#fat)"/>
  <path id="oral-cavity" d="{path(oral, closed=True, tension=0.7)}" fill="#E7A39A" stroke="#C97C73" stroke-width="3"/>
  <path id="parotid" d="{path(PAROTID, closed=True, tension=0.6)}" fill="url(#gland)" stroke="#A88B62" stroke-width="3"/>
  <path d="{path(mirror(PAROTID), closed=True, tension=0.6)}" fill="url(#gland)" stroke="#A88B62" stroke-width="3"/>
  <path id="masseter" d="{path(MASSETER, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path d="{path(mirror(MASSETER), closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="pterygomandibular-space" d="{path([(-35.0, 53), (-41.6, 67), (-46.0, 80), (-42.0, 80.6), (-34.6, 70), (-27.6, 63.6), (-24.0, 60.4)], closed=True, tension=0.6)}" fill="#F0D79A" stroke="none"/>
  <path id="medial-pterygoid" d="{path(MED_PTERYGOID, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path d="{path(mirror(MED_PTERYGOID), closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="ramus" d="{path(RAMUS, closed=True, tension=0.5)}" fill="#F1E7D0" stroke="#A8977A" stroke-width="5"/>
  <path d="{path(mirror(RAMUS), closed=True, tension=0.5)}" fill="#F1E7D0" stroke="#A8977A" stroke-width="5"/>
  <path id="buccinator" d="{path(BUCCINATOR, tension=0.7)}" fill="none" stroke="#9A3530" stroke-width="{fmt(2.6 * PX_MM)}" stroke-linecap="round"/>
  <path d="{path(mirror(BUCCINATOR), tension=0.7)}" fill="none" stroke="#9A3530" stroke-width="{fmt(2.6 * PX_MM)}" stroke-linecap="round"/>
  <path id="constrictor" d="{path(CONSTRICTOR + list(reversed(mirror(CONSTRICTOR)))[1:], tension=0.7)}" fill="none" stroke="#9A3530" stroke-width="{fmt(2.4 * PX_MM)}" stroke-linecap="round"/>
  {circle(RAPHE, 1.6, 'id="raphe" fill="#F4EEE6" stroke="#B5A693" stroke-width="3"')}
  {circle((-RAPHE[0], RAPHE[1]), 1.6, 'fill="#F4EEE6" stroke="#B5A693" stroke-width="3"')}
  <ellipse id="pharynx" cx="{fmt(c(PHARYNX[0])[0])}" cy="{fmt(c(PHARYNX[0])[1])}" rx="{fmt(PHARYNX[1] * PX_MM)}" ry="{fmt(PHARYNX[2] * PX_MM)}" fill="#5A2E2E" stroke="#3E1E1E" stroke-width="3"/>
  <path id="tongue" d="{path(both(TONGUE_RIGHT), closed=True, tension=0.7)}" fill="url(#tongue-grad)" stroke="#9E4640" stroke-width="3"/>
  <path id="gingiva" d="{path(ARCH_OUT + ARCH_IN, closed=True, tension=0.6)}" fill="#E39A93" stroke="#C47A72" stroke-width="3"/>
  <path d="{path(mirror(ARCH_OUT + ARCH_IN), closed=True, tension=0.6)}" fill="#E39A93" stroke="#C47A72" stroke-width="3"/>
  <g id="teeth">{teeth}</g>
  {circle(IA_VEIN, 1.2, 'id="ia-vein" fill="#4A6AA6" stroke="#2F4A78" stroke-width="2"')}
  {circle(IA_ARTERY, 0.9, 'id="ia-artery" fill="#C8433A" stroke="#8E211D" stroke-width="2"')}
  {circle(IAN, IAN_R, 'id="ian" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {circle(LINGUAL, LINGUAL_R, 'id="lingual-nerve" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
</g>

<g class="marking">
  <polygon id="syringe" points="{' '.join(f'{fmt(x)},{fmt(y)}' for x, y in barrel)}" fill="url(#barrel)" stroke="#7D868F" stroke-width="3"/>
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="7" stroke-linecap="butt"/>
  <line x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="3" stroke-linecap="butt"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="8" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out, f"needle {NEEDLE_LEN_MM:.1f} mm from hub, entry at {ENTRY[0]:.1f},{ENTRY[1]:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
