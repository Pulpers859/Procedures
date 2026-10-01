"""Femoral nerve block - probe and needle on the patient (layout).

Painted base plus code-drawn markings. base.jpg is Gemini (Nano Banana Pro,
driven through Antigravity) repainting the flat layout of commit 542c88e
as a clinical photograph with prompt A (provenance.json). The thigh, drapes,
probe, cable, needle and tubing lie on the layout within a few pixels, so
the layout shapes stay as the invisible regions (DEBUG=1 shows them); the
probe, its cable, the groin crease and the ASIS are traced in base pixels,
and the skin markings are hidden where the probe and cable cover the skin.
Re-trace them if the base is replaced.

Layout notes follow.

Adapted from the approved FICB positioning layout (commit 7c45a2a): same
groin, same view. Record: supine, leg extended; transducer transverse over
the femoral crease; needle in-plane from lateral to medial. The probe is
centred over the femoral vessels so the nerve, lateral to the artery, lies
under it (added: the exact centring).

Original FICB notes follow.

The positioning half of the pair (owner, 2026-09-30: "for nerve blocks ...
2 separate images, one for patient positioning and one for the anatomy").
ficb_anatomy_layers is the section under this probe.

Right groin and upper thigh from above, patient supine, seen from the foot
of the bed: head at the top, the patient's right on the image left, so
lateral is left and medial is right, the same way round as the anatomy plate
and a transverse ultrasound. Sterile drapes leave a window over the groin.

Landmarks (record anatomy: "the femoral artery medially and the ASIS
laterally; the injection point is lateral to the artery"): the ASIS, the
pubic tubercle, the inguinal ligament between them, and the surface course
of the femoral artery from the mid-inguinal point down the thigh. The linear
probe lies transversely at the inguinal crease, just below the ligament, with
the artery under its medial end (record ultrasound slot: "Linear probe
placed at the inguinal crease"). The needle enters just beyond the probe's
lateral end, in line with it (in-plane from lateral, record steps).

Code-drawn markings: the dashed ligament, the landmark rings and the dashed
artery course. The probe and needle are in the painted layer, for the
painting to render; their placement is checked here and again on the
painting.

Millimetres from the pubic tubercle (x medial, y toward the feet) at
4 px/mm. Adult proportions.

Run: python3 visuals/femoral_nerve_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "femoral_nerve_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
BASE_SCALE = 1600 / BASE_SIZE[0]

# Traced on the painting, in base pixels.
PROBE_FACE = [(512, 238), (525, 232), (655, 232), (664, 245), (664, 282), (650, 292), (600, 300), (560, 305),
              (530, 298), (512, 282)]
CABLE = [(470, 0), (520, 40), (562, 96), (586, 150), (592, 200), (590, 232), (612, 232), (614, 200), (608, 146),
         (582, 86), (540, 30), (506, 0)]
CREASE_PX = [(460, 205), (510, 222), (590, 255), (665, 290), (720, 320), (780, 355), (830, 395)]
ASIS_PX = (372, 105)                               # the painted prominence of the hip bone


def based(points):
    return " ".join(f"{fmt(x * BASE_SCALE)},{fmt(y * BASE_SCALE + (1200 - BASE_SIZE[1] * BASE_SCALE) / 2)}" for x, y in points)


def base_mm(p):
    """base pixels -> mm from the pubic tubercle."""
    return ((p[0] * BASE_SCALE - ORIGIN[0]) / PX_MM, (p[1] * BASE_SCALE + (1200 - BASE_SIZE[1] * BASE_SCALE) / 2 - ORIGIN[1]) / PX_MM)


PX_MM = 4.0
ORIGIN = (1000.0, 380.0)          # canvas of the pubic tubercle


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


ASIS = base_mm(ASIS_PX) if BASE.exists() else (-120.0, -55.0)
# The painting does not show the pubic tubercle; it is placed from the layout,
# 8 mm higher on the painted plate, where the probe was painted about 3 mm
# higher than drawn and would otherwise touch the ligament's medial end.
PUBIC_TUBERCLE = (0.0, -8.0) if BASE.exists() else (0.0, 0.0)
SYMPHYSIS = (25.0, 5.0)
MID_INGUINAL = ((ASIS[0] + SYMPHYSIS[0]) / 2, (ASIS[1] + SYMPHYSIS[1]) / 2)
ARTERY = [(MID_INGUINAL[0], MID_INGUINAL[1] + 4), (-44, 20), (-38, 80), (-31, 150), (-26, 215)]
CREASE = ([base_mm(q) for q in CREASE_PX] if BASE.exists()
          else [(-108, -30), (-80, -16), (-50, -2), (-22, 10), (-4, 20)])

PROBE_CENTRE, PROBE_LEN, PROBE_W = (-55.0, -6.0), 50.0, 16.0
PROBE_X0, PROBE_X1 = PROBE_CENTRE[0] - PROBE_LEN / 2, PROBE_CENTRE[0] + PROBE_LEN / 2
NEEDLE_ENTRY = (PROBE_X0 - 9, PROBE_CENTRE[1])
NEEDLE_HUB = (PROBE_X0 - 44, PROBE_CENTRE[1])

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
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    body_outline = LATERAL + MEDIAL + [(MEDIAL_DRAPE_X + 40, -100)]
    skin = path(body_outline, closed=True, tension=0.6)
    probe_gap = (PROBE_X0 - 2, PROBE_CENTRE[1] - PROBE_W / 2 - 3, PROBE_X1 + 2, PROBE_CENTRE[1] + PROBE_W / 2 + 3)
    artery_pieces = dashed_segments(densify(ARTERY), [] if painted else [probe_gap])

    p0 = c((PROBE_X0, PROBE_CENTRE[1] - PROBE_W / 2))
    pw, ph = PROBE_LEN * PX_MM, PROBE_W * PX_MM
    cable = path([(PROBE_CENTRE[0] + 6, PROBE_CENTRE[1] - PROBE_W / 2), (-50, -40), (-70, -75), (-110, -110)])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    tubing = path([(NEEDLE_HUB[0] - 6, NEEDLE_HUB[1]), (-150, 5), (-165, 40), (-175, 90), (-200, 130)])
    asis, pt = c(ASIS), c(PUBIC_TUBERCLE)

    labels = [
        Label(["ASIS"], anchor=(80, 170), leader=[(210, 188), (asis[0] - 16, asis[1] - 10)], target_id="asis", emphasis=False),
        Label(["Inguinal", "ligament"], anchor=(1150, 110), leader=[(1180, 236), c((-12.5, -13.0))], target_id="inguinal-ligament"),
        Label(["Femoral artery"], anchor=(1050, 1110), leader=[(1060, 1060), c((-34, 120))], target_id="femoral-artery-course",
              emphasis=True),
    ]

    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * BASE_SCALE) / 2)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * BASE_SCALE)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if debug else 0}"'
        probe_shape = f'<polygon id="probe" points="{based(PROBE_FACE)}" fill="#ff00ff"/>'
        mask = (f'<mask id="skin-visible" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200">'
                f'<rect width="1600" height="1200" fill="#fff"/><polygon points="{based(PROBE_FACE)}" fill="#000"/>'
                f'<polygon points="{based(CABLE)}" fill="#000"/></mask>')
        marking_mask = ' mask="url(#skin-visible)"'
    else:
        base_attr = base_image = layout_attr = mask = marking_mask = ""
        probe_shape = (f'<rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(pw)}" height="{fmt(ph)}" rx="22" '
                       f'fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>')

    body = f"""
{mask}
<g id="anatomy"{base_attr}>
  {base_image}
  <g id="layout"{layout_attr}>
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
  {probe_shape}
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="10" stroke-linecap="round" opacity="0.95"/>
  <rect x="{fmt(nh[0] - 36)}" y="{fmt(nh[1] - 9)}" width="40" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path id="femoral-artery-course" d="{path(ARTERY)}" fill="none" stroke="#000" stroke-opacity="0" stroke-width="22"/>
  </g>
</g>

<g class="marking" fill="none" stroke-linecap="butt"{marking_mask}>
  <line id="inguinal-ligament" x1="{fmt(asis[0])}" y1="{fmt(asis[1])}" x2="{fmt(pt[0])}" y2="{fmt(pt[1])}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12"/>
  <circle id="asis" cx="{fmt(asis[0])}" cy="{fmt(asis[1])}" r="18" stroke="#4A2F7A" stroke-width="6"/>
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
