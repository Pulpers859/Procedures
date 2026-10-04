"""Serratus anterior plane block - probe and needle on the patient (painted base, code-drawn probe).

Owner, 2026-10-03: follow NYSORA Fig-9 (concept only, not committed): the
patient's left side, supine, male chest, head toward the upper right, the
arm abducted across the upper right, the armpit centre right, the drape
along the lower right. The base is the owner's Gemini photo with the probe
and needle removed (Gemini failed the probe pose four times; PLAYBOOK rule:
draw it in code).

Record (follows NYSORA): transducer transverse over the mid-axillary line at
the 4th-5th ribs; needle in-plane from the superior-anterior end.

Traced on the base (canvas px): nipple (410, 255); axillary hair/apex about
(990, 570); the torso's lateral edge runs from (100, 1170) to (1100, 830),
so the body axis points up-right (cranial) at about -19 degrees and the
anterior-posterior direction across the lateral wall is along (0.32, 0.947).

Code-drawn:
- the mid-axillary line (dashed) running caudally from the axillary apex;
- the probe seen from above as a short rounded bar - the footprint lying
  anterior-posterior across the lateral wall (transverse), centred on the
  mid-axillary line just below nipple level (the 4th-5th ribs), with gel and
  its cable leaving toward the drape;
- the needle in line with the bar, entering at its anterior end from the
  superior-anterior side (in-plane), green hub, tubing.

Run: python3 visuals/serratus_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt  # noqa: E402

ASSET_ID = "serratus_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1198.0, 896.0)

U = (0.32, 0.947)                  # anterior -> posterior across the lateral wall (footprint and needle line)
N = (U[1], -U[0])                  # across the bar
C = (592.0, 752.0)                 # probe centre: mid-axillary line, just below nipple level
HALF_L, HALF_W = 118.0, 36.0       # footprint bar, about 4.5 x 1.2 cm
MAL = [(1000.0, 600.0), (250.0, 856.0)]
AXILLA = (990.0, 570.0)
NEEDLE_ENTRY = (C[0] - U[0] * (HALF_L + 16), C[1] - U[1] * (HALF_L + 16))
NEEDLE_HUB = (C[0] - U[0] * (HALF_L + 230), C[1] - U[1] * (HALF_L + 230))


def at(s, t):
    return (C[0] + U[0] * s + N[0] * t, C[1] + U[1] * s + N[1] * t)


DEFS = """
<linearGradient id="probe-top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C7CDD3"/><stop offset="0.45" stop-color="#F4F6F8"/>
  <stop offset="1" stop-color="#B9C0C7"/></linearGradient>
<linearGradient id="g-steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.5" stop-color="#B9C0C7"/>
  <stop offset="1" stop-color="#6E777F"/></linearGradient>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>
"""


def build() -> str:
    ang = math.degrees(math.atan2(U[1], U[0]))
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    cs = at(HALF_L - 10, 0)
    cable = (f"M{fmt(cs[0])},{fmt(cs[1])} C{fmt(cs[0] + 60)},{fmt(cs[1] + 140)} "
             f"{fmt(cs[0] + 220)},{fmt(cs[1] + 230)} {fmt(cs[0] + 520)},1240")
    tubing = (f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 60)},{fmt(nh[1] - 40)} {fmt(nh[0] - 180)},{fmt(nh[1] + 120)} "
              f"{fmt(nh[0] - 280)},1240")
    labels = [
        Label(["Axilla"], anchor=(1180, 420), leader=[(1190, 440), (AXILLA[0] + 20, AXILLA[1])], target_id="axilla-mark"),
        Label(["Mid-axillary line"], anchor=(40, 1000), leader=[(300, 960), (400, 805)], target_id="mal"),
        Label(["Linear probe"], anchor=(780, 1000), leader=[(800, 960), at(70, HALF_W - 8)], target_id="probe"),
        Label(["Block needle"], anchor=(560, 420), leader=[(580, 440), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
    ]
    painted = BASE.exists()
    scale = 1600 / BASE_SIZE[0]
    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
    else:
        base_attr = base_image = ""

    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy">
  <rect id="chest" x="0" y="0" width="1600" height="1200" fill="#000" opacity="0"/>
</g>

<g class="marking">
  <line id="mal" x1="{fmt(MAL[0][0])}" y1="{fmt(MAL[0][1])}" x2="{fmt(MAL[1][0])}" y2="{fmt(MAL[1][1])}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
  <circle id="axilla-mark" cx="{fmt(AXILLA[0])}" cy="{fmt(AXILLA[1])}" r="50" fill="#000" opacity="0"/>
  <path d="{cable}" fill="none" stroke="#2E3338" stroke-width="22" stroke-linecap="round" opacity="0.9"/>
  <path d="{tubing}" fill="none" stroke="#E6EEF2" stroke-width="9" stroke-linecap="round" opacity="0.9"/>
  <g transform="translate({fmt(C[0])} {fmt(C[1])}) rotate({fmt(ang)})">
    <rect x="{fmt(-HALF_L - 14)}" y="{fmt(-HALF_W - 12)}" width="{fmt(2 * HALF_L + 28)}" height="{fmt(2 * HALF_W + 24)}" rx="34"
          fill="#E8F2F6" opacity="0.18" filter="url(#soft)"/>
    <rect x="{fmt(-HALF_L + 10)}" y="{fmt(-HALF_W + 14)}" width="{fmt(2 * HALF_L)}" height="{fmt(2 * HALF_W)}" rx="26" fill="#1B2733"
          opacity="0.28" filter="url(#soft)"/>
    <rect id="probe" x="{fmt(-HALF_L)}" y="{fmt(-HALF_W)}" width="{fmt(2 * HALF_L)}" height="{fmt(2 * HALF_W)}" rx="26"
          fill="url(#probe-top)" stroke="#7D868F" stroke-width="3"/>
    <rect x="{fmt(-HALF_L + 38)}" y="{fmt(-HALF_W + 12)}" width="{fmt(2 * HALF_L - 76)}" height="{fmt(2 * HALF_W - 24)}" rx="16"
          fill="none" stroke="#A9B0B7" stroke-width="2"/>
    <rect x="{fmt(-HALF_L + 18)}" y="-4" width="20" height="8" rx="4" fill="#8E969E"/>
  </g>
  <rect x="{fmt(nh[0] - 30)}" y="{fmt(nh[1] - 10)}" width="44" height="20" rx="6" fill="#2FA58A" stroke="#1E7A66" stroke-width="2"
        transform="rotate({fmt(ang)} {fmt(nh[0])} {fmt(nh[1])})"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="url(#g-steel)" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" rx="9" ry="6" fill="#B07A66" opacity="0.7" transform="rotate({fmt(ang)} {fmt(ne[0])} {fmt(ne[1])})"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="3" fill="#8A5A4A"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #6FA3A8; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
