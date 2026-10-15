"""Sural nerve block - the right ankle in section under a linear probe (layout).

Transverse section of the right ankle just above the tip of the lateral
malleolus, under a probe transverse between the lateral malleolus and the
Achilles tendon, as on the screen: posterior (the Achilles tendon) on the
image left, anterior (peroneus brevis, the fibula) on the right, skin at the
top. Composition after NYSORA's sural reverse-ultrasound plate (concept only,
not committed), mirrored to the house laterality as the superficial peroneal
section (anterior on the right); drawn from scratch.

Record: the sural nerve travels with the small saphenous vein behind the
lateral malleolus; the nerve is tiny, adjacent to the vein and usually
posterior to it; the vein collapses under the probe, the nerve does not;
inject 3-5 mL around the nerve and vein. NYSORA: the nerve lies beside the
vein superficial to the deep fascia; needle in-plane (or out of plane),
spread around the vein.

Standard anatomy added: the vein and nerve wrapped together in one thin
fascial sheath in the subcutaneous fat (house style: nerves never float in
fat); the Achilles tendon wrapped by the deep fascia; peroneus brevis muscle
with the peroneus longus tendon on its posterior surface; the fibula deep in
front; flexor hallucis longus deep behind, with Kager's fat between it and
the Achilles. Needle in-plane from the anterior end, as the superficial
peroneal section.

Millimetres from the skin over the vein (x anterior = image right, y deep)
at 26 px/mm.

Run: python3 visuals/sural_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "sural_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (800.0, 110.0)
X0, X1 = -30.8, 30.8
L, R = X0 - 3, X1 + 3
FASCIA_TOP, FASCIA_BOT = 6.2, 6.9


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


VEIN = ((2.0, 4.0), 1.7, 1.7)
NERVE = ((-2.4, 4.5), 1.2, 0.85)
SHEATH = ((-0.1, 4.05), 4.6, 1.9)
ACHILLES = ((-21.5, 11.8), 8.8, 4.6)
FIBULA = ((21.0, 31.0), 8.5, 7.5)
PL_TENDON = ((-3.0, 10.2), 2.7, 1.7)
PBM = [(-5.6, FASCIA_BOT), (R, FASCIA_BOT), (R, 21.5), (29, 24.4), (24, 23.3), (18, 23.9), (14.2, 26.4), (12.8, 30.0),
       (13.0, 33.6), (9.0, 30.0), (4.0, 26.0), (-1.5, 21.0), (-5.0, 15.0), (-6.6, 10.0)]
FHL = [(L, 25.0), (-22, 21.8), (-13, 19.5), (-6.5, 16.5), (0, 17), (8, 22), (14, 28), (14, 46), (L, 46)]
NEEDLE_ENTRY = (X1 - 4.6, 0.0)
NEEDLE_TIP = (4.9, 4.2)


def spread():
    return [(-5.6, 3.0), (-4.2, 2.2), (-1.0, 1.95), (2.6, 2.0), (5.4, 2.8), (6.4, 4.2), (5.6, 5.5), (2.0, 5.95),
            (-2.0, 5.95), (-5.2, 5.4), (-6.2, 4.3)]


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A63F37"/><stop offset="1" stop-color="#7A2621"/></linearGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.4, e[1] - dy * 0.4)
    probe_x1 = c((X1 - 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F8F6F0" stroke-width="7"'
    vein, nerve = c(VEIN[0]), c(NERVE[0])
    labels = [
        Label(["Deep fascia"], anchor=(40, 236), leader=[(330, 224), (400, 276)], target_id="deep-fascia"),
        Label(["Sural nerve"], anchor=(330, 700), leader=[(560, 660), (nerve[0], nerve[1] + 4)], target_id="nerve", emphasis=True),
        Label(["Small saphenous", "vein"], anchor=(960, 380), leader=[(1010, 340), (vein[0] + 6, vein[1] + 6)], target_id="vein"),
        Label(["Achilles tendon"], anchor=(40, 580), leader=[(200, 540), (230, 460)], target_id="achilles"),
        Label(["Peroneus brevis"], anchor=(1060, 700), leader=[(1100, 660), (1060, 560)], target_id="pbm"),
        Label(["Fibula"], anchor=(1340, 1160), leader=[(1380, 1116), (1350, 1000)], target_id="fibula"),
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
  <path id="kager-fat" d="{path(band(FASCIA_BOT, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="fhl" d="{path(FHL, closed=True, tension=0.3)}" {M}/>
  <path id="pbm" d="{path(PBM, closed=True, tension=0.3)}" {M}/>
  {ell("pl-tendon", PL_TENDON, 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="5"')}
  {ell("fibula", FIBULA, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  {ell("achilles", ACHILLES, 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="7"')}
  <path id="deep-fascia" d="{path(band(FASCIA_TOP, FASCIA_BOT), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  {ell("sheath", SHEATH, 'fill="#F3E4C2" stroke="#F8F6F0" stroke-width="7"')}
  {ell("vein", VEIN, 'fill="#3E5C9A" stroke="#2C4475" stroke-width="3"')}
  {ell("nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.5" stroke="#0E8C98" stroke-width="3"/>
  <rect id="probe" x="-100" y="-60" width="{fmt(probe_x1 + 100)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="-100" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(probe_x1 + 82)}" height="14" rx="6" fill="#3E454C"/>
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
