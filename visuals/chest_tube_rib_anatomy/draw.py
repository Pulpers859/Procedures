"""Thoracostomy - over-the-rib insertion: one intercostal space in section (layout).

Coronal section through the lateral chest wall at the mid-axillary line,
head at the top: skin on the image left, the pleural cavity and lung on the
right, two ribs (above and below the space) cut across. The same way round
as the needle decompression inset (skin left, pleura right, head up).

Record: the intercostal neurovascular bundle (vein, artery, nerve) runs
along the inferior margin of each rib; always pass the tube over the
superior border of the lower rib; incise parallel to the rib; bluntly
dissect with a Kelly over the rib into the pleural space; finger sweep;
advance the tube.

Standard anatomy added: skin, subcutaneous fat and serratus anterior over
the ribs at the mid-axillary line; external, internal and innermost
intercostal muscles; the bundle in the costal groove between the internal
and innermost layers, vein highest and nerve lowest; endothoracic fascia
and parietal pleura; the pleural space shown opened (air or fluid) with the
lung behind it. A 24 Fr tube (about 8 mm) to scale.

Millimetres from the skin at the middle of the space (x deep = image right,
y caudal = image down) at 20 px/mm.

Run: python3 visuals/chest_tube_rib_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "chest_tube_rib_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 20.0
ORIGIN = (110.0, 600.0)
T, B = -33.0, 33.0                       # band ends, past the frame
SKIN, FAT, SERRATUS = 2.0, 10.0, 16.0    # outer surface of the next layer
EXT, INT, INNER0, INNER1 = 16.4, 21.2, 26.9, 29.4
PLEURA, LUNG = 30.0, 40.0
F = 0.18                                 # half-thickness of a fascial line (7 px)
UPPER_RIB = ((22.3, -15.0), 4.3, 6.5)
LOWER_RIB = ((22.3, 15.0), 4.3, 6.5)
TUBE_Y, TUBE_R = 3.6, 3.6
TUBE_TIP = 37.0


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def vband(x0, x1, n=30):
    ys = [T + (B - T) * i / n for i in range(n + 1)]
    return [(x0, y) for y in ys] + [(x1, y) for y in reversed(ys)]


def bundle(rib_y_bottom):
    """Vein, artery, nerve from the top down, in the groove under a rib."""
    return [((26.6, rib_y_bottom - 1.0), 1.15, "vein"), ((26.6, rib_y_bottom + 1.1), 0.9, "artery"),
            ((26.5, rib_y_bottom + 2.9), 0.85, "nerve")]


UPPER_BUNDLE = bundle(UPPER_RIB[0][1] + UPPER_RIB[2])
LOWER_BUNDLE = bundle(LOWER_RIB[0][1] + LOWER_RIB[2])
COLOURS = {"vein": ('#3E5C9A', '#2C4475'), "artery": ('#C8463C', '#8E2A23'), "nerve": ('#EFCB5A', '#B8962E')}

DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A63F37"/><stop offset="1" stop-color="#7A2621"/></linearGradient>
<linearGradient id="lung-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9A9A4"/><stop offset="1" stop-color="#D88E8A"/></linearGradient>
<linearGradient id="tube-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F7F9"/><stop offset="0.5" stop-color="#DCE3E8"/><stop offset="1" stop-color="#B9C3CB"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    ry = e[2] if len(e) > 2 else e[1]
    return f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


def bundle_svg(parts, suffix, group_id):
    out = []
    for centre, r, kind in parts:
        fill, stroke = COLOURS[kind]
        out.append(ell(f"{kind}{suffix}", (centre, r), f'fill="{fill}" stroke="{stroke}" stroke-width="3"'))
    xs = [p[0][0] for p in parts]
    ys = [p[0][1] for p in parts]
    box = ((min(xs) - 1.6, min(ys) - 1.6), (max(xs) + 1.6, max(ys) + 1.4))
    p0, p1 = c(box[0]), c(box[1])
    envelope = (f'<rect id="{group_id}" x="{fmt(p0[0])}" y="{fmt(p0[1])}" width="{fmt(p1[0] - p0[0])}" '
                f'height="{fmt(p1[1] - p0[1])}" rx="24" fill="#F3E4C2" stroke="#F8F6F0" stroke-width="7"/>')
    return envelope + "".join(out)


def build() -> str:
    tube_x0 = -12.0
    t0, t1 = c((tube_x0, TUBE_Y - TUBE_R)), c((TUBE_TIP, TUBE_Y + TUBE_R))
    W = 'fill="#F8F6F0"'
    M = 'fill="url(#muscle)"'
    upper_rib, lower_rib = c(UPPER_RIB[0]), c(LOWER_RIB[0])
    ub = c(UPPER_BUNDLE[1][0])
    labels = [
        Label(["Rib"], anchor=(1000, 250), leader=[(990, 236), (upper_rib[0] + 30, upper_rib[1] - 40)], target_id="upper-rib"),
        Label(["Vein, artery, nerve"], anchor=(1000, 420), leader=[(990, 404), (ub[0] + 10, ub[1])], target_id="upper-bundle", emphasis=True),
        Label(["Lower rib"], anchor=(1000, 1000), leader=[(990, 984), (lower_rib[0] + 30, lower_rib[1] + 40)], target_id="lower-rib"),
        Label(["Chest tube"], anchor=(1100, 760), leader=[(1090, 744), (c((TUBE_TIP - 3, 0))[0], c((0, TUBE_Y + 1))[1])], target_id="tube"),
        Label(["Parietal pleura"], anchor=(1060, 130), leader=[(1050, 114), (c((PLEURA, 0))[0], 114)], target_id="pleura"),
        Label(["Lung"], anchor=(1380, 560), leader=[(1370, 544), (1330, 544)], target_id="lung"),
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
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(vband(0, SKIN), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(vband(SKIN, FAT - F), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="serratus" d="{path(vband(FAT + F, SERRATUS - F), closed=True, tension=0.2)}" {M}/>
  <path id="external-ic" d="{path(vband(EXT, INT - F), closed=True, tension=0.2)}" {M}/>
  <path id="internal-ic" d="{path(vband(INT + F, INNER0 - F), closed=True, tension=0.2)}" {M}/>
  <path id="innermost-ic" d="{path(vband(INNER0 + F, INNER1), closed=True, tension=0.2)}" {M}/>
  <path id="endothoracic" d="{path(vband(INNER1, PLEURA - F), closed=True, tension=0.2)}" fill="#F3E4C2"/>
  <path id="pleural-space" d="{path(vband(PLEURA + F, LUNG - F), closed=True, tension=0.2)}" fill="#E4E9EC"/>
  <path id="lung" d="{path(vband(LUNG + F, 80), closed=True, tension=0.2)}" fill="url(#lung-grad)"/>
  <path id="fascia-1" d="{path(vband(FAT - F, FAT + F), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-2" d="{path(vband(SERRATUS - F, EXT), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-3" d="{path(vband(INT - F, INT + F), closed=True, tension=0.2)}" {W}/>
  <path id="fascia-4" d="{path(vband(INNER0 - F, INNER0 + F), closed=True, tension=0.2)}" {W}/>
  <path id="pleura" d="{path(vband(PLEURA - F, PLEURA + F), closed=True, tension=0.2)}" {W}/>
  <path id="visceral-pleura" d="{path(vband(LUNG - F, LUNG + F), closed=True, tension=0.2)}" {W}/>
  {ell("upper-rib", UPPER_RIB, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="10"')}
  {ell("lower-rib", LOWER_RIB, 'fill="#EFE6D2" stroke="#A8977A" stroke-width="10"')}
  {bundle_svg(UPPER_BUNDLE, "", "upper-bundle")}
  {bundle_svg(LOWER_BUNDLE, "-low", "lower-bundle")}
  <line x1="{fmt(ORIGIN[0])}" y1="0" x2="{fmt(ORIGIN[0])}" y2="1200" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <rect id="tube" x="{fmt(t0[0])}" y="{fmt(t0[1])}" width="{fmt(t1[0] - t0[0])}" height="{fmt(t1[1] - t0[1])}" rx="{fmt(TUBE_R * PX_MM)}"
        fill="url(#tube-grad)" fill-opacity="0.92" stroke="#7D868F" stroke-width="3"/>
  <line x1="{fmt(t0[0])}" y1="{fmt(c((0, TUBE_Y + 1.2))[1])}" x2="{fmt(t1[0] - 40)}" y2="{fmt(c((0, TUBE_Y + 1.2))[1])}" stroke="#5E6670" stroke-width="5" stroke-dasharray="26 14"/>
  <circle id="tube-tip" cx="{fmt(t1[0] - 20)}" cy="{fmt(c((0, TUBE_Y))[1])}" r="4" fill="#000" opacity="0"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
