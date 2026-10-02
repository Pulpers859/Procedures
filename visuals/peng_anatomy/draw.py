"""PENG block - the right hip in section under a linear probe (layout).

Transverse-oblique section at the AIIS / iliopubic eminence level, seen from
the feet as on ultrasound: lateral (the AIIS) on the image left, medial (the
femoral vessels) on the right, skin at the top. Composition after NYSORA's
sonoanatomy figure (concept only, not committed), mirrored to the house
laterality; drawn from scratch. The same way round as the positioning plate.

Record: the articular branches run between the psoas muscle and tendon and
the iliopubic eminence; the needle tip rests on the bony contour of the
eminence, deep to the psoas tendon; the femoral vessels are medial; needle
in-plane from lateral to medial; 20-30 mL.

Standard adult anatomy added: the bony contour from the AIIS down into the
iliopsoas groove and up onto the eminence, then the superior pubic ramus;
iliopsoas over the groove with the psoas tendon in its deep part; sartorius
superficial and lateral; the femoral nerve on the iliopsoas under the fascia
iliaca, lateral to the artery; artery then vein medially; pectineus deep
and medial. Bone about 3-3.5 cm deep.

Millimetres from the skin over the groove (x medial = image right, y deep)
at 24 px/mm. Adult proportions; depths vary with habitus.

Run: python3 visuals/peng_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "peng_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 24.0
ORIGIN = (840.0, 110.0)            # canvas of the skin over the groove
X0, X1 = -35.0, 31.7               # frame edges in mm


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


L, R = X0 - 3, X1 + 3
BONE_TOP = [(L, 27), (-28, 24.5), (-22, 22.2), (-16, 24.5), (-9, 30.5), (-3, 35.2), (2, 33.6), (6, 30.6), (9, 29.8),
            (14, 31.6), (22, 34.4), (R, 36.4)]
BONE = BONE_TOP + [(R, 50), (L, 50)]
ILIOPSOAS_TOP = [(L, 12.6), (-26, 12.4), (-18, 9.4), (-8, 8.6), (2, 9.4), (8, 12.4), (10.6, 18), (10.2, 25), (9.6, 29.2)]
ILIOPSOAS = ILIOPSOAS_TOP + [(x, y - 0.3) for x, y in reversed(BONE_TOP) if x < 9.6]
TENDON = ((2.4, 30.4), 3.4, 1.8)
SARTORIUS = [(L, 5.6), (-26, 5.2), (-20, 6.2), (-19, 8.6), (-24, 12.4), (L, 13)]
PECTINEUS = [(14, 24), (22, 21), (R, 21), (R, 36.2), (22, 34.2), (14, 31.4), (11.4, 27.6)]
FEMORAL_NERVE = ((12.4, 13.2), 3.2, 1.3)
ARTERY = ((18.8, 14.0), 3.6)
VEIN = ((27.4, 15.0), 4.8, 3.8)
FASCIA_ILIACA = [(-24, 12.6), (-12, 8.0), (2, 8.6), (9, 11.0), (13, 15.0), (16, 21.0)]
FASCIA_LATA = 4.6
PROBE_LATERAL_X = X0 + 10.0        # the probe stops 1 cm short of the lateral edge
NEEDLE_ENTRY = (X0 + 5.0, 0.0)
NEEDLE_TIP = (1.0, 33.0)           # on the eminence's lateral slope, deep to the tendon


def spread():
    """Teal injectate between the psoas tendon / muscle and the bone, rounded ends."""
    top = [(-7.4, 31.0), (-4, 31.6), (0, 31.0), (4, 30.6), (8, 29.4), (10.4, 29.0)]
    bottom = [(10.0, 30.2), (6, 31.4), (2, 33.4), (-2, 34.6), (-5.4, 33.6), (-7.6, 31.8)]
    return top + bottom


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


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.35, e[1] - dy * 0.35)
    probe_x = c((PROBE_LATERAL_X, 0))[0]
    labels = [
        Label(["Iliopubic eminence"], anchor=(760, 1150), leader=[(980, 1100), c((9.4, 31.0))], target_id="bone", emphasis=True),
        Label(["Psoas tendon"], anchor=(1110, 780), leader=[(1120, 750), c((5.0, 30.0))], target_id="psoas-tendon"),
        Label(["AIIS"], anchor=(40, 1030), leader=[(140, 980), c((-22, 23.6))], target_id="bone"),
        Label(["Femoral artery"], anchor=(1180, 620), leader=[(1250, 570), c((19.4, 16.2))], target_id="femoral-artery"),
        Label(["Iliopsoas"], anchor=(560, 560), leader=[(640, 520), c((-6, 16))], target_id="iliopsoas"),
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
  <path id="fascia-lata" d="{path(band(FASCIA_LATA, FASCIA_LATA + 0.35), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  <path id="bone" d="{path(BONE, closed=True, tension=0.6)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="pectineus" d="{path(PECTINEUS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="iliopsoas" d="{path(ILIOPSOAS, closed=True, tension=0.4)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  {ell("psoas-tendon", TENDON, 'fill="#F1EDE4" stroke="#B9B2A4" stroke-width="4"')}
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="fascia-iliaca" d="{path(FASCIA_ILIACA, tension=0.7)}" fill="none" stroke="#F8F6F0" stroke-width="7"/>
  {ell("femoral-nerve", FEMORAL_NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ell("femoral-vein", VEIN, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("femoral-artery", ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.75" stroke="#0E8C98" stroke-width="3"/>
  {ell("tendon-outline", TENDON, 'fill="none" stroke="#B9B2A4" stroke-width="4"')}
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
