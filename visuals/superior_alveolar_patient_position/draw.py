"""Superior alveolar (supraperiosteal) block - needle entry on the patient (layout).

A close-up of the lower face from the front, seated patient, head at the top:
the base of the nose, the mouth open, the upper teeth, the chin at the bottom;
the patient's right on the image left (house laterality). The operator's
gloved index finger comes in from the patient's right and lifts the right
upper lip, opening the mucobuccal fold above the right canine. The syringe
comes up from below, in front of the teeth, the needle entering the fold
above the canine and pointing up along the tooth toward its root apex. The
same composition family as the approved infraorbital and mental plates.

Record: seated, head resting firmly; identify the tooth; retract the upper
lip; insert at the height of the mucobuccal fold, angled toward the apex of
the tooth; advance a few millimetres until near bone; 1-2 mL. The tooth is
the right maxillary canine (default; the record says the painful tooth).

Standard anatomy added: adult tooth widths seen from the front; the canine
root about 17 mm long, its apex above the fold; the fold about 11 mm above
the gingival margin.

Code-drawn over the painting: the canine root as a dashed translucent outline
with its apex, the entry point at the fold, the needle and syringe (the
needle's path under the mucosa dashed to just short of the apex).

Millimetres from the midline at the upper central incisors' edges (x toward
the patient's left = image right, y down) at 12 px/mm.

Run: python3 visuals/superior_alveolar_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import SYRINGE_DEFS, Label, document, fmt, smooth_path, syringe  # noqa: E402

ASSET_ID = "superior_alveolar_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 12.0
ORIGIN = (800.0, 640.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


# Upper teeth, patient's right (negative x) to left: (x0, x1, gingival margin y, edge y).
RIGHT = [(-32.0, -27.0, -8.0, -1.0), (-27.0, -21.5, -8.6, -1.0), (-21.5, -15.0, -11.0, 0.6), (-15.0, -8.5, -9.0, -1.0),
         (-8.5, 0.0, -10.5, 0.0)]
TEETH = RIGHT + [(-x1, -x0, gm, e) for x0, x1, gm, e in reversed(RIGHT)]
CANINE = RIGHT[2]
CANINE_AXIS_X = (CANINE[0] + CANINE[1]) / 2
APEX = (CANINE_AXIS_X - 0.8, -28.0)
FOLD_Y = -23.6
FOLD = [(-34, -26.0), (-26, -25.0), (-18, -23.6), (-11, -20.6), (-5, -15.0)]
ENTRY = (CANINE_AXIS_X, FOLD_Y + 0.4)
TIP = (APEX[0] + 0.3, APEX[1] + 3.0)
HUB = (CANINE_AXIS_X + 1.4, -6.0)
NOSE = [(-12, -62), (-14, -54), (-21, -50), (-20, -44), (-15, -39.5), (-6, -39.5), (0, -38), (6, -39.5), (15, -39.5), (20, -44), (21, -50), (14, -54), (12, -62)]
MOUTH = ((2.0, 8.0), 34.0, 15.0)
UPPER_LIP = [(40, -6), (20, -9.6), (0, -10.6), (-6, -14), (-10, -19.6), (-20, -25.6), (-38, -27.4), (-38, -36.5), (-20, -35.4), (-8, -30), (0, -21), (20, -17.5), (42, -12)]
GUM = [(-37, -27.0), (-20, -25.2), (-10, -19.2), (-5.6, -13.6), (0, -10.4), (38, -6.4), (36, -5), (0, -8.0), (-36, -6.0)]
FINGER = [(-70, -41), (-46, -41), (-38.5, -38.5), (-35, -33), (-38, -27.8), (-46, -26.2), (-70, -26.2)]
DEFS = SYRINGE_DEFS + """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.5" stop-color="#EBC3AA"/>
  <stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="glove" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F2EC"/><stop offset="1" stop-color="#DCD8CE"/></linearGradient>
<linearGradient id="enamel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5F1E6"/><stop offset="1" stop-color="#E7E0CC"/></linearGradient>
"""


def tooth(x0, x1, gm, e, el_id=""):
    pts = [(x0 + 0.3, gm), (x1 - 0.3, gm), (x1, (gm + e) / 2), (x1 - 0.8, e), ((x0 + x1) / 2, e + 0.3), (x0 + 0.8, e), (x0, (gm + e) / 2)]
    id_attr = f' id="{el_id}"' if el_id else ""
    return f'<path{id_attr} d="{path(pts, closed=True, tension=0.4)}" fill="url(#enamel)" stroke="#BDB49E" stroke-width="3"/>'


def build() -> str:
    teeth = "".join(tooth(*t, el_id="canine" if t == CANINE else "") for t in TEETH)
    lower = "".join(tooth(x0, x1, 22.0, 14.0) for x0, x1, _, _ in TEETH[2:-2])
    e, h, t, a = c(ENTRY), c(HUB), c(TIP), c(APEX)
    u = (e[0] - h[0], e[1] - h[1]); n = math.hypot(*u); u = (u[0] / n, u[1] / n)
    rw0, rw1 = 3.0, 0.9
    root = [(CANINE_AXIS_X - rw0, CANINE[2]), (APEX[0] - rw1, APEX[1] + 2.5), APEX, (APEX[0] + rw1, APEX[1] + 2.5),
            (CANINE_AXIS_X + rw0, CANINE[2])]
    labels = [
        Label(["Mucobuccal", "fold"], anchor=(40, 440), leader=[(250, 392), c((-30, -25.6))], target_id="fold"),
        Label(["Root apex"], anchor=(1000, 200), leader=[(990, 186), (a[0] + 8, a[1])], target_id="apex", emphasis=True),
        Label(["Needle"], anchor=(760, 520), leader=[(748, 504), ((e[0] + h[0]) / 2, (e[1] + h[1]) / 2)], target_id="needle"),
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

    mo = c(MOUTH[0])
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect id="face" x="0" y="0" width="1600" height="1200" fill="url(#skin-grad)"/>
  <path id="nose" d="{path(NOSE, tension=0.6)} L{fmt(c((12, -70))[0])},0 L{fmt(c((-12, -70))[0])},0 Z" fill="#E6B9A0" stroke="#B98A74" stroke-width="3"/>
  <ellipse cx="{fmt(c((-8, -40.5))[0])}" cy="{fmt(c((-8, -40.5))[1])}" rx="40" ry="18" fill="#8E5A48"/>
  <ellipse cx="{fmt(c((8, -40.5))[0])}" cy="{fmt(c((8, -40.5))[1])}" rx="40" ry="18" fill="#8E5A48"/>
  <ellipse id="mouth" cx="{fmt(mo[0])}" cy="{fmt(mo[1])}" rx="{fmt(MOUTH[1] * PX_MM)}" ry="{fmt(MOUTH[2] * PX_MM)}" fill="#5A2A2A"/>
  <path id="lower-lip" d="{path([(-34, 20), (0, 24.5), (36, 20), (34, 31), (0, 35), (-32, 31)], closed=True, tension=0.6)}" fill="#C9787A" stroke="#A55C5E" stroke-width="3"/>
  {lower}
  <path id="gum" d="{path(GUM, closed=True, tension=0.4)}" fill="#E58C8C" stroke="#C46A6C" stroke-width="3"/>
  {teeth}
  <path id="fold" d="{path(FOLD, tension=0.7)}" fill="none" stroke="#B85660" stroke-width="5"/>
  <path id="upper-lip" d="{path(UPPER_LIP, closed=True, tension=0.5)}" fill="#C9787A" stroke="#A55C5E" stroke-width="3"/>
  <path id="finger" d="{path(FINGER, closed=True, tension=0.4)}" fill="url(#glove)" stroke="#B9B2A4" stroke-width="3"/>
</g>

<g class="marking">
  <path id="root" d="{path(root, closed=True, tension=0.4)}" fill="#FFFFFF" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="4" stroke-dasharray="12 8"/>
  <circle id="apex" cx="{fmt(a[0])}" cy="{fmt(a[1])}" r="12" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="4"/>
  <line x1="{fmt(e[0])}" y1="{fmt(e[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#0E8C98" stroke-width="5" stroke-dasharray="10 7"/>
  {syringe(h, u, PX_MM, shadow=True)}
  <line id="needle" x1="{fmt(h[0])}" y1="{fmt(h[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" stroke="url(#syr-steel)" stroke-width="5" stroke-linecap="round"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #3A3F46; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
