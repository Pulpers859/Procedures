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

## Making a plate: read PLAYBOOK.md

The owner-approved workflow (code layout, reference, the owner's Gemini
repaint, review, code-drawn markings and labels, approval, build) is in
[`PLAYBOOK.md`](PLAYBOOK.md), with the prompts that worked, the repair rules,
and what failed. This file is the reference for the tools it uses:

- `render_visuals.py <id>`: render and check; `--reference` exports the
  unlabelled reference; `--record-approval --promote` after the owner approves.
- `visual_patch.py overlay | crop | merge`: lay a painting over its reference;
  repaint one area without letting the rest drift.

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
- Labels: 56 px Inter (about 12 pt on the card), nouns only, two to three
  per image (a nerve-block anatomy plate up to five if the card is not
  crowded), each leader ending in a dot inside its structure.
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
