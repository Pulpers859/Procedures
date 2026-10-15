"""Infraorbital nerve block - expected distribution, head view.

The infraorbital nerve: the lower eyelid, the medial cheek, the side of the
nose and the upper lip on one side; in bone, the anterior wall of the maxilla
around the foramen and the upper teeth from the second premolar to the central
incisor (anterior and middle superior alveolar branches). The molars and the
lateral cheek stay grey.

Run: python3 visuals/infraorbital_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "infraorbital_distribution"
VIEW = "head"
CLIPS = {"right-lower-face": R.RIGHT_LOWER_FACE}

# Lower eyelid (below the lash line, y 326), medial cheek (not the lateral
# cheek) to the corner of the mouth, side of the nose, upper lip to the midline.
INFRAORBITAL_SKIN = [(850, 334), (918, 332), (936, 350), (950, 390), (950, 438), (906, 438), (890, 436), (870, 420),
                     (850, 380)]

ZONES = [
    Zone("infraorbital-skin", "teal", INFRAORBITAL_SKIN, clip="right-lower-face", feather=4),
    Zone("infraorbital-bone", "teal", R.MAXILLA, layer="bone", feather=1.5, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
