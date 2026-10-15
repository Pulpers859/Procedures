"""Transversus abdominis plane block - probe and needle on the patient (layout).

The right side of the abdomen of a supine adult, seen from above the right
flank: head off the left of the frame, feet off the right, the anterior
abdominal wall (umbilicus at the top) curving down to the flank, which meets
the drape along the bottom. The costal margin runs down the left of the
field, as the edge of the rib cage, and the iliac crest down the right, as the
edge of the hip; both drawn as shaded regions so the painting renders them
as body contours, not lines. A gown is pulled up over the chest beyond the
costal margin and a drape covers the hip below the crest, exposing the flank.

Record: supine, abdomen exposed; transducer transverse on the lateral
abdominal wall, midway between the costal margin and the iliac crest, in the
mid-axillary line; needle in-plane, anterior to posterior or the reverse.
Here: the probe stands upright on the mid-axillary line midway between the
costal margin and the iliac crest, its long face running across the body
(up and down in the picture); the needle enters just above its upper
(anterior) end, in line, aimed posteriorly. The prompt asks for a gloved
hand holding the probe (owner, 2026-10-15: probes read better held).

Standard anatomy added: costal margin and iliac crest about 11 cm apart at
the mid-axillary line; the umbilicus toward the midline.

Millimetres from the probe centre (x toward the feet = image right, y toward
the back = image down) at 3.2 px/mm.

Painted version (2026-10-15): the costal margin is under the gown and the hand
covers the iliac crest, so those are not labelled; a dashed mid-axillary line
is drawn through the probe face instead (record: mid-axillary line).

Run: python3 visuals/tap_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "tap_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 3.2
ORIGIN = (800.0, 640.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


BODY = [(-270, -230), (270, -230), (270, 96), (150, 88), (0, 82), (-150, 86), (-270, 94)]
COSTAL = [(-205, -160), (-150, -115), (-105, -66), (-74, -18), (-58, 30), (-54, 72)]
ILIAC = [(150, -150), (108, -96), (76, -46), (60, 6), (56, 54), (60, 84)]
UMBILICUS = ((10.0, -150.0), 7.0, 5.0)
PROBE_LEN, PROBE_W = 38.0, 8.0
PROBE = ((-PROBE_W / 2, -PROBE_LEN / 2), (PROBE_W / 2, PROBE_LEN / 2))
NEEDLE_ENTRY = (0.0, -PROBE_LEN / 2 - 5)
NEEDLE_HUB = (-2.0, -PROBE_LEN / 2 - 36)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0CDB6"/><stop offset="0.7" stop-color="#E8BDA3"/>
  <stop offset="1" stop-color="#D9A88C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8FB8C9"/><stop offset="1" stop-color="#6F9FB4"/></linearGradient>
<linearGradient id="probe-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9ECEF"/><stop offset="1" stop-color="#B9C0C7"/></linearGradient>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def build() -> str:
    p0, p1 = c(PROBE[0]), c(PROBE[1])
    ne, nh = c(NEEDLE_ENTRY), c(NEEDLE_HUB)
    q = lambda dx, dy: c((dx, dy))
    # Handle seen from above and slightly toward the feet: it narrows as it rises off the skin, drawn to the right.
    handle = (f"M{fmt(q(4, -18)[0])},{fmt(q(0, -18)[1])} C{fmt(q(14, -15)[0])},{fmt(q(0, -15)[1])} {fmt(q(26, -7)[0])},{fmt(q(0, -7)[1])} "
              f"{fmt(q(46, -6)[0])},{fmt(q(0, -6)[1])} L{fmt(q(46, 6)[0])},{fmt(q(0, 6)[1])} C{fmt(q(26, 7)[0])},{fmt(q(0, 7)[1])} "
              f"{fmt(q(14, 15)[0])},{fmt(q(0, 15)[1])} {fmt(q(4, 18)[0])},{fmt(q(0, 18)[1])} Z")
    cable = (f"M{fmt(q(46, 0)[0])},{fmt(q(46, 0)[1])} C{fmt(q(70, 2)[0])},{fmt(q(0, 2)[1])} "
             f"{fmt(q(110, 30)[0])},{fmt(q(0, 30)[1])} {fmt(q(160, 130)[0])},1260")
    tubing = f"M{fmt(nh[0])},{fmt(nh[1])} C{fmt(nh[0] - 20)},{fmt(nh[1] - 80)} {fmt(nh[0] - 150)},{fmt(nh[1] - 120)} {fmt(nh[0] - 330)},-40"
    labels = [
        Label(["Mid-axillary line"], anchor=(40, 760), leader=[(420, 744), (520, c((0, 0))[1])], target_id="mal"),
        Label(["Linear probe"], anchor=(980, 860), leader=[(1000, 820), (p1[0] - 6, p1[1] - 20)], target_id="probe"),
        Label(["Block needle"], anchor=(420, 300), leader=[(640, 320), ((ne[0] + nh[0]) / 2, (ne[1] + nh[1]) / 2)], target_id="needle"),
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
  <path id="body" d="{path(BODY, closed=True, tension=0.3)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="costal" d="{path([(-270, -230), (-215, -230)] + COSTAL + [(-60, 90), (-270, 94)], closed=True, tension=0.4)}" fill="#E4B59B" stroke="#CFA086" stroke-width="2"/>
  <path id="iliac" d="{path([(270, -230), (165, -230)] + ILIAC + [(64, 92), (270, 96)], closed=True, tension=0.4)}" fill="#E4B59B" stroke="#CFA086" stroke-width="2"/>
  <path id="gown" d="{path([(-270, -230), (-280, -230)] + [(x - 75, y) for x, y in COSTAL] + [(-135, 92), (-270, 94)], closed=True, tension=0.4)}" fill="#BFD3DC" stroke="#9FB6C2" stroke-width="3"/>
  <path id="drape" d="{path([(270, -230), (225, -230)] + [(x + 60, y) for x, y in ILIAC] + [(124, 93), (270, 96)], closed=True, tension=0.4)}" fill="#6F9FB4" stroke="#5D8CA1" stroke-width="3"/>
  {ell("umbilicus", UMBILICUS, 'fill="#C99478" stroke="#B07E64" stroke-width="2"')}
  <path d="{tubing}" fill="none" stroke="#E9EEF2" stroke-width="9" stroke-linecap="round"/>
  <rect x="{fmt(nh[0] - 9)}" y="{fmt(nh[1] - 34)}" width="18" height="38" rx="5" fill="#F2F2F2" stroke="#8A9199" stroke-width="2"/>
  <line id="needle" x1="{fmt(nh[0])}" y1="{fmt(nh[1])}" x2="{fmt(ne[0])}" y2="{fmt(ne[1])}" stroke="#8E969E" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(ne[0])}" cy="{fmt(ne[1])}" r="4" fill="#9E6B5A"/>
  <path d="{cable}" fill="none" stroke="#3E454C" stroke-width="14" stroke-linecap="round"/>
  <path id="probe-handle" d="{handle}" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
  <rect id="probe" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" height="{fmt(p1[1] - p0[1])}" rx="12" fill="url(#probe-body)" stroke="#7D868F" stroke-width="3"/>
</g>

<g class="marking">
  <line id="mal" x1="{fmt(c((-125, 0))[0])}" y1="{fmt(c((0, 0))[1])}" x2="{fmt(p0[0] - 14)}" y2="{fmt(c((0, 0))[1])}" stroke="#F6F7F9" stroke-width="10" stroke-dasharray="20 12" stroke-linecap="round" opacity="0.9"/>
  <line x1="{fmt(c((-125, 0))[0])}" y1="{fmt(c((0, 0))[1])}" x2="{fmt(p0[0] - 14)}" y2="{fmt(c((0, 0))[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12" stroke-linecap="round"/>
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
