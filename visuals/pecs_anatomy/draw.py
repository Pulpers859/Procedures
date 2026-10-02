"""PECS I / II block - the right chest wall in section under a linear probe (layout).

Oblique section of the right anterior chest wall at the 3rd-4th rib level,
along the probe of the positioning plate (below the lateral third of the
clavicle, pointing toward the axilla): lateral (the axilla) on the image
left, medial on the right, skin at the top - the same way round as the
positioning plate, where the needle comes in from the medial end.

Record: PECS I - the plane between pectoralis major and minor (10 mL).
PECS II - advance through pectoralis minor into the pectoserratus plane,
between pectoralis minor and serratus anterior (15-20 mL); stop there,
short of the ribs and pleura. Needle in-plane from medial to lateral.

Standard adult anatomy added: pectoralis major about 1 cm thick, pectoralis
minor tapering laterally, serratus anterior over the ribs, two ribs in
section with intercostal muscle between them, the pleura and lung deep; the
pectoral branch of the thoracoacromial artery in the PECS I plane.

Code-drawn: the probe, the needle (tip in the PECS II plane), the two teal
spreads.

Millimetres from the skin at the frame's centre (x toward the midline =
image right, y deep) at 26 px/mm.

Run: python3 visuals/pecs_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "pecs_anatomy"
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


FAT_Y, B3, PLEURA_Y = 5.0, 27.0, 36.2
PMIN_LAT = -24.0                   # pectoralis minor's lateral tip


def b1(x):
    """Pectoralis major / minor interface (the PECS I plane)."""
    return 13.4 + 0.07 * x


def b2(x):
    """Pectoralis minor / serratus interface (the PECS II plane); minor tapers laterally."""
    return b1(x) + 8.6 * min(1.0, max(0.0, (x - PMIN_LAT) / 10.0)) + 0.03 * max(0.0, x)


XS = [L + (R - L) * k / 60 for k in range(61)]
XS_MIN = [x for x in XS if x >= PMIN_LAT]
PMAJ = [(x, FAT_Y) for x in XS] + [(x, b1(x)) for x in reversed(XS)]
PMIN = [(x, b1(x)) for x in XS_MIN] + [(x, b2(x)) for x in reversed(XS_MIN)]
SERRATUS = [(x, b2(x) if x >= PMIN_LAT else b1(x)) for x in XS] + [(x, B3) for x in reversed(XS)]
INTERCOSTAL = [(L, B3), (R, B3), (R, PLEURA_Y), (L, PLEURA_Y)]
RIBS = [((-15.0, 31.4), 7.2, 4.2), ((14.0, 31.4), 7.2, 4.2)]
TA_ARTERY = ((4.0, b1(4.0)), 0.75)
NEEDLE_ENTRY = (X1 - 4.6, 0.0)
NEEDLE_TIP = (-2.0, b2(-2.0) - 0.5)


def lens(fn, x0, x1, h):
    xs = [x0 + (x1 - x0) * k / 12 for k in range(13)]
    taper = lambda x: h * (1 - ((2 * (x - x0) / (x1 - x0)) - 1) ** 4)  # noqa: E731
    return [(x, fn(x) - taper(x)) for x in xs] + [(x, fn(x) + taper(x)) for x in reversed(xs)]


def pecs1():
    return lens(b1, -12.0, 18.0, 0.9)


def pecs2():
    return lens(b2, -14.0, 16.0, 1.0)


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
    probe_x1 = c((X1 - 10.0, 0))[0]
    labels = [
        Label(["Pectoralis major"], anchor=(40, 330), leader=[(300, 290), c((-20, 9))], target_id="pmaj"),
        Label(["Serratus anterior"], anchor=(40, 760), leader=[(140, 712), c((-27, 20))], target_id="serratus"),
        Label(["Pectoralis minor"], anchor=(1110, 640), leader=[(1120, 600), c((12, 18.6))], target_id="pmin"),
        Label(["PECS I"], anchor=(1180, 300), leader=[(1200, 320), c((14, b1(14)))], target_id="spread-pecs1", emphasis=True),
        Label(["PECS II"], anchor=(560, 790), leader=[(640, 750), c((2, b2(2)))], target_id="spread-pecs2", emphasis=True),
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
  <path id="pmin" d="{path(PMIN, closed=True, tension=0.1)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="pmaj" d="{path(PMAJ, closed=True, tension=0.1)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  {ell("ta-artery", TA_ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread-pecs1" d="{path(pecs1(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.75" stroke="#0E8C98" stroke-width="3"/>
  <path id="spread-pecs2" d="{path(pecs2(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.75" stroke="#0E8C98" stroke-width="3"/>
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
