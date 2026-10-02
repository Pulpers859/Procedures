"""Intraosseous access - the proximal humerus insertion site (layout).

The right shoulder and upper arm from the front, patient supine, arm
adducted at the side with the hand on the abdomen (internal rotation): the
shoulder at the top, the arm running off the bottom edge, the patient's right
on the image left, so lateral is left and medial (the chest) is right (house
laterality). A gown covers the chest.

Record: palpate the greater tubercle, the most prominent lateral bony point
of the shoulder; needle at 45 degrees to the anterior plane, aimed
posteromedially, not 90 degrees.

Standard adult anatomy added: the acromion about 4 cm above the greater
tubercle, the clavicle running medially from it, the deltoid contour, the
deltopectoral groove. The inset is a schematic of the right humeral head
seen from above (from the head of the bed): anterior up, lateral left, the
greater tubercle anterolateral with the arm internally rotated, the glenoid
medial.

Code-drawn markings: the teal 1 cm insertion zone on the greater tubercle
and the whole inset (needle at 45 degrees to the dashed anterior plane).

Millimetres from the insertion site (x medial = image right, y distal =
image down) at 5 px/mm. Adult proportions. The inset is not to scale.

Run: python3 visuals/io_humeral_site/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "io_humeral_site"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 5.0
ORIGIN = (500.0, 470.0)            # canvas of the insertion site


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Body outline: neck and trapezius at the top right, over the shoulder, down the arm.
BODY = [(240, -110), (140, -110), (112, -80), (78, -60), (40, -52), (8, -50), (-16, -47), (-31, -39),
        (-40, -24), (-43, -2), (-42, 24), (-39, 60), (-35, 100), (-33, 140), (-32, 170), (240, 170)]
GOWN = [(240, -110), (128, -110), (100, -60), (78, -20), (64, 20), (52, 60), (44, 100), (40, 170), (240, 170)]
CLAVICLE = [(6, -42), (30, -44), (55, -41), (90, -37)]
ACROMION = ((-8.0, -41.0), 13.0, 6.0)
DELTOPECTORAL = [(58, -42), (52, -18), (45, 8)]
TARGET = (0.0, 0.0)
TARGET_R = 5.0                     # a 1 cm zone

# Inset (canvas px): humeral head from above, anterior up, lateral left.
INSET = (1030.0, 640.0, 1570.0, 1170.0)
HEAD_C, HEAD_R = (1370.0, 975.0), 95.0
TUBERCLE_ANGLE = 222.0             # anterolateral, image degrees (0 right, 90 down)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.5" stop-color="#EDC7AE"/>
  <stop offset="1" stop-color="#DDAE92"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="gown-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A9C3D8"/><stop offset="1" stop-color="#8FAEC7"/></linearGradient>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(e[2] * PX_MM)}" {attrs}/>'


def on_head(deg, r):
    a = math.radians(deg)
    return (HEAD_C[0] + r * math.cos(a), HEAD_C[1] + r * math.sin(a))


def inset() -> tuple[str, dict]:
    x0, y0, x1, y1 = INSET
    tub = on_head(TUBERCLE_ANGLE, HEAD_R + 16)
    # Needle: 45 degrees to the anterior (horizontal) plane, aimed posteromedially (down-right).
    d = (math.cos(math.radians(45)), math.sin(math.radians(45)))
    tip = (tub[0] + d[0] * 26, tub[1] + d[1] * 26)
    hub = (tub[0] - d[0] * 190, tub[1] - d[1] * 190)
    plane_y = tub[1]
    arc_r = 70
    arc0 = (tub[0] - arc_r, plane_y)
    arc1 = (tub[0] - arc_r * d[0], tub[1] - arc_r * d[1])
    soft = smooth_path([(HEAD_C[0] + dx, HEAD_C[1] + dy) for dx, dy in
                        [(-200, -10), (-170, -140), (-50, -200), (90, -180), (165, -100), (180, 30), (130, 150), (-30, 170), (-160, 110)]],
                       closed=True, tension=0.8)
    glenoid = (f'M{fmt(HEAD_C[0] + HEAD_R + 16)},{fmt(HEAD_C[1] - 62)} Q{fmt(HEAD_C[0] + HEAD_R - 6)},{fmt(HEAD_C[1])} '
               f'{fmt(HEAD_C[0] + HEAD_R + 16)},{fmt(HEAD_C[1] + 62)} L{fmt(HEAD_C[0] + HEAD_R + 60)},{fmt(HEAD_C[1] + 30)} '
               f'L{fmt(HEAD_C[0] + 172)},{fmt(HEAD_C[1] + 50)} L{fmt(HEAD_C[0] + 172)},{fmt(HEAD_C[1] - 6)} L{fmt(HEAD_C[0] + HEAD_R + 60)},{fmt(HEAD_C[1] - 34)} Z')
    tb = [on_head(TUBERCLE_ANGLE - 26, HEAD_R - 4), on_head(TUBERCLE_ANGLE - 12, HEAD_R + 14), tub,
          on_head(TUBERCLE_ANGLE + 14, HEAD_R + 12), on_head(TUBERCLE_ANGLE + 28, HEAD_R - 4)]
    svg = f"""
  <g id="inset">
    <rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" rx="28" fill="#F6F7F9" fill-opacity="0.96" stroke="#9AA6B2" stroke-width="3"/>
    <path id="inset-soft-tissue" d="{soft}" fill="#F1D3C1" stroke="#C99A80" stroke-width="3"/>
    <path id="inset-glenoid" d="{glenoid}" fill="#EFE6D2" stroke="#A8977A" stroke-width="3"/>
    <circle id="humeral-head" cx="{fmt(HEAD_C[0])}" cy="{fmt(HEAD_C[1])}" r="{fmt(HEAD_R)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="4"/>
    <circle cx="{fmt(HEAD_C[0])}" cy="{fmt(HEAD_C[1])}" r="{fmt(HEAD_R - 14)}" fill="#E8C9B8"/>
    <path id="inset-tubercle" d="{smooth_path(tb, tension=0.7)} Z" fill="#EFE6D2" stroke="#A8977A" stroke-width="4"/>
    <line id="anterior-plane" x1="{fmt(x0 + 24)}" y1="{fmt(plane_y)}" x2="{fmt(tub[0] + 30)}" y2="{fmt(plane_y)}"
          stroke="#4A2F7A" stroke-width="4" stroke-dasharray="14 10"/>
    <path id="angle-arc" d="M{fmt(arc0[0])},{fmt(arc0[1])} A{arc_r},{arc_r} 0 0 1 {fmt(arc1[0])},{fmt(arc1[1])}"
          fill="none" stroke="#4A2F7A" stroke-width="5"/>
    <line id="inset-needle" x1="{fmt(hub[0])}" y1="{fmt(hub[1])}" x2="{fmt(tip[0])}" y2="{fmt(tip[1])}"
          stroke="#7B848C" stroke-width="9" stroke-linecap="round"/>
    <line x1="{fmt(hub[0])}" y1="{fmt(hub[1])}" x2="{fmt(tip[0])}" y2="{fmt(tip[1])}" stroke="#E6EAEE" stroke-width="3" stroke-linecap="round"/>
    <rect x="-34" y="-11" width="40" height="22" rx="5" fill="#C9D0D6" stroke="#7B848C" stroke-width="3"
          transform="translate({fmt(hub[0])} {fmt(hub[1])}) rotate(45)"/>
  </g>"""
    return svg, {"tub": tub, "arc_mid": ((arc0[0] + arc1[0]) / 2 - 6, (arc0[1] + arc1[1]) / 2 + 2), "plane_y": plane_y}


def build() -> str:
    t = c(TARGET)
    inset_svg, pts = inset()
    labels = [
        Label(["Greater tubercle"], anchor=(40, 760), leader=[(250, 712), (t[0] - 10, t[1] + TARGET_R * PX_MM - 6)],
              target_id="target", emphasis=True),
        Label(["Acromion"], anchor=(60, 150), leader=[(200, 168), c((-10, -41))], target_id="acromion"),
        Label(["45°"], anchor=(pts["tub"][0] - 190, pts["plane_y"] - 22), leader=[(pts["tub"][0] - 82, pts["plane_y"] - 36), pts["arc_mid"]],
              target_id="angle-arc"),
        Label(["Anterior plane"], anchor=(1050, 1150), leader=[(1068, 1104), (INSET[0] + 31, pts["plane_y"])], target_id="anterior-plane"),
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
  <path id="shoulder" d="{path(BODY, closed=True, tension=0.5)}" fill="url(#skin-grad)" stroke="#B98A74" stroke-width="3"/>
  <path id="clavicle" d="{path(CLAVICLE, tension=0.8)}" fill="none" stroke="#F0CFBA" stroke-width="22" stroke-linecap="round" opacity="0.7"/>
  {ell("acromion", ACROMION, 'fill="#F0CDB5" stroke="#D2A588" stroke-width="2"')}
  <path id="deltopectoral-groove" d="{path(DELTOPECTORAL, tension=0.8)}" fill="none" stroke="#D2A084" stroke-width="6" opacity="0.8"/>
  <path id="gown" d="{path(GOWN, closed=True, tension=0.5)}" fill="url(#gown-grad)" stroke="#7896B0" stroke-width="3"/>
</g>

<g class="marking">
  <circle id="target" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="{fmt(TARGET_R * PX_MM)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="5"/>
  <circle cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="5" fill="#0E8C98"/>
{inset_svg}
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
