"""Clip regions and outlines on the back base, shared by the plates.

Base-painting px (visuals/distribution_bases/back/base.jpg), traced on gridded
zooms. Seen from behind, the patient's RIGHT is on the image RIGHT. A clip
region keeps a skin tint on one part of the body; a bone outline is clipped
again by the painted bone mask.
"""

# Body (right figure, midline x 847): the patient's right leg from the
# gluteal fold down, between the other leg (image left) and the hand.
RIGHT_LEG = [(848, 498), (948, 498), (948, 896), (848, 896)]
# Right half of the back from the neck base to the waist, stopping short of
# the arm (the arm hangs away from the trunk below y 300).
RIGHT_BACK = [(849, 205), (925, 205), (926, 260), (930, 300), (924, 330), (918, 405), (849, 405)]

# Skeleton (left figure, midline x 350).
# Right leg from the tibial plateau to the heel and forefoot: tibia, fibula,
# ankle and foot, held back from the medial malleolus and the distal medial
# tibial border (saphenous periosteum).
LEG_BONE = [(374, 664), (416, 664), (417, 690), (413, 760), (409, 830), (404, 838), (426, 846), (428, 858),
            (372, 869), (366, 858), (368, 846), (384, 836), (388, 820), (386, 780), (378, 760), (374, 720), (372, 690)]
# Right hip joint seen from behind: the acetabular rim and the head and neck
# behind the greater trochanter.
HIP_BONE = [(392, 448), (412, 444), (424, 458), (414, 470), (404, 476), (392, 474), (388, 462)]
# Right ribs from the second to about the tenth, lateral to the spine and
# below the shoulder blade (the scapula, x 392-445 above y 268, is not
# supplied by an erector spinae plane block).
RIB_BONE = [(363, 215), (392, 215), (392, 262), (406, 272), (432, 272), (432, 330), (363, 330)]
