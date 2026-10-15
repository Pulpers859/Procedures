"""TAP block (lateral approach) - expected distribution, front view.

The lateral (mid-axillary) TAP block reaches the anterior branches of T10-T12
in the transversus abdominis plane: the anterior abdominal wall below the
umbilicus, from the midline out to about the anterior axillary line, one
side. The flank stays grey (the lateral cutaneous branches leave before the
plane), as do the upper abdomen (it needs a subcostal approach) and the
groin (L1, inconsistent).

Run: python3 visuals/tap_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import front_regions as R  # noqa: E402,F401

ASSET_ID = "tap_distribution"
VIEW = "front"
CLIPS = {"right-abdomen": R.RIGHT_ABDOMEN}

# Umbilicus (T10) at (846, 380), the midline at x 848. Audit 2026-10-15: out to
# the anterior axillary line (x 800 here), the lower border kept 10 px off the
# groin crease (L1 is not consistently covered).
TAP_SKIN = [(800, 386), (812, 379), (835, 376), (848, 376), (848, 452), (842, 452), (830, 442), (816, 427),
            (802, 411)]

ZONES = [
    Zone("tap-skin", "teal", TAP_SKIN, clip="right-abdomen", feather=7, fade=(820, 368, 820, 388)),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
