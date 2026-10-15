"""Clip regions and bone outlines on the hand base, shared by the plates.

Base-painting px (visuals/distribution_bases/hand/base.jpg): the skeleton of
the right hand seen from the palm side (thumb on the image right), the right
hand from the palm side (thumb right), and the right hand from the back
(thumb left). One rectangle per panel keeps a tint on the panel it belongs to.
"""

PALM = [(386, 100), (792, 100), (792, 800), (386, 800)]
DORSUM = [(798, 100), (1195, 100), (1195, 800), (798, 800)]

# Skeleton, palm view (finger rays from the little finger on the left).
LITTLE_RAY = [(52, 246), (88, 246), (90, 430), (92, 440), (108, 548), (92, 562), (76, 545), (58, 500), (58, 452), (54, 432)]
MIDDLE_PHALANGES = [(132, 106), (172, 106), (174, 392), (132, 392)]
INDEX_PHALANGES = [(174, 166), (214, 166), (216, 396), (174, 396)]
THUMB_PHALANGES = [(262, 384), (306, 378), (312, 420), (280, 508), (234, 508), (234, 468), (254, 428)]
