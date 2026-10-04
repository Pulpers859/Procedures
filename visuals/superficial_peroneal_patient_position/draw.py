"""Superficial peroneal nerve block - probe and needle on the patient (layout).

The right distal leg and ankle of a supine patient, seen from above with the
knee off the top and the foot at the bottom: the patient's right on the image
left, so lateral (the lateral malleolus, the fibula side) is left and medial
is right. The same camera and way round as the approved deep peroneal plate,
zoomed out to show the distal third of the leg.

Record: supine; transducer transverse on the anterolateral distal leg; needle
in-plane toward the nerve; the nerve pierces the crural fascia in the distal
third of the lateral leg. NYSORA (concept only, not committed): transducer
transverse 5-10 cm proximal to the lateral malleolus; in-plane needle from
the anterior side. Here: the probe lies across the anterolateral leg about
7.5 cm above the lateral malleolus, its face from near the lateral edge of
the leg to just past the shin; the needle enters just beyond its anterior
(right, toward the shin) end, in line, aimed laterally.

Upright probe as in the interscalene and deep peroneal layouts, for the
painting to render; code-drawn over the painting: labels only.

Millimetres from the midpoint between the malleoli (x medial = image right,
y toward the foot) at 3.6 px/mm; the frame runs from mid-shin to the mid-foot.

Run: python3 visuals/superficial_peroneal_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "superficial_peroneal_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 3.6
ORIGIN = (800.0, 680.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


LATERAL = [(-56, -200), (-48, -150), (-42, -110), (-37, -70), (-35, -35), (-37, -5), (-40, 15), (-38, 40), (-43, 80), (-49, 125), (-51, 150)]
MEDIAL = [(52, 150), (50, 125), (47, 100), (42, 60), (38, 25), (35, -5), (32, -35), (34, -70), (40, -110), (46, -150), (54, -200)]
LAT_MALLEOLUS = ((-34.0, 6.0), 6.0, 8.0)
MED_MALLEOLUS = ((32.0, -6.0), 5.5, 7.5)
PC = (-14.0, -75.0)                 # probe centre, about 7.5 cm above the lateral malleolus
PROBE_LEN, PROBE_W = 38.0, 8.0
PROBE = ((PC[0] - PROBE_LEN / 2, PC[1] - PROBE_W / 2), (PC[0] + PROBE_LEN / 2, PC[1] + PROBE_W / 2))
NEEDLE_ENTRY = (PC[0] + PROBE_LEN / 2 + 6, PC[1])
NEEDLE_HUB = (PC[0] + PROBE_LEN / 2 + 34, PC[1] - 4)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.3" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def q(dx, dy):
    return c((PC[0] + dx, PC[1] + dy))


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    leg = path(LATERAL + [(-52, 190), (53, 190)] + MEDIAL, closed=True, tension=0.4)
    handle = (f"M{fmt(q(-16, 0)[0])},{fmt(p0[1] + 4)} C{fmt(q(-13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(-7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(-6, 0)[0])},{fmt(q(0, -44)[1])} L{fmt(q(6, 0)[0])},{fmt(q(0, -44)[1])} C{fmt(q(7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(16, 0)[0])},{fmt(p0[1] + 4)} Z")
    cable = (f"M{fmt(q(0, -44)[0])},{fmt(q(0, -44)[1])} C{fmt(q(2, -56)[0])},{fmt(q(0, -56)[1])} "
             f"{fmt(q(-20, -70)[0])},{fmt(q(0, -70)[1])} {fmt(q(-40, -130)[0])},-20")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 80)},{fmt(nh[1] - 10)} {fmt(nh[0] + 140)},{fmt(nh[1] + 100)} {fmt(nh[0] + 220)},1240"
    lm = c(LAT_MALLEOLUS[0])
    labels = [
        Label(["Lateral", "malleolus"], anchor=(140, 640), leader=[(350, 680), (lm[0] - 20, lm[1])], target_id="lat-malleolus"),
        Label(["Linear probe"], anchor=(80, 300), leader=[(370, 320), (p0[0] + 20, (p0[1] + p1[1]) / 2)], target_id="probe"),
        Label(["Block needle"], anchor=(1100, 300), leader=[(1180, 320), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="url(#sheet)"/>
  <path id="leg" d="{leg}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  {ell("lat-malleolus", LAT_MALLEOLUS, 'fill="#E2B39A" stroke="#C49379" stroke-width="2"')}
  {ell("med-malleolus", MED_MALLEOLUS, 'fill="#E9BEA4" stroke="#C49379" stroke-width="2"')}
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 4)}" y="{fmt(nh[1] - 9)}" width="38" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="16" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #DDE5EC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
