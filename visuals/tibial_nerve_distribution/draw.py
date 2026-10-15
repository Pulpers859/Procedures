"""Tibial nerve block (posterior tibial, at the ankle) - expected distribution, foot views.

The medial and lateral plantar nerves and the medial calcaneal branch: the
sole of the foot and the plantar surface of all the toes, except the lateral
border strip (sural). The dorsum stays grey.

Run: python3 visuals/tibial_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import foot_regions as R  # noqa: E402,F401

ASSET_ID = "tibial_nerve_distribution"
VIEW = "foot"
CLIPS = {"sole": R.SOLE}

# Sole view (big toe on the image right): the plantar surface from the toe
# tips to the heel, leaving the lateral border strip (image left, below the
# toes) to the sural nerve.
PLANTAR = [(598, 140), (824, 140), (826, 780), (650, 788), (648, 700), (640, 600), (634, 500), (632, 400),
           (632, 316), (600, 310), (596, 240)]

ZONES = [
    Zone("plantar-skin", "teal", PLANTAR, clip="sole", feather=3.5),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
