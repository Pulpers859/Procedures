"""RAPTIR (retroclavicular infraclavicular) block - probe and needle on the patient (layout).

Owner, 2026-10-02: the overhead view made the probe look odd (its handle lay
flat across the shoulder); redrawn as an oblique view with the probe standing
upright, after NYSORA's infraclavicular patient photo (concept only, not
committed; drawn from scratch, no hands).

Camera at the patient's head and right side, looking down across the right
shoulder toward the feet (NYSORA's camera): the chest and right nipple toward
the top, the clavicle across the lower third from the shoulder (left) to the
base of the neck (lower right), the deltoid at the left. Cranial is toward
the bottom of the frame, caudal toward the top.

Record: supine, arm adducted; transducer sagittal over the infraclavicular
fossa; needle inserted posterior to the clavicle, aimed caudally, strictly
in-plane.

Drawn: the linear probe standing upright on the infraclavicular fossa just
below the lateral third of the clavicle, its footprint along the body
(sagittal, up and down in this view), its handle rising out of the top; the needle entering just above the
clavicle, cranial to the probe and in line with it, aimed caudally and deep
under the clavicle toward the probe's beam. Code-drawn: the dashed clavicle.
Perspective layout; markings traced on the painting.

Run: python3 visuals/raptir_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "raptir_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

SHEET = [(-40, -40), (520, -40), (380, 140), (220, 330), (60, 520), (-40, 600)]
NECK = [(1640, 860), (1300, 900), (1080, 1000), (980, 1240), (1640, 1240)]
SHOULDER = [(-40, 600), (60, 520), (200, 500), (330, 560), (400, 700), (380, 880), (300, 1060), (220, 1240), (-40, 1240)]
CLAVICLE = [(260, 760), (430, 750), (620, 770), (820, 800), (1010, 860)]
NIPPLE = (1180.0, 230.0)
FOOT = [(470, 600), (560, 600), (575, 700), (480, 700)]
HANDLE = [(480, 605), (555, 605), (590, 380), (610, 160), (620, -40), (520, -40), (500, 160), (470, 380)]
NEEDLE_ENTRY = (500.0, 830.0)
NEEDLE_HUB = (470.0, 1010.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ECC8AE"/><stop offset="1" stop-color="#D3A386"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    labels = [
        Label(["Clavicle"], anchor=(700, 960), leader=[(760, 910), (620, 770)], target_id="clavicle-mark"),
        Label(["Linear probe"], anchor=(780, 420), leader=[(780, 400), (560, 330)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(40, 1150), leader=[(260, 1110), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <rect id="chest" x="0" y="0" width="1600" height="1200" fill="url(#skin-grad)"/>
  <path d="{smooth_path(SHEET, closed=True, tension=0.5)}" fill="#D3DDE6" stroke="#B98A74" stroke-width="3"/>
  <path id="neck" d="{smooth_path(NECK, closed=True, tension=0.5)}" fill="#DDB194" stroke="#B98A74" stroke-width="3"/>
  <path id="shoulder" d="{smooth_path(SHOULDER, closed=True, tension=0.5)}" fill="#E6BB9F" stroke="#B98A74" stroke-width="3"/>
  <path id="clavicle-ridge" d="{smooth_path(CLAVICLE, tension=0.7)}" fill="none" stroke="#F2D3BF" stroke-width="26" stroke-linecap="round" opacity="0.8"/>
  <circle id="nipple" cx="{fmt(NIPPLE[0])}" cy="{fmt(NIPPLE[1])}" r="24" fill="#B87F6C"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 40)},{fmt(nh[1] + 80)} {fmt(nh[0] - 160)},{fmt(nh[1] + 120)} {fmt(nh[0] - 300)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 10)}" y="{fmt(nh[1] - 4)}" width="20" height="40" rx="6" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path d="M570,-40 C580,-100 640,-140 700,-160" fill="none" stroke="#3E454C" stroke-width="18"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.3)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <path id="clavicle-mark" d="{smooth_path(CLAVICLE, tension=0.7)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #D3DDE6; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
