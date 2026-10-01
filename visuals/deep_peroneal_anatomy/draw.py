"""Deep peroneal nerve block - the right anterior ankle in section under a linear probe.

Flat code layout for the owner's Gemini repaint (visuals/PLAYBOOK.md). The
anatomy half of the pair; deep_peroneal_patient_position shows this probe on
the patient.

Transverse section of the right ankle at the level of the malleoli, patient
supine, seen from the feet as on ultrasound: lateral on the image left,
medial on the right, skin at the top - the same way round as the
positioning plate.

Record: the deep peroneal nerve runs with the anterior tibial artery between
the extensor hallucis longus and extensor digitorum longus tendons, usually
lateral to the artery; inject next to the artery. Added, standard anatomy
not in the record: tibialis anterior tendon most medial; paired venae
comitantes beside the artery; the extensor retinaculum over the tendons;
the distal tibia below. Sizes are typical adult values: artery about 3 mm,
nerve about 2 mm, at about 7 mm deep; depths vary with habitus.

Markings: the probe (medial edge to about 1 cm short of the lateral edge),
the needle in-plane from lateral (an addition: the record does not name the
approach) with its tip lateral to the nerve, and the teal injectate around
the artery and nerve.

Millimetres from the artery centre (x lateral, y deep from the skin) at
40 px/mm.

Run: python3 visuals/deep_peroneal_anatomy/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "deep_peroneal_anatomy"
PX_MM = 40.0
ORIGIN = (800.0, 330.0)           # canvas of the skin surface above the artery
X0, X1 = -20.0, 20.0              # frame edges in mm (lateral positive)


def c(p):
    """mm (x lateral, y deep) -> canvas; lateral is drawn on the left."""
    return (ORIGIN[0] - p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def curve(fn, x0=X0 - 3, x1=X1 + 3, n=40):
    return [(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def band(top, bottom, x0=X0 - 3, x1=X1 + 3):
    return curve(top, x0, x1) + list(reversed(curve(bottom, x0, x1)))


def retinaculum_y(x):
    return 3.4 + 0.002 * x * x


def bone_y(x):
    return 11.6 + 0.006 * x * x


ARTERY = ((0.0, 7.0), 1.5)
VENAE = [((-2.0, 7.4), 0.9, 0.7), ((1.6, 8.5), 0.8, 0.6)]
NERVE = ((2.9, 6.8), 1.1, 0.85)
TIB_ANT = ((-14.0, 6.0), 3.8, 2.4)
EHL = ((-5.8, 6.1), 2.2, 1.7)
EDL = [((8.6, 6.4), 1.6, 1.2), ((12.2, 6.1), 1.6, 1.2), ((15.8, 6.3), 1.5, 1.15)]

PROBE = (-23.0, 10.0)                       # footprint, mm (medial edge to 1 cm short of lateral)
NEEDLE_OUT, NEEDLE_ENTRY, NEEDLE_TIP = (24.0, -6.3), (14.5, 0.0), (4.4, 6.75)


def spread():
    """Teal pool around the artery and nerve, under the retinaculum, above the bone."""
    pts = []
    for i in range(36):
        t = 2 * math.pi * i / 36
        pts.append((1.0 + 4.6 * math.cos(t), 7.3 + 2.0 * math.sin(t)))
    return pts


def ellipse(center, rx, ry, attrs):
    p = c(center)
    return f'<ellipse cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(rx * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<radialGradient id="art-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein-grad" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""

TENDON = 'fill="#F3EEE2" stroke="#B8AE98" stroke-width="4"'


def build() -> str:
    skin = band(lambda x: 0.0, lambda x: 40)
    fat = band(lambda x: 1.6, lambda x: 40)
    bone = band(bone_y, lambda x: 40)
    a, e, t = c(NEEDLE_OUT), c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    p0, p1 = c((PROBE[0], 0)), c((PROBE[1], 0))
    left, right = min(p0[0], p1[0]), max(p0[0], p1[0])

    labels = [
        Label(["Deep peroneal n."], anchor=(150, 980), leader=[(420, 930), c((2.9, 6.8))], target_id="deep-peroneal-nerve",
              emphasis=True),
        Label(["Anterior tibial a."], anchor=(560, 1100), leader=[(760, 1050), c((0, 7.4))], target_id="anterior-tibial-artery"),
        Label(["EHL"], anchor=(1060, 1000), leader=[(1080, 960), c((-5.8, 6.6))], target_id="ehl"),
        Label(["EDL"], anchor=(170, 760), leader=[(250, 720), c((12.2, 6.4))], target_id="edl"),
    ]

    body = f"""
<g id="anatomy" clip-path="url(#frame)">
  <path id="skin" d="{path(skin, closed=True, tension=0.3)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(fat, closed=True, tension=0.3)}" fill="url(#fat)"/>
  <path id="bone" d="{path(bone, closed=True, tension=0.3)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  <path id="retinaculum" d="{path(curve(retinaculum_y))}" fill="none" stroke="#F8F6F0" stroke-width="10"/>
  <path d="{path(curve(retinaculum_y))}" fill="none" stroke="#9E927C" stroke-width="3"/>
  {ellipse(*TIB_ANT, 'id="tibialis-anterior" ' + TENDON)}
  {ellipse(*EHL, 'id="ehl" ' + TENDON)}
  <g id="edl-tendons">{"".join(ellipse(*t_, ('id="edl" ' if i == 1 else '') + TENDON) for i, t_ in enumerate(EDL))}</g>
  {"".join(ellipse(*v, 'fill="url(#vein-grad)" stroke="#2F4A78" stroke-width="3"') for v in VENAE)}
  {ellipse(ARTERY[0], ARTERY[1], ARTERY[1], 'id="anterior-tibial-artery" fill="url(#art-grad)" stroke="#8E211D" stroke-width="5"')}
  {ellipse(*NERVE, 'id="deep-peroneal-nerve" fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.5)}" fill="#7FD3D8" fill-opacity="0.55" stroke="#0E8C98" stroke-width="4"/>
  {ellipse(*NERVE, 'fill="none" stroke="#B8962E" stroke-width="4"')}
  <rect id="probe" x="{fmt(left)}" y="{fmt(p0[1] - 150)}" width="{fmt(right - left)}" height="150" rx="26" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10" stroke-linecap="butt"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5" stroke-linecap="butt"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="3" fill="#5E6670"/>
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
