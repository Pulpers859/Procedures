"""Popliteal sciatic block - the right popliteal fossa in section under a linear probe (layout).

Transverse section of the right thigh about 6 cm above the crease, patient
prone, seen as on the screen with the probe on the back of the leg: skin at
the top, lateral (biceps femoris) on the image right, medial
(semitendinosus, semimembranosus) on the left - the same way round as the
positioning plate and NYSORA's prone figure (concept only, not committed);
drawn from scratch.

Record: the sciatic nerve divides about 6 cm above the crease into the
tibial (medial) and common peroneal (lateral) nerves; the popliteal artery
(deepest) and vein (middle) are medial and deep; needle in-plane from
lateral to medial into the common paraneural sheath, outside the nerves.

Standard adult anatomy added: semitendinosus over semimembranosus medially,
biceps femoris laterally, popliteal fat filling the fossa, the two nerves
side by side in one paraneural sheath about 2.5 cm deep, the vein deep and
medial to the tibial nerve, the artery deeper still.

Millimetres from the skin over the tibial nerve (x lateral = image right,
y deep) at 28 px/mm. Depths vary with habitus.

Run: python3 visuals/popliteal_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "popliteal_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 28.0
ORIGIN = (760.0, 110.0)
X0, X1 = -27.1, 30.0
L, R = X0 - 3, X1 + 3


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


FASCIA_Y = 5.0
SEMITEND = [(L, FASCIA_Y), (-12, FASCIA_Y), (-9, 9), (-10, 14), (-14, 17), (L, 16)]
SEMIMEMB = [(L, 16.4), (-14.4, 17.4), (-11, 21), (-10.6, 27), (-13, 33), (L, 35)]
BICEPS = [(R, FASCIA_Y), (13, FASCIA_Y), (10, 9), (10.4, 15), (13, 21), (18, 26), (R, 28)]
TIBIAL = ((-1.0, 22.6), 4.6, 3.2)
PERONEAL = ((6.0, 16.0), 2.8, 2.2)
SHEATH = [(-6.6, 23.0), (-5.4, 19.0), (-1.6, 18.4), (2.0, 15.0), (5.2, 13.0), (9.6, 13.6), (10.2, 16.6),
          (8.0, 20.0), (6.4, 23.4), (2.0, 26.4), (-2.4, 26.8), (-5.8, 25.6)]
VEIN = ((-5.6, 30.2), 4.0, 3.2)
ARTERY = ((-10.4, 33.8), 3.2)
PROBE_LATERAL_X = X1 - 10.0        # the probe stops 1 cm short of the lateral edge
NEEDLE_ENTRY = (X1 - 3.0, 0.0)
NEEDLE_TIP = (4.6, 22.0)           # in the sheath, between the two nerves, deep to the peroneal


def spread():
    """Teal injectate filling the paraneural sheath around both nerves."""
    return [(-7.6, 23.2), (-6.2, 18.4), (-2.0, 17.4), (1.6, 14.0), (5.2, 12.0), (10.4, 12.8), (11.2, 16.8),
            (9.0, 20.6), (7.0, 24.2), (2.2, 27.4), (-2.6, 27.8), (-6.6, 26.4)]


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
    probe_x = c((PROBE_LATERAL_X, 0))[0]
    labels = [
        Label(["Tibial nerve"], anchor=(40, 760), leader=[(330, 720), c((-3.4, 23.4))], target_id="tibial-nerve", emphasis=True),
        Label(["Common peroneal", "nerve"], anchor=(1040, 330), leader=[(1060, 390), c((7.6, 15.8))], target_id="peroneal-nerve", emphasis=True),
        Label(["Popliteal vein"], anchor=(800, 990), leader=[(810, 960), c((-2.2, 29.6))], target_id="popliteal-vein"),
        Label(["Popliteal artery"], anchor=(640, 1160), leader=[(650, 1120), c((-8.4, 35.0))], target_id="popliteal-artery"),
        Label(["Biceps femoris"], anchor=(1120, 900), leader=[(1230, 860), c((21, 22))], target_id="biceps"),
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
  <path id="deep-fascia" d="{path(band(FASCIA_Y - 0.3, FASCIA_Y), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  <path id="semitendinosus" d="{path(SEMITEND, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="semimembranosus" d="{path(SEMIMEMB, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="biceps" d="{path(BICEPS, closed=True, tension=0.5)}" fill="url(#muscle)" stroke="#F4EFE6" stroke-width="4"/>
  <path id="sheath" d="{path(SHEATH, closed=True, tension=0.7)}" fill="#E9DFC4" stroke="#F8F6F0" stroke-width="5"/>
  {ell("tibial-nerve", TIBIAL, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  {ell("peroneal-nerve", PERONEAL, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  {ell("popliteal-vein", VEIN, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("popliteal-artery", ARTERY, 'fill="url(#artery)" stroke="#8E211D" stroke-width="6"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="3"/>
  {ell("tibial-outline", TIBIAL, 'fill="none" stroke="#B8962E" stroke-width="4"')}
  {ell("peroneal-outline", PERONEAL, 'fill="none" stroke="#B8962E" stroke-width="4"')}
  <rect id="probe" x="-100" y="-60" width="{fmt(probe_x + 100)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="-100" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(probe_x + 82)}" height="14" rx="6" fill="#3E454C"/>
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
