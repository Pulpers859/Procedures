"""Fascia iliaca block - the right groin in section under a linear probe.

Painted base plus code-drawn markings. The art descends from the owner's
Gemini Nano Banana Pro repaint of the flat-colour zoomed layout (commit
d7c43c8), the best tissue rendering of every attempt, which the owner then
had Gemini revise with the fascial plane opened (provenance.json). It ran
medial-left, so it is mirrored here (gemini-original.jpg is the file as
painted) to run lateral-left like the patient-position plate and a
transverse ultrasound. The painting lies on the layout within a few pixels;
the layout shapes stay as the invisible regions (DEBUG=1 shows them), with
the muscle surface under the opened plane traced on the painting. The dent
under Gemini's narrow probe was eased level in base.jpg and the probe is
drawn here across the whole field. Re-trace them if the base is replaced.

Transverse section at the inguinal crease, patient supine, seen from the
feet: lateral on the image left, medial on the right, skin at the top.
Superficial to deep (record subtitle): skin, subcutaneous fat, fascia lata,
fascia iliaca, then iliopsoas, with bone at the bottom. The femoral vein and
artery lie superficial to the fascia iliaca, vein medial. The femoral nerve
and the lateral femoral cutaneous nerve lie in the fascial plane deep to the
fascia iliaca, on the iliopsoas and its own thin fascia, not in the muscle
(owner, 2026-09-30); the muscle region is shaped to pass beneath them.

A second pale fascial line, code-drawn along the floor of that plane (the
muscle's own fascia), shows it as a plane of its own between two layers
(owner, 2026-09-30).

Markings: the probe, the needle in-plane from lateral (tip in that plane,
lateral to the nerve), and the teal injectate opening the plane - lifting
the fascia iliaca off the iliopsoas and wrapping the femoral nerve medially
and the lateral femoral cutaneous nerve laterally (record anatomy).

Millimetres from the femoral artery centre (x lateral, y deep from the skin)
at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/ficb_anatomy_layers/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_anatomy_layers"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 28.0
ORIGIN = (392.0, 130.0)           # layout origin before the mirror
X0, X1 = -16.0, 45.0              # frame edges in mm


def c(p):
    """mm (x lateral, y deep) -> canvas; lateral is drawn on the left."""
    return (1600 - (ORIGIN[0] + p[0] * PX_MM), ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=60):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom, x0=X0 - 3, x1=X1 + 3):
    return curve(top, x0, x1) + list(reversed(curve(bottom, x0, x1)))


def lata_y(x):
    return 7.8 - 0.035 * x


# Fascia iliaca, traced lateral to medial: under sartorius, over the nerve,
# then down the medial border of the iliopsoas, deep and lateral to the artery.
ILIACA = [(X1 + 3, 17.2), (40, 17.0), (32, 16.4), (24, 15.2), (16, 13.9), (11, 13.6), (8, 14.6), (6.4, 17.2),
          (4.6, 21.5), (3.2, 27), (2.4, 34)]


def iliaca_y(x):
    for (xa, ya), (xb, yb) in zip(ILIACA, ILIACA[1:]):
        if xb <= x <= xa:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    raise ValueError(x)


ARTERY = ((0.0, 13.8), 4.8)
VEIN = ((-11.0, 17.0), 6.0, 5.2)
NERVE = ((13.2, 16.3), 4.2, 1.6, 6.0)            # centre, rx, ry, rotation (deg)
LFCN = ((36.5, 18.6), 1.1)
SARTORIUS = [(31, 12.2), (36, 9.6), (42, 8.9), (X1 + 3, 9.0), (X1 + 3, 16.6), (40, 16.4), (34, 15.4)]
BONE_Y = 34.5
PROBE = (-5.0, 33.0)                               # footprint, mm
# The iliopsoas surface under the opened plane, traced on the painting (mm).
MUSCLE_SURFACE = [(8, 19.36), (10, 19.26), (12, 19.3), (14, 19.31), (16, 19.35), (18, 18.88), (20, 18.69), (22, 18.26),
                  (24, 18.17), (26, 18.26), (28, 18.4), (30, 18.7), (32, 19.12), (34, 19.83), (36, 20.4), (38, 20.5),
                  (40, 20.02), (42, 19.36), (44, 19.1), (48, 19.0)]
# The probe covers the whole field, as the section is the ultrasound plane
# (owner, 2026-09-30); it ends just short of the lateral edge, where the
# needle goes in. The painted dent under Gemini's narrow probe was eased
# level (provenance.json), so the skin lies flat under this face.
PROBE_START_PX = 150.0                             # canvas x of the probe's lateral end
SKIN_UNDER_PROBE_MM = 1.02                         # the flattened skin surface under the face
SKIN_NATURAL_MM = 0.0
GAP_START_PX = 53.0                                # the skin eases back up across the gap
NEEDLE_TIP = (19.6, 16.6)                          # mid-plane, lateral to the nerve, under the probe
NEEDLE_ENTRY_X = 39.7                              # in the gap at the probe's lateral end
SPREAD_MEDIAL = NERVE[0][0] - NERVE[1] - 0.7


def canvas_x_mm(px):
    return (1600 - px - ORIGIN[0]) / PX_MM


def painted_skin(x):
    """The skin surface on the (flattened) painting, in mm: level under the
    probe, easing back to its natural height across the lateral gap."""
    x_probe, x_gap = canvas_x_mm(PROBE_START_PX), canvas_x_mm(GAP_START_PX)
    if x <= x_probe:
        return SKIN_UNDER_PROBE_MM
    if x >= x_gap:
        return SKIN_NATURAL_MM
    f = (x - x_probe) / (x_gap - x_probe)
    return SKIN_UNDER_PROBE_MM + (SKIN_NATURAL_MM - SKIN_UNDER_PROBE_MM) * (1 - math.cos(math.pi * f)) / 2


def needle_entry():
    return (NEEDLE_ENTRY_X, painted_skin(NEEDLE_ENTRY_X))


def needle_out():
    """The needle continues 45% of its buried length back out of the skin."""
    (ex, ey), (tx, ty) = needle_entry(), NEEDLE_TIP
    return (ex + (ex - tx) * 0.45, ey + (ey - ty) * 0.45)


def muscle_top(x):
    """The iliopsoas surface, deep to the opened fascial plane in which both
    nerves lie (traced on the painting)."""
    pts_ = MUSCLE_SURFACE
    if x <= pts_[0][0]:
        return pts_[0][1]
    for (xa, ya), (xb, yb) in zip(pts_, pts_[1:]):
        if xa <= x <= xb:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    return pts_[-1][1]


def floor_smooth(x):
    """The plane's floor (muscle surface), smoothed over 4 mm so its edge has
    no kinks from the tracing."""
    return sum(muscle_top(x + d) for d in (-2, -1, 0, 1, 2)) / 5


CAP_X = 10.5                                       # where the rounded medial end begins


def spread():
    """The injectate filling the opened plane between the fascia iliaca and the
    muscle, from a rounded end just medial to the femoral nerve out to the
    lateral edge."""
    lateral = X1 + 3
    n = 40
    tops = [(lateral - (lateral - CAP_X) * i / n, 0) for i in range(n + 1)]
    top = [(x, iliaca_y(x) + 0.2) for x, _ in tops]
    y_top, y_bot = iliaca_y(CAP_X) + 0.2, floor_smooth(CAP_X) - 0.15
    mid, half = (y_top + y_bot) / 2, (y_bot - y_top) / 2
    reach = CAP_X - (NERVE[0][0] - NERVE[1] - 0.8)  # rounds out past the nerve's medial tip
    cap = [(CAP_X - reach * math.sin(math.radians(a)), mid - half * math.cos(math.radians(a))) for a in range(20, 180, 20)]
    bottom = [(x, floor_smooth(x) - 0.15) for x, _ in reversed(tops)]
    return top + cap + bottom


def plane_floor_line():
    """The muscle's own fascia: the floor of the plane, below the nerves and
    above the muscle, then round the muscle's medial corner and down its
    medial border."""
    lateral = X1 + 3
    along = [(lateral - (lateral - 8.0) * i / 40, 0) for i in range(41)]
    # Medially it follows the muscle round its corner and down its medial
    # border, inside the fascia iliaca, to the bone (traced on the painting).
    return [(x, floor_smooth(x) + 0.05) for x, _ in along] + MEDIAL_BORDER


MUSCLE_TOP = [(x, muscle_top(x)) for x in [X1 + 3 - i * (X1 + 3 - 8.0) / 60 for i in range(61)]]
# The muscle's medial corner and border, traced on the painting (mm).
MEDIAL_BORDER = [(7.4, 19.75), (6.5, 20.55), (5.9, 21.5), (5.35, 22.8), (4.95, 24.5), (4.55, 26.2), (4.15, 28.3),
                 (3.75, 30.2), (3.45, 32.2), (3.25, 33.8)]
ILIOPSOAS = MUSCLE_TOP + MEDIAL_BORDER + [(X1 + 3, BONE_Y - 0.4)]


def ellipse(center, rx, ry, attrs, rot=0.0):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'transform="rotate({fmt(-rot)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="deep-fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFD386"/><stop offset="1" stop-color="#E2BC5E"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    below_skin = band(lambda x: 1.6, lambda x: 60)
    below_lata = band(lata_y, lambda x: 60)
    skin = band(lambda x: 0.0, lambda x: 60)
    bone = band(lambda x: BONE_Y, lambda x: 60)

    a, e, t = c(needle_out()), c(needle_entry()), c(NEEDLE_TIP)
    px0, px1 = sorted((c((PROBE[0], 0))[0], c((PROBE[1], 0))[0]))

    labels = [
        Label(["Fascia iliaca"], anchor=(40, 800), leader=[(236, 750), c((canvas_x_mm(262), iliaca_y(canvas_x_mm(262))))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(620, 1010), leader=[(800, 955), c((13.2, 16.4))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(1150, 300), leader=[(1300, 322), c((0.5, 10.0))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(480, 880), leader=[(600, 832), c((22, 23))], target_id="iliopsoas"),
        Label(["Sartorius"], anchor=(40, 488), leader=[(150, 506), (150, 540)], target_id="sartorius"),
    ]

    if painted:
        face_y = ORIGIN[1] + SKIN_UNDER_PROBE_MM * PX_MM
        probe_marking = (
            f'<rect id="probe" x="{fmt(PROBE_START_PX)}" y="-60" width="{fmt(1700 - PROBE_START_PX)}" height="{fmt(face_y + 60)}" rx="34" '
            f'fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>'
            f'<rect x="{fmt(PROBE_START_PX + 18)}" y="{fmt(face_y - 16)}" width="{fmt(1700 - PROBE_START_PX)}" height="14" rx="6" fill="#3E454C"/>'
            f'<path d="M{fmt(PROBE_START_PX + 34)},{fmt(face_y - 44)} H1600" stroke="#C6CCD2" stroke-width="3" opacity="0.8"/>')
    else:
        probe_marking = (f'<rect id="probe" x="{fmt(px0)}" y="{fmt(ORIGIN[1] - 150)}" width="{fmt(px1 - px0)}" height="150" rx="26" '
                         f'fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>'
                         f'<rect x="{fmt(px0 + 10)}" y="{fmt(ORIGIN[1] - 14)}" width="{fmt(px1 - px0 - 20)}" height="12" rx="5" fill="#3E454C"/>')
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
  <path id="muscle-surface" d="{path(MUSCLE_TOP + MEDIAL_BORDER, tension=0.6)}" fill="none" stroke="#E9CFC6" stroke-width="4"/>
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="bone" d="{path(bone, closed=True, tension=0.3)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="fascia-lata" d="{path(curve(lata_y))}" fill="none" stroke="#F8F6F0" stroke-width="10"/>
  <path d="{path(curve(lata_y))}" fill="none" stroke="#9E927C" stroke-width="3"/>
  <path id="fascia-iliaca" d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="11"/>
  <path d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#9E927C" stroke-width="3"/>
  {ellipse(NERVE[0], NERVE[1], NERVE[2], 'id="femoral-nerve" fill="#EFCB5A" stroke="#B8962E" stroke-width="4"', NERVE[3])}
  {ellipse(LFCN[0], LFCN[1], LFCN[1], 'id="lfcn" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ellipse(VEIN[0], VEIN[1], VEIN[2], 'id="femoral-vein" fill="url(#vein-grad)" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(ARTERY[0], ARTERY[1], ARTERY[1], 'id="femoral-artery" fill="url(#artery-grad)" stroke="#8E211D" stroke-width="6"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
  </g>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.9)}" fill="#6CCBD2" fill-opacity="0.66" stroke="#0E8C98" stroke-width="3" stroke-opacity="0.8"/>
  <path id="plane-floor" d="{path(plane_floor_line(), tension=0.9)}" fill="none" stroke="#FBF6F1" stroke-width="9" stroke-linecap="round" opacity="0.95"/>
  <path d="{path(plane_floor_line(), tension=0.9)}" fill="none" stroke="#C9B6AC" stroke-width="2.5" stroke-linecap="round"/>
  {probe_marking}
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
