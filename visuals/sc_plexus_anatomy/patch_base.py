"""Pixel edits for sc_plexus_anatomy base.jpg (recorded in provenance.pixelEdits).

1. Composite from the earlier painting (paint5) over the final repair (paint6): the bony peak
   and tubercle wings (Gemini invented them), the external jugular on the SCM, the stray vessel
   painted in the left fat.
2. The cervical fascia band repainted as a white two-layered fascial sheet (owner: no
   subcutaneous-looking fat in the plane), leaving the four painted nerves untouched.
"""
import importlib.util, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

D = Path("tmp/visual-drafts/antigravity/sc_plexus_anatomy")
spec = importlib.util.spec_from_file_location("lay", "visuals/sc_plexus_anatomy/draw.py")
lay = importlib.util.module_from_spec(spec); spec.loader.exec_module(lay)
S = 0.75; OY = (1200 - 896 / S) / 2


def base_pt(mm):
    x, y = lay.c(mm)
    return (x * S, (y - OY) * S)


a = Image.open(D / "paint5_scm_partfat.jpg").convert("RGB")
b = Image.open(D / "paint6_bone.jpg").convert("RGB")
m = Image.new("L", b.size, 0); d = ImageDraw.Draw(m)
d.rectangle((486, 318, 814, 582), fill=255)
d.rectangle((700, 582, 790, 606), fill=255)
d.ellipse((842 - 64, 134 - 26, 842 + 64, 134 + 26), fill=255)
d.rectangle((0, 150, 380, 224), fill=255)
img = Image.composite(a, b, m.filter(ImageFilter.GaussianBlur(5)))

# Fascia sheet.
xs = [lay.L + (lay.R - lay.L) * i / 300 for i in range(301)]


def line(dy):
    return [base_pt((x, lay.plane_y(x) + dy)) for x in xs]


band = line(-lay.HALF - 0.08) + list(reversed(line(lay.HALF + 0.08)))
sheet = Image.new("RGB", img.size, (232, 226, 216))
sd = ImageDraw.Draw(sheet)
for dy, col, w in [(-0.55, (214, 206, 194), 2), (-0.2, (244, 240, 233), 2), (0.15, (210, 202, 190), 2),
                   (0.5, (240, 236, 228), 2)]:
    sd.line(line(dy), fill=col, width=w)
for dy in (-lay.HALF, lay.HALF):
    sd.line(line(dy), fill=(252, 252, 250), width=4)
sheet = sheet.filter(ImageFilter.GaussianBlur(0.8))
mask = Image.new("L", img.size, 0); md = ImageDraw.Draw(mask)
md.polygon(band, fill=255)
for (ct, r) in lay.NERVES:
    cx, cy = base_pt(ct); rr = r * lay.PX_MM * S + 3
    md.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=0)
img = Image.composite(sheet, img, mask.filter(ImageFilter.GaussianBlur(1.2)))
img.save("visuals/sc_plexus_anatomy/base.jpg", quality=92)
img.crop((150, 180, 950, 420)).resize((1600, 480)).save(D / "fascia_crop.png")
