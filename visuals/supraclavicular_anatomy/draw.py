"""Supraclavicular block - the right supraclavicular fossa in section under a linear probe (layout).

Section in the plane of the probe (transverse in the fossa, parallel to the
clavicle, aimed caudally), seen from the feet as on ultrasound: lateral on
the image left, medial on the right, skin at the top. Drawn from scratch on
the approved interscalene section layout (commit 6a33318): same scale,
palette and probe; nothing traced or copied from a published image.

Record: the plexus lies lateral and superficial to the subclavian artery,
which rests on the first rib; the pleura is deep to the rib and medial to
the artery. Needle in-plane from lateral to medial into the corner pocket:
deep to the plexus, superficial to the first rib, lateral to the artery.
15 mL there, then 5 mL at the plexus's superficial aspect. First rib not
seen: do not advance, the pleura is directly underneath.

Standard adult anatomy added (not in the record): the plexus as a cluster of
seven trunks and divisions; the middle scalene lateral and deep to it,
reaching the rib; the anterior scalene medial to the artery, inserting on
the rib; the subclavian vein medial to the anterior scalene; the clavicular
head of the sternocleidomastoid at the medial edge; the investing fascia
under the fat; the lung beneath the pleura, its dome rising medial to the
rib. Depths: artery centre about 1.6 cm, rib about 2 cm (typical adult;
they vary with habitus).

Markings: the probe, the needle from lateral with its tip in the corner
pocket, and the teal spread filling the pocket under the plexus.

Millimetres from the artery's lateral side line (x lateral, y deep from the
skin) at 28 px/mm. Adult proportions.

Run: python3 visuals/supraclavicular_anatomy/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "supraclavicular_anatomy"
PX_MM = 28.0
ORIGIN = (700.0, 130.0)           # before the mirror: x = 0 lands at canvas 900
X0, X1 = -25.0, 32.2              # medial (right) and lateral (left) frame edges in mm


def c(p):
    """mm (x lateral, y deep) -> canvas; lateral is drawn on the left."""
    return (1600 - (ORIGIN[0] + p[0] * PX_MM), ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=40):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom):
    return curve(top) + list(reversed(curve(bottom)))


ARTERY = ((-4.0, 15.6), 3.6)
VEIN = ((-20.2, 14.0), 4.4, 3.0)
# Trunks and divisions, superficial and lateral to the artery.
PLEXUS = {
    "trunk-a": ((1.8, 12.8), 1.3),
    "trunk-b": ((4.4, 12.6), 1.4),
    "trunk-c": ((6.9, 11.2), 1.3),
    "trunk-d": ((3.0, 10.0), 1.4),
    "trunk-e": ((5.6, 9.0), 1.3),
    "trunk-f": ((8.3, 9.0), 1.1),
    "trunk-g": ((1.4, 8.2), 1.1),
}
RIB = [(-10, 21.2), (-6, 19.6), (0, 19.3), (6, 19.6), (9.5, 20.8), (10.3, 23.4), (6.5, 25.4), (0, 25.7),
       (-6, 25.3), (-10, 23.6)]
MSM = [(10.6, 13.6), (13.5, 10.6), (20, 9.6), (X1 + 3, 9.8), (X1 + 3, 26.4), (22, 26.2), (14, 25.0), (10.9, 22.0),
       (10.4, 18)]
ASM = [(-8.2, 10.2), (-11, 8.8), (-14.4, 10.2), (-15.3, 14.5), (-13.6, 19.4), (-10.6, 21.0), (-8.4, 19.0),
       (-7.9, 14.2)]
SCM = [(-16.6, 2.4), (-20, 2.1), (X0 - 3, 2.0), (X0 - 3, 8.6), (-22, 8.3), (-18.6, 6.2)]
FASCIA = [(X1 + 3, 6.4), (24, 6.2), (12, 5.8), (2, 5.6), (-8, 5.6), (-16.4, 5.4)]
# One continuous pleural line, split where it turns up past the rib's medial end.
PLEURA_DEEP = [(X1 + 3, 28.6), (20, 28.2), (12, 27.6), (4, 27.2), (-3, 26.9), (-7, 26.3), (-9, 25.6)]   # under the rib
PLEURA = [(-9, 25.6), (-11.5, 24.0), (-16, 23.3), (-21, 23.4), (X0 - 3, 23.6)]           # medial to the rib
PROBE_LATERAL_X = 22.0
NEEDLE_ENTRY = (29.0, 0.0)
NEEDLE_TIP = (1.6, 17.4)          # corner pocket: under the plexus, above the rib, lateral to the artery


def ellipse(center, rx, ry, attrs, rot=0.0):
    p = c(center)
    return (f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" '
            f'transform="rotate({fmt(rot)} {fmt(p[0])} {fmt(p[1])})" {attrs}/>')


def lung():
    """Lung beneath both pleural lines, to the bottom of the frame."""
    top = list(reversed(PLEURA)) + list(reversed(PLEURA_DEEP))[1:]
    return top + [(X1 + 3, 29.6), (X1 + 3, 60), (X0 - 3, 60), (X0 - 3, 24.6)]


def spread():
    """Teal pool filling the corner pocket and cupping the plexus's deep side."""
    return [(0.1, 14.6), (-0.1, 17.0), (0.0, 18.6), (2.5, 18.7), (6.5, 18.4), (9.4, 16.8), (9.8, 14.2),
            (8.6, 12.9), (6.2, 14.4), (3.2, 13.9), (1.6, 13.8)]


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8483F"/><stop offset="1" stop-color="#8A2D28"/></linearGradient>
<radialGradient id="art-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="lung-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9C4C4"/><stop offset="1" stop-color="#D9A9AC"/></linearGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.25, e[1] - dy * 0.25)
    probe_x = c((PROBE_LATERAL_X, 0))[0]
    labels = [
        Label(["Brachial plexus"], anchor=(470, 290), leader=[(640, 305), c(PLEXUS["trunk-e"][0])], target_id="trunk-e", emphasis=True),
        Label(["Subclavian artery"], anchor=(1060, 330), leader=[(1180, 345), c((-5.5, 13.6))], target_id="artery"),
        Label(["Middle scalene"], anchor=(40, 1010), leader=[(160, 960), c((18, 18))], target_id="msm"),
        Label(["First rib"], anchor=(560, 1150), leader=[(660, 1100), c((2, 23))], target_id="rib"),
        Label(["Pleura"], anchor=(1260, 1010), leader=[(1330, 960), c((-16, 23.3))], target_id="pleura"),
    ]
    plexus = "".join(ellipse(ct, r, r * 0.92, f'id="{k}" fill="#EFCB5A" stroke="#B8962E" stroke-width="4"') for k, (ct, r) in PLEXUS.items())
    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="skin" d="{path(band(lambda x: 0, lambda x: 60), closed=True, tension=0.3)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(lambda x: 1.6, lambda x: 60), closed=True, tension=0.3)}" fill="url(#fat)"/>
  <path id="lung" d="{path(lung(), closed=True, tension=0.25)}" fill="url(#lung-grad)"/>
  <path id="pleura" d="{path(PLEURA, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="8"/>
  <path id="pleura-deep" d="{path(PLEURA_DEEP, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="8"/>
  <path id="rib" d="{path(RIB, closed=True, tension=0.6)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="msm" d="{path(MSM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="asm" d="{path(ASM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="scm" d="{path(SCM, closed=True, tension=0.6)}" fill="url(#muscle)" stroke="#6E221E" stroke-width="3"/>
  <path id="investing-fascia" d="{path(FASCIA, tension=0.8)}" fill="none" stroke="#F8F6F0" stroke-width="7"/>
  {plexus}
  {ellipse(VEIN[0], VEIN[1], VEIN[2], 'id="vein" fill="url(#vein-grad)" stroke="#2F4A78" stroke-width="4"')}
  {ellipse(ARTERY[0], ARTERY[1], ARTERY[1], 'id="artery" fill="url(#art-grad)" stroke="#8E211D" stroke-width="6"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.8)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="3"/>
  <rect id="probe" x="{fmt(probe_x)}" y="-60" width="{fmt(1700 - probe_x)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(probe_x + 18)}" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(1700 - probe_x)}" height="14" rx="6" fill="#3E454C"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="4" fill="#5E6670"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
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
