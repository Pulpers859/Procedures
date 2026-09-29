"""Pigtail pleural catheter: dilate to chest-wall depth only.

A painted base with code-drawn labels. The art is a Gemini (Nano Banana Pro)
render that the owner iterated in the Gemini app and that was checked against
the answer key in spec.json; see provenance.json for the prompt and repairs.
Because the base is a raster, its anatomy cannot be measured in code. The
label targets below are regions hand-traced over the base in base-image
pixels, and render_visuals.py checks that each leader lands inside its
region. Re-trace them if the base image is ever replaced.

Run: python3 visuals/pigtail_seldinger/draw.py   (DEBUG=1 shows the regions)
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, pts, strip  # noqa: E402

ASSET_ID = "pigtail_seldinger"
BASE = "base.jpg"
BASE_SIZE = (1200.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2


def canvas(p):
    """Base-image pixel -> canvas coordinate."""
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels.
BRACKET = ((298.0, 508.5), (780.0, 508.5))            # cyan skin-to-pleura line
PLEURA = [(767, 330), (768, 400), (775, 436), (769, 462), (746, 492), (724, 560)]  # parietal pleura at the tip
DILATOR_TIP = (768.0, 445.0)


def band(points, half_width):
    """Closed polygon around a polyline, for a thin traced structure."""
    left, right = [], []
    for i, p in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, len(points) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5 or 1
        nx, ny = -dy / length * half_width, dx / length * half_width
        left.append((p[0] + nx, p[1] + ny))
        right.append((p[0] - nx, p[1] - ny))
    return left + right[::-1]


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    region_style = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'

    pleura_region = [canvas(p) for p in band(PLEURA, 7)]
    bracket_region = [canvas(p) for p in strip(*BRACKET, 16)]

    labels = [
        Label(["Parietal pleura"], anchor=(1010, 170),
              leader=[(1150, 190), canvas((768, 398))],
              target_id="parietal-pleura", emphasis=True),
        Label(["Measured", "depth"], anchor=(48, 900),
              leader=[(200, 845), canvas((360, 508.5))],
              target_id="measured-depth"),
    ]

    # The base's hash is part of the SVG, so replacing the painting changes the
    # SVG and voids an approval recorded against it.
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()
    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  <polygon id="parietal-pleura" points="{pts(pleura_region)}" {region_style}/>
  <polygon id="measured-depth" points="{pts(bracket_region)}" {region_style}/>
  <circle id="dilator-tip" cx="{fmt(canvas(DILATOR_TIP)[0])}" cy="{fmt(canvas(DILATOR_TIP)[1])}" r="6" {region_style}/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F8F5EC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
