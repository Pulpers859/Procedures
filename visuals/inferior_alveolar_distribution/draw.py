"""Inferior alveolar nerve block - expected distribution, head view.

The inferior alveolar nerve and its mental branch: all the lower teeth on one
side and the body of the mandible; the skin of the lower lip and the chin.
The tongue (lingual nerve) is not visible on this figure.

Run: python3 visuals/inferior_alveolar_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "inferior_alveolar_distribution"
VIEW = "head"
CLIPS = {"right-lower-face": R.RIGHT_LOWER_FACE}

MENTAL_SKIN = [(880, 448), (950, 448), (952, 470), (948, 510), (900, 516), (882, 490)]

ZONES = [
    Zone("mental-skin", "teal", MENTAL_SKIN, clip="right-lower-face", feather=4),
    Zone("mandible-bone", "teal", R.MANDIBLE_BODY, layer="bone", feather=1.5, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
