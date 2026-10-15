"""Clip regions and bone outlines on the front base, shared by the plates.

Base-painting px (visuals/distribution_bases/front/base.jpg), traced on 4x
gridded zooms; patient's right on the image left. A clip region keeps a
skin tint on one part of the body (no bleed onto a neighbouring limb or the
trunk); a bone outline is clipped again by the painted bone mask, so it only
has to separate one bone from its neighbours.
"""

# Body (right figure).
RIGHT_LEG = [(766.5, 373.0), (846.8, 373.0), (846.8, 898.0), (746.2, 898.0), (750.0, 568.0),
             (753.8, 485.5), (761.2, 448.0), (766.5, 418.0)]
# The arm from the anterior axillary fold out, shoulder to fingertips.
RIGHT_ARM = [(690, 190), (745, 185), (772, 205), (770, 250), (770, 290), (778, 300), (776, 330), (772, 380),
             (762, 420), (752, 470), (760, 575), (660, 575), (660, 470), (685, 400), (695, 300)]
# Neck base to the shoulder tip and down to the second rib, a little past
# the midline so a feathered edge there stays soft.
RIGHT_SHOULDER = [(700, 140), (856, 140), (856, 262), (776, 262), (745, 266), (700, 266)]
# Front of the chest, anterior axillary fold to the midline.
RIGHT_CHEST = [(776, 200), (849, 200), (849, 330), (776, 330)]
# Lower abdomen, flank to the midline (the umbilicus is at x 846; audit).
RIGHT_ABDOMEN = [(770, 340), (849, 340), (849, 480), (770, 480)]

# Skeleton (left figure).
# Humerus head to condyles with the glenoid (the shoulder joint).
HUMERUS = [(238, 205), (256, 201), (272, 203), (284, 212), (284, 228), (274, 238), (268, 250),
           (266, 300), (267, 335), (236, 335), (236, 300), (240, 240)]
# Humerus below the anatomical neck (no joint).
HUMERUS_SHAFT = [(240, 232), (268, 232), (266, 300), (267, 345), (262, 362), (236, 362),
                 (227, 345), (236, 300)]
# Radius, ulna, carpals, metacarpals and fingers; the femur's greater
# trochanter starts at x 282 beside the little finger, the pelvis at x 280.
FOREARM_HAND = [(232, 360), (264, 360), (258, 400), (252, 440), (252, 470), (262, 482), (274, 500),
                (284, 528), (283, 548), (270, 558), (160, 560), (168, 500), (200, 470), (210, 420),
                (222, 380)]
# Lateral third of the clavicle with the acromion.
CLAVICLE_LATERAL = [(246, 186), (262, 184), (282, 188), (284, 198), (268, 203), (252, 204),
                    (244, 198)]
# Femoral head and the acetabular rim (anterior hip capsule).
HIP_JOINT = [(289, 444), (298, 442), (306, 446), (312, 452), (313, 463), (308, 469), (302, 472), (300, 480), (293, 480),
             (285, 463), (292, 458), (292, 450)]
