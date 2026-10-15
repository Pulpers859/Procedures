"""Thoracostomy / chest tube - the safe triangle (painted base reused, code-drawn markings).

The base is the owner-approved serratus_patient_position painting (reused,
PLAYBOOK / memory: reuse solved anatomy): the patient's left lateral chest,
supine, arm abducted, head toward the upper right, the nipple at the upper
left, the axilla centre right, the drape along the bottom. The record names
no side; this is the shipped painting of the view the triangle needs.

Record: the triangle is bordered by the anterior border of latissimus dorsi,
the lateral border of pectoralis major, a line superior to the horizontal
level of the nipple, and the apex of the axilla; 4th-5th intercostal space,
mid-axillary line; incise parallel to the rib.

Traced on the base (canvas px), reusing the serratus tracing: nipple
(410, 255); axillary apex about (980, 560); the body axis points up-right
(cranial) at about -19 degrees, so the transverse ("horizontal") direction
across the lateral wall is U = (0.32, 0.947), anterior to posterior. The
anterior axillary fold is the shadowed ridge above the axillary hair; the
posterior fold runs along the junction of the arm and the lower contour.

Code-drawn: the triangle (apex at the axilla, base on the nipple-level line),
the dashed mid-axillary line, and the insertion site at the 4th-5th space on
the mid-axillary line just above the base, with a short incision along the
rib.

Run: python3 visuals/chest_tube_safe_triangle/draw.py
"""

from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt  # noqa: E402

ASSET_ID = "chest_tube_safe_triangle"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1198.0, 896.0)

U = (0.32, 0.947)                     # transverse, anterior -> posterior
AXIS = (U[1], -U[0])                  # cranial
NIPPLE = (410.0, 255.0)
APEX = (980.0, 560.0)
ANT_BASE = (NIPPLE[0] + U[0] * 205, NIPPLE[1] + U[1] * 205)     # nipple line meets the pectoral border
POST_BASE = (NIPPLE[0] + U[0] * 640, NIPPLE[1] + U[1] * 640)    # nipple line meets the latissimus border
MAL = [(1000.0, 600.0), (250.0, 856.0)]
SITE = (575.5 + AXIS[0] * 60, 744.6 + AXIS[1] * 60)            # 4th-5th space on the MAL, just above the base


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def build() -> str:
    tri = " ".join(f"{fmt(p[0])},{fmt(p[1])}" for p in (APEX, ANT_BASE, POST_BASE))
    ang = math.degrees(math.atan2(U[1], U[0]))
    i0 = (SITE[0] - U[0] * 34, SITE[1] - U[1] * 34)
    i1 = (SITE[0] + U[0] * 34, SITE[1] + U[1] * 34)
    pec_mid, lat_mid, base_mid = lerp(APEX, ANT_BASE, 0.45), lerp(APEX, POST_BASE, 0.5), lerp(ANT_BASE, POST_BASE, 0.3)
    labels = [
        Label(["Pectoralis major", "(lateral border)"], anchor=(560, 300), leader=[(700, 392), pec_mid], target_id="pec-border"),
        Label(["Latissimus dorsi", "(anterior border)"], anchor=(860, 960), leader=[(900, 900), lat_mid], target_id="lat-border"),
        Label(["Nipple level"], anchor=(60, 470), leader=[(370, 470), base_mid], target_id="nipple-line"),
        Label(["Axilla"], anchor=(1180, 470), leader=[(1190, 490), (APEX[0] + 20, APEX[1])], target_id="axilla-mark"),
        Label(["4th-5th space,", "mid-axillary line"], anchor=(80, 960), leader=[(340, 900), SITE], target_id="site", emphasis=True),
    ]
    sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
    scale = 1600 / BASE_SIZE[0]
    base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                  f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')

    body = f"""
<g id="painting" data-base-sha256="{sha}">{base_image}</g>
<g id="anatomy">
  <rect id="chest" x="0" y="0" width="1600" height="1200" fill="#000" opacity="0"/>
</g>

<g class="marking">
  <polygon id="triangle" points="{tri}" fill="#3FB59A" fill-opacity="0.26" stroke="none"/>
  <line id="pec-border" x1="{fmt(APEX[0])}" y1="{fmt(APEX[1])}" x2="{fmt(ANT_BASE[0])}" y2="{fmt(ANT_BASE[1])}" stroke="#1E8C74" stroke-width="7" stroke-linecap="round"/>
  <line id="lat-border" x1="{fmt(APEX[0])}" y1="{fmt(APEX[1])}" x2="{fmt(POST_BASE[0])}" y2="{fmt(POST_BASE[1])}" stroke="#1E8C74" stroke-width="7" stroke-linecap="round"/>
  <line id="nipple-line" x1="{fmt(NIPPLE[0])}" y1="{fmt(NIPPLE[1])}" x2="{fmt(POST_BASE[0])}" y2="{fmt(POST_BASE[1])}" stroke="#1E8C74" stroke-width="5" stroke-dasharray="4 12" stroke-linecap="round"/>
  <line x1="{fmt(ANT_BASE[0])}" y1="{fmt(ANT_BASE[1])}" x2="{fmt(POST_BASE[0])}" y2="{fmt(POST_BASE[1])}" stroke="#1E8C74" stroke-width="7" stroke-linecap="round"/>
  <line id="mal" x1="{fmt(MAL[0][0])}" y1="{fmt(MAL[0][1])}" x2="{fmt(MAL[1][0])}" y2="{fmt(MAL[1][1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="18 12"/>
  <circle id="axilla-mark" cx="{fmt(APEX[0])}" cy="{fmt(APEX[1])}" r="40" fill="#000" opacity="0"/>
  <line id="incision" x1="{fmt(i0[0])}" y1="{fmt(i0[1])}" x2="{fmt(i1[0])}" y2="{fmt(i1[1])}" stroke="#F6F7F9" stroke-width="13" stroke-linecap="round"/>
  <line x1="{fmt(i0[0])}" y1="{fmt(i0[1])}" x2="{fmt(i1[0])}" y2="{fmt(i1[1])}" stroke="#D8432A" stroke-width="7" stroke-linecap="round"/>
  <ellipse id="site" cx="{fmt(SITE[0])}" cy="{fmt(SITE[1])}" rx="22" ry="40" fill="#000" opacity="0" transform="rotate({fmt(ang - 90)} {fmt(SITE[0])} {fmt(SITE[1])})"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #6FA3A8; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
