"""Thoracic erector spinae plane block - probe and needle on the patient (layout).

The bare back of an adult sitting up and leaning slightly forward, seen from
directly behind: head at the top, the patient's right on the image right
(as when standing behind the patient), from the back of the head to the
lower ribs. The same painting, with the probe and needle removed, is the
base of the thoracentesis site plate.

Record: sitting or lateral decubitus; transducer sagittal about 3 cm lateral
to the thoracic spinous processes; needle in-plane, usually cranial to
caudal. NYSORA (concept only, not committed): transducer paramedian sagittal
at T5, patient sitting; needle in-plane from cranial. Here: the probe stands
upright on the right side of the back, its long face running up and down
3 cm from the spinous processes at the level of T5, between the spine and the
medial border of the scapula; the needle enters just above its upper end,
in line, with the hub and tubing above.

Standard anatomy added: spinous processes about 24 mm apart from the C7
prominence; the scapulae with the medial border about 7 cm from the midline
and the inferior angle at about T7.

Millimetres from the C7 spinous process (x patient's right = image right,
y caudal) at 3.4 px/mm.

Run: python3 visuals/esp_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "esp_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 3.4
ORIGIN = (800.0, 205.0)
SP_STEP = 24.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def mirror(points):
    return [(-x, y) for x, y in points]


# Right half of the torso outline, from the nape down the right side.
TORSO_R = [(46, -60), (50, -12), (70, -2), (115, 12), (160, 26), (192, 44), (196, 90), (192, 150), (186, 230), (180, 320)]
ARM_R = [(186, 36), (214, 52), (232, 84), (238, 130), (236, 210), (232, 320), (194, 320), (190, 220), (188, 140), (184, 80)]
SCAPULA_R = [(70, 22), (115, 24), (150, 30), (176, 44), (166, 78), (142, 122), (110, 170), (98, 168), (84, 120), (74, 70)]
HEAD = ((0.0, -105.0), 74.0, 92.0)
SP_COUNT = 12                       # C7 to T11
PC = (30.0, 120.0)                  # probe centre: 3 cm right of the midline at T5
PROBE_LEN, PROBE_W = 38.0, 8.0
PROBE = ((PC[0] - PROBE_W / 2, PC[1] - PROBE_LEN / 2), (PC[0] + PROBE_W / 2, PC[1] + PROBE_LEN / 2))
NEEDLE_ENTRY = (PC[0], PC[1] - PROBE_LEN / 2 - 5)
NEEDLE_HUB = (PC[0] + 2, PC[1] - PROBE_LEN / 2 - 34)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.25" stop-color="#EBC3AA"/>
  <stop offset="0.75" stop-color="#EBC3AA"/><stop offset="1" stop-color="#D9A88C"/></linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E3E8EC"/><stop offset="1" stop-color="#CFD8E0"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def q(dx, dy):
    return c((PC[0] + dx, PC[1] + dy))


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    torso = path(mirror(list(reversed(TORSO_R))) + TORSO_R + [(180, 400), (-180, 400)], closed=True, tension=0.4)
    # Handle seen from slightly lateral: it narrows as it rises off the skin toward the camera and to the right.
    handle = (f"M{fmt(q(4, -18)[0])},{fmt(q(0, -18)[1])} C{fmt(q(14, -15)[0])},{fmt(q(0, -15)[1])} {fmt(q(26, -7)[0])},{fmt(q(0, -7)[1])} "
              f"{fmt(q(46, -6)[0])},{fmt(q(0, -6)[1])} L{fmt(q(46, 6)[0])},{fmt(q(0, 6)[1])} C{fmt(q(26, 7)[0])},{fmt(q(0, 7)[1])} "
              f"{fmt(q(14, 15)[0])},{fmt(q(0, 15)[1])} {fmt(q(4, 18)[0])},{fmt(q(0, 18)[1])} Z")
    cable = (f"M{fmt(q(46, 0)[0])},{fmt(q(46, 0)[1])} C{fmt(q(62, 2)[0])},{fmt(q(0, 2)[1])} "
             f"{fmt(q(80, 20)[0])},{fmt(q(0, 20)[1])} {fmt(q(100, 90)[0])},{fmt(q(0, 90)[1])} S{fmt(q(150, 200)[0])},1260 {fmt(q(170, 220)[0])},1300")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 10)},{fmt(nh[1] - 90)} {fmt(nh[0] + 120)},{fmt(nh[1] - 150)} {fmt(nh[0] + 300)},-40"
    sps = "".join(
        ell(f"sp-{i}" if i else "c7", ((0.0, i * SP_STEP), 5.0 if i else 7.0, 4.0 if i else 5.5), 'fill="#DFAE94" stroke="none"')
        for i in range(SP_COUNT))
    scap = c((120, 120))
    labels = [
        Label(["Linear probe"], anchor=(1060, 860), leader=[(1100, 816), (p1[0] - 6, p1[1] - 20)], target_id="probe"),
        Label(["Block needle"], anchor=(1080, 300), leader=[(1100, 316), ((ne[0] + nh[0]) / 2 + 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
        Label(["Spinous", "processes"], anchor=(330, 900), leader=[(560, 850), c((-1, 9 * SP_STEP))], target_id="spine"),
        Label(["Scapula"], anchor=(1250, 700), leader=[(1300, 656), scap], target_id="scapula"),
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

    s0, s1 = c((0, 4)), c((0, 340))
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="url(#wall)"/>
  <path id="arm-left" d="{path(mirror(ARM_R), closed=True, tension=0.4)}" fill="#E2B49B" stroke="#B98A74" stroke-width="3"/>
  <path id="arm-right" d="{path(ARM_R, closed=True, tension=0.4)}" fill="#E2B49B" stroke="#B98A74" stroke-width="3"/>
  <path id="back" d="{torso}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="scapula-left" d="{path(mirror(SCAPULA_R), closed=True, tension=0.5)}" fill="#E4B79E"/>
  <path id="scapula" d="{path(SCAPULA_R, closed=True, tension=0.5)}" fill="#E4B79E"/>
  <rect id="spine" x="{fmt(s0[0] - 9)}" y="{fmt(s0[1])}" width="18" height="{fmt(s1[1] - s0[1])}" rx="9" fill="#E0B096"/>
  {sps}
  {ell("head", HEAD, 'fill="#4A3B33" stroke="#33281F" stroke-width="3"')}
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 9)}" y="{fmt(nh[1] - 34)}" width="18" height="38" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="12" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #DDE5EC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
