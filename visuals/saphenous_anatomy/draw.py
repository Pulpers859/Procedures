"""Saphenous nerve (adductor canal) block - the right mid-thigh in section under a linear probe (layout).

Transverse section of the right thigh at the adductor canal, as on the
screen with the probe on the medial thigh: lateral (vastus medialis) on the
image left, medial/posterior (adductor longus) on the right, skin at the top.
Composition after NYSORA's adductor canal reverse-ultrasound plate (concept
only, not committed); drawn from scratch.

Record: in the adductor canal the saphenous nerve travels with the
superficial femoral artery, deep to the sartorius; inject into the fascial
plane around the artery. Needle in-plane, lateral to medial (or anterior to
posterior). Steps: the nerve often appears anterior/lateral to the artery.

Standard adult anatomy added: sartorius as the canal's roof, vastus medialis
laterally, adductor longus medially and deep, the femoral vein deep to the
artery. The artery about 2.5 cm deep.

Millimetres from the skin over the artery (x medial = image right, y deep)
at 26 px/mm.

Run: python3 visuals/saphenous_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "saphenous_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (800.0, 110.0)
X0, X1 = -30.8, 30.8
L, R = X0 - 3, X1 + 3


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


SARTORIUS = [(-22, 9.0), (-10, 7.0), (4, 6.6), (18, 8.0), (26, 11.0), (20, 15.6), (8, 18.4), (-6, 18.6), (-18, 15.0)]
VMM = [(L, 9.0), (-23, 9.4), (-19, 15.6), (-8, 19.6), (-4, 21.6), (-2, 27.0), (-6, 34.0), (-10, 60), (L, 60)]
ALM = [(R, 12.0), (26.6, 12.0), (22, 16.6), (12, 20.4), (6, 22.0), (2.8, 26.8), (3.6, 33.0), (6, 60), (R, 60)]
CANAL = [(-7, 19.6), (8, 18.6), (11, 20.4), (5, 22.4), (2.6, 27.0), (3.4, 32.0), (-0.6, 32.6), (-2.6, 27.0), (-4.6, 21.8)]
ARTERY = ((3.0, 23.2), 2.6)
VEIN = ((1.0, 28.8), 2.6, 1.9)
NERVE = ((-2.2, 21.2), 1.3, 0.9)
FAT_Y = 6.0
NEEDLE_ENTRY = (X0 + 4.6, 0.0)
NEEDLE_TIP = (-3.8, 21.6)


def spread():
    return [(-5.4, 20.4), (-3.0, 19.6), (0.2, 19.6), (1.2, 20.8), (0.6, 22.6), (-0.4, 24.4), (-2.0, 24.2), (-4.0, 22.8), (-5.6, 21.6)]


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
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
    probe_x0 = c((X0 + 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"'
    labels = [
        Label(["Sartorius"], anchor=(1060, 300), leader=[(1080, 320), c((12, 10))], target_id="sartorius"),
        Label(["Saphenous nerve"], anchor=(40, 1060), leader=[(300, 1010), c((-2.6, 21.6))], target_id="saphenous-nerve", emphasis=True),
        Label(["Femoral artery"], anchor=(1100, 660), leader=[(1110, 620), c((5.2, 23.4))], target_id="femoral-artery"),
        Label(["Femoral vein"], anchor=(1100, 920), leader=[(1110, 880), c((3.2, 29.2))], target_id="femoral-vein"),
        Label(["Vastus medialis"], anchor=(40, 760), leader=[(465, 745), c((-12, 28))], target_id="vmm"),
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
  <path id="subcutaneous-fat" d="{path(band(1.6, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="deep-compartment" d="{path(band(FAT_Y + 3, 60), closed=True, tension=0.2)}" fill="#9A3530"/>
  <path id="vmm" d="{path(VMM, closed=True, tension=0.5)}" {M}/>
  <path id="alm" d="{path(ALM, closed=True, tension=0.5)}" {M}/>
  <path id="canal" d="{path(CANAL, closed=True, tension=0.5)}" fill="url(#fat)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" {M}/>
  {ell("femoral-vein", VEIN, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("femoral-artery", ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  {ell("saphenous-nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="3"/>
  {ell("nerve-outline", NERVE, 'fill="none" stroke="#B8962E" stroke-width="3"')}
  <rect id="probe" x="{fmt(probe_x0)}" y="-60" width="{fmt(1700 - probe_x0)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(probe_x0 + 18)}" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(1700 - probe_x0)}" height="14" rx="6" fill="#3E454C"/>
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
