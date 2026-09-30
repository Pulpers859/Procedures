"""Radial arterial line - volar wrist from above, the operator's view.

Right wrist, palm up, resting extended over a rolled towel. The forearm runs
left to right with the hand on the right, so the thumb (radial) side is at the
top. Skin is drawn see-through.

Everything is placed in millimetres from the wrist crease: u runs distally
(toward the fingers), v runs radially (toward the thumb), from adult surface
anatomy. At the crease, from radial to ulnar: brachioradialis tendon over the
radial styloid, radial artery (about 9 mm in from the radial border), FCR,
median nerve (deep, between FCR and palmaris longus), palmaris longus
(midline), FDS tendons (deep), ulnar artery, ulnar nerve, FCU inserting on
the pisiform. The radial artery turns dorsally around the styloid (dashed =
deep) and gives a small superficial palmar branch over the thenar eminence.

Markings (drawn again in code over the painted base): the target zone, 1-2 cm
proximal to the wrist crease over the artery, and a dimension bracket from the
crease to the far edge of the zone.

One wrist crease is drawn on purpose. Real wrists have two or three, and the
record measures from "the wrist crease"; a second crease would make the
distance ambiguous. The hand is not foreshortened by the wrist extension.

Scale: 8 px per mm.

Run: python3 visuals/radial_approach/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "radial_approach"
PX_PER_MM = 8.0
CREASE_X = 620.0          # canvas x of the wrist crease on the forearm axis
AXIS_Y = 760.0            # canvas y of the forearm axis

ZONE_NEAR_MM, ZONE_FAR_MM = 10.0, 20.0          # record: 1-2 cm proximal to the wrist crease


def c(p):
    """(u, v) in mm from the crease -> canvas. u distal (right), v radial (up)."""
    return (CREASE_X + p[0] * PX_PER_MM, AXIS_Y - p[1] * PX_PER_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def mm(value):
    return value * PX_PER_MM


# Outline, clockwise from the proximal radial border.
RADIAL_BORDER = [(-85, 35), (-65, 33.5), (-45, 31.5), (-25, 29.5), (-10, 29), (-3, 30.2), (3, 29.4)]
# Relaxed thumb, about 30 degrees off the index and about 60 mm from the first web to the tip.
THUMB = [(14, 33), (26, 39), (38, 45), (50, 51), (62, 57), (76, 64.5), (90, 72), (100, 77), (106, 77.5), (111, 74),
         (112, 68), (104, 58), (92, 50), (80, 43), (70, 37.5), (66, 35)]
FINGERS = [(74, 33.5), (90, 32), (110, 31.5), (140, 31.5), (140, -42), (110, -42.5)]
ULNAR_BORDER = [(95, -44), (80, -45), (60, -44), (42, -41), (25, -36), (14, -31.5), (8, -30.6), (2, -28.6),
                (-5, -28.6), (-10, -29.6), (-22, -30), (-45, -32), (-65, -33.5), (-85, -35), (-110, 0)]
FINGER_WEBS = [(102, 13), (102, -6), (99, -25)]

# Centrelines (u, v).
RADIAL_ARTERY = [(-85, 8.2), (-60, 10.5), (-40, 13), (-20, 15.5), (-8, 17.2), (0, 18.2), (5, 19.5)]
RADIAL_ARTERY_DORSAL = [(5, 19.5), (9, 22.5), (11.5, 26), (12.5, 30)]
SUPERFICIAL_PALMAR = [(-4, 17.6), (8, 18.4), (20, 20.5), (30, 23.5)]
BR_BELLY, BR_TENDON = [(-90, 28.5), (-45, 26.5)], [(-45, 26.5), (-15, 25.6), (-4, 25.5)]
FCR_BELLY, FCR = [(-90, 1.5), (-58, 5)], [(-58, 5), (-40, 6.3), (-20, 7.6), (0, 9), (8, 11), (13, 13.5)]
FCR_DEEP = [(13, 13.5), (22, 16)]
PL_BELLY, PALMARIS = [(-90, -3), (-66, -2)], [(-66, -2), (-40, -1.5), (0, -1), (6, -1)]
MEDIAN_NERVE = [(-85, 0.5), (-50, 2), (-20, 3.2), (0, 4)]
MEDIAN_DEEP = [(0, 4), (15, 4.8), (28, 6.5)]
FDS = [[(-55, -8), (0, -7), (16, -6)], [(-55, -13), (0, -12.5), (16, -11.5)]]
ULNAR_ARTERY = [(-85, -13), (-40, -15.5), (0, -17.5), (10, -17)]
ULNAR_ARTERY_DEEP = [(10, -17), (25, -15), (40, -9), (48, 0)]
ULNAR_NERVE = [(-85, -17.5), (-40, -19.5), (0, -20), (10, -18.5)]   # passes radial to the pisiform
FCU_BELLY, FCU = [(-90, -26.5), (-25, -25)], [(-25, -25), (0, -25.5), (7, -24.5)]
CREASE = [(0, 27.5), (1, 14), (1.5, 0), (1, -14), (0, -27.5)]

THENAR_CREASE = [(7, 1), (15, 8), (28, 17), (45, 25), (60, 30), (68, 32)]
PROXIMAL_PALMAR = [(67, 32), (65, 16), (59, -4), (52, -22)]
DISTAL_PALMAR = [(76, -44), (80, -30), (86, -14), (92, 2), (98, 12)]
THUMB_CREASES = [[(69, 58.5), (78.5, 43.5)], [(88, 70.5), (98, 55.5)]]
DIGITAL_CREASES = [[(106, 30), (105, 22), (106, 15)], [(106, 11), (105, 3), (106, -4)],
                   [(105, -8), (104, -16), (105, -23)], [(103, -27), (102, -34), (103, -41)]]


def artery_v(u: float) -> float:
    for (u0, v0), (u1, v1) in zip(RADIAL_ARTERY, RADIAL_ARTERY[1:]):
        if u0 <= u <= u1:
            return v0 + (v1 - v0) * (u - u0) / (u1 - u0)
    raise ValueError(u)


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBCAB5"/><stop offset="0.3" stop-color="#F6E3D6"/>
  <stop offset="0.6" stop-color="#F8E8DD"/><stop offset="0.85" stop-color="#F2DACB"/><stop offset="1" stop-color="#E3BCA6"/></linearGradient>
<radialGradient id="eminence" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#E3B49C" stop-opacity="0.6"/><stop offset="1" stop-color="#E3B49C" stop-opacity="0"/></radialGradient>
<linearGradient id="roll" x1="0" x2="1"><stop offset="0" stop-color="#9FB2C2"/><stop offset="0.45" stop-color="#E2EAF0"/>
  <stop offset="0.6" stop-color="#EEF3F6"/><stop offset="1" stop-color="#8FA3B4"/></linearGradient>
<linearGradient id="artery" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E26B61"/><stop offset="0.4" stop-color="#C8322B"/><stop offset="1" stop-color="#9E2420"/></linearGradient>
<linearGradient id="tendon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBFAF4"/><stop offset="0.5" stop-color="#EDE8DA"/><stop offset="1" stop-color="#CFC6B0"/></linearGradient>
<filter id="lift" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
<clipPath id="arm"><path d="{silhouette}"/></clipPath>
"""


def stroke(points, width_mm, colour, extra="", cap="round"):
    return (f'<path d="{path(points)}" fill="none" stroke="{colour}" stroke-width="{fmt(mm(width_mm))}" '
            f'stroke-linecap="{cap}" {extra}/>')


def belly(points, width_a, width_b, colour, opacity):
    """A muscle belly: a tapered band from points[0] (width_a mm) to points[-1] (width_b mm)."""
    (u0, v0), (u1, v1) = points
    poly = [(u0, v0 + width_a / 2), (u1, v1 + width_b / 2), (u1 + width_b / 2, v1), (u1, v1 - width_b / 2), (u0, v0 - width_a / 2)]
    return f'<path d="{path(poly, closed=True, tension=0.5)}" fill="{colour}" opacity="{opacity}"/>'


def build() -> str:
    outline = RADIAL_BORDER + THUMB + FINGERS + ULNAR_BORDER
    arm = path(outline, closed=True, tension=0.7)

    webs = "".join(
        f'<path d="{path([(142, v - 4.5), (118, v - 2.6), (u + 1, v - 1), (u, v), (u + 1, v + 1), (118, v + 2.6), (142, v + 4.5)], closed=True, tension=0.5)}"/>'
        for u, v in FINGER_WEBS)

    zone_near = CREASE_X - ZONE_NEAR_MM * PX_PER_MM
    zone_far = CREASE_X - ZONE_FAR_MM * PX_PER_MM
    zone_cx = (zone_near + zone_far) / 2
    zone_cy = c((0, artery_v(-(ZONE_NEAR_MM + ZONE_FAR_MM) / 2)))[1]
    bracket_y = c((0, 21))[1]
    tick = 10

    labels = [
        Label(["Radial artery"], anchor=(40, 140), leader=[(300, 162), c((-40, 13))],
              target_id="radial-artery", emphasis=True),
        Label(["FCR tendon"], anchor=(40, 1150), leader=[(300, 1100), c((-40, 6.3))],
              target_id="fcr-tendon"),
        Label(["Wrist crease"], anchor=(880, 1156), leader=[(900, 1106), c((1, -14))],
              target_id="wrist-crease"),
    ]

    body = f"""
<g id="anatomy">
  <g id="roll"><rect x="{fmt(c((-14, 0))[0])}" y="{fmt(c((0, 41))[1])}" width="{fmt(mm(26))}" height="{fmt(mm(82))}" rx="{fmt(mm(13))}"
    fill="url(#roll)" stroke="#8193A3" stroke-width="3"/></g>

  <path id="forearm" d="{arm}" fill="url(#skin)" stroke="#C9A08A" stroke-width="3" filter="url(#lift)"/>
  <g fill="#F4F1EA" stroke="#C9A08A" stroke-width="3">{webs}</g>

  <g clip-path="url(#arm)" stroke-linejoin="round">
    <ellipse cx="{fmt(c((34, 30))[0])}" cy="{fmt(c((34, 30))[1])}" rx="{fmt(mm(30))}" ry="{fmt(mm(15))}" fill="url(#eminence)"/>
    <ellipse cx="{fmt(c((45, -33))[0])}" cy="{fmt(c((45, -33))[1])}" rx="{fmt(mm(34))}" ry="{fmt(mm(10))}" fill="url(#eminence)"/>

    {belly(BR_BELLY, 11, 5, "#D48C80", 0.45)}
    {belly(FCR_BELLY, 14, 5, "#D48C80", 0.5)}
    {belly(PL_BELLY, 9, 3, "#D48C80", 0.45)}
    {belly(FCU_BELLY, 13, 6, "#D48C80", 0.45)}

    <ellipse id="radial-styloid" cx="{fmt(c((-3, 25.5))[0])}" cy="{fmt(c((-3, 25.5))[1])}" rx="{fmt(mm(7))}" ry="{fmt(mm(3.5))}"
             fill="#EFE6D2" fill-opacity="0.5" stroke="#A8977A" stroke-width="2.5" stroke-dasharray="10 8"/>
    <ellipse id="pisiform" cx="{fmt(c((8.5, -24.5))[0])}" cy="{fmt(c((8.5, -24.5))[1])}" rx="{fmt(mm(5))}" ry="{fmt(mm(4.5))}"
             fill="#EFE6D2" fill-opacity="0.6" stroke="#A8977A" stroke-width="2.5" stroke-dasharray="10 8"/>

    {"".join(stroke(t, 4.5, "url(#tendon)", 'opacity="0.35"') for t in FDS)}
    {stroke(MEDIAN_DEEP, 5, "#EFCB5A", 'opacity="0.3"')}
    {stroke(MEDIAN_NERVE, 5.5, "#EFCB5A", 'id="median-nerve" opacity="0.85"')}
    {stroke(ULNAR_ARTERY_DEEP, 2, "#C8322B", 'stroke-dasharray="9 7" opacity="0.5"', cap="butt")}
    {stroke(ULNAR_ARTERY, 2.3, "url(#artery)", 'id="ulnar-artery" opacity="0.8"')}
    {stroke(ULNAR_NERVE, 3.5, "#EFCB5A", 'id="ulnar-nerve" opacity="0.8"')}
    {stroke(FCU, 6, "url(#tendon)", 'id="fcu-tendon"')}
    {stroke(BR_TENDON, 5, "url(#tendon)", 'id="brachioradialis-tendon" opacity="0.8"')}
    <path d="{path([(4, -3), (4, 1), (30, 12), (46, 10), (48, -18), (30, -20)], closed=True, tension=0.5)}" fill="#EDE8DA" opacity="0.16"/>
    {stroke(PALMARIS, 3, "url(#tendon)", 'id="palmaris-longus"')}
    {stroke(FCR_DEEP, 5, "#E6DFCB", 'opacity="0.4"')}
    {stroke(FCR, 5.5, "url(#tendon)", 'id="fcr-tendon" filter="url(#lift)"')}
    {stroke(SUPERFICIAL_PALMAR, 1.3, "#C8322B", 'opacity="0.6"')}
    {stroke(RADIAL_ARTERY_DORSAL, 2.4, "#C8322B", 'id="radial-artery-dorsal" stroke-dasharray="9 7" opacity="0.7"', cap="butt")}
    {stroke(RADIAL_ARTERY, 2.6, "url(#artery)", 'id="radial-artery" filter="url(#lift)"')}

    <g fill="none" stroke="#C49580" stroke-linecap="round">
      <path d="{path(THENAR_CREASE)}" stroke-width="4"/>
      <path d="{path(PROXIMAL_PALMAR)}" stroke-width="3.5"/>
      <path d="{path(DISTAL_PALMAR)}" stroke-width="3.5"/>
      {"".join(f'<path d="{path(cr)}" stroke-width="3" opacity="0.8"/>' for cr in THUMB_CREASES + DIGITAL_CREASES)}
    </g>
    <path id="wrist-crease" d="{path(CREASE)}" fill="none" stroke="#B4826C" stroke-width="6" stroke-linecap="round"/>
  </g>

  <ellipse id="target-zone" class="marking" cx="{fmt(zone_cx)}" cy="{fmt(zone_cy)}" rx="{fmt((zone_near - zone_far) / 2)}" ry="26"
           fill="#0E8C98" fill-opacity="0.28" stroke="#0E8C98" stroke-width="4"/>
  <g class="marking" stroke="#1C2530" stroke-width="3" opacity="0.85">
    <line id="crease-to-zone" x1="{fmt(CREASE_X)}" y1="{fmt(bracket_y)}" x2="{fmt(zone_far)}" y2="{fmt(bracket_y)}"/>
    <line x1="{fmt(CREASE_X)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(CREASE_X)}" y2="{fmt(bracket_y + tick)}"/>
    <line x1="{fmt(zone_near)}" y1="{fmt(bracket_y - tick / 2)}" x2="{fmt(zone_near)}" y2="{fmt(bracket_y + tick / 2)}"/>
    <line x1="{fmt(zone_far)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(zone_far)}" y2="{fmt(bracket_y + tick)}"/>
  </g>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS.replace("{silhouette}", arm), extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
