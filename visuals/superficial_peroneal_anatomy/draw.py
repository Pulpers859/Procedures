"""Superficial peroneal nerve block - the right distal leg in section under a linear probe (layout).

Transverse section of the right leg about 7 cm above the lateral malleolus,
under a probe transverse on the anterolateral leg, as on the screen: lateral
(peroneus brevis, fibula) on the image left, anterior (extensor digitorum
longus) on the right, skin at the top. Composition after NYSORA's superficial
peroneal reverse-ultrasound plate (concept only, not committed), mirrored to
the house laterality (lateral on the left, as the deep peroneal plate); drawn
from scratch.

Record: in the distal third of the lateral leg the nerve pierces the deep
(crural) fascia to become superficial; it appears as a small bright structure
that pops through the fascial line; needle in-plane toward the nerve; inject
around it. NYSORA: the nerve lies at the junction of the crural fascia and
the intermuscular septum between the lateral (peroneus brevis) and anterior
(extensor digitorum longus) compartments, 5-10 cm above the lateral
malleolus; needle in-plane from the anterior side.

Standard anatomy added: the fibula deep in the lateral compartment, the
muscles packed with only thin fascial septa between them (owner, 2026-10-04:
no fat between muscles), a small fat triangle where the septum meets the
fascia.

Millimetres from the skin over the septum (x anterior = image right, y deep)
at 26 px/mm.

Run: python3 visuals/superficial_peroneal_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "superficial_peroneal_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (800.0, 110.0)
X0, X1 = -30.8, 30.8
L, R = X0 - 3, X1 + 3
FASCIA_TOP, FASCIA_BOT = 5.0, 5.7


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


SEPTUM = [(0.1, 9.4), (-4.5, 14.8), (-8.6, 23.4)]
FIBULA = ((-15.0, 29.0), 8.6, 6.6)
EDL = [(3.6, FASCIA_BOT), (R, FASCIA_BOT), (R, 44), (-4, 44), (-5.4, 36), (-7.4, 26.6), (-8.6, 23.4), (-4.5, 14.8), (0.1, 9.4), (1.85, 7.55)]
PBM = [(L, FASCIA_BOT), (-3.0, FASCIA_BOT), (-1.45, 7.55), (0.1, 9.4), (-4.5, 14.8), (-8.6, 23.4), (-15, 22.2), (-22, 24.8), (L, 27)]
JUNCTION_FAT = [(-3.0, FASCIA_BOT), (3.6, FASCIA_BOT), (0.1, 9.4)]
NERVE = ((0.2, 7.0), 1.5, 0.85)
NEEDLE_ENTRY = (X1 - 4.6, 0.0)
NEEDLE_TIP = (2.1, 6.5)


def spread():
    return [(-3.6, 6.0), (-1.6, 5.8), (1.4, 5.8), (3.6, 6.2), (3.2, 7.8), (1.0, 8.9), (-1.2, 8.8), (-3.2, 7.6)]


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A63F37"/><stop offset="1" stop-color="#7A2621"/></linearGradient>
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
    probe_x1 = c((X1 - 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"'
    labels = [
        Label(["Crural fascia"], anchor=(40, 212), leader=[(392, 200), (470, 249)], target_id="crural-fascia"),
        Label(["Superficial", "peroneal nerve"], anchor=(930, 372), leader=[(912, 334), (818, 296)], target_id="nerve", emphasis=True),
        Label(["Peroneus brevis"], anchor=(40, 482), leader=[(490, 466), (560, 466)], target_id="pbm"),
        Label(["Extensor digitorum", "longus"], anchor=(1030, 760), leader=[(1100, 712), (1100, 650)], target_id="edl"),
        Label(["Fibula"], anchor=(90, 1110), leader=[(250, 1070), (330, 990)], target_id="fibula"),
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
  <path id="deep-compartment" d="{path(band(FASCIA_BOT, 60), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="edl" d="{path(EDL, closed=True, tension=0.3)}" {M}/>
  <path id="pbm" d="{path(PBM, closed=True, tension=0.3)}" {M}/>
  {ell("fibula", FIBULA, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  <path id="septum" d="{path(SEPTUM, tension=0.6)}" fill="none" stroke="#F8F6F0" stroke-width="6"/>
  <path id="junction-fat" d="{path(JUNCTION_FAT, closed=True, tension=0.3)}" fill="url(#fat)" stroke="#F8F6F0" stroke-width="3"/>
  <path id="crural-fascia" d="{path(band(FASCIA_TOP, FASCIA_BOT), closed=True, tension=0.2)}" fill="#F8F6F0"/>
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
