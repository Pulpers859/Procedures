"""Clip regions on the foot base, shared by the plates.

Base-painting px (visuals/distribution_bases/foot/base.jpg): the skeleton of
the right foot (top view), the right foot seen from above (toes up, big toe
on the image left), from below (the sole, big toe on the image right) and
from its outer side (toes to the image right). One rectangle per panel keeps
a tint on the panel it belongs to.
"""

TOP = [(318, 100), (578, 100), (578, 800), (318, 800)]
SOLE = [(586, 100), (828, 100), (828, 800), (586, 800)]
LATERAL = [(836, 100), (1195, 100), (1195, 800), (836, 800)]
