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

# Brow (y 285) to the vertex, from the temporal line and the coronal plane
# through the ear to the supratrochlear strip; the lateral upper eyelid to the
# lash line (audit 2026-10-15: the temple is not supraorbital).
SUPRAORBITAL = [(846, 148), (870, 140), (877, 168), (896, 200), (910, 250), (915, 285), (898, 290), (898, 326),
                (862, 326), (862, 292), (850, 285), (840, 270), (830, 240), (822, 205), (818, 172)]
# Medial forehead strip (about 2 cm), the root of the nose and the medial lid.
SUPRATROCHLEAR = [(858, 140), (877, 168), (896, 200), (910, 250), (915, 285), (898, 290), (898, 326), (918, 326),
                  (934, 352), (944, 352), (947, 300), (947, 285), (942, 250), (928, 200), (909, 168)]

ZONES = [
    Zone("supraorbital-skin", "teal", SUPRAORBITAL, clip="right-face", feather=6),
    Zone("supratrochlear-skin", "violet", SUPRATROCHLEAR, clip="right-face", feather=3.5),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
