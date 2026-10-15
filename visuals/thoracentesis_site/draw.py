"""Thoracentesis - entry site on the back, with an over-the-rib inset (painted base, code-drawn markings).

Base (make_base.py): the owner's Gemini edits of the ESP positioning photo -
equipment removed, then re-posed seated and leaning forward over a padded
bedside table with the forearms on a pillow (the record's position, which
drops the scapula) - the bare back from behind, the patient's right on the
image right - plus, in the lower
left, an inset cropped from the approved chest_tube_rib_anatomy painting
(one intercostal space in coronal section, skin left, head up).

Record: posterior-lateral approach at the ultrasound-marked pocket; insert
along the superior margin of the lower rib; the bundle runs vein, artery,
nerve in the costal groove and is not reliably protected posteriorly, so
stay as lateral or anterior as the target allows; on the right the liver is
at risk below the 9th rib posteriorly.

Traced on the leaning-forward back (canvas px): C7 prominence (800, 290);
spine down the midline x = 800 to the waist at y = 1100; the right flank edge
near x = 1100 at the level of the site. About 2 px/mm (shoulder to shoulder
about 40 cm); the scapular tip, near T7, lies about y = 630.

Code-drawn: the marked site on the right posterolateral chest below the
scapular tip and toward the flank (a typical site; the level is set by
ultrasound), and the needle in the inset passing just over the lower rib into
the pleural space, clear of the bundle under the rib above.

Run: python3 visuals/thoracentesis_site/make_base.py && python3 visuals/thoracentesis_site/draw.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt  # noqa: E402

ASSET_ID = "thoracentesis_site"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

SITE = (1015.0, 735.0)
CHEST_RIGHT = [(800, 300), (1100, 300), (1200, 420), (1250, 640), (1105, 800), (1095, 1100), (800, 1100)]
INSET = (64, 690, 504, 1174)
S = 0.55                                  # inset px per rib-plate canvas px


def ins(x_mm, y_mm):
    """Rib-plate millimetres (x deep from skin, y caudal) to canvas px inside the inset."""
    return (INSET[0] + (110 + 20 * x_mm - 100) * S, INSET[1] + (600 + 20 * y_mm - 160) * S)


LOWER_RIB = ((22.3, 15.0), 4.3, 6.5)
UPPER_BUNDLE = ((24.9, -11.1), (28.2, -4.2))
PLEURAL_SPACE = ((30.2, -22.0), (39.5, 22.0))
NEEDLE_Y = 5.5
NEEDLE_FROM, NEEDLE_TIP = -1.0, 34.0

DEFS = """
<linearGradient id="g-steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.5" stop-color="#B9C0C7"/>
  <stop offset="1" stop-color="#6E777F"/></linearGradient>
"""


def rect(el_id, a, b, extra='fill="#000" opacity="0"'):
    p0, p1 = ins(*a), ins(*b)
    return f'<rect id="{el_id}" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" {extra}/>'


def build() -> str:
    rib_c = ins(*LOWER_RIB[0])
    n0, n1 = ins(NEEDLE_FROM, NEEDLE_Y), ins(NEEDLE_TIP, NEEDLE_Y)
    hub0 = (INSET[0] - 18, n0[1])
    bundle_c = ins((UPPER_BUNDLE[0][0] + UPPER_BUNDLE[1][0]) / 2, (UPPER_BUNDLE[0][1] + UPPER_BUNDLE[1][1]) / 2)
    labels = [
        Label(["Marked site"], anchor=(1130, 900), leader=[(1180, 858), (SITE[0], SITE[1] + 4)], target_id="site", emphasis=True),
        Label(["Vein, artery, nerve"], anchor=(530, 862), leader=[(520, 846), (bundle_c[0], bundle_c[1])], target_id="inset-bundle"),
        Label(["Needle"], anchor=(530, 1010), leader=[(520, 994), (n1[0] - 40, n1[1])], target_id="inset-needle"),
        Label(["Lower rib"], anchor=(530, 1150), leader=[(520, 1134), (rib_c[0] + 20, rib_c[1] + 20)], target_id="inset-lower-rib"),
    ]
    sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
    scale = 1600 / BASE_SIZE[0]
    base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                  f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
    chest = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in CHEST_RIGHT)
    rx, ry = LOWER_RIB[1] * 20 * S, LOWER_RIB[2] * 20 * S

    body = f"""
<g id="painting" data-base-sha256="{sha}">{base_image}</g>
<g id="anatomy">
  <polygon id="chest-right" points="{chest}" fill="#000" opacity="0"/>
  <line id="spine" x1="800" y1="290" x2="800" y2="1100" stroke="#000" stroke-width="10" opacity="0"/>
  <rect id="inset" x="{INSET[0]}" y="{INSET[1]}" width="{INSET[2] - INSET[0]}" height="{INSET[3] - INSET[1]}" fill="#000" opacity="0"/>
  <ellipse id="inset-lower-rib" cx="{fmt(rib_c[0])}" cy="{fmt(rib_c[1])}" rx="{fmt(rx)}" ry="{fmt(ry)}" fill="#000" opacity="0"/>
  {rect("inset-bundle", *UPPER_BUNDLE)}
  {rect("inset-pleural-space", *PLEURAL_SPACE)}
</g>

<g class="marking">
  <rect x="{fmt(hub0[0] - 30)}" y="{fmt(hub0[1] - 11)}" width="44" height="22" rx="6" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line x1="{fmt(hub0[0])}" y1="{fmt(n0[1] + 3)}" x2="{fmt(n1[0])}" y2="{fmt(n1[1] + 3)}" stroke="#1B2733" stroke-width="12" stroke-linecap="round" opacity="0.55"/>
  <line id="inset-needle" x1="{fmt(hub0[0])}" y1="{fmt(n0[1])}" x2="{fmt(n1[0])}" y2="{fmt(n1[1])}" stroke="url(#g-steel)" stroke-width="8" stroke-linecap="round"/>
  <circle id="inset-needle-tip" cx="{fmt(n1[0] - 3)}" cy="{fmt(n1[1])}" r="3" fill="#000" opacity="0"/>
  <circle cx="{fmt(SITE[0])}" cy="{fmt(SITE[1])}" r="26" fill="none" stroke="#F6F7F9" stroke-width="9"/>
  <circle cx="{fmt(SITE[0])}" cy="{fmt(SITE[1])}" r="26" fill="none" stroke="#D8432A" stroke-width="5"/>
  <circle id="site" cx="{fmt(SITE[0])}" cy="{fmt(SITE[1])}" r="8" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #B9C3C9; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
