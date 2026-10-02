"""Median nerve block - probe and needle on the patient (layout).

The right forearm from above, supinated and extended on a drape: elbow at
the top, the heel of the hand at the bottom, the thumb (radial) side on the
image left, as in the anatomical position seen from the front. The same way
round as the anatomy plate's section (radial left).

Record: arm supinated and extended; nerve in short axis in the mid-forearm;
needle in-plane.

Drawn: the linear probe transverse across the mid-forearm about 11 cm
proximal to the wrist crease, its handle standing up toward the elbow with
the cable (the interscalene plate's approved probe, scaled); the block
needle entering just beyond the probe's radial (left) end, in line with it,
with extension tubing; the thenar eminence and wrist crease for orientation.

Millimetres from the probe's centre (x toward the ulna = image right, y
toward the hand = image down) at 6 px/mm. Adult proportions.

Run: python3 visuals/median_nerve_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "median_nerve_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 6.0
ORIGIN = (800.0, 360.0)            # canvas of the probe centre


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Forearm outline, radial (left) border then ulnar (right) border, elbow to hand.
RADIAL = [(-44, -70), (-41, -40), (-36, -10), (-33, 20), (-31, 50), (-28, 80), (-27, 106), (-33, 122), (-40, 145)]
ULNAR = [(38, 145), (34, 124), (30, 108), (30, 80), (32, 50), (35, 20), (38, -10), (42, -40), (46, -70)]
THENAR = [(-31, 115), (-15, 114), (-8, 124), (-11, 145), (-40, 145), (-35, 126)]
WRIST_CREASE = [(-27, 110), (0, 112), (29, 110)]
PROBE_LEN, PROBE_W = 40.0, 9.0
PROBE = ((-PROBE_LEN / 2, -PROBE_W / 2), (PROBE_LEN / 2, PROBE_W / 2))
NEEDLE_ENTRY = (-PROBE_LEN / 2 - 8, 0.0)
NEEDLE_HUB = (-PROBE_LEN / 2 - 42, 0.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.5" stop-color="#EDC7AE"/>
  <stop offset="1" stop-color="#DDAE92"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    m = PX_MM
    handle = (f"M{fmt(c((-15, 0))[0])},{fmt(p0[1] + 4)} C{fmt(c((-12, 0))[0])},{fmt(c((0, -16))[1])} "
              f"{fmt(c((-8, 0))[0])},{fmt(c((0, -34))[1])} {fmt(c((-6, 0))[0])},{fmt(c((0, -58))[1])} "
              f"L{fmt(c((6, 0))[0])},{fmt(c((0, -58))[1])} C{fmt(c((8, 0))[0])},{fmt(c((0, -34))[1])} "
              f"{fmt(c((12, 0))[0])},{fmt(c((0, -16))[1])} {fmt(c((15, 0))[0])},{fmt(p0[1] + 4)} Z")
    cable = (f"M{fmt(c((0, -58))[0])},{fmt(c((0, -58))[1])} C{fmt(c((2, -70))[0])},{fmt(c((0, -70))[1])} "
             f"{fmt(c((20, -78))[0])},{fmt(c((0, -78))[1])} {fmt(c((60, -60))[0])},0")
    labels = [
        Label(["Block needle"], anchor=(40, 250), leader=[(200, 280), ((ne[0] + nh[0]) / 2, ne[1] - 2)], target_id="needle"),
        Label(["Linear probe"], anchor=(1110, 470), leader=[(1120, 440), (p1[0] - 20, (p0[1] + p1[1]) / 2)], target_id="probe"),
        Label(["Thenar eminence"], anchor=(40, 1060), leader=[(340, 1050), c((-20, 128))], target_id="thenar"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="url(#drape)"/>
  <path id="forearm" d="{path(RADIAL + ULNAR, closed=True, tension=0.6)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="thenar" d="{path(THENAR, closed=True, tension=0.7)}" fill="#E8BFA4" stroke="#C49478" stroke-width="2"/>
  <path id="wrist-crease" d="{path(WRIST_CREASE, tension=0.8)}" fill="none" stroke="#B98A74" stroke-width="4"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="12" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="{fmt(2.5 * m)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 80)},{fmt(nh[1])} {fmt(nh[0] - 140)},{fmt(nh[1] + 80)} {fmt(nh[0] - 180)},{fmt(nh[1] + 260)}" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 30)}" y="{fmt(nh[1] - 8)}" width="34" height="16" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #4F80A8; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
