"""Transgluteal / proximal sciatic block - the right buttock in section under a curved probe (layout).

Transverse section of the right buttock at the level of the ischial
tuberosity and the greater trochanter, patient prone, under a probe placed
transversely between them, as on the screen: medial (the ischial tuberosity)
on the image left, lateral (the greater trochanter) on the right, skin at the
top - the same way round as the popliteal section and the positioning plate.
Composition after NYSORA's gluteal reverse-ultrasound plate (concept only,
not committed); drawn from scratch.

Record: transducer transverse below the gluteal fold; the ischial tuberosity
medial and the greater trochanter lateral if scanning high enough; the
sciatic nerve a large oval hyperechoic structure midway between them, deep to
gluteus maximus; needle in-plane; inject 20-30 mL around it. NYSORA: needle
in-plane from lateral to medial toward the lateral edge of the nerve within
the fascial plane.

Standard anatomy added: thick subcutaneous fat and gluteus maximus; the nerve
flat-oval, lying on quadratus femoris in the plane under gluteus maximus, in
its own fascial sheath (house style), with the hamstring origin on the
tuberosity medially; typical adult depths (nerve about 5 cm deep).

Millimetres from the skin over the nerve (x lateral = image right, y deep) at
12 px/mm.

Run: python3 visuals/transgluteal_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "transgluteal_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 12.0
ORIGIN = (800.0, 110.0)
X0, X1 = -66.7, 66.7
L, R = X0 - 3, X1 + 3
SKIN, FAT = 2.5, 22.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


GM_BOTTOM = [(L, 49.0), (-40, 47.5), (-20, 47.2), (0, 47.0), (20, 46.6), (40, 45.6), (R, 44.0)]
ISCHIUM = ((-46.0, 66.0), 17.0, 13.0)
TROCHANTER = ((50.0, 63.0), 19.0, 17.0)
HAMSTRING = [(-62, 50.5), (-48, 48.6), (-34, 49.2), (-30.5, 51.6), (-35, 53.6), (-48, 53.4), (-62, 53.6)]
QF = [(-30, 49.6), (-14, 47.8), (-11.0, 47.9), (-7.5, 52.2), (0, 53.3), (7.5, 52.2), (11.0, 47.7), (20, 47.2), (31, 48.6), (33, 56), (31, 63), (0, 60.5), (-29, 63), (-31.5, 56)]
SHEATH = ((0.0, 50.3), 11.5, 2.8)
NERVE = ((0.0, 50.3), 9.0, 1.9)
NEEDLE_ENTRY = (X1 - 6.0, 0.0)
NEEDLE_TIP = (11.2, 49.8)


def spread():
    return [(-13.5, 49.9), (-9, 47.5), (0, 47.1), (9, 47.5), (13.8, 48.9), (14.2, 50.7), (9, 52.8), (0, 53.3), (-9, 52.8), (-13.8, 51.5)]


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
    a = (e[0] - dx * 0.2, e[1] - dy * 0.2)
    probe_x1 = c((X1 - 12.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F8F6F0" stroke-width="7"'
    gm = [(L, FAT), (R, FAT)] + list(reversed(GM_BOTTOM))
    labels = [
        Label(["Gluteus maximus"], anchor=(40, 470), leader=[(450, 454), (520, 454)], target_id="gm"),
        Label(["Sciatic nerve"], anchor=(560, 600), leader=[(700, 610), (c((-3, 50.3))[0], c((-3, 50.3))[1] + 4)], target_id="nerve", emphasis=True),
        Label(["Ischial", "tuberosity"], anchor=(40, 1010), leader=[(200, 968), (240, 900)], target_id="ischium"),
        Label(["Greater", "trochanter"], anchor=(1290, 1000), leader=[(1400, 956), (1400, 880)], target_id="trochanter"),
        Label(["Quadratus femoris"], anchor=(520, 1130), leader=[(700, 1090), (760, 800)], target_id="qf"),
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
  <path id="skin" d="{path(band(0, 120), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(SKIN, 120), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="deep" d="{path(band(45, 120), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="qf" d="{path(QF, closed=True, tension=0.3)}" {M}/>
  {ell("ischium", ISCHIUM, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  {ell("trochanter", TROCHANTER, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  <path id="gm" d="{path(gm, closed=True, tension=0.3)}" {M}/>
  {ell("sheath", SHEATH, 'fill="#F3E4C2" stroke="#F8F6F0" stroke-width="7"')}
  {ell("nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.62" stroke="#0E8C98" stroke-width="3" stroke-opacity="0.85"/>
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
