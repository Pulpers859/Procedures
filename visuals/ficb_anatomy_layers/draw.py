"""Fascia iliaca block - the right groin in cross-section at the inguinal crease.

Transverse section, patient supine, seen from the feet as on CT or a
transverse ultrasound: the patient's right is on the image left, so lateral
is left and medial is right. Skin at the top.

Layers, superficial to deep (record subtitle): skin, subcutaneous fat,
fascia lata, fascia iliaca, then iliopsoas. The femoral vein and artery lie
superficial to the fascia iliaca, vein medial; the femoral nerve lies deep to
it on the iliopsoas, lateral to the artery. Sartorius sits laterally inside
the fascia lata; pectineus lies deep to the vein; the femoral head is deep.

Markings: an in-plane needle from lateral, entering the skin lateral to the
nerve and artery (record step), its tip in the plane between fascia iliaca
and iliacus, lateral to the nerve; and the teal spread in that plane,
reaching toward the nerve (record anatomy).

Millimetres from the femoral artery centre (x medial, y deep from the skin)
at 12 px/mm. Adult proportions; depths vary a lot with habitus.

Run: python3 visuals/ficb_anatomy_layers/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_anatomy_layers"
PX_MM = 12.0
ORIGIN = (1000.0, 250.0)          # canvas of the skin surface above the artery
X_MIN, X_MAX = -84.0, 51.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def skin_y(x):
    return 0.0009 * (x + 10) ** 2


def curve(fn, x0=X_MIN - 12, x1=X_MAX + 12, n=36):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom):
    """Closed polygon between two depth functions across (and beyond) the frame."""
    return curve(top) + list(reversed(curve(bottom)))


def lata_y(x):
    return skin_y(x) + 11.0


def iliaca_y(x):
    """Fascia iliaca: over the iliopsoas, a little shallower laterally, then
    turning down along the muscle's medial border."""
    if x <= -10:
        return 25.0 + 0.02 * (x + 10)
    if x <= 4:
        return 25.0
    return 25.0 + (x - 4) * 2.4


ARTERY = ((0.0, 19.0), 4.5)
VEIN = ((13.5, 20.0), 6.6, 5.0)
NERVE = ((-11.0, 27.3), 5.2, 1.8)
MEDIAL_EDGE_X = 12.0          # where the fascia iliaca reaches the medial border's depth
SARTORIUS = [(-84, 17.2), (-74, 16.4), (-62, 16.2), (-50, 17.0), (-44, 19.5), (-52, 23.0), (-66, 23.2), (-84, 22.6)]
ILIOPSOAS = ([(x, iliaca_y(x) + 0.4) for x in (-96, -80, -60, -40, -20, -5, 4)]
             + [(7, 32.5), (10.5, 42), (9, 52), (-5, 57), (-30, 58), (-60, 55), (-96, 52)])
PECTINEUS = [(14, 30), (24, 27.5), (40, 27.0), (X_MAX + 12, 27.5), (X_MAX + 12, 50), (30, 50), (16, 48), (13.5, 40)]
FEMORAL_HEAD = ((-20.0, 86.0), 27.0)
NEEDLE_OUT, NEEDLE_TIP = (-74.0, -12.0), (-24.0, 26.4)


def spread():
    xs = [-42 + i * 2 for i in range(19)]            # -42 .. -6
    top = [(x, iliaca_y(x) + 0.25) for x in xs]
    bottom = [(x, iliaca_y(x) + 0.4 + 2.6 * math.sin(math.pi * (x + 42) / 36) ** 0.8) for x in reversed(xs)]
    return top + bottom


def ellipse(center, rx, ry, attrs):
    p = c(center)
    return f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7E6B4"/><stop offset="1" stop-color="#EFD698"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9695E"/><stop offset="1" stop-color="#A8483F"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#3E5E96"/></radialGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    tissue = band(skin_y, lambda x: 140)
    fat = band(lambda x: skin_y(x) + 2.2, lambda x: 140)
    below_lata = band(lata_y, lambda x: 140)

    x_entry = next(x / 10 for x in range(-800, 0) if _on_line(x / 10) >= skin_y(x / 10))
    entry = (x_entry, skin_y(x_entry))

    labels = [
        Label(["Fascia iliaca"], anchor=(40, 1010), leader=[(300, 960), c((-60, iliaca_y(-60)))],
              target_id="fascia-iliaca", emphasis=True),
        Label(["Femoral nerve"], anchor=(560, 1130), leader=[(760, 1080), c((-13, 27.6))], target_id="femoral-nerve"),
        Label(["Femoral artery"], anchor=(1150, 120), leader=[(1200, 140), c((1.5, 17.5))], target_id="femoral-artery"),
    ]

    a = c(NEEDLE_OUT)
    t = c(NEEDLE_TIP)
    e = c(entry)
    fh = c(FEMORAL_HEAD[0])

    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="skin" d="{path(tissue, closed=True, tension=0.3)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(fat, closed=True, tension=0.3)}" fill="url(#fat)"/>
  <path d="{path(below_lata, closed=True, tension=0.3)}" fill="#E9D4A6"/>
  <circle id="femoral-head" cx="{fmt(fh[0])}" cy="{fmt(fh[1])}" r="{fmt(FEMORAL_HEAD[1] * PX_MM)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="iliopsoas" d="{path(ILIOPSOAS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#8E3A33" stroke-width="3"/>
  <path id="pectineus" d="{path(PECTINEUS, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#8E3A33" stroke-width="3" opacity="0.92"/>
  <path id="sartorius" d="{path(SARTORIUS, closed=True, tension=0.8)}" fill="url(#muscle)" stroke="#8E3A33" stroke-width="3"/>
  <path id="fascia-lata" d="{path(curve(lata_y))}" fill="none" stroke="#F8F6F0" stroke-width="10"/>
  <path d="{path(curve(lata_y))}" fill="none" stroke="#9E927C" stroke-width="3"/>
  <path id="fascia-iliaca" d="{path(curve(iliaca_y, X_MIN - 12, MEDIAL_EDGE_X + 4, 60))}" fill="none" stroke="#F8F6F0" stroke-width="10"/>
  <path d="{path(curve(iliaca_y, X_MIN - 12, MEDIAL_EDGE_X + 4, 60))}" fill="none" stroke="#9E927C" stroke-width="3"/>
  {ellipse(NERVE[0], NERVE[1], NERVE[2], 'id="femoral-nerve" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
  {ellipse(VEIN[0], VEIN[1], VEIN[2], 'id="femoral-vein" fill="url(#vein)" stroke="#2F4A78" stroke-width="3"')}
  {ellipse(ARTERY[0], ARTERY[1], ARTERY[1], 'id="femoral-artery" fill="url(#artery)" stroke="#8E211D" stroke-width="4"')}
  <path d="{path(curve(skin_y))}" fill="none" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#7FD3D8" fill-opacity="0.75" stroke="#0E8C98" stroke-width="4"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10" stroke-linecap="butt"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5" stroke-linecap="butt"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def _on_line(x):
    (x0, y0), (x1, y1) = NEEDLE_OUT, NEEDLE_TIP
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
