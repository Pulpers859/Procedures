"""Greater occipital (suboccipital) nerve block - needle entry on the patient.

A seated man seen from behind with his head bent forward, close on the back
of the head and neck. The patient's right is on the image right (seen from
behind). Photograph: Antigravity, from the approved thoracentesis patient
(same man, same room) with the approved ESP glove as the glove reference.

Record: palpate the external occipital protuberance and the mastoid; at the
point one-third of the way from the protuberance to the mastoid, on the
superior nuchal line, feel for the occipital artery; the entry is just
medial to it; insert perpendicular to the skin until resistance.

In the photo the gloved index fingertip rests on the occipital artery at the
base of the skull on the patient's right. Code-drawn: the needle and syringe
entering just medial to the fingertip, the ring over the artery, and the
dashed midline. Canvas px; the photo fills the canvas (4:3).

Run: python3 visuals/greater_occipital_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import SYRINGE_DEFS, Label, document, fmt, syringe  # noqa: E402

ASSET_ID = "greater_occipital_patient_position"
BASE = Path(__file__).with_name("base.jpg")

FINGERTIP = (925.0, 540.0)        # glove tip on the occipital artery (base 694, 405; place_hand.py)
ENTRY = (893.0, 538.0)            # just medial to the fingertip, about 2 cm from the midline
MIDLINE_X = 797.0                 # midline of the back of the head (base 598)
# The needle comes toward the scalp from below and slightly to the left; with
# the head bent forward this reads as perpendicular to the skull.
ANGLE = math.radians(80)         # direction from entry back along the needle (image coords)
NEEDLE_LEN = 40.0
PX_MM = 5.0                       # head about 15 cm across in the photo

DEFS = SYRINGE_DEFS


def build() -> str:
    ux, uy = math.cos(ANGLE), math.sin(ANGLE)
    hub = (ENTRY[0] + ux * NEEDLE_LEN, ENTRY[1] + uy * NEEDLE_LEN)
    kit = syringe(hub, (-ux, -uy), PX_MM)
    labels = [
        Label(["Occipital artery", "under the fingertip"], anchor=(1010, 300), leader=[(1060, 345), (FINGERTIP[0] + 10, FINGERTIP[1] - 14)],
              target_id="artery-mark"),
        Label(["Entry, just medial"], anchor=(280, 330), leader=[(560, 360), (ENTRY[0] - 4, ENTRY[1] - 4)],
              target_id="needle-entry", emphasis=True),
    ]
    painted = BASE.exists()
    if painted:
        from PIL import Image
        bw_, bh_ = Image.open(BASE).size
        height = 1600 * bh_ / bw_
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - height) / 2)}" width="1600" '
                      f'height="{fmt(height)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if os.environ.get("DEBUG") == "1" else 0}"'
    else:
        base_attr = base_image = layout_attr = ""
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#B8C3CC"/>
  <ellipse id="head" cx="{fmt(MIDLINE_X)}" cy="380" rx="330" ry="360" fill="#3A302A"/>
</g>

<g class="marking">
  <line id="midline" x1="{fmt(MIDLINE_X)}" y1="430" x2="{fmt(MIDLINE_X)}" y2="760" stroke="#F6F7F9" stroke-width="4" stroke-dasharray="12 10" opacity="0.8"/>
  <circle id="artery-mark" cx="{fmt(FINGERTIP[0])}" cy="{fmt(FINGERTIP[1])}" r="30" fill="none" stroke="#C8322B" stroke-width="6" stroke-dasharray="10 7"/>
  <g id="syringe">{kit}</g>
  <line id="needle" x1="{fmt(hub[0])}" y1="{fmt(hub[1])}" x2="{fmt(ENTRY[0])}" y2="{fmt(ENTRY[1])}" stroke="url(#syr-steel)" stroke-width="5" stroke-linecap="round"/>
  <circle id="needle-entry" cx="{fmt(ENTRY[0])}" cy="{fmt(ENTRY[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #B8C3CC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
