# Visual Asset Production Guide

Procedures should use illustrations as clinical content, not decoration.

The goal is a reviewed offline visual that helps a trained clinician avoid one important miss in under 10 seconds. One excellent diagram is better than a gallery.

## Product Fit

Use visuals for:

- Landmark identification
- Probe position
- Danger zone avoidance
- Confirmation pattern
- Setup layout

Do not use visuals for:

- Decorative medical ambience
- Stock clinician photos
- Broad anatomy galleries
- Unreviewed AI-generated anatomy in release builds
- Long instructional sequences that turn the app into a course module

## Production Rule

Each procedure should start with one primary visual asset. Add a second only when it prevents a different high-risk error.

The visual must answer:

- What is the user trying to find, avoid, or confirm?
- What is the bad miss this image prevents?
- What labels are absolutely necessary on a phone?
- What clinical reviewer must approve this before release?

## Style Standard

Use simple schematic medical illustration:

- Clean vector-like shapes exported as bundled raster images
- Large labels readable on iPhone
- High contrast in light and dark mode
- Limited color palette
- Red/orange only for true danger or warning zones
- Blue/cyan for ultrasound/probe concepts
- Green only for confirmation/success states
- No photorealism unless the image must show a real device, kit, or waveform
- No small textbook labels, dense arrows, or multi-panel clutter

Recommended canvas:

- Primary aspect ratio: 4:3
- Minimum export: 1600 x 1200 PNG
- Keep critical labels inside a safe margin so rounded cards do not crop them
- Test at phone width before review

## Clinical Review Status

Treat each visual like procedure text. Track its status in the asset tracker or issue list:

- Needed
- Drafted
- Clinician review needed
- Clinician reviewed
- Bundled
- Deprecated

Do not set `visualAssets.assetName` for release artwork until the image has been clinically reviewed.

## AI Use Policy

AI image tools may be used for internal drafts only:

- Composition sketches
- Style exploration
- Label-placement experiments
- Non-release thumbnails for reviewer discussion

Before release, the final asset should be redrawn, corrected, or explicitly approved by a clinician. Never ship an AI-generated anatomy/procedure diagram solely because it looks plausible.

Two draft render lanes exist, sharing one prompt spec (`docs/visual-assets/gemini_prompts.json`):

- Gemini API: `docs/visual-assets/GEMINI_WORKFLOW.md` and `scripts/generate_visual_assets_gemini.py`.
- Google Antigravity (local desktop app): `docs/visual-assets/ANTIGRAVITY_WORKFLOW.md`, `scripts/export_antigravity_prompts.py`, and `tools/Invoke-AntigravityAgentApi.ps1`.

Draft outputs stay in `tmp/visual-drafts/` (gitignored) and outside the app bundle until reviewed.

## Source Options

Best options, in order:

1. Commission a medical illustrator for the high-risk procedure set.
2. Build an internal reusable vector style and export reviewed PNG assets.
3. Use public-domain or permissively licensed source material only when licensing and clinical accuracy are verified.
4. Use AI drafts only as a starting point for reviewed final artwork.

Avoid screenshots from textbooks, journal figures, medical websites, or commercial apps unless explicit license terms allow bundling in this app.

## File Naming

Use the existing `visualAssets.id` when possible:

```text
<visual_asset_id>.png
```

Examples:

```text
chest_tube_safe_triangle.png
ij_probe_orientation.png
lp_position_landmark.png
canthotomy_inferior_crus.png
```

Keep final bundled files in the app target resources so `ProcedureVisualLoader` can find them by `assetName`.

## Integration Checklist

For each final image:

1. Confirm the matching procedure has a `visualAssets` entry in `Procedures/Resources/procedures.json`.
2. Add the image file to the app bundle resources.
3. Set `assetName` to the bundled filename.
4. Keep `caption` short and clinically useful.
5. Keep `clinicalWarning` focused on the miss the image prevents.
6. Run `python scripts/validate_procedures.py`.
7. Check the procedure detail screen on iPhone width.
8. Confirm dark mode readability.

Structural validation does not prove clinical correctness. Record clinical review separately.

## First Illustration Batch

Prioritize visuals where the image can prevent a major miss:

| Procedure | Visual asset id | Purpose |
| --- | --- | --- |
| Cricothyrotomy | `cric_membrane` | Find membrane and keep incision path midline. |
| Thoracostomy / Chest Tube | `chest_tube_safe_triangle` | Show safe triangle and over-the-rib entry. |
| Central Venous Catheter | `ij_probe_orientation` | Show IJ/carotid relationship, compression, and needle path. |
| Needle Decompression | `needle_decompression_landmarks` | Show correct decompression sites and medial danger zone. |
| Pericardiocentesis | `pericardiocentesis_approach` | Show ultrasound-guided approach and unsafe trajectory risk. |
| Lateral Canthotomy & Cantholysis | `canthotomy_inferior_crus` | Show inferior crus target and globe-safe direction. |
| Lumbar Puncture | `lp_position_landmark` | Show iliac crest line, safe interspace, and trajectory. |
| Paracentesis | `paracentesis_liq_site` | Show LLQ site, inferior epigastric vessel avoidance, and bowel risk. |
| Thoracentesis | `thoracentesis_site` | Show diaphragm boundary and over-the-rib entry. |
| Ultrasound-Guided Peripheral IV | `usgiv_needle_tracking` | Show needle tip vs shaft visualization. |

## Current Gap

The app already has visual metadata and rendering infrastructure. The missing work is final reviewed artwork and bundle integration.

Keep the system restrained: build the first reviewed visual set before expanding into more images per procedure.
