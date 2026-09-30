"""Cricothyrotomy landmarks - anterior (A-P) view, the operator's view.

Patient supine, head at the top of the image. It shows what the operator
palpates and cuts: the thyroid cartilage, the cricothyroid membrane below it,
the cricoid ring below that, the tracheal rings, and the thyroid gland with its
isthmus over the upper rings, clear of the membrane. Incisions: the horizontal
membrane incision (solid) and the vertical midline skin incision for an
impalpable membrane (dashed = skin layer), centred on the membrane and 9 cm
long, inside the record's 8-10 cm.

Style follows clean textbook line art: outlined structures, soft flat fills.
Scale: 9 px per mm, so the drawn sizes are real sizes.

Run: python3 visuals/cric_membrane/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "cric_membrane"
PX_PER_MM = 9.0
CX = 800.0                      # midline

HYOID_Y = 205.0
THYROID_TOP, THYROID_NOTCH, THYROID_BOTTOM = 262.0, 306.0, 482.0
MEMBRANE_TOP, MEMBRANE_BOTTOM = 482.0, 570.0        # about 10 mm
CRICOID_TOP, CRICOID_BOTTOM = 570.0, 626.0          # about 6 mm arch
RING_TOP, RING_H, RING_GAP = 646.0, 34.0, 18.0
MEMBRANE_CENTER_Y = (MEMBRANE_TOP + MEMBRANE_BOTTOM) / 2
SKIN_INCISION_MM = 90.0


def ring_path(y0, y1, half_top, half_bottom, sag=10):
    return (f"M{fmt(CX - half_top)},{fmt(y0)} Q{fmt(CX)},{fmt(y0 + sag)} {fmt(CX + half_top)},{fmt(y0)} "
            f"L{fmt(CX + half_bottom)},{fmt(y1)} Q{fmt(CX)},{fmt(y1 + sag)} {fmt(CX - half_bottom)},{fmt(y1)} Z")


def build() -> str:
    # Neck silhouette: jaw at the top, clavicles and sternal notch at the bottom.
    neck = ("M300,0 C330,120 420,200 470,300 C520,420 520,720 500,860 C480,980 380,1080 180,1140 L0,1160 L0,1200 "
            "L1600,1200 L1600,1160 L1420,1140 C1220,1080 1120,980 1100,860 C1080,720 1080,420 1130,300 "
            "C1180,200 1270,120 1300,0 Z")
    jaw = "M300,0 C420,110 600,150 800,152 C1000,150 1180,110 1300,0"

    thyroid = smooth_path([
        (CX - 190, THYROID_TOP + 8), (CX - 90, THYROID_TOP), (CX - 30, THYROID_TOP + 14), (CX, THYROID_NOTCH),
        (CX + 30, THYROID_TOP + 14), (CX + 90, THYROID_TOP), (CX + 190, THYROID_TOP + 8),
        (CX + 165, 380), (CX + 118, 452), (CX + 70, THYROID_BOTTOM - 4), (CX, THYROID_BOTTOM),
        (CX - 70, THYROID_BOTTOM - 4), (CX - 118, 452), (CX - 165, 380),
    ], closed=True)
    prominence = f"M{fmt(CX)},{fmt(THYROID_NOTCH + 6)} L{fmt(CX)},{fmt(THYROID_BOTTOM - 30)}"

    membrane = (f"M{fmt(CX - 78)},{fmt(MEMBRANE_TOP - 2)} Q{fmt(CX)},{fmt(MEMBRANE_TOP + 4)} {fmt(CX + 78)},{fmt(MEMBRANE_TOP - 2)} "
                f"L{fmt(CX + 118)},{fmt(MEMBRANE_BOTTOM + 2)} Q{fmt(CX)},{fmt(MEMBRANE_BOTTOM - 8)} {fmt(CX - 118)},{fmt(MEMBRANE_BOTTOM + 2)} Z")
    cricoid = ring_path(CRICOID_TOP, CRICOID_BOTTOM, 124, 116, sag=-6)

    rings = []
    y = RING_TOP
    while y < 1060:
        rings.append(ring_path(y, y + RING_H, 104, 104, sag=12))
        y += RING_H + RING_GAP
    ring2_top = RING_TOP + RING_H + RING_GAP
    ring4_bottom = RING_TOP + 3 * (RING_H + RING_GAP) + RING_H

    # Thyroid gland: lobes beside the lower larynx and upper trachea, isthmus
    # across rings 2-4 - below the cricoid, never over the membrane.
    lobe_l = smooth_path([(CX - 128, 560), (CX - 205, 600), (CX - 250, 720), (CX - 232, 860), (CX - 170, 900),
                          (CX - 118, 840), (CX - 104, 700)], closed=True)
    lobe_r = smooth_path([(CX + 128, 560), (CX + 205, 600), (CX + 250, 720), (CX + 232, 860), (CX + 170, 900),
                          (CX + 118, 840), (CX + 104, 700)], closed=True)
    isthmus = smooth_path([(CX - 116, ring2_top + 6), (CX - 40, ring2_top - 4), (CX + 40, ring2_top - 4),
                           (CX + 116, ring2_top + 6), (CX + 122, (ring2_top + ring4_bottom) / 2), (CX + 112, ring4_bottom - 4),
                           (CX + 40, ring4_bottom + 10), (CX - 40, ring4_bottom + 10), (CX - 112, ring4_bottom - 4),
                           (CX - 122, (ring2_top + ring4_bottom) / 2)], closed=True)

    half = SKIN_INCISION_MM * PX_PER_MM / 2
    skin_top, skin_bottom = MEMBRANE_CENTER_Y - half, MEMBRANE_CENTER_Y + half
    membrane_cut_y = MEMBRANE_CENTER_Y + 6

    labels = [
        Label(["Thyroid", "cartilage"], anchor=(60, 330), leader=[(330, 350), (CX - 110, 380)],
              target_id="thyroid-cartilage"),
        Label(["Cricothyroid", "membrane"], anchor=(40, 560), leader=[(420, 545), (CX - 60, 540)],
              target_id="cricothyroid-membrane", emphasis=True),
        Label(["Cricoid", "cartilage"], anchor=(1300, 580), leader=[(1290, 600), (CX + 110, 600)],
              target_id="cricoid-cartilage"),
    ]

    body = f"""
<g id="anatomy">
  <path d="{neck}" fill="#F6E4D8" stroke="#D8B4A0" stroke-width="3"/>
  <path d="{jaw}" fill="#F9ECE3" stroke="#D8B4A0" stroke-width="3"/>
  <path d="M560,1150 Q700,1120 800,1140 Q900,1120 1040,1150" fill="none" stroke="#D8B4A0" stroke-width="3"/>

  <g stroke-linejoin="round">
    <path id="hyoid" d="M{fmt(CX - 150)},{fmt(HYOID_Y - 14)} Q{fmt(CX)},{fmt(HYOID_Y + 10)} {fmt(CX + 150)},{fmt(HYOID_Y - 14)}"
          fill="none" stroke="#E9E0CF" stroke-width="24" stroke-linecap="round"/>
    <path d="M{fmt(CX - 150)},{fmt(HYOID_Y - 14)} Q{fmt(CX)},{fmt(HYOID_Y + 10)} {fmt(CX + 150)},{fmt(HYOID_Y - 14)}"
          fill="none" stroke="#9D907A" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
    <path d="M{fmt(CX - 150)},{fmt(HYOID_Y + 8)} L{fmt(CX + 150)},{fmt(HYOID_Y + 8)} L{fmt(CX + 180)},{fmt(THYROID_TOP + 8)} L{fmt(CX - 180)},{fmt(THYROID_TOP + 8)} Z"
          fill="#E6EEF4" opacity="0.7"/>

    <path id="thyroid-gland-left" d="{lobe_l}" fill="#F2B9A8" fill-opacity="0.8" stroke="#C98774" stroke-width="2.5"/>
    <path id="thyroid-gland-right" d="{lobe_r}" fill="#F2B9A8" fill-opacity="0.8" stroke="#C98774" stroke-width="2.5"/>

    <path id="thyroid-cartilage" d="{thyroid}" fill="#DCE8F1" stroke="#5F7C93" stroke-width="3"/>
    <path d="{prominence}" stroke="#9FB5C6" stroke-width="3"/>
    <path id="cricothyroid-membrane" d="{membrane}" fill="#A9D3EE" stroke="#2F7FB5" stroke-width="3"/>
    <path id="cricoid-cartilage" d="{cricoid}" fill="#DCE8F1" stroke="#5F7C93" stroke-width="3"/>
    <g id="tracheal-rings" fill="#DCE8F1" stroke="#5F7C93" stroke-width="2.5">{"".join(f'<path d="{r}"/>' for r in rings)}</g>
    <path id="thyroid-isthmus" d="{isthmus}" fill="#F2B9A8" fill-opacity="0.85" stroke="#C98774" stroke-width="2.5"/>
  </g>

  <line id="vertical-skin-incision" x1="{fmt(CX)}" y1="{fmt(skin_top)}" x2="{fmt(CX)}" y2="{fmt(skin_bottom)}"
        stroke="#D8432A" stroke-width="6" stroke-dasharray="20 14" stroke-linecap="round" opacity="0.85"/>
  <line id="membrane-incision" x1="{fmt(CX - 62)}" y1="{fmt(membrane_cut_y)}" x2="{fmt(CX + 62)}" y2="{fmt(membrane_cut_y)}"
        stroke="#D8432A" stroke-width="11" stroke-linecap="round"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F7F6F2; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
