"""RAPTIR (retroclavicular infraclavicular) block - probe and needle on the patient (layout).

Owner, 2026-10-03: three clinical RAPTIR photos shared as the model (Highland
Ultrasound; concept only, not committed; drawn from scratch, no hands). They
agree on: camera at the patient's right side with the head to the left,
looking across the right shoulder; arm at the side; the probe standing
upright, sagittal, in the infraclavicular fossa just medial to the coracoid
at the deltopectoral groove; the needle entering above the clavicle in the
supraclavicular hollow, on the head side of the probe, long and shallow,
in line with the probe, aimed caudally under the clavicle.

Record: supine, arm adducted; transducer sagittal over the infraclavicular
fossa; needle inserted posterior to the clavicle, aimed caudally, strictly
in-plane. Standard anatomy added: the coracoid just lateral to the probe,
the deltopectoral groove, the deltoid and pectoralis major.

Code-drawn: the dashed clavicle and a ring on the coracoid. Perspective
layout; markings traced on the painting.

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

SKIN_TOP = [(-40, 330), (180, 360), (330, 470), (430, 600), (600, 640), (800, 630), (1000, 600), (1250, 540), (1640, 470)]
NECK_EDGE = [(330, 470), (380, 640), (420, 780), (430, 900)]
SUPRACLAV = [(400, 640), (560, 650), (640, 690), (560, 720), (430, 720)]
CLAVICLE = [(420, 735), (560, 742), (700, 744), (820, 736)]
CORACOID = (890.0, 832.0)
DELTOID = [(640, 1240), (700, 1010), (820, 900), (980, 890), (1180, 960), (1340, 1100), (1420, 1240)]
DP_GROOVE = [(930, 840), (1010, 900), (1110, 990), (1200, 1100)]
NIPPLE = (1480.0, 760.0)
FOOT = [(880, 770), (1060, 770), (1056, 812), (884, 812)]
HANDLE = [(892, 772), (1048, 772), (1030, 520), (1012, 260), (1006, -40), (928, -40), (922, 260), (906, 520)]
NEEDLE_ENTRY = (560.0, 700.0)
NEEDLE_HUB = (250.0, 690.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9C2A6"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    labels = [
        Label(["Clavicle"], anchor=(330, 900), leader=[(460, 860), (420, 735)], target_id="clavicle-mark"),
        Label(["Coracoid"], anchor=(560, 1060), leader=[(700, 1020), (CORACOID[0] - 20, CORACOID[1])], target_id="coracoid-mark"),
        Label(["Linear probe"], anchor=(1100, 330), leader=[(1100, 310), (1010, 300)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(40, 560), leader=[(240, 580), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
        Label(["Deltoid"], anchor=(1220, 1160), leader=[(1230, 1120), (1080, 1000)], target_id="deltoid"),
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

    skin = smooth_path(SKIN_TOP, tension=0.5) + " L1640,1240 L-40,1240 Z"
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#D3DDE6"/>
  <path id="skin" d="{skin}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path d="{smooth_path(NECK_EDGE, tension=0.7)}" fill="none" stroke="#B98A74" stroke-width="5" opacity="0.7"/>
  <path id="supraclavicular-hollow" d="{smooth_path(SUPRACLAV, closed=True, tension=0.6)}" fill="#C79579" opacity="0.6"/>
  <path id="clavicle-ridge" d="{smooth_path(CLAVICLE, tension=0.7)}" fill="none" stroke="#F2D3BF" stroke-width="26" stroke-linecap="round" opacity="0.8"/>
  <path id="deltoid" d="{smooth_path(DELTOID, closed=True, tension=0.6)}" fill="#E2B497" stroke="#C49478" stroke-width="3"/>
  <path d="{smooth_path(DP_GROOVE, tension=0.7)}" fill="none" stroke="#B98A74" stroke-width="6" opacity="0.8"/>
  <circle cx="{fmt(NIPPLE[0])}" cy="{fmt(NIPPLE[1])}" r="22" fill="#B87F6C"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 80)},{fmt(nh[1] + 10)} {fmt(nh[0] - 140)},{fmt(nh[1] + 160)} {fmt(nh[0] - 290)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 40)}" y="{fmt(nh[1] - 9)}" width="44" height="18" rx="6" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path d="M967,-40 C970,-100 1040,-140 1110,-160" fill="none" stroke="#3E454C" stroke-width="18"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.3)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <path id="clavicle-mark" d="{smooth_path(CLAVICLE, tension=0.7)}" fill="none" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
  <circle id="coracoid-mark" cx="{fmt(CORACOID[0])}" cy="{fmt(CORACOID[1])}" r="20" fill="none" stroke="#4A2F7A" stroke-width="5"/>
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
