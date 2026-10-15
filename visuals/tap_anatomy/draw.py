"""Transversus abdominis plane block - the lateral abdominal wall in section (layout).

Transverse section of the right lateral abdominal wall at the mid-axillary
line, midway between the costal margin and the iliac crest, under a probe
placed transversely, as on the screen: posterior on the image left, anterior
on the right (the patient's right on the image left, seen from the feet),
skin at the top. Composition after NYSORA's TAP reverse-ultrasound plates
(concept only, not committed); drawn from scratch.

Record: transducer transverse on the lateral abdominal wall, midway between
the costal margin and the iliac crest (mid-axillary line); three muscle
layers; needle in-plane anterior to posterior (or the reverse) until the tip
pops through the internal oblique fascia into the TAP plane; inject 20-30 mL
in increments.

Standard anatomy added: external oblique, internal oblique (thickest) and
transversus abdominis separated by thin fascial sheets; the thoracolumbar
segmental nerve with a small artery running in the plane between internal
oblique and transversus (house style: in its own sheath); transversalis
fascia, a thin layer of preperitoneal fat and the peritoneum, bowel deep.
Typical adult depths.

Millimetres from the skin at the middle of the field (x anterior = image
right, y deep) at 20 px/mm.

Run: python3 visuals/tap_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "tap_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 20.0
ORIGIN = (800.0, 110.0)
X0, X1 = -40.0, 40.0
L, R = X0 - 3, X1 + 3
SKIN, FAT = 2.0, 14.0
EO = (14.4, 21.5)
IO = (22.3, 33.5)
TA = (34.3, 39.8)
F = 0.4                                   # half-thickness of a fascial line (7 px... at 20 px/mm about 0.35 mm)
PLANE = ((IO[1] + TA[0]) / 2)
TRANSVERSALIS, PERITONEUM = 40.2, 43.2
NERVE_SHEATH = ((-6.0, 34.3), 1.9, 0.95)
NERVE = ((-6.7, 34.3), 0.7, 0.6)
ARTERY = ((-5.0, 34.35), 0.5, 0.5)
NEEDLE_ENTRY = (X1 - 4.6, 0.0)
NEEDLE_TIP = (4.0, 33.75)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


def spread():
    return [(-26, 33.95), (-14, 33.8), (0, 33.7), (10, 33.75), (17, 33.95), (12, 35.9), (0, 37.6), (-13, 37.0), (-23, 35.3)]


BOWEL = [((-24, 51), 13, 7), ((4, 50), 15, 6.5), ((32, 51.5), 12, 7)]

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
    a = (e[0] - dx * 0.25, e[1] - dy * 0.25)
    probe_x1 = c((X1 - 10.0, 0))[0]
    W = 'fill="#F8F6F0"'
    M = 'fill="url(#muscle)"'
    labels = [
        Label(["External oblique"], anchor=(40, 488), leader=[(420, 472), (470, 472)], target_id="eo"),
        Label(["Internal oblique"], anchor=(40, 690), leader=[(410, 674), (460, 674)], target_id="io"),
        Label(["Transversus abdominis"], anchor=(40, 880), leader=[(560, 864), (610, 864)], target_id="ta"),
        Label(["TAP plane"], anchor=(1120, 1020), leader=[(1160, 980), (1060, c((0, PLANE))[1])], target_id="tap-plane", emphasis=True),
        Label(["Peritoneum"], anchor=(40, 1060), leader=[(300, 1024), (340, c((0, PERITONEUM))[1])], target_id="peritoneum"),
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

    bowel = "".join(ell(f"bowel-{i}", b, 'fill="#E2A29A" stroke="#F8F6F0" stroke-width="6"') for i, b in enumerate(BOWEL))
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 80), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(SKIN, 80), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="eo" d="{path(band(EO[0], EO[1]), closed=True, tension=0.2)}" {M}/>
  <path id="io" d="{path(band(IO[0], IO[1]), closed=True, tension=0.2)}" {M}/>
  <path id="ta" d="{path(band(TA[0], TA[1]), closed=True, tension=0.2)}" {M}/>
  <path id="preperitoneal-fat" d="{path(band(TRANSVERSALIS, PERITONEUM), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="cavity" d="{path(band(PERITONEUM, 80), closed=True, tension=0.2)}" fill="#EAD2C8"/>
  {bowel}
  <path id="fascia-eo" d="{path(band(EO[0] - F, EO[0] + 0.0), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-eo-io" d="{path(band(EO[1], IO[0]), closed=True, tension=0.2)}" {W}/>
  <path id="tap-plane" d="{path(band(IO[1], TA[0]), closed=True, tension=0.2)}" {W}/>
  <path id="transversalis" d="{path(band(TA[1], TRANSVERSALIS + 0.2), closed=True, tension=0.2)}" {W}/>
  <path id="peritoneum" d="{path(band(PERITONEUM - 0.2, PERITONEUM + 0.2), closed=True, tension=0.2)}" {W}/>
  {ell("nerve-sheath", NERVE_SHEATH, 'fill="#F3E4C2" stroke="#F8F6F0" stroke-width="6"')}
  {ell("nerve", NERVE, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ell("artery", ARTERY, 'fill="#C8463C" stroke="#8E2A23" stroke-width="3"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.6)}" fill="#6CCBD2" fill-opacity="0.62" stroke="#0E8C98" stroke-width="3" stroke-opacity="0.85"/>
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
