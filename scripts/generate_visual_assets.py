from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 1200
OUT_DIR = Path(__file__).resolve().parents[1] / "Procedures" / "Resources" / "Visuals"

BG = "#F6F8FB"
CARD = "#FFFFFF"
TEXT = "#17212B"
SUBTEXT = "#465363"
LINE = "#5D6D7E"
BLUE = "#1D6FD8"
CYAN = "#2B9BC7"
RED = "#D64545"
ORANGE = "#F08C2B"
GREEN = "#1F9D66"
GOLD = "#E2B93B"
SKIN = "#E9C8B2"
SKIN_DARK = "#D8AE92"
MUSCLE = "#F0D4C3"
BONE = "#E9ECF2"
RIB = "#C9D3DF"
ULTRASOUND_BG = "#17314B"
ULTRASOUND_GRID = "#35526D"
WHITE = "#FFFFFF"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    if not path.exists():
        path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size)


TITLE_FONT = font(50, bold=True)
SUBTITLE_FONT = font(24)
LABEL_FONT = font(27, bold=True)
BODY_FONT = font(24)
SMALL_FONT = font(20)


def new_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, WIDTH - 40, HEIGHT - 40), radius=34, fill=CARD, outline="#D7DFE9", width=3)
    draw.text((86, 82), title, fill=TEXT, font=TITLE_FONT)
    draw.text((86, 148), subtitle, fill=SUBTEXT, font=SUBTITLE_FONT)
    draw.line((84, 196, WIDTH - 84, 196), fill="#DFE6EF", width=3)
    return image, draw


def callout(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int],
    lines: list[str],
    target: tuple[int, int],
    accent: str = BLUE,
    width: int = 330,
) -> None:
    x, y = box
    line_height = 34
    height = 26 + line_height * len(lines)
    rect = (x, y, x + width, y + height)
    draw.rounded_rectangle(rect, radius=20, fill=WHITE, outline=accent, width=3)
    text_y = y + 14
    for index, line in enumerate(lines):
        use_font = LABEL_FONT if index == 0 else SMALL_FONT
        use_fill = TEXT if index == 0 else SUBTEXT
        draw.text((x + 18, text_y), line, fill=use_fill, font=use_font)
        text_y += line_height

    box_edge_x = rect[2] if target[0] > rect[2] else rect[0]
    box_edge_y = min(max(target[1], rect[1] + 24), rect[3] - 24)
    draw.line((box_edge_x, box_edge_y, target[0], target[1]), fill=accent, width=4)
    draw.ellipse((target[0] - 7, target[1] - 7, target[0] + 7, target[1] + 7), fill=accent)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int = 7,
    head: int = 20,
) -> None:
    draw.line((start, end), fill=color, width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux
    p1 = (end[0] - ux * head + px * (head * 0.45), end[1] - uy * head + py * (head * 0.45))
    p2 = (end[0] - ux * head - px * (head * 0.45), end[1] - uy * head - py * (head * 0.45))
    draw.polygon([end, p1, p2], fill=color)


def dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int = 5,
    dash: int = 18,
    gap: int = 14,
) -> None:
    x1, y1 = start
    x2, y2 = end
    length = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    if length == 0:
        return
    for offset in range(0, length, dash + gap):
        seg_start = offset / length
        seg_end = min(offset + dash, length) / length
        sx = x1 + (x2 - x1) * seg_start
        sy = y1 + (y2 - y1) * seg_start
        ex = x1 + (x2 - x1) * seg_end
        ey = y1 + (y2 - y1) * seg_end
        draw.line((sx, sy, ex, ey), fill=color, width=width)


def badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str, fg: str = WHITE) -> None:
    x, y = xy
    text_width = draw.textlength(text, font=SMALL_FONT)
    box_width = int(text_width + 34)
    box = (x, y, x + box_width, y + 42)
    draw.rounded_rectangle(box, radius=18, fill=fill)
    draw.text((x + 16, y + 8), text, font=SMALL_FONT, fill=fg)


def save(image: Image.Image, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUT_DIR / filename, format="PNG", optimize=True)


def draw_cric_membrane() -> None:
    image, draw = new_canvas(
        "Cricothyroid Membrane",
        "Target the soft midline membrane between the thyroid and cricoid cartilages.",
    )

    center_x = 820
    top_y = 280
    thyroid = [
        (center_x - 110, top_y + 40),
        (center_x, top_y),
        (center_x + 110, top_y + 40),
        (center_x + 72, top_y + 170),
        (center_x, top_y + 210),
        (center_x - 72, top_y + 170),
    ]
    draw.polygon(thyroid, fill=SKIN_DARK, outline=LINE)
    draw.rounded_rectangle((center_x - 70, top_y + 214, center_x + 70, top_y + 272), radius=18, fill=CYAN, outline=LINE, width=2)
    draw.rounded_rectangle((center_x - 92, top_y + 286, center_x + 92, top_y + 352), radius=26, fill=SKIN_DARK, outline=LINE, width=2)
    draw.rounded_rectangle((center_x - 52, top_y + 355, center_x + 52, top_y + 530), radius=28, fill=MUSCLE, outline=LINE, width=2)

    dashed_line(draw, (center_x, top_y - 18), (center_x, top_y + 540), ORANGE, width=6)
    draw.line((center_x - 76, top_y + 243, center_x + 76, top_y + 243), fill=RED, width=8)

    badge(draw, (110, 225), "VERTICAL SKIN INCISION", ORANGE)
    arrow(draw, (370, 246), (center_x, top_y + 150), ORANGE, width=6)
    badge(draw, (1110, 225), "HORIZONTAL MEMBRANE INCISION", RED)
    arrow(draw, (1098, 245), (center_x + 18, top_y + 243), RED, width=6)

    callout(draw, (90, 400), ["Thyroid cartilage", "Palpable notch at the top", "Slide down to the soft target"], (center_x - 72, top_y + 88), accent=BLUE)
    callout(draw, (1110, 430), ["Cricothyroid membrane", "Soft midline depression", "Primary target"], (center_x + 74, top_y + 243), accent=CYAN)
    callout(draw, (120, 760), ["Cricoid cartilage", "Firm ring just below", "Stay above this level"], (center_x - 62, top_y + 315), accent=BLUE)
    callout(draw, (1040, 760), ["Midline", "Do not drift laterally", "Lateral deviation risks vessels"], (center_x, top_y + 405), accent=RED)

    save(image, "cric_membrane.png")


def draw_chest_tube_safe_triangle() -> None:
    image, draw = new_canvas(
        "Chest Tube Safe Triangle",
        "Use the 4th-5th intercostal space near the mid-axillary line and enter above the rib.",
    )

    torso = [
        (710, 255),
        (620, 350),
        (594, 470),
        (618, 610),
        (640, 770),
        (700, 930),
        (912, 930),
        (952, 806),
        (968, 670),
        (980, 560),
        (1015, 470),
        (1060, 412),
        (1090, 330),
        (1010, 250),
    ]
    draw.polygon(torso, fill=SKIN, outline=LINE)
    draw.arc((850, 240, 1080, 430), 210, 332, fill=LINE, width=4)

    pectoralis = [(740, 350), (915, 415), (930, 575)]
    latissimus = [(972, 350), (922, 500), (890, 720)]
    draw.line(pectoralis, fill=BLUE, width=8)
    draw.line(latissimus, fill=CYAN, width=8)
    draw.line((650, 610, 1040, 610), fill=LINE, width=4)
    draw.text((642, 620), "Nipple level / 4th-5th intercostal space", fill=SUBTEXT, font=SMALL_FONT)

    safe_triangle = [(766, 397), (962, 397), (916, 640)]
    draw.polygon(safe_triangle, fill="#A7D8F2", outline=CYAN)
    badge(draw, (630, 292), "SAFE TRIANGLE", CYAN)

    entry = (900, 590)
    draw.ellipse((entry[0] - 16, entry[1] - 16, entry[0] + 16, entry[1] + 16), fill=GREEN, outline=WHITE, width=3)
    arrow(draw, (1110, 550), entry, GREEN, width=7)
    draw.text((1134, 530), "Preferred entry\nabove the rib", fill=TEXT, font=BODY_FONT)

    inset = (1100, 710, 1450, 980)
    draw.rounded_rectangle(inset, radius=28, fill="#F9FBFE", outline="#D0DCE8", width=3)
    draw.text((1130, 738), "Over-the-rib rule", fill=TEXT, font=LABEL_FONT)
    for y in (820, 890):
        draw.rounded_rectangle((1160, y, 1410, y + 28), radius=12, fill=RIB, outline=LINE)
        draw.line((1160, y + 28, 1410, y + 28), fill=RED, width=7)
    arrow(draw, (1260, 806), (1260, 760), GREEN, width=7)
    draw.text((1130, 930), "Neurovascular bundle runs\nalong the inferior rib margin.", fill=SUBTEXT, font=SMALL_FONT)

    callout(draw, (78, 330), ["Pectoralis major", "Anterior border", "Forms the front edge"], (815, 395), accent=BLUE)
    callout(draw, (68, 670), ["Latissimus dorsi", "Posterior border", "Forms the back edge"], (935, 436), accent=CYAN)
    callout(draw, (90, 900), ["Insertion zone", "Aim in the triangle", "Stay above the rib"], entry, accent=GREEN)

    save(image, "chest_tube_safe_triangle.png")


def draw_ij_probe_orientation() -> None:
    image, draw = new_canvas(
        "IJ Ultrasound Probe Orientation",
        "Short-axis view: the IJ is lateral and compressible; the carotid is deeper and pulsatile.",
    )

    panel = (460, 280, 1180, 860)
    draw.rounded_rectangle(panel, radius=34, fill=ULTRASOUND_BG, outline="#234A68", width=4)
    for x in range(panel[0] + 50, panel[2], 80):
        draw.line((x, panel[1] + 24, x, panel[3] - 24), fill=ULTRASOUND_GRID, width=2)
    for y in range(panel[1] + 40, panel[3], 80):
        draw.line((panel[0] + 24, y, panel[2] - 24, y), fill=ULTRASOUND_GRID, width=2)

    skin_y = 360
    draw.rounded_rectangle((560, skin_y, 1080, skin_y + 28), radius=10, fill=SKIN_DARK, outline=SKIN_DARK)
    draw.rounded_rectangle((610, 430, 850, 570), radius=70, fill="#4FC1F0", outline=WHITE, width=4)
    draw.ellipse((895, 440, 1045, 590), fill="#D9534F", outline=WHITE, width=4)
    draw.text((678, 483), "IJ", fill=ULTRASOUND_BG, font=LABEL_FONT)
    draw.text((923, 492), "CA", fill=WHITE, font=LABEL_FONT)

    draw.rounded_rectangle((615, 290, 1035, 338), radius=18, fill="#CDD7E2", outline=LINE, width=3)
    draw.line((825, 286, 825, 220), fill=LINE, width=5)
    draw.polygon([(825, 208), (812, 228), (838, 228)], fill=LINE)
    draw.text((650, 302), "Probe marker toward patient's right", fill=TEXT, font=SMALL_FONT)

    draw.ellipse((620, 445, 840, 555), outline=WHITE, width=5)
    draw.line((612, 500, 848, 500), fill=WHITE, width=4)
    draw.text((540, 894), "Needle path toward the IJ lumen", fill=TEXT, font=BODY_FONT)
    arrow(draw, (560, 870), (660, 618), ORANGE, width=7)

    callout(draw, (90, 350), ["Internal jugular vein", "Lateral and superficial", "Compressible under probe"], (610, 498), accent=CYAN)
    callout(draw, (1100, 380), ["Carotid artery", "Deeper and round", "Pulsatile / non-compressible"], (1046, 515), accent=RED)
    callout(draw, (88, 720), ["Compression check", "Vein should flatten", "Artery should stay open"], (732, 575), accent=BLUE)
    callout(draw, (1090, 725), ["Needle target", "Watch the tip enter the vein", "Do not advance blind"], (664, 616), accent=ORANGE, width=360)

    badge(draw, (118, 240), "PATIENT RIGHT", BLUE)
    save(image, "ij_probe_orientation.png")


def draw_needle_decompression_landmarks() -> None:
    image, draw = new_canvas(
        "Needle Decompression Landmarks",
        "Two accepted sites: 2nd intercostal midclavicular or 4th-5th intercostal anterior axillary.",
    )

    torso = [
        (710, 255),
        (615, 335),
        (586, 500),
        (616, 706),
        (700, 938),
        (904, 938),
        (980, 720),
        (1000, 510),
        (1060, 340),
        (972, 255),
    ]
    draw.polygon(torso, fill=SKIN, outline=LINE)
    draw.line((800, 256, 800, 938), fill="#B8C5D3", width=4)
    draw.line((740, 255, 740, 938), fill="#E4B7A8", width=3)
    draw.line((860, 255, 860, 938), fill="#E4B7A8", width=3)

    for y in (372, 434, 496, 558, 620, 682):
        draw.arc((640, y, 962, y + 90), 192, 348, fill=RIB, width=5)

    internal_mammary_x = 714
    draw.rectangle((internal_mammary_x, 310, internal_mammary_x + 22, 918), fill="#F8C3C3", outline="#E59898")
    draw.text((650, 946), "Internal mammary danger zone", fill=RED, font=SMALL_FONT)

    anterior_site = (746, 430)
    lateral_site = (975, 620)
    draw.ellipse((anterior_site[0] - 14, anterior_site[1] - 14, anterior_site[0] + 14, anterior_site[1] + 14), fill=ORANGE, outline=WHITE, width=3)
    draw.ellipse((lateral_site[0] - 14, lateral_site[1] - 14, lateral_site[0] + 14, lateral_site[1] + 14), fill=GREEN, outline=WHITE, width=3)
    arrow(draw, (1120, 620), lateral_site, GREEN, width=7)
    arrow(draw, (1105, 408), anterior_site, ORANGE, width=7)
    draw.text((1135, 594), "4th-5th ICS\nAnterior axillary line\nPreferred lateral site", fill=TEXT, font=BODY_FONT)
    draw.text((1120, 358), "2nd ICS\nMidclavicular line", fill=TEXT, font=BODY_FONT)

    callout(draw, (82, 310), ["Anterior option", "2nd intercostal space", "Stay at the midclavicular line"], anterior_site, accent=ORANGE)
    callout(draw, (82, 650), ["Lateral option", "4th-5th intercostal space", "Preferred in larger body habitus"], lateral_site, accent=GREEN)
    callout(draw, (1090, 835), ["Over-the-rib rule", "Enter above the rib", "Inferior margin holds the bundle"], (968, 662), accent=BLUE, width=360)
    callout(draw, (1115, 235), ["Do not go too medial", "Internal mammary artery", "Too low risks abdominal contents"], (726, 520), accent=RED, width=380)

    save(image, "needle_decompression_landmarks.png")


def draw_lp_position_landmark() -> None:
    image, draw = new_canvas(
        "Lumbar Puncture Landmarks",
        "Use Tuffier's line to find L4, then target the L3-L4 or L4-L5 interspace below the conus.",
    )

    pelvis = [(650, 745), (590, 905), (730, 990), (868, 990), (1010, 905), (950, 745)]
    draw.polygon(pelvis, fill=BONE, outline=LINE)
    draw.ellipse((690, 320, 910, 1040), outline=SKIN_DARK, width=6)
    draw.line((800, 325, 800, 998), fill="#AAB7C4", width=4)

    vertebra_y = [410, 470, 530, 590, 650, 710, 770]
    labels = ["L1", "L2", "L3", "L4", "L5", "S1", "S2"]
    for y, label in zip(vertebra_y, labels):
        draw.rounded_rectangle((760, y, 840, y + 40), radius=14, fill="#D7DEE8", outline=LINE, width=2)
        draw.text((875, y + 6), label, fill=SUBTEXT, font=SMALL_FONT)

    tuffier_y = 610
    dashed_line(draw, (570, tuffier_y, ), (1030, tuffier_y), BLUE, width=6)
    draw.text((1060, 596), "Tuffier's line crosses\nnear the L4 spinous process", fill=TEXT, font=BODY_FONT)

    target_band = (742, 550, 858, 690)
    draw.rounded_rectangle(target_band, radius=18, outline=GREEN, width=6)
    draw.text((610, 990), "Target interspaces: L3-L4 or L4-L5", fill=GREEN, font=BODY_FONT)

    needle_start = (1140, 560)
    needle_end = (848, 615)
    arrow(draw, needle_start, needle_end, ORANGE, width=8)
    draw.text((1152, 512), "Slight cephalad angle\nfor the midline approach", fill=TEXT, font=BODY_FONT)

    callout(draw, (82, 340), ["Conus ends above this zone", "Do not insert above L3", "Stay below the conus"], (840, 428), accent=RED, width=360)
    callout(draw, (84, 690), ["Iliac crest line", "Use both crests to find L4", "Then drop one space below if needed"], (642, tuffier_y), accent=BLUE, width=360)
    callout(draw, (1088, 760), ["Needle target", "Aim midline between spinous processes", "Withdraw and redirect if bone is hit"], (802, 618), accent=ORANGE, width=385)

    save(image, "lp_position_landmark.png")


def main() -> None:
    draw_cric_membrane()
    draw_chest_tube_safe_triangle()
    draw_ij_probe_orientation()
    draw_needle_decompression_landmarks()
    draw_lp_position_landmark()
    print(f"Wrote visual assets to {OUT_DIR}")


if __name__ == "__main__":
    main()
