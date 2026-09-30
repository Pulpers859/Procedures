"""Fascia iliaca block - the right groin in section under a linear probe.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of this file's layout (provenance.json). The painting lies on the
layout within a few pixels, so the layout shapes stay in place as the
invisible label and check regions (DEBUG=1 shows them) and the texture
cues are not drawn. The painted probe is kept; its region is the layout's.
Re-check the regions against the painting if the base is replaced.

Composition after the classic regional-anaesthesia plate (owner's choice,
2026-09-30): zoomed in on the plane, probe on the skin, needle in-plane from
lateral. Drawn from scratch here; nothing is traced or copied from any
published image.

Transverse section at the inguinal crease, patient supine, seen from the
feet as on CT or a transverse ultrasound (probe marker to the patient's
right): lateral on the image left, medial on the right, skin at the top. The
patient-position plate (ficb_patient_position) is drawn the same way round,
so the needle comes from the left in both.

The layout carries texture cues so the repaint reads as a cut face: muscle
as flattened fascicle bundles overlapping like scales, edged with pale
perimysium, with small paired vessels; fat as small orange-gold lobules;
nerves as a pale sheath round a few large speckled fascicle compartments;
vessels as walls round a lumen; bone as cortex over cancellous bone. The
probe dents the skin, and the fat above the fascia lata takes the squeeze. Superficial to deep
(record subtitle): skin, subcutaneous fat, fascia lata, fascia iliaca, then
iliopsoas, with bone at the bottom. The femoral vein and artery lie
superficial to the fascia iliaca, vein medial. The femoral nerve lies deep to
the fascia iliaca, lateral to the artery; the fascia turns down along the
muscle's medial border, deep and lateral to the artery. Sartorius sits
laterally under the fascia lata; the lateral femoral cutaneous nerve lies
deep to the fascia iliaca near it (record: the spread reaches both nerves).

A plain probe is in the painted layer too, so the strip above the skin is
not an empty margin (an empty strip made Gemini frame the picture); code
draws the exact probe over it. The femoral nerve and the lateral femoral cutaneous nerve lie in the fascial
plane, deep to the fascia iliaca and on the iliopsoas's own thin fascia, not
in the muscle (owner, 2026-09-30). The layout shows that plane opened by the
injectate, as a pale fluid layer lifting the fascia iliaca off the muscle and
wrapping both nerves; code colours it teal.

Markings: the probe, the needle from lateral (tip under the fascia iliaca,
lateral to the nerve), and the teal spread in the plane between fascia
iliaca and iliopsoas, lifting the fascia and reaching the femoral nerve
medially and the lateral femoral cutaneous nerve laterally.

Millimetres from the femoral artery centre (x lateral, y deep from the skin)
at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/ficb_anatomy_layers/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_anatomy_layers"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1195.0, 896.0)
PX_MM = 28.0
ORIGIN = (392.0, 130.0)           # canvas of the skin surface above the artery
X0, X1 = -16.0, 45.0              # frame edges in mm


def c(p):
    """mm (x lateral, y deep) -> canvas; lateral is drawn on the left."""
    return (1600 - (ORIGIN[0] + p[0] * PX_MM), ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=40):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom, x0=X0 - 3, x1=X1 + 3):
    return curve(top, x0, x1, 90) + list(reversed(curve(bottom, x0, x1, 90)))


PROBE = (-5.0, 33.0)                               # footprint, mm
PRESS_MM = 2.2                                     # the probe dents the skin this deep


def press(x):
    """Depth of the probe's dent at x: flat under the face, rounded at its ends."""
    x0, x1 = PROBE
    edge = 4.0
    if x <= x0 - edge or x >= x1 + edge:
        return 0.0
    if x0 + edge <= x <= x1 - edge:
        return PRESS_MM
    d = (x - (x0 - edge)) if x < x0 + edge else ((x1 + edge) - x)
    return PRESS_MM * (1 - math.cos(math.pi * min(d, 2 * edge) / (2 * edge))) / 2


def skin_y(x):
    return press(x)


def lata_y(x):
    return 7.8 - 0.035 * x + 0.5 * press(x)


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
NERVE = ((13.2, 15.8), 4.3, 1.5, 6.0)            # centre, rx, ry, rotation (deg): just under the fascia iliaca
LFCN = ((36.5, 18.2), 1.1)
SARTORIUS = [(31, 12.2), (36, 9.6), (42, 8.9), (X1 + 3, 9.0), (X1 + 3, 16.6), (40, 16.4), (34, 15.4)]
BONE_Y = 34.5
NEEDLE_OUT, NEEDLE_TIP = (43.2, -10.4), (21.5, 16.1)


def needle_entry():
    """Where the needle line meets the skin."""
    (xa, ya), (xb, yb) = NEEDLE_OUT, NEEDLE_TIP
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        x, y = xa + (xb - xa) * m, ya + (yb - ya) * m
        lo, hi = (m, hi) if y < skin_y(x) else (lo, m)
    return (xa + (xb - xa) * lo, ya + (yb - ya) * lo)


SPREAD_LATERAL = 39.0
SPREAD_MEDIAL = NERVE[0][0] - NERVE[1] - 0.7


def _hug(x, centre, rx, ry, pad=0.6):
    """Depth of the lower edge of an ellipse widened by `pad`, or 0 outside it."""
    (cx, cy), w = centre, rx + pad
    if abs(x - cx) >= w:
        return 0.0
    return cy + (ry + pad * 0.8) * math.sqrt(1 - ((x - cx) / w) ** 2)


def plane_floor(x):
    """The muscle surface under the opened fascial plane: the spread lifts the
    fascia iliaca off the iliopsoas, and both nerves lie in that plane."""
    lens = iliaca_y(x) + 0.5 + 2.6 * max(0.0, math.sin(math.pi * (SPREAD_LATERAL - x) / (SPREAD_LATERAL - SPREAD_MEDIAL))) ** 0.7
    return max(lens, _hug(x, NERVE[0], NERVE[1], NERVE[2]), _hug(x, LFCN[0], LFCN[1], LFCN[1], 0.5))


def spread():
    """The injectate: the opened plane between the fascia iliaca and the muscle."""
    n = 40
    xs = [SPREAD_LATERAL - (SPREAD_LATERAL - SPREAD_MEDIAL) * i / n for i in range(n + 1)]
    return [(x, iliaca_y(x) + 0.2) for x in xs] + [(x, plane_floor(x)) for x in reversed(xs)]


def muscle_top(x):
    if SPREAD_MEDIAL <= x <= SPREAD_LATERAL:
        return plane_floor(x)
    return iliaca_y(x) + 0.35


# Iliopsoas: its surface runs under the opened plane, then down its medial
# border beside the fascia iliaca, to the bone.
_TOP = [(x, muscle_top(x)) for x in [X1 + 3 - i * (X1 + 3 - SPREAD_MEDIAL) / 60 for i in range(61)]]
ILIOPSOAS = _TOP + [(6.9, 17.4), (5.4, 21.8), (4.0, 27.5), (3.4, BONE_Y - 0.4), (X1 + 3, BONE_Y - 0.4)]


def ellipse(center, rx, ry, attrs, rot=0.0):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'transform="rotate({fmt(-rot)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


def scatter(seed, x0, x1, y0, y1, step):
    """Jittered hex grid in mm, deterministic."""
    rng = random.Random(seed)
    out, row, y = [], 0, y0
    while y <= y1:
        x = x0 + (step / 2 if row % 2 else 0)
        while x <= x1:
            out.append((x + rng.uniform(-0.3, 0.3) * step, y + rng.uniform(-0.3, 0.3) * step, rng.random(), rng.random()))
            x += step
        y += step * 0.87
        row += 1
    return out


def fat_lobules(seed, y0, y1, colour_a, colour_b):
    parts = []
    for x, y, u, v in scatter(seed, X0 - 2, X1 + 2, y0, y1, 1.35):
        p = c((x, y))
        r = (0.56 + 0.18 * u) * PX_MM
        fill = colour_a if v < 0.5 else colour_b
        parts.append(f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(r)}" ry="{fmt(r * (0.8 + 0.3 * v))}" fill="{fill}"/>')
    return "".join(parts)


def fascicles(seed, x0, x1, y0, y1):
    """Cut muscle: flattened fascicle bundles overlapping like scales, each edged
    with a pale streak of perimysium; drawn row by row so each overlaps the last."""
    rng = random.Random(seed)
    shades = ("#7E1F1C", "#8C2622", "#701A18", "#962B25")
    parts, y, row = [], y0, 0
    while y <= y1:
        x = x0 - (1.6 if row % 2 else 0)
        while x <= x1:
            cx, cy = x + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.15, 0.15)
            p = c((cx, cy))
            rx, ry = rng.uniform(1.7, 2.5) * PX_MM, rng.uniform(0.55, 0.8) * PX_MM
            rot = rng.uniform(-12, 12)
            parts.append(f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx)}" ry="{fmt(ry)}" '
                         f'transform="rotate({fmt(rot)} {fmt(p[0])} {fmt(p[1])})" fill="{rng.choice(shades)}" '
                         f'stroke="#E8C4BC" stroke-width="2.2"/>')
            x += rng.uniform(2.9, 3.4)
        y += 1.05
        row += 1
    for _ in range(int((x1 - x0) * (y1 - y0) / 55)):
        vx, vy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        a, b = c((vx, vy)), c((vx - 0.42, vy))
        parts.append(f'<circle cx="{fmt(a[0])}" cy="{fmt(a[1])}" r="{fmt(0.24 * PX_MM)}" fill="#C8453A" stroke="#F1D6CF" stroke-width="1.5"/>'
                     f'<circle cx="{fmt(b[0])}" cy="{fmt(b[1])}" r="{fmt(0.22 * PX_MM)}" fill="#2F4A86" stroke="#D7DDEB" stroke-width="1.5"/>')
    return "".join(parts)


def nerve_bundle(center, rx, ry, rot, compartments, seed, clip_id):
    """A nerve cut across: a pale sheath round a few large fascicle compartments,
    each finely speckled, divided by thin pale septa."""
    rng = random.Random(seed)
    q = c(center)
    rot_c = -rot                                     # canvas rotation (the x axis is mirrored)
    inner_rx, inner_ry = (rx - 0.25) * PX_MM, (ry - 0.25) * PX_MM
    ell = (f'cx="{fmt(q[0])}" cy="{fmt(q[1])}" rx="{fmt(inner_rx)}" ry="{fmt(inner_ry)}" '
           f'transform="rotate({fmt(rot_c)} {fmt(q[0])} {fmt(q[1])})"')
    dots = "".join(
        f'<circle cx="{fmt(q[0] + rng.uniform(-inner_rx, inner_rx))}" cy="{fmt(q[1] + rng.uniform(-inner_ry, inner_ry) * 1.3)}" '
        f'r="{fmt(rng.uniform(1.4, 2.6))}"/>' for _ in range(int(inner_rx * inner_ry / 14)))
    septa = "".join(
        f'<line x1="{fmt(q[0] + (k / compartments - 0.5) * 2 * inner_rx + rng.uniform(-6, 6))}" y1="{fmt(q[1] - inner_ry * 1.4)}" '
        f'x2="{fmt(q[0] + (k / compartments - 0.5) * 2 * inner_rx + rng.uniform(-6, 6))}" y2="{fmt(q[1] + inner_ry * 1.4)}"/>'
        for k in range(1, compartments))
    return (f'<clipPath id="{clip_id}"><ellipse {ell}/></clipPath>'
            f'<ellipse {ell} fill="#B9AE4C"/>'
            f'<g clip-path="url(#{clip_id})" transform="rotate({fmt(rot_c)} {fmt(q[0])} {fmt(q[1])})">'
            f'<g fill="#8E8634" opacity="0.7">{dots}</g>'
            f'<g stroke="#F3ECCB" stroke-width="5">{septa}</g></g>')


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="deep-fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFD386"/><stop offset="1" stop-color="#E2BC5E"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery" cx="0.45" cy="0.4" r="0.65"><stop offset="0" stop-color="#8E1F1B"/><stop offset="1" stop-color="#5E1210"/></radialGradient>
<radialGradient id="vein" cx="0.45" cy="0.4" r="0.65"><stop offset="0" stop-color="#2E4A82"/><stop offset="1" stop-color="#1B2F5C"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
{clips}"""


def build() -> str:
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    skin = band(skin_y, lambda x: 60)
    below_skin = band(lambda x: skin_y(x) + 1.6, lambda x: 60)
    sub_fat = band(lambda x: skin_y(x) + 1.6, lata_y)
    below_lata = band(lata_y, lambda x: 60)
    bone = band(lambda x: BONE_Y, lambda x: 60)
    cancellous = band(lambda x: BONE_Y + 1.3, lambda x: 60)

    clips = "".join(f'<clipPath id="{k}"><path d="{d}"/></clipPath>' for k, d in (
        ("clip-sub-fat", path(sub_fat, closed=True, tension=0.3)),
        ("clip-deep-fat", path(below_lata, closed=True, tension=0.3)),
        ("clip-iliopsoas", path(ILIOPSOAS, closed=True, tension=0.5)),
        ("clip-sartorius", path(SARTORIUS, closed=True, tension=0.6)),
        ("clip-cancellous", path(cancellous, closed=True, tension=0.3))))

    rng = random.Random(7)
    speckle = "".join(
        f'<circle cx="{fmt(c((x, y))[0])}" cy="{fmt(c((x, y))[1])}" r="{fmt((0.25 + 0.35 * u) * PX_MM)}"/>'
        for x, y, u, _ in scatter(11, X0 - 2, X1 + 2, BONE_Y + 1.5, 45, 1.3))

    a, e, t = c(NEEDLE_OUT), c(needle_entry()), c(NEEDLE_TIP)
    px0, px1 = sorted((c((PROBE[0], 0))[0], c((PROBE[1], 0))[0]))
    art, (vc, vrx, vry) = ARTERY, VEIN

    labels = [
        Label(["Fascia iliaca"], anchor=(40, 300), leader=[(300, 322), c((29, iliaca_y(29)))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(620, 1010), leader=[(800, 955), c((13.2, 16.4))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(1150, 300), leader=[(1300, 322), c((0.5, 10.0))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(40, 1010), leader=[(250, 955), c((33, 26))], target_id="iliopsoas"),
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
  <path id="skin" d="{path(skin, closed=True, tension=0.3)}" fill="#E4B49B"/>
  <path d="{path(band(lambda x: skin_y(x) + 0.35, lambda x: 60), closed=True, tension=0.3)}" fill="#EDC7B2"/>
  <path id="subcutaneous-fat" d="{path(below_skin, closed=True, tension=0.3)}" fill="#C98E32"/>
  {'' if painted else f'''<g clip-path="url(#clip-sub-fat)">{fat_lobules(1, 1.0, 10.5, "#F2BE52", "#EAB044")}</g>'''}
  {'' if painted else f'''<g clip-path="url(#clip-deep-fat)">{fat_lobules(2, 6.5, 36, "#F0C560", "#E8B54C")}</g>'''}

  <path id="iliopsoas" d="{path(ILIOPSOAS, closed=True, tension=0.5)}" fill="#5E1715" stroke="#4A1210" stroke-width="3"/>
  {'' if painted else f'''<g clip-path="url(#clip-iliopsoas)">{fascicles(3, -2, X1 + 3, 13, 35)}</g>'''}
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" fill="#5E1715" stroke="#4A1210" stroke-width="3"/>
  {'' if painted else f'''<g clip-path="url(#clip-sartorius)">{fascicles(4, 28, X1 + 3, 8.5, 17)}</g>'''}

  <path id="bone" d="{path(bone, closed=True, tension=0.3)}" fill="#F4EEDF" stroke="#A8977A" stroke-width="5"/>
  <path d="{path(cancellous, closed=True, tension=0.3)}" fill="#E5D5B2"/>
  {'' if painted else f'''<g clip-path="url(#clip-cancellous)" fill="#CDB98E">{speckle}</g>'''}

  <path id="fascia-lata" d="{path(curve(lata_y))}" fill="none" stroke="#FBFAF6" stroke-width="10"/>
  <path d="{path(curve(lata_y))}" fill="none" stroke="#A89C86" stroke-width="2.5"/>
  <path id="opened-plane" d="{path(spread(), closed=True, tension=0.5)}" fill="#EDEFEA" stroke="#D7D2C4" stroke-width="2"/>
  <path id="muscle-surface" d="{path(_TOP[:-1] + [(6.9, 17.4), (5.4, 21.8), (4.0, 27.5), (3.4, BONE_Y - 0.4)], tension=0.6)}" fill="none" stroke="#EBD9CF" stroke-width="5"/>
  <path id="fascia-iliaca" d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#FBFAF6" stroke-width="11"/>
  <path d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#A89C86" stroke-width="2.5"/>

  {ellipse(NERVE[0], NERVE[1], NERVE[2], 'id="femoral-nerve" fill="#F4DC92" stroke="#B8962E" stroke-width="4"', NERVE[3])}
  {'' if painted else nerve_bundle(NERVE[0], NERVE[1], NERVE[2], NERVE[3], 4, 5, "clip-fn")}
  {ellipse(LFCN[0], LFCN[1], LFCN[1], 'id="lfcn" fill="#F4DC92" stroke="#B8962E" stroke-width="3"')}
  {'' if painted else nerve_bundle(LFCN[0], LFCN[1], LFCN[1], 0, 2, 6, "clip-lfcn")}
  {ellipse(vc, vrx, vry, 'id="femoral-vein" fill="#5B79AC" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(vc, vrx - 0.7, vry - 0.7, 'fill="url(#vein)"')}
  {ellipse(art[0], art[1], art[1], 'id="femoral-artery" fill="#C95A4F" stroke="#8E211D" stroke-width="5"')}
  {ellipse(art[0], art[1] - 1.5, art[1] - 1.5, 'fill="url(#artery)" stroke="#9E2A24" stroke-width="3"')}
  <path d="{path(curve(skin_y, n=80))}" fill="none" stroke="#B98A74" stroke-width="4"/>
  <rect id="probe" x="{fmt(px0)}" y="{fmt(ORIGIN[1] + PRESS_MM * PX_MM - 150)}" width="{fmt(px1 - px0)}" height="150" rx="26" fill="#8A929B"/>
  </g>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#6CCBD2" fill-opacity="0.72" stroke="#0E8C98" stroke-width="4"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10" stroke-linecap="butt"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5" stroke-linecap="butt"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS.replace("{clips}", clips), extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
