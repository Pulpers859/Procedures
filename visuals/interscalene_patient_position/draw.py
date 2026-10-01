"""Interscalene block - probe and needle on the patient (layout).

The right side of the neck from above, patient supine with the head turned
to the left: head at the top, the patient's right (posterior neck,
shoulder) on the image left, the chin and midline to the right. Sterile
drapes frame the neck. The same way round as the anatomy plate.

Record: linear probe transverse, scanned up from the supraclavicular fossa
to the interscalene level; needle in-plane from posterior to anterior
(lateral to medial). NYSORA (concept only): transducer transverse about
2-3 cm above the clavicle, over the external jugular vein.

Landmarks drawn: the sternocleidomastoid (its lateral border is where the
groove lies, under the probe), the clavicle, the external jugular vein
crossing the muscle, the ear and jaw for orientation. The probe lies
transverse across the lateral border of the SCM about 3 cm above the
clavicle; the needle enters just beyond its posterior (left) end, in line.

Code-drawn markings: the dashed SCM lateral border. The probe and needle are
in the painted layer; their placement is checked here and on the painting.

Millimetres from the probe's centre (x toward the midline = image right,
y toward the feet) at 8 px/mm. Adult proportions.

Run: python3 visuals/interscalene_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "interscalene_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 8.0
ORIGIN = (760.0, 640.0)            # canvas of the probe centre


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


CLAVICLE_Y = 34.0                   # probe ~3 cm above the clavicle
CLAVICLE = [(-90, CLAVICLE_Y + 4), (-50, CLAVICLE_Y + 1), (-10, CLAVICLE_Y), (30, CLAVICLE_Y + 2), (60, CLAVICLE_Y + 6)]
# Sternocleidomastoid band, mastoid (upper left) to sternoclavicular joint (lower right).
SCM_LATERAL = [(-48, -70), (-30, -40), (-8, -10), (6, 10), (22, 36)]
SCM_MEDIAL = [(-28, -76), (-8, -46), (14, -16), (30, 8), (48, 38)]
EJV = [(-14, -76), (-14, -46), (-15, -16), (-18, 8), (-24, 30)]
JAW = [(-50, -78), (-20, -77), (20, -72), (60, -62), (90, -56)]
EAR = (-62.0, -70.0)
PROBE_LEN, PROBE_W = 50.0, 9.0
PROBE = ((-PROBE_LEN / 2, -PROBE_W / 2), (PROBE_LEN / 2, PROBE_W / 2))
NEEDLE_ENTRY = (-PROBE_LEN / 2 - 9, 0.0)
NEEDLE_HUB = (-PROBE_LEN / 2 - 40, 0.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.4" stop-color="#EBC3AA"/>
  <stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    scm = path(SCM_LATERAL + list(reversed(SCM_MEDIAL)), closed=True, tension=0.6)
    labels = [
        Label(["Block needle"], anchor=(40, 470), leader=[(200, 500), ((ne[0] + nh[0]) / 2, ne[1] - 2)], target_id="needle"),
        Label(["Linear probe"], anchor=(1180, 760), leader=[(1200, 720), (p1[0] - 30, (p0[1] + p1[1]) / 2)], target_id="probe"),
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
  <path id="skin" d="M120,0 H1600 V1200 H60 C80,900 100,500 120,0 Z" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="jaw" d="{path(JAW, tension=0.7)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  <path d="M{fmt(c(JAW[0])[0])},0 L{fmt(c(JAW[0])[0])},{fmt(c(JAW[0])[1])} {' '.join(f'L{fmt(c(q)[0])},{fmt(c(q)[1])}' for q in JAW[1:])} L1600,{fmt(c(JAW[-1])[1])} L1600,0 Z" fill="#D9A88C"/>
  <ellipse id="ear" cx="{fmt(c(EAR)[0])}" cy="{fmt(c(EAR)[1])}" rx="70" ry="110" fill="#D79E86" stroke="#A9765F" stroke-width="3"/>
  <path id="scm" d="{scm}" fill="#E3B49A" stroke="#C49478" stroke-width="3"/>
  <path id="ejv" d="{path(EJV, tension=0.8)}" fill="none" stroke="#8C94B4" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
  <path id="clavicle" d="{path(CLAVICLE, tension=0.8)}" fill="none" stroke="#EED8C6" stroke-width="26" stroke-linecap="round"/>
  <rect x="0" y="{fmt(c((0, CLAVICLE_Y + 16))[1])}" width="1600" height="400" fill="url(#drape)"/>
  <path id="probe-handle" d="M{fmt(c((-20, -PROBE_W / 2))[0])},{fmt(p0[1] + 4)} C{fmt(c((-16, -16))[0])},{fmt(c((0, -16))[1])} {fmt(c((-9, -30))[0])},{fmt(c((0, -34))[1])} {fmt(c((-7, -58))[0])},{fmt(c((0, -58))[1])} L{fmt(c((7, -58))[0])},{fmt(c((0, -58))[1])} C{fmt(c((9, -34))[0])},{fmt(c((0, -34))[1])} {fmt(c((16, -16))[0])},{fmt(c((0, -16))[1])} {fmt(c((20, -PROBE_W / 2))[0])},{fmt(p0[1] + 4)} Z" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="M{fmt(c((0, -58))[0])},{fmt(c((0, -58))[1])} C{fmt(c((2, -70))[0])},{fmt(c((0, -70))[1])} {fmt(c((14, -80))[0])},{fmt(c((0, -80))[1])} {fmt(c((26, -92))[0])},0" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="20" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 80)},{fmt(nh[1])} {fmt(nh[0] - 140)},{fmt(nh[1] + 80)} {fmt(nh[0] - 180)},{fmt(nh[1] + 260)}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 34)}" y="{fmt(nh[1] - 9)}" width="38" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
</g>

<mask id="skin-visible" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200"><rect width="1600" height="1200" fill="#fff"/>
  <rect x="{fmt(p0[0] - 6)}" y="{fmt(p0[1] - 6)}" width="{fmt(p1[0] - p0[0] + 12)}" height="{fmt(p1[1] - p0[1] + 12)}" rx="24" fill="#000"/></mask>
<g class="marking" fill="none" mask="url(#skin-visible)">
  <path id="scm-border" d="{path(SCM_LATERAL, tension=0.8)}" stroke="#4A2F7A" stroke-width="6" stroke-dasharray="18 12" opacity="{0 if painted else 1}"/>
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
