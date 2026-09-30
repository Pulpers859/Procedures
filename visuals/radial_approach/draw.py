"""Radial arterial line - volar wrist from above, the operator's view.

Right wrist, palm up, resting extended over a rolled towel. The forearm runs
left to right with the hand on the right, so the thumb (radial) side is at the
top. Skin is drawn see-through: the radial artery runs lateral (here: above)
to the flexor carpi radialis tendon, then turns dorsally around the radial
styloid. Bones are left out: dashed outlines under everything read as clutter. The median nerve is medial to FCR, under
palmaris longus.

Markings (drawn again in code over the painted base): the target zone, 1-2 cm
proximal to the wrist crease over the artery, and a dimension bracket from the
crease to the far edge of the zone.

One wrist crease is drawn on purpose. Real wrists have two or three, and the
record measures from "the wrist crease"; a second crease would make the
distance ambiguous.

Scale: 11 px per mm, drawn in canvas coordinates (no view transform).

Run: python3 visuals/radial_approach/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "radial_approach"
PX_PER_MM = 11.0
CREASE_X = 760.0

ZONE_NEAR_MM, ZONE_FAR_MM = 10.0, 20.0          # record: 1-2 cm proximal to the wrist crease
ZONE_NEAR_X = CREASE_X - ZONE_NEAR_MM * PX_PER_MM
ZONE_FAR_X = CREASE_X - ZONE_FAR_MM * PX_PER_MM

# Centrelines, proximal (left) to distal (right). Catmull-Rom passes through
# every point, so leaders can end exactly on one.
RADIAL_ARTERY = [(-20, 468), (250, 448), (450, 430), (595, 418), (700, 410), (782, 400)]
RADIAL_ARTERY_DORSAL = [(782, 400), (816, 374), (834, 340), (842, 308)]
FCR = [(240, 552), (450, 530), (600, 512), (760, 499), (840, 488)]
PALMARIS = [(200, 650), (500, 630), (760, 615), (850, 612)]
MEDIAN_NERVE = [(-20, 640), (400, 598), (760, 566), (900, 580)]
BRACHIORADIALIS = [(-20, 334), (400, 334), (640, 330), (740, 326)]
FCU = [(-20, 866), (400, 872), (760, 880), (815, 893)]
ULNAR_ARTERY = [(-20, 808), (400, 818), (760, 830), (880, 824)]
CREASE = [(766, 322), (756, 450), (752, 620), (756, 790), (766, 920)]


def artery_y(x: float) -> float:
    for (x0, y0), (x1, y1) in zip(RADIAL_ARTERY, RADIAL_ARTERY[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8C5B0"/><stop offset="0.2" stop-color="#F5E1D4"/>
  <stop offset="0.55" stop-color="#F8E8DD"/><stop offset="0.85" stop-color="#F2DACB"/><stop offset="1" stop-color="#E3BCA6"/></linearGradient>
<radialGradient id="thenar" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#E6BBA4" stop-opacity="0.55"/><stop offset="1" stop-color="#E6BBA4" stop-opacity="0"/></radialGradient>
<linearGradient id="roll" x1="0" x2="1"><stop offset="0" stop-color="#9FB2C2"/><stop offset="0.45" stop-color="#E2EAF0"/>
  <stop offset="0.6" stop-color="#EEF3F6"/><stop offset="1" stop-color="#8FA3B4"/></linearGradient>
<linearGradient id="artery" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E26B61"/><stop offset="0.4" stop-color="#C8322B"/><stop offset="1" stop-color="#9E2420"/></linearGradient>
<linearGradient id="tendon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBFAF4"/><stop offset="0.5" stop-color="#EDE8DA"/><stop offset="1" stop-color="#CFC6B0"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D98C80"/><stop offset="1" stop-color="#B8665C"/></linearGradient>
<filter id="lift" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
<clipPath id="arm"><path d="{silhouette}"/></clipPath>
"""


def silhouette() -> str:
    """Forearm, palm, thumb (up and out of frame) and the start of the index finger."""
    points = [
        (-120, 250), (-40, 254), (300, 266), (560, 286), (700, 300), (745, 298), (790, 294),   # radial border to the styloid
        (880, 262), (980, 206), (1070, 130), (1140, 50), (1180, -30),            # thenar eminence into the thumb
        (1330, -30), (1340, 60), (1370, 160), (1420, 230),                       # thumb, ulnar side, to the web
        (1520, 250), (1640, 262),                                                # index finger
        (1700, 600), (1700, 1010),
        (1400, 1000), (1100, 990), (900, 962), (820, 944), (760, 928),           # hypothenar
        (500, 950), (200, 972), (-40, 986), (-120, 990), (-200, 620),
    ]
    return smooth_path(points, closed=True, tension=0.85)


def stroke(points, width, colour, extra="", cap="round"):
    return f'<path d="{smooth_path(points)}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="{cap}" {extra}/>'


def build() -> str:
    arm = silhouette()
    thenar_crease = smooth_path([(840, 640), (900, 520), (1000, 400), (1150, 300), (1330, 246), (1420, 232)])
    palmar_crease = smooth_path([(1450, 300), (1520, 420), (1640, 520)])
    hypothenar = smooth_path([(860, 930), (1050, 900), (1300, 900), (1640, 920)])
    fcr_muscle = smooth_path([(-20, 632), (120, 590), (250, 552)])

    zone_cx = (ZONE_NEAR_X + ZONE_FAR_X) / 2
    zone_cy = artery_y(zone_cx)
    zone_rx = (ZONE_NEAR_X - ZONE_FAR_X) / 2
    bracket_y = zone_cy - 74
    tick = 16

    labels = [
        Label(["Radial artery"], anchor=(40, 140), leader=[(300, 162), (450, 430)],
              target_id="radial-artery", emphasis=True),
        Label(["FCR tendon"], anchor=(40, 1120), leader=[(300, 1070), (450, 530)],
              target_id="fcr-tendon"),
        Label(["Wrist crease"], anchor=(900, 1120), leader=[(960, 1070), (756, 790)],
              target_id="wrist-crease"),
    ]

    body = f"""
<g id="anatomy">
  <g id="roll"><rect x="615" y="178" width="210" height="890" rx="100" fill="url(#roll)" stroke="#8193A3" stroke-width="3"/>
    <path d="M640,190 L640,1056 M797,190 L797,1056" stroke="#B7C6D2" stroke-width="3" opacity="0.8"/></g>

  <path id="forearm" d="{arm}" fill="url(#skin)" stroke="#C9A08A" stroke-width="3" filter="url(#lift)"/>
  <g clip-path="url(#arm)" stroke-linejoin="round">
    <ellipse cx="1030" cy="330" rx="230" ry="170" fill="url(#thenar)"/>
    <ellipse cx="1150" cy="900" rx="300" ry="90" fill="url(#thenar)"/>
    <path d="{fcr_muscle}" fill="none" stroke="url(#muscle)" stroke-width="110" stroke-linecap="round" opacity="0.5"/>
    {stroke(MEDIAN_NERVE, 30, "#EFCB5A", 'id="median-nerve" opacity="0.85"')}
    {stroke(BRACHIORADIALIS, 34, "url(#tendon)", 'id="brachioradialis-tendon" opacity="0.8"')}
    {stroke(FCU, 44, "url(#tendon)", 'id="fcu-tendon"')}
    {stroke(ULNAR_ARTERY, 20, "url(#artery)", 'id="ulnar-artery" opacity="0.75"')}
    {stroke(PALMARIS, 24, "url(#tendon)", 'id="palmaris-longus"')}
    {stroke(FCR, 54, "url(#tendon)", 'id="fcr-tendon" filter="url(#lift)"')}
    {stroke(RADIAL_ARTERY_DORSAL, 26, "#C8322B", 'id="radial-artery-dorsal" stroke-dasharray="16 12" opacity="0.7"', cap="butt")}
    {stroke(RADIAL_ARTERY, 28, "url(#artery)", 'id="radial-artery" filter="url(#lift)"')}
    <path d="{thenar_crease}" fill="none" stroke="#C9A08A" stroke-width="4" opacity="0.8"/>
    <path d="{palmar_crease}" fill="none" stroke="#C9A08A" stroke-width="3" opacity="0.6"/>
    <path d="{hypothenar}" fill="none" stroke="#D7B19C" stroke-width="3" opacity="0.6"/>
    <path id="wrist-crease" d="{smooth_path(CREASE)}" fill="none" stroke="#B4826C" stroke-width="6" stroke-linecap="round"/>
  </g>

  <ellipse id="target-zone" class="marking" cx="{fmt(zone_cx)}" cy="{fmt(zone_cy)}" rx="{fmt(zone_rx)}" ry="34"
           fill="#0E8C98" fill-opacity="0.28" stroke="#0E8C98" stroke-width="4"/>
  <g class="marking" stroke="#1C2530" stroke-width="3" opacity="0.85">
    <line id="crease-to-zone" x1="{fmt(CREASE_X)}" y1="{fmt(bracket_y)}" x2="{fmt(ZONE_FAR_X)}" y2="{fmt(bracket_y)}"/>
    <line x1="{fmt(CREASE_X)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(CREASE_X)}" y2="{fmt(bracket_y + tick)}"/>
    <line x1="{fmt(ZONE_NEAR_X)}" y1="{fmt(bracket_y - tick / 2)}" x2="{fmt(ZONE_NEAR_X)}" y2="{fmt(bracket_y + tick / 2)}"/>
    <line x1="{fmt(ZONE_FAR_X)}" y1="{fmt(bracket_y - tick)}" x2="{fmt(ZONE_FAR_X)}" y2="{fmt(bracket_y + tick)}"/>
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
