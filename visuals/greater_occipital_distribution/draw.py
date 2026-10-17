"""Greater occipital (suboccipital) nerve block - expected distribution, back of the head.

The greater occipital nerve: the back of the scalp on one side, from the
occiput (superior nuchal line) up toward the vertex, from the midline out to
about the line above the ear. The area behind the ear (lesser occipital) and
the back of the neck (third occipital, cervical) stay grey. No bone is shaded.
Seen from behind: the patient's right is on the image right.

Run: python3 visuals/greater_occipital_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_back_regions as R  # noqa: E402,F401

ASSET_ID = "greater_occipital_distribution"
VIEW = "head_back"
CLIPS = {"right-scalp": R.RIGHT_SCALP}

# Midline (x 880) to just short of the ear region (x about 1000), from the
# occiput (y about 425, above the neck) up to the crown; graded toward the vertex.
GON_SKIN = [(878, 100), (925, 104), (965, 128), (992, 180), (998, 250), (995, 330), (982, 385), (958, 412),
            (922, 426), (878, 428)]

ZONES = [
    Zone("gon-skin", "teal", GON_SKIN, clip="right-scalp", feather=8, fade=(940, 92, 940, 165)),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
