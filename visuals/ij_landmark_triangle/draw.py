"""Internal jugular landmarks - the sternocleidomastoid triangle, anterior view.

Right neck, patient supine. The sternal and clavicular heads of the SCM rise
from the manubrium and the medial clavicle and join at the apex of a small
triangle whose base is the clavicle. The internal jugular vein runs deep to
that triangle, lateral to the carotid, which lies deep to the sternal head.
The external jugular is superficial and crosses the SCM belly obliquely.

Orientation: the operator stands at the head of the bed for an IJ line, so
the default is that view - the anatomy rotated 180 degrees, head at the bottom,
the patient's right on the image right. ORIENT=head-top renders the atlas
orientation (head at the top) instead, for the owner to choose between.

Marking (drawn again in code over the painted base): the landmark entry point
at the apex, where the two heads meet.

Scale: 12 px per mm in anatomy coordinates. Structure positions are drawn in
the atlas orientation and rotated by view().

Run: python3 visuals/ij_landmark_triangle/draw.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ij_landmark_triangle"
PX_PER_MM = 12.0
CX = 1250.0                      # midline; the patient's right neck is to the image left before rotation
APEX = (860.0, 530.0)            # where the two heads meet, about 35 mm above the clavicle
ENTRY = (860.0, 552.0)           # just inside the apex
HEAD_AT_BOTTOM = os.environ.get("ORIENT") != "head-top"


def view(p):
    """Atlas coordinates to canvas coordinates."""
    return (WIDTH - p[0], HEIGHT - p[1]) if HEAD_AT_BOTTOM else p


def mirror(points):
    return [(2 * CX - x, y) for x, y in points]


# Atlas orientation (head at the top), patient's right neck on the image left.
# Frame: clavicle near the bottom, about 8 cm of neck above it.
STERNAL_HEAD = [(1165, 1055), (1080, 1072), (990, 958), (925, 745), APEX, (1040, 560), (1110, 800)]
CLAVICULAR_HEAD = [(770, 952), (815, 740), APEX, (700, 500), (560, 520), (520, 740), (490, 948)]
SCM_BELLY = [APEX, (1040, 560), (960, 350), (860, 130), (790, -40), (420, -40), (470, 200), (530, 380), (560, 520)]
# The whole muscle as one outline with the triangle as a notch, so no seams show.
SCM_OUTLINE = [(1165, 1055), (1110, 800), (1040, 560), (960, 350), (860, 130), (790, -40), (420, -40),
               (470, 200), (530, 380), (560, 520), (520, 740), (490, 948), (630, 962), (770, 952),
               (815, 740), APEX, (925, 745), (990, 958), (1080, 1072)]
IJ = [(876, 1000), (880, 950), (865, 740), (850, 530), (820, 250), (780, -40)]
CAROTID = [(1030, 1000), (1000, 800), (965, 530), (935, 250), (905, -40)]
EXTERNAL_JUGULAR = [(650, -40), (560, 250), (450, 560), (330, 820), (250, 960)]
CLAVICLE = [(1010, 1012), (800, 986), (500, 1000), (200, 1040), (-60, 1030)]
LEFT_CLAVICLE = mirror([(1010, 1012), (800, 986), (560, 996)])
LEFT_STERNAL_HEAD = mirror([(1165, 1055), (1080, 1072), (990, 958), (925, 745), (880, 560), (1040, 560), (1110, 800)])
MANUBRIUM = [(1030, 1030), (1140, 1040), (1250, 1062), (1360, 1040), (1470, 1030), (1470, 1260), (1030, 1260)]
TRAPEZIUS = [(100, -40), (60, 400), (-60, 800)]
THYROID_CARTILAGE = [(1120, 110), (1235, 118), (1250, 150), (1265, 118), (1380, 110), (1340, 230), (1250, 290), (1160, 230)]


def vpoly(points):
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in (view(p) for p in points))


def vpath(points, closed=False, tension=1.0):
    return smooth_path([view(p) for p in points], closed=closed, tension=tension)


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#EBCBB7"/><stop offset="0.5" stop-color="#F7E6DA"/>
  <stop offset="1" stop-color="#F2DACB"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D98F83"/><stop offset="1" stop-color="#B7675C"/></linearGradient>
<linearGradient id="bone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6F0E2"/><stop offset="1" stop-color="#D8CBAE"/></linearGradient>
<filter id="lift" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
"""


def build() -> str:
    entry = view(ENTRY)

    if HEAD_AT_BOTTOM:
        labels = [
            Label(["Sternal head"], anchor=(40, 620), leader=[(330, 556), view((1080, 820))], target_id="sternal-head"),
            Label(["Clavicular", "head"], anchor=(1230, 560), leader=[(1240, 572), view((660, 760))], target_id="clavicular-head"),
            Label(["Internal jugular vein"], anchor=(560, 110), leader=[(760, 130), view((880, 880))],
                  target_id="internal-jugular", emphasis=True),
        ]
    else:
        labels = [
            Label(["Sternal head"], anchor=(1200, 620), leader=[(1250, 640), (1080, 820)], target_id="sternal-head"),
            Label(["Clavicular", "head"], anchor=(40, 560), leader=[(300, 572), (660, 760)], target_id="clavicular-head"),
            Label(["Internal jugular vein"], anchor=(480, 1150), leader=[(720, 1105), (880, 880)],
                  target_id="internal-jugular", emphasis=True),
        ]

    def stroke(points, width, colour, extra="", cap="round"):
        return (f'<path d="{vpath(points)}" fill="none" stroke="{colour}" stroke-width="{width}" '
                f'stroke-linecap="{cap}" {extra}/>')

    body = f"""
<g id="anatomy">
  <rect id="neck" x="-10" y="-10" width="1620" height="1220" fill="url(#skin)"/>
  <path d="{vpath(TRAPEZIUS)}" fill="none" stroke="#D2AA94" stroke-width="4"/>
  <path d="{vpath([(1250, 380), (1250, 1000)])}" stroke="#E4C6B3" stroke-width="230" stroke-linecap="round" opacity="0.45"/>
  <path d="{vpath(THYROID_CARTILAGE, closed=True, tension=0.6)}" fill="#E8CBB8" stroke="#CFA58F" stroke-width="3" opacity="0.5"/>

  {stroke(CAROTID, 84, "#C8322B", 'id="carotid-artery" stroke-opacity="0.65"', cap="butt")}
  {stroke(IJ, 144, "#4F78B8", 'id="internal-jugular" stroke-opacity="0.6"', cap="butt")}

  <path id="manubrium" d="{vpath(MANUBRIUM, closed=True, tension=0.4)}" fill="url(#bone)" filter="url(#lift)"/>
  <path id="clavicle" d="{vpath(CLAVICLE)}" fill="none" stroke="url(#bone)" stroke-width="140" stroke-linecap="round" filter="url(#lift)"/>
  <path d="{vpath(LEFT_CLAVICLE)}" fill="none" stroke="url(#bone)" stroke-width="140" stroke-linecap="round" filter="url(#lift)"/>

  <path id="scm" d="{vpath(SCM_OUTLINE, closed=True, tension=0.35)}" fill="#C97A6E" fill-opacity="0.84"
        stroke="#9C5046" stroke-width="3" stroke-linejoin="round" filter="url(#lift)"/>
  <g fill="#000" fill-opacity="0">
    <polygon id="sternal-head" points="{vpoly(STERNAL_HEAD)}"/>
    <polygon id="clavicular-head" points="{vpoly(CLAVICULAR_HEAD)}"/>
    <polygon id="scm-belly" points="{vpoly(SCM_BELLY)}"/>
  </g>
  <path d="{vpath(LEFT_STERNAL_HEAD, closed=True, tension=0.4)}" fill="#C97A6E" fill-opacity="0.8" stroke="#9C5046" stroke-width="3" filter="url(#lift)"/>
  {stroke(EXTERNAL_JUGULAR, 26, "#5C84C4", 'id="external-jugular" opacity="0.9"')}

  <circle id="entry-point" class="marking" cx="{fmt(entry[0])}" cy="{fmt(entry[1])}" r="20"
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
