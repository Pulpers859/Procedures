"""Shared building blocks for code-drawn procedure visuals.

Each visual lives in `visuals/<asset_id>/`: a `draw.py` that builds the SVG
from named geometry, the generated `<asset_id>.svg`, and a `spec.json` that
states what the picture must get right. `scripts/render_visuals.py` renders
the SVG in Chromium and checks the spec against the real rendered geometry.

Why code rather than an image model: a model gives plausible texture with no
guarantee of laterality, endpoints or spelling, and every fix is a re-roll.
Here every structure is a named element, a label's leader has an exact
endpoint, and a correction is a one-line change that re-renders identically.
See `visuals/README.md`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from xml.sax.saxutils import escape

WIDTH = 1600
HEIGHT = 1200

Point = tuple[float, float]


def fmt(value: float) -> str:
    text = f"{value:.1f}"
    return text[:-2] if text.endswith(".0") else text


def pts(points: list[Point]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ellipse_point(center: Point, rx: float, ry: float, degrees: float) -> Point:
    """Point on an ellipse; 0 degrees is image-right, 90 is image-down."""
    radians = math.radians(degrees)
    return (center[0] + rx * math.cos(radians), center[1] + ry * math.sin(radians))


def smooth_path(points: list[Point], closed: bool = False, tension: float = 1.0) -> str:
    """Catmull-Rom spline through every point, emitted as cubic Beziers."""
    if len(points) < 2:
        raise ValueError("need at least two points")
    seq = list(points)
    if closed:
        seq = [seq[-1]] + seq + [seq[0], seq[1]]
    else:
        seq = [seq[0]] + seq + [seq[-1]]
    out = [f"M{fmt(seq[1][0])},{fmt(seq[1][1])}"]
    for i in range(1, len(seq) - 2):
        p0, p1, p2, p3 = seq[i - 1], seq[i], seq[i + 1], seq[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 6, p1[1] + (p2[1] - p0[1]) * tension / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 6, p2[1] - (p3[1] - p1[1]) * tension / 6)
        out.append(f"C{fmt(c1[0])},{fmt(c1[1])} {fmt(c2[0])},{fmt(c2[1])} {fmt(p2[0])},{fmt(p2[1])}")
    if closed:
        out.append("Z")
    return " ".join(out)


def ellipse_band(center: Point, rx: float, ry: float, thickness: float,
                 start: float, end: float, steps: int = 24) -> list[Point]:
    """Closed polygon for a band of `thickness` centred on an elliptical arc."""
    half = thickness / 2
    outer = [ellipse_point(center, rx + half, ry + half, start + (end - start) * i / steps) for i in range(steps + 1)]
    inner = [ellipse_point(center, rx - half, ry - half, end - (end - start) * i / steps) for i in range(steps + 1)]
    return outer + inner


def strip(a: Point, b: Point, width_a: float, width_b: float | None = None) -> list[Point]:
    """Four-corner polygon for a straight band from a to b (a tapered tendon)."""
    width_b = width_a if width_b is None else width_b
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    return [
        (a[0] + nx * width_a / 2, a[1] + ny * width_a / 2),
        (b[0] + nx * width_b / 2, b[1] + ny * width_b / 2),
        (b[0] - nx * width_b / 2, b[1] - ny * width_b / 2),
        (a[0] - nx * width_a / 2, a[1] - ny * width_a / 2),
    ]


def hair_strokes(seed: int, along: list[Point], count: int, length: float,
                 spread: float, lean: float) -> str:
    """Deterministic short strokes following a curve - brows, lashes."""
    rng = random.Random(seed)
    parts = []
    for _ in range(count):
        t = rng.random() * (len(along) - 1)
        i = min(int(t), len(along) - 2)
        base = lerp(along[i], along[i + 1], t - i)
        dx, dy = along[i + 1][0] - along[i][0], along[i + 1][1] - along[i][1]
        angle = math.atan2(dy, dx) + lean + rng.uniform(-0.25, 0.25)
        offset = rng.uniform(-spread, spread)
        start = (base[0], base[1] + offset)
        stroke = length * rng.uniform(0.6, 1.1)
        end = (start[0] + math.cos(angle) * stroke, start[1] + math.sin(angle) * stroke)
        bend = (lerp(start, end, 0.5)[0], lerp(start, end, 0.5)[1] - stroke * 0.12)
        parts.append(f"M{fmt(start[0])},{fmt(start[1])} Q{fmt(bend[0])},{fmt(bend[1])} {fmt(end[0])},{fmt(end[1])}")
    return " ".join(parts)


@dataclass
class Label:
    """A noun label whose leader ends exactly on the element it names.

    `lines` are the rendered text lines; `anchor` is where the text block
    starts; `target_id` is the element the leader must land inside, which
    `render_visuals.py` verifies in the browser.
    """

    lines: list[str]
    anchor: Point
    leader: list[Point]
    target_id: str
    emphasis: bool = False
    align: str = "start"

    def svg(self) -> str:
        cls = "label emphasis" if self.emphasis else "label"
        text_lines = "".join(
            f'<tspan x="{fmt(self.anchor[0])}" dy="{0 if i == 0 else 66}">{escape(line)}</tspan>'
            for i, line in enumerate(self.lines)
        )
        end = self.leader[-1]
        return (
            f'<g class="{cls}" data-label="{escape(" ".join(self.lines))}" data-target="{self.target_id}">'
            f'<polyline class="leader-halo" points="{pts(self.leader)}"/>'
            f'<polyline class="leader" points="{pts(self.leader)}"/>'
            f'<circle class="leader-dot" cx="{fmt(end[0])}" cy="{fmt(end[1])}" r="7"/>'
            f'<text x="{fmt(self.anchor[0])}" y="{fmt(self.anchor[1])}" text-anchor="{self.align}">{text_lines}</text>'
            f"</g>"
        )


HOUSE_STYLE = """
@font-face { font-family: "Plate Sans"; font-weight: 500; src: url("../fonts/inter-latin-500-normal.woff2") format("woff2"); }
@font-face { font-family: "Plate Sans"; font-weight: 700; src: url("../fonts/inter-latin-700-normal.woff2") format("woff2"); }
svg {
  --bg: #F6F7F9;
  --ink: #1C2530;
  --skin-hi: #F7E3D4; --skin: #EDCDB8; --skin-lo: #D9AE95; --skin-deep: #C48F75;
  --lid-line: #7A4E3E; --lash: #3B2A24; --brow: #6B4A3A;
  --sclera: #FBFBF8; --sclera-shade: #E4E2DC;
  --iris-hi: #7FA7A1; --iris: #4F7C78; --iris-lo: #2E4F4D; --pupil: #141A1C;
  --caruncle: #E39A95;
  --bone: #EFE6D2; --bone-edge: #A8977A;
  --deep-grey: #8B8F96;
  --target: #0E8C98; --target-fill: rgba(14, 140, 152, 0.38);
  --danger: #D8432A; --danger-soft: #F08A73;
  --halo: rgba(246, 247, 249, 0.92);
  font-family: "Plate Sans", "Inter", "Helvetica Neue", Arial, sans-serif;
}
/* Dark mode: plates are full-bleed, so labels sit on the art, not on the page.
   Keep the label colours and dim the art a little so it does not glare in a
   dark card. A plate that leaves open background would override --bg here. */
svg.dark { --bg: #16191E; }
svg.dark #anatomy { filter: brightness(0.86) saturate(0.95); }
.plate-bg { fill: var(--bg); }
.label text { font-size: 56px; font-weight: 500; fill: var(--ink); paint-order: stroke; stroke: var(--halo); stroke-width: 14px; stroke-linejoin: round; }
.label.emphasis text { font-weight: 700; fill: var(--target); }
.leader { fill: none; stroke: var(--ink); stroke-width: 3; }
.label.emphasis .leader { stroke: var(--target); stroke-width: 4; }
.leader-halo { fill: none; stroke: var(--halo); stroke-width: 11; stroke-linecap: round; }
.leader-dot { fill: var(--ink); stroke: var(--halo); stroke-width: 4; }
.label.emphasis .leader-dot { fill: var(--target); }
"""


def document(body: str, defs: str = "", extra_style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">\n'
        f"<style>{HOUSE_STYLE}{extra_style}</style>\n"
        f"<defs>{defs}</defs>\n"
        f'<rect class="plate-bg" width="{WIDTH}" height="{HEIGHT}"/>\n'
        f"{body}\n</svg>\n"
    )
