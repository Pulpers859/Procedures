# Clinical Image Generation Constitution

The standing law for generating procedure illustrations in this app. Every
prompt — Gemini API lane, Gemini web lane, or Antigravity render lane — must
obey these rules. They are enforced in code by `build_prompt()` in
`scripts/generate_visual_assets_gemini.py` (the "Labeling rules" and "Style
requirements" blocks) and graded by `CLINICAL_IMAGE_RUBRIC.md`. When you learn
a new rule while iterating on an image, add it here first, then propagate it to
`build_prompt` and the rubric so it is both enforced and gradeable.

This governs *how images are generated*. The rubric governs *how they are
graded*. Clinical correctness is always the gate; a beautiful image with one
wrong structure fails.

## Articles

### 1. Labels are nouns, never instructions
Every label names the anatomical structure or the single target its leader line
touches. No imperative, directive, or warning text as a label — no "cut away
from globe", "avoid", "do not", "danger", "stay midline". Those are wasted space
and clutter. If a rule matters, express it through the drawing (an arrow, a
shaded zone), not a sentence stuck on the anatomy.

**Why:** directive labels bloat the frame, shrink the anatomy, and read as noise
at phone size. The teaching point belongs in the picture, not in a caption.

### 2. Correct placement beats symmetry
Place each label on the side of the image nearest the structure it points to;
its leader line must land exactly on that structure. Never force labels into two
even columns or balance the count per side. An asymmetric layout with correct
leaders passes; a symmetric layout with one misplaced leader fails.

**Why:** a forced two-column balance rule once dragged the "Lateral canthus"
label onto the wrong (medial) corner. Layout symmetry is cosmetic; a leader
pointing at the wrong structure is a clinical error.

### 3. Direction is shown by arrows, not words
Cut direction, needle trajectory, insertion angle, and motion are drawn as
arrows. The arrow must be unambiguous and must point **away from** the danger
structure it protects (e.g., cut direction points away from the globe; needle
passes over the top of the rib, not under it).

### 4. The view must match the clinical reality
Choose the anatomical view a clinician actually uses at the bedside. Do not
default to a dramatic cross-section if it misleads. For example: lateral
canthotomy is a **frontal (anterior) view of the eye**, never a sagittal globe
cutaway; IJ ultrasound is a **grayscale short-axis B-mode window**, not a
colorized Doppler cartoon.

### 5. A leader lands exactly on its structure
Ambiguity is failure. "Lateral canthus" lands on the outer (lateral) corner, not
the medial one. "Inferior crus" lands at the lateral canthus, not mid-lid.
"Internal jugular vein" lands on the lateral, superficial, compressible vessel.
If two structures are close, separate the leaders clearly.

### 6. Only the required labels — nothing else
Render exactly the labels in the asset's `requiredLabels`, spelled verbatim. No
title banner, caption, watermark, signature, logo, duplicated text, or invented
extra labels anywhere in the image.

### 7. Restrained clinical palette, phone-legible
Premium medical-reference look, flat vector-like shapes, light background, calm
palette. Red-orange only for incision / danger / cut direction; blue-cyan only
for ultrasound or landmark guidance. Soft rounded humanist sans-serif labels
with generous spacing so words never touch. One teaching point per image — no
gallery layouts. Tighten the crop so the anatomy fills the frame.

### 8. Every image is a draft for clinician review
No image here is final medical authority. Do not invent clinical claims beyond
the requested labels and anatomy. Validator-clean and rubric-passing means
structurally sound, not clinically ratified.

## Per-asset placement notes

Specifics that have burned us; keep them true in every regeneration.

- **canthotomy_inferior_crus** — Frontal eye. "Lateral canthus" → outer corner
  where the lids meet and the incision begins (never the medial corner). Cut
  arrow points inferolaterally, away from the globe, toward the orbital rim on
  the scissors' side. Four labels only: Lateral canthus, Canthotomy incision,
  Inferior crus, Globe.
- **ij_probe_orientation** — Grayscale short-axis B-mode. Vein lateral +
  superficial + compressible; artery medial + deeper + round. No saturated
  red/blue vessel fill (that implies Doppler).
- **cric_danger_zone** — Thyroid isthmus crosses the upper tracheal rings,
  **below** the cricoid — not at the membrane. Veins run lateral to midline.
- **chest_tube_safe_triangle** — Pec major anterior, lat dorsi posterior;
  neurovascular bundle in the inferior groove of the upper rib; enter over the
  top of the lower rib.

See `CLINICAL_IMAGE_RUBRIC.md` for the full per-image answer keys and the 99%
grading gate.
