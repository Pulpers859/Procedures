"""Femoral nerve block - expected distribution, front view.

The femoral territory of the audited fascia iliaca plate (ficb_distribution,
2026-10-15) without the lateral femoral cutaneous zone: a femoral block at the
inguinal crease does not reliably reach it. Coordinates are base-painting px
(visuals/distribution_bases/front), converted from that plate.

Run: python3 visuals/femoral_nerve_distribution/draw.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from distribution_lib import Zone, build_plate, write  # noqa: E402

ASSET_ID = "femoral_nerve_distribution"
VIEW = "front"

# The patient's right leg on the body (image left), between the hanging hand
# and the other leg.
CLIPS = {"right-leg": [(766.5, 373.0), (846.8, 373.0), (846.8, 898.0), (746.2, 898.0), (750.0, 568.0),
                       (753.8, 485.5), (761.2, 448.0), (766.5, 418.0)]}

# Anterior thigh (anterior femoral cutaneous), the knee, and the medial leg
# and ankle to the base of the big toe (saphenous); the upper medial thigh
# (obturator, genitofemoral) and the lateral thigh stay grey.
FEMORAL_SKIN = [(780.0, 412.7), (804.0, 427.0), (819.0, 452.5), (823.5, 478.0), (825.8, 508.0), (831.0, 545.5),
                (837.0, 583.0), (837.8, 628.0), (839.2, 676.8), (836.2, 718.0), (834.8, 778.0), (835.5, 823.0),
                (830.5, 842.0), (831.0, 853.0), (822.0, 853.0), (819.0, 846.0), (822.0, 832.0), (822.0, 815.5), (817.5, 778.0), (816.0, 721.8),
                (810.0, 688.0), (796.5, 664.0), (790.0, 644.5), (790.0, 625.0), (793.5, 622.0), (793.5, 590.5),
                (791.2, 523.0), (788.2, 448.0)]
# The femur from head to condyles and the patella (articular branches to the
# hip and knee).
FEMORAL_BONE = [(270.8, 472.7), (271.5, 464.5), (274.5, 460.0), (279.0, 458.5), (284.2, 460.0), (286.5, 462.2),
                (291.0, 458.5), (293.2, 452.5), (295.5, 448.7), (301.5, 447.2), (307.5, 451.7), (312.0, 457.0),
                (313.5, 463.0), (309.8, 467.5), (304.5, 469.7), (300.8, 473.5), (299.2, 484.0), (299.2, 494.5),
                (301.5, 515.5), (307.5, 545.5), (315.0, 575.5), (322.5, 605.5), (325.5, 622.0), (331.5, 636.2),
                (333.8, 644.5), (331.5, 652.0), (330.8, 656.5), (321.0, 657.2), (315.0, 658.8), (310.5, 659.5),
                (304.5, 658.0), (300.0, 657.2), (293.2, 656.5), (291.0, 649.0), (290.2, 641.5), (293.2, 632.5),
                (296.2, 626.5), (294.0, 613.0), (290.2, 583.0), (286.5, 545.5), (282.8, 515.5), (277.5, 493.0),
                (273.0, 481.7)]
# Saphenous periosteal branches: the anteromedial proximal tibia and the
# medial distal tibia with the medial malleolus (Lundblad et al. 2013).
SAPH_BONE_PROX = [(310.5, 658.0), (333.0, 658.0), (333.8, 669.2), (328.5, 680.5), (324.0, 689.5), (322.5, 694.0),
                  (313.5, 694.0), (312.8, 684.2), (310.5, 673.0)]
SAPH_BONE_DIST = [(315.8, 781.8), (324.0, 781.8), (325.5, 793.0), (330.0, 804.2), (332.2, 817.8), (330.8, 823.8),
                  (322.5, 823.0), (318.0, 814.0), (315.0, 800.5)]

ZONES = [
    Zone("femoral-skin", "teal", FEMORAL_SKIN, clip="right-leg",
         fade=(812.3, 434.5, 787.5, 467.5)),       # fades along the inguinal ligament
    Zone("femoral-bone", "teal", FEMORAL_BONE, layer="bone", feather=0, tension=0.3),
    Zone("saphenous-bone", "teal", SAPH_BONE_PROX, layer="bone", feather=2.6, tension=0.3, extra=[SAPH_BONE_DIST]),
]


def build() -> str:
    return build_plate(VIEW, ZONES, CLIPS)


if __name__ == "__main__":
    raise SystemExit(write(ASSET_ID, build()))
