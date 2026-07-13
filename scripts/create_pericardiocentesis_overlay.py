from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


BASE = Path(
    "docs/visual-assets/review-candidates/"
    "pericardiocentesis_needle_path_iter20_anatomy_only_base.png"
)
OUT = Path(
    "docs/visual-assets/review-candidates/"
    "pericardiocentesis_needle_path_iter20_hybrid_overlay_candidate.png"
)


def line(draw: ImageDraw.ImageDraw, xy: tuple[float, float, float, float], fill, width: int) -> None:
    draw.line(xy, fill=fill, width=width, joint="curve")


def circle(draw: ImageDraw.ImageDraw, center: tuple[float, float], radius: float, fill, outline=None, width=1) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline, width=width)


def main() -> None:
    scale = 4
    base = Image.open(BASE).convert("RGBA")
    canvas = base.resize((base.width * scale, base.height * scale), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas, "RGBA")

    def spt(x: float, y: float) -> tuple[float, float]:
        return x * scale, y * scale

    def sxy(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
        return x1 * scale, y1 * scale, x2 * scale, y2 * scale

    metal = (64, 82, 94, 245)
    metal_light = (224, 233, 238, 245)
    teal = (23, 132, 165, 235)
    shadow = (40, 50, 58, 65)

    # Main torso overlay: hub lower-left/bottom-center, entry just right of the liver edge,
    # needle rises toward image-right/superior. Coordinates are intentionally fixed.
    barrel_start = (145, 314)
    barrel_end = (186, 266)
    needle_start = (186, 266)
    entry = (207, 214)
    tip = (292, 168)

    # Soft underlay makes the instrument readable without becoming a thick "tube."
    line(draw, sxy(*barrel_start, *barrel_end), shadow, 12 * scale)
    line(draw, sxy(*needle_start, *tip), shadow, 5 * scale)

    # Syringe barrel and plunger, drawn in the same slash direction.
    line(draw, sxy(*barrel_start, *barrel_end), metal_light, 10 * scale)
    line(draw, sxy(*barrel_start, *barrel_end), metal, 2 * scale)
    line(draw, sxy(134, 303, 156, 324), metal, 2 * scale)
    line(draw, sxy(129, 309, 140, 298), metal, 2 * scale)
    line(draw, sxy(152, 330, 164, 318), metal, 2 * scale)
    line(draw, sxy(178, 260, 195, 275), metal, 3 * scale)

    # Needle shaft: slim, explicit, and separate from the liver. No direction dot or arrow.
    line(draw, sxy(*needle_start, *tip), metal_light, 4 * scale)
    line(draw, sxy(*entry, *tip), metal, 2 * scale)

    # Inset overlay: a separate magnified needle tip stopping in the external blue fluid crescent.
    inset_hub = (355, 282)
    inset_tip = (482, 238)
    line(draw, sxy(*inset_hub, *inset_tip), shadow, 5 * scale)
    line(draw, sxy(*inset_hub, *inset_tip), metal_light, 3 * scale)
    line(draw, sxy(440, 252, *inset_tip), metal, 2 * scale)
    circle(draw, spt(*inset_tip), 2.4 * scale, teal, (255, 255, 255, 230), 1 * scale)

    result = canvas.resize(base.size, Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
