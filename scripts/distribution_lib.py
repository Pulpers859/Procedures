"""Shared drawing for the nerve-block distribution plates (`visuals/*_distribution`).

A plate is one of the shared base paintings in `visuals/distribution_bases/<view>/`
(the figures are painted once per view, never per block) with the block's
territories tinted over it. Owner, 2026-10-15: no labels on the plate (the key
is the record's `legend`), strict territories that never bleed onto a part
the block does not supply, and an independent audit of every plate.

How the tint stays strict:
- every territory is clipped to a mask traced from the painting
  (`distribution_bases/make_masks.py`): `body` for skin, `bone` for bone;
- a skin territory is also clipped to a hand-traced region of its limb or
  body part (`clip`), so a soft edge can never reach a neighbouring limb;
- the tint is multiplied onto the painting so its shading shows through.

Coordinates are base-painting px (1200 x 896), patient's right on the image
left in front views (the house laterality) and on the image right in back
views. The model plate is `ficb_distribution/` (drawn before this module, in
canvas px); its look parameters are the defaults here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from visuals_lib import document, fmt, smooth_path

REPO = Path(__file__).resolve().parents[1]
BASES = REPO / "visuals" / "distribution_bases"
BASE_W, BASE_H = 1200.0, 896.0
K = 1600 / BASE_W
OY = (1200 - BASE_H * K) / 2

# Shared with the app (LegendEntry.Tone.color) and validate_procedures.py.
TONES = {"teal": "#2E9C97", "violet": "#8A78C2", "amber": "#D99A3A", "rose": "#D0707A", "blue": "#4A8FD0"}

Point = tuple[float, float]


@dataclass
class Zone:
    """One tinted territory.

    layer: "skin" (clipped to the painted body) or "bone" (to the painted bone).
    clip: name of a region in the plate's CLIPS; required for skin.
    feather: blur in base px; 0 keeps a hard edge that follows the mask.
    fade: optional (x1, y1, x2, y2) - the tint fades from nothing at the
      first point to full at the second (a border that is a gradient in life).
    """
    id: str
    tone: str
    points: list[Point]
    layer: str = "skin"
    clip: str | None = None
    feather: float = 4.5
    opacity: float | None = None
    tension: float = 0.35
    fade: tuple[float, float, float, float] | None = None
    extra: list[list[Point]] = field(default_factory=list)   # more polygons of the same territory

    def __post_init__(self):
        if self.tone not in TONES:
            raise ValueError(f"{self.id}: tone {self.tone!r} not in {sorted(TONES)}")
        if self.layer not in ("skin", "bone"):
            raise ValueError(f"{self.id}: layer must be skin or bone")
        if self.layer == "skin" and not self.clip:
            raise ValueError(f"{self.id}: a skin territory needs a clip region (no bleed onto other parts)")


def _rel(view: str, name: str) -> str:
    return f"../distribution_bases/{view}/{name}"


def build_plate(view: str, zones: list[Zone], clips: dict[str, list[Point]]) -> str:
    base = BASES / view / "base.jpg"
    sha = hashlib.sha256(base.read_bytes()).hexdigest()
    feathers = sorted({z.feather for z in zones if z.feather})
    defs = [f'<filter id="feather-{fmt(f).replace(".", "_")}" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feGaussianBlur stdDeviation="{fmt(f)}"/></filter>' for f in feathers]
    for layer in ("body", "bone"):
        defs.append(f'<mask id="m-{layer}" maskUnits="userSpaceOnUse" x="0" y="0" width="{fmt(BASE_W)}" height="{fmt(BASE_H)}">'
                    f'<image href="{_rel(view, f"mask_{layer}.png")}" x="0" y="0" width="{fmt(BASE_W)}" '
                    f'height="{fmt(BASE_H)}" preserveAspectRatio="none"/></mask>')
    for name, pts in clips.items():
        defs.append(f'<clipPath id="c-{name}"><path d="{smooth_path(pts, closed=True, tension=0.2)}"/></clipPath>')
    for z in zones:
        if z.fade:
            x1, y1, x2, y2 = z.fade
            defs.append(f'<linearGradient id="fade-{z.id}" gradientUnits="userSpaceOnUse" x1="{fmt(x1)}" y1="{fmt(y1)}" '
                        f'x2="{fmt(x2)}" y2="{fmt(y2)}"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#FFF"/></linearGradient>'
                        f'<mask id="m-fade-{z.id}" maskUnits="userSpaceOnUse" x="0" y="0" width="{fmt(BASE_W)}" height="{fmt(BASE_H)}">'
                        f'<rect width="{fmt(BASE_W)}" height="{fmt(BASE_H)}" fill="url(#fade-{z.id})"/></mask>')

    groups = []
    for z in zones:
        opacity = z.opacity if z.opacity is not None else (0.58 if z.layer == "skin" else 0.5)
        polys = [z.points] + z.extra
        d = " ".join(smooth_path(p, closed=True, tension=z.tension) for p in polys)
        shape = f'<path id="{z.id}" d="{d}" fill="{TONES[z.tone]}" fill-opacity="{fmt(opacity)}"/>'
        if z.feather:
            shape = f'<g filter="url(#feather-{fmt(z.feather).replace(".", "_")})">{shape}</g>'
        if z.fade:
            shape = f'<g mask="url(#m-fade-{z.id})">{shape}</g>'
        shape = f'<g mask="url(#m-{"body" if z.layer == "skin" else "bone"})">{shape}</g>'
        clip = f' clip-path="url(#c-{z.clip})"' if z.clip else ""
        # Multiply on the outermost group: inside a mask it composites as paint.
        groups.append(f'<g{clip} style="mix-blend-mode:multiply">{shape}</g>')

    body = f"""
<g id="painting" data-base-sha256="{sha}">
  <image id="base" href="{_rel(view, 'base.jpg')}" x="0" y="{fmt(OY)}" width="1600" height="{fmt(BASE_H * K)}" preserveAspectRatio="none"/>
</g>
<g class="marking" transform="translate(0 {fmt(OY)}) scale({K:.6f})">
  {chr(10).join('  ' + g for g in groups)}
</g>
"""
    return document(body, defs="\n".join(defs), extra_style=".plate-bg { fill: #F4F3EF; }")


def write(asset_id: str, text: str) -> int:
    out = REPO / "visuals" / asset_id / f"{asset_id}.svg"
    out.write_text(text, encoding="utf-8")
    print(out)
    return 0
