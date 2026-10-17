"""Move the photographed glove 34 px toward the ear (independent review,
2026-10-17: the fingertip sat about 1.7 cm from the midline; the artery is
about 2.5 cm out). The hand is cut from the first photo by its blue colour
and pasted onto the hand-free repaint of the same photo.

Run: python3 visuals/greater_occipital_patient_position/place_hand.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
DRAFTS = HERE.parents[1] / "tmp" / "visual-drafts" / "antigravity" / "greater_occipital_patient_position"
SHIFT = 34


def main() -> int:
    with_hand = Image.open(DRAFTS / "base_v1.jpg").convert("RGB")
    clean = Image.open(DRAFTS / "greater_occipital_patient_position_nohand.png").convert("RGB").resize(with_hand.size, Image.LANCZOS)
    a = np.asarray(with_hand).astype(int)
    glove = (a[..., 2] > a[..., 0] + 40) & (a[..., 2] > a[..., 1] + 10)
    mask = Image.fromarray((glove * 255).astype("uint8")).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    hand = Image.new("RGB", with_hand.size)
    hand.paste(with_hand, (SHIFT, 0))
    shifted_mask = Image.new("L", with_hand.size)
    shifted_mask.paste(mask, (SHIFT, 0))
    out = Image.composite(hand, clean, shifted_mask)
    out.save(HERE / "base.jpg", quality=92)
    print(HERE / "base.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
