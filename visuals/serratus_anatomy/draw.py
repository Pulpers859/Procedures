"""Serratus anterior plane block - the right lateral chest wall in section under a sagittal probe (layout).

Sagittal section in the right mid-axillary line at the 4th-5th ribs, as on
the screen: cranial on the image left, caudal on the right, skin at the top.
Composition after NYSORA's serratus plane reverse-ultrasound plate (concept
only, not committed); drawn from scratch.

Record: latissimus dorsi, then serratus anterior on the ribs, then pleura;
inject superficial to serratus (between latissimus and serratus) or deep to
it (between serratus and ribs); the thoracodorsal artery runs in the
superficial plane. Needle in-plane, cranial to caudal.

Standard adult anatomy added: latissimus about 7 mm thick, serratus about
6 mm, two ribs in section with intercostal muscle between, pleura and lung.

Code-drawn: the probe, the needle (tip in the superficial plane, short of
the artery), both teal planes (superficial and deep options).

Millimetres from the skin at the frame's centre (x caudal = image right,
y deep) at 26 px/mm.

Run: python3 visuals/serratus_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "serratus_anatomy"
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


FAT_Y, PLEURA_Y = 5.0, 30.6


def b1(x):
    """Latissimus / serratus interface (the superficial plane)."""
    return 12.4 + 0.04 * x


def b2(x):
    """Serratus / rib interface (the deep plane)."""
    return 19.0 + 0.04 * x


XS = [L + (R - L) * k / 60 for k in range(61)]
LAT = [(x, FAT_Y) for x in XS] + [(x, b1(x)) for x in reversed(XS)]
SERRATUS = [(x, b1(x)) for x in XS] + [(x, b2(x)) for x in reversed(XS)]
INTERCOSTAL = [(x, b2(x)) for x in XS] + [(R, PLEURA_Y), (L, PLEURA_Y)]
RIBS = [((-15.0, 23.4), 7.6, 4.4), ((15.0, 24.6), 7.6, 4.4)]
TDA = ((6.0, b1(6.0)), 0.9)
NEEDLE_ENTRY = (X0 + 4.6, 0.0)
NEEDLE_TIP = (0.0, b1(0.0) - 0.2)


def lens(fn, x0, x1, h):
    xs = [x0 + (x1 - x0) * k / 12 for k in range(13)]
    taper = lambda x: h * (1 - ((2 * (x - x0) / (x1 - x0)) - 1) ** 4)  # noqa: E731
    return [(x, fn(x) - taper(x)) for x in xs] + [(x, fn(x) + taper(x)) for x in reversed(xs)]


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
    probe_x0 = c((X0 + 10.0, 0))[0]
    labels = [
        Label(["Latissimus dorsi"], anchor=(1080, 390), leader=[(1090, 350), c((11, 8.4))], target_id="latissimus"),
        Label(["Serratus anterior"], anchor=(1080, 600), leader=[(1090, 560), c((11, 15.6))], target_id="serratus"),
        Label(["Thoracodorsal artery"], anchor=(860, 210), leader=[(1000, 230), c((6.6, b1(6.0) - 0.4))], target_id="tda"),
        Label(["Superficial plane"], anchor=(40, 470), leader=[(320, 430), c((-8, b1(-8)))], target_id="spread-superficial", emphasis=True),
        Label(["Deep plane"], anchor=(40, 780), leader=[(300, 740), c((-8, b2(-8)))], target_id="spread-deep", emphasis=True),
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
  <path id="lung" d="{path(band(PLEURA_Y, 60), closed=True, tension=0.2)}" fill="#9AA3AE"/>
  <path id="intercostal" d="{path(INTERCOSTAL, closed=True, tension=0.1)}" fill="#8F332D"/>
  {"".join(ell(f"rib-{i}", r, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="6"') for i, r in enumerate(RIBS, 1))}
  <path id="pleura" d="{path(band(PLEURA_Y - 0.3, PLEURA_Y + 0.3), closed=True, tension=0.2)}" fill="#F4F6F8"/>
  <path id="serratus" d="{path(SERRATUS, closed=True, tension=0.1)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="latissimus" d="{path(LAT, closed=True, tension=0.1)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  {ell("tda", TDA, 'fill="url(#artery)" stroke="#8E211D" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread-superficial" d="{path(lens(b1, -14.0, 4.0, 0.9), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.75" stroke="#0E8C98" stroke-width="3"/>
  <path id="spread-deep" d="{path(lens(b2, -12.0, 10.0, 0.8), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.45" stroke="#0E8C98" stroke-width="3" stroke-dasharray="12 8"/>
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
