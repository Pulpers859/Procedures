"""Serratus anterior plane block - probe and needle on the patient (layout).

Owner, 2026-10-03: copy NYSORA's serratus patient photo (Fig-9) explicitly
(concept only, not committed; drawn from scratch, no hands). The patient's
LEFT side, seen from the front: the head at the top, the feet at the bottom,
the midline toward the image left, the left pectoral area and nipple in the
centre (a male chest: owner, 2026-10-03), the left arm abducted out to the
image right with the armpit visible. NYSORA's axes: cranial up, anterior toward the camera/left,
posterior toward the arm/right.

The probe's face rests on the mid-axillary line (straight down from the
axillary apex) just below nipple level, the 4th-5th ribs; its body runs diagonally down to the
lower right (about 35 degrees) toward the operator, as in NYSORA. The needle comes
in level from the left (anterior), entering just in front of the probe head.

Record (follows NYSORA, owner 2026-10-03): transducer transverse over the
mid-axillary line at the 4th-5th ribs; needle in-plane from the
superior-anterior end. The NYSORA side (left) is used, not the house
right, at the owner's direction.

Perspective layout; markings traced on the painting.

Run: python3 visuals/serratus_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "serratus_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

PEC_BORDER = [(500, 600), (700, 640), (900, 600), (1080, 520), (1200, 420)]   # lower border of pectoralis major
NIPPLE = (850.0, 470.0)
ARM = [(1180, -40), (2020, -40), (2020, 510), (1450, 450), (1330, 400), (1250, 300), (1190, 150)]
AXILLA = [(1190, 150), (1250, 300), (1300, 400)]
MAL_X = 1300.0                     # mid-axillary line, straight down from the axillary apex
STERNUM_SHADOW = [(-40, -40), (360, -40), (300, 300), (240, 700), (-40, 760)]
DRAPE = [(340, 900), (500, 890), (1000, 870), (1300, 850), (1640, 820), (2020, 790), (2020, 1240), (340, 1240)]
import math  # noqa: E402

# NYSORA Fig-9: the probe's face is pressed into the side of the chest and its body runs diagonally down
# to the lower right toward the operator (owner, 2026-10-03: not horizontal).
HEAD_C = (1285.0, 625.0)
PROBE_ANG = 35.0                   # degrees below horizontal, toward the lower right


def rot(p):
    a = math.radians(PROBE_ANG)
    return (HEAD_C[0] + p[0] * math.cos(a) - p[1] * math.sin(a), HEAD_C[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


HEAD = [rot(q) for q in [(-15, -66), (15, -66), (15, 66), (-15, 66)]]
PROBE = [rot(q) for q in [(15, -62), (70, -74), (130, -72), (1100, -62), (1100, 62), (130, 72), (70, 74), (15, 62)]]
# The needle comes in level from the anterior side and its tip goes into the skin right at the probe's
# anterior edge (owner: the painted tip stopped short of the skin).
NEEDLE_ENTRY = (rot((-15, -40))[0] - 6, rot((-15, -40))[1] + 4)
NEEDLE_HUB = (880.0, NEEDLE_ENTRY[1] - 8)
CAM_DX = -380.0
AXILLA_PX = (985.0, 400.0)          # traced on the owner's painting: the armpit hollow                    # owner, 2026-10-03: pan the camera toward the axilla; a pure shift, nothing else changes

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E7BFA2"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="mound-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBC6AA"/><stop offset="1" stop-color="#D9A88B"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    dx = CAM_DX
    labels = [
        Label(["Linear probe"], anchor=(1180, 1000), leader=[(1200, 960), (rot((300, 0))[0] + dx, rot((300, 0))[1])], target_id="probe"),
        Label(["Block needle"], anchor=(40, 760), leader=[(300, 720), ((ne[0] + nh[0]) / 2 + dx, (ne[1] + nh[1]) / 2)], target_id="needle"),
        Label(["Axilla"], anchor=(600, 200), leader=[(760, 220), AXILLA_PX if BASE.exists() else (1250 + dx, 300)], target_id="axilla-mark" if BASE.exists() else "axilla"),
        Label(["Mid-axillary line"], anchor=(980, 1120), leader=[(1050, 1080), (MAL_X + dx, 790)], target_id="mal"),
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
<g id="anatomy"{layout_attr}><g transform="translate({fmt(CAM_DX)} 0)">
  <rect id="chest" x="{fmt(-CAM_DX)}" y="0" width="1600" height="1200" fill="url(#skin-grad)"/>
  <path d="{smooth_path(STERNUM_SHADOW, closed=True, tension=0.5)}" fill="#B98266" opacity="0.5"/>
  <path id="arm" d="{smooth_path(ARM, closed=True, tension=0.5)}" fill="#E2B497" stroke="#B98A74" stroke-width="3"/>
  <path id="axilla" d="{smooth_path(AXILLA, tension=0.7)}" fill="none" stroke="#A9765F" stroke-width="10" stroke-linecap="round"/>
  <path id="pec-border" d="{smooth_path(PEC_BORDER, tension=0.6)}" fill="none" stroke="#B98A74" stroke-width="6" opacity="0.8"/>
  <circle id="nipple" cx="{fmt(NIPPLE[0])}" cy="{fmt(NIPPLE[1])}" r="22" fill="#B87F6C"/>
  <path id="drape" d="{smooth_path(DRAPE, closed=True, tension=0.3)}" fill="#3F6B6E"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 60)},{fmt(nh[1] + 10)} {fmt(nh[0] - 140)},{fmt(nh[1] + 200)} {fmt(nh[0] - 260)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 50)}" y="{fmt(nh[1] - 11)}" width="54" height="22" rx="6" fill="#2FA58A" stroke="#1E7A66" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <ellipse cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" rx="12" ry="6" fill="#C9907A" opacity="0.8"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path id="probe" d="{smooth_path(PROBE, closed=True, tension=0.3)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe-head" points="{pts(HEAD)}" fill="#C9D0D6" stroke="#7D868F" stroke-width="3"/>
</g></g>

{f'<circle id="axilla-mark" cx="{AXILLA_PX[0]}" cy="{AXILLA_PX[1]}" r="40" fill="#000" opacity="0"/>' if BASE.exists() else ""}
<g class="marking" transform="translate({fmt(CAM_DX)} 0)">
  <line id="mal" x1="{fmt(MAL_X)}" y1="420" x2="{fmt(MAL_X)}" y2="840" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #3F6B6E; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
