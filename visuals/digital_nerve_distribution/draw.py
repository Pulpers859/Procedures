"""Digital nerve block (one finger, shown on the middle finger) - expected distribution, hand views.

The two palmar and two dorsal digital nerves at the base of the finger: the
whole finger distal to the web, front and back including the nail bed; in
bone, the phalanges. The same for any finger.

Run: python3 visuals/digital_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import hand_regions as R  # noqa: E402,F401

ASSET_ID = "digital_nerve_distribution"
VIEW = "hand"
CLIPS = {"palm": R.PALM, "dorsum": R.DORSUM}

FINGER_PALM = [(554, 112), (604, 112), (606, 380), (552, 380)]
FINGER_DORSUM = [(996, 108), (1044, 108), (1046, 396), (994, 396)]

ZONES = [
    Zone("finger-palm", "teal", FINGER_PALM, clip="palm", feather=3, tension=0.2),
    Zone("finger-dorsum", "teal", FINGER_DORSUM, clip="dorsum", feather=3, tension=0.2),
    Zone("finger-bone", "teal", R.MIDDLE_PHALANGES, layer="bone", feather=1.5, tension=0.2),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
