"""Fascia iliaca block - the right groin in section under a linear probe.

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

Run: python3 visuals/ficb_anatomy_layers/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_anatomy_layers"
PX_MM = 28.0
ORIGIN = (392.0, 130.0)           # canvas of the skin surface above the artery
X0, X1 = -16.0, 45.0              # frame edges in mm


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


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
    below_skin = band(lambda x: 1.6, lambda x: 60)
    below_lata = band(lata_y, lambda x: 60)
    skin = band(skin_y, lambda x: 60)
    bone = band(lambda x: BONE_Y, lambda x: 60)

    a, e, t = c(NEEDLE_OUT), c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    p0, p1 = c((PROBE[0], 0)), c((PROBE[1], 0))

    labels = [
        Label(["Fascia iliaca"], anchor=(1010, 250), leader=[(1150, 272), c((26, iliaca_y(26)))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(430, 1000), leader=[(620, 945), c((13.0, 16.4))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(40, 250), leader=[(260, 272), c((-1.5, 12.5))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(1150, 1000), leader=[(1250, 945), c((31, 26))], target_id="iliopsoas"),
    ]

    body = f"""
<g id="anatomy" clip-path="url(#frame)">
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

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#7FD3D8" fill-opacity="0.8" stroke="#0E8C98" stroke-width="4"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1] - 150)}" width="{fmt(p1[0] - p0[0])}" height="150" rx="26" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(p0[0] + 10)}" y="{fmt(p0[1] - 14)}" width="{fmt(p1[0] - p0[0] - 20)}" height="12" rx="5" fill="#3E454C"/>
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
