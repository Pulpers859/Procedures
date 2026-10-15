"""Radial nerve block (superficial radial, in the forearm) - expected distribution, hand views.

The superficial radial nerve: the radial two thirds of the back of the hand,
the back of the thumb, and the back of the index, middle and radial half of
the ring finger as far as the proximal interphalangeal joint. Nothing on the
palm.

Run: python3 visuals/radial_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import hand_regions as R  # noqa: E402,F401

ASSET_ID = "radial_nerve_distribution"
VIEW = "hand"
CLIPS = {"dorsum": R.DORSUM}

RADIAL_DORSUM = [(856, 376), (900, 384), (940, 470), (944, 390), (948, 300), (996, 300), (1000, 290), (1038, 290),
                 (1046, 322), (1068, 322), (1072, 420), (1076, 520), (1080, 620), (944, 640), (940, 630),
                 (900, 570), (880, 520)]

ZONES = [
    Zone("radial-dorsum", "teal", RADIAL_DORSUM, clip="dorsum", feather=5),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
