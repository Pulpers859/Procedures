"""Deep peroneal nerve block (at the ankle) - expected distribution, foot views.

The terminal cutaneous branch of the deep peroneal nerve: the first web
space, the adjacent dorsal sides of the big toe and the second toe. Nothing
else on the dorsum or sole.

Run: python3 visuals/deep_peroneal_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import foot_regions as R  # noqa: E402,F401

ASSET_ID = "deep_peroneal_distribution"
VIEW = "foot"
CLIPS = {"top": R.TOP}

# First web: the adjacent sides of the big toe and the second toe on the
# dorsum, from the cleft back to the metatarsal heads.
WEB = [(404, 200), (418, 196), (424, 230), (432, 200), (442, 206), (440, 270), (430, 320), (418, 340), (408, 320),
       (402, 260)]

ZONES = [
    Zone("web-skin", "teal", WEB, clip="top", feather=3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
