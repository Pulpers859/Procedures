"""Auricular block - needle entry on the patient, right ear from the side.

Patient seated, right side of the head seen from the right in the atlas
orientation: head up, face to the image right (anterior), occiput to the
left. Painted as a photograph.

Placed in millimetres from the centre of the ear: u runs anteriorly (right),
v runs up. Adult surface anatomy: auricle about 62 mm tall and 33 mm wide,
long axis tilted back about 15 degrees; tragus over the ear canal; lobe free
below its attachment; mandibular ramus in front of and below the lobe, angle
about 25 mm below the lobe; hairline about 15 mm above the helix.

Markings (drawn again in code over the painted base): the two puncture sites
from the record - just below the earlobe and just above the ear - and the four
subcutaneous tracks from them, in front of the tragus and behind the ear over
the mastoid, meeting as a diamond round the base of the ear.

Scale: 10 px per mm.

Run: python3 visuals/auricular_patient_position/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "auricular_patient_position"
PX_PER_MM = 10.0
OX, OY = 800.0, 500.0     # canvas position of the ear centre


def c(p):
    return (OX + p[0] * PX_PER_MM, OY - p[1] * PX_PER_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


EAR = [(8, 21), (3, 28.5), (-4, 31.5), (-11, 29.5), (-16, 21), (-18.5, 9), (-17, -4), (-13, -15), (-9, -23),
       (-6, -29.5), (-1.5, -32), (3, -29.5), (5.5, -23), (7.5, -17), (9.5, -9), (10.5, -2), (9.5, 6), (8.5, 14)]
HELIX_INNER = [(6, 19), (2, 25.5), (-4, 28), (-10, 26), (-14, 19), (-15.5, 8), (-14, -4), (-10.5, -13), (-7, -19)]
ANTIHELIX = [(4, 15), (-1, 20), (-7, 21), (-11.5, 14), (-12.5, 3), (-10.5, -8), (-6.5, -15), (-1, -16),
             (2, -12), (-4, -9), (-6.5, 0), (-5, 9), (0, 12)]
CONCHA = [(4.5, 8), (-1, 10), (-4.5, 4), (-5.5, -4), (-2.5, -11), (3, -11), (6.5, -6), (7, 2)]
CANAL = (4.5, -2)
TRAGUS = [(10.5, 3), (7.5, 2.5), (5.5, -1), (6, -6), (8.5, -8), (10.5, -6)]
ANTITRAGUS = [(1, -12), (-3, -13), (-5.5, -11), (-3, -9), (0.5, -9.5)]
LOBE = [(-6, -23), (-5, -29.5), (-1.5, -31.5), (2.5, -29), (4, -23), (-1, -20)]

HAIR = [(-90, 70), (-90, -8), (-70, -6), (-50, 4), (-36, 22), (-24, 40), (-8, 47), (10, 48), (28, 45),
        (46, 50), (90, 56), (90, 70)]
JAW = [(14, -17), (13, -32), (11, -46), (12, -56), (19, -63), (35, -68), (60, -74), (95, -80)]
NECK = [(-90, -72), (-40, -68), (-10, -62), (12, -56), (19, -63), (35, -68), (60, -74), (95, -80), (95, -90), (-90, -90)]

INFERIOR_SITE = (-1.5, -37.5)
SUPERIOR_SITE = (-4, 37.5)
ANTERIOR_MEET = (17, 1)
POSTERIOR_MEET = (-26, 0)
TRACKS = {
    "track-inf-ant": [INFERIOR_SITE, (11, -22), ANTERIOR_MEET],
    "track-inf-post": [INFERIOR_SITE, (-17, -22), POSTERIOR_MEET],
    "track-sup-ant": [SUPERIOR_SITE, (10, 24), ANTERIOR_MEET],
    "track-sup-post": [SUPERIOR_SITE, (-19, 25), POSTERIOR_MEET],
}

DEFS = ""


def build() -> str:
    tracks = "".join(
        f'<path id="{tid}" d="{path(pts)}" fill="none" stroke="#0E8C98" stroke-width="9" stroke-linecap="round" opacity="0.8"/>'
        for tid, pts in TRACKS.items())
    sites = "".join(
        f'<circle id="{sid}" cx="{fmt(c(p)[0])}" cy="{fmt(c(p)[1])}" r="16" fill="#C8322B" stroke="#FFFFFF" stroke-width="4"/>'
        for sid, p in (("site-inferior", INFERIOR_SITE), ("site-superior", SUPERIOR_SITE)))
    cx, cy = c(CANAL)

    labels = [
        Label(["Puncture sites"], anchor=(1060, 150), leader=[(1150, 175), c(SUPERIOR_SITE)],
              target_id="site-superior", emphasis=True),
        Label(["Tragus"], anchor=(1180, 560), leader=[(1180, 540), c((8.5, -3))], target_id="tragus"),
        Label(["Mastoid"], anchor=(80, 700), leader=[(260, 660), c((-26, -8))], target_id="head"),
    ]

    body = f"""
<g id="anatomy" stroke-linejoin="round">
  <rect id="head" x="0" y="0" width="1600" height="1200" fill="#EFCDB6"/>
  <path id="neck" d="{path(NECK, closed=True, tension=0.6)}" fill="#E2B79D"/>
  <path id="jaw" d="{path(JAW)}" fill="none" stroke="#C99A80" stroke-width="5"/>
  <path id="hair" d="{path(HAIR, closed=True, tension=0.6)}" fill="#5A4030"/>
  <path id="ear" d="{path(EAR, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="4"/>
  <path id="helix-rim" d="{path(HELIX_INNER, tension=0.8)}" fill="none" stroke="#B98468" stroke-width="4"/>
  <path id="antihelix" d="{path(ANTIHELIX, closed=True, tension=0.8)}" fill="#F3CDB8" stroke="#B98468" stroke-width="3"/>
  <path id="concha" d="{path(CONCHA, closed=True, tension=0.8)}" fill="#D99A83" stroke="#B98468" stroke-width="3"/>
  <ellipse id="ear-canal" cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(2.2 * PX_PER_MM)}" ry="{fmt(3.2 * PX_PER_MM)}" fill="#6E3A2E"/>
  <path id="tragus" d="{path(TRAGUS, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="3"/>
  <path id="antitragus" d="{path(ANTITRAGUS, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="3"/>
  <path id="lobe" d="{path(LOBE, closed=True, tension=0.8)}" fill="#EDB39B" stroke="none"/>
</g>
<g id="markings" class="marking">{tracks}{sites}</g>
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
