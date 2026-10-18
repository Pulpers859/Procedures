# Procedure Image Playbook

Read this before you make or repair any procedure image. It distils the nine
plates made on 2026-09-29/30. `README.md` in this folder is the reference for
the tools; this file says how to use them.

## The deal

- **The owner paints; you place.** The owner runs Gemini (Nano Banana Pro,
  "Thinking" in the Gemini app). You draw the layout, write every prompt,
  review every painting, and draw everything that must be exact in code.
- **Gemini is good at** tissue, skin, light and photo realism. **It is bad at**
  position, counts, instruments, laterality and text. Never ask it for those,
  and never ask it for anatomy from words alone: always attach a layout.
- **The owner's approval is the only gate.** The owner also chooses the view,
  judges the look, and is the clinical authority. Checks prove geometry, not
  quality. An AI "pass" proves nothing.

## What made the FICB plates the best so far

1. The owner supplied a gold-standard plate (NYSORA). We copied its
   *composition* into our own layout: zoomed on the target plane, the probe on
   the skin, the needle from lateral.
2. Gemini painted a **flat-colour** layout with prompt A, and that gave the best
   tissue. The owner then revised that painting with the concept plate attached
   (prompt B) to open the fascial plane.
3. Everything that had to be exact was drawn in code: the probe, needle,
   injectate, plane-floor line and labels.
4. Every change was a single change: one Gemini line, one crop repaint or one
   code edit. Each was re-rendered and shown to the owner at card size.
5. Every line drawn along a painted structure was traced from the painting,
   not guessed.

## 1. Pick the slot and agree the view

- `python3 scripts/pq.py visuals` lists every slot A–Z by procedure. Take the
  first `empty` slot in that order (any kind, Setup included) that is not on
  one of these two lists:
  - **Skip; the owner adds real images** (ultrasound and rhythm strips):
    `aline_us_short_axis`, `ij_probe_orientation`, `cvc_wire_confirmation`,
    `ficb_subfascial_spread`, `fb_us_appearance`, `knee_us_effusion`,
    `pericardiocentesis_approach`, `pigtail_us_effusion`,
    `tvp_capture_confirmation`, `usgiv_short_axis`, `usgiv_needle_tracking`.
  - **Skip as low value unless the owner asks:** `abscess_technique`.

  Every nerve block has two slots (owner, 2026-09-30): `<block>_patient_position`
  and `<block>_anatomy`. Landmark blocks (the face and ear) show the needle
  entry instead of a probe.
- Read the record: `pq visuals <procedure id> --full`, then
  `pq show <id> steps equipment troubleshooting`.
- Pick the one error the image prevents.
- **Ask or draw.** If two views are both plausible, ask the owner before
  drawing. Otherwise draw your default, and say it is your default in the
  message that sends the reference.
- **Default view:** the orientation an atlas uses, head at the top. Include
  enough surrounding anatomy to recognise the region at a glance (the jaw and
  ear above a neck, the knee above a shin). An upside-down "operator's view"
  (the IJ seen from the head of the bed) was unreadable.
- **House laterality:** draw the patient's right side unless the record
  names a side (pericardiocentesis: left of the xiphoid). Front views and
  sections show the patient's right on the image left, as when facing the
  patient, on a chest X-ray or CT, or on a transverse ultrasound. Draw the
  layout this way round from the start.
- **Nerve blocks get two images:**
  - patient positioning: the probe and needle on the patient, painted as a
    photo;
  - anatomy: the cross-section under the probe.

  Ask the owner for a gold-standard plate to set the composition.
- List anything you add that the record does not say, such as standard
  anatomy or typical depths.
- If the record contradicts itself, or lacks a number the image needs, draw
  what its steps say and put the contradiction to the owner as your one
  question. Never settle it silently.
- Never say the owner agreed to something they did not say.

## 2. Draw the layout

Write `visuals/<slot id>/draw.py` and `spec.json`. Every shipped plate's
`draw.py` has been replaced by its painted version, so start from a flat
layout in git history: `git show 2657ce4:visuals/radial_approach/draw.py`
(a limb from above) or `git show d7c43c8:visuals/ficb_anatomy_layers/draw.py`
(a section under a probe), with the matching `spec.json`.

- **True scale.** Place structures from real adult measurements in mm, and
  state the px/mm. The radial wrist drawn as "tubes on a paddle" was
  rejected; redrawn from measurements, it was accepted.
- **Zoom to the working area**, so it fills a 4:3 card. The FICB field is about
  6 cm across.
- **Flat colour and clean outlines only:** no texture, no hatching, no faint
  "hint" lines. Gemini:
  - copies drawn texture crudely (FICB);
  - paints dashed hints as dashed lines (the Vas-Cath aorta);
  - turned faint tendons into a cut-open window (the digital block).
- **Draw every structure Gemini would otherwise invent** (sternum, ribs,
  trachea). Anything missing gets invented.
- **The layout must be anatomically right.** Gemini copies layout errors, and
  no repair fixes them (the ulnar nerve over the pisiform, the SVC on the
  midline). If you find one, fix the layout, re-export it, and have the owner
  start a new chat.
- Give everything code will draw over the painting `class="marking"`:
  target zones, needles, incisions, brackets, guide lines. The reference then
  leaves them out; labels are left out automatically.
- A target is a zone the size the record gives (a 1 cm IO site), not a whole
  surface.
- In `spec.json`, write plain-words claims and a geometry check for each one:
  sides, lengths from the record, "tip in the plane", "nerve not in muscle".
  Copy the nearest plate's `spec.json`. The check types are listed in
  README.md.
- Run `python3 scripts/render_visuals.py <id>`. It must pass. Then look at
  `render/<id>.png` yourself.
- Export the reference with
  `python3 scripts/render_visuals.py <id> --reference`, which writes
  `render/<id>-reference.png`.
- Run the gate (below), then commit and push the layout to main. A "draft" is
  just that: an ordinary commit to main, not a branch or PR; nothing reaches
  the app without approval. Section 6 replaces this `draw.py`, so the layout
  lives on in that commit: note its hash, and name it in `provenance.json`
  (`reference`) when section 6 creates that file.
  `git show <commit>:visuals/<id>/draw.py` recovers it.
- Send the reference PNG with prompt A. Send every image to the owner with
  the `SendUserFile` tool: the owner is on a phone.

## 3. Prompts

Every prompt you send names **a new chat or the same chat**, and **which file
to attach**, described by what it shows. Send one prompt per image per
message: the owner lost track when two arrived together.

**A. First paint of a layout** (new chat; attach the reference):

```
The attached image is an exact anatomical layout of <view and orientation>: <every structure in the reference, in plain words, with its colour>. Repaint it as a premium medical-atlas illustration, in the same 4:3 landscape frame.

Keep every structure exactly where it is, with the same size, outline and position; the image will be overlaid with exact markings afterwards, so nothing may move. Change only the rendering: soft painted shading, fine crisp outlines, realistic <tissue> textures, gentle depth and light from the upper left. Calm, restrained palette on the same off-white background. Do not add, remove, move or resize anything, and add no text, letters, numbers, labels, lines, incisions, instruments, hands or blood.
```

**B. Revision with a concept plate.** Use this for nerve blocks only, while
the exception at the end of this file stands. New chat. Image 1 is the layout
or the chosen painting; image 2 is the third-party plate. The full FICB
wording is in `ficb_anatomy_layers/provenance.json` (`promptStep2`).

```
Image 1 is the exact layout. Use it as the structure for a scientifically accurate <section>: keep every outline, position and size exactly as drawn, in the same 4:3 landscape frame, with the tissue running to all four edges. Exact labels and a needle will be laid over it afterwards.

Image 2 is for understanding the anatomy only: <the relationship to learn from it>. Take the relationships from image 2; take every position, shape and size from image 1; the drawing itself is new.

Paint it as a premium regional-anaesthesia atlas plate: a rich, deep, saturated palette with soft glossy highlights, fine crisp outlines and gentle depth, lit softly from the upper left.

Work from the top down:
1. <layer: what it is and how it looks>
2. <next layer>

The picture shows only this anatomy<and the probe>.
```

**The house style for nerve-block sections** (owner, 2026-10-13: "I really
like how this nerve bundle was illustrated as well as that fascial spacing
... in addition to the more enhanced muscle appearance"). The model is
`supraclavicular_anatomy`: layout `b15df31`, painting and repairs in its
`provenance.json`. Build every section this way unless the owner asks
otherwise.

- **Draw the fascia in the layout.** Nerves never float in fat:
  - Give a nerve bundle its own sheath element: a closed pale shape (`#F3E4C2`) with a 7 px white (`#F8F6F0`) outline round all its fascicles or trunks.
  - Pack the trunks inside the sheath, slightly apart, not touching.
  - Draw each fascial plane as a 7 px white line, including one along the surface of any muscle the needle runs beside.
  - A muscle that ends beside the target tapers to a point on its bony attachment. Do not leave a block of fat where the muscle would be.
- **Use these layer lines in prompt B**, adapted to the block:

```
3. The long thin white lines are crisp, glistening fascial sheets: <where each runs>.
4. The pale outlined shape holding the yellow circles is the <nerve> sheath: a thin, translucent, glistening grey-white membrane with pale connective tissue between the nerves.
5. The <n> yellow circles are the <nerve, trunks or divisions>: each a round olive-yellow nerve bundle in a thin pale sheath with finely speckled fascicles.
6. The maroon shapes are skeletal muscle cut across, made of fine fascicle bundles edged with thin white connective tissue; <a tapering muscle> tapers to a point resting on the bone.
```

  The image-2 sentence that taught the spacing: "how the <nerve> is packed inside one thin fascial sheath beside the <artery>, how the <muscle> tapers under it with a fascial sheet on its surface, and how every structure is wrapped in thin glistening fascia rather than floating in fat."
- **Expect Gemini to paint some muscles lumpy, like a gland or liver**, with no fibres. Fix each one with prompt C:
  > Paint the <muscle, by colour and position> with fine parallel maroon muscle fibres, like the large muscle on the left. Keep everything else in the image the same.

  For a muscle at the edge, use the crop tool and prompt D instead: "paint it as skeletal muscle with fine parallel maroon fibres and thin white connective-tissue streaks, in exactly the same outline and position".
- **Lung:** if it comes back split into different tissues, use prompt C:
  > Paint the whole pink area along the bottom, below the thin white pleural line, as one continuous lung: soft, pale pink, finely spongy alveolar tissue with the same even texture from the left edge to the right edge, under a thin glistening pleura. Keep everything else in the image the same.
- **Check each repair against the one before it.** A repair can remove things it was not asked to touch (the SCM vanished with an invented muscle). Take the lost area back from the earlier image with `visual_patch.py crop` and `merge`.

**C. Repair of the whole image** (same chat; one change):

```
<One change, in one plain sentence, said positively>. Keep everything else in the image the same.
```

These worked:
- "Remove 3 of those catheter lines. Keep everything else in the image the same."
- "Remove the cut-open window on the back of the hand and paint normal intact skin there instead, like the rest of the hand. Keep everything else in the image the same."

**D. Repair of one area** (crop tool, section 5; new chat; attach only
`patch-crop.png`):

```
Using the attached close-up, change only <X>: <what it should be, where, how big>. Keep everything else exactly the same, preserving <what surrounds it>, the lighting and the same framing as the attached image.
```

Put a follow-up change to the same crop in that same chat, one per turn.

Rules for every prompt:
- **Say what you want, not what you don't:** "plain intact skin", not "no
  cut-away". The only negative list is the last line of prompt A.
- **Name the frame** ("same 4:3 landscape frame"). Without it, edits come back
  16:9 and recomposed.
- **One change per turn.** A three-change line ("stand the probe up, add a
  hand, remove a cable") came back as a new 16:9 photo with the thigh gone.
- **Keep repairs short and literal.** The owner's short catheter line beat
  long, careful ones.
- **Photos get camera words:** shot from above, soft even procedure-room
  light, shallow depth of field.

## 4. Review every painting

1. **Overlay it first.** Run
   `python3 scripts/visual_patch.py overlay <id> <painting>`. It writes
   `render/overlay.png`, the reference's outlines in magenta over the
   painting, and fails if the frame's shape changed. Do it before section 6:
   once the layout's `draw.py` is replaced, `--reference` exports the
   painting, not the layout.
   - Judge from that overlay and from the full-size file. Zoom in on every
     area you will mark, and on the corners (watermark).
   - Never judge from memory or a thumbnail. An earlier review called the FICB
     painting "framed and shrunk"; the overlay showed it lined up.
2. **Anything that moved, vanished or appeared is a defect.** Sort each one:
   - **Must fix:** it sits under a marking or label, or a clinician would read
     it as wrong anatomy.
   - **Accept and record:** it is cosmetic and away from everything marked.

   Stop repairing once the marked landmarks are right.
3. **An upload nearly identical to the previous one** came from the old chat
   or the old attachment. Say so, and name the file to attach in a new chat.
4. **Three or more structural errors in one painting:** don't repair it. Fix
   the layout or the prompt, and start a new chat.
5. **Reject any repair that breaks a landmark**, and go back to the previous
   version. The cric hyoid repair erased the membrane.

## 5. Choose the fix

| Situation | Do |
| --- | --- |
| One thing wrong across the image | Prompt C, same chat. |
| One small area wrong, the rest right | The crop tool (below). |
| Several things wrong | One prompt C per turn, the most important first. |
| The layout was wrong | Fix the layout's `draw.py` (recover it from its commit if section 6 has replaced it), re-export, then prompt A in a new chat. |
| Gemini fails the same element twice | Stop asking. Draw it in code (the FICB probe; catheters by default) or fix it with a pixel edit (below). Tell the owner why. |
| The owner prefers Gemini's version of something you drew in code | Use theirs. Correct its clinical fault with a pixel edit. |

**The crop tool:**
1. Run
   `python3 scripts/visual_patch.py crop <id> --box X0 Y0 X1 Y1 --image <painting>`.
   Box only the defect; the tool adds the margin.
2. The owner repaints `render/patch-crop.png` with prompt D.
3. Run `python3 scripts/visual_patch.py merge <id> <repaint>`. It must report
   0 px changed outside the box.

To take back only part of the crop, add `--keep X0 Y0 X1 Y1` to the merge.

**Pixel edits you may make yourself.** Keep the untouched file as
`gemini-original.jpg`, and record every edit in provenance.
- **Mirror** to the house laterality (section 1) with `ImageOps.mirror`.
  - The light then comes from the other side; record it.
  - Mirror only when the mirrored image is still the view the caption names.
  - Mirror the side claims and checks in `spec.json` with it, and note in
    provenance that the layout commit is the other way round.
- **Erase** a wrong part by blending in the same area from a clean painting of
  the same anatomy (the IJ catheter tail). Crop the edited file, then merge the
  clean file.
- **Flatten** a small shape change (the FICB probe dent) with a warp kept above
  a layer that must not move. Diff the result: nothing at or below that layer
  may change.

No clean painting to blend from? Use the crop tool instead. A painted object
that code redraws anyway (the FICB probe) needs no erasing: draw over it.

Never move an object by cutting and cloning it. On the FICB probe that left a
ghost glove and a doubled skin fold.

## 6. Build the plate on the painting

- Save the chosen file as `visuals/<id>/base.jpg`.
- Copy the structure of the nearest existing plate's `draw.py`:
  - `cric_membrane`: a simple overlay;
  - `ficb_anatomy_layers`: a section with a probe, needle and injectate;
  - `ficb_patient_position`: a photo;
  - `digital_block_landmark`: two panels with a callout.
- **Trace from the painting.** Trace every target region, and every line you
  draw along a painted structure, in base pixels. Check them with `DEBUG=1`.
  The FICB plane-floor line wandered into the muscle because its border was
  guessed.
- Re-derive the px/mm from a traced landmark whose size the layout fixed
  (the FICB artery), so lengths stay true.
- Keep the base's SHA-256 stamp (`data-base-sha256`) that the example plates
  write, so replacing the painting voids an approval.
- **Code draws:** markings, needles, incisions, injectate, target highlights,
  any instrument Gemini got wrong, and the labels.
- **Labels** are nouns, 2–3 per image. A nerve-block anatomy plate may carry
  up to 5 if the card-size render is not crowded.
- **The caption** is one line stating the orientation, for example "Right
  groin in section under the probe, seen from the feet as on ultrasound:
  lateral (the hip) on the left."
- **`provenance.json`** records the prompts, repairs, rejected versions and
  why, pixel edits, known limits, and any third-party concept image attached.
- Render again. All checks must pass. Look at `render/<id>-phone.png` at card
  size, in light and dark.
- Run the gate (below), then commit and push the plate to main as a review
  draft.

**Nerve-block anatomy rules** (owner, FICB, 2026-09-30):
- The nerve lies in the fascial plane, never inside the muscle. Add a check
  that it doesn't overlap the muscle.
- Show the plane's floor as its own thin fascial line under the nerve, traced
  along the painted muscle surface.
- The injectate is a smooth teal layer with rounded ends, filling that plane
  around the nerve. Code draws it.
- In a section under the probe, the probe covers the top of the field from
  the medial edge to just short of the lateral edge, leaving a gap of about
  1 cm. The needle enters in-plane in that gap, with its tip in the plane
  lateral to the nerve.
- Keep the nerve visible inside the teal, drawn over it or showing through.
- Both images of a block are seen from the same side, and a section under a
  probe runs the way the ultrasound screen shows it. For the right-sided FICB
  both are seen from the feet, with lateral (the hip) on the left.
- The positioning image names the approach in its title (FICB:
  "Infraligamentous approach").

## Distribution plates (nerve blocks, first tile)

Owner, 2026-10-15: each nerve block gets a first tile showing where to expect
numbness, as a skeleton and a grey body side by side, premium and calm, not
bolted on. The model is `ficb_distribution/`.

- **Kind and placement.** `"kind": "Distribution"`, first in the block's
  `visualAssets`. The colour key is a `legend` in the record (one bullet per
  nerve, `tone` from the fixed palette teal / violet / amber / rose / blue),
  shown by the app under the image. No labels or leaders on the plate.
- **One base per view.** The two figures are painted once from a layout
  (`ficb_distribution` draw.py `skeleton()` and `body_outline()`) through
  Antigravity, front view; reuse that base for every block seen from the
  front, and make one more base per view a block needs (back, head). Never
  repaint the figures per block.
- **Masks, not outlines.** `make_masks.py` traces bone and body from the
  painting; the tint is clipped to those masks, and the body tint also to a
  hand-traced region of the limb (`RIGHT_LEG`) so it can never reach the arm,
  trunk or other limb.
- **Strict territories.** Trace on 6x gridded zooms of the painting. Shade a
  bone only if the block supplies it (the femur and patella for the femoral
  nerve, never the pelvis or tibia). Leave out inconsistent nerves (obturator
  in a fascia iliaca block) and say so in the claims. Right side, patient's
  right on the image left.
- **Look.** `mix-blend-mode: multiply` so the painted shading shows through;
  about 0.7 opacity on skin, 0.62 on bone; a 4 px feather on skin, none on
  bone; a fade along a border that is a gradient in life (the inguinal
  ligament).
- **Independent audit, every plate** (owner, 2026-10-15). Before sending a
  distribution plate, run a separate reviewer agent on it: a tinted-pixel map
  against the untinted base for bleed onto anything the block does not supply
  (other bones, the arm, trunk, other limb, floor, background), and each
  territory against NYSORA's distribution figure and standard cutaneous maps.
  Fix what it finds, then send.

- **Bases and tools (2026-10-15).** The figures are painted once per view in
  `visuals/distribution_bases/<view>/` (`base.jpg`): front, back, head (bust),
  hand (skeleton palm view, palm, back of the hand), foot (skeleton top, top,
  sole, outer side) and side (head to thighs, right arm raised). Each view has
  `make_masks.py` masks and `<view>_regions.py` with the clip regions and bone
  outlines traced on gridded zooms. A plate is a short `draw.py` that calls
  `scripts/distribution_lib.py` (`Zone`, `build_plate`); a skin zone must name
  a clip region, so a tint cannot reach a neighbouring limb. Laterality: the
  patient's RIGHT is the image left in the front view, the image right in the
  back view, and the painted hands and feet are RIGHT (the paintings came back
  as left and were mirrored panel by panel).
- **Audit tool.** `python3 scripts/distribution_audit.py <id>` renders the plate
  with and without its markings and writes `render/tintmap.png` (every tinted
  pixel in solid colour) and `tintmap.json`; the independent auditor works from
  that plus NYSORA and the literature.
- **Words that moved the search-ranking probes** when they were in a
  distribution caption or subtitle: "block", "nerve", "arm", plus the older
  list. The legend is not searched, so the nerve names go there. Keep captions
  to what is left unshaded and why. Leave the subtitle empty (owner,
  2026-10-17: "Where to expect numbness..." was cut as useless).

## 7. Send, approve, ship

- **Send** `render/review.png` and the full plate (`SendUserFile`). If the
  review sheet is refused as too big, send `render/<id>-phone.png` (the card
  at phone size) instead. In one message give:
  - what changed;
  - the known limits;
  - at most one question;
  - the exact next step.
- **Approval is explicit**: "approve", "looks great, commit". Then:
  1. Run `render_visuals.py <id> --record-approval --promote`.
  2. Set the slot's `assetName` and `caption` in `procedures.json`.
  3. Run the gate.
  4. Check that `git status` shows nothing left: the imageset, SVG, base and
     provenance are all committed.
  5. Push to main.
  6. Build and send the link (CLAUDE.md, "Shipping A Build").

## The gate

Before every push, run each of these and check its exit code (`pytest | tail`
once hid a failure, and it was pushed):

```
python3 scripts/validate_procedures.py
python3 scripts/check_search_ranking.py
python3 scripts/check_review_state_sources.py
python3 -m pytest scripts/tests -q
```

## Traps that cost time

- **Gradient ids that collide with element ids.** The renderer now refuses
  duplicates.
- **A filter region set in canvas coordinates** clips a shape drawn in a
  rotated frame. The IJ catheter vanished this way.
- **A JSON edit that silently missed.** After editing, re-query the slot with
  `pq visuals <procedure id> --full`.
- **A `spec.json` for a slot that is not in `procedures.json`** fails the
  tests. Add the slot first.
- **Re-solving a body part that is already solved.** The superolateral knee
  took three new chats (the leg painted too slim, the kneecap unreadable)
  while the IO tibia plate already had an approved right knee from the front.
  Before drawing, check the shipped `visuals/*/base.jpg` for the same region
  and view. Reuse it: build on it directly, or attach it to Gemini as image 2
  for the region's proportions. Record the reuse in provenance
  (owner, 2026-10-02).

## Third-party plates (owner's temporary exception, 2026-09-30)

Until every nerve-block image is done, a third-party plate (NYSORA) may be
attached to Gemini as image 2, for concept understanding only (prompt B).
- It is never committed.
- Provenance records that it was attached.
- Any result that reproduces its drawing is rejected. Ask the owner to send
  you the plate in the chat, so you can compare the two.

Outside this exception, never copy or restyle a stock or textbook image: the
repo and the builds are public.
