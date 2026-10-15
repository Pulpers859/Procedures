"""Supraclavicular block - expected distribution, front view.

The trunks and divisions above the first rib: the whole arm from the deltoid
to the fingertips, and in bone the humerus below the head, the
radius, ulna and the hand. Grey: the shoulder joint, the cape of the shoulder (supraclavicular
nerves, C3-C4) and the axilla and upper medial arm (intercostobrachial, T2),
which run outside the plexus sheath.

Run: python3 visuals/supraclavicular_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import front_regions as R  # noqa: E402,F401

ASSET_ID = "supraclavicular_distribution"
VIEW = "front"
CLIPS = {"right-arm": R.RIGHT_ARM}

# Below the cape (y about 238) to the fingertips, with a notch for the upper
# medial arm beside the axilla.
ARM_SKIN = [(700, 238), (738, 234), (758, 238), (764, 246), (766, 262), (762, 276), (760, 286), (756, 300),
            (758, 318), (764, 334), (772, 346), (776, 362), (770, 400), (760, 440), (752, 480), (756, 572),
            (664, 572), (664, 470), (688, 400), (698, 300)]

ZONES = [
    Zone("plexus-skin", "teal", ARM_SKIN, clip="right-arm"),
    Zone("plexus-bone", "teal", R.HUMERUS_SHAFT, layer="bone", feather=0, tension=0.3, extra=[R.FOREARM_HAND]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
