from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


OUT = Path("docs/visual-assets/review-candidates/pericardiocentesis_needle_path_iter32_controlled_schematic.png")


S = 3
W, H = 1600, 1200


def sc(v: float) -> int:
    return int(round(v * S))


def xy(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    return tuple(sc(v) for v in box)


def pt(point: tuple[float, float]) -> tuple[int, int]:
    return sc(point[0]), sc(point[1])


def line(draw: ImageDraw.ImageDraw, coords: tuple[float, float, float, float], fill, width: float) -> None:
    draw.line(tuple(sc(v) for v in coords), fill=fill, width=sc(width), joint="curve")


def ellipse(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], fill, outline=None, width: float = 1) -> None:
    draw.ellipse(xy(box), fill=fill, outline=outline, width=sc(width))


def rounded(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill, outline=None, width: float = 1) -> None:
    draw.rounded_rectangle(xy(box), radius=sc(radius), fill=fill, outline=outline, width=sc(width))


def capsule(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], width: float, fill, outline=None) -> None:
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    nx = -dy / length * width / 2
    ny = dx / length * width / 2
    poly = [
        (sc(x1 + nx), sc(y1 + ny)),
        (sc(x2 + nx), sc(y2 + ny)),
        (sc(x2 - nx), sc(y2 - ny)),
        (sc(x1 - nx), sc(y1 - ny)),
    ]
    draw.polygon(poly, fill=fill)
    r = width / 2
    ellipse(draw, (x1 - r, y1 - r, x1 + r, y1 + r), fill, None)
    ellipse(draw, (x2 - r, y2 - r, x2 + r, y2 + r), fill, None)
    if outline:
        draw.line(poly + [poly[0]], fill=outline, width=sc(2), joint="curve")


def main() -> None:
    img = Image.new("RGBA", (W * S, H * S), (250, 249, 244, 255))
    d = ImageDraw.Draw(img, "RGBA")

    # Torso silhouette.
    torso = [pt((230, 115)), pt((1370, 115)), pt((1465, 1110)), pt((135, 1110))]
    d.polygon(torso, fill=(238, 195, 175, 120), outline=(130, 78, 60, 145))
    line(d, (800, 150, 800, 1030), (170, 120, 105, 55), 2)

    # Sternum and xiphoid.
    rounded(d, (735, 150, 865, 540), 56, (222, 195, 145, 205), (115, 95, 70, 155), 4)
    d.polygon([pt((775, 540)), pt((825, 540)), pt((800, 610))], fill=(222, 195, 145, 205), outline=(115, 95, 70, 155))

    # Ribs and costal margins.
    rib_color = (170, 145, 108, 168)
    cartilage = (216, 216, 196, 135)
    for y, rx in [(235, 475), (320, 535), (410, 585), (500, 620), (590, 640)]:
        d.arc(xy((800 - rx, y - 80, 800, y + 130)), 184, 354, fill=rib_color, width=sc(9))
        d.arc(xy((800, y - 80, 800 + rx, y + 130)), 186, 356, fill=rib_color, width=sc(9))
        rounded(d, (715, y + 20, 800, y + 42), 10, cartilage, None, 1)
        rounded(d, (800, y + 20, 885, y + 42), 10, cartilage, None, 1)
    line(d, (735, 590, 660, 785), (154, 129, 100, 160), 8)
    line(d, (865, 590, 1015, 785), (154, 129, 100, 160), 8)

    # Heart, kept superior/right of the skin entry so the external entry dot
    # cannot read as a needle entering myocardium in the main torso panel.
    ellipse(d, (790, 365, 1040, 650), (203, 66, 74, 150), (130, 35, 45, 125), 4)

    # Liver: visible danger anatomy, deliberately clear of instrument corridor.
    ellipse(d, (225, 705, 615, 955), (142, 58, 40, 172), (98, 32, 28, 190), 4)
    ellipse(d, (300, 735, 575, 890), (175, 82, 57, 70), None, 1)

    # Subxiphoid external syringe: one continuous physical instrument; visible needle stops at entry.
    barrel_start = (430, 1080)
    barrel_end = (635, 800)
    hub = (660, 765)
    entry = (770, 645)
    shadow = (25, 35, 40, 42)
    line(d, (*barrel_start, *barrel_end), shadow, 38)
    capsule(d, barrel_start, barrel_end, 34, (220, 238, 244, 120), (58, 79, 90, 210))
    line(d, (458, 1040, 594, 826), (255, 255, 255, 120), 5)
    for t in [0.18, 0.34, 0.50, 0.66, 0.82]:
        x = barrel_start[0] + (barrel_end[0] - barrel_start[0]) * t
        y = barrel_start[1] + (barrel_end[1] - barrel_start[1]) * t
        line(d, (x - 13, y - 8, x + 13, y + 8), (55, 75, 86, 130), 2)
    line(d, (380, 1155, *barrel_start), (60, 65, 70, 220), 9)
    line(d, (340, 1118, 420, 1185), (60, 65, 70, 220), 9)
    line(d, (395, 1030, 500, 1118), (60, 65, 70, 220), 9)
    capsule(d, (620, 790), (680, 730), 36, (39, 147, 169, 230), (20, 80, 95, 230))
    line(d, (*hub, *entry), (236, 242, 244, 255), 9)
    line(d, (*hub, *entry), (42, 54, 62, 245), 3)
    ellipse(d, (727, 610, 743, 626), (25, 130, 160, 230), (255, 255, 255, 210), 2)

    # Inset.
    inset = (1045, 305, 1510, 775)
    d.rectangle(xy(inset), fill=(255, 250, 244, 255), outline=(22, 22, 22, 255), width=sc(6))
    ellipse(d, (1120, 365, 1410, 710), (205, 62, 75, 235), (125, 35, 45, 220), 5)
    d.pieslice(xy((1200, 330, 1505, 740)), 82, 278, fill=(73, 155, 207, 218), outline=(22, 94, 140, 240), width=sc(5))
    # Fine needle tip in fluid, with blue surrounding the tip.
    line(d, (1510, 425, 1342, 590), (35, 45, 52, 240), 7)
    line(d, (1510, 425, 1342, 590), (232, 240, 244, 255), 4)
    d.polygon([pt((1342, 590)), pt((1366, 575)), pt((1356, 604))], fill=(232, 240, 244, 255), outline=(35, 45, 52, 230))
    ellipse(d, (1335, 583, 1349, 597), (30, 135, 182, 225), (255, 255, 255, 210), 2)

    # Subtle crop border.
    d.rectangle((0, 0, W * S - 1, H * S - 1), outline=(235, 232, 220, 255), width=sc(2))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = img.resize((W, H), Image.Resampling.LANCZOS).convert("RGB")
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
