"""Interscalene block - expected distribution, front view.

The roots and upper trunk (C5-C7) between the scalenes: the shoulder (the
lower deltoid and lateral arm skin of the axillary nerve), the lateral
forearm to the wrist (musculocutaneous), and in bone the shoulder joint, the
humerus and the lateral clavicle with the acromion. The supraclavicular
nerves (C3-C4: the cape of the shoulder and the skin over the clavicle) are
reached by the frequent spread to the superficial cervical plexus and have
their own tone. The ulnar side of the arm and the hand (C8-T1) stay grey:
the inferior trunk is usually spared.

Run: python3 visuals/interscalene_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import front_regions as R  # noqa: E402,F401

ASSET_ID = "interscalene_distribution"
VIEW = "front"
CLIPS = {"right-arm": R.RIGHT_ARM, "right-shoulder": R.RIGHT_SHOULDER}

# Deltoid and lateral arm, then the radial (image-left) half of the forearm
# to the wrist crease (y 470).
C5_C7_SKIN = [(728, 240), (756, 240), (764, 252), (762, 272), (752, 292), (750, 300), (748, 340), (738, 380), (732, 420),
              (724, 468), (700, 472), (700, 420), (704, 380), (710, 340), (718, 300), (722, 262)]
# Neck base to the shoulder tip and down to the second rib, tapering to the
# sternoclavicular joint.
CAPE_SKIN = [(796, 170), (820, 182), (830, 196), (832, 210), (830, 224), (800, 228), (770, 232), (745, 230),
             (722, 224), (718, 210), (740, 194), (770, 178)]

ZONES = [
    Zone("plexus-skin", "teal", C5_C7_SKIN, clip="right-arm"),
    Zone("supraclavicular-skin", "violet", CAPE_SKIN, clip="right-shoulder", feather=6),
    Zone("plexus-bone", "teal", R.HUMERUS, layer="bone", feather=0, tension=0.3, extra=[R.CLAVICLE_LATERAL]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
