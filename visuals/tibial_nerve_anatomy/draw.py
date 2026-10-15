"""Tibial nerve block - the right ankle in section behind the medial malleolus (layout).

Transverse section of the right ankle just above the tip of the medial
malleolus, under a probe transverse between the malleolus and the Achilles
tendon, as on the screen: anterior (the malleolus, tibialis posterior) on the
image left, posterior (the Achilles tendon) on the right, skin at the top.
Composition after NYSORA's tibial reverse-ultrasound plate (concept only, not
committed), which has the same way round; drawn from scratch.

Record: transducer transverse behind the medial malleolus; posterior tibial
artery with its paired veins; the nerve immediately posterior/lateral to the
artery; needle in-plane (out of plane if the Achilles, the malleolus or the
artery blocks the path); inject 5-10 mL around the nerve. NYSORA: inject into
the fascial plane enveloping the nerve; in-plane needle from the posterior
end.

Standard anatomy added: the flexor retinaculum over the tunnel; tibialis
posterior and flexor digitorum longus tendons just behind the malleolus;
artery, paired veins and nerve together in one fascial sheath (house style);
flexor hallucis longus deep; Kager's fat in front of the Achilles. 40 x 27 mm
field (true scale, as the sural section).

Millimetres from the skin over the nerve (x posterior = image right, y deep)
at 40 px/mm.

Run: python3 visuals/tibial_nerve_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "tibial_nerve_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 40.0
ORIGIN = (800.0, 110.0)
X0, X1 = -20.0, 20.0
L, R = X0 - 3, X1 + 3
SKIN, RET_TOP, RET_BOT = 1.4, 3.6, 4.1


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


MALLEOLUS = ((-15.0, 12.0), 8.0, 8.0)        # medial malleolus, just under the retinaculum
TP_TENDON = ((-5.0, 6.8), 2.4, 1.8)
FDL_TENDON = ((-0.6, 7.2), 1.9, 1.5)
SHEATH = ((6.0, 7.2), 4.6, 2.6)
ARTERY = ((3.6, 7.0), 1.1, 1.1)
VEINS = (((2.4, 8.3), 0.7, 0.7), ((4.9, 5.8), 0.7, 0.7))
NERVE = ((7.6, 7.4), 1.9, 1.5)
ACHILLES = ((16.5, 7.0), 5.0, 2.6)
FHL = [(-6.0, 13.0), (0.0, 10.6), (8.0, 10.4), (13.0, 11.6), (16.0, 15.0), (17.0, 30.0), (-6.5, 30.0)]
NEEDLE_ENTRY = (X1 - 3.0, 0.0)
NEEDLE_TIP = (9.9, 6.6)


def spread():
    return [(5.2, 5.9), (6.5, 4.9), (8.6, 4.8), (10.2, 5.7), (10.8, 7.3), (10.1, 9.0), (8.2, 9.9), (6.0, 9.6), (5.0, 8.4), (4.9, 7.1)]


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
    a = (e[0] - dx * 0.4, e[1] - dy * 0.4)
    probe_x1 = c((X1 - 6.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F8F6F0" stroke-width="7"'
    T = 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="5"'
    nerve, artery = c(NERVE[0]), c(ARTERY[0])
    labels = [
        Label(["Flexor retinaculum"], anchor=(40, 236), leader=[(470, 224), (520, c((0, (RET_TOP + RET_BOT) / 2))[1])], target_id="retinaculum"),
        Label(["Tibial nerve"], anchor=(880, 640), leader=[(1000, 600), (nerve[0] + 6, nerve[1] + 14)], target_id="nerve", emphasis=True),
        Label(["Posterior", "tibial artery"], anchor=(560, 800), leader=[(700, 740), (artery[0], artery[1] + 6)], target_id="artery"),
        Label(["Medial malleolus"], anchor=(40, 1000), leader=[(200, 960), (200, 700)], target_id="malleolus"),
        Label(["Achilles", "tendon"], anchor=(1300, 720), leader=[(1360, 680), (1460, 420)], target_id="achilles"),
        Label(["Flexor hallucis longus"], anchor=(460, 1130), leader=[(700, 1090), (800, 950)], target_id="fhl"),
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

    veins = "".join(ell(f"vein-{i}", v, 'fill="#3E5C9A" stroke="#2C4475" stroke-width="3"') for i, v in enumerate(VEINS))
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 60), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(SKIN, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="deep-fat" d="{path(band(RET_BOT, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="fhl" d="{path(FHL, closed=True, tension=0.3)}" {M}/>
  {ell("malleolus", MALLEOLUS, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  {ell("tp-tendon", TP_TENDON, T)}
  {ell("fdl-tendon", FDL_TENDON, T)}
  {ell("achilles", ACHILLES, 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="7"')}
  <path id="retinaculum" d="{path(band(RET_TOP, RET_BOT), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  {ell("sheath", SHEATH, 'fill="#F3E4C2" stroke="#F8F6F0" stroke-width="7"')}
  {ell("artery", ARTERY, 'fill="#C8463C" stroke="#8E2A23" stroke-width="3"')}
  {veins}
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
