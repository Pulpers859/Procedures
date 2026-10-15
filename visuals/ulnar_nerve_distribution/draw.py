"""Ulnar nerve block (forearm) - expected distribution, hand views.

The ulnar nerve with its dorsal and palmar cutaneous branches: the ulnar third
of the palm and of the back of the hand, the little finger and the ulnar half
of the ring finger on both sides. In bone, the fifth metacarpal and the
phalanges of the little finger (the boxer's fracture).

Run: python3 visuals/ulnar_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import hand_regions as R  # noqa: E402,F401

ASSET_ID = "ulnar_nerve_distribution"
VIEW = "hand"
CLIPS = {"palm": R.PALM, "dorsum": R.DORSUM}

ULNAR_PALM = [(466, 236), (512, 236), (514, 166), (536, 166), (536, 380), (556, 386), (556, 520), (560, 644),
              (498, 646), (480, 600), (470, 500), (464, 400)]
ULNAR_DORSUM = [(1100, 238), (1138, 238), (1140, 400), (1144, 520), (1128, 600), (1100, 640), (1066, 640),
                (1066, 520), (1064, 400), (1070, 160), (1092, 160), (1096, 300)]

ZONES = [
    Zone("ulnar-palm", "teal", ULNAR_PALM, clip="palm", feather=5),
    Zone("ulnar-dorsum", "teal", ULNAR_DORSUM, clip="dorsum", feather=5),
    Zone("ulnar-bone", "teal", R.LITTLE_RAY, layer="bone", feather=1.5, tension=0.2),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
