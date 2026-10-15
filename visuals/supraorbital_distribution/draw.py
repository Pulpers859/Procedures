"""Supraorbital (and supratrochlear) nerve block - expected distribution, head view.

The supraorbital nerve: the forehead and the anterior scalp up to the vertex
and the upper eyelid, from the lateral forehead to the supratrochlear strip;
the supratrochlear nerve (the steps sweep medially toward the bridge of the
nose): the medial forehead strip, the root of the nose and the medial upper
eyelid. One side, to the midline. The temple and the rest of the face stay grey.

Run: python3 visuals/supraorbital_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "supraorbital_distribution"
VIEW = "head"
CLIPS = {"right-face": R.RIGHT_FACE}

# Brow (y 285) to the vertex, from the coronal plane through the ear (x 790)
# to the supratrochlear strip (x 915); upper eyelid to the lash line.
SUPRAORBITAL = [(790, 150), (820, 140), (900, 142), (915, 150), (915, 282), (900, 290), (920, 292), (924, 326),
                (788, 326), (786, 290), (800, 284), (788, 260), (786, 200)]
# Medial forehead strip (about 2 cm), the root of the nose and the medial lid.
SUPRATROCHLEAR = [(915, 160), (946, 168), (948, 300), (950, 350), (934, 352), (922, 326), (912, 290), (912, 200)]

ZONES = [
    Zone("supraorbital-skin", "teal", SUPRAORBITAL, clip="right-face", feather=6),
    Zone("supratrochlear-skin", "violet", SUPRATROCHLEAR, clip="right-face", feather=3.5),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
