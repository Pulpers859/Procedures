"""Internal jugular landmarks - the sternocleidomastoid triangle, with the line in.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
repaint of the code-drawn layout (git history of this file, and
provenance.json): front of the neck, head at the top turned slightly left,
the right neck on the image left. The IJ shows in the triangle between the
sternal and clavicular heads of the right SCM, lateral to the carotid.

Markings, drawn here (owner, 2026-09-30: "show the catheter with triple
lumen coming out of the neck and IJ"): a triple-lumen central line leaving
the skin at the apex of the triangle, over the IJ, with its hub pointing
headward as an IJ line lies, three extension lines, clamps and caps. The teal
ring marks the site. Lumen colours are left neutral, since they vary by kit.

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
EXIT = (583.0, 560.0)                                        # just inside the apex
LINE_ANGLE = -27.0                                           # degrees from straight up; negative leans lateral (image left)


def catheter(exit_c) -> str:
    """Triple-lumen line in a local frame pointing up from the exit site, then rotated."""
    tube = 'fill="none" stroke-linecap="round"'
    ends = [(-95, -430), (0, -455), (95, -430)]
    lines, clamps, caps = [], [], []
    for x, y in ends:
        d = f"M0,-222 C{fmt(x * 0.2)},-290 {fmt(x * 0.9)},{fmt(y + 90)} {fmt(x)},{fmt(y)}"
        lines.append(f'<path d="{d}" {tube} stroke="#8C949C" stroke-width="12"/>'
                     f'<path d="{d}" {tube} stroke="#F7F8F6" stroke-width="7"/>')
        cx, cy = x * 0.82, y + 62
        clamps.append(f'<rect x="{fmt(cx - 17)}" y="{fmt(cy - 7)}" width="34" height="14" rx="4" fill="#E9ECEE" stroke="#6E7780" stroke-width="2.5"/>')
        caps.append(f'<rect x="{fmt(x - 11)}" y="{fmt(y - 34)}" width="22" height="36" rx="6" fill="#C9D0D6" stroke="#5E6873" stroke-width="2.5"/>')
    return f"""
  <g id="central-line" class="marking" transform="translate({fmt(exit_c[0])} {fmt(exit_c[1])}) rotate({fmt(LINE_ANGLE)})">
    <line id="catheter-shaft" x1="0" y1="0" x2="0" y2="-150" stroke="#6E7780" stroke-width="15" stroke-linecap="round"/>
    <line x1="0" y1="0" x2="0" y2="-150" stroke="#F7F8F6" stroke-width="10" stroke-linecap="round"/>
    {"".join(lines)}
    <rect x="-44" y="-196" width="88" height="18" rx="9" fill="#E3E7EA" stroke="#5E6873" stroke-width="2.5"/>
    <circle cx="-32" cy="-187" r="4" fill="#5E6873"/><circle cx="32" cy="-187" r="4" fill="#5E6873"/>
    <rect id="catheter-hub" x="-19" y="-226" width="38" height="80" rx="9" fill="#D5DBE0" stroke="#5E6873" stroke-width="2.5"/>
    {"".join(clamps)}
    {"".join(caps)}
  </g>"""


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
{catheter(exit_c)}
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
