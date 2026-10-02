"""Introducer sheath (Cordis) - the dilator-sheath unit over the wire (layout).

A side-on section through the skin and a vein in its long axis, as an atlas
cut-away: air and the device's hub above, the skin across the middle, the
vein running left to right below it, muscle at the bottom. Site-neutral: the
record covers IJ, subclavian, axillary and femoral sheaths.

Record: nick the skin through the dermis into subcutaneous tissue; advance
the assembled dilator and sheath over the wire as a unit, through an
adequate nick, with a controlled wire; never force.

Drawn from the record's kit (8.5-9 Fr, 10 cm sheath with a haemostasis valve
and side arm) and standard sizes: sheath 3.3 mm outer diameter, dilator
2.8 mm tapering to the 0.89 mm (0.035 in) wire over about 16 mm, skin 2.5 mm,
subcutaneous fat to 11 mm, a vein 13 mm across centred 18 mm deep. The unit
travels at 40 degrees to the skin; the nick is 8 mm long at the surface.
The moment shown: the dilator tip is in the vein, the sheath tip just
through the nick, the wire running on along the vein and out of the back of
the dilator hub, where it is held.

Code-drawn: the whole device (wire, dilator, sheath, hub, valve, side arm
and tubing) and the inset of the back end, not to scale: the wire tail out
of the dilator hub, held. The painting carries the tissue and the nick.

Millimetres from the nick's centre (x along the skin = image right, y depth
= image down) at 14 px/mm, zoomed to the entry site:
the hub, valve and side arm run off the top-left edge (drawn, out of frame).

Run: python3 visuals/cordis_dilator_unit/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt  # noqa: E402

ASSET_ID = "cordis_dilator_unit"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 14.0
ORIGIN = (760.0, 540.0)           # canvas of the nick's centre on the skin
ANGLE = 40.0                       # device to the skin, degrees

DERMIS = 2.5
FAT = 11.0
VEIN_Y, VEIN_R, VEIN_WALL = 18.0, 6.5, 0.9
MUSCLE = 28.0
NICK_HALF = 4.0

SHEATH_R, DILATOR_R, WIRE_R = 1.65, 1.4, 0.45
SHEATH_TIP = 6.0                   # mm along the device from the skin
TAPER_START, DILATOR_TIP = 8.0, 24.0
SHEATH_BACK = SHEATH_TIP - 100.0   # 10 cm sheath
VALVE_LEN, VALVE_R = 24.0, 5.0
DHUB_LEN, DHUB_R = 16.0, 3.5

DEFS = """
<linearGradient id="g-sheath" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9F1F7"/><stop offset="0.35" stop-color="#C3D6E4"/>
  <stop offset="1" stop-color="#7E9AB0"/></linearGradient>
<linearGradient id="g-dilator" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#EEF1F4"/>
  <stop offset="1" stop-color="#A9B3BC"/></linearGradient>
<linearGradient id="g-hub" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FB2DA"/><stop offset="0.45" stop-color="#3F7FB5"/>
  <stop offset="1" stop-color="#245782"/></linearGradient>
<linearGradient id="g-steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.45" stop-color="#B9C1C8"/>
  <stop offset="1" stop-color="#6E777F"/></linearGradient>
"""


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


D = (math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE)))


def along(t, v=0.0):
    """Canvas point t mm along the device from the nick, v mm to its lower-left side."""
    return c((t * D[0] - v * D[1], t * D[1] + v * D[0]))


def tissue() -> str:
    W = 1600
    y = lambda mm: fmt(c((0, mm))[1])  # noqa: E731
    vt, vb = VEIN_Y - VEIN_R, VEIN_Y + VEIN_R
    n0, n1 = c((-NICK_HALF, 0)), c((NICK_HALF, 0))
    nb0, nb1 = c((-NICK_HALF * 0.55, DERMIS)), c((NICK_HALF * 0.55, DERMIS))
    return f"""
  <rect id="muscle" x="0" y="{y(MUSCLE)}" width="{W}" height="{fmt(1200 - c((0, MUSCLE))[1])}" fill="#B65A55"/>
  <rect id="fat" x="0" y="{y(DERMIS)}" width="{W}" height="{fmt((MUSCLE - DERMIS) * PX_MM)}" fill="#F2D27A"/>
  <rect id="fascia" x="0" y="{fmt(c((0, FAT))[1] - 3)}" width="{W}" height="6" fill="#F4EFE6"/>
  <rect id="vein-wall" x="0" y="{y(vt - VEIN_WALL)}" width="{W}" height="{fmt((2 * VEIN_R + 2 * VEIN_WALL) * PX_MM)}" fill="#6D7FB2"/>
  <rect id="vein" x="0" y="{y(vt)}" width="{W}" height="{fmt(2 * VEIN_R * PX_MM)}" fill="#3E4F8C"/>
  <rect id="dermis" x="0" y="{y(0)}" width="{W}" height="{fmt(DERMIS * PX_MM)}" fill="#E7A79A"/>
  <rect id="epidermis" x="0" y="{fmt(c((0, 0))[1] - 2)}" width="{W}" height="6" fill="#D98F7E"/>
  <path id="nick" d="M{fmt(n0[0])},{fmt(n0[1] - 2)} L{fmt(n1[0])},{fmt(n1[1] - 2)} L{fmt(nb1[0])},{fmt(nb1[1] + 4)} L{fmt(nb0[0])},{fmt(nb0[1] + 4)} Z"
        fill="#8E2F2A"/>"""


def device() -> tuple[str, dict]:
    m = PX_MM
    ang = ANGLE
    st, tp, dt, sb = SHEATH_TIP * m, TAPER_START * m, DILATOR_TIP * m, SHEATH_BACK * m
    vb = sb - VALVE_LEN * m
    hb = vb - DHUB_LEN * m
    sr, dr, wr, vr, hr = SHEATH_R * m, DILATOR_R * m, WIRE_R * m, VALVE_R * m, DHUB_R * m
    side_u = sb - 9 * m
    side_out = vr + 14 * m
    local = f"""
    <line x1="{fmt(hb - 260)}" y1="0" x2="{fmt(dt)}" y2="0" stroke="url(#g-steel)" stroke-width="{fmt(2 * wr)}"/>
    <path id="dilator" d="M{fmt(st - 2)},{fmt(-dr)} L{fmt(tp)},{fmt(-dr)} L{fmt(dt)},{fmt(-wr - 1)} L{fmt(dt)},{fmt(wr + 1)} L{fmt(tp)},{fmt(dr)} L{fmt(st - 2)},{fmt(dr)} Z"
          fill="url(#g-dilator)" stroke="#8D98A3" stroke-width="2"/>
    <path id="sheath" d="M{fmt(sb)},{fmt(-sr)} L{fmt(st - 1.5 * m)},{fmt(-sr)} L{fmt(st)},{fmt(-dr)} L{fmt(st)},{fmt(dr)} L{fmt(st - 1.5 * m)},{fmt(sr)} L{fmt(sb)},{fmt(sr)} Z"
          fill="url(#g-sheath)" stroke="#5F7C93" stroke-width="2" fill-opacity="0.95"/>
    <line x1="{fmt(sb + 4)}" y1="{fmt(-sr + 5)}" x2="{fmt(st - 14)}" y2="{fmt(-sr + 5)}" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.75" stroke-linecap="round"/>
    <rect x="{fmt(side_u - 3.5 * m)}" y="{fmt(vr - 2)}" width="{fmt(7 * m)}" height="{fmt(side_out - vr + 2)}" rx="6" fill="url(#g-hub)" stroke="#1E4A70" stroke-width="2"/>
    <path id="valve" d="M{fmt(vb)},{fmt(-vr)} H{fmt(sb - 3 * m)} L{fmt(sb)},{fmt(-sr - 4)} V{fmt(sr + 4)} L{fmt(sb - 3 * m)},{fmt(vr)} H{fmt(vb)} Z"
          fill="url(#g-hub)" stroke="#1E4A70" stroke-width="2"/>
    <rect x="{fmt(vb - 2)}" y="{fmt(-vr - 4)}" width="{fmt(4 * m)}" height="{fmt(2 * vr + 8)}" rx="6" fill="#E4E9EE" stroke="#8D98A3" stroke-width="2"/>
    <rect id="dilator-hub" x="{fmt(hb)}" y="{fmt(-hr)}" width="{fmt(DHUB_LEN * m)}" height="{fmt(2 * hr)}" rx="8" fill="url(#g-dilator)" stroke="#8D98A3" stroke-width="2"/>
    {"".join(f'<line x1="{fmt(hb + k * 2.4 * m)}" y1="{fmt(-hr)}" x2="{fmt(hb + k * 2.4 * m)}" y2="{fmt(hr)}" stroke="#A9B3BC" stroke-width="2"/>' for k in range(1, 4))}"""
    side_end = along(SHEATH_BACK - 9, VALVE_R + 14)
    # Wire on beyond the dilator tip: curve into the vein's axis and run off the right edge.
    tip = along(DILATOR_TIP)
    a = along(DILATOR_TIP + 6)
    vy = c((0, VEIN_Y + 1))[1]
    wire_on = (f'M{fmt(tip[0])},{fmt(tip[1])} C{fmt(a[0])},{fmt(a[1])} {fmt(a[0] + 40)},{fmt(vy)} {fmt(a[0] + 110)},{fmt(vy)} '
               f'L1640,{fmt(vy)}')
    tube = (f'M{fmt(side_end[0])},{fmt(side_end[1])} C{fmt(side_end[0] - 60)},{fmt(side_end[1] + 80)} '
            f'{fmt(side_end[0] - 150)},{fmt(side_end[1] + 120)} -40,{fmt(side_end[1] + 150)}')
    svg = f"""
  <path id="side-tubing" d="{tube}" fill="none" stroke="#DDE6EC" stroke-width="16" stroke-linecap="round" opacity="0.95"/>
  <path d="{tube}" fill="none" stroke="#A9B8C4" stroke-width="16" stroke-linecap="round" opacity="0.35" transform="translate(0 4)"/>
  <path id="guidewire-in-vein" d="{wire_on}" fill="none" stroke="url(#g-steel)" stroke-width="{fmt(2 * WIRE_R * PX_MM)}" stroke-linecap="round"/>
  <path d="{wire_on}" fill="none" stroke="#6E777F" stroke-width="{fmt(2 * WIRE_R * PX_MM)}" stroke-linecap="round" opacity="0.6"/>
  <g id="device" transform="translate({fmt(ORIGIN[0])} {fmt(ORIGIN[1])}) rotate({fmt(ang)})">{local}</g>
  <circle id="dilator-tip" cx="{fmt(tip[0])}" cy="{fmt(tip[1])}" r="5" fill="#000" opacity="0"/>
  <circle id="sheath-tip" cx="{fmt(along(SHEATH_TIP)[0])}" cy="{fmt(along(SHEATH_TIP)[1])}" r="5" fill="#000" opacity="0"/>"""
    return svg, {"tip": tip}


def hub_inset() -> str:
    """The back end, not to scale: the wire tail out of the dilator hub, held."""
    x0, y0, x1, y1 = 1000.0, 30.0, 1570.0, 380.0
    cy = 190.0
    return f"""
  <g id="inset">
    <clipPath id="inset-clip"><rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28"/></clipPath>
    <rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28" fill="#FFFFFF" fill-opacity="0.96" stroke="#9AA6B2" stroke-width="3"/>
    <g clip-path="url(#inset-clip)">
      <path d="M1320,{fmt(cy + 30)} C1320,{fmt(cy + 90)} 1260,{fmt(cy + 120)} 1180,{fmt(cy + 200)}" fill="none" stroke="#DDE6EC" stroke-width="14" stroke-linecap="round"/>
      <path d="M1320,{fmt(cy + 30)} C1320,{fmt(cy + 90)} 1260,{fmt(cy + 120)} 1180,{fmt(cy + 200)}" fill="none" stroke="#A9B8C4" stroke-width="3" opacity="0.8"/>
      <rect x="1300" y="{fmt(cy + 16)}" width="40" height="40" rx="6" fill="url(#g-hub)" stroke="#1E4A70" stroke-width="2"/>
      <rect id="inset-sheath" x="1350" y="{fmt(cy - 9)}" width="260" height="18" rx="4" fill="url(#g-sheath)" stroke="#5F7C93" stroke-width="2"/>
      <path id="inset-valve" d="M1236,{fmt(cy - 30)} H1330 L1354,{fmt(cy - 13)} V{fmt(cy + 13)} L1330,{fmt(cy + 30)} H1236 Z" fill="url(#g-hub)" stroke="#1E4A70" stroke-width="2"/>
      <rect x="1226" y="{fmt(cy - 34)}" width="18" height="68" rx="5" fill="#E4E9EE" stroke="#8D98A3" stroke-width="2"/>
      <rect x="1150" y="{fmt(cy - 20)}" width="78" height="40" rx="8" fill="url(#g-dilator)" stroke="#8D98A3" stroke-width="2"/>
      {"".join(f'<line x1="{1150 + k * 18}" y1="{fmt(cy - 20)}" x2="{1150 + k * 18}" y2="{fmt(cy + 20)}" stroke="#A9B3BC" stroke-width="2"/>' for k in range(1, 4))}
      <path id="wire-tail" d="M1150,{fmt(cy)} C1100,{fmt(cy)} 1060,{fmt(cy - 10)} 1030,{fmt(cy - 60)} C1010,{fmt(cy - 95)} 980,{fmt(cy - 110)} 960,{fmt(cy - 120)}"
            fill="none" stroke="url(#g-steel)" stroke-width="7" stroke-linecap="round"/>
      <path d="M1150,{fmt(cy)} C1100,{fmt(cy)} 1060,{fmt(cy - 10)} 1030,{fmt(cy - 60)} C1010,{fmt(cy - 95)} 980,{fmt(cy - 110)} 960,{fmt(cy - 120)}"
            fill="none" stroke="#6E777F" stroke-width="7" stroke-linecap="round" opacity="0.5"/>
    </g>
  </g>"""


def build() -> str:
    dev, p = device()
    sheath_mid = along(-20)
    dil_mid = along(15)
    labels = [
        Label(["Sheath"], anchor=(560, 230), leader=[(580, 252), (sheath_mid[0] + 4, sheath_mid[1] - 4)], target_id="sheath"),
        Label(["Skin nick"], anchor=(330, 470), leader=[(600, 484), c((-NICK_HALF * 0.85, 0.6))], target_id="nick"),
        Label(["Dilator"], anchor=(1130, 470), leader=[(1140, 484), (dil_mid[0] + 4, dil_mid[1])], target_id="dilator"),
        Label(["Guidewire"], anchor=(1250, 1110), leader=[(1400, 1066), (1450, c((0, VEIN_Y + 1))[1])], target_id="guidewire-in-vein"),
        Label(["Wire tail"], anchor=(1040, 340), leader=[(1100, 296), (1108, 187)], target_id="wire-tail"),
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
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#F6F4F0"/>{tissue()}
</g>

<g class="marking">{dev}{hub_inset()}
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
