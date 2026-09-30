"""Internal jugular landmarks - the sternocleidomastoid triangle, anterior view.

Patient supine, head at the top, turned slightly to the left, so the right
side of the neck faces the viewer (on the image left). The jaw, ear lobe,
chin, thyroid cartilage, sternal notch, clavicles and shoulder are in frame
so the orientation reads at a glance; an earlier head-of-bed version without
them was unreadable (owner, 2026-09-30).

The right SCM runs from the mastoid, behind the ear, down to the sternum and
the medial clavicle. Its sternal and clavicular heads part just above the
clavicle, leaving a small triangle whose base is the clavicle and whose apex
is where the heads meet. The internal jugular vein runs deep to that triangle,
lateral to the carotid; the external jugular crosses the SCM superficially.

Marking (drawn again in code over the painted base): the landmark entry point
at the apex.

Scale: 6 px per mm. Coordinates are millimetres from the sternal notch:
x toward the patient's left (image right), y toward the feet (image down).

Run: python3 visuals/ij_landmark_triangle/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ij_landmark_triangle"
PX_PER_MM = 6.0
NOTCH = (1000.0, 950.0)          # canvas position of the sternal notch
APEX = (-36.0, -38.0)            # where the two heads meet, about 35 mm above the clavicle
ENTRY = (-36.0, -35.0)           # just inside the apex


def c(p):
    return (NOTCH[0] + p[0] * PX_PER_MM, NOTCH[1] + p[1] * PX_PER_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def poly(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in (c(p) for p in points))


def mm(v):
    return v * PX_PER_MM


# Skin outline: lower face, neck and shoulders.
BODY = [(-200, -60), (-160, -40), (-118, -75), (-100, -120), (-92, -170),      # right shoulder, lateral neck
        (140, -170), (140, 60), (-200, 60)]
JAW = [(-66, -170), (-60, -140), (-48, -126), (-10, -118), (25, -116), (55, -122), (80, -138), (100, -170)]
EAR_LOBE = [(-78, -170), (-86, -160), (-84, -150), (-74, -148), (-68, -158)]
THYROID_CARTILAGE = [(-12, -86), (2, -84), (8, -78), (14, -84), (26, -86), (22, -70), (8, -60), (-6, -70)]

# Right SCM, as one outline with the triangle as a notch (no seams).
SCM_OUTLINE = [(-3, 6), (-8, -20), (-20, -60), (-40, -100), (-62, -130), (-80, -152),         # medial (sternal) border up to the mastoid
               (-96, -140), (-86, -110), (-74, -80), (-66, -50), (-64, -20), (-70, -4),       # lateral (clavicular) border down
               (-58, -2), (-46, -3),                                                        # clavicular origin
               (-42, -20), APEX, (-30, -20), (-21, -3),                                     # the triangle
               (-12, 7)]                                                                    # sternal origin
STERNAL_HEAD = [(-3, 6), (-8, -20), (-14, -42), APEX, (-30, -20), (-21, -3), (-12, 7)]
CLAVICULAR_HEAD = [(-46, -3), (-42, -20), APEX, (-50, -44), (-64, -40), (-64, -20), (-70, -4), (-58, -2)]
LEFT_STERNAL_HEAD = [(3, 6), (8, -20), (20, -60), (36, -100), (52, -122), (72, -118), (52, -80), (32, -30), (21, -3), (12, 7)]

IJ = ([(-32, 0), (-35, -20), (-36, -45), (-42, -80), (-50, -110), (-56, -128)], 12)       # ends under the clavicle and the jaw
CAROTID = ([(-14, 0), (-17, -30), (-22, -70), (-30, -105), (-36, -122)], 8)
EXTERNAL_JUGULAR = ([(-56, -130), (-68, -95), (-80, -55), (-90, -12)], 4)
CLAVICLE_R = [(-20, -1), (-45, -6), (-75, -4), (-105, -12), (-140, -26), (-170, -28)]
CLAVICLE_L = [(-x, y) for x, y in CLAVICLE_R]
MANUBRIUM = [(-24, 2), (-10, -2), (0, 1), (10, -2), (24, 2), (26, 60), (-26, 60)]


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9C7B2"/><stop offset="0.55" stop-color="#F7E6DA"/>
  <stop offset="1" stop-color="#EFD5C4"/></linearGradient>
<linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EECDB9"/><stop offset="1" stop-color="#F3DBCB"/></linearGradient>
<linearGradient id="bone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6F0E2"/><stop offset="1" stop-color="#D8CBAE"/></linearGradient>
<filter id="lift" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1800" height="1400"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
"""


def build() -> str:
    entry = c(ENTRY)

    def vessel(element_id, structure, colour, opacity, cap="round"):
        points, width = structure
        return (f'<path id="{element_id}" d="{path(points)}" fill="none" stroke="{colour}" stroke-width="{fmt(mm(width))}" '
                f'stroke-linecap="{cap}" stroke-opacity="{opacity}"/>')

    labels = [
        Label(["Sternal head"], anchor=(1180, 820), leader=[(1175, 800), c((-10, -10))], target_id="sternal-head"),
        Label(["Clavicular head"], anchor=(40, 1150), leader=[(300, 1100), c((-58, -14))], target_id="clavicular-head"),
        Label(["Internal", "jugular vein"], anchor=(1180, 560), leader=[(1175, 572), c((-36, -28))],
              target_id="internal-jugular", emphasis=True),
    ]

    body = f"""
<g id="anatomy">
  <path id="body" d="{path(BODY, closed=True, tension=0.6)}" fill="url(#skin)" stroke="#C9A08A" stroke-width="3" filter="url(#lift)"/>
  <path d="{path([(8, -60), (4, -10)])}" stroke="#E4C6B3" stroke-width="{fmt(mm(20))}" stroke-linecap="round" opacity="0.5"/>
  <path id="thyroid-cartilage" d="{path(THYROID_CARTILAGE, closed=True, tension=0.6)}" fill="#E6C6B2" stroke="#C49580" stroke-width="3"/>

  {vessel("carotid-artery", CAROTID, "#C8322B", 0.6, cap="butt")}
  {vessel("internal-jugular", IJ, "#4F78B8", 0.6, cap="butt")}

  <path d="{path(JAW + [(100, -175), (-66, -175)], closed=True, tension=0.5)}" fill="url(#face)"/>
  <path id="jaw" d="{path(JAW)}" fill="none" stroke="#C49580" stroke-width="5" filter="url(#lift)"/>
  <path id="ear-lobe" d="{path(EAR_LOBE, closed=True, tension=0.8)}" fill="#EBC3AD" stroke="#C49580" stroke-width="3"/>
  <path id="manubrium" d="{path(MANUBRIUM, closed=True, tension=0.4)}" fill="url(#bone)" opacity="0.7" filter="url(#lift)"/>
  <path id="clavicle" d="{path(CLAVICLE_R)}" fill="none" stroke="url(#bone)" stroke-width="{fmt(mm(13))}" stroke-linecap="round" filter="url(#lift)"/>
  <path d="{path(CLAVICLE_L)}" fill="none" stroke="url(#bone)" stroke-width="{fmt(mm(13))}" stroke-linecap="round" filter="url(#lift)"/>

  <path d="{path(LEFT_STERNAL_HEAD, closed=True, tension=0.4)}" fill="#C97A6E" fill-opacity="0.55" stroke="#9C5046" stroke-width="2.5"/>
  <path id="scm" d="{path(SCM_OUTLINE, closed=True, tension=0.35)}" fill="#C97A6E" fill-opacity="0.82"
        stroke="#9C5046" stroke-width="3" stroke-linejoin="round" filter="url(#lift)"/>
  <g fill="#000" fill-opacity="0">
    <polygon id="sternal-head" points="{poly(STERNAL_HEAD)}"/>
    <polygon id="clavicular-head" points="{poly(CLAVICULAR_HEAD)}"/>
  </g>
  {vessel("external-jugular", EXTERNAL_JUGULAR, "#5C84C4", 0.9)}

  <circle id="entry-point" class="marking" cx="{fmt(entry[0])}" cy="{fmt(entry[1])}" r="16"
          fill="#0E8C98" fill-opacity="0.35" stroke="#0E8C98" stroke-width="5"/>
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
