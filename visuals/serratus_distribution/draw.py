"""Serratus anterior plane block - expected distribution, side view.

An injection at the mid-axillary line over the fifth rib spreads in the plane
over or under the serratus anterior: the lateral cutaneous branches of the
intercostal nerves, T2 to T9, the skin of the lateral chest wall from the
armpit to the costal margin; in bone, the ribs beneath. The abdomen below the
ribs stays grey.

Run: python3 visuals/serratus_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import side_regions as R  # noqa: E402,F401

ASSET_ID = "serratus_distribution"
VIEW = "side"
CLIPS = {"right-chest": R.RIGHT_CHEST}

# From the armpit (y 326) to the costal margin (T9, sloping up toward the front),
# the whole lateral chest wall as seen from the side.
CHEST_SKIN = [(796, 328), (840, 316), (900, 306), (942, 314), (990, 346), (992, 498), (900, 514), (740, 540),
              (740, 336), (790, 334)]

ZONES = [
    Zone("serratus-skin", "teal", CHEST_SKIN, clip="right-chest", feather=6),
    Zone("serratus-bone", "teal", R.RIBS_ALL, layer="bone", feather=2.0, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
