"""Superficial cervical plexus block - the right neck in section at mid-SCM under a linear probe (layout).

Transverse section of the right neck at the midpoint of the
sternocleidomastoid, as on the screen with the probe transverse over the
mid-SCM: posterior (lateral) on the image left, anterior (medial, the
carotid) on the right, skin at the top. The same way round as the
interscalene plate. Drawn from scratch.

Record: the plexus wraps around the posterior border of the SCM at about its
midpoint; the external jugular vein crosses the SCM near this level; the SCM
is the large superficial muscle, with the levator scapulae or scalenes deep
to it; the plexus is a small hyperechoic cluster at the posterior edge of
the SCM. Needle in-plane from posterior to anterior; inject in the fascial
plane immediately deep to the posterior border of the SCM; spread along the
posterior border, separating the fascial layers.

Standard adult anatomy added: the external jugular vein on the SCM's
surface; the prevertebral fascia over levator scapulae, middle and anterior
scalene; the internal jugular vein and carotid deep to the SCM medially; a
cervical transverse process deep. No brachial plexus roots are drawn (above
their level). Depths: the posterior SCM border about 9 mm deep, adult
proportions.

Millimetres from the skin over the SCM's posterior border (x medial = image
right, y deep) at 26 px/mm.

Run: python3 visuals/sc_plexus_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "sc_plexus_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (760.0, 110.0)
X0, X1 = -29.2, 32.3
L, R = X0 - 3, X1 + 3


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


SCM = [(-1.5, 8.5), (1, 6.0), (6, 4.8), (14, 4.4), (24, 4.4), (R, 4.6), (R, 16.4), (24, 16.2), (14, 14.8),
       (6, 12.4), (1, 10.4)]
FASCIA = [(L, 13.2), (-10, 13.2), (0, 13.2), (8, 13.6), (14, 15.0)]
LEVATOR = [(L, 14.6), (-16, 14.0), (-10, 14.4), (-9, 20), (-10, 30), (L, 31)]
MSM = [(-8.0, 14.2), (-2, 13.8), (3, 14.4), (4, 20), (2, 30), (-7, 31), (-8.2, 22)]
ASM = [(5.4, 15.0), (9, 15.2), (12.6, 16.6), (12, 24), (9.4, 28.6), (6, 26), (5.2, 20)]
BONE = [(-6, 34), (2, 32.4), (10, 33.6), (14, 37), (14, 44), (-8, 44), (-8, 37)]
EJV = ((14.0, 3.2), 2.6, 1.3)
IJV = ((19.0, 20.4), 3.6, 2.4)
CAROTID = ((24.8, 23.2), 3.0)
PLEXUS = [((-1.6, 11.4), 0.7), ((0.2, 11.6), 0.6), ((1.6, 12.0), 0.55), ((-0.6, 12.6), 0.5)]
NEEDLE_ENTRY = (-22.0, 0.0)
NEEDLE_TIP = (-3.0, 11.2)


def spread():
    return [(-5.4, 11.8), (-3.6, 10.6), (-1.0, 10.0), (2.0, 10.9), (5.0, 11.9), (7.6, 12.8), (6.0, 13.1), (2.0, 13.1),
            (-2.0, 13.1), (-4.6, 12.9)]


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
    id_attr = f'id="{el_id}" ' if el_id else ""
    return f'<ellipse {id_attr}cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.4, e[1] - dy * 0.4)
    probe_x0 = c((X0 + 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"'
    labels = [
        Label(["Sternocleidomastoid"], anchor=(1010, 300), leader=[(1100, 320), c((18, 10))], target_id="scm"),
        Label(["External jugular vein"], anchor=(470, 215), leader=[(1010, 200), c((12.0, 3.2))], target_id="ejv"),
        Label(["Superficial", "cervical plexus"], anchor=(40, 470), leader=[(330, 530), c((-1.6, 11.4))], target_id="plexus",
              emphasis=True),
        Label(["Levator scapulae"], anchor=(40, 1080), leader=[(200, 1030), c((-18, 22))], target_id="levator"),
        Label(["Carotid"], anchor=(1330, 1150), leader=[(1420, 1100), c((24.8, 25.0))], target_id="carotid"),
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

    nerves = "".join(ell("plexus" if i == 0 else "", (ct, r), 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')
                     for i, (ct, r) in enumerate(PLEXUS))
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 60), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(1.6, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="bone" d="{path(BONE, closed=True, tension=0.6)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="levator" d="{path(LEVATOR, closed=True, tension=0.4)}" {M}/>
  <path id="msm" d="{path(MSM, closed=True, tension=0.8)}" {M}/>
  <path id="asm" d="{path(ASM, closed=True, tension=0.8)}" {M}/>
  <path id="prevertebral-fascia" d="{path(FASCIA, tension=0.6)}" fill="none" stroke="#F8F6F0" stroke-width="8"/>
  <path id="scm" d="{path(SCM, closed=True, tension=0.5)}" {M}/>
  {ell("ijv", IJV, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("carotid", CAROTID, 'fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  {ell("ejv", EJV, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {nerves}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="3"/>
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
