from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


BASE = Path(
    "docs/visual-assets/review-candidates/"
    "pericardiocentesis_needle_path_iter21_anatomy_only_base_fullres.png"
)
OUT = Path(
    "docs/visual-assets/review-candidates/"
    "pericardiocentesis_needle_path_iter21_hybrid_overlay_candidate.png"
)

DESIGN_WIDTH = 570
DESIGN_HEIGHT = 312


def line(draw: ImageDraw.ImageDraw, xy: tuple[float, float, float, float], fill, width: int) -> None:
    draw.line(xy, fill=fill, width=width, joint="curve")


def circle(draw: ImageDraw.ImageDraw, center: tuple[float, float], radius: float, fill, outline=None, width=1) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline, width=width)


def capsule_polygon(start: tuple[float, float], end: tuple[float, float], width: float) -> list[tuple[float, float]]:
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    nx = -dy / length * width / 2
    ny = dx / length * width / 2
    return [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]


def draw_rotated_capsule(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    fill,
    outline=None,
    outline_width: int = 1,
) -> None:
    poly = capsule_polygon(start, end, width)
    draw.polygon(poly, fill=fill)
    if outline:
        draw.line(poly + [poly[0]], fill=outline, width=outline_width, joint="curve")


def main() -> None:
    scale = 2
    base = Image.open(BASE).convert("RGBA")
    canvas = base.resize((base.width * scale, base.height * scale), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas, "RGBA")
    sx = base.width / DESIGN_WIDTH
    sy = base.height / DESIGN_HEIGHT

    def spt(x: float, y: float) -> tuple[float, float]:
        return x * sx * scale, y * sy * scale

    def sxy(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
        return x1 * sx * scale, y1 * sy * scale, x2 * sx * scale, y2 * sy * scale

    metal = (58, 74, 86, 245)
    metal_mid = (128, 151, 164, 230)
    metal_light = (232, 239, 242, 240)
    glass = (218, 236, 242, 88)
    teal = (23, 132, 165, 235)
    shadow = (30, 40, 48, 45)

    # Main torso overlay: a real-looking syringe/needle, fully inside the card.
    # It enters just inferior to the xiphoid, travels as a forward slash, and
    # stays visibly above/right of the liver rather than crossing it.
    barrel_start = (116, 286)
    barrel_end = (168, 238)
    hub = (176, 231)
    entry = (186, 209)
    tip = (252, 170)

    # Soft shadow.
    line(draw, sxy(*barrel_start, *barrel_end), shadow, 14 * scale)
    line(draw, sxy(*hub, *tip), shadow, 4 * scale)

    # Syringe barrel: translucent body with a subtle metal outline.
    draw_rotated_capsule(
        draw,
        spt(*barrel_start),
        spt(*barrel_end),
        9 * scale,
        glass,
        metal_mid,
        2 * scale,
    )
    line(draw, sxy(126, 279, 158, 249), (255, 255, 255, 105), 1 * scale)

    # Plunger and finger flange sit inside the card rather than being clipped.
    line(draw, sxy(100, 302, 116, 286), metal, 2 * scale)
    line(draw, sxy(92, 294, 109, 311), metal, 2 * scale)
    line(draw, sxy(110, 312, 122, 300), metal, 2 * scale)

    # Hub and needle shaft.
    line(draw, sxy(163, 232, 177, 246), metal, 2 * scale)
    draw_rotated_capsule(draw, spt(168, 233), spt(182, 219), 4 * scale, metal_light, metal, 1 * scale)
    line(draw, sxy(*hub, *tip), metal_light, 3 * scale)
    line(draw, sxy(*entry, *tip), metal, 1 * scale)

    # Inset overlay: a separate magnified needle tip stopping in the external blue fluid crescent.
    inset_hub = (352, 284)
    inset_tip = (480, 238)
    line(draw, sxy(*inset_hub, *inset_tip), shadow, 4 * scale)
    line(draw, sxy(*inset_hub, *inset_tip), metal_light, 2 * scale)
    line(draw, sxy(438, 253, *inset_tip), metal, 1 * scale)
    circle(draw, spt(*inset_tip), 1.9 * scale, teal, (255, 255, 255, 230), 1 * scale)

    result = canvas.resize(base.size, Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
