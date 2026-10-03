"""Serratus anterior plane block - probe and needle on the patient (layout).

Owner, 2026-10-03: copy NYSORA's serratus patient photo (Fig-9) explicitly
(concept only, not committed; drawn from scratch, no hands). The patient's
LEFT side, seen from the front: the head at the top, the feet at the bottom,
the midline toward the image left, the left pectoral area and nipple in the
centre (a male chest: owner, 2026-10-03), the left arm abducted out to the
image right with the armpit visible. NYSORA's axes: cranial up, anterior toward the camera/left,
posterior toward the arm/right.

The probe's head rests on the mid-axillary line (straight down from the
axillary apex) just below nipple level, the 4th-5th ribs; its body lies along the chest wall
running off to the right (posterior) toward the operator. The needle comes
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

PEC_BORDER = [(120, 600), (320, 640), (520, 600), (700, 520), (820, 420)]   # lower border of pectoralis major
NIPPLE = (470, 470.0)
ARM = [(800, -40), (1640, -40), (1640, 470), (1070, 450), (950, 400), (870, 300), (810, 150)]
AXILLA = [(810, 150), (870, 300), (920, 400)]
MAL_X = 920.0                     # mid-axillary line, straight down from the axillary apex
STERNUM_SHADOW = [(-40, -40), (110, -40), (90, 300), (70, 700), (-40, 760)]   # the sternum toward the midline
DRAPE = [(-40, 900), (120, 890), (620, 870), (920, 850), (1640, 820), (1640, 1240), (-40, 1240)]
PROBE = [(920, 565), (980, 550), (1040, 553), (1640, 600), (1640, 740), (1040, 695), (980, 699), (920, 685)]
HEAD = [(890, 563), (920, 559), (920, 691), (890, 687)]
NEEDLE_ENTRY = (852, 625.0)
NEEDLE_HUB = (500, 612.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E7BFA2"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="mound-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBC6AA"/><stop offset="1" stop-color="#D9A88B"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    labels = [
        Label(["Linear probe"], anchor=(1100, 880), leader=[(1180, 840), (1150, 680)], target_id="probe"),
        Label(["Block needle"], anchor=(40, 760), leader=[(300, 720), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
        Label(["Axilla"], anchor=(600, 200), leader=[(760, 220), (870, 300)], target_id="axilla"),
        Label(["Mid-axillary line"], anchor=(980, 1120), leader=[(1050, 1080), (MAL_X, 790)], target_id="mal"),
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
  <path d="{smooth_path(STERNUM_SHADOW, closed=True, tension=0.5)}" fill="#B98266" opacity="0.5"/>
  <path id="arm" d="{smooth_path(ARM, closed=True, tension=0.5)}" fill="#E2B497" stroke="#B98A74" stroke-width="3"/>
  <path id="axilla" d="{smooth_path(AXILLA, tension=0.7)}" fill="none" stroke="#A9765F" stroke-width="10" stroke-linecap="round"/>
  <path id="pec-border" d="{smooth_path(PEC_BORDER, tension=0.6)}" fill="none" stroke="#B98A74" stroke-width="6" opacity="0.8"/>
  <circle id="nipple" cx="{fmt(NIPPLE[0])}" cy="{fmt(NIPPLE[1])}" r="22" fill="#B87F6C"/>
  <path id="drape" d="{smooth_path(DRAPE, closed=True, tension=0.3)}" fill="#3F6B6E"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 60)},{fmt(nh[1] + 10)} {fmt(nh[0] - 140)},{fmt(nh[1] + 200)} {fmt(nh[0] - 260)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 50)}" y="{fmt(nh[1] - 11)}" width="54" height="22" rx="6" fill="#2FA58A" stroke="#1E7A66" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path id="probe" d="{smooth_path(PROBE, closed=True, tension=0.3)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe-head" points="{pts(HEAD)}" fill="#C9D0D6" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
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
