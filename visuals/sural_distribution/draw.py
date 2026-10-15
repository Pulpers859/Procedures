"""Sural nerve block - expected distribution, foot views.

The sural nerve: the lateral border of the foot, the little toe's lateral side,
the lateral heel and the skin around the lateral malleolus. Seen on the top
of the foot (lateral border strip) and from the outer side. The sole stays
grey (lateral plantar nerve), as does the dorsum (superficial peroneal).

Run: python3 visuals/sural_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import foot_regions as R  # noqa: E402,F401

ASSET_ID = "sural_distribution"
VIEW = "foot"
CLIPS = {"top": R.TOP, "lateral": R.LATERAL}

# Top view: the lateral border strip from the ankle to the little toe.
SURAL_TOP = [(498, 596), (524, 596), (536, 480), (548, 380), (560, 300), (562, 244), (534, 244), (524, 300),
             (514, 400), (506, 500)]
# Outer side: below the malleolus, the lateral foot and the lateral heel,
# leaving a band along the dorsum (superficial peroneal) and the sole.
SURAL_LATERAL = [(858, 604), (900, 590), (950, 596), (984, 622), (1030, 664), (1096, 704), (1146, 726), (1160, 744),
                 (1150, 758), (1090, 770), (960, 776), (884, 770), (854, 736), (850, 660)]

ZONES = [
    Zone("sural-top", "teal", SURAL_TOP, clip="top", feather=3),
    Zone("sural-lateral", "teal", SURAL_LATERAL, clip="lateral", feather=3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
