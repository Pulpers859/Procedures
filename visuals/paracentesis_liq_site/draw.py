"""Paracentesis - the left lower quadrant entry site (layout).

A distended (ascitic) abdomen seen from directly above, patient supine,
head at the top, the patient's left on the image right (house laterality):
the umbilicus, both anterior superior iliac spines, the inguinal creases,
drapes over the chest and the pubis.

Record: entry more than two-thirds of the way from the midline to the ASIS;
the inferior epigastric vessels lie about 40% of the way out, medial to it.

Drawn: the line from the umbilicus (on the midline) to the left ASIS, with
ticks at 40% and two-thirds; the inferior epigastric vessels running up and
medially from the mid-inguinal point, crossing the line at 40%; the entry
zone (1.6 cm) at three-quarters of the way out. Standard adult anatomy: the
ASIS about 12.5 cm lateral and 7 cm caudal to the umbilicus.

Painted plate: Gemini centred the abdomen, moving the umbilicus about 14 mm
down and 7 mm right of the layout (commit 681652a); the left ASIS landed
on the layout. Every marking is placed on the umbilicus and left ASIS
traced on the painting (TRACED_U, TRACED_A, canvas px): the line between
them, the 40% and two-thirds ticks, the vessels' crossing at 40% from the
mid-inguinal point (midway from the ASIS to the pubic symphysis), the entry
zone at three-quarters. Scale on the painting: about 4 px/mm (12.5 cm
midline to ASIS).

Millimetres from the umbilicus (x toward the patient's left = image right,
y toward the feet = image down) at 4.5 px/mm.

Run: python3 visuals/paracentesis_liq_site/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "paracentesis_liq_site"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 4.5
ORIGIN = (720.0, 470.0)            # canvas of the umbilicus

ASIS_L = (125.0, 70.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def along(f):
    return (ASIS_L[0] * f, ASIS_L[1] * f)


ABDOMEN = [(-175, -110), (-182, -40), (-180, 20), (-168, 70), (-150, 110), (-120, 140), (-60, 165), (0, 172),
           (60, 165), (120, 140), (150, 110), (168, 70), (180, 20), (182, -40), (175, -110)]
CHEST_DRAPE = [(-200, -120), (200, -120), (200, -88), (100, -82), (0, -80), (-100, -82), (-200, -88)]
PUBIC_DRAPE = [(-200, 200), (-110, 150), (-50, 138), (0, 136), (50, 138), (110, 150), (200, 200)]
CREASE_L = [(ASIS_L[0] + 6, ASIS_L[1] + 10), (100, 112), (70, 135), (40, 150)]
CREASE_R = [(-x, y) for x, y in CREASE_L]
MID_INGUINAL = (66.0, 133.0)
IEA = [MID_INGUINAL, (58.0, 80.0), along(0.40), (46.0, 0.0), (42.0, -60.0)]
TARGET = along(0.75)
TARGET_R = 8.0

TRACED_U = (793.0, 609.0)          # umbilicus on the painting
TRACED_A = (1290.0, 786.0)         # left ASIS on the painting
TRACED_PUBIS = (790.0, 1075.0)     # pubic symphysis at the drape edge
PAINT_PX_MM = (TRACED_A[0] - TRACED_U[0]) / ASIS_L[0]

DEFS = """
<radialGradient id="belly" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#EDC7AE"/><stop offset="1" stop-color="#D4A286"/></radialGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<linearGradient id="drape" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5C8DB5"/><stop offset="1" stop-color="#46779F"/></linearGradient>
"""


def lerp(p, q, f):
    return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)


def build() -> str:
    painted0 = BASE.exists()
    if painted0:
        u, a = TRACED_U, TRACED_A
        mid = lerp(TRACED_A, TRACED_PUBIS, 0.5)
        p40 = lerp(u, a, 0.40)
        iea_pts = [mid, lerp(mid, p40, 0.55), p40, (p40[0] - 24, p40[1] - 140), (p40[0] - 42, p40[1] - 280)]
        r = TARGET_R * PAINT_PX_MM
    else:
        u, a = c((0, 0)), c(ASIS_L)
        iea_pts = [c(q) for q in IEA]
        r = TARGET_R * PX_MM
    t40, t23, t = lerp(u, a, 0.40), lerp(u, a, 2 / 3), lerp(u, a, 0.75)
    nx, ny = -(a[1] - u[1]), a[0] - u[0]
    n = (nx * nx + ny * ny) ** 0.5
    nx, ny = nx / n * 26, ny / n * 26
    iea_mid = iea_pts[1]
    labels = [
        Label(["Umbilicus"], anchor=(330, 560), leader=[(560, 580), (u[0] - 16, u[1])], target_id="mark-umbilicus"),
        Label(["ASIS"], anchor=(1380, 920), leader=[(1390, 880), (a[0] + 10, a[1] + 12)], target_id="mark-asis"),
        Label(["Inferior epigastric", "vessels"], anchor=(140, 1000), leader=[(560, 1020), iea_mid], target_id="iea"),
        Label(["2/3"], anchor=(1070, 560), leader=[(1090, 580), (t23[0] + nx, t23[1] + ny)], target_id="tick-23"),
        Label(["Entry site"], anchor=(1230, 640), leader=[(1250, 655), (t[0] + r * 0.6, t[1] - r * 0.7)], target_id="target", emphasis=True),
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
  <path id="abdomen" d="{path(ABDOMEN, closed=True, tension=0.6)}" fill="url(#belly)" stroke="#B98A74" stroke-width="3"/>
  <path d="{path(CREASE_L, tension=0.8)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  <path d="{path(CREASE_R, tension=0.8)}" fill="none" stroke="#B98A74" stroke-width="5"/>
  <ellipse id="asis-left" cx="{fmt(a[0])}" cy="{fmt(a[1])}" rx="{fmt(9 * PX_MM)}" ry="{fmt(6 * PX_MM)}" fill="#E8BFA4" stroke="#C49478" stroke-width="3"/>
  <ellipse cx="{fmt(c((-ASIS_L[0], ASIS_L[1]))[0])}" cy="{fmt(a[1])}" rx="{fmt(9 * PX_MM)}" ry="{fmt(6 * PX_MM)}" fill="#E8BFA4" stroke="#C49478" stroke-width="3"/>
  <ellipse id="umbilicus" cx="{fmt(u[0])}" cy="{fmt(u[1])}" rx="{fmt(5 * PX_MM)}" ry="{fmt(6 * PX_MM)}" fill="#A9765F" stroke="#8C5F4B" stroke-width="3"/>
  <path d="{path(CHEST_DRAPE, closed=True, tension=0.3)}" fill="url(#drape)"/>
  <path d="{path(PUBIC_DRAPE, tension=0.6)} L{fmt(c((200, 260))[0])},1200 L{fmt(c((-200, 260))[0])},1200 Z" fill="url(#drape)"/>
</g>

<g class="marking">
  <circle id="mark-umbilicus" cx="{fmt(u[0])}" cy="{fmt(u[1])}" r="18" fill="#000" opacity="0"/>
  <circle id="mark-asis" cx="{fmt(a[0])}" cy="{fmt(a[1])}" r="22" fill="none" stroke="#4A2F7A" stroke-width="5"/>
  <line id="spino-umbilical" x1="{fmt(u[0])}" y1="{fmt(u[1])}" x2="{fmt(a[0])}" y2="{fmt(a[1])}" stroke="#4A2F7A" stroke-width="5" stroke-dasharray="20 12"/>
  <path id="iea" d="{smooth_path(iea_pts, tension=0.7)}" fill="none" stroke="#C8322B" stroke-width="8" stroke-dasharray="18 10" stroke-linecap="round"/>
  <line id="tick-40" x1="{fmt(t40[0] - nx)}" y1="{fmt(t40[1] - ny)}" x2="{fmt(t40[0] + nx)}" y2="{fmt(t40[1] + ny)}" stroke="#4A2F7A" stroke-width="6"/>
  <line id="tick-23" x1="{fmt(t23[0] - nx)}" y1="{fmt(t23[1] - ny)}" x2="{fmt(t23[0] + nx)}" y2="{fmt(t23[1] + ny)}" stroke="#4A2F7A" stroke-width="6"/>
  <circle id="target" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="{fmt(r)}" fill="#6CCBD2" fill-opacity="0.55" stroke="#0E8C98" stroke-width="5"/>
  <circle cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="5" fill="#0E8C98"/>
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
