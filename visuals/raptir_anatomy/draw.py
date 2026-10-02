"""RAPTIR (retroclavicular infraclavicular) block - sagittal section under the probe (layout).

Parasagittal section of the right infraclavicular fossa under a sagittal
linear probe, as on the screen: cranial (the clavicle) on the image left,
caudal on the right, skin at the top. Composition informed by NYSORA's
infraclavicular reverse-ultrasound plate (concept only, not committed);
drawn from scratch.

Record: the cords surround the axillary artery deep to pectoralis major and
minor; the axillary vein is usually medial or caudal; target the posterior
aspect of the artery, at about 6 o'clock. Needle inserted posterior to the
clavicle, aimed caudally, strictly in-plane, under the clavicle into the
beam; 20-30 mL as a U-shaped spread around the artery.

Standard adult anatomy added: the clavicle in section at the cranial edge,
the lateral cord cranial-superficial, the posterior cord deep (6 o'clock),
the medial cord between the artery and the caudal vein, serratus, ribs and
pleura deep. The artery about 3 cm deep.

Millimetres from the skin over the artery (x caudal = image right, y deep)
at 22 px/mm.

Run: python3 visuals/raptir_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "raptir_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 22.0
ORIGIN = (900.0, 100.0)
X0, X1 = -40.9, 31.8
L, R = X0 - 3, X1 + 3


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


CLAVICLE = ((-23.0, 4.4), 5.0, 3.6)
PMAJ = [(-20, 3.2), (R, 3.2), (R, 13.0), (10, 12.6), (-6, 12.2), (-16, 11.8), (-21, 9.0)]
PMIN = [(-16, 13.6), (-4, 14.0), (10, 14.6), (R, 15.2), (R, 21.4), (10, 20.6), (-4, 19.8), (-14, 18.8), (-18, 16.0)]
ARTERY = ((0.0, 27.0), 3.8)
LATERAL_CORD = ((-6.4, 23.6), 2.2, 2.0)
POSTERIOR_CORD = ((0.6, 33.4), 2.2, 1.9)
MEDIAL_CORD = ((5.8, 30.8), 2.0, 1.8)
VEIN = ((12.4, 30.0), 5.2, 4.0)
SERRATUS_Y = 39.0
RIBS = [((-14.0, 44.0), 7.0, 3.4), ((16.0, 45.0), 7.0, 3.4)]
PLEURA_Y = 48.6
PROBE_CRANIAL_X = -15.0             # the probe sits caudal to the clavicle
NEEDLE_ENTRY = (-40.0, 0.0)         # behind (cranial to) the clavicle
NEEDLE_TIP = (-1.6, 31.2)           # at the artery's posterior aspect, about 6 o'clock


def spread():
    """U-shaped teal spread under the artery, from the lateral to the medial cord."""
    outer = [(-8.6, 24.6), (-6.8, 29.4), (-3.6, 33.6), (0.6, 36.0), (5.0, 34.6), (8.2, 31.6), (8.6, 28.4)]
    inner = [(6.4, 28.8), (3.6, 31.0), (0.4, 31.4), (-3.0, 30.0), (-4.8, 27.4), (-5.6, 25.0)]
    return outer + inner


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
    a = (e[0] - dx * 0.15, e[1] - dy * 0.15)
    probe_x = c((PROBE_CRANIAL_X, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"'
    N = 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"'
    labels = [
        Label(["Clavicle"], anchor=(40, 420), leader=[(150, 380), c((-24, 6))], target_id="clavicle"),
        Label(["Pectoralis minor"], anchor=(1100, 330), leader=[(1180, 350), c((22, 17.6))], target_id="pmin"),
        Label(["Axillary artery"], anchor=(1060, 590), leader=[(1080, 610), c((2.6, 25.6))], target_id="axillary-artery"),
        Label(["Axillary vein"], anchor=(1180, 880), leader=[(1250, 840), c((15, 32))], target_id="axillary-vein"),
        Label(["Posterior cord"], anchor=(560, 1070), leader=[(700, 1030), c((0.2, 34.6))], target_id="posterior-cord", emphasis=True),
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
  <path id="skin" d="{path(band(0, 70), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(1.5, 70), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="lung" d="{path(band(PLEURA_Y, 70), closed=True, tension=0.2)}" fill="#9AA3AE"/>
  <path id="intercostal" d="{path(band(SERRATUS_Y + 2.6, PLEURA_Y), closed=True, tension=0.2)}" fill="#8F332D"/>
  {"".join(ell(f"rib-{i}", r, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="5"') for i, r in enumerate(RIBS, 1))}
  <path id="pleura" d="{path(band(PLEURA_Y - 0.3, PLEURA_Y + 0.3), closed=True, tension=0.2)}" fill="#F4F6F8"/>
  <path id="serratus" d="{path(band(SERRATUS_Y - 1.6, SERRATUS_Y + 2.6), closed=True, tension=0.2)}" {M}/>
  <path id="pmaj" d="{path(PMAJ, closed=True, tension=0.5)}" {M}/>
  <path id="pmin" d="{path(PMIN, closed=True, tension=0.5)}" {M}/>
  {ell("clavicle", CLAVICLE, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="6"')}
  {ell("axillary-vein", VEIN, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("axillary-artery", ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  {ell("lateral-cord", LATERAL_CORD, N)}
  {ell("posterior-cord", POSTERIOR_CORD, N)}
  {ell("medial-cord", MEDIAL_CORD, N)}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="3"/>
  {ell("posterior-outline", POSTERIOR_CORD, 'fill="none" stroke="#B8962E" stroke-width="4"')}
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
