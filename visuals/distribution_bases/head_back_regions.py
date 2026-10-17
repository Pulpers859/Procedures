"""Clip regions on the back-of-head base.

Base-painting px (visuals/distribution_bases/head_back/base.jpg): a skull and a
grey head seen from behind, so the patient's RIGHT is on the image RIGHT. The
body's midline is x 880; the skull base meets the neck about y 450-470.
"""

# Body: the right half of the scalp, midline to the ear, above the neck.
RIGHT_SCALP = [(880, 60), (1100, 60), (1100, 470), (880, 470)]
