# Code-Drawn Procedure Visuals

This is the primary lane for procedure images from 2026-09-29. The Gemini and
Antigravity lanes in `docs/visual-assets/` are kept for reference but are no
longer the route to a shipped image. After 30+ iterations per image they
produced two bundled images with clinical errors that their own rubric forbids,
and an AI grader passed both.

## Why code

An image model draws plausible texture with no guarantee of laterality, leader
endpoints, or spelling, and every fix is a re-roll that can lose what was
right. Here every structure is a named SVG element built from named geometry,
so:

- a correction is a one-line change that re-renders identically;
- the answer key in `spec.json` is checked against the geometry the browser
  actually drew, not judged by eye (a mirrored eye, an arrow turned toward the
  globe, and a stray caption each fail the checks);
- labels are real text in a vendored font (`fonts/`, Inter, SIL OFL), so
  spelling and count are exact.

## Layout

```
visuals/
  README.md
  fonts/                      Inter 500/700 + OFL licence
  <asset_id>/
    draw.py                   builds the SVG from named geometry
    <asset_id>.svg            generated, committed so diffs are reviewable
    spec.json                 answer key: claims, labels, geometry checks, review
    render/                   gitignored: PNGs, check.json, review.png
scripts/visuals_lib.py        shared geometry, label and house-style helpers
scripts/render_visuals.py     render + check + review sheet + promote
scripts/tests/test_code_drawn_visuals.py   CI guard (no browser)
```

`<asset_id>` is the `visualAssets.id` in `procedures.json`.

## Loop

1. Write or edit `draw.py` and `spec.json`. Put the anatomical claims in
   `spec.claims` in plain words; they are what the owner confirms.
2. `python3 scripts/render_visuals.py <asset_id>` (needs `pip install playwright`;
   uses the preinstalled Chromium). All checks must pass.
3. Look at `render/<asset_id>.png` yourself before anyone else does. Checks
   prove the drawing matches the spec, not that it looks right.
4. Send the owner `render/review.png`. It shows the card at iPhone size, light
   and dark, then the claims, then the check results.
5. Only when the owner approves:
   `python3 scripts/render_visuals.py <asset_id> --record-approval --promote`,
   then set `visualAssets.assetName` and run `validate_procedures.py`.
   Approval is recorded against the SVG's SHA-256; any later edit voids it, and
   CI fails if a bundled drawing no longer matches its approval.

## Standard workflow (owner-approved 2026-09-30)

This is how every new procedure image is made, unless the owner says
otherwise. It is the route that produced the approved cricothyrotomy plate.
Painting comes from Gemini; geometry, markings and labels come from code.

1. **Pick the image from the record and ask the owner for the view.**
   - Read the procedure with `pq.py`, and pick the single miss the image
     prevents.
   - Default to the operator's view: what the clinician sees over the
     patient. A-P for the neck and chest wall is the usual choice.
   - Propose the view and the slot text. Never claim the owner agreed to
     something they did not say.
2. **Draw the layout in code.**
   - `visuals/<slot id>/draw.py` places every structure at true scale,
     with a stated px/mm, from the record's own numbers.
   - Incisions, needle paths and target highlights get `class="marking"`.
   - `spec.json` states the claims and the geometry checks, including
     `lengthRange` for any length the record gives.
   - `python3 scripts/render_visuals.py <id>` must pass. Look at the
     render too; checks do not judge appearance.
3. **Export the reference.** Run
   `python3 scripts/render_visuals.py <id> --reference`. It writes
   `render/<id>-reference.png` with no labels and no markings. Send that
   image to the owner.
4. **The owner repaints it in Gemini** (Nano Banana Pro, a new chat, the
   reference attached). Use the prompt template below.
5. **Review the painting against the reference.**
   - Anything that moved, vanished or appeared is an error. Zoom into the
     actual file, not a screenshot.
   - Give one targeted repair line per problem, in the same chat.
   - Reject any repair that breaks a landmark and fall back to the
     previous version. The cric hyoid repair erased the membrane and was
     rejected.
   - Accept cosmetic limits and record them.
6. **Rebuild the plate on the painting.**
   - Copy the chosen file to `visuals/<id>/base.jpg`.
   - Rewrite `draw.py`: place the base, trace target regions in base
     pixels (check them with `DEBUG=1`), then redraw the markings and at
     most 2-3 noun labels in code.
   - Re-derive the scale from a traced landmark, so lengths stay true.
   - Stamp the base's SHA-256 into the SVG.
   - Write `provenance.json`: prompt, repairs, rejected versions, known
     limits.
7. **Owner approval, then ship.**
   - Send `render/review.png`. On approval, run
     `--record-approval --promote`, set `assetName`, run the gate, and
     push.
   - Build the sideload .ipa and give the owner the release link.

Prompt template for step 4:

```
The attached image is an exact anatomical layout of <view and orientation, e.g. "the anterior neck, patient supine, head at the top">: <every structure in the reference, in plain words>. Repaint it as a premium medical-atlas illustration.

Keep every structure exactly where it is, with the same size, outline and position; the image will be overlaid with exact markings afterwards, so nothing may move. Change only the rendering: soft painted shading, fine crisp outlines, realistic <tissue> textures, gentle depth and light from the upper left. Calm, restrained palette on the same off-white background. Do not add, remove, move or resize anything, and add no text, letters, numbers, labels, lines, incisions, instruments, hands or blood.
```

What did not work, so it is not repeated:

- **Text-only prompts** for fixed-geometry views (a midsagittal larynx,
  for example). They produced structural errors: gland inside the airway,
  a second puncture, cartilage on the wrong wall.
- **Letting Gemini draw incisions, instruments or labels.** They drift or
  misspell. Code draws them.
- **Copying or restyling a stock or textbook image.** It is copyrighted,
  and the repo and builds are public. Use only its composition ideas.
- **Trusting an AI "PASS".** The owner's approval is the only gate.

## Painted base plus code labels

When the art comes from an image model (for example `pigtail_seldinger`,
painted by Gemini Nano Banana Pro in the Gemini app), the plate is `base.jpg`
plus a `draw.py` that places it and draws the labels. The anatomy in a raster
cannot be measured, so:

- the owner iterates the painting in Gemini, and the agent checks it against
  the claims in `spec.json` by eye, zooming into the instrument and landmarks;
- label targets are regions hand-traced over the base (`DEBUG=1` shows them),
  and the renderer checks that each leader lands inside its region;
- `provenance.json` records the prompt, every repair, what was rejected, and
  known limits;
- the base's SHA-256 is written into the SVG, so replacing the painting voids
  an approval just as editing a drawing does.

## House style

- 1600 x 1200 canvas (4:3); it shows at about 350 pt wide on the phone.
- Labels: 56 px Inter (about 12 pt on the card), nouns only, at most two to
  three per image, each leader ending in a dot inside its structure.
- Colours are CSS variables in `visuals_lib.HOUSE_STYLE`: teal = target,
  red-orange = incision, cut, or danger, dashed or hatched outline = deep
  structure, grey = present but not the target.
- Dark mode: plates are full-bleed, so dark mode dims the art slightly and
  keeps label colours. Promotion writes both PNGs into the imageset.

## Toward illustration quality: what is realistic

The ceiling of this lane is a clean, well-shaded textbook schematic. Closing
the gap to painted medical illustration takes one or more of:

1. **More craft in `draw.py`**: better anatomical outlines, layered shading,
   and texture. This is incremental and cheap, and improves every plate that
   shares the helpers.
2. **Outlines from real anatomy data**: project openly licensed 3D models
   (BodyParts3D / Z-Anatomy, CC-BY-SA) or trace public-domain Gray's plates
   for torso, rib, liver, and heart shapes. This gives true proportions and
   laterality. CC-BY-SA derivatives must be released under the same licence,
   and CC-BY sources need an in-app credits screen, because the repo and the
   .ipa are public.
3. **AI restyle over a locked drawing** (needs a Gemini or OpenAI key as an
   environment secret): pass the rendered plate as the reference, ask for a
   painted rendering with no text, then re-overlay the labels from the spec and
   reject any output whose anatomy moved. It is a texture pass only; the drawing
   stays the source of truth.
4. **A medical illustrator** for the few highest-stakes plates, with a licence
   that allows a public repo.

None of these replaces the owner's review of the claims.
