"""Radial nerve block - the right mid-forearm in section under a linear probe (layout).

Transverse section of the right forearm, palm up, seen from the hand as on
the screen: radial (lateral, the thumb side) on the image left, ulnar on the
right, the volar skin at the top - the same way round as the median nerve
plates. Composition informed by NYSORA's reverse-ultrasound plate of the
superficial radial nerve at the mid-forearm (concept only, not committed),
mirrored to the house laterality; drawn from scratch.

Record: in the mid-forearm the radial nerve lies directly lateral to the
radial artery, in the same fascial plane; needle in-plane; 5-7 mL around the
nerve, circumferentially.

Standard adult anatomy added: brachioradialis over the nerve and artery,
extensor carpi radialis laterally, flexor carpi radialis medially, pronator
teres and flexor pollicis longus deep, the radius deep and lateral. The
nerve about 1 cm deep. The needle comes in-plane from the lateral (radial)
end, as in NYSORA, so the artery stays beyond the nerve.

Millimetres from the skin over the nerve (x toward the ulna = image right,
y deep) at 30 px/mm.

Run: python3 visuals/radial_nerve_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "radial_nerve_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 30.0
ORIGIN = (760.0, 110.0)
X0, X1 = -25.3, 28.0
L, R = X0 - 3, X1 + 3


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


PLANE_Y = 10.4
BR = [(-15.6, 4.0), (8.6, 4.0), (9.6, 6.6), (6.6, 9.2), (2.0, 9.2), (-6, 9.2), (-12.6, 9.6), (-15.4, 7.6)]
ECR = [(L, 4.0), (-15.8, 4.0), (-15.8, 8.0), (-13.0, 10.2), (-11.6, 14.6), (-12.6, 19.6), (L, 21.0)]
FCR = [(9.0, 4.0), (R, 4.0), (R, 15.4), (20, 14.6), (13, 12.6), (9.4, 11.6), (8.6, 9.0), (10.0, 6.6)]
PT = [(-12.6, 11.2), (-4, 11.6), (3, 11.6), (9.0, 12.0), (13, 13.2), (20, 15.4), (R, 16.2), (R, 22.0), (14, 21.6),
      (4, 21.2), (-6, 21.0), (-10.6, 20.2), (-11.2, 15.4)]
FPL = [(-10.0, 21.4), (2, 21.6), (14, 22.0), (R, 22.4), (R, 40), (-6, 40), (-8.6, 30.0)]
RADIUS = ((-17.4, 27.6), 8.4, 6.8)
NERVE = ((0.0, PLANE_Y), 2.4, 1.1)
ARTERY = ((6.4, PLANE_Y), 1.4)
VC = [((4.4, PLANE_Y + 0.6), 0.6), ((8.4, PLANE_Y + 0.6), 0.6)]
PROBE_LATERAL_X = X0 + 10.0
NEEDLE_ENTRY = (X0 + 5.0, 0.0)
NEEDLE_TIP = (-2.8, PLANE_Y + 0.4)


def spread():
    top = [(-5.6, 10.6), (-3, 8.8), (0, 8.6), (3, 9.0), (4.4, 10.2)]
    bottom = [(4.0, 11.6), (2, 12.2), (-1, 12.3), (-4, 12.0), (-5.6, 11.2)]
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
    a = (e[0] - dx * 0.4, e[1] - dy * 0.4)
    probe_x = c((PROBE_LATERAL_X, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"'
    labels = [
        Label(["Radial nerve"], anchor=(560, 640), leader=[(700, 600), c((0.6, PLANE_Y + 0.6))], target_id="radial-nerve", emphasis=True),
        Label(["Radial artery"], anchor=(1110, 600), leader=[(1130, 560), c((7.2, PLANE_Y + 0.4))], target_id="radial-artery"),
        Label(["Brachioradialis"], anchor=(980, 250), leader=[(990, 270), c((3, 6.4))], target_id="brachioradialis"),
        Label(["Pronator teres"], anchor=(1080, 860), leader=[(1100, 820), c((10, 18.0))], target_id="pronator-teres"),
        Label(["Radius"], anchor=(40, 1150), leader=[(150, 1100), c((-17.4, 27))], target_id="radius"),
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
  <path id="skin" d="{path(band(0, 60), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(1.5, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="deep-compartment" d="{path(band(4.0, 60), closed=True, tension=0.2)}" fill="#9A3530"/>
  <path id="investing-fascia" d="{path(band(3.6, 4.0), closed=True, tension=0.2)}" fill="#F4EFE6"/>
  <path id="np-plane" d="{path([(-12.6, 9.4), (-4, 9.2), (4, 9.2), (9.0, 9.6), (9.0, 11.8), (4, 11.6), (-4, 11.6), (-12.6, 11.2)], closed=True, tension=0.5)}" fill="url(#fat)"/>
  <path id="fpl" d="{path(FPL, closed=True, tension=0.5)}" {M}/>
  <path id="pronator-teres" d="{path(PT, closed=True, tension=0.5)}" {M}/>
  {ell("radius", RADIUS, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="6"')}
  <path id="ecr" d="{path(ECR, closed=True, tension=0.5)}" {M}/>
  <path id="fcr" d="{path(FCR, closed=True, tension=0.5)}" {M}/>
  <path id="brachioradialis" d="{path(BR, closed=True, tension=0.5)}" {M}/>
  {ell("radial-nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  {ell("radial-artery", ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="5"')}
  {"".join(ell(f"vc-{i}", v, 'fill="#5876B0" stroke="#34528A" stroke-width="2"') for i, v in enumerate(VC))}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="3"/>
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
