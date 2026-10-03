"""Serratus anterior plane block - probe and needle on the patient (layout).

Owner, 2026-10-03: follow NYSORA's serratus patient photo (Fig-8/9; concept
only, not committed; drawn from scratch, no hands): the right lateral chest
wall seen face-on, cranial at the top, anterior on the image left, posterior
on the right (NYSORA's Cr / A / P axes). The pectoral/breast contour arches
across the top left, the armpit is at the top right, the latissimus edge
runs down the right side, and the drape lies below.

NYSORA: transducer transverse over the mid-axillary line at the 4th-5th ribs
(its long axis anterior-posterior); needle in-plane from superior-anterior
to posterior-inferior. (The record currently says sagittal, cranial to
caudal; raised with the owner.)

Drawn: the probe on the mid-axillary line, its footprint lying anterior-
posterior (horizontal here), its handle angled down and posterior toward
the operator; the needle entering just anterior (left) of the probe's
anterior end, from slightly superior, in line with it. Code-drawn: the
dashed mid-axillary line. Perspective layout; markings traced on the
painting.

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

BREAST = [(-40, 380), (200, 330), (460, 300), (700, 340), (860, 440), (900, 520), (760, 540), (520, 500), (260, 500), (-40, 540)]
AXILLA = [(1180, 120), (1260, 260), (1300, 420)]
LAT_EDGE = [(1300, 420), (1330, 700), (1350, 1000)]
DRAPE = [(-40, 1040), (400, 1000), (900, 980), (1300, 1000), (1640, 1040), (1640, 1240), (-40, 1240)]
MAL_X = 780.0
PROBE_C = (780.0, 720.0)
FOOT = [(PROBE_C[0] - 130, PROBE_C[1] - 30), (PROBE_C[0] + 130, PROBE_C[1] - 30), (PROBE_C[0] + 130, PROBE_C[1] + 30),
        (PROBE_C[0] - 130, PROBE_C[1] + 30)]
HANDLE = [(PROBE_C[0] - 110, PROBE_C[1] + 20), (PROBE_C[0] + 110, PROBE_C[1] + 20), (PROBE_C[0] + 300, PROBE_C[1] + 300),
          (PROBE_C[0] + 520, 1240), (PROBE_C[0] + 360, 1240), (PROBE_C[0] + 140, PROBE_C[1] + 340)]
NEEDLE_ENTRY = (PROBE_C[0] - 175, PROBE_C[1] - 6)
NEEDLE_HUB = (PROBE_C[0] - 470, PROBE_C[1] - 90)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ECC8AE"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    labels = [
        Label(["Mid-axillary line"], anchor=(860, 120), leader=[(880, 140), (MAL_X, 300)], target_id="mal"),
        Label(["Linear probe"], anchor=(1180, 760), leader=[(1190, 720), (PROBE_C[0] + 200, PROBE_C[1] + 220)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(40, 860), leader=[(260, 820), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <path id="breast" d="{smooth_path(BREAST, closed=True, tension=0.5)}" fill="#E9C2A6" stroke="#B98A74" stroke-width="3"/>
  <path d="{smooth_path(AXILLA, tension=0.7)}" fill="none" stroke="#A9765F" stroke-width="7"/>
  <path d="{smooth_path(LAT_EDGE, tension=0.7)}" fill="none" stroke="#B98A74" stroke-width="5" opacity="0.7"/>
  <path id="drape" d="{smooth_path(DRAPE, closed=True, tension=0.4)}" fill="#5E8C8A"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 60)},{fmt(nh[1] - 20)} {fmt(nh[0] - 120)},{fmt(nh[1] + 200)} {fmt(nh[0] - 200)},1240" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 46)}" y="{fmt(nh[1] - 10)}" width="50" height="20" rx="6" fill="#2FA58A" stroke="#1E7A66" stroke-width="2" transform="rotate(16 {fmt(nh[0])} {fmt(nh[1])})"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.25)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <line id="mal" x1="{fmt(MAL_X)}" y1="140" x2="{fmt(MAL_X)}" y2="960" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
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
