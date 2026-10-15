"""PECS I / II block - expected distribution, side view.

PECS I reaches the pectoral nerves (motor to the pectoral muscles, no skin).
PECS II adds the lateral cutaneous branches of T2-T6 and the intercostobrachial
nerve: the skin of the anterolateral chest wall from the armpit to about the
sixth rib, and the armpit; in bone, the ribs beneath. The abdomen stays grey.

Run: python3 visuals/pecs_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import side_regions as R  # noqa: E402,F401

ASSET_ID = "pecs_distribution"
VIEW = "side"
CLIPS = {"right-chest": R.RIGHT_CHEST, "right-axilla": R.RIGHT_AXILLA}

# Armpit (y 326) to about the sixth rib (y 425).
CHEST_SKIN = [(796, 328), (840, 316), (900, 306), (942, 314), (990, 346), (992, 408), (900, 418), (740, 436),
              (740, 336), (790, 334)]
# The armpit and the inner side of the upper arm next to it.
ARMPIT = [(806, 296), (840, 288), (866, 300), (868, 324), (836, 328), (808, 320)]

ZONES = [
    Zone("pecs-skin", "teal", CHEST_SKIN, clip="right-chest", feather=6),
    Zone("armpit-skin", "violet", ARMPIT, clip="right-axilla", feather=6),
    Zone("pecs-bone", "teal", R.RIBS_UPPER, layer="bone", feather=2.0, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
