"""Internal jugular landmarks - the sternocleidomastoid triangle, with the line in.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of the code-drawn layout (git history of this file, and
provenance.json): front of the neck, head at the top turned slightly left,
the right neck on the image left. The IJ shows in the triangle between the
sternal and clavicular heads of the right SCM, lateral to the carotid.

The triple-lumen line is painted too (owner, 2026-09-30: "show the catheter
with triple lumen coming out of the neck and IJ"; the owner preferred the
painted line to a code-drawn one). Gemini ran the shaft on past the triangle
to a clear stub lying on the clavicle. That tail and stub were erased by
blending back colour-matched pixels from the owner's clean painting of the
same anatomy (gemini-line-original.jpg is the unedited file). The shaft now
ends in the triangle over the IJ, about 1.5 cm below the apex; code draws the
skin-entry dimple and the teal ring there.

Regions are hand-traced over the base in base-image pixels (DEBUG=1 shows
them). Re-trace everything if the base is replaced.

Run: python3 visuals/ij_landmark_triangle/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, pts, smooth_path  # noqa: E402

ASSET_ID = "ij_landmark_triangle"
BASE = "base.jpg"
BASE_SIZE = (1195.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2


def canvas(p):
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels.
TRIANGLE_IJ = [(582, 552), (566, 652), (620, 652)]           # the IJ as it shows in the triangle
STERNAL_HEAD = [(586, 545), (625, 655), (690, 740), (735, 740), (700, 640), (640, 500), (600, 470)]
CLAVICULAR_HEAD = [(445, 690), (562, 662), (580, 548), (560, 480), (462, 480), (442, 600)]
CAROTID = ([(588, 170), (615, 300), (640, 420), (655, 500)], 22)
EXIT = (586.0, 624.0)                                        # where the painted shaft enters the skin, in the triangle over the IJ


# The painted line, traced in base pixels: the shaft from the hub to where it
# now enters the skin, and the hub itself.
SHAFT = ([(350, 440), (420, 482), (480, 530), (530, 575), (586, 624)], 12)
HUB = [(262, 350), (300, 338), (336, 372), (318, 400), (276, 396)]


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    region = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()

    def poly(points):
        return pts([canvas(p) for p in points])

    carotid_points, carotid_width = CAROTID
    carotid_style = 'stroke="#ff00ff" stroke-opacity="0.5"' if debug else 'stroke="#000" stroke-opacity="0"'
    exit_c = canvas(EXIT)

    labels = [
        Label(["Sternal head"], anchor=(1150, 930), leader=[(1145, 910), canvas((660, 640))], target_id="sternal-head"),
        Label(["Clavicular head"], anchor=(40, 1150), leader=[(300, 1100), canvas((500, 620))], target_id="clavicular-head"),
        Label(["Internal", "jugular vein"], anchor=(1150, 620), leader=[(1145, 632), canvas((593, 625))],
              target_id="internal-jugular", emphasis=True),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  <polygon id="internal-jugular" points="{poly(TRIANGLE_IJ)}" {region}/>
  <polygon id="sternal-head" points="{poly(STERNAL_HEAD)}" {region}/>
  <polygon id="clavicular-head" points="{poly(CLAVICULAR_HEAD)}" {region}/>
  <path id="carotid-artery" d="{smooth_path([canvas(p) for p in carotid_points])}" fill="none" stroke-width="{fmt(carotid_width * SCALE)}" {carotid_style}/>
  <path id="catheter-shaft" d="{smooth_path([canvas(p) for p in SHAFT[0]])}" fill="none" stroke-width="{fmt(SHAFT[1] * SCALE)}" {carotid_style}/>
  <polygon id="catheter-hub" points="{poly(HUB)}" {region}/>
  <ellipse class="marking" cx="{fmt(exit_c[0] + 2)}" cy="{fmt(exit_c[1] + 3)}" rx="13" ry="8" fill="#6A3F33" opacity="0.4" transform="rotate(38 {fmt(exit_c[0])} {fmt(exit_c[1])})"/>
  <circle id="exit-site" class="marking" cx="{fmt(exit_c[0])}" cy="{fmt(exit_c[1])}" r="22" fill="none" stroke="#0E8C98" stroke-width="5"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
