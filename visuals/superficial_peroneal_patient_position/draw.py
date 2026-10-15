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
y toward the foot) at 3.0 px/mm; the frame runs from mid-shin to the toes, the foot drawn after the deep peroneal layout so the ankle reads clearly.

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
PX_MM = 3.0
ORIGIN = (800.0, 450.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


LATERAL = [(-56, -200), (-48, -150), (-42, -110), (-37, -70), (-35, -35), (-37, -5), (-40, 15), (-36, 40), (-41, 80), (-46, 125), (-48, 150), (-47, 172)]
MEDIAL = [(47, 170), (50, 140), (47, 100), (42, 60), (38, 25), (35, -5), (32, -35), (34, -70), (40, -110), (46, -150), (54, -200)]
TOES = [(-47, -33, 196), (-33, -19, 206), (-19, -4, 214), (-4, 12, 220), (13, 45, 232)]
LAT_MALLEOLUS = ((-34.0, 6.0), 6.0, 8.0)
MED_MALLEOLUS = ((32.0, -6.0), 5.5, 7.5)
PC = (-14.0, -75.0)                 # probe centre, about 7.5 cm above the lateral malleolus
PROBE_LEN, PROBE_W = 38.0, 8.0
PROBE = ((PC[0] - PROBE_LEN / 2, PC[1] - PROBE_W / 2), (PC[0] + PROBE_LEN / 2, PC[1] + PROBE_W / 2))
NEEDLE_ENTRY = (PC[0] + PROBE_LEN / 2 + 6, PC[1])
NEEDLE_HUB = (PC[0] + PROBE_LEN / 2 + 34, PC[1] - 4)

# Traced on base.jpg (base pixels; place_probe.py put the photo's own probe here).
K, OY = 1600 / 1200, (1200 - 896 * 1600 / 1200) / 2
T_LEG = [(493, 0), (501, 60), (507, 120), (517, 180), (523, 240), (524, 300), (513, 360), (523, 420), (512, 560),
         (494, 700), (500, 780), (520, 860), (700, 860), (708, 700), (690, 560), (677, 420), (686, 360), (675, 300),
         (673, 240), (677, 180), (686, 120), (695, 60), (706, 0)]
T_LAT_MALL, T_MED_MALL = ((527.0, 378.0), 16.0, 20.0), ((673.0, 366.0), 14.0, 18.0)
T_FACE = (524, 172, 650, 198)
T_HANDLE = (530, 18, 642, 172)
T_ENTRY, T_HUB = (655.0, 194.0), (800.0, 182.0)


def b(p):
    return (p[0] * K, p[1] * K + OY)


DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.3" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="g-steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.5" stop-color="#B9C0C7"/><stop offset="1" stop-color="#6E777F"/></linearGradient>
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
    toes = []
    for x0, x1, tip in TOES:
        base = 172 if x0 < 0 else 176
        toes += [(x0 + 1, base + 4), (x0 + 2, tip - 6), ((x0 + x1) / 2, tip), (x1 - 2, tip - 6), (x1 - 1, base + 4)]
    leg = path(LATERAL + toes + MEDIAL, closed=True, tension=0.4)
    handle = (f"M{fmt(q(-16, 0)[0])},{fmt(p0[1] + 4)} C{fmt(q(-13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(-7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(-6, 0)[0])},{fmt(q(0, -44)[1])} L{fmt(q(6, 0)[0])},{fmt(q(0, -44)[1])} C{fmt(q(7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(16, 0)[0])},{fmt(p0[1] + 4)} Z")
    cable = (f"M{fmt(q(0, -44)[0])},{fmt(q(0, -44)[1])} C{fmt(q(2, -56)[0])},{fmt(q(0, -56)[1])} "
             f"{fmt(q(-20, -70)[0])},{fmt(q(0, -70)[1])} {fmt(q(-40, -130)[0])},-20")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 80)},{fmt(nh[1] - 10)} {fmt(nh[0] + 140)},{fmt(nh[1] + 100)} {fmt(nh[0] + 220)},1240"
    lm = c(LAT_MALLEOLUS[0])
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    scale = 1600 / BASE_SIZE[0]
    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
        f0, f1 = b(T_FACE[:2]), b(T_FACE[2:])
        h0, h1 = b(T_HANDLE[:2]), b(T_HANDLE[2:])
        ne, nh = b(T_ENTRY), b(T_HUB)
        lm = b(T_LAT_MALL[0])
        mm = b(T_MED_MALL[0])
        tubing = f"M{fmt(nh[0] + 40)},{fmt(nh[1])} C{fmt(nh[0] + 120)},{fmt(nh[1] - 6)} {fmt(nh[0] + 160)},{fmt(nh[1] + 160)} {fmt(nh[0] + 200)},1240"
        regions = f"""
<g id="regions" opacity="{0.35 if debug else 0}">
  <path id="leg" d="{smooth_path([b(q) for q in T_LEG], closed=True, tension=0.3)}" fill="#F0F"/>
  <ellipse id="lat-malleolus" cx="{fmt(lm[0])}" cy="{fmt(lm[1])}" rx="{fmt(T_LAT_MALL[1] * K)}" ry="{fmt(T_LAT_MALL[2] * K)}" fill="#0FF"/>
  <ellipse id="med-malleolus" cx="{fmt(mm[0])}" cy="{fmt(mm[1])}" rx="{fmt(T_MED_MALL[1] * K)}" ry="{fmt(T_MED_MALL[2] * K)}" fill="#0FF"/>
  <rect id="probe-handle" x="{fmt(h0[0])}" y="{fmt(h0[1])}" width="{fmt(h1[0] - h0[0])}" height="{fmt(h1[1] - h0[1])}" fill="#FF0"/>
  <rect id="probe" x="{fmt(f0[0])}" y="{fmt(f0[1])}" width="{fmt(f1[0] - f0[0])}" height="{fmt(f1[1] - f0[1])}" fill="#F00"/>
</g>"""
        layout = ""
        marking = f"""
<g class="marking">
  <path d="{tubing}" fill="none" stroke="#9AA6B1" stroke-width="8" stroke-linecap="round" opacity="0.35"/>
  <path d="{tubing}" fill="none" stroke="#F4F7F9" stroke-width="5" stroke-linecap="round" opacity="0.8"/>
  <line x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#4E565E" stroke-width="7" stroke-linecap="round" opacity="0.55"/>
  <rect x="{fmt(nh[0] - 2)}" y="{fmt(nh[1] - 12)}" width="46" height="24" rx="6" fill="#F4F5F6" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="url(#g-steel)" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" rx="8" ry="5" fill="#B07A66" opacity="0.6"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="3" fill="#8A5A4A"/>
</g>"""
        p0, p1 = f0, f1
    else:
        base_attr = base_image = regions = marking = ""
        layout = "x"
    if layout:
        layout = f"""
<g id="anatomy">
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
</g>"""
    labels = [
        Label(["Lateral", "malleolus"], anchor=(140, 560), leader=[(350, 520), (lm[0] - 8, lm[1])], target_id="lat-malleolus"),
        Label(["Linear probe"], anchor=(80, 140), leader=[(370, 160), (p0[0] + 20, (p0[1] + p1[1]) / 2)], target_id="probe"),
        Label(["Block needle"], anchor=(1080, 140), leader=[(1160, 160), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
    ]

    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
{regions}{layout}
{marking}
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
