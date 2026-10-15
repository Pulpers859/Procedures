"""Sural nerve block - probe and needle on the patient (layout).

The outer side of the right ankle and foot, the leg rolled inward so the
lateral malleolus faces the camera: leg up out of the top of the frame, foot
pointing to the right with the sole along the bottom on the drape, heel at
the lower left, the Achilles tendon running up the left edge of the ankle.
Camera after NYSORA's sural photo (concept only, not committed), mirrored to
the right foot.

Record: supine, foot internally rotated; transducer transverse behind the
lateral malleolus. NYSORA: transducer transverse between the lateral
malleolus and the Achilles tendon; needle in-plane or out of plane. Here:
the probe lies across the groove behind the malleolus, just above its tip,
its long face running front to back from the malleolus to the Achilles
tendon; the needle enters just beyond its front (right) end, in line, as on
the section plate.

Upright probe as in the superficial peroneal and deep peroneal layouts, for
the painting to render; code-drawn over the painting: labels only.

Millimetres from the tip of the lateral malleolus (x toward the toes = image
right, y toward the sole) at 5.0 px/mm.

Run: python3 visuals/sural_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "sural_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 5.0
ORIGIN = (520.0, 640.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Outline, clockwise from the back of the leg at the top of the frame.
POSTERIOR = [(-40, -140), (-36, -100), (-33, -62), (-33, -32), (-36, -8), (-44, 14), (-50, 34), (-50, 50), (-42, 62)]
SOLE = [(-26, 68), (0, 68), (30, 64), (62, 64), (100, 70), (140, 74), (170, 74), (196, 70), (208, 62)]
DORSUM = [(204, 52), (180, 46), (140, 38), (100, 22), (66, 4), (44, -16), (34, -38), (32, -70), (34, -105), (38, -140)]
LAT_MALLEOLUS = ((-3.0, -5.0), 11.0, 13.0)   # traced on the painting (layout had (2, -14), 12 x 16; commit 1bfe7a8)
T_ENTRY = (589.0, 531.0)                       # canvas px: where the painted needle meets the skin
ACHILLES = [(-36, -120), (-31, -80), (-28, -45), (-30, -15), (-37, 8)]
PC = (-12.0, -22.0)                 # probe centre: across the groove behind the malleolus, just above its tip
PROBE_LEN, PROBE_W = 38.0, 8.0
PROBE = ((PC[0] - PROBE_LEN / 2, PC[1] - PROBE_W / 2), (PC[0] + PROBE_LEN / 2, PC[1] + PROBE_W / 2))
NEEDLE_ENTRY = (PC[0] + PROBE_LEN / 2 + 5, PC[1])
NEEDLE_HUB = (PC[0] + PROBE_LEN / 2 + 32, PC[1] - 4)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.3" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def q(dx, dy):
    return c((PC[0] + dx, PC[1] + dy))


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    foot = path(POSTERIOR + SOLE + DORSUM, closed=True, tension=0.4)
    handle = (f"M{fmt(q(-16, 0)[0])},{fmt(p0[1] + 4)} C{fmt(q(-13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(-7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(-6, 0)[0])},{fmt(q(0, -44)[1])} L{fmt(q(6, 0)[0])},{fmt(q(0, -44)[1])} C{fmt(q(7, 0)[0])},{fmt(q(0, -24)[1])} "
              f"{fmt(q(13, 0)[0])},{fmt(q(0, -12)[1])} {fmt(q(16, 0)[0])},{fmt(p0[1] + 4)} Z")
    cable = (f"M{fmt(q(0, -44)[0])},{fmt(q(0, -44)[1])} C{fmt(q(-2, -56)[0])},{fmt(q(0, -56)[1])} "
             f"{fmt(q(-20, -70)[0])},{fmt(q(0, -70)[1])} {fmt(q(-40, -130)[0])},-20")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] + 90)},{fmt(nh[1] - 20)} {fmt(nh[0] + 160)},{fmt(nh[1] - 140)} {fmt(nh[0] + 260)},-40"
    lm = c(LAT_MALLEOLUS[0])
    labels = [
        Label(["Lateral", "malleolus"], anchor=(760, 800), leader=[(790, 740), (lm[0] + 10, lm[1] + 10)], target_id="lat-malleolus"),
        Label(["Achilles", "tendon"], anchor=(40, 760), leader=[(150, 700), c((-30, -15))], target_id="achilles"),
        Label(["Linear probe"], anchor=(40, 150), leader=[(300, 170), (p0[0] + 95, (p0[1] + p1[1]) / 2)], target_id="probe"),
        Label(["Block needle"], anchor=(1000, 300), leader=[(1060, 320), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <path id="foot" d="{foot}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="achilles" d="{path(ACHILLES, tension=0.5)}" fill="none" stroke="#D2A288" stroke-width="22" stroke-linecap="round"/>
  {ell("lat-malleolus", LAT_MALLEOLUS, 'fill="#E2B39A" stroke="#C49379" stroke-width="2"')}
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 4)}" y="{fmt(nh[1] - 9)}" width="38" height="18" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="16" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <ellipse cx="{fmt(T_ENTRY[0] - 2)}" cy="{fmt(T_ENTRY[1] + 1)}" rx="9" ry="5" fill="#8A5A4A" opacity="0.45"/>
  <circle cx="{fmt(T_ENTRY[0] - 1)}" cy="{fmt(T_ENTRY[1])}" r="2.6" fill="#6E4436" opacity="0.85"/>
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
