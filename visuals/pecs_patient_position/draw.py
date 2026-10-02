"""PECS I / II block - probe and needle on the patient (layout).

The right anterior chest and shoulder from above, patient supine with the
right arm abducted to 90 degrees on an arm board: head at the top, the
patient's right on the image left (house laterality), so the abducted arm
runs off the left edge and the sternum is at the right.

Record: supine, arm abducted to 90 degrees; transducer oblique below the
lateral third of the clavicle; needle in-plane from medial to lateral.

Drawn: the linear probe below the lateral third of the clavicle, about 5 cm
down at the 3rd-4th rib level, its long axis oblique - the medial end up
and toward the clavicle, the lateral end down toward the axilla, across the
ribs - with an upright handle and cable (the approved interscalene probe
style); the needle entering just beyond the probe's medial (upper-right)
end, in line with it. Standard male anatomy: clavicle about 15 cm, the
nipple at the 4th space on the midclavicular line, the anterior axillary
fold.

Millimetres from the sternal notch (x toward the patient's left = image
right, y down) at 4.4 px/mm.

Run: python3 visuals/pecs_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "pecs_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 4.4
ORIGIN = (1180.0, 230.0)           # canvas of the sternal notch


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Body: neck at the top right, shoulder, the abducted arm along the left, chest below.
BODY = [(110, -60), (22, -60), (18, -30), (-40, -22), (-120, -16), (-160, -12), (-200, -18), (-320, -20),
        (-320, 72), (-200, 70), (-160, 82), (-140, 112), (-138, 160), (-134, 230), (110, 230)]
CLAVICLE = [(-6, 2), (-40, -2), (-80, -8), (-115, -6), (-150, -10)]
AX_FOLD = [(-160, 80), (-140, 92), (-122, 102), (-104, 112)]
NIPPLE = (-84.0, 104.0)
STERNUM = [(0, 8), (0, 60), (0, 120), (0, 180)]
PROBE_C, PROBE_LEN, PROBE_W = (-115.0, 42.0), 46.0, 9.0
DIR = (-0.5, 0.866)                # medial end -> lateral end (image: down and left)
ANG = math.degrees(math.atan2(DIR[1], DIR[0]))
MED_END = (PROBE_C[0] - DIR[0] * PROBE_LEN / 2, PROBE_C[1] - DIR[1] * PROBE_LEN / 2)
NEEDLE_ENTRY = (MED_END[0] - DIR[0] * 8, MED_END[1] - DIR[1] * 8)
NEEDLE_HUB = (MED_END[0] - DIR[0] * 34, MED_END[1] - DIR[1] * 34)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9C2A6"/><stop offset="1" stop-color="#DDAE90"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def build() -> str:
    pc = c(PROBE_C)
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    m = PX_MM
    L, W = PROBE_LEN * m, PROBE_W * m
    # Handle stands up off the probe toward the viewer, drawn leaning up and lateral (toward the shoulder), clear of the needle.
    up = (-0.55, -0.83)
    side = (DIR[0] * PROBE_LEN * m * 0.3, DIR[1] * PROBE_LEN * m * 0.3)
    hp = (pc[0] + up[0] * 46 * m * 0.9, pc[1] + up[1] * 46 * m * 0.9)
    tw = (DIR[0] * 8 * m, DIR[1] * 8 * m)
    handle = (f"M{fmt(pc[0] - side[0])},{fmt(pc[1] - side[1])} Q{fmt((pc[0] + hp[0]) / 2 - tw[0] * 1.4)},{fmt((pc[1] + hp[1]) / 2 - tw[1] * 1.4)} "
              f"{fmt(hp[0] - tw[0])},{fmt(hp[1] - tw[1])} L{fmt(hp[0] + tw[0])},{fmt(hp[1] + tw[1])} "
              f"Q{fmt((pc[0] + hp[0]) / 2 + tw[0] * 1.4)},{fmt((pc[1] + hp[1]) / 2 + tw[1] * 1.4)} {fmt(pc[0] + side[0])},{fmt(pc[1] + side[1])} Z")
    labels = [
        Label(["Clavicle"], anchor=(760, 90), leader=[(780, 110), c((-60, -5))], target_id="clavicle"),
        Label(["Linear probe"], anchor=(40, 760), leader=[(260, 720), (pc[0] - 30, pc[1] + 48)], target_id="probe"),
        Label(["Block needle"], anchor=(900, 560), leader=[(920, 530), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2 + 1)], target_id="needle"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="url(#drape)"/>
  <path id="body" d="{path(BODY, closed=True, tension=0.5)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="clavicle" d="{path(CLAVICLE, tension=0.8)}" fill="none" stroke="#F0CFBA" stroke-width="24" stroke-linecap="round" opacity="0.8"/>
  <path id="axillary-fold" d="{path(AX_FOLD, tension=0.8)}" fill="none" stroke="#C99A80" stroke-width="6"/>
  <path d="{path(STERNUM, tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="5" opacity="0.6"/>
  <circle id="nipple" cx="{fmt(c(NIPPLE)[0])}" cy="{fmt(c(NIPPLE)[1])}" r="{fmt(6 * m)}" fill="#B87F6C"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 50)},{fmt(nh[1] - 30)} {fmt(nh[0] + 160)},{fmt(nh[1] + 20)} {fmt(nh[0] + 220)},{fmt(nh[1] + 260)}" fill="none" stroke="#E9EEF2" stroke-width="8" stroke-linecap="round"/>
  <rect x="-4" y="-8" width="36" height="16" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2" transform="translate({fmt(nh[0])} {fmt(nh[1])}) rotate({fmt(ANG + 180)})"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path d="M{fmt(hp[0])},{fmt(hp[1])} C{fmt(hp[0] - 20)},{fmt(hp[1] - 40)} {fmt(hp[0] - 60)},{fmt(hp[1] - 70)} {fmt(hp[0] - 120)},-20" fill="none" stroke="#3E454C" stroke-width="12" stroke-linecap="round"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <rect id="probe" x="{fmt(-L / 2)}" y="{fmt(-W / 2)}" width="{fmt(L)}" height="{fmt(W)}" rx="{fmt(W / 2)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3" transform="translate({fmt(pc[0])} {fmt(pc[1])}) rotate({fmt(ANG)})"/>
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
