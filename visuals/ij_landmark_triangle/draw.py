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


CATHETER_DEFS = """
<filter id="cath-shadow" filterUnits="userSpaceOnUse" x="-400" y="-600" width="800" height="700">
  <feDropShadow dx="5" dy="8" stdDeviation="4.5" flood-color="#5A3A2E" flood-opacity="0.32"/></filter>
<linearGradient id="hub" x1="0" x2="1"><stop offset="0" stop-color="#A7B1B9"/><stop offset="0.45" stop-color="#F3F5F6"/>
  <stop offset="0.6" stop-color="#E4E8EB"/><stop offset="1" stop-color="#9AA5AE"/></linearGradient>
<linearGradient id="cap" x1="0" x2="1"><stop offset="0" stop-color="#8E99A3"/><stop offset="0.45" stop-color="#DDE2E6"/><stop offset="1" stop-color="#7F8B96"/></linearGradient>
"""


def catheter(exit_c) -> str:
    """Triple-lumen line in a local frame pointing up from the exit site, then rotated.

    Shaded as translucent plastic: a grey edge, a pale body and a thin
    highlight, with a soft contact shadow on the skin and a small dimple where
    the shaft enters it. Lumen colours are neutral."""
    ends = [(-95, -430), (0, -455), (95, -430)]

    def tube(d, width):
        return (f'<path d="{d}" fill="none" stroke-linecap="round" stroke="#7C8690" stroke-width="{width + 5}"/>'
                f'<path d="{d}" fill="none" stroke-linecap="round" stroke="#E9EDEF" stroke-width="{width}"/>'
                f'<path d="{d}" fill="none" stroke-linecap="round" stroke="#FFFFFF" stroke-width="{max(width * 0.3, 2)}" '
                f'opacity="0.9" transform="translate(-{width * 0.22:.1f} 0)"/>')

    lines, clamps, caps = [], [], []
    for x, y in ends:
        lines.append(tube(f"M0,-222 C{fmt(x * 0.2)},-290 {fmt(x * 0.9)},{fmt(y + 90)} {fmt(x)},{fmt(y)}", 7))
        cx, cy = x * 0.82, y + 62
        clamps.append(f'<rect x="{fmt(cx - 18)}" y="{fmt(cy - 8)}" width="36" height="16" rx="5" fill="#F7F8F8" stroke="#6E7780" stroke-width="2.5"/>'
                      f'<rect x="{fmt(cx - 12)}" y="{fmt(cy - 3)}" width="24" height="3" rx="1.5" fill="#B8C0C6"/>')
        caps.append(f'<rect x="{fmt(x - 12)}" y="{fmt(y - 36)}" width="24" height="38" rx="6" fill="url(#cap)" stroke="#56606B" stroke-width="2.5"/>'
                    f'<path d="M{fmt(x - 12)},{fmt(y - 24)} h24 M{fmt(x - 12)},{fmt(y - 16)} h24" stroke="#6B7580" stroke-width="1.5" opacity="0.7"/>')
    return f"""
  <g id="central-line" class="marking" transform="translate({fmt(exit_c[0])} {fmt(exit_c[1])}) rotate({fmt(LINE_ANGLE)})">
    <ellipse cx="0" cy="2" rx="11" ry="6" fill="#7A4E3E" opacity="0.35"/>
    <g filter="url(#cath-shadow)">
      <line id="catheter-shaft" x1="0" y1="0" x2="0" y2="-150" stroke="#7C8690" stroke-width="15" stroke-linecap="round"/>
      <line x1="0" y1="-3" x2="0" y2="-150" stroke="#E9EDEF" stroke-width="10" stroke-linecap="round"/>
      <line x1="-2.5" y1="-8" x2="-2.5" y2="-148" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.9"/>
      {"".join(lines)}
      <rect x="-46" y="-197" width="92" height="20" rx="10" fill="url(#hub)" stroke="#56606B" stroke-width="2.5"/>
      <circle cx="-33" cy="-187" r="4.5" fill="#F4F1EA" stroke="#56606B" stroke-width="2"/>
      <circle cx="33" cy="-187" r="4.5" fill="#F4F1EA" stroke="#56606B" stroke-width="2"/>
      <rect id="catheter-hub" x="-20" y="-228" width="40" height="82" rx="10" fill="url(#hub)" stroke="#56606B" stroke-width="2.5"/>
      <rect x="-9" y="-222" width="5" height="70" rx="2.5" fill="#FFFFFF" opacity="0.75"/>
      {"".join(clamps)}
      {"".join(caps)}
    </g>
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
    return document(body, defs=CATHETER_DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
