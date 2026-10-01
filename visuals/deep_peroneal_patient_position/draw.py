"""Deep peroneal nerve block - probe and needle on the patient (layout).

Flat code layout for the owner's Gemini repaint (visuals/PLAYBOOK.md). The
positioning half of the pair; deep_peroneal_anatomy is the section under
this probe.

Right ankle and foot of a supine patient, seen from above with the leg at
the top and the toes at the bottom: the patient's right on the image left,
so lateral (the little toe, the lateral malleolus) is left and medial (the
big toe, the medial malleolus) is right - the same way round as a
transverse ultrasound and the anatomy plate. A sheet lies under the leg.

Record: supine; transducer transverse over the anterior ankle; the nerve
runs with the anterior tibial artery (dorsalis pedis), usually lateral to
it. Added, not in the record: the probe sits at the level of the malleoli;
the needle enters just beyond the probe's lateral end; the dashed red
artery course runs from the mid-ankle to the first intermetatarsal space
(standard anatomy). In-plane from lateral is the owner's choice
(2026-10-01: "I want the needle coming in plane").

Code-drawn marking: the dashed artery course. The probe and needle are in
the painted layer, for the painting to render.

Millimetres from the mid-point of the anterior ankle between the malleoli
(x toward medial = image right, y toward the toes) at 3.6 px/mm. Adult foot,
about 255 mm long and 95 mm across the metatarsal heads.

Run: python3 visuals/deep_peroneal_patient_position/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "deep_peroneal_patient_position"
PX_MM = 3.6
ORIGIN = (780.0, 290.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


LAT_MALLEOLUS = (-37.0, 6.0)      # lower and further back than the medial
MED_MALLEOLUS = (35.0, -6.0)

# Outline clockwise from the top of the leg, lateral side first.
LATERAL = [(-28, -100), (-25, -50), (-28, -20), (-37, 2), (-38, 18), (-36, 40), (-41, 80), (-46, 125), (-48, 150), (-47, 172)]
TOES = [  # little toe to big toe: (x0, x1, tip y)
    (-47, -33, 196), (-33, -19, 206), (-19, -4, 214), (-4, 12, 220), (13, 45, 232),
]
MEDIAL = [(47, 170), (50, 140), (47, 100), (42, 60), (38, 25), (36, 0), (28, -25), (25, -50), (27, -100)]

ARTERY = [(3, -60), (3, -20), (5, 10), (10, 50), (15, 90), (19, 118)]

PROBE_CENTRE, PROBE_LEN, PROBE_W = (0.0, -2.0), 38.0, 12.0
PROBE_X0 = PROBE_CENTRE[0] - PROBE_LEN / 2
NEEDLE_ENTRY = (PROBE_X0 - 6, PROBE_CENTRE[1])
NEEDLE_HUB = (PROBE_X0 - 40, PROBE_CENTRE[1] - 6)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.3" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def foot_outline():
    pts = list(LATERAL)
    for x0, x1, tip in TOES:
        base = 172 if x0 < 0 else 176
        pts += [(x0 + 1, base + 4), (x0 + 2, tip - 6), ((x0 + x1) / 2, tip), (x1 - 2, tip - 6), (x1 - 1, base + 4)]
    return pts + MEDIAL


def build() -> str:
    skin = path(foot_outline(), closed=True, tension=0.5)
    p0 = c((PROBE_X0, PROBE_CENTRE[1] - PROBE_W / 2))
    pw, ph = PROBE_LEN * PX_MM, PROBE_W * PX_MM
    cable = path([(PROBE_CENTRE[0] + 4, PROBE_CENTRE[1] - PROBE_W / 2), (10, -40), (30, -75), (70, -95)])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    syringe_end = c((NEEDLE_HUB[0] - 45, NEEDLE_HUB[1] - 8))
    lm, mm = c(LAT_MALLEOLUS), c(MED_MALLEOLUS)
    toe_gaps = "".join(
        f'<path d="{path([(x1 - 0.5, 182), (x1, 177)])}" stroke="#B98A74" stroke-width="3" fill="none"/>' for _, x1, _ in TOES[:-1])

    labels = [
        Label(["Lateral", "malleolus"], anchor=(150, 300), leader=[(330, 340), (lm[0] - 12, lm[1])], target_id="lat-malleolus"),
        Label(["Medial", "malleolus"], anchor=(1250, 240), leader=[(1240, 280), (mm[0] + 12, mm[1])], target_id="med-malleolus"),
        Label(["Dorsalis pedis"], anchor=(1150, 900), leader=[(1140, 880), c((15, 90))], target_id="artery-course", emphasis=True),
    ]

    body = f"""
<g id="anatomy">
  <rect x="0" y="0" width="1600" height="1200" fill="url(#sheet)"/>
  <path id="skin" d="{skin}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  {toe_gaps}
  <ellipse id="lat-malleolus" cx="{fmt(lm[0])}" cy="{fmt(lm[1])}" rx="22" ry="30" fill="#E2B39A" stroke="#C49379" stroke-width="2"/>
  <ellipse id="med-malleolus" cx="{fmt(mm[0])}" cy="{fmt(mm[1])}" rx="20" ry="28" fill="#E9BEA4" stroke="#C49379" stroke-width="2"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="16" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(pw)}" height="{fmt(ph)}" rx="16" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <line x1="{fmt(syringe_end[0])}" y1="{fmt(syringe_end[1])}" x2="{fmt(nh[0] - 30)}" y2="{fmt(nh[1] - 5)}" stroke="#F4F6F8" stroke-width="26" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 32)}" y="{fmt(nh[1] - 9)}" width="34" height="16" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
</g>

<g class="marking" fill="none">
  <path id="artery-course" d="{path(ARTERY)}" stroke="#C8322B" stroke-width="7" stroke-dasharray="16 11"/>
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
