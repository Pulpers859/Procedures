"""Transgluteal / proximal sciatic block - the right thigh in section just below the gluteal fold (layout).

Transverse section of the right proximal posterior thigh at the gluteal
crease, patient prone, under a probe placed transversely just below the
gluteal fold (the subgluteal approach), as on the screen: medial on the
image left, lateral on the right, skin at the top - the same way round as
the positioning plate. Composition after NYSORA's subgluteal reverse-
ultrasound plate (Fig-6; concept only, not committed); drawn from scratch.

Redrawn 2026-10-15 (owner: keep the probe where it anatomically belongs,
below the gluteal fold). The first layout showed the higher gluteal level
(ischial tuberosity, greater trochanter, quadratus femoris), which does not
match a probe below the fold.

Record: transducer transverse below the gluteal fold; the sciatic nerve is a
large oval hyperechoic structure deep to gluteus maximus; needle in-plane;
inject 20-30 mL around it. NYSORA: at the gluteal crease the nerve lies in
the fascial plane between gluteus maximus (posterior), biceps femoris
(medial) and adductor magnus (anterior); needle in-plane from lateral to
medial toward the lateral edge of the nerve within the fascial plane.

Standard anatomy added: the lower part of gluteus maximus thinning medially
where it meets the long head of biceps femoris with its tendon; the nerve
flat-oval in its own fascial sheath (house style); typical adult depths
(nerve about 3.5 cm deep).

Millimetres from the skin over the nerve (x lateral = image right, y deep) at
16 px/mm.

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
PX_MM = 16.0
ORIGIN = (800.0, 110.0)
X0, X1 = -50.0, 50.0
L, R = X0 - 3, X1 + 3
SKIN, FAT = 2.0, 15.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


PLANE = [(L, 37.5), (-30, 37.0), (-15, 35.8), (-4, 35.4), (6, 35.6), (18, 35.0), (32, 33.6), (R, 32.4)]
GM = [(-18, FAT + 0.4), (R, FAT + 0.4), (R, 32.0), (32, 32.9), (20, 33.3), (12, 33.0), (6, 32.9), (0, 33.1), (-4, 33.9), (-9, 33.4), (-13, 28), (-17, 21)]
BF = [(L, FAT + 0.4), (-18.8, FAT + 0.4), (-17.8, 21), (-13.8, 28), (-9.8, 33.6), (-5, 35.0), (-15, 35.4), (-30, 36.6), (L, 37.1)]
BF_TENDON = ((-32.0, 25.0), 7.0, 3.2)
SHEATH = ((6.0, 35.3), 11.5, 2.6)
NERVE = ((6.0, 35.3), 9.0, 1.8)
NEEDLE_ENTRY = (X1 - 6.0, 0.0)
NEEDLE_TIP = (17.0, 34.7)


def spread():
    return [(-6.8, 35.0), (-3, 32.9), (6, 32.4), (14, 32.8), (18.4, 34.3), (18.2, 36.2), (14, 37.8), (6, 38.3), (-3, 37.8), (-7, 36.4)]


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
    nerve = c(NERVE[0])
    labels = [
        Label(["Gluteus maximus"], anchor=(1060, 470), leader=[(1050, 454), (980, 454)], target_id="gm"),
        Label(["Biceps femoris"], anchor=(40, 760), leader=[(180, 700), (160, 640)], target_id="bf"),
        Label(["Sciatic nerve"], anchor=(560, 830), leader=[(700, 790), (nerve[0] - 20, nerve[1] + 6)], target_id="nerve", emphasis=True),
        Label(["Adductor magnus"], anchor=(560, 1080), leader=[(760, 1040), (800, 940)], target_id="am"),
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

    am = [(L, 37.6), (-30, 37.1), (-15, 36.2), (-6, 37.3), (0, 37.8), (6, 37.9), (12, 37.7), (19, 36.8), (25, 35.2), (32, 33.9), (R, 32.7), (R, 90), (L, 90)]
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 120), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(SKIN, 120), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="fascia-bed" d="{path(band(FAT + 0.2, 120), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  <path id="am" d="{path(am, closed=True, tension=0.3)}" {M}/>
  <path id="bf" d="{path(BF, closed=True, tension=0.3)}" {M}/>
  {ell("bf-tendon", BF_TENDON, 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="5"')}
  <path id="gm" d="{path(GM, closed=True, tension=0.3)}" {M}/>
  <path id="plane" d="{path(PLANE, tension=0.4)}" fill="none" stroke="#F8F6F0" stroke-width="7"/>
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
