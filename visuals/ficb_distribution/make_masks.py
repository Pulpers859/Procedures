"""Trace the figures on base.jpg into masks for the distribution tint.

Writes, next to this file:
- mask_bone.png: white where the painting shows bone (warm ivory or its grey
  shading) inside the skeleton's half of the plate;
- mask_body.png: white where it shows the grey body in the other half.

The tint in draw.py is clipped to these, so a territory follows the painted
contours exactly instead of a hand-drawn outline. The background is a soft
vertical gradient, estimated per row from the plate's outer columns.

Run: python3 visuals/ficb_distribution/make_masks.py
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SPLIT = 600                      # base px: skeleton left of this column, body right


def main() -> int:
    img = np.asarray(Image.open(HERE / "base.jpg").convert("RGB")).astype(float)
    h, w, _ = img.shape
    edge = np.concatenate([img[:, :40], img[:, -40:]], axis=1)
    bg = np.median(edge, axis=1)[:, None, :]
    diff = np.abs(img - bg).sum(axis=2)
    warmth = img[..., 0] - img[..., 2]
    bg_warmth = (bg[..., 0] - bg[..., 2])
    cols = np.arange(w)[None, :]

    bone = ((diff > 22) | (warmth - bg_warmth > 9)) & (cols < SPLIT)
    body = (diff > 60) & (cols >= SPLIT) & (img.std(axis=2) < 9)   # 60: the floor shadow stays out

    for name, m in (("mask_bone.png", bone), ("mask_body.png", body)):
        im = Image.fromarray((m * 255).astype("uint8"))
        # Close small gaps, then erode so the mask sits inside the painted outline (audit: no halo).
        im = im.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
        im.save(HERE / name, optimize=True)
        print(HERE / name, round(m.mean() * 100, 1), "% of plate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
