"""Saphenous nerve (adductor canal) block - expected distribution, front view.

The saphenous nerve below the adductor canal: the anteromedial knee below the
patella (infrapatellar branch), the medial leg and ankle and the medial
border of the foot to the base of the big toe; in bone, its periosteal
branches to the anteromedial proximal tibia and the medial distal tibia and
malleolus. The thigh above the knee stays grey (the anterior and medial
femoral cutaneous nerves leave the femoral nerve above the canal).

Run: python3 visuals/saphenous_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import front_regions as R  # noqa: E402,F401

ASSET_ID = "saphenous_distribution"
VIEW = "front"
CLIPS = {"right-leg": R.RIGHT_LEG}

# From below the patella (infrapatellar branch) and the medial joint line down
# the medial leg to the base of the big toe; the same medial border as the audited femoral territory.
SAPH_SKIN = [(806, 666), (820, 654), (832, 644), (838, 648), (839.2, 676.8), (836.2, 718.0), (834.8, 778.0),
             (835.5, 823.0), (830.5, 842.0), (831.0, 853.0), (822.0, 853.0), (819.0, 846.0), (822.0, 832.0),
             (822.0, 815.5), (817.5, 778.0), (816.0, 721.8), (810.0, 688.0), (802, 672)]
# Saphenous periosteal branches (Lundblad et al. 2013); the same patches as
# the femoral and fascia iliaca plates.
SAPH_BONE_PROX = [(310.5, 658.0), (333.0, 658.0), (333.8, 669.2), (328.5, 680.5), (324.0, 689.5), (322.5, 694.0),
                  (313.5, 694.0), (312.8, 684.2), (310.5, 673.0)]
SAPH_BONE_DIST = [(315.8, 781.8), (324.0, 781.8), (325.5, 793.0), (330.0, 804.2), (332.2, 817.8), (330.8, 823.8),
                  (322.5, 823.0), (318.0, 814.0), (315.0, 800.5)]

ZONES = [
    Zone("saphenous-skin", "teal", SAPH_SKIN, clip="right-leg"),
    Zone("saphenous-bone", "teal", SAPH_BONE_PROX, layer="bone", feather=2.6, tension=0.3, extra=[SAPH_BONE_DIST]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
