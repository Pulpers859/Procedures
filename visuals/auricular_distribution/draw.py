"""Auricular (ring) block - expected distribution, head view.

A ring of local anaesthetic around the base of the ear blocks the great
auricular, lesser occipital, auriculotemporal and auricular branch of the
vagus together: the whole auricle and a ring of skin around its base.

Run: python3 visuals/auricular_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "auricular_distribution"
VIEW = "head"
CLIPS = {"ear": R.EAR}

# The auricle and a ring of skin about a centimetre wide around it.
AURICLE = [(716, 322), (746, 290), (790, 292), (800, 324), (802, 360), (800, 402), (786, 424), (754, 424),
           (728, 396), (718, 360)]

ZONES = [
    Zone("auricle-skin", "teal", AURICLE, clip="ear", feather=3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
