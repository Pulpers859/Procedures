"""Ulnar nerve block - the right mid-forearm in section under a linear probe (layout).

Transverse section of the right forearm at mid-forearm, palm up, under a probe
on the volar-ulnar side, as on the screen: radial (FDS) on the image left,
ulnar (FCU, the ulna) on the right, volar skin at the top - the same way round
as the approved median section. Composition after NYSORA's ulnar
reverse-ultrasound plate (concept only, not committed); drawn from scratch.

Record: probe transverse on the volar forearm, slid medially to the ulnar
artery; the ulnar nerve lies directly medial to the artery, oval or
triangular, deep to FCU, in the same fascial plane as the artery; slide
proximally to where the two have separated; needle in-plane from the medial
side; inject along the medial surface of the nerve first, then at the
nerve/artery border, 5-10 mL. NYSORA: the FCU tendon lies just superficial to
the artery and can be mistaken for the nerve.

Standard anatomy added: FDS radial, FCU ulnar and superficial, FDP deep with
the ulna under it on the ulnar side; the artery and nerve together in one
fascial compartment between FDS, FCU and FDP (house style: never in fat).

Millimetres from the skin over the artery (x ulnar = image right, y deep) at
26 px/mm.

Run: python3 visuals/ulnar_nerve_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ulnar_nerve_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (800.0, 110.0)
X0, X1 = -30.8, 30.8
L, R = X0 - 3, X1 + 3
SKIN, FASCIA_TOP, FASCIA_BOT = 1.5, 4.4, 4.75


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


FCU = [(-0.6, FASCIA_BOT), (R, FASCIA_BOT), (R, 15.6), (16, 16.4), (10.5, 14.6), (7.2, 12.8), (5.4, 10.2), (2.4, 9.3), (0.0, 8.0)]
FDS = [(L, FASCIA_BOT), (-0.6, FASCIA_BOT), (0.0, 8.0), (-1.4, 9.4), (-4.2, 10.2), (-10, 10.8), (-20, 11.6), (L, 12.0)]
FDP = [(L, 12.0), (-20, 11.6), (-10, 10.8), (-4.2, 10.2), (-2.6, 12.0), (0.0, 13.4), (4.0, 13.8), (7.2, 12.8), (10.5, 14.6), (16, 16.4), (R, 15.6), (R, 44), (L, 44)]
SHEATH = [(-4.2, 10.2), (-1.4, 9.4), (0.0, 8.0), (2.4, 9.3), (5.4, 10.2), (7.2, 12.8), (4.0, 13.8), (0.0, 13.4), (-2.6, 12.0)]
ARTERY = ((-0.5, 11.5), 1.15, 1.15)
NERVE = ((3.4, 11.5), 1.55, 1.15)
FCU_TENDON = ((0.8, 6.4), 1.6, 0.9)
ULNA = ((17.0, 24.0), 7.4, 6.0)
NEEDLE_ENTRY = (X1 - 4.6, 0.0)
NEEDLE_TIP = (5.6, 11.0)


def spread():
    return [(1.0, 10.0), (2.6, 9.6), (4.6, 9.7), (6.2, 10.4), (6.6, 11.6), (5.8, 12.8), (3.8, 13.2), (1.8, 13.0), (0.8, 12.2), (0.5, 11.0)]


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
    probe_x1 = c((X1 - 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F8F6F0" stroke-width="7"'
    nerve, artery = c(NERVE[0]), c(ARTERY[0])
    labels = [
        Label(["Ulnar nerve"], anchor=(1000, 560), leader=[(1060, 520), (nerve[0] + 10, nerve[1] + 12)], target_id="nerve", emphasis=True),
        Label(["Ulnar artery"], anchor=(330, 560), leader=[(600, 520), (artery[0] - 6, artery[1] + 10)], target_id="artery"),
        Label(["Flexor carpi", "ulnaris"], anchor=(1220, 340), leader=[(1210, 324), (1150, 324)], target_id="fcu"),
        Label(["FDS"], anchor=(80, 260), leader=[(200, 244), (300, 244)], target_id="fds"),
        Label(["FDP"], anchor=(80, 900), leader=[(200, 884), (300, 884)], target_id="fdp"),
        Label(["Ulna"], anchor=(1380, 1110), leader=[(1420, 1066), (1300, 800)], target_id="ulna"),
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
  <path id="subcutaneous-fat" d="{path(band(SKIN, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="fdp" d="{path(FDP, closed=True, tension=0.3)}" {M}/>
  <path id="fds" d="{path(FDS, closed=True, tension=0.3)}" {M}/>
  <path id="fcu" d="{path(FCU, closed=True, tension=0.3)}" {M}/>
  {ell("fcu-tendon", FCU_TENDON, 'fill="#F1EEE6" stroke="#F8F6F0" stroke-width="5"')}
  {ell("ulna", ULNA, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="8"')}
  <path id="antebrachial-fascia" d="{path(band(FASCIA_TOP, FASCIA_BOT), closed=True, tension=0.2)}" fill="#F8F6F0"/>
  <path id="sheath" d="{path(SHEATH, closed=True, tension=0.3)}" fill="#F3E4C2" stroke="#F8F6F0" stroke-width="7"/>
  {ell("artery", ARTERY, 'fill="#C8463C" stroke="#8E2A23" stroke-width="3"')}
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
