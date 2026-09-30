"""Fascia iliaca block - the right groin in section under a linear probe.

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
as cut fascicles, fat as small lobules, nerves as fascicle bundles in their
sheath, vessels as walls round a lumen, bone as cortex over cancellous bone. Superficial to deep
(record subtitle): skin, subcutaneous fat, fascia lata, fascia iliaca, then
iliopsoas, with bone at the bottom. The femoral vein and artery lie
superficial to the fascia iliaca, vein medial. The femoral nerve lies deep to
the fascia iliaca, lateral to the artery; the fascia turns down along the
muscle's medial border, deep and lateral to the artery. Sartorius sits
laterally under the fascia lata; the lateral femoral cutaneous nerve lies
deep to the fascia iliaca near it (record: the spread reaches both nerves).

A plain probe is in the painted layer too, so the strip above the skin is
not an empty margin (an empty strip made Gemini frame the picture); code
draws the exact probe over it. Markings: the probe, the needle from lateral (tip under the fascia iliaca,
lateral to the nerve), and the teal spread in the plane between fascia
iliaca and iliopsoas, lifting the fascia and reaching the femoral nerve
medially and the lateral femoral cutaneous nerve laterally.

Millimetres from the femoral artery centre (x lateral, y deep from the skin)
at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/ficb_anatomy_layers/draw.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_anatomy_layers"
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
ILIOPSOAS = ([(x, y + 0.35) for x, y in ILIACA[:8]] + [(5.4, 21.8), (4.0, 27.5), (3.4, BONE_Y - 0.4)]
             + [(X1 + 3, BONE_Y - 0.4)])
PROBE = (-5.0, 33.0)                               # footprint, mm
NEEDLE_OUT, NEEDLE_ENTRY, NEEDLE_TIP = (43.2, -10.4), (34.6, 0.0), (21.5, 16.1)


def spread():
    """Lens under the fascia from the lateral nerve to just over the femoral nerve."""
    xs = [39 - i * 1.5 for i in range(21)]          # 39 .. 9
    top = [(x, iliaca_y(x) + 0.2) for x in xs]
    bottom = [(x, iliaca_y(x) + 0.5 + 3.4 * math.sin(math.pi * (39 - x) / 30) ** 0.7) for x in reversed(xs)]
    return top + bottom


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
    parts = []
    for x, y, u, v in scatter(seed, x0, x1, y0, y1, 1.15):
        p = c((x, y))
        rx, ry = (0.56 + 0.14 * u) * PX_MM, (0.46 + 0.14 * v) * PX_MM
        parts.append(f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx)}" ry="{fmt(ry)}" '
                     f'transform="rotate({fmt(u * 180)} {fmt(p[0])} {fmt(p[1])})"/>')
    return "".join(parts)


def nerve_bundle(center, rx, ry, rot, r, seed):
    """Fascicles (radius r mm) packed on a hex grid inside a nerve's sheath."""
    rng = random.Random(seed)
    a = math.radians(-rot)
    out, step = [], 2.15 * r
    ly = -ry
    row = 0
    while ly <= ry:
        lx = -rx + (step / 2 if row % 2 else 0)
        while lx <= rx:
            if (lx / (rx - r * 1.15)) ** 2 + (ly / max(ry - r * 1.15, 0.01)) ** 2 <= 1.0 if ry > r * 1.2 else abs(ly) < 0.01 and abs(lx) <= rx - r * 1.2:
                jx, jy = lx + rng.uniform(-0.08, 0.08), ly + rng.uniform(-0.08, 0.08)
                px, py = center[0] + jx * math.cos(a) - jy * math.sin(a), center[1] + jx * math.sin(a) + jy * math.cos(a)
                q = c((px, py))
                out.append(f'<circle cx="{fmt(q[0])}" cy="{fmt(q[1])}" r="{fmt(r * rng.uniform(0.85, 1.0) * PX_MM)}" '
                           f'fill="#D9A93A" stroke="#B8862A" stroke-width="2"/>')
            lx += step
        ly += step * 0.87
        row += 1
    return "".join(out)


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
    skin = band(skin_y, lambda x: 60)
    below_skin = band(lambda x: 1.6, lambda x: 60)
    sub_fat = band(lambda x: 1.6, lata_y)
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

    a, e, t = c(NEEDLE_OUT), c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    px0, px1 = sorted((c((PROBE[0], 0))[0], c((PROBE[1], 0))[0]))
    art, (vc, vrx, vry) = ARTERY, VEIN

    labels = [
        Label(["Fascia iliaca"], anchor=(40, 300), leader=[(300, 322), c((29, iliaca_y(29)))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(620, 1010), leader=[(800, 955), c((13.2, 16.4))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(1150, 300), leader=[(1300, 322), c((0.5, 10.0))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(40, 1010), leader=[(250, 955), c((33, 26))], target_id="iliopsoas"),
    ]

    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="skin" d="{path(skin, closed=True, tension=0.3)}" fill="#E4B49B"/>
  <path d="{path(band(lambda x: 0.35, lambda x: 60), closed=True, tension=0.3)}" fill="#EDC7B2"/>
  <path id="subcutaneous-fat" d="{path(below_skin, closed=True, tension=0.3)}" fill="#E2B955"/>
  <g clip-path="url(#clip-sub-fat)">{fat_lobules(1, 1.0, 10.5, "#F6DD8E", "#F1D27A")}</g>
  <g clip-path="url(#clip-deep-fat)">{fat_lobules(2, 6.5, 36, "#F2D787", "#ECCB72")}</g>

  <path id="iliopsoas" d="{path(ILIOPSOAS, closed=True, tension=0.5)}" fill="#E9B8AD" stroke="#6E221E" stroke-width="3"/>
  <g clip-path="url(#clip-iliopsoas)" fill="#A63A31">{fascicles(3, -2, X1 + 3, 12, 36)}</g>
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" fill="#E9B8AD" stroke="#6E221E" stroke-width="3"/>
  <g clip-path="url(#clip-sartorius)" fill="#A63A31">{fascicles(4, 28, X1 + 3, 7, 18)}</g>

  <path id="bone" d="{path(bone, closed=True, tension=0.3)}" fill="#F4EEDF" stroke="#A8977A" stroke-width="5"/>
  <path d="{path(cancellous, closed=True, tension=0.3)}" fill="#E5D5B2"/>
  <g clip-path="url(#clip-cancellous)" fill="#CDB98E">{speckle}</g>

  <path id="fascia-lata" d="{path(curve(lata_y))}" fill="none" stroke="#FBFAF6" stroke-width="10"/>
  <path d="{path(curve(lata_y))}" fill="none" stroke="#A89C86" stroke-width="2.5"/>
  <path id="fascia-iliaca" d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#FBFAF6" stroke-width="11"/>
  <path d="{path(ILIACA, tension=0.8)}" fill="none" stroke="#A89C86" stroke-width="2.5"/>

  {ellipse(NERVE[0], NERVE[1], NERVE[2], 'id="femoral-nerve" fill="#F4DC92" stroke="#B8962E" stroke-width="4"', NERVE[3])}
  {nerve_bundle(NERVE[0], NERVE[1], NERVE[2], NERVE[3], 0.5, 5)}
  {ellipse(LFCN[0], LFCN[1], LFCN[1], 'id="lfcn" fill="#F4DC92" stroke="#B8962E" stroke-width="3"')}
  {nerve_bundle(LFCN[0], LFCN[1], LFCN[1], 0, 0.36, 6)}
  {ellipse(vc, vrx, vry, 'id="femoral-vein" fill="#5B79AC" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(vc, vrx - 0.7, vry - 0.7, 'fill="url(#vein)"')}
  {ellipse(art[0], art[1], art[1], 'id="femoral-artery" fill="#C95A4F" stroke="#8E211D" stroke-width="5"')}
  {ellipse(art[0], art[1] - 1.5, art[1] - 1.5, 'fill="url(#artery)" stroke="#9E2A24" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
  <rect x="{fmt(px0)}" y="{fmt(ORIGIN[1] - 150)}" width="{fmt(px1 - px0)}" height="150" rx="26" fill="#8A929B"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#7FD3D8" fill-opacity="0.8" stroke="#0E8C98" stroke-width="4"/>
  <rect id="probe" x="{fmt(px0)}" y="{fmt(ORIGIN[1] - 150)}" width="{fmt(px1 - px0)}" height="150" rx="26" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(px0 + 10)}" y="{fmt(ORIGIN[1] - 14)}" width="{fmt(px1 - px0 - 20)}" height="12" rx="5" fill="#3E454C"/>
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
