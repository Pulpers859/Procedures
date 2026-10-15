"""Transgluteal / proximal sciatic block - probe and needle on the patient (layout).

An adult lying prone, seen from directly above the right buttock and the
back of the right thigh: head off the top of the frame, feet off the bottom,
the patient's right on the image right (seen from behind, as the section
plate's lateral-right). The natal cleft runs down the left of the field, the
lateral hip bulges at the right with the greater trochanter, and the gluteal
fold crosses below the buttock.

Record: lateral decubitus (Sims) or prone; curvilinear transducer transverse
below the gluteal fold; ischial tuberosity medial and greater trochanter
lateral; needle in-plane. NYSORA (concept only, not committed): needle
in-plane from lateral to medial. Here: prone (the record's alternative,
simpler to read); the curved probe stands upright across the back of the
thigh just below the gluteal fold, midway between the ischial tuberosity and
the greater trochanter; the needle enters just beyond its lateral (right)
end, in line, aimed medially. The prompt adds a gloved hand holding the probe
from above (owner, 2026-10-15: probes read better held).

Standard anatomy added: adult proportions; the ischial tuberosity under the
medial end of the gluteal fold, the greater trochanter at the lateral hip
about 10 cm lateral to it.

Millimetres from the probe centre (x lateral = image right, y toward the
feet = image down) at 2.4 px/mm.

Run: python3 visuals/transgluteal_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "transgluteal_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 2.4
ORIGIN = (800.0, 720.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Right buttock and thigh (medial edge = natal cleft, then the inner thigh), lateral contour on the right.
RIGHT = [(-155, -320), (-153, -120), (-150, -60), (-140, -25), (-118, -6), (-112, 40), (-106, 120), (-100, 220),
         (125, 220), (128, 120), (138, 40), (150, -40), (162, -110), (165, -170), (150, -250), (140, -320)]
LEFT = [(-400, -320), (-155, -320), (-153, -120), (-150, -60), (-165, -25), (-195, -8), (-210, 40), (-220, 120), (-226, 220), (-400, 220)]
MOUND = ((-60.0, -120.0), 165.0, 95.0)       # right buttock; its lower edge is the gluteal fold
FOLD = [(x, MOUND[0][1] + MOUND[2] * math.sqrt(1 - ((x - MOUND[0][0]) / MOUND[1]) ** 2)) for x in range(-140, 70, 10)]
CLEFT = [(-400, -320), (-155, -320), (-153, -120), (-150, -60), (-165, -25), (-195, -8), (-210, 40), (-220, 120), (-226, 220), (-400, 220)]
TROCHANTER = ((140.0, -95.0), 18.0, 24.0)
ISCHIUM = ((-70.0, -38.0), 16.0, 12.0)
PROBE_LEN, PROBE_W = 60.0, 14.0
PROBE = ((-PROBE_LEN / 2, -PROBE_W / 2), (PROBE_LEN / 2, PROBE_W / 2))
NEEDLE_ENTRY = (PROBE_LEN / 2 + 5, 0.0)
NEEDLE_HUB = (PROBE_LEN / 2 + 38, -6.0)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E2B69C"/><stop offset="0.5" stop-color="#F0CDB6"/>
  <stop offset="1" stop-color="#D9A88C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8FB8C9"/><stop offset="1" stop-color="#6F9FB4"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    q = lambda dx, dy: c((dx, dy))
    handle = (f"M{fmt(q(-24, 0)[0])},{fmt(p0[1] + 4)} C{fmt(q(-20, 0)[0])},{fmt(q(0, -16)[1])} {fmt(q(-11, 0)[0])},{fmt(q(0, -30)[1])} "
              f"{fmt(q(-8, 0)[0])},{fmt(q(0, -52)[1])} L{fmt(q(8, 0)[0])},{fmt(q(0, -52)[1])} C{fmt(q(11, 0)[0])},{fmt(q(0, -30)[1])} "
              f"{fmt(q(20, 0)[0])},{fmt(q(0, -16)[1])} {fmt(q(24, 0)[0])},{fmt(p0[1] + 4)} Z")
    cable = (f"M{fmt(q(0, -52)[0])},{fmt(q(0, -52)[1])} C{fmt(q(0, -66)[0])},{fmt(q(0, -66)[1])} "
             f"{fmt(q(-20, -90)[0])},{fmt(q(0, -90)[1])} {fmt(q(-40, -200)[0])},-20")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 80)},{fmt(nh[1] - 10)} {fmt(nh[0] + 140)},{fmt(nh[1] + 120)} {fmt(nh[0] + 200)},1240"
    labels = [
        Label(["Gluteal fold"], anchor=(40, 400), leader=[(330, 420), c((-80, MOUND[0][1] + MOUND[2] * math.sqrt(1 - (20 / 165) ** 2)))], target_id="fold"),
        Label(["Greater", "trochanter"], anchor=(1280, 240), leader=[(1320, 276), c((140, -95))], target_id="trochanter"),
        Label(["Curved probe"], anchor=(330, 940), leader=[(600, 900), (p0[0] + 30, p1[1] - 10)], target_id="probe"),
        Label(["Block needle"], anchor=(1060, 860), leader=[(1100, 820), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <rect x="0" y="0" width="1600" height="1200" fill="url(#sheet)"/>
  <path id="left-side" d="{path(LEFT, closed=True, tension=0.4)}" fill="#E6BBA1" stroke="#B98A74" stroke-width="3"/>
  <path id="buttock" d="{path(RIGHT, closed=True, tension=0.4)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <clipPath id="right-clip"><path d="{path(RIGHT, closed=True, tension=0.4)}"/></clipPath>
  <ellipse id="mound" cx="{fmt(c(MOUND[0])[0])}" cy="{fmt(c(MOUND[0])[1])}" rx="{fmt(MOUND[1] * PX_MM)}" ry="{fmt(MOUND[2] * PX_MM)}" fill="#F2D3BE" clip-path="url(#right-clip)"/>
  <path id="cleft" d="{path(CLEFT, tension=0.6)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  {ell("trochanter", TROCHANTER, 'fill="#E8BCA2" stroke="#D2A487" stroke-width="2"')}
  <path id="fold" d="{path(FOLD, tension=0.6)}" fill="none" stroke="#B98A74" stroke-width="6" stroke-linecap="round"/>
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 4)}" y="{fmt(nh[1] - 9)}" width="38" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="20" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #8FB8C9; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
