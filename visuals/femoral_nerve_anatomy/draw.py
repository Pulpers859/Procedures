"""Femoral nerve block - the right groin in section under a linear probe.

Painted base plus code-drawn markings. base.jpg is Gemini (Nano Banana Pro,
driven through Antigravity) repainting the flat layout of commit 542c88e
with prompt B, the NYSORA femoral plate attached for the relationships only
(provenance.json). The painting lies on the layout within a few pixels, so
the layout shapes stay as the invisible regions (DEBUG=1 shows them); the
iliopsoas surface under the nerve and its medial border are traced on the
painting. Re-trace them if the base is replaced.

The layout notes follow.

Adapted from the approved FICB section layout (commit d7c43c8), mirrored to
run lateral-left like the positioning plate and a transverse ultrasound, with
the iliopsoas shaped to pass beneath the femoral nerve (the nerve lies in the
fascial plane, not the muscle; owner, 2026-09-30). Record: the femoral nerve
lies lateral to the femoral artery, covered by the fascia iliaca; needle
in-plane from lateral to medial; the tip pops through the fascia iliaca
beside the nerve; inject 15-20 mL. The teal spread is drawn round the femoral
nerve in the plane under the fascia iliaca.

FICB layout notes follow (sides there are before the mirror).

Composition after the classic regional-anaesthesia plate (owner's choice,
2026-09-30): zoomed in on the plane, probe on the skin, needle in-plane from
lateral. Drawn from scratch here; nothing is traced or copied from any
published image.

Transverse section at the inguinal crease, patient supine: medial on the
image left, lateral on the right, skin at the top. Superficial to deep
(record subtitle): skin, subcutaneous fat, fascia lata, fascia iliaca, then
iliopsoas, with bone at the bottom. The femoral vein and artery lie
superficial to the fascia iliaca, vein medial. The femoral nerve lies deep to
the fascia iliaca, lateral to the artery; the fascia turns down along the
muscle's medial border, deep and lateral to the artery. Sartorius sits
laterally under the fascia lata; the lateral femoral cutaneous nerve lies
deep to the fascia iliaca near it (record: the spread reaches both nerves).

Markings: the probe, the needle from lateral (tip under the fascia iliaca,
lateral to the nerve), and the teal spread in the plane between fascia
iliaca and iliopsoas, lifting the fascia and reaching the femoral nerve
medially and the lateral femoral cutaneous nerve laterally.

Millimetres from the femoral artery centre (x lateral, y deep from the skin)
at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/femoral_nerve_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "femoral_nerve_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 28.0
ORIGIN = (392.0, 130.0)           # canvas of the skin surface above the artery
X0, X1 = -16.0, 45.0              # frame edges in mm


def c(p):
    return (1600 - (ORIGIN[0] + p[0] * PX_MM), ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=40):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom, x0=X0 - 3, x1=X1 + 3):
    return curve(top, x0, x1) + list(reversed(curve(bottom, x0, x1)))


def skin_y(x):
    return 0.0


def lata_y(x):
    return 7.8 - 0.035 * x


# Fascia iliaca, traced lateral to medial: under sartorius, over the nerve,
# then down the medial border of the iliopsoas, deep and lateral to the artery.
ILIACA = [(X1 + 3, 17.2), (40, 17.0), (32, 16.4), (24, 15.2), (16, 13.9), (11, 13.6), (8, 14.6), (6.4, 17.2),
          (4.6, 21.5), (3.2, 27), (2.4, 34)]


def iliaca_y(x):
    pts_ = ILIACA
    for (xa, ya), (xb, yb) in zip(pts_, pts_[1:]):
        if xb <= x <= xa:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    raise ValueError(x)


ARTERY = ((0.0, 13.8), 4.8)
VEIN = ((-11.0, 17.0), 6.0, 5.2)
NERVE = ((13.2, 16.3), 4.2, 1.6, 6.0)            # centre, rx, ry, rotation (deg)
LFCN = ((36.5, 18.6), 1.1)
SARTORIUS = [(31, 12.2), (36, 9.6), (42, 8.9), (X1 + 3, 9.0), (X1 + 3, 16.6), (40, 16.4), (34, 15.4)]
BONE_Y = 34.5
# Muscle top: under the fascia laterally, dropping beneath the femoral nerve
# so the nerve lies in the plane, then down the medial border to the bone.
MUSCLE_TOP = [(X1 + 3, 17.55), (40, 17.35), (32, 16.75), (24, 15.55), (21, 16.4), (19, 17.6), (16.5, 18.4),
              (12, 18.6), (9.4, 18.25), (7.6, 18.45), (5.6, 21.6), (4.2, 27.4), (3.4, BONE_Y - 0.4)]


def muscle_top(x):
    for (xa, ya), (xb, yb) in zip(MUSCLE_TOP, MUSCLE_TOP[1:]):
        if xb <= x <= xa:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    raise ValueError(x)
PROBE = (-5.0, 33.0)                               # footprint in the layout, mm
NEEDLE_OUT, NEEDLE_ENTRY, NEEDLE_TIP = (43.2, -8.2), (34.6, 0.0), (18.7, 15.2)
# The probe covers the field from the medial edge to about 1 cm short of the
# lateral edge, where the needle goes in (owner, 2026-09-30).
PROBE_START_PX = 284.0                             # canvas x of the probe's lateral end

# The iliopsoas surface under the fascial plane, its medial corner and its
# medial border down to the bone, traced on the painting (canvas px).
FLOOR_PX = [(450, 575), (525, 577), (575, 580), (625, 605), (675, 622), (725, 632), (800, 637), (875, 640),
            (950, 640), (990, 645), (1015, 665), (1036, 700), (1049, 725), (1057, 750), (1071, 800),
            (1082, 850), (1095, 900), (1110, 950), (1124, 1000), (1132, 1075), (1136, BONE_Y * PX_MM + ORIGIN[1] - 10)]


def mm(px):
    """canvas px -> mm (x lateral, y deep)."""
    return ((1600 - px[0] - ORIGIN[0]) / PX_MM, (px[1] - ORIGIN[1]) / PX_MM)


FLOOR = [mm(p) for p in FLOOR_PX]
# Lateral to the trace the muscle lies on the fascia, as in the layout.
LATERAL_TOP = [pt for pt in MUSCLE_TOP if pt[0] > FLOOR[0][0] + 1.5]
ILIOPSOAS = LATERAL_TOP + FLOOR + [(X1 + 3, BONE_Y - 0.4)]


def floor_y(x):
    """The traced muscle surface under the plane, in mm (x within the trace's top run)."""
    for (xa, ya), (xb, yb) in zip(FLOOR, FLOOR[1:]):
        if xb <= x <= xa:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    raise ValueError(x)


SPREAD_LATERAL, SPREAD_MEDIAL = 21.4, 7.7


def spread():
    """Teal lens in the plane between the fascia iliaca and the traced muscle
    surface, wrapping the femoral nerve, with rounded ends."""
    xa, xb, n = SPREAD_LATERAL, SPREAD_MEDIAL, 40
    xs = [xa - (xa - xb) * k / n for k in range(n + 1)]
    top = [(x, iliaca_y(x) + 0.25) for x in xs]

    def bot(x):
        t = iliaca_y(x) + 0.25
        return t + (floor_y(x) - 0.05 - t) * min(1.0, 1.6 * max(0.0, math.sin(math.pi * (x - xb) / (xa - xb))) ** 0.5)
    return top + [(x, bot(x)) for x in reversed(xs)]


def plane_floor_line():
    """The muscle's own fascia, the floor of the plane: from where the plane
    opens under the fascia iliaca, along the traced surface, round the medial
    corner and down the medial border."""
    return [(x, y + 0.05) for x, y in FLOOR[2:]]


def ellipse(center, rx, ry, attrs, rot=0.0):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'transform="rotate({fmt(rot)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="deep-fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFD386"/><stop offset="1" stop-color="#E2BC5E"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    below_skin = band(lambda x: 1.6, lambda x: 60)
    below_lata = band(lata_y, lambda x: 60)
    skin = band(skin_y, lambda x: 60)
    bone = band(lambda x: BONE_Y, lambda x: 60)

    a, e, t = c(NEEDLE_OUT), c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    face_y = ORIGIN[1]

    labels = [
        Label(["Fascia iliaca"], anchor=(40, 1060), leader=[(260, 1010), c((26, iliaca_y(26)))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(640, 440), leader=[(820, 452), c((13.6, 16.0))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(1160, 300), leader=[(1260, 330), c((-1.5, 12.5))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(520, 900), leader=[(580, 860), c((22, 24))], target_id="iliopsoas"),
    ]

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
<g id="anatomy" clip-path="url(#frame)"{base_attr}>
  {base_image}
  <g id="layout"{layout_attr}>
  <path id="skin" d="{path(skin, closed=True, tension=0.3)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(below_skin, closed=True, tension=0.3)}" fill="url(#fat)"/>
  <path d="{path(below_lata, closed=True, tension=0.3)}" fill="url(#deep-fat)"/>
  <path id="iliopsoas" d="{path(ILIOPSOAS, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="bone" d="{path(bone, closed=True, tension=0.3)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="fascia-lata" d="{path(curve(lata_y))}" fill="none" stroke="#F8F6F0" stroke-width="10"/>
  <path d="{path(curve(lata_y))}" fill="none" stroke="#9E927C" stroke-width="3"/>
  <path id="fascia-iliaca" d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="11"/>
  <path d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#9E927C" stroke-width="3"/>
  {ellipse(NERVE[0], NERVE[1], NERVE[2], 'id="femoral-nerve" fill="#EFCB5A" stroke="#B8962E" stroke-width="4"', NERVE[3])}
  {ellipse(LFCN[0], LFCN[1], LFCN[1], 'id="lfcn" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ellipse(VEIN[0], VEIN[1], VEIN[2], 'id="femoral-vein" fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(ARTERY[0], ARTERY[1], ARTERY[1], 'id="femoral-artery" fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
  </g>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.9)}" fill="#6CCBD2" fill-opacity="0.66" stroke="#0E8C98" stroke-width="3" stroke-opacity="0.8"/>
  <path id="plane-floor" d="{path(plane_floor_line(), tension=0.6)}" fill="none" stroke="#FBF6F1" stroke-width="9" stroke-linecap="round" opacity="0.95"/>
  <path d="{path(plane_floor_line(), tension=0.6)}" fill="none" stroke="#C9B6AC" stroke-width="2.5" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(PROBE_START_PX)}" y="-60" width="{fmt(1700 - PROBE_START_PX)}" height="{fmt(face_y + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(PROBE_START_PX + 18)}" y="{fmt(face_y - 16)}" width="{fmt(1700 - PROBE_START_PX)}" height="14" rx="6" fill="#3E454C"/>
  <path d="M{fmt(PROBE_START_PX + 34)},{fmt(face_y - 44)} H1600" stroke="#C6CCD2" stroke-width="3" opacity="0.8"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10" stroke-linecap="butt"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5" stroke-linecap="butt"/>
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
