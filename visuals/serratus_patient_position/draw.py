"""Serratus anterior plane block - probe and needle on the patient (layout).

After NYSORA's serratus plane patient photo (concept only, not committed;
drawn from scratch, no hands): the right lateral chest wall seen from the
patient's right side, patient supine with the arm abducted and the upper
arm raised beside the head (out of the top left): head to the left, the
front of the chest (with the nipple) toward the top, the back toward the
bed at the bottom, the armpit at the upper left.

Record: supine or lateral decubitus, arm abducted; transducer sagittal in
the mid-axillary line at the 4th or 5th intercostal space; needle in-plane,
cranial to caudal (or caudal to cranial).

Drawn: the probe standing upright on the mid-axillary line at the 4th-5th
rib level, below the armpit, its footprint along the body (horizontal here);
the needle entering just cranial (left) of the probe, level, in line with it.
Code-drawn: the dashed mid-axillary line. Perspective layout; markings
traced on the painting.

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

CHEST_TOP = [(-40, 420), (200, 330), (420, 300), (700, 280), (1000, 270), (1300, 280), (1640, 300)]
CHEST_BOTTOM = [(1640, 1000), (1200, 1010), (800, 1020), (400, 1030), (-40, 1040)]
ARM = [(-40, -40), (520, -40), (480, 120), (420, 300), (300, 360), (120, 400), (-40, 430)]
AXILLA = [(300, 360), (380, 420), (440, 470)]
NIPPLE = (1260.0, 330.0)
LAT_EDGE = [(320, 860), (700, 900), (1100, 920), (1640, 930)]
MAL_Y = 660.0
PROBE_C = (860.0, 640.0)
FOOT = [(PROBE_C[0] - 110, PROBE_C[1] - 26), (PROBE_C[0] + 110, PROBE_C[1] - 26), (PROBE_C[0] + 110, PROBE_C[1] + 26),
        (PROBE_C[0] - 110, PROBE_C[1] + 26)]
HANDLE = [(PROBE_C[0] - 90, PROBE_C[1] - 20), (PROBE_C[0] + 90, PROBE_C[1] - 20), (PROBE_C[0] + 70, 300), (PROBE_C[0] + 60, -40),
          (PROBE_C[0] - 60, -40), (PROBE_C[0] - 70, 300)]
NEEDLE_ENTRY = (PROBE_C[0] - 150, PROBE_C[1])
NEEDLE_HUB = (PROBE_C[0] - 420, PROBE_C[1] - 20)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ECC8AE"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    labels = [
        Label(["Mid-axillary line"], anchor=(1110, 760), leader=[(1180, 720), (1240, MAL_Y)], target_id="mal"),
        Label(["Linear probe"], anchor=(1020, 170), leader=[(1030, 190), (PROBE_C[0] + 40, 300)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(40, 760), leader=[(260, 720), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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

    chest = smooth_path(CHEST_TOP, tension=0.5) + " L" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in CHEST_BOTTOM) + " Z"
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#D3DDE6"/>
  <rect x="0" y="1000" width="1600" height="200" fill="#F2F4F6"/>
  <path id="chest" d="{chest}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="arm" d="{smooth_path(ARM, closed=True, tension=0.5)}" fill="#E2B497" stroke="#B98A74" stroke-width="3"/>
  <path d="{smooth_path(AXILLA, tension=0.7)}" fill="none" stroke="#A9765F" stroke-width="6"/>
  <path d="{smooth_path(LAT_EDGE, tension=0.7)}" fill="none" stroke="#B98A74" stroke-width="5" opacity="0.7"/>
  <circle cx="{fmt(NIPPLE[0])}" cy="{fmt(NIPPLE[1])}" r="24" fill="#B87F6C"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 60)},{fmt(nh[1] + 20)} {fmt(nh[0] - 120)},{fmt(nh[1] + 200)} {fmt(nh[0] - 260)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 44)}" y="{fmt(nh[1] - 10)}" width="48" height="20" rx="6" fill="#2FA58A" stroke="#1E7A66" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path d="M{fmt(PROBE_C[0])},-40 C{fmt(PROBE_C[0] + 10)},-100 {fmt(PROBE_C[0] + 120)},-140 {fmt(PROBE_C[0] + 200)},-160" fill="none" stroke="#3E454C" stroke-width="18"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.25)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <line id="mal" x1="360" y1="{fmt(MAL_Y)}" x2="1560" y2="{fmt(MAL_Y)}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
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
