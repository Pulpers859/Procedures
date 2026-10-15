"""Clip regions and bone outlines on the side base, shared by the plates.

Base-painting px (visuals/distribution_bases/side/base.jpg): a skeleton on
the left and a grey body on the right, both seen from the patient's right
side, facing the image right, from the head to the upper thighs, the right
arm raised with the hand behind the head. A clip region keeps a skin tint on
one part of the body; a bone outline is clipped again by the painted bone mask.
"""

# Body: the right side of the chest and upper abdomen from the armpit down
# (the raised arm and the neck are above y 320 and stay out).
RIGHT_CHEST = [(796, 326), (846, 314), (900, 300), (940, 308), (992, 350), (992, 560), (740, 560), (740, 334), (790, 332)]
# Body: the armpit and the inner side of the raised upper arm next to it.
RIGHT_AXILLA = [(790, 250), (870, 250), (870, 342), (790, 342)]

# Skeleton: the right ribs lateral to the shoulder blade (x 225-296), from the
# first rib's level down to the costal margin; the spine (x < 302) is left out.
RIBS_ALL = [(313, 306), (380, 306), (420, 330), (445, 420), (446, 480), (425, 500), (400, 508), (370, 500),
            (340, 492), (313, 486), (302, 420)]
# The same ribs down to about the sixth (PECS II): the band above y 425.
RIBS_UPPER = [(313, 306), (380, 306), (420, 330), (445, 410), (446, 430), (310, 430), (302, 420)]
