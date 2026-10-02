"""PENG block - probe and needle on the patient (layout).

Reuses the approved femoral_nerve_patient_position layout (commit 542c88e):
the same right groin, drapes and frame, so its approved painting can be
attached as the style image (owner, 2026-10-02: reuse solved anatomy). Only
the probe, cable and needle move.

Right groin and upper thigh from above, patient supine, head at the top,
lateral on the image left, medial on the right - the same way round as the
anatomy plate.

Record: supine; transducer transverse over the AIIS, slid caudally to the
iliopubic eminence and psoas tendon; needle in-plane from lateral to medial.
NYSORA (concept only): the transducer lies transverse-oblique, parallel to
the inguinal ligament, just below it.

Drawn: the probe below the lateral half of the ligament, its axis parallel
to it, centred over the iliopubic eminence about 3 cm lateral to the femoral
artery (standard anatomy), its medial end short of the artery; the needle
entering beyond the probe's lateral end, in line with it. The AIIS is marked
about 3 cm below the ASIS (standard anatomy).

Millimetres from the pubic tubercle (x toward the midline = image right, y
toward the feet) at 4 px/mm.

Run: python3 visuals/peng_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "peng_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 4.0
ORIGIN = (1000.0, 380.0)          # canvas of the pubic tubercle


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


ASIS = (-120.0, -55.0)
PUBIC_TUBERCLE = (0.0, 0.0)
SYMPHYSIS = (25.0, 5.0)
MID_INGUINAL = ((ASIS[0] + SYMPHYSIS[0]) / 2, (ASIS[1] + SYMPHYSIS[1]) / 2)
ARTERY = [(MID_INGUINAL[0], MID_INGUINAL[1] + 4), (-44, 20), (-38, 80), (-31, 150), (-26, 215)]
CREASE = [(-108, -30), (-80, -16), (-50, -2), (-22, 10), (-4, 20)]

import math  # noqa: E402

PROBE_CENTRE, PROBE_LEN, PROBE_W = (-75.0, -14.0), 50.0, 16.0
ANGLE = math.degrees(math.atan2(-ASIS[1], -ASIS[0]))   # parallel to the ligament, medial end lower
_U = (math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE)))
PROBE_X0, PROBE_X1 = PROBE_CENTRE[0] - PROBE_LEN / 2, PROBE_CENTRE[0] + PROBE_LEN / 2
PROBE_LAT = (PROBE_CENTRE[0] - _U[0] * PROBE_LEN / 2, PROBE_CENTRE[1] - _U[1] * PROBE_LEN / 2)
NEEDLE_ENTRY = (PROBE_LAT[0] - _U[0] * 9, PROBE_LAT[1] - _U[1] * 9)
NEEDLE_HUB = (PROBE_LAT[0] - _U[0] * 44, PROBE_LAT[1] - _U[1] * 44)
AIIS = (ASIS[0] + 6.0, ASIS[1] + 30.0)

# Body outline under the drapes: lateral contour of hip and thigh, medial
# contour of the thigh below the groin.
LATERAL = [(-186, -100), (-188, -40), (-184, 20), (-176, 90), (-166, 160), (-160, 215)]
MEDIAL = [(4, 215), (9, 150), (16, 90), (28, 45), (40, 22)]
TOP_DRAPE_Y, MEDIAL_DRAPE_X = -86.0, 40.0

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.25" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
<radialGradient id="asis-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#F6DCCB"/><stop offset="1" stop-color="#F6DCCB" stop-opacity="0"/></radialGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def dashed_segments(points, gaps):
    """Split a polyline (mm) into pieces outside the x-ranges in `gaps`."""
    out, cur = [], []
    for p in points:
        inside = any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for x0, y0, x1, y1 in gaps)
        if inside:
            if len(cur) > 1:
                out.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        out.append(cur)
    return out


def densify(points, n=12):
    out = []
    for a, b in zip(points, points[1:]):
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    return out + [points[-1]]


def build() -> str:
    body_outline = LATERAL + MEDIAL + [(MEDIAL_DRAPE_X + 40, -100)]
    skin = path(body_outline, closed=True, tension=0.6)
    artery_pieces = [densify(ARTERY)]
    aiis = c(AIIS)

    p0 = c((PROBE_X0, PROBE_CENTRE[1] - PROBE_W / 2))
    pw, ph = PROBE_LEN * PX_MM, PROBE_W * PX_MM
    cable = path([(PROBE_CENTRE[0] + 4, PROBE_CENTRE[1] - PROBE_W / 2 + 1), (-68, -45), (-82, -80), (-110, -110)])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    tubing = path([(NEEDLE_HUB[0] - 5, NEEDLE_HUB[1] - 2), (-150, -40), (-168, 0), (-176, 60), (-200, 130)])
    asis, pt = c(ASIS), c(PUBIC_TUBERCLE)

    labels = [
        Label(["ASIS"], anchor=(60, 90), leader=[(180, 110), (asis[0] - 16, asis[1] - 10)], target_id="asis", emphasis=False),
        Label(["Inguinal", "ligament"], anchor=(1150, 110), leader=[(1180, 236), c((-30, -13.75))], target_id="inguinal-ligament"),
        Label(["Femoral artery"], anchor=(1050, 1110), leader=[(1060, 1060), c((-34, 120))], target_id="femoral-artery-course"),
        Label(["AIIS"], anchor=(80, 470), leader=[(190, 440), (aiis[0] - 12, aiis[1] + 10)], target_id="aiis"),
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
  <path id="skin" d="{skin}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <ellipse cx="{fmt(asis[0])}" cy="{fmt(asis[1])}" rx="70" ry="46" fill="url(#asis-glow)"/>
  <path id="inguinal-crease" d="{path(CREASE)}" fill="none" stroke="#B98A74" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
  <rect id="top-drape" x="0" y="0" width="1600" height="{fmt(c((0, TOP_DRAPE_Y))[1])}" fill="url(#drape)"/>
  <rect id="medial-drape" x="{fmt(c((MEDIAL_DRAPE_X, 0))[0])}" y="0" width="{fmt(1600 - c((MEDIAL_DRAPE_X, 0))[0])}" height="1200" fill="url(#drape)"/>
  <g fill="none" stroke="#3B6A92" stroke-width="4" opacity="0.6" stroke-linecap="round">
    <path d="M40,{fmt(c((0, TOP_DRAPE_Y))[1] - 40)} C400,{fmt(c((0, TOP_DRAPE_Y))[1] - 70)} 900,{fmt(c((0, TOP_DRAPE_Y))[1] - 20)} 1560,{fmt(c((0, TOP_DRAPE_Y))[1] - 55)}"/>
    <path d="M{fmt(c((MEDIAL_DRAPE_X, 0))[0] + 60)},420 C{fmt(c((MEDIAL_DRAPE_X, 0))[0] + 30)},700 {fmt(c((MEDIAL_DRAPE_X, 0))[0] + 90)},900 {fmt(c((MEDIAL_DRAPE_X, 0))[0] + 50)},1180"/>
  </g>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="16" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(pw)}" height="{fmt(ph)}" rx="22" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3" transform="rotate({fmt(ANGLE)} {fmt(c(PROBE_CENTRE)[0])} {fmt(c(PROBE_CENTRE)[1])})"/>
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="10" stroke-linecap="round" opacity="0.95"/>
  <rect x="{fmt(nh[0] - 36)}" y="{fmt(nh[1] - 9)}" width="40" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2" transform="rotate({fmt(ANGLE)} {fmt(nh[0])} {fmt(nh[1])})"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path id="femoral-artery-course" d="{path(ARTERY)}" fill="none" stroke="#000" stroke-opacity="0" stroke-width="22"/>
</g>

<g class="marking" fill="none" stroke-linecap="butt">
  <line id="inguinal-ligament" x1="{fmt(asis[0])}" y1="{fmt(asis[1])}" x2="{fmt(pt[0])}" y2="{fmt(pt[1])}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
  <circle id="asis" cx="{fmt(asis[0])}" cy="{fmt(asis[1])}" r="18" stroke="#4A2F7A" stroke-width="6"/>
  <circle id="aiis" cx="{fmt(aiis[0])}" cy="{fmt(aiis[1])}" r="16" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="8 6"/>
  <circle id="pubic-tubercle" cx="{fmt(pt[0])}" cy="{fmt(pt[1])}" r="14" stroke="#4A2F7A" stroke-width="6"/>
  {"".join(f'<path d="{path(piece)}" stroke="#C8322B" stroke-width="7" stroke-dasharray="16 11"/>' for piece in artery_pieces)}
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
