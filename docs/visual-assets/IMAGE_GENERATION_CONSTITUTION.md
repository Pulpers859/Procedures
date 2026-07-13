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

### 4. Trajectories start from the real entry point
Needles, scissors, and procedural arrows must originate at the real skin,
probe, or tissue entry point. If an image needs both correct and incorrect
paths, draw them from the same entry point when that is the clinical comparison.
Never let a trajectory start inside the target organ, loop back on itself, curl,
or point out of the body unless the procedure actually requires that motion.

**Why:** pericardiocentesis repeatedly failed by drawing arrows from inside the
heart or as looping/downward paths. The fix was to erase both arrows and redraw
one shallow correct path and one steep incorrect path from a shared subxiphoid
entry.

### 5. The view must match the clinical reality
Choose the anatomical view a clinician actually uses at the bedside. Do not
default to a dramatic cross-section if it misleads. For example: lateral
canthotomy is a **frontal (anterior) view of the eye**, never a sagittal globe
cutaway; IJ ultrasound is a **grayscale short-axis B-mode window**, not a
colorized Doppler cartoon.

### 6. A leader lands exactly on its structure
Ambiguity is failure. "Lateral canthus" lands on the outer (lateral) corner, not
the medial one. "Inferior crus" lands at the lateral canthus, not mid-lid.
"Internal jugular vein" lands on the lateral, superficial, compressible vessel.
If two structures are close, separate the leaders clearly.

### 7. Only the required labels, exactly once
Render exactly the labels in the asset's `requiredLabels`, spelled verbatim,
and render each label once. No title banner, heading, subtitle, caption,
watermark, signature, logo, duplicated text, parenthetical expansion, anatomy
label not in the required list, or invented explanatory phrase anywhere in the
image.

**Why:** failed iterations added procedure titles, subtitles, captions,
parentheticals, vertebral-body labels, nonsense text, duplicated labels
("Needle trajectory", "Diaphragm", "Pectoralis major"), and misspellings
("epgastric"). Extra text is not harmless; it is a critical defect.

### 8. Aspect ratio is a requirement, not a preference
Generate a true 4:3 composition unless a spec explicitly says otherwise. Do not
accept near-square output as the target format. If a clinically correct render
comes out near-square, treat it as a review candidate that needs crop or light
re-render before bundling.

### 9. Restrained clinical palette, phone-legible
Premium medical-reference look, flat vector-like shapes, light background, calm
palette. Red-orange only for incision / danger / cut direction; blue-cyan only
for ultrasound or landmark guidance. Soft rounded humanist sans-serif labels
with generous spacing so words never touch. One teaching point per image — no
gallery layouts. Tighten the crop so the anatomy fills the frame.

### 10. Split concepts instead of cramming them
A procedure can have more than one visual when the images prevent different
high-risk errors. Do not compress procedural setup, landmark geometry,
ultrasound confirmation, rescue anatomy, and danger zones into one crowded
diagram. Create separate `visualAssets` and prompts, each with one teaching
point and a small label set.

**Why:** the first pericardiocentesis draft passed a geometry rubric but still
read like a subxiphoid TTE view rather than a procedural access image. The fix
is not prettier arrows; it is splitting subxiphoid needle geometry from
ultrasound target confirmation.

### 11. Repair prompts preserve what passed
When repairing a failed render, name the failed element and ask for the smallest
change that fixes it. Preserve passed anatomy, view, crop, colors, and labels.
For trajectory failures, explicitly say to erase the wrong trajectory and redraw
it from scratch; small nudges often keep the original error.

### 12. Every image is a draft for clinician review
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
- **pericardiocentesis_needle_path** — This is the procedural geometry image,
  not a TTE teaching view. Oblique torso/procedure view with xiphoid/costal
  margin, probe low in the subxiphoid window, and the needle as the star. Show
  a shallow path entering adjacent to the probe, tracking under the costal
  margin toward the patient's left shoulder, with liver and myocardium as
  red-orange danger anatomy. A small ultrasound inset is allowed only as
  confirmation.
- **pericardiocentesis_approach** — This is the ultrasound target-confirmation
  image. The ultrasound panel is the star: pericardial effusion, myocardium,
  drainage target, and needle tip entering the fluid pocket. Do not reuse this
  slot for the procedural access geometry.
- **ij_probe_orientation** — Grayscale short-axis B-mode. Vein lateral +
  superficial + compressible; artery medial + deeper + round. Needle target
  sits inside the IJ lumen, away from the carotid. No saturated red/blue vessel
  fill (that implies Doppler).
- **cric_danger_zone** — Thyroid isthmus crosses the upper tracheal rings,
  **below** the cricoid — not at the membrane. Veins run lateral to midline.
- **chest_tube_safe_triangle** — Pec major anterior, lat dorsi posterior;
  neurovascular bundle in the inferior groove of the upper rib; enter over the
  top of the lower rib.
- **needle_decompression_landmarks** — The 2nd intercostal-space marker must sit
  on the midclavicular line, not parasternal or within the internal mammary
  danger zone. Delete captions such as "preferred lateral site"; teach
  preference through relative emphasis, not extra text.
- **lp_position_landmark** — Show interspace labels L3-L4 and L4-L5 only; do
  not add separate vertebral-body labels L3, L4, or L5 unless the asset spec
  requires them.
- **paracentesis_liq_site** — LLQ entry is lateral to midline and midway between
  umbilicus and the ASIS on the same side as the entry. Inferior epigastric
  vessels are medial to the entry, between entry and midline. Spell
  "epigastric" correctly.
- **thoracentesis_site** — Entry sits over the superior margin of the lower rib,
  above the diaphragm, within pleural fluid. Diaphragm appears and is labeled
  once only.
- **usgiv_needle_tracking** — No title or subtitle. Short-axis grayscale B-mode
  view with distinct needle tip, visible shaft, vein lumen, and anterior wall
  tenting. The shaft may be simplified for teaching, but the tip must remain
  visually distinct.

See `CLINICAL_IMAGE_RUBRIC.md` for the full per-image answer keys and the 99%
grading gate.
