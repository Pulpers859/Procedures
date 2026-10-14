"""Cut the photographed glove finger out of SRC and lay it on CLEAN at a new
pose: scaled by S, rotated so its axis rises ANGLE degrees toward the tip,
its tip at TIP (base px). Writes OUT and prints the finger outline (base px)."""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, clean, out = sys.argv[1:4]
S, ANGLE = float(sys.argv[4]), float(sys.argv[5])
TIP = (float(sys.argv[6]), float(sys.argv[7]))

# Traced finger outline on SRC, base px (from the draw.py trace, mm -> base).
mm = [(-90, -5.4), (-75, -5.1), (-52.8, -3.7), (-30.6, -2.0), (-19.4, -0.3), (-15.0, 1.9), (-13.1, 6.3),
      (-14.4, 10.8), (-19.4, 12.1), (-41.7, 14.1), (-75, 13.8), (-90, 13.8)]
poly = [((900 + 12 * x) * 0.75, (540 + 12 * y) * 0.75) for x, y in mm]
src_tip = (poly[6][0] + 2, poly[6][1])               # front point of the fingertip
src_angle = 3.0                                       # the painted finger rises ~3 deg to the tip

im = Image.open(src).convert('RGB')
W, H = im.size
m = Image.new('L', (W, H), 0)
ImageDraw.Draw(m).polygon([(x, y) for x, y in poly], fill=255)
a = np.array(im.convert('HSV')).astype(np.float32) / 255
glove = (np.clip((0.22 - a[..., 1]) / 0.08, 0, 1) * np.clip((a[..., 2] - 0.55) / 0.1, 0, 1) * 255).astype(np.uint8)
mask = np.minimum(np.array(m.filter(ImageFilter.MaxFilter(9))), glove)
mask = Image.fromarray(mask).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.3))
rgba = im.copy(); rgba.putalpha(mask)

# Affine: new = R*S*(old - src_tip) + TIP; PIL wants the inverse map.
th = math.radians(ANGLE - src_angle)                   # extra rise toward the tip (image y is down)
c, s = math.cos(th), math.sin(th)
def fwd(p):
    dx, dy = p[0] - src_tip[0], p[1] - src_tip[1]
    return (TIP[0] + S * (c * dx + s * dy), TIP[1] + S * (-s * dx + c * dy))
# inverse
ic, is_ = c / S, s / S
inv = (ic, -is_, src_tip[0] - ic * TIP[0] + is_ * TIP[1],
       is_, ic, src_tip[1] - is_ * TIP[0] - ic * TIP[1])
placed = rgba.transform((W, H), Image.AFFINE, inv, resample=Image.BICUBIC)

base = Image.open(clean).convert('RGB')
alpha = placed.split()[3]
shadow = alpha.filter(ImageFilter.GaussianBlur(9))
shadow = Image.fromarray((np.array(shadow).astype(np.float32) * 0.38).astype(np.uint8))
sh = Image.new('L', (W, H), 0); sh.paste(shadow, (5, 9))
dark = Image.new('RGB', (W, H), (60, 38, 30))
base = Image.composite(dark, base, sh)
base.paste(placed.convert('RGB'), (0, 0), alpha)
base.save(out, quality=95)
print(json.dumps([[round(v, 1) for v in fwd(p)] for p in poly]))
