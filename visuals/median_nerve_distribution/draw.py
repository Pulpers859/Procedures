"""Median nerve block (forearm) - expected distribution, hand views.

The median nerve with its palmar cutaneous branch: the radial two thirds of
the palm, the thenar eminence, the palmar thumb, index, middle and the radial
half of the ring finger, and the back of the distal index, middle and radial
ring finger (nail beds). In bone, the phalanges of the thumb, index and
middle fingers.

Run: python3 visuals/median_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import hand_regions as R  # noqa: E402,F401

ASSET_ID = "median_nerve_distribution"
VIEW = "hand"
CLIPS = {"palm": R.PALM, "dorsum": R.DORSUM}

MEDIAN_PALM = [(554, 112), (648, 112), (650, 372), (700, 378), (750, 376), (750, 440), (708, 560), (660, 600),
               (606, 644), (562, 644), (554, 520)]
RING_RADIAL = [(534, 164), (556, 164), (557, 382), (534, 382)]
INDEX_TIP = [(948, 150), (998, 150), (998, 228), (948, 228)]
MIDDLE_TIP = [(1000, 114), (1042, 114), (1042, 202), (1000, 202)]
RING_TIP = [(1046, 158), (1070, 158), (1070, 234), (1046, 234)]

ZONES = [
    Zone("median-palm", "teal", MEDIAN_PALM, clip="palm", feather=5, extra=[RING_RADIAL]),
    Zone("median-dorsum-tips", "teal", INDEX_TIP, clip="dorsum", feather=2.5, tension=0.2,
         extra=[MIDDLE_TIP, RING_TIP]),
    Zone("median-bone", "teal", R.THUMB_PHALANGES, layer="bone", feather=1.5, tension=0.2,
         extra=[R.INDEX_PHALANGES, R.MIDDLE_PHALANGES]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
