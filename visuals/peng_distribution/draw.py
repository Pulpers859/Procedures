"""PENG block - expected distribution, front view.

The pericapsular nerve group block targets the articular branches of the
femoral, obturator and accessory obturator nerves to the anterior hip
capsule. In bone: the femoral head and neck with the acetabular rim. No skin
is shaded: the block is designed to spare the cutaneous and motor branches.

Run: python3 visuals/peng_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import front_regions as R  # noqa: E402,F401

ASSET_ID = "peng_distribution"
VIEW = "front"
CLIPS: dict = {}

ZONES = [
    Zone("hip-capsule", "teal", R.HIP_JOINT, layer="bone", feather=2.0, tension=0.4),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
