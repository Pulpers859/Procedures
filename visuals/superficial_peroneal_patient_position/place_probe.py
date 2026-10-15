"""Build base.jpg for superficial_peroneal_patient_position (recorded in provenance.pixelEdits).

The owner's Gemini photo put the probe about 2 cm above the lateral malleolus
and left the needle outside the skin. Gemini then removed the equipment
(owner2_clean.jpg). This takes the photo's own probe (with its gel) from the
first photo (owner1.jpg), by the difference between the two, and pastes it
100 px higher and 10 px lateral: about 7 cm above the lateral malleolus on
the anterolateral leg (NYSORA: 5-10 cm). The needle and tubing are drawn in
draw.py.

Run from the repo root: python3 visuals/superficial_peroneal_patient_position/place_probe.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter

SRC = Path("tmp/visual-drafts/antigravity/superficial_peroneal_patient_position")   # gitignored source photos
OUT = Path(__file__).with_name("base.jpg")
BOX = (515, 0, 665, 335)          # probe, cable stub and gel in owner1 (excludes the hub at x >= 668)
SHIFT = (-10, -100)

a = Image.open(SRC / "owner1.jpg").convert("RGB")
b = Image.open(SRC / "owner2_clean.jpg").convert("RGB")
d = np.asarray(ImageChops.difference(a, b)).sum(2) > 45
m = np.zeros_like(d)
x0, y0, x1, y1 = BOX
m[y0:y1, x0:x1] = d[y0:y1, x0:x1]
mask = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(3))
mask = mask.filter(ImageFilter.GaussianBlur(1.5))
layer = Image.new("RGB", a.size); layer.paste(a, SHIFT)
shifted = Image.new("L", a.size, 0); shifted.paste(mask, SHIFT)
out = Image.composite(layer, b, shifted)
out.save(OUT, quality=92)
print(OUT, out.size)
