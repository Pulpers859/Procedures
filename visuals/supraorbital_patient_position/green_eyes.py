"""Recolour the two irises of a photo to green, keeping texture and light."""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
irises = [((389, 593), 50), ((953, 588), 50)]
im = Image.open(src).convert('RGB')
hsv = np.array(im.convert('HSV')).astype(np.float32)
h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
H, W = s.shape
yy, xx = np.mgrid[0:H, 0:W]
mask = np.zeros((H, W), np.float32)
for (cx, cy), r in irises:
    d = np.hypot(xx - cx, yy - cy)
    mask = np.maximum(mask, np.clip((r - d) / 6, 0, 1))
# Only the coloured iris: skip the dark pupil, white catchlights, sclera and lashes.
colour = (np.clip((s - 0.15) / 0.10, 0, 1) * np.clip((0.60 - v) / 0.08, 0, 1) * np.clip((v - 0.10) / 0.06, 0, 1)
          * np.clip((h - 18) / 6, 0, 1) * np.clip((70 - h) / 8, 0, 1))
m = mask * colour
m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
new_h = 88 + (h - 34) * 0.35
new_s = np.clip(s * 0.85, 0, 1)
hh = h * (1 - m) + new_h * m
ss = s * (1 - m) + new_s * m
res = np.stack([np.mod(hh, 360) * 255 / 360, ss * 255, v * 255], -1).astype(np.uint8)
Image.fromarray(res, 'HSV').convert('RGB').save(out, quality=95)
