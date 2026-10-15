"""Transgluteal (subgluteal) sciatic nerve block - expected distribution, back view.

The sciatic nerve at the subgluteal level: the posterior and lateral leg
below the knee and the foot, except the medial strip (saphenous branch of the
femoral nerve); in bone, the tibia, fibula, ankle and foot (not the medial
distal tibia and malleolus) and the posterior hip joint. The posterior femoral
cutaneous nerve of the posterior thigh is blocked when the spread reaches it
and has its own tone.

Run: python3 visuals/transgluteal_distribution/draw.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "distribution_bases"))

from distribution_lib import Zone, build_plate, write  # noqa: E402
import back_regions as R  # noqa: E402,F401

ASSET_ID = "transgluteal_distribution"
VIEW = "back"
CLIPS = {"right-leg": R.RIGHT_LEG}

# Below the popliteal crease (y about 645): posterior and lateral calf, heel;
# the thin medial border strip (saphenous) stays grey.
SCIATIC_SKIN = [(880, 648), (944, 648), (946, 700), (942, 780), (940, 830), (944, 874), (866, 874), (868, 836),
                (871, 800), (868, 740), (874, 690)]
# Posterior thigh from the gluteal fold to the popliteal crease.
PFCN_SKIN = [(850, 506), (924, 506), (924, 648), (850, 648)]

ZONES = [
    Zone("pfcn-skin", "violet", PFCN_SKIN, clip="right-leg", feather=5),
    Zone("sciatic-skin", "teal", SCIATIC_SKIN, clip="right-leg"),
    Zone("sciatic-bone", "teal", R.LEG_BONE, layer="bone", feather=2.0, tension=0.3, extra=[R.HIP_BONE, R.KNEE_BONE]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
