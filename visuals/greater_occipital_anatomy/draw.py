"""Greater occipital (suboccipital) nerve block - the back of the skull (layout).

The skull seen from behind, head at the top, zoomed on the right half: the
patient's right is on the image RIGHT (seen from behind). The midline and the
external occipital protuberance sit near the left third; the superior nuchal
line runs out to the right mastoid process.

Record: palpate the external occipital protuberance and the mastoid; the
nerve lies about one-third of the way from the protuberance to the mastoid,
on the superior nuchal line, about 2 cm lateral to the protuberance, just
medial to the occipital artery (position varies). The nerve is the posterior
ramus of C2 and reaches the scalp at the superior nuchal line; insert
perpendicular to the skin until resistance.

Drawn in code over the painting: the dashed protuberance-to-mastoid line with
its one-third mark, the nerve (yellow; dashed where it is deep, below the
line), the occipital artery (red), and the entry point.

Millimetres from the protuberance (x toward the patient's right = image
right, y down) at 11 px/mm.

Run: python3 visuals/greater_occipital_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "greater_occipital_anatomy"
BASE = Path(__file__).with_name("base.jpg")
PX_MM = 11.0
ORIGIN = (545.0, 700.0)          # canvas of the external occipital protuberance


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


EOP = (0.0, 0.0)
MASTOID_PALP = (64.0, 6.0)        # the palpable bulk of the mastoid, level with the line's end
THIRD = (MASTOID_PALP[0] / 3, MASTOID_PALP[1] / 3)
NUCHAL = [(0, 0), (12, -0.5), (24, 1.0), (36, 2.5), (48, 4.0), (58, 6.0), (64, 8.0)]
MASTOID = [(61, 5), (71, 4), (77, 18), (73, 36), (66, 38), (61, 22)]
SKULL = [(-50, -75), (95, -75), (95, -20), (88, 10), (77, 36), (70, 40), (62, 31), (48, 25), (30, 28),
         (12, 30), (0, 30), (-12, 30), (-50, 32)]
ATLAS = [(-26, 38), (0, 35), (26, 38), (28, 43), (0, 40), (-28, 43)]       # posterior arch of C1
NERVE_SCALP = [(21.3, 2.0), (20.6, -18), (19.0, -40), (16.0, -72)]
NERVE_DEEP = [(14.0, 44), (17.5, 22), (21.3, 2.0)]
ARTERY = [(50, 44), (38, 24), (28.5, 6), (27.0, 0), (28.5, -10), (26.0, -22), (30.0, -34), (27.0, -48),
          (31.0, -60), (29.0, -75)]
ENTRY = (19.6, -0.8)          # just above the line, clear of the one-third tick

DEFS = """
<linearGradient id="bone" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EFE3C8"/><stop offset="1" stop-color="#DCCBA6"/></linearGradient>
"""


def build() -> str:
    e, eop, mp, third = c(ENTRY), c(EOP), c(MASTOID_PALP), c(THIRD)
    labels = [
        Label(["Greater occipital", "nerve"], anchor=(60, 140), leader=[(330, 180), c(NERVE_SCALP[2])],
              target_id="gon", emphasis=True),
        Label(["Occipital artery"], anchor=(1060, 120), leader=[(1150, 140), c(ARTERY[7])], target_id="occipital-artery"),
        Label(["External occipital", "protuberance"], anchor=(40, 1000), leader=[(250, 960), (eop[0] - 8, eop[1] + 8)],
              target_id="eop"),
        Label(["Mastoid"], anchor=(1330, 1150), leader=[(1380, 1110), c((69, 26))], target_id="mastoid"),
        Label(["Superior nuchal line"], anchor=(980, 620), leader=[(1100, 650), c(NUCHAL[4])], target_id="nuchal-line"),
        Label(["One-third"], anchor=(700, 1000), leader=[(760, 960), (third[0], third[1] + 14)], target_id="third-mark"),
    ]
    painted = BASE.exists()
    if painted:
        from PIL import Image
        bw_, bh_ = Image.open(BASE).size
        height = 1600 * bh_ / bw_
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - height) / 2)}" width="1600" '
                      f'height="{fmt(height)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if os.environ.get("DEBUG") == "1" else 0}"'
    else:
        base_attr = base_image = layout_attr = ""
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <path id="skull" d="{path(SKULL, closed=True, tension=0.3)}" fill="url(#bone)" stroke="#B9A884" stroke-width="3"/>
  <path id="nuchal-line" d="{path(NUCHAL, tension=0.8)}" fill="none" stroke="#A8977A" stroke-width="10" stroke-linecap="round"/>
  <path id="mastoid" d="{path(MASTOID, closed=True, tension=0.6)}" fill="#E6D7B6" stroke="#A8977A" stroke-width="3"/>
  <circle id="eop" cx="{fmt(eop[0])}" cy="{fmt(eop[1])}" r="{fmt(5 * PX_MM)}" fill="#E6D7B6" stroke="#A8977A" stroke-width="3"/>
  <path id="atlas" d="{path(ATLAS, closed=True, tension=0.5)}" fill="#E6D7B6" stroke="#A8977A" stroke-width="3"/>
  <line id="midline" x1="{fmt(eop[0])}" y1="0" x2="{fmt(eop[0])}" y2="1200" stroke="#C9B994" stroke-width="2" stroke-dasharray="4 10"/>
</g>

<g class="marking">
  <line id="measure" x1="{fmt(eop[0])}" y1="{fmt(eop[1])}" x2="{fmt(mp[0])}" y2="{fmt(mp[1])}" stroke="#1C2530" stroke-width="4" stroke-dasharray="14 10" opacity="0.75"/>
  <path id="occipital-artery" d="{path(ARTERY, tension=0.9)}" fill="none" stroke="#C8322B" stroke-width="9" stroke-linecap="round"/>
  <path id="gon-deep" d="{path(NERVE_DEEP, tension=0.8)}" fill="none" stroke="#E8C547" stroke-width="8" stroke-dasharray="14 10" stroke-linecap="round"/>
  <path id="gon" d="{path(NERVE_SCALP, tension=0.8)}" fill="none" stroke="#E8C547" stroke-width="9" stroke-linecap="round"/>
  <line id="third-mark" x1="{fmt(third[0])}" y1="{fmt(third[1] - 22)}" x2="{fmt(third[0])}" y2="{fmt(third[1] + 22)}" stroke="#1C2530" stroke-width="6" stroke-linecap="round"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="12" fill="#D8432A" stroke="#F6F7F9" stroke-width="4"/>
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
