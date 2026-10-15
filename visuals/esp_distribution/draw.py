"""Thoracic erector spinae plane block - expected distribution, back view.

An ESP block at about T5 spreads cranio-caudally under the erector spinae and
into the paravertebral and intercostal spaces: the posterior hemithorax, from
about T2 to T9, with a graded lower border; in bone, the right ribs below the
shoulder blade. Midline is a hard border for the skin on one side.

Run: python3 visuals/esp_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import back_regions as R  # noqa: E402,F401

ASSET_ID = "esp_distribution"
VIEW = "back"
CLIPS = {"right-back": R.RIGHT_BACK}

ESP_SKIN = [(849, 216), (880, 206), (915, 214), (924, 234), (924, 300), (920, 336), (849, 318)]

ZONES = [
    Zone("esp-skin", "teal", ESP_SKIN, clip="right-back", feather=7),
    Zone("esp-bone", "teal", R.RIB_BONE, layer="bone", feather=2.0, tension=0.3),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
