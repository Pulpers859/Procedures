"""Mental nerve block - expected distribution, head view.

The mental nerve: the skin of the lower lip and the chin on one side, to the
midline. No bone and no teeth are shaded.

Run: python3 visuals/mental_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "mental_distribution"
VIEW = "head"
CLIPS = {"right-lower-face": R.RIGHT_LOWER_FACE}

MENTAL_SKIN = [(880, 448), (950, 448), (952, 470), (948, 510), (900, 516), (882, 490)]

ZONES = [
    Zone("mental-skin", "teal", MENTAL_SKIN, clip="right-lower-face", feather=4),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
