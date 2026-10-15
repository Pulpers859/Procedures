"""Superficial peroneal nerve block - expected distribution, foot views.

The medial and intermediate dorsal cutaneous nerves: the dorsum of the foot
and the dorsal toes, and the skin of the distal anterolateral leg. The first
web space (deep peroneal) and the lateral border (sural) stay grey.

Run: python3 visuals/superficial_peroneal_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import foot_regions as R  # noqa: E402,F401

ASSET_ID = "superficial_peroneal_distribution"
VIEW = "foot"
CLIPS = {"top": R.TOP, "lateral": R.LATERAL}

# Dorsum from the toes to the front of the ankle and on up the cropped leg; the first web (x 402-436)
# and the lateral border (x > 522) are left out.
DORSUM = [(344, 150), (400, 150), (404, 210), (438, 216), (440, 200), (524, 222), (526, 250), (520, 300),
          (518, 600), (508, 690), (504, 800), (396, 800), (386, 700), (386, 650), (372, 560), (364, 480), (350, 400), (342, 250)]
# Outer side: the distal anterolateral leg and a band over the dorsum.
LEG_DORSUM = [(932, 392), (986, 392), (990, 540), (992, 600), (1040, 632), (1100, 670), (1150, 706), (1132, 724),
              (1086, 716), (1040, 690), (990, 654), (960, 632), (936, 602), (932, 500)]

ZONES = [
    Zone("dorsum-top", "teal", DORSUM, clip="top", feather=3.5),
    Zone("leg-lateral", "teal", LEG_DORSUM, clip="lateral", feather=3.5, fade=(960, 392, 960, 480)),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
