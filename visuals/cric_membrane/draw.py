"""Cricothyrotomy landmarks - anterior (A-P) view, the operator's view.

Patient supine, head at the top of the image. It shows what the operator
palpates and cuts: the thyroid cartilage, the cricothyroid membrane below it,
the cricoid ring below that, the tracheal rings, and the thyroid gland with its
isthmus over the upper rings, clear of the membrane. Incisions: the horizontal
membrane incision (solid) and the vertical midline skin incision (dashed = skin
layer), 4 cm, beginning over the thyroid cartilage and running distally - the
owner's specification (2026-09-30), 3-5 cm.

Scale: 9 px per mm in anatomy coordinates. The anatomy is zoomed by VIEW_SCALE
so the larynx fills the card; labels are unscaled and their leaders are mapped
through view().

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

SKIN_INCISION_START_Y = 390.0   # over the lower thyroid cartilage
SKIN_INCISION_MM = 40.0         # owner: 3-5 cm, starting over the thyroid cartilage, going distal

# Zoom so the hyoid-to-ring-7 region fills the 1600 x 1200 card.
VIEW_SCALE = 1.34
VIEW_SHIFT = (-272.0, -170.0)


def view(p):
    return (p[0] * VIEW_SCALE + VIEW_SHIFT[0], p[1] * VIEW_SCALE + VIEW_SHIFT[1])


def ring_path(y0, y1, half_top, half_bottom, sag=10):
    return (f"M{fmt(CX - half_top)},{fmt(y0)} Q{fmt(CX)},{fmt(y0 + sag)} {fmt(CX + half_top)},{fmt(y0)} "
            f"L{fmt(CX + half_bottom)},{fmt(y1)} Q{fmt(CX)},{fmt(y1 + sag)} {fmt(CX - half_bottom)},{fmt(y1)} Z")


DEFS = """
<linearGradient id="skinSide" x1="0" x2="1"><stop offset="0" stop-color="#E9C8B4"/><stop offset="0.28" stop-color="#F6E3D6"/>
  <stop offset="0.5" stop-color="#F9EADF"/><stop offset="0.72" stop-color="#F6E3D6"/><stop offset="1" stop-color="#E9C8B4"/></linearGradient>
<linearGradient id="cartilage" x1="0" x2="1"><stop offset="0" stop-color="#B9CCDB"/><stop offset="0.5" stop-color="#EEF4F8"/><stop offset="1" stop-color="#B9CCDB"/></linearGradient>
<linearGradient id="lamina" x1="0" x2="1"><stop offset="0" stop-color="#A9C0D2"/><stop offset="0.42" stop-color="#E6EEF4"/>
  <stop offset="0.5" stop-color="#F4F8FB"/><stop offset="0.58" stop-color="#E6EEF4"/><stop offset="1" stop-color="#A9C0D2"/></linearGradient>
<linearGradient id="ringShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#B7CADA"/></linearGradient>
<linearGradient id="tube" x1="0" x2="1"><stop offset="0" stop-color="#C98E8A"/><stop offset="0.5" stop-color="#EBC1BB"/><stop offset="1" stop-color="#C98E8A"/></linearGradient>
<radialGradient id="membraneShade" cx="0.5" cy="0.5" r="0.7"><stop offset="0" stop-color="#BFE0F4"/><stop offset="1" stop-color="#6FB0DC"/></radialGradient>
<radialGradient id="gland" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#F6C9BC"/><stop offset="1" stop-color="#DB9585"/></radialGradient>
<pattern id="lobules" width="18" height="18" patternUnits="userSpaceOnUse">
  <circle cx="5" cy="6" r="2.2" fill="#C87C6B" opacity="0.35"/><circle cx="13" cy="14" r="1.8" fill="#C87C6B" opacity="0.3"/></pattern>
<filter id="lift" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
"""


def build() -> str:
    neck = ("M300,0 C330,120 420,200 470,300 C520,420 520,720 500,860 C480,980 380,1080 180,1140 L0,1160 L0,1200 "
            "L1600,1200 L1600,1160 L1420,1140 C1220,1080 1120,980 1100,860 C1080,720 1080,420 1130,300 "
            "C1180,200 1270,120 1300,0 Z")
    jaw = "M300,0 C420,110 600,150 800,152 C1000,150 1180,110 1300,0"
    # Sternocleidomastoid contours: faint depth cues from behind the ear to the sternal notch.
    scm_l = "M470,160 C560,420 680,760 760,1080"
    scm_r = "M1130,160 C1040,420 920,760 840,1080"

    thyroid = smooth_path([
        (CX - 190, THYROID_TOP + 8), (CX - 90, THYROID_TOP), (CX - 30, THYROID_TOP + 14), (CX, THYROID_NOTCH),
        (CX + 30, THYROID_TOP + 14), (CX + 90, THYROID_TOP), (CX + 190, THYROID_TOP + 8),
        (CX + 165, 380), (CX + 118, 452), (CX + 70, THYROID_BOTTOM - 4), (CX, THYROID_BOTTOM),
        (CX - 70, THYROID_BOTTOM - 4), (CX - 118, 452), (CX - 165, 380),
    ], closed=True)
    horns = (f"M{fmt(CX - 182)},{fmt(THYROID_TOP + 10)} L{fmt(CX - 196)},{fmt(HYOID_Y + 16)} "
             f"M{fmt(CX + 182)},{fmt(THYROID_TOP + 10)} L{fmt(CX + 196)},{fmt(HYOID_Y + 16)}")
    oblique = (f"M{fmt(CX - 160)},{fmt(THYROID_TOP + 40)} C{fmt(CX - 150)},340 {fmt(CX - 128)},400 {fmt(CX - 100)},{fmt(THYROID_BOTTOM - 20)} "
               f"M{fmt(CX + 160)},{fmt(THYROID_TOP + 40)} C{fmt(CX + 150)},340 {fmt(CX + 128)},400 {fmt(CX + 100)},{fmt(THYROID_BOTTOM - 20)}")
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
    trachea = f"M{fmt(CX - 100)},{fmt(CRICOID_BOTTOM - 4)} L{fmt(CX + 100)},{fmt(CRICOID_BOTTOM - 4)} L{fmt(CX + 100)},1100 L{fmt(CX - 100)},1100 Z"

    lobe_l = smooth_path([(CX - 128, 560), (CX - 205, 600), (CX - 250, 720), (CX - 232, 860), (CX - 170, 900),
                          (CX - 118, 840), (CX - 104, 700)], closed=True)
    lobe_r = smooth_path([(CX + 128, 560), (CX + 205, 600), (CX + 250, 720), (CX + 232, 860), (CX + 170, 900),
                          (CX + 118, 840), (CX + 104, 700)], closed=True)
    isthmus = smooth_path([(CX - 116, ring2_top + 6), (CX - 40, ring2_top - 4), (CX + 40, ring2_top - 4),
                           (CX + 116, ring2_top + 6), (CX + 122, (ring2_top + ring4_bottom) / 2), (CX + 112, ring4_bottom - 4),
                           (CX + 40, ring4_bottom + 10), (CX - 40, ring4_bottom + 10), (CX - 112, ring4_bottom - 4),
                           (CX - 122, (ring2_top + ring4_bottom) / 2)], closed=True)

    skin_top = SKIN_INCISION_START_Y
    skin_bottom = SKIN_INCISION_START_Y + SKIN_INCISION_MM * PX_PER_MM
    membrane_cut_y = MEMBRANE_CENTER_Y + 6

    labels = [
        Label(["Thyroid", "cartilage"], anchor=(48, 250), leader=[(300, 290), view((CX - 128, 360))],
              target_id="thyroid-cartilage"),
        Label(["Cricothyroid", "membrane"], anchor=(36, 560), leader=[(410, 548), view((CX - 64, 540))],
              target_id="cricothyroid-membrane", emphasis=True),
        Label(["Cricoid", "cartilage"], anchor=(1300, 560), leader=[(1290, 588), view((CX + 112, 600))],
              target_id="cricoid-cartilage"),
    ]

    body = f"""
<g id="anatomy" transform="translate({fmt(VIEW_SHIFT[0])} {fmt(VIEW_SHIFT[1])}) scale({VIEW_SCALE})">
  <path d="{neck}" fill="url(#skinSide)" stroke="#D2A994" stroke-width="3"/>
  <path d="{jaw}" fill="none" stroke="#D2A994" stroke-width="3"/>
  <path d="{scm_l}" fill="none" stroke="#DDB6A2" stroke-width="10" stroke-linecap="round" opacity="0.45"/>
  <path d="{scm_r}" fill="none" stroke="#DDB6A2" stroke-width="10" stroke-linecap="round" opacity="0.45"/>

  <g stroke-linejoin="round">
    <path d="M{fmt(CX - 150)},{fmt(HYOID_Y + 8)} L{fmt(CX + 150)},{fmt(HYOID_Y + 8)} L{fmt(CX + 184)},{fmt(THYROID_TOP + 8)} L{fmt(CX - 184)},{fmt(THYROID_TOP + 8)} Z"
          fill="#E3EAF0" opacity="0.8"/>
    <path id="hyoid" d="M{fmt(CX - 150)},{fmt(HYOID_Y - 14)} Q{fmt(CX)},{fmt(HYOID_Y + 10)} {fmt(CX + 150)},{fmt(HYOID_Y - 14)}"
          fill="none" stroke="#EDE3CF" stroke-width="26" stroke-linecap="round" filter="url(#lift)"/>
    <path d="M{fmt(CX - 150)},{fmt(HYOID_Y - 14)} Q{fmt(CX)},{fmt(HYOID_Y + 10)} {fmt(CX + 150)},{fmt(HYOID_Y - 14)}"
          fill="none" stroke="#A89776" stroke-width="2.5" stroke-linecap="round" opacity="0.55"/>

    <path d="{trachea}" fill="url(#tube)" filter="url(#lift)"/>
    <path id="thyroid-gland-left" d="{lobe_l}" fill="url(#gland)" stroke="#C07A69" stroke-width="2.5" filter="url(#lift)"/>
    <path d="{lobe_l}" fill="url(#lobules)"/>
    <path id="thyroid-gland-right" d="{lobe_r}" fill="url(#gland)" stroke="#C07A69" stroke-width="2.5" filter="url(#lift)"/>
    <path d="{lobe_r}" fill="url(#lobules)"/>

    <path d="{horns}" stroke="#8FA9BD" stroke-width="12" stroke-linecap="round"/>
    <path id="thyroid-cartilage" d="{thyroid}" fill="url(#lamina)" stroke="#557389" stroke-width="3" filter="url(#lift)"/>
    <path d="{oblique}" fill="none" stroke="#8FA9BD" stroke-width="2.5" opacity="0.7"/>
    <path d="{prominence}" stroke="#A3B8C8" stroke-width="3"/>
    <path id="cricothyroid-membrane" d="{membrane}" fill="url(#membraneShade)" stroke="#2F7FB5" stroke-width="3"/>
    <path id="cricoid-cartilage" d="{cricoid}" fill="url(#ringShade)" stroke="#557389" stroke-width="3" filter="url(#lift)"/>
    <g id="tracheal-rings" fill="url(#ringShade)" stroke="#6A8599" stroke-width="2.5">{"".join(f'<path d="{r}"/>' for r in rings)}</g>
    <path id="thyroid-isthmus" d="{isthmus}" fill="url(#gland)" fill-opacity="0.9" stroke="#C07A69" stroke-width="2.5"/>
    <path d="{isthmus}" fill="url(#lobules)"/>
  </g>

  <line id="vertical-skin-incision" x1="{fmt(CX)}" y1="{fmt(skin_top)}" x2="{fmt(CX)}" y2="{fmt(skin_bottom)}"
        stroke="#D8432A" stroke-width="6" stroke-dasharray="20 14" stroke-linecap="round" opacity="0.9"/>
  <line id="membrane-incision" x1="{fmt(CX - 62)}" y1="{fmt(membrane_cut_y)}" x2="{fmt(CX + 62)}" y2="{fmt(membrane_cut_y)}"
        stroke="#D8432A" stroke-width="11" stroke-linecap="round"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F7F6F2; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
