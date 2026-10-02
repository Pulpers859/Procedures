"""Popliteal sciatic block - probe and needle on the patient (layout).

Owner, 2026-10-02: use NYSORA's patient view (their Fig-5 photo, concept
only, not committed; no hands), then "I am having a hard time visualizing
landmarks of the back of the leg" - so the camera pulls back and up to a
posterolateral view that shows the whole back of the knee.

The prone right leg runs across the frame, thigh on the left, knee and calf
on the right; the camera looks down on the back of the leg from the lateral
side, so the broad upper surface is the back of the thigh and knee, and the
lateral thigh is the lower band facing the camera.

Record: prone; transducer transverse, traced proximally from the popliteal
crease to where the tibial and common peroneal nerves join, about 6 cm above
it; needle in-plane from lateral to medial.

Drawn: the popliteal crease, the hamstring tendons framing the fossa above
it (semitendinosus medial, the upper edge; biceps femoris lateral, the
lower edge, running to the fibular head), the calf; the probe standing
across the back of the thigh about 6 cm above the crease; the needle
entering the lateral thigh directly below the probe, in line with it.

Code-drawn markings: the dashed crease, the dashed biceps femoris tendon,
and a bracket from the crease to the probe marked 6 cm. Perspective layout:
markings are traced on the painting.

Run: python3 visuals/popliteal_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "popliteal_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

BACK_TOP = [(-40, 330), (300, 316), (700, 318), (1000, 330), (1180, 350), (1360, 330), (1640, 360)]
EDGE = [(1640, 700), (1360, 690), (1240, 668), (1100, 650), (800, 640), (400, 650), (-40, 664)]
LATERAL_BOTTOM = [(-40, 1010), (600, 1000), (1200, 990), (1640, 1010)]
CREASE = [(1170, 362), (1190, 450), (1205, 560), (1214, 650)]
SEMITEND = [(560, 352), (800, 352), (1000, 366), (1150, 378)]
BICEPS = [(560, 612), (800, 606), (1000, 612), (1150, 628), (1250, 660)]
FIBULAR_HEAD = (1275.0, 668.0)
CALF = [(1240, 360), (1330, 420), (1380, 520), (1350, 640)]
PROBE_X = 820.0
FOOT = [(780, 400), (850, 396), (868, 590), (798, 596)]
HANDLE = [(788, 470), (760, 300), (740, 120), (744, -40), (880, -40), (872, 120), (858, 300), (862, 470)]
NEEDLE_ENTRY = (826.0, 700.0)
NEEDLE_HUB = (872.0, 900.0)

DEFS = """
<linearGradient id="back-skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9C4AA"/><stop offset="1" stop-color="#E0B396"/></linearGradient>
<linearGradient id="side-skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D7A386"/><stop offset="1" stop-color="#BE8B70"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    crease_mid = CREASE[1]
    br_y = 250.0
    labels = [
        Label(["Popliteal", "crease"], anchor=(1260, 820), leader=[(1270, 780), (1209, 600)], target_id="crease-mark"),
        Label(["Biceps femoris", "tendon"], anchor=(250, 760), leader=[(470, 700), (900, 608)], target_id="biceps-mark"),
        Label(["6 cm"], anchor=(960, 210), leader=[(990, 222), (1000, br_y + 1)], target_id="bracket-hit"),
        Label(["Linear probe"], anchor=(330, 150), leader=[(560, 170), (752, 200)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(950, 1100), leader=[(980, 1060), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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

    back = smooth_path(BACK_TOP, tension=0.6) + " L" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in EDGE) + " Z"
    side = smooth_path(list(reversed(EDGE)), tension=0.6) + " L" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in reversed(LATERAL_BOTTOM)) + " Z"
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="url(#drape)"/>
  <path id="leg" d="{back}" fill="url(#back-skin)" stroke="#B98A74" stroke-width="3"/>
  <path id="lateral-thigh" d="{side}" fill="url(#side-skin)" stroke="#B98A74" stroke-width="3"/>
  <path id="semitendinosus" d="{smooth_path(SEMITEND, tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="14" stroke-linecap="round" opacity="0.7"/>
  <path id="biceps" d="{smooth_path(BICEPS, tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="16" stroke-linecap="round" opacity="0.7"/>
  <ellipse cx="{fmt(FIBULAR_HEAD[0])}" cy="{fmt(FIBULAR_HEAD[1])}" rx="26" ry="18" fill="#E2B497"/>
  <path d="{smooth_path(CALF, tension=0.8)}" fill="none" stroke="#C99A80" stroke-width="6" opacity="0.7"/>
  <path id="crease" d="{smooth_path(CREASE, tension=0.8)}" fill="none" stroke="#A9765F" stroke-width="8" stroke-linecap="round"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 30)},{fmt(nh[1] + 80)} {fmt(nh[0] + 120)},{fmt(nh[1] + 140)} {fmt(nh[0] + 200)},1240" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 14)}" y="{fmt(nh[1] - 4)}" width="28" height="52" rx="8" fill="#F2F2F2" stroke="#8A9199" stroke-width="2" transform="rotate(-13 {fmt(nh[0])} {fmt(nh[1])})"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path d="M812,-40 C812,-120 900,-160 960,-200" fill="none" stroke="#3E454C" stroke-width="20" stroke-linecap="round"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.3)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <path id="crease-mark" d="{smooth_path(CREASE, tension=0.8)}" fill="none" stroke="#4A2F7A" stroke-width="7" stroke-dasharray="18 12"/>
  <path id="biceps-mark" d="{smooth_path(BICEPS[1:], tension=0.8)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="14 10"/>
  <rect id="bracket-hit" x="{fmt(PROBE_X)}" y="{fmt(br_y - 8)}" width="{fmt(CREASE[0][0] - PROBE_X)}" height="16" fill="#000" opacity="0"/>
  <g id="bracket" stroke="#4A2F7A" stroke-width="5" fill="none">
    <line x1="{fmt(PROBE_X)}" y1="{fmt(br_y)}" x2="{fmt(CREASE[0][0])}" y2="{fmt(br_y)}"/>
    <line x1="{fmt(PROBE_X)}" y1="{fmt(br_y - 14)}" x2="{fmt(PROBE_X)}" y2="{fmt(br_y + 14)}"/>
    <line x1="{fmt(CREASE[0][0])}" y1="{fmt(br_y - 14)}" x2="{fmt(CREASE[0][0])}" y2="{fmt(br_y + 14)}"/>
    <line x1="{fmt(CREASE[0][0])}" y1="{fmt(br_y + 14)}" x2="{fmt(CREASE[0][0])}" y2="{fmt(CREASE[0][1])}" stroke-dasharray="8 8" stroke-width="3"/>
  </g>
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
