"""Superior alveolar nerve block (supraperiosteal infiltration at the canine) - expected distribution, head view.

The injected tooth (any upper tooth can be the target; shown on the canine) with
its root and the alveolar bone over it, strongest, and its two neighbours in the
arch, the lateral incisor and the first premolar, lighter (spread through the
porous maxilla). No skin is shaded.

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
    Zone("neighbour-bone", "amber", R.LATERAL_INCISOR, layer="bone", feather=1.0, tension=0.3, opacity=0.34,
         extra=[R.FIRST_PREMOLAR]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
