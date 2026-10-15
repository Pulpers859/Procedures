"""Thoracic erector spinae plane block - parasagittal section under a sagittal probe (layout).

Parasagittal section of the right upper back at about T5, 3 cm from the
midline, under a probe placed sagittally, as on the screen: cranial on the
image left, caudal on the right, skin at the top. Composition after NYSORA's
ESP reverse-ultrasound plate (concept only, not committed); drawn from
scratch.

Record: transducer sagittal about 3 cm lateral to the thoracic spinous
processes; the erector spinae runs vertically over the square, shadowing
transverse processes; needle in-plane, usually cranial to caudal, until the
tip touches a transverse process; injectate spreads deep to the erector
spinae. NYSORA: above T5 the trapezius, rhomboid major and erector spinae
are three layers over the transverse processes; the pleura is not seen at the
right level.

Standard anatomy added: three transverse processes about 26 mm apart, with
the erector spinae lying directly on them (no fat in the plane), short
intertransverse muscle and the superior costotransverse ligament between them, paravertebral fat and the
pleura deep to the ligament, typical depths (transverse processes about
4 cm deep).

Millimetres from the skin over the middle transverse process (x caudal =
image right, y deep) at 18 px/mm.

Run: python3 visuals/esp_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "esp_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 18.0
ORIGIN = (800.0, 110.0)
X0, X1 = -44.4, 44.4
L, R = X0 - 3, X1 + 3
SKIN, FAT = 2.0, 6.0
TRAP, RHOMB, ES = 11.0, 17.0, 37.6     # deep surface of each muscle
F = 0.4                                 # half-thickness of a fascial line (7 px)
TP_TOP, TP_BOT, TP_HALF = 38.3, 47.0, 7.0
TPS = (-26.0, 0.0, 26.0)
LIG_TOP, LIG_BOT = 41.0, 42.4
PLEURA = 53.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


def rect(el_id, x0, y0, x1, y1, rx, attrs):
    p0, p1 = c((x0, y0)), c((x1, y1))
    return (f'<rect id="{el_id}" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" '
            f'height="{fmt(p1[1] - p0[1])}" rx="{fmt(rx * PX_MM)}" {attrs}/>')


NEEDLE_ENTRY = (-38.0, 0.0)
NEEDLE_TIP = (-2.5, 37.6)


def spread():
    top = [(-46, 37.4), (-36, 36.4), (-20, 35.6), (0, 35.2), (20, 35.6), (36, 36.4), (46, 37.4)]
    bottom = [(46, 37.9), (39.5, 38.5), (33.5, 37.9), (26, 37.85), (19.0, 37.9), (13.0, 38.6), (7.0, 37.9), (0, 37.85),
              (-7.0, 37.9), (-13.0, 38.6), (-19.0, 37.9), (-26, 37.85), (-33.5, 37.9), (-39.5, 38.5), (-46, 37.9)]
    return top + bottom


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A63F37"/><stop offset="1" stop-color="#7A2621"/></linearGradient>
<linearGradient id="lung-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9A9A4"/><stop offset="1" stop-color="#D88E8A"/></linearGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.25, e[1] - dy * 0.25)
    probe_x0 = c((NEEDLE_ENTRY[0] + 5.0, 0))[0]
    W = 'fill="#F8F6F0"'
    tps = "".join(rect(f"tp-{i}" if x else "tp", x - TP_HALF, TP_TOP, x + TP_HALF, TP_BOT, 3.0,
                       'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"') for i, x in enumerate(TPS))
    labels = [
        Label(["Trapezius"], anchor=(1250, 282), leader=[(1240, 266), (1190, 266)], target_id="trapezius"),
        Label(["Rhomboid major"], anchor=(1100, 384), leader=[(1090, 368), (1040, 368)], target_id="rhomboid"),
        Label(["Erector spinae"], anchor=(1160, 610), leader=[(1150, 594), (1100, 594)], target_id="erector-spinae"),
        Label(["Transverse process"], anchor=(940, 1010), leader=[(1000, 968), (850, 900)], target_id="tp", emphasis=True),
        Label(["Pleura"], anchor=(60, 1160), leader=[(130, 1116), (170, c((0, PLEURA))[1])], target_id="pleura"),
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
  <path id="skin" d="{path(band(0, 80), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(SKIN, 80), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="trapezius" d="{path(band(FAT + F, TRAP - F), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="rhomboid" d="{path(band(TRAP + F, RHOMB - F), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="erector-spinae" d="{path(band(RHOMB + F, ES - F), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="intertransverse" d="{path(band(ES + F, LIG_TOP), closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="pvs-fat" d="{path(band(LIG_BOT, PLEURA - F), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="lung" d="{path(band(PLEURA + F, 80), closed=True, tension=0.2)}" fill="url(#lung-grad)"/>
  <path id="fascia-1" d="{path(band(FAT - F, FAT + F), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-2" d="{path(band(TRAP - F, TRAP + F), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-3" d="{path(band(RHOMB - F, RHOMB + F), closed=True, tension=0.2)}" {W}/>
  <path id="es-fascia" d="{path(band(ES - F, ES + F), closed=True, tension=0.2)}" {W}/>
  <path id="ligament" d="{path(band(LIG_TOP, LIG_BOT), closed=True, tension=0.2)}" fill="#F1EEE6" stroke="#F8F6F0" stroke-width="4"/>
  <path id="pleura" d="{path(band(PLEURA - F, PLEURA + F), closed=True, tension=0.2)}" {W}/>
  {tps}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#6CCBD2" fill-opacity="0.5" stroke="#0E8C98" stroke-width="3"/>
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
