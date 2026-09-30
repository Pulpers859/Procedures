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

- `python3 scripts/pq.py visuals` lists every slot A–Z. Take the next `empty`
  slot that is not on one of these two lists:
  - **Skip; the owner adds real images** (ultrasound and rhythm strips):
    `aline_us_short_axis`, `ij_probe_orientation`, `cvc_wire_confirmation`,
    `ficb_subfascial_spread`, `fb_us_appearance`, `knee_us_effusion`,
    `pericardiocentesis_approach`, `pigtail_us_effusion`,
    `tvp_capture_confirmation`, `usgiv_short_axis`, `usgiv_needle_tracking`.
  - **Skip as low value unless the owner asks:** `abscess_technique`.
- Read the record: `pq visuals <procedure id> --full`, then
  `pq show <id> steps equipment troubleshooting`.
- Pick the one error the image prevents.
- **Ask or draw.** If two views are both plausible, ask the owner before
  drawing. Otherwise draw your default, and say it is your default in the
  message that sends the reference.
- **Default view:** the orientation an atlas uses, head at the top. Include
  enough context to read it at a glance (jaw, ear, shoulder, a whole hand). An
  upside-down "operator's view" (the IJ seen from the head of the bed) was
  unreadable.
- **Nerve blocks get two images:**
  - patient positioning: the probe and needle on the patient, painted as a
    photo;
  - anatomy: the cross-section under the probe.

  Ask the owner for a gold-standard plate to set the composition.
- List anything you add that the record does not say, such as standard
  anatomy or typical depths.
- Never say the owner agreed to something they did not say.

## 2. Draw the layout

Write `visuals/<slot id>/draw.py` and `spec.json`.

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
- Give markings, needles and target highlights `class="marking"`, so the
  reference leaves them out.
- In `spec.json`, write plain-words claims and a geometry check for each one:
  sides, lengths from the record, "tip in the plane", "nerve not in muscle".
- Run `python3 scripts/render_visuals.py <id>`. It must pass. Then look at
  `render/<id>.png` yourself.
- Export the reference with
  `python3 scripts/render_visuals.py <id> --reference`, which writes
  `render/<id>-reference.png`. Send it with prompt A.

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
   painting, and fails if the frame's shape changed.
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
| The layout was wrong | Fix `draw.py`, re-export, then prompt A in a new chat. |
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
- **Mirror** to the house laterality with `ImageOps.mirror`.
  - The light then comes from the other side; record it.
  - Mirror only when the mirrored image is still the view the caption names.
- **Erase** a wrong part by blending in the same area from a clean painting of
  the same anatomy (the IJ catheter tail). Crop the edited file, then merge the
  clean file.
- **Flatten** a small shape change (the FICB probe dent) with a warp kept above
  a layer that must not move.

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
- Re-derive the px/mm from a traced landmark, so lengths stay true.
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

**Nerve-block anatomy rules** (owner, FICB, 2026-09-30):
- The nerve lies in the fascial plane, never inside the muscle. Add a check
  that it doesn't overlap the muscle.
- Show the plane's floor as its own thin fascial line under the nerve, traced
  along the painted muscle surface.
- The injectate is a smooth teal layer with rounded ends, filling that plane
  around the nerve. Code draws it.
- In a section under the probe, the probe covers the whole top of the field.
  The needle enters in-plane just beyond the probe's lateral end, with its tip
  in the plane lateral to the nerve.
- Both images of a block are seen from the same side, and a section under a
  probe runs the way the ultrasound screen shows it. For the right-sided FICB
  both are seen from the feet, with lateral (the hip) on the left.
- The positioning image names the approach in its title (FICB:
  "Infraligamentous approach").

## 7. Send, approve, ship

- **Send** `render/review.png` and the full plate. If the review sheet is too
  big to send, send its card-size crop. In one message give:
  - what changed;
  - the known limits;
  - at most one question;
  - the exact next step.
- **Approval is explicit**: "approve", "looks great, commit". Then:
  1. Run `render_visuals.py <id> --record-approval --promote`.
  2. Set the slot's `assetName` and `caption` in `procedures.json`.
  3. Run the gate from CLAUDE.md, checking each exit code. `pytest | tail`
     once hid a failure, and it was pushed.
  4. Check that `git status` shows nothing left: the imageset, SVG, base and
     provenance are all committed.
  5. Push to main.
  6. Build and send the link (CLAUDE.md, "Shipping A Build").

## Traps that cost time

- **Gradient ids that collide with element ids.** The renderer now refuses
  duplicates.
- **A filter region set in canvas coordinates** clips a shape drawn in a
  rotated frame. The IJ catheter vanished this way.
- **A JSON edit that silently missed.** After editing, re-query the slot with
  `pq visuals <procedure id> --full`.
- **A `spec.json` for a slot that is not in `procedures.json`** fails the
  tests. Add the slot first.

## Third-party plates (owner's temporary exception, 2026-09-30)

Until every nerve-block image is done, a third-party plate (NYSORA) may be
attached to Gemini as image 2, for concept understanding only (prompt B).
- It is never committed.
- Provenance records that it was attached.
- Any result that reproduces its drawing is rejected.

Outside this exception, never copy or restyle a stock or textbook image: the
repo and the builds are public.
