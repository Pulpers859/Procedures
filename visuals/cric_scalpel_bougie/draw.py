"""Cricothyrotomy, scalpel-bougie: midsagittal layout plate.

Midline section, patient supine: head image-left, chest image-right, front
of the neck along the top. Teaching point: the number 10 blade and the
bougie go through ONE opening in the cricothyroid membrane, the blade's sharp
edge faces the feet, and the bougie turns down the open trachea toward the
feet.

This plate is the geometry reference handed to Gemini, which is asked to
repaint it without moving anything, and it is a candidate plate in its own
right. It deliberately has no text, because text in a reference leaks into
the painting.

Scale: about 10 px per mm. Tracheal lumen about 18 mm, cricothyroid membrane
about 9 mm long, cricoid arch about 6 mm long in the midline, posterior
cricoid lamina about 22 mm long.

Run: python3 visuals/cric_scalpel_bougie/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import document, fmt, smooth_path  # noqa: E402

ASSET_ID = "cric_scalpel_bougie"

SKIN_Y = 330.0          # skin surface over the larynx
FAT_BOTTOM = 388.0
LUMEN_TOP = 440.0       # anterior mucosa of larynx and trachea
LUMEN_BOTTOM = 650.0    # posterior wall
FRONT_WALL = (400.0, LUMEN_TOP)   # cartilage band y range on the front wall

THYROID_X = (350.0, 600.0)        # front wall only: no back wall in the midline
MEMBRANE_X = (600.0, 690.0)
CRICOID_ARCH_X = (690.0, 752.0)
CRICOID_LAMINA_X = (520.0, 752.0) # tall back plate: extends toward the head
RING_START, RING_W, RING_GAP = 780.0, 46.0, 24.0

INCISION_X = 650.0
BLADE_TIP = (648.0, 525.0)         # 8.5 mm inside the lumen, 12 mm short of the back wall


def rounded_rect(x0, y0, x1, y1, r):
    return (f"M{fmt(x0 + r)},{fmt(y0)} H{fmt(x1 - r)} Q{fmt(x1)},{fmt(y0)} {fmt(x1)},{fmt(y0 + r)} "
            f"V{fmt(y1 - r)} Q{fmt(x1)},{fmt(y1)} {fmt(x1 - r)},{fmt(y1)} H{fmt(x0 + r)} "
            f"Q{fmt(x0)},{fmt(y1)} {fmt(x0)},{fmt(y1 - r)} V{fmt(y0 + r)} Q{fmt(x0)},{fmt(y0)} {fmt(x0 + r)},{fmt(y0)} Z")


def build() -> str:
    # Thyroid cartilage in the midline: a front-wall bar that thickens at the
    # laryngeal prominence near its upper (cranial, image-left) end.
    thyroid = smooth_path([(THYROID_X[0], 404), (390, 386), (440, 380), (520, 392), (THYROID_X[1], 402),
                           (THYROID_X[1], 436), (520, 438), (440, 440), (390, 440), (THYROID_X[0], 438)], closed=True)
    cricoid_arch = rounded_rect(CRICOID_ARCH_X[0], 396, CRICOID_ARCH_X[1], 446, 12)
    cricoid_lamina = smooth_path([(CRICOID_LAMINA_X[0], 648), (560, 628), (650, 638), (CRICOID_LAMINA_X[1], 640),
                                  (CRICOID_LAMINA_X[1], 700), (650, 702), (560, 700), (CRICOID_LAMINA_X[0], 690)], closed=True)
    rings = []
    x = RING_START
    while x < 1640:
        rings.append(rounded_rect(x, 404, x + RING_W, 440, 9))
        x += RING_W + RING_GAP

    # #10 blade, sharp curved belly facing image-right (feet), straight back
    # facing image-left (head), tip at the bottom.
    tip = BLADE_TIP
    blade = (f"M{fmt(INCISION_X - 12)},250 L{fmt(INCISION_X - 12)},{fmt(tip[1] - 60)} "
             f"Q{fmt(INCISION_X - 12)},{fmt(tip[1] - 8)} {fmt(tip[0])},{fmt(tip[1])} "
             f"Q{fmt(INCISION_X + 44)},{fmt(tip[1] - 70)} {fmt(INCISION_X + 40)},{fmt(tip[1] - 170)} "
             f"L{fmt(INCISION_X + 34)},250 Z")
    handle = rounded_rect(INCISION_X - 20, -40, INCISION_X + 40, 252, 10)

    # Bougie: one line, enters at the incision alongside the blade, turns
    # toward the feet and runs down the middle of the tracheal lumen.
    mid = (LUMEN_TOP + LUMEN_BOTTOM) / 2
    # It runs along the blade's blunt back (image-left), so both are visible in
    # the same opening, then curves under the blade tip toward the feet.
    bougie = smooth_path([(560, -20), (598, 120), (620, 260), (624, SKIN_Y), (624, 420), (628, 486),
                          (650, 532), (700, mid), (800, mid), (1000, mid), (1300, mid), (1640, mid)])

    grip = "".join(f'<line x1="{fmt(INCISION_X - 8)}" y1="{y}" x2="{fmt(INCISION_X + 28)}" y2="{y}"/>'
                   for y in range(40, 210, 22))

    vertebrae = "".join(
        f'<path d="{rounded_rect(x0, 830, x0 + 150, 960, 16)}" fill="#E8DCC2" stroke="#B9A67E" stroke-width="3"/>'
        for x0 in range(120, 1600, 190))

    body = f"""
<g id="anatomy">
  <rect x="0" y="{fmt(SKIN_Y)}" width="1600" height="{fmt(1200 - SKIN_Y)}" fill="#F0D3C2"/>
  <path d="M0,{fmt(SKIN_Y - 180)} C120,{fmt(SKIN_Y - 200)} 200,{fmt(SKIN_Y - 40)} 300,{fmt(SKIN_Y)} L0,{fmt(SKIN_Y)} Z" fill="#F0D3C2"/>
  <path d="M0,{fmt(SKIN_Y - 180)} C120,{fmt(SKIN_Y - 200)} 200,{fmt(SKIN_Y - 40)} 300,{fmt(SKIN_Y)} L1600,{fmt(SKIN_Y)}" fill="none" stroke="#C7917B" stroke-width="4"/>
  <rect id="fat" x="0" y="{fmt(SKIN_Y + 18)}" width="1600" height="{fmt(FAT_BOTTOM - SKIN_Y - 18)}" fill="#F3DE9C"/>

  <rect id="esophagus" x="500" y="712" width="1100" height="58" rx="26" fill="#C98372"/>
  <rect x="0" y="788" width="1600" height="30" fill="#E7C4B3"/>
  {vertebrae}

  <rect id="airway-lumen" rx="60" x="300" y="{fmt(LUMEN_TOP)}" width="1340" height="{fmt(LUMEN_BOTTOM - LUMEN_TOP)}" fill="#7E5A63"/>
  <rect id="trachea-lumen" x="752" y="{fmt(LUMEN_TOP)}" width="888" height="{fmt(LUMEN_BOTTOM - LUMEN_TOP)}" fill="#7E5A63"/>
  <line id="posterior-tracheal-wall" x1="752" y1="{fmt(LUMEN_BOTTOM + 4)}" x2="1640" y2="{fmt(LUMEN_BOTTOM + 4)}" stroke="#D99A95" stroke-width="10"/>

  <path id="vocal-folds" d="M440,448 C470,500 500,560 548,634 L566,628 C520,556 492,500 470,446 Z" fill="#E5A3A0"/>

  <ellipse id="hyoid" cx="262" cy="410" rx="24" ry="34" fill="#E8DCC2" stroke="#B9A67E" stroke-width="3"/>
  <path d="M286,412 L{fmt(THYROID_X[0])},414" stroke="#E3C9C9" stroke-width="10"/>
  <path id="thyroid-cartilage" d="{thyroid}" fill="#B8CBDA" stroke="#6E8AA1" stroke-width="4"/>
  <rect id="cricothyroid-membrane" x="{fmt(MEMBRANE_X[0])}" y="414" width="{fmt(MEMBRANE_X[1] - MEMBRANE_X[0])}" height="16" fill="#E3B9B4" stroke="#B88580" stroke-width="2"/>
  <path id="cricoid-arch" d="{cricoid_arch}" fill="#B8CBDA" stroke="#6E8AA1" stroke-width="4"/>
  <path id="cricoid-lamina" d="{cricoid_lamina}" fill="#B8CBDA" stroke="#6E8AA1" stroke-width="4"/>
  <g id="tracheal-rings" fill="#B8CBDA" stroke="#6E8AA1" stroke-width="3">{"".join(f'<path d="{r}"/>' for r in rings)}</g>

  <g id="scalpel">
    <path id="scalpel-handle" d="{handle}" fill="#A9AFB5" stroke="#5E656C" stroke-width="3"/>
    <g stroke="#6E757C" stroke-width="4">{grip}</g>
    <path id="blade" d="{blade}" fill="#DDE2E6" stroke="#5E656C" stroke-width="3"/>
    <path id="blade-edge" d="M{fmt(tip[0])},{fmt(tip[1])} Q{fmt(INCISION_X + 44)},{fmt(tip[1] - 70)} {fmt(INCISION_X + 40)},{fmt(tip[1] - 170)}" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  </g>
  <!-- Bougie in the same opening, along the blade's blunt back. -->
  <path id="bougie" d="{bougie}" fill="none" stroke="#EFE3C4" stroke-width="18" stroke-linecap="round"/>
  <path d="{bougie}" fill="none" stroke="#B8A57A" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F7F6F2; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
