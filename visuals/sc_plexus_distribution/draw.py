"""Superficial cervical plexus block - expected distribution, head and neck view.

The superficial cervical plexus (C2-C4): the skin of the lateral and anterior
neck on one side from the lower border of the mandible to the clavicle, the
skin over the angle of the jaw and the ear lobe (great auricular), and the cape
of the shoulder over the clavicle (supraclavicular nerves); in bone, the
clavicle. The face above the jaw line stays grey.

Run: python3 visuals/sc_plexus_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import head_regions as R  # noqa: E402,F401

ASSET_ID = "sc_plexus_distribution"
VIEW = "head"
CLIPS = {"right-neck": R.RIGHT_NECK}

# Below the jaw line (ear lobe to chin), the neck to the midline, to the
# clavicle and out over the shoulder tip.
NECK_SKIN = [(722, 412), (786, 414), (795, 440), (825, 475), (860, 500), (905, 520), (906, 690), (850, 688),
             (780, 680), (700, 684), (646, 704), (640, 690), (660, 650), (700, 625), (722, 590), (720, 500)]

ZONES = [
    Zone("neck-skin", "teal", NECK_SKIN, clip="right-neck", feather=4),
    Zone("clavicle-bone", "teal", R.CLAVICLE, layer="bone", feather=1.5, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
