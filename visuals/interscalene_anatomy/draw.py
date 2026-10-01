"""Interscalene block - the right neck in section under a linear probe (layout).

Transverse section at the interscalene level (C6), seen from the feet as on
ultrasound: lateral (posterior neck) on the image left, medial (the carotid)
on the right, skin at the top. Composition after NYSORA's reverse-ultrasound
plate (concept only, not committed), mirrored to the house laterality; drawn
from scratch.

Record: C5-C7 roots stacked between the anterior and middle scalenes (the
'stoplight'); the phrenic nerve runs over the anterior scalene; the carotid
and internal jugular lie medial to it. Needle in-plane from posterior to
anterior (lateral to medial) through the middle scalene, tip in the
interscalene groove; spread around C5-C7.

Standard adult anatomy added: sternocleidomastoid over the groove and the
vessels, the deep cervical fascia over the scalenes, the vertebral artery
deep and medial, the C7 transverse process deep. Depths: the plexus at
1-3 cm (NYSORA tips).

Millimetres from the interscalene groove (x lateral, y deep from the skin)
at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/interscalene_anatomy/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "interscalene_anatomy"
PX_MM = 28.0
ORIGIN = (800.0, 130.0)           # canvas of the skin over the groove (before the mirror)
X0, X1 = -28.6, 28.6


def c(p):
    """mm (x lateral, y deep) -> canvas; lateral is drawn on the left."""
    return (1600 - (ORIGIN[0] + p[0] * PX_MM), ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=40):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom):
    return curve(top) + list(reversed(curve(bottom)))


SCM = [(4.0, 3.8), (-4, 3.6), (-14, 3.6), (-26, 4.0), (X0 - 3, 4.2), (X0 - 3, 12.6), (-24, 12.4), (-16, 10.6),
       (-8, 8.0), (-1, 5.6)]
FASCIA = [(X1 + 3, 7.0), (20, 7.2), (10, 7.6), (3, 8.0), (-3, 7.8), (-10, 8.4), (-16, 10.8)]
ASM = [(-3.6, 9.2), (-8, 8.8), (-13.6, 10.6), (-16.6, 15), (-16.2, 21), (-12, 25.6), (-6.4, 26.2), (-4.4, 22),
       (-3.8, 15)]
MSM = [(3.4, 8.6), (10, 8.0), (20, 7.9), (X1 + 3, 8.2), (X1 + 3, 31), (20, 31.5), (10, 29.6), (4.8, 26),
       (3.2, 18)]
ROOTS = {"c5": ((0.6, 11.0), 1.6), "c6": ((0.2, 15.0), 2.0), "c7": ((0.0, 20.6), 2.4)}
PHRENIC = ((-9.6, 7.7), 0.9)
CAROTID = ((-24.6, 17.8), 3.6)
IJV = ((-19.6, 13.6), 5.0, 3.0)
VERTEBRAL = ((-8.6, 30.0), 2.0)
BONE = [(-4, 31), (2, 28.6), (10, 30.6), (16, 33.6), (18, 40), (-6, 40), (-6.6, 34)]
PROBE_LATERAL_X = X1 - 10.0                       # the probe ends 1 cm short of the lateral edge
NEEDLE_ENTRY = (26.0, 0.0)
NEEDLE_TIP = (2.7, 17.6)                          # in the groove, lateral to the roots, between C6 and C7


def ellipse(center, rx, ry, attrs, rot=0.0):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'transform="rotate({fmt(rot)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


def spread():
    """Teal sheath of injectate in the groove, wrapping C5-C7 between the
    scalenes, rounded at both ends."""
    right = [(-2.4, 9.4), (-2.8, 13), (-3.0, 17.4), (-3.2, 21), (-3.0, 23.8)]
    left = [(3.0, 24.0), (3.0, 20.6), (2.9, 17.0), (2.6, 13.0), (2.2, 9.4)]
    return [(0, 8.4)] + right + [(-0.2, 24.8)] + left


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    a, e, t = None, c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.45, e[1] - dy * 0.45)
    probe_x = c((PROBE_LATERAL_X, 0))[0]
    labels = [
        Label(["Middle scalene"], anchor=(40, 1060), leader=[(200, 1010), c((14, 22))], target_id="msm"),
        Label(["C5-C7 roots"], anchor=(720, 1150), leader=[(800, 1100), c((0.0, 20.6))], target_id="c7", emphasis=True),
        Label(["Anterior scalene"], anchor=(1040, 1060), leader=[(1150, 1010), c((-10, 20))], target_id="asm"),
        Label(["Phrenic nerve"], anchor=(1060, 440), leader=[(1150, 400), c((-9.6, 7.7))], target_id="phrenic"),
        Label(["Carotid"], anchor=(1330, 1150), leader=[(1420, 1100), c((-24.6, 20.0))], target_id="carotid"),
    ]
    roots = "".join(ellipse(ct, r, r * 0.92, f'id="{k}" fill="#EFCB5A" stroke="#B8962E" stroke-width="4"') for k, (ct, r) in ROOTS.items())
    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="skin" d="{path(band(lambda x: 0, lambda x: 60), closed=True, tension=0.3)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(lambda x: 1.6, lambda x: 60), closed=True, tension=0.3)}" fill="url(#fat)"/>
  <path id="bone" d="{path(BONE, closed=True, tension=0.6)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="msm" d="{path(MSM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="asm" d="{path(ASM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="scm" d="{path(SCM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="cervical-fascia" d="{path(FASCIA, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="8"/>
  {roots}
  {ellipse(PHRENIC[0], PHRENIC[1], PHRENIC[1], 'id="phrenic" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ellipse(IJV[0], IJV[1], IJV[2], 'id="ijv" fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(CAROTID[0], CAROTID[1], CAROTID[1], 'id="carotid" fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  {ellipse(VERTEBRAL[0], VERTEBRAL[1], VERTEBRAL[1], 'id="vertebral" fill="url(#artery)" stroke="#8E211D" stroke-width="4"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="3"/>
  <rect id="probe" x="{fmt(probe_x)}" y="-60" width="{fmt(1700 - probe_x)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(probe_x + 18)}" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(1700 - probe_x)}" height="14" rx="6" fill="#3E454C"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5"/>
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
