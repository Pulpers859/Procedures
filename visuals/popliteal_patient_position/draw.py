"""Popliteal sciatic block - probe and needle on the patient (layout).

Prone, after a clinical photo the owner shared (2026-10-02; concept only,
not committed; drawn from scratch, no hands). The record's first position.

Camera at the patient's right (lateral) side near the foot, above the bed,
looking up the back of the right thigh toward the hip: the thigh runs
straight up the frame from the knee at the bottom to the drapes over the
buttock (owner, 2026-10-03: the probe must read as transverse, square
across the thigh). Its upper face is the posterior thigh; the narrow strip along
its left edge is the lateral thigh, facing the camera.

Record: prone; transducer transverse over the popliteal crease, traced
proximally to where the tibial and common peroneal nerves join, about 6 cm
above it; needle in-plane from lateral to medial.

Drawn: the probe standing upright on the posterior thigh about 6 cm above
the crease, its footprint across the thigh (transverse); the needle entering
the lateral thigh in the probe's plane, level, aimed medially under the
probe, hub and tubing out to the left. Code-drawn: the dashed crease and a
bracket from the crease to the probe marked 6 cm. Perspective layout;
markings traced on the painting.

Run: python3 visuals/popliteal_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "popliteal_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)

LEFT_EDGE = [(470, 1240), (480, 800), (510, 400), (550, -40)]        # posterior / lateral border
LATERAL_EDGE = [(370, 1240), (380, 800), (415, 400), (460, -40)]      # lateral thigh meets the bed
RIGHT_EDGE = [(1310, 1240), (1300, 800), (1270, 400), (1240, -40)]    # posterior / medial border
_a = (0.0, -1.0)                                                      # the thigh runs straight up the frame
_n = math.hypot(*_a)
AXIS = (_a[0] / _n, _a[1] / _n)                                      # knee to hip
PERP = (-AXIS[1], AXIS[0])                                           # across the thigh, lateral to medial
CREASE_C = (890.0, 1060.0)
PROBE_C = (880.0, 560.0)


def off(p, d, k):
    return (p[0] + d[0] * k, p[1] + d[1] * k)


CREASE = [off(CREASE_C, PERP, -300), off(CREASE_C, PERP, -100), off(CREASE_C, PERP, 120), off(CREASE_C, PERP, 300)]
FOOT = [off(off(PROBE_C, PERP, -110), AXIS, -26), off(off(PROBE_C, PERP, 110), AXIS, -26),
        off(off(PROBE_C, PERP, 110), AXIS, 26), off(off(PROBE_C, PERP, -110), AXIS, 26)]
HANDLE = [off(PROBE_C, PERP, -90), off(PROBE_C, PERP, 90), (PROBE_C[0] + 70, 300), (PROBE_C[0] + 60, -40),
          (PROBE_C[0] - 60, -40), (PROBE_C[0] - 70, 300)]
NEEDLE_ENTRY = off(PROBE_C, PERP, -400)
NEEDLE_HUB = off(PROBE_C, PERP, -660)

DEFS = """
<linearGradient id="post-skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E7BFA4"/><stop offset="1" stop-color="#D9AA8E"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9C0C7"/><stop offset="0.5" stop-color="#E9ECEF"/>
  <stop offset="1" stop-color="#C3CAD1"/></linearGradient>
"""


def pts(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def build() -> str:
    ne, nh = NEEDLE_ENTRY, NEEDLE_HUB
    b_off = 250
    b0, b1 = off(CREASE_C, PERP, b_off), off(PROBE_C, PERP, b_off)
    t = lambda p: (off(p, PERP, -14), off(p, PERP, 14))  # noqa: E731
    t0, t1 = t(b0), t(b1)
    bm = ((b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2)
    labels = [
        Label(["Popliteal crease"], anchor=(40, 1150), leader=[(420, 1110), off(CREASE_C, PERP, -300)], target_id="crease-mark"),
        Label(["6 cm"], anchor=(1340, 760), leader=[(1340, 780), bm], target_id="bracket-hit"),
        Label(["Linear probe"], anchor=(1020, 170), leader=[(1030, 190), (PROBE_C[0] + 40, 300)], target_id="probe-handle"),
        Label(["Block needle"], anchor=(40, 720), leader=[(200, 680), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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

    posterior = smooth_path(LEFT_EDGE, tension=0.5) + " L" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in reversed(RIGHT_EDGE)) + " Z"
    lateral = smooth_path(LATERAL_EDGE, tension=0.5) + " L" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in reversed(LEFT_EDGE)) + " Z"
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#F2F4F6"/>
  <path id="lateral-thigh" d="{lateral}" fill="#C79579" stroke="#A9765F" stroke-width="3"/>
  <path id="leg" d="{posterior}" fill="url(#post-skin)" stroke="#B98A74" stroke-width="3"/>
  <path d="M1050,-40 C1150,120 1300,200 1640,180 L1640,-40 Z" fill="#FFFFFF" stroke="#C9D2DA" stroke-width="3"/>
  <path id="crease" d="{smooth_path(CREASE, tension=0.6)}" fill="none" stroke="#A9765F" stroke-width="7" stroke-linecap="round"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 80)},{fmt(nh[1] + 30)} {fmt(nh[0] - 120)},{fmt(nh[1] + 200)} {fmt(nh[0] - 260)},1240" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <polygon points="{pts([off(off(nh, PERP, -46), AXIS, -12), off(off(nh, PERP, 0), AXIS, -12), off(off(nh, PERP, 0), AXIS, 12), off(off(nh, PERP, -46), AXIS, 12)])}" fill="#2FA58A" stroke="#1E7A66" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="5" fill="#9E6B5A"/>
  <path d="M{fmt(PROBE_C[0])},-40 C{fmt(PROBE_C[0] + 10)},-100 {fmt(PROBE_C[0] + 120)},-140 {fmt(PROBE_C[0] + 200)},-160" fill="none" stroke="#3E454C" stroke-width="18"/>
  <path id="probe-handle" d="{smooth_path(HANDLE, closed=True, tension=0.25)}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <polygon id="probe" points="{pts(FOOT)}" fill="#D5DADF" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <path id="crease-mark" d="{smooth_path(CREASE, tension=0.6)}" fill="none" stroke="#4A2F7A" stroke-width="7" stroke-dasharray="16 10"/>
  <polygon id="bracket-hit" points="{pts([off(b0, PERP, -10), off(b1, PERP, -10), off(b1, PERP, 10), off(b0, PERP, 10)])}" fill="#000" opacity="0"/>
  <g id="bracket" stroke="#4A2F7A" stroke-width="5" fill="none">
    <line x1="{fmt(b0[0])}" y1="{fmt(b0[1])}" x2="{fmt(b1[0])}" y2="{fmt(b1[1])}"/>
    <line x1="{fmt(t0[0][0])}" y1="{fmt(t0[0][1])}" x2="{fmt(t0[1][0])}" y2="{fmt(t0[1][1])}"/>
    <line x1="{fmt(t1[0][0])}" y1="{fmt(t1[0][1])}" x2="{fmt(t1[1][0])}" y2="{fmt(t1[1][1])}"/>
  </g>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F2F4F6; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
