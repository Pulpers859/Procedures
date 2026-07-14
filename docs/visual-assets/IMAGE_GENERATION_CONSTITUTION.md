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

### 1. Labels are optional, and often absent
Do not assume a procedure visual needs labels. Many bedside procedure visuals
should work more like a clean procedural plate: anatomy, tool position, entry
site, target, and direction are shown by composition, path, arrows, contrast,
and inset detail. Use in-image labels only when they identify an ambiguous
landmark or target that the image cannot otherwise make obvious.

For proceduralists, labels such as "shallow needle path", "toward left
shoulder", "liver", or "myocardium" often add strain without adding knowledge.
Show those ideas visually unless Patrick explicitly asks for labels.

### 1a. Labels are nouns, never instructions
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
passes over the top of the rib, not under it). Do not add direction labels when
the arrow itself makes the direction clear.

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

### 5a. Laterality is clinical anatomy, not layout
For any torso, eye, limb, neck, or ultrasound view where right/left matters,
lock the view orientation in the prompt and audit it before scoring. If the
composition uses an anterior-facing torso, the patient's right is image-left
and the patient's left is image-right. Direction arrows such as "Toward left
shoulder" must follow that orientation, and danger anatomy such as the liver
must stay on the patient's anatomical side. A mirrored render fails even if the
labels, leader lines, and general shapes look clean.

### 6. A leader lands exactly on its structure
Ambiguity is failure. "Lateral canthus" lands on the outer (lateral) corner, not
the medial one. "Inferior crus" lands at the lateral canthus, not mid-lid.
"Internal jugular vein" lands on the lateral, superficial, compressible vessel.
If two structures are close, separate the leaders clearly. A leader line that
crosses multiple plausible targets or lands in empty/confusing space fails even
when the label text is spelled correctly.

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

Required labels should be sparse. Label procedural decision points, targets,
trajectories, and ambiguous landmarks. Do not label obvious organs or basic
anatomy that a proceduralist is expected to recognize unless the label prevents
a specific high-risk miss. Show those structures visually instead.

### 7a. Prefer controlled label overlays for high-risk visuals
For high-risk procedure visuals, ask the image model for clean unlabeled
anatomy/geometry whenever label placement has failed once. Add labels and
leader lines afterward in a deterministic overlay controlled by the app asset
pipeline. The generated base image should contain no text at all; the overlay
owns exact spelling, count, clipping, and leader-line endpoints.

**Why:** Gemini improved the pericardiocentesis anatomy after reference
grounding, but repeatedly added extra labels, clipped required labels, or moved
leaders ambiguously. Text is not where the image model should be trusted.

If the model also misplaces the procedure trajectory, first simplify and
reference-ground the full-scene prompt so the instrument is rendered as part of
the same illustration. Do not jump straight to a local instrument overlay.
Manual or deterministic overlays are appropriate for labels, leader lines,
simple arrows, or small target dots. They are usually a poor fit for the actual
procedure instrument because a separately drawn syringe/needle looks pasted on,
breaks the visual style, and can make a clinically correct path feel wrong.

### 8. No unexplained devices or phantom anatomy
Only draw tools, wires, catheters, sheaths, tubes, drains, needles, probes, and
anatomy that the asset spec explicitly requires. A random device crossing a
target organ is a failure because it changes the procedure story. If the asset
is about a needle path, draw one visually thin needle shaft with a clear tip;
do not replace it with a thick tube, catheter, or guidewire unless that is the
explicit teaching point.

For instrument-path assets, the tool itself must carry the teaching geometry.
Do not accept a render where the syringe points one direction but a separate
arrow, pointer, guide line, or second shaft shows the intended direction. That
is a clinical failure, not a cosmetic simplification, because the learner cannot
tell which line is the real instrument.

If the model repeatedly turns an internal needle path into a duplicate shaft,
ghost tip, wire, or unsafe line over an organ, split the concept: main panel
shows the external instrument angle up to the entry site, and the inset shows
the internal endpoint. Do not force the main panel to show an internal line just
because the procedure path exists in three dimensions.

### 9. Aspect ratio is a requirement, not a preference
Generate a true 4:3 composition unless a spec explicitly says otherwise. Do not
accept near-square output as the target format. If a clinically correct render
comes out near-square, treat it as a review candidate that needs crop or light
re-render before bundling.

### 10. Restrained clinical palette, phone-legible
Premium medical-reference look, flat vector-like shapes, light background, calm
palette. Red-orange only for incision / danger / cut direction; blue-cyan only
for ultrasound or landmark guidance. Soft rounded humanist sans-serif labels
with generous spacing so words never touch. One teaching point per image — no
gallery layouts. Tighten the crop so the anatomy fills the frame.

### 11. Split concepts instead of cramming them
A procedure can have more than one visual when the images prevent different
high-risk errors. Do not compress procedural setup, landmark geometry,
ultrasound confirmation, rescue anatomy, and danger zones into one crowded
diagram. Create separate `visualAssets` and prompts, each with one teaching
point and a small label set.

**Why:** the first pericardiocentesis draft passed a geometry rubric but still
read like a subxiphoid TTE view rather than a procedural access image. The fix
is not prettier arrows; it is splitting subxiphoid needle geometry from
ultrasound target confirmation.

### 12. Use real procedure references before generating
For high-risk anatomy, do not invent the composition from prose alone. First
collect a small reference board from reputable procedural examples such as
society guidance, major clinical centers, textbooks, open medical diagrams, or
the procedure's cited references. Extract factual constraints from those
references — patient orientation, landmark side, approach options, needle
direction, danger anatomy, and what the standard diagrams consistently show.
Then generate an original app-native schematic from those constraints. Do not
copy, trace, restyle, or closely reproduce any single copyrighted reference
image.

**Why:** pericardiocentesis failed repeatedly when prompted from an abstract
description. Reference diagrams immediately exposed the mirrored-liver error
and made the substernal/subxiphoid access geometry more coherent.

When Patrick provides a reference image, study the composition language, not
just the labels. Capture whether the reference teaches through a patient torso,
transparent anatomy, procedural instruments, approach letters, magnified
insets, ultrasound panels, or comparison views. Prompt for an original image
with the useful composition pattern while removing the clutter Patrick does not
want. Do not merely make the existing schematic less labeled if the reference
is showing a different kind of procedural plate.

### 13. Repair prompts preserve what passed
When repairing a failed render, name the failed element and ask for the smallest
change that fixes it. Preserve passed anatomy, view, crop, colors, and labels.
For trajectory failures, explicitly say to erase the wrong trajectory and redraw
it from scratch; small nudges often keep the original error.

### 14. Every image is a draft for clinician review
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
  not a TTE teaching view. The preferred composition is a reference-style
  procedural plate: anterior torso, semi-transparent ribs/sternum/costal
  margins, real syringe/needle entering the subxiphoid/substernal region, and a
  magnified cardiac inset showing the tip in pericardial fluid. Use an
  anterior-facing torso orientation unless explicitly changed: patient's right
  is image-left, patient's left is image-right. The liver stays on the
  patient's right upper abdomen / image-left side; the needle trajectory trends
  image-right/superior toward the patient's left shoulder. Show only the
  subxiphoid/substernal approach in this asset; do not include parasternal or
  apical approaches unless a separate comparison asset is requested. The needle
  tip must terminate visibly inside the blue pericardial fluid pocket in the
  inset, not on epicardium or myocardium. Do not add in-image labels, approach
  letters, direction labels, path labels, organ labels, or basic-anatomy labels.
  The syringe barrel, hub, and needle must be one continuous physical instrument;
  do not accept a separate arrow/trajectory line as a substitute for the needle.
  If full internal main-torso path rendering creates a double needle, a ghost
  tip, or a line over the heart, use the external-entry-plus-inset design: the
  main torso shows the external syringe/needle up to the skin entry only, and
  the inset shows the needle tip in the fluid pocket.
  If Gemini draws the main needle as lower-right to upper-left, or if a corrected
  bottom-left to upper-right needle crosses the liver, restart with a simpler
  reference-first prompt before trying local overlays. The syringe/needle should
  normally be generated as part of the illustration so it matches the plate's
  style and reads like a real procedure, not a post-hoc vector line.
  If a render lane repeats the same critical direction error after focused
  repair, mark the lane blocked instead of promoting a "closest so far" image.
  The path's shallowness and target should be visible through the instrument
  angle, inset, and anatomy.
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
