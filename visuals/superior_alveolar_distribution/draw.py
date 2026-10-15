"""Superior alveolar nerve block (supraperiosteal infiltration at the canine) - expected distribution, head view.

One tooth: the upper canine with its root and the alveolar bone over it. No
skin is shaded.

Run: python3 visuals/superior_alveolar_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "superior_alveolar_distribution"
VIEW = "head"
CLIPS: dict = {}

ZONES = [
    Zone("canine-bone", "teal", R.CANINE, layer="bone", feather=1.0, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
