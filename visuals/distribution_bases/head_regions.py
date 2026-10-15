"""Clip regions and bone outlines on the head base, shared by the plates.

Base-painting px (visuals/distribution_bases/head/base.jpg): a skeleton bust
on the left (skull turned three-quarters toward the image right, the patient's
right cheek toward the viewer, midline of the dentition near x 447) and the
same bust as a grey body on the right (face midline near x 949; the patient's
right ear on the image left). A clip region keeps a skin tint on one part of
the head or neck; a bone outline is clipped again by the painted bone mask.
"""

# Body: forehead and scalp to the face midline, above the chin.
RIGHT_FACE = [(700, 100), (949, 100), (949, 545), (700, 545)]
# Body: the face below the brow to the chin, to the midline (lips at x ~ 950).
RIGHT_LOWER_FACE = [(700, 270), (956, 270), (956, 545), (700, 545)]
# Body: the ear and a ring of skin around it.
EAR = [(690, 250), (840, 250), (840, 460), (690, 460)]
# Body: the right neck and the top of the right shoulder, to the midline of the
# neck (the suprasternal notch is at x ~ 905).
RIGHT_NECK = [(600, 400), (906, 400), (906, 740), (600, 740)]

# Skeleton: right clavicle from the acromial end to the sternal end.
CLAVICLE = [(98, 682), (150, 676), (200, 682), (260, 688), (300, 690), (340, 694), (348, 708), (336, 722),
            (300, 716), (250, 706), (200, 698), (150, 696), (104, 700)]
# Skeleton: right maxilla around the infraorbital foramen (x 363, y 355) and
# the upper teeth from the second premolar to the central incisor, clear of
# the nasal aperture (x 395-425, y 345-385) and of the molars.
MAXILLA = [(352, 350), (396, 350), (398, 386), (422, 395), (440, 386), (447, 400), (447, 440), (376, 440),
           (376, 410), (352, 410)]
# Skeleton: the right upper canine with its root and the alveolar bone over it
# (teeth counted from the midline: central incisor x 440-447, lateral incisor
# 430-440, canine 410-428, first premolar 392-410).
CANINE = [(406, 382), (430, 382), (432, 440), (404, 440)]
# Skeleton: the right body of the mandible with its teeth, from the angle to
# the chin (the mandibular ramus above is left out).
MANDIBLE_BODY = [(300, 436), (447, 432), (449, 508), (385, 516), (335, 502), (300, 472)]
