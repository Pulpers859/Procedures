"""Lumbar puncture - the needle's path through the layers (layout).

A midline sagittal section of the lumbar spine at L3-L4, as an atlas
cut-away: the back's skin at the top, the head to the image right (the same
way round as the landmark plate), the vertebral bodies at the bottom.

Record: midline approach, needle angled slightly cephalad, through skin,
subcutaneous tissue, supraspinous ligament, interspinous ligament,
ligamentum flavum, then dura; introducer first, then the atraumatic needle
through it.

Standard adult anatomy added: spinous processes 3.8 cm apart, about 2.2 cm
tall in section with 1.6 cm gaps; the supraspinous ligament over their tips;
the ligamentum flavum between the laminae about 4 cm deep; the epidural fat;
the dura about 5 cm from the skin; the thecal sac about 1.4 cm across with
cauda equina roots; the posterior longitudinal ligament, vertebral bodies
and the L3-L4 disc. Depths vary with habitus.

Code-drawn: the introducer, the spinal needle with its pencil-point tip in
the CSF, at about 12 degrees cephalad.

Millimetres from the skin over the L3-L4 interspace (x toward the head =
image right, y deep) at 14 px/mm.

Run: python3 visuals/lp_needle_trajectory/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "lp_needle_trajectory"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 14.0
ORIGIN = (800.0, 150.0)            # canvas of the skin over the interspace
SEG = 38.0
L, R = -60.0, 60.0                 # beyond the frame edges, mm

SKIN, FAT, TIP_Y = 2.0, 12.0, 14.0
LAMINA_Y0, LAMINA_Y1 = 39.0, 46.0
DURA_POST, DURA_ANT = 50.0, 64.0
PLL_Y, BODY_Y = 65.5, 67.0
ENTRY = (-6.0, 0.0)
TIP = (5.9, 54.0)
INTRODUCER_DEPTH = 26.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def rect(el_id, x0, y0, x1, y1, attrs):
    a, b = c((x0, y0)), c((x1, y1))
    return f'<rect id="{el_id}" x="{fmt(a[0])}" y="{fmt(a[1])}" width="{fmt(b[0] - a[0])}" height="{fmt(b[1] - a[1])}" {attrs}/>'


def spinous(xc):
    """A lumbar spinous process and its lamina in midline section."""
    return [(xc - 11, TIP_Y + 1.5), (xc - 6, TIP_Y), (xc + 6, TIP_Y), (xc + 11, TIP_Y + 1.5), (xc + 10, 30),
            (xc + 12, LAMINA_Y0), (xc + 12, LAMINA_Y1), (xc - 14, LAMINA_Y1 - 1), (xc - 13, LAMINA_Y0), (xc - 10, 30)]


CENTRES = {"l2": 2 * SEG - SEG / 2, "l3": SEG / 2, "l4": -SEG / 2, "l5": -SEG - SEG / 2}

DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="g-steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.45" stop-color="#B9C1C8"/>
  <stop offset="1" stop-color="#6E777F"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def needle() -> str:
    e, t = c(ENTRY), c(TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    back = (e[0] - ux * 150, e[1] - uy * 150)
    intro_end = (e[0] + ux * INTRODUCER_DEPTH * PX_MM / uy / PX_MM * uy, e[1] + INTRODUCER_DEPTH * PX_MM)
    intro_end = (e[0] + ux / uy * INTRODUCER_DEPTH * PX_MM, e[1] + INTRODUCER_DEPTH * PX_MM)
    ang = math.degrees(math.atan2(uy, ux))
    hub = (e[0] - ux * 130, e[1] - uy * 130)
    return f"""
  <line id="introducer" x1="{fmt(back[0])}" y1="{fmt(back[1])}" x2="{fmt(intro_end[0])}" y2="{fmt(intro_end[1])}" stroke="#7B848C" stroke-width="22" stroke-linecap="butt"/>
  <line x1="{fmt(back[0])}" y1="{fmt(back[1])}" x2="{fmt(intro_end[0])}" y2="{fmt(intro_end[1])}" stroke="#D5DADF" stroke-width="8"/>
  <line id="spinal-needle" x1="{fmt(back[0])}" y1="{fmt(back[1])}" x2="{fmt(t[0] - ux * 14)}" y2="{fmt(t[1] - uy * 14)}" stroke="url(#g-steel)" stroke-width="11"/>
  <path d="M{fmt(t[0] - ux * 16 - uy * 5.5)},{fmt(t[1] - uy * 16 + ux * 5.5)} Q{fmt(t[0] - uy * 3)},{fmt(t[1] + ux * 3)} {fmt(t[0])},{fmt(t[1])}
           Q{fmt(t[0] + uy * 3)},{fmt(t[1] - ux * 3)} {fmt(t[0] - ux * 16 + uy * 5.5)},{fmt(t[1] - uy * 16 - ux * 5.5)} Z" fill="#B9C1C8" stroke="#6E777F" stroke-width="2"/>
  <rect x="-34" y="-20" width="68" height="40" rx="8" fill="#F2F2F2" stroke="#8A9199" stroke-width="3"
        transform="translate({fmt(hub[0])} {fmt(hub[1])}) rotate({fmt(ang - 90)})"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="5" fill="#000" opacity="0"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="5" fill="#000" opacity="0"/>"""


def build() -> str:
    procs = "".join(f'<path id="{k}" d="{path(spinous(x), closed=True, tension=0.4)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="5"/>'
                    for k, x in CENTRES.items())
    roots = "".join(f'<path d="{path([(L, y), (-20, y + 0.4), (20, y - 0.3), (R, y + 0.2)], tension=0.8)}" fill="none" '
                    f'stroke="#E9C766" stroke-width="7" opacity="0.9"/>' for y in (56.0, 58.6, 61.2))
    bodies = (rect("l3-body", 1.0 + 4.5, BODY_Y, R, 100, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="5"')
              + rect("l4-body", L, BODY_Y, -4.5 + 1.0, 100, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="5"')
              + rect("disc", -3.5, BODY_Y, 5.5, 100, 'fill="#DDE6EE" stroke="#9FB2C2" stroke-width="4"'))
    labels = [
        Label(["Supraspinous ligament"], anchor=(940, 110), leader=[(1060, 128), c((24, TIP_Y - 0.6))], target_id="supraspinous"),
        Label(["Interspinous", "ligament"], anchor=(40, 300), leader=[(300, 380), c((-2.5, 26))], target_id="interspinous"),
        Label(["Ligamentum", "flavum"], anchor=(1220, 520), leader=[(1230, 600), c((0.5, 43))], target_id="ligamentum-flavum"),
        Label(["Dura"], anchor=(1300, 790), leader=[(1310, 806), c((26, DURA_POST))], target_id="dura"),
        Label(["CSF"], anchor=(40, 900), leader=[(150, 880), c((-30, 53.2))], target_id="csf", emphasis=True),
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
  {rect("skin", L, 0, R, 100, 'fill="#E7A79A"')}
  {rect("subcutaneous-fat", L, SKIN, R, 100, 'fill="url(#fat)"')}
  {rect("interspinous", L, FAT, R, LAMINA_Y1, 'fill="#E6DCCB"')}
  {rect("epidural-fat", L, LAMINA_Y1 - 1, R, DURA_POST, 'fill="#F2D27A"')}
  {rect("ligamentum-flavum", -7.0, LAMINA_Y0 + 0.5, 5.0, LAMINA_Y1 - 0.5, 'fill="#E8C24A" stroke="#B8962E" stroke-width="3"')}
  {rect("csf", L, DURA_POST, R, DURA_ANT, 'fill="#BFDCEB"')}
  {roots}
  <line id="dura" x1="0" y1="{fmt(c((0, DURA_POST))[1])}" x2="1600" y2="{fmt(c((0, DURA_POST))[1])}" stroke="#8FA3B8" stroke-width="7"/>
  <line x1="0" y1="{fmt(c((0, DURA_ANT))[1])}" x2="1600" y2="{fmt(c((0, DURA_ANT))[1])}" stroke="#8FA3B8" stroke-width="7"/>
  {rect("pll", L, DURA_ANT + 0.3, R, BODY_Y, 'fill="#F1EDE4"')}
  {bodies}
  {procs}
  <path id="supraspinous" d="{path([(L, TIP_Y - 0.8), (-30, TIP_Y - 0.8), (0, TIP_Y - 1.0), (30, TIP_Y - 0.8), (R, TIP_Y - 0.8)], tension=0.8)}" fill="none" stroke="#F4EFE6" stroke-width="22"/>
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
  <rect x="0" y="0" width="1600" height="{fmt(ORIGIN[1] - 2)}" fill="#F6F4F0"/>
</g>

<g class="marking">{needle()}
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F6F4F0; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
