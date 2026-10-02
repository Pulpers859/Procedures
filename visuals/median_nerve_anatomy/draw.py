"""Median nerve block - the right mid-forearm in section under a linear probe (layout).

Transverse section of the right forearm, palm up, seen from the hand as on
ultrasound: radial (lateral, the thumb side) on the image left, ulnar on the
right, the volar skin at the top under the probe. Composition informed by
NYSORA's reverse-ultrasound plate of the mid-forearm (concept only, not
committed), mirrored to the house laterality; drawn from scratch.

Record: in the mid-forearm the median nerve lies between the FDS and FDP
bellies; needle in-plane, aimed at the nerve's deep border; 5-10 mL spreads
in the fascial plane around the nerve.

Standard adult anatomy added: brachioradialis with the radial artery under
its edge, FCR and palmaris longus superficially, FCU with the ulnar artery
and nerve on the ulnar side, FPL deep on the radial side, the radius and
ulna with the interosseous membrane. The nerve about 15 mm deep.

Millimetres from the skin over the nerve (x toward the ulna = image right,
y deep) at 28 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/median_nerve_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "median_nerve_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 34.0
ORIGIN = (816.0, 120.0)            # canvas of the skin over the nerve
X0, X1 = -24.0, 23.06              # frame edges in mm


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [X0 - 3 + (X1 - X0 + 6) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


L, R = X0 - 3, X1 + 3
FASCIA_Y = 4.6
# The FDS deep border (the nerve's plane), ulnar to radial.
PLANE = [(R, 13.6), (18, 13.4), (12, 13.8), (5, 13.3), (0, 13.1), (-5, 13.4), (-12, 14.2), (-18, 15.0), (L, 15.6)]
# The deep muscles' top border, radial to ulnar, opening a lens around the nerve.
DEEP_TOP = [(L, 15.8), (-18, 15.2), (-12, 14.4), (-5.4, 13.7), (-3.2, 15.7), (0, 16.4), (3.2, 15.6), (5.2, 13.6),
            (12, 14.0), (18, 13.6), (R, 13.8)]
FDS = [(L, FASCIA_Y), (R, FASCIA_Y)] + PLANE
DEEP = DEEP_TOP + [(R, 45), (L, 45)]
FPL = [(L, 15.8), (-18, 15.2), (-12, 14.4), (-5.4, 13.7), (-3.4, 16.4), (-4.2, 20.6), (-6.6, 24.2), (-11, 25.0),
       (-17, 24.4), (L, 24.0)]
BR = [(L, FASCIA_Y), (-21.2, FASCIA_Y), (-20.4, 8.4), (-21.6, 12.4), (-23.0, 15.4), (L, 15.8)]
FCR = [(-21.2, FASCIA_Y), (-9.2, FASCIA_Y), (-8.0, 7.2), (-10.6, 9.8), (-16.4, 10.4), (-20.4, 8.4)]
FCU = [(12.0, FASCIA_Y), (R, FASCIA_Y), (R, 12.2), (19.6, 12.6), (14.6, 10.8), (11.6, 7.6)]
TENDONS = [((-11.0, 11.2), 1.8, 1.0), ((6.4, 9.6), 2.0, 1.1), ((-13.6, 20.4), 2.2, 1.2)]
PL = ((-2.0, 5.8), 2.2, 1.0)
RADIUS = ((-15.0, 30.0), 7.2, 4.6)
ULNA = ((16.0, 31.4), 6.2, 4.2)
MEMBRANE = [(-8.0, 29.6), (1, 29.4), (10.0, 30.6)]
NERVE = ((0.0, 14.7), 3.0, 1.5)
RADIAL_A = ((-21.6, 10.4), 1.2)
ULNAR_A = ((13.6, 14.4), 1.15)
ULNAR_N = ((16.8, 14.5), 1.4, 1.0)
PROBE_RADIAL_X = X0 + 10.0         # the probe stops 1 cm short of the radial edge
NEEDLE_ENTRY = (X0 + 5.0, 0.0)
NEEDLE_TIP = (-2.2, 16.2)          # at the nerve's deep radial border


def spread():
    """Teal lens of injectate in the FDS-FDP plane, wrapping the nerve."""
    top = [(-7.0, 13.9), (-4.0, 13.3), (0, 13.0), (4.0, 13.2), (7.0, 13.7)]
    bottom = [(6.6, 14.7), (3.4, 16.4), (0, 17.0), (-3.6, 16.7), (-6.6, 14.9)]
    return top + bottom


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    ry = e[2] if len(e) > 2 else e[1]
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.45, e[1] - dy * 0.45)
    probe_x = c((PROBE_RADIAL_X, 0))[0]
    labels = [
        Label(["Median nerve"], anchor=(560, 1150), leader=[(700, 1100), c((0.4, 15.2))], target_id="median-nerve", emphasis=True),
        Label(["FDS"], anchor=(1060, 232), leader=[(1090, 246), c((2.2, 10.8))], target_id="fds"),
        Label(["FDP"], anchor=(1300, 1150), leader=[(1330, 1100), c((12, 22))], target_id="fdp"),
        Label(["FPL"], anchor=(40, 900), leader=[(110, 858), c((-17, 19))], target_id="fpl"),
        Label(["Radial artery"], anchor=(30, 330), leader=[(120, 348), c((-21.6, 10.0))], target_id="radial-artery"),
    ]
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
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
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 50), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(1.5, 50), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="plane-tissue" d="{path(band(FASCIA_Y, 50), closed=True, tension=0.2)}" fill="#F1E2B8"/>
  <path id="fdp" d="{path(DEEP, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  <path id="fpl" d="{path(FPL, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  <path id="fds" d="{path(FDS, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  <path id="br" d="{path(BR, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  <path id="fcr" d="{path(FCR, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  <path id="fcu" d="{path(FCU, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"/>
  {"".join(ell(f"tendon-{k}", t, 'fill="#F1EDE4" stroke="#B9B2A4" stroke-width="3"') for k, t in enumerate(TENDONS))}
  {ell("pl", PL, 'fill="#F1EDE4" stroke="#B9B2A4" stroke-width="3"')}
  <path id="interosseous-membrane" d="{path(MEMBRANE, tension=0.8)}" fill="none" stroke="#F4EFE6" stroke-width="8"/>
  {ell("radius", RADIUS, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="6"')}
  {ell("ulna", ULNA, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="6"')}
  {ell("median-nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  {ell("radial-artery", RADIAL_A, 'fill="url(#artery)" stroke="#8E211D" stroke-width="4"')}
  {ell("ulnar-artery", ULNAR_A, 'fill="url(#artery)" stroke="#8E211D" stroke-width="4"')}
  {ell("ulnar-nerve", ULNAR_N, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.8" stroke="#0E8C98" stroke-width="3"/>
  {ell("nerve-outline", NERVE, 'fill="none" stroke="#B8962E" stroke-width="4"')}
  <rect id="probe" x="{fmt(probe_x)}" y="-60" width="{fmt(1700 - probe_x)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(probe_x + 18)}" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(1700 - probe_x)}" height="14" rx="6" fill="#3E454C"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="4" fill="#000" opacity="0"/>
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
