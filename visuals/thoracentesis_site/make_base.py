"""Build base.jpg for thoracentesis_site: the clean back plus the rib-section inset.

The back is the owner's Gemini re-pose of the clean ESP back: seated, leaning
forward over a padded bedside table with the arms on a pillow (tmp/visual-drafts/antigravity/thoracentesis_site/, gitignored),
downscaled to 1200 x 896. The inset is a crop of the approved
chest_tube_rib_anatomy painting (skin left, head up): the upper rib with its
bundle, the space, and the lower rib, pasted into the lower left with a white
border. draw.py draws the needle and labels over both.

Run: python3 visuals/thoracentesis_site/make_base.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BACK = ROOT / "tmp/visual-drafts/antigravity/thoracentesis_site/owner2_leaning_1200.jpg"
RIB = ROOT / "visuals/chest_tube_rib_anatomy/base.jpg"
K = 1600 / 1200                       # canvas px per base px
OY = (1200 - 896 * K) / 2

# Inset: canvas rect and the rib plate's canvas region it shows (mm -0.5..39.5 deep, -22..22 head-foot).
INSET = (64, 690, 504, 1174)
RIB_REGION = (100, 160, 900, 1040)


def to_base(x, y):
    return (round(x / K), round((y - OY) / K))


def main() -> int:
    back = Image.open(BACK).convert("RGB")
    rib = Image.open(RIB).convert("RGB")
    r0, r1 = to_base(*RIB_REGION[:2]), to_base(*RIB_REGION[2:])
    i0, i1 = to_base(*INSET[:2]), to_base(*INSET[2:])
    crop = rib.crop((*r0, *r1)).resize((i1[0] - i0[0], i1[1] - i0[1]), Image.LANCZOS)
    shadow = Image.new("L", back.size, 0)
    ImageDraw.Draw(shadow).rectangle((i0[0] + 4, i0[1] + 6, i1[0] + 6, i1[1] + 8), fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    back.paste(Image.new("RGB", back.size, (30, 30, 30)), (0, 0), shadow)
    ImageDraw.Draw(back).rectangle((i0[0] - 3, i0[1] - 3, i1[0] + 2, i1[1] + 2), fill=(248, 246, 240))
    back.paste(crop, i0)
    back.save(HERE / "base.jpg", quality=92)
    print(HERE / "base.jpg", back.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
