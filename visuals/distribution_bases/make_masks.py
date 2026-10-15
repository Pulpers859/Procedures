"""Trace a distribution base painting into the masks the tint is clipped to.

Writes, next to `<view>/base.jpg`:
- mask_bone.png: white where the painting shows bone (warm ivory or its grey
  shading) inside the skeleton's part of the plate;
- mask_body.png: white where it shows the grey body in the rest.

Same method as `ficb_distribution/make_masks.py` (audited 2026-10-15): the
background is a soft vertical gradient estimated per row from the plate's
outer columns; the masks are closed, then eroded so they sit inside the
painted outline (no halo).

Run: python3 visuals/distribution_bases/make_masks.py <view> [<view> ...]
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
# Base px row below which a floor shadow can sit under the skeleton.
FLOOR = {"front": 820, "back": 820, "hand": 835, "foot": 855}
# Largest enclosed hole (px) filled in each mask: painted highlights, never
# the gaps between ribs or fingers.
HOLE = {"body": 10000, "bone": 150}
# Base px column where the skeleton's part of the plate ends.
SPLIT = {"front": 600, "back": 600, "head": 568, "hand": 384, "foot": 305, "side": 600}


def fill_small_holes(m, limit):
    holes, n = ndimage.label(~m)
    sizes = ndimage.sum(~m, holes, range(1, n + 1))
    edge = set(np.unique(np.concatenate([holes[0], holes[-1], holes[:, 0], holes[:, -1]])))
    out = m.copy()
    for i, size in enumerate(sizes, start=1):
        if size <= limit and i not in edge:
            out[holes == i] = True
    return out


def masks(view: str) -> None:
    img = np.asarray(Image.open(HERE / view / "base.jpg").convert("RGB")).astype(float)
    h, w, _ = img.shape
    edge = np.concatenate([img[:, :40], img[:, -40:]], axis=1)
    bg = np.median(edge, axis=1)[:, None, :]
    diff = np.abs(img - bg).sum(axis=2)
    warmth = img[..., 0] - img[..., 2]
    bg_warmth = bg[..., 0] - bg[..., 2]
    cols = np.arange(w)[None, :]
    split = SPLIT[view]

    bone = ((diff > 22) | (warmth - bg_warmth > 9)) & (cols < split)
    # The floor shadow under the feet is grey, not ivory: below the ankles
    # keep only warm pixels or clear line work.
    rows = np.arange(h)[:, None]
    floor = FLOOR.get(view)
    if floor:
        bone &= (rows < floor) | (warmth - bg_warmth > 6) | (diff > 70)
    body = (diff > 60) & (cols >= split) & (img.std(axis=2) < 9)   # 60: the floor shadow stays out

    for name, m in (("mask_bone.png", bone), ("mask_body.png", body)):
        m = fill_small_holes(m, HOLE["bone" if "bone" in name else "body"])
        im = Image.fromarray((m * 255).astype("uint8"))
        im = (im.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(3))
              .filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.8)))
        im.save(HERE / view / name, optimize=True)
        print(HERE / view / name, round(m.mean() * 100, 1), "% of plate")


if __name__ == "__main__":
    for v in sys.argv[1:]:
        masks(v)
