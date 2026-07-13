# Gemini Visual Asset Workflow

Use Gemini image generation outside the iOS app to create draft clinical illustrations. The app remains offline-first; only reviewed bundled image files should ship.

## Current Google Path

Use either the Gemini API image models or Patrick's logged-in Gemini web app,
depending on what he explicitly asks for in the session. If Patrick says to use
Chrome/Gemini web, do not switch back to API generation.

For the API lane, use:

- `gemini-3-pro-image` for higher-quality production drafts.
- `gemini-3.1-flash-image` for faster or cheaper iteration.

Do not build new workflow around Imagen. Google marks Imagen 4 as deprecated with shutdown on August 17, 2026.

A second, local render lane exists through the Google Antigravity desktop app; it uses the same prompt spec and promotion rule. See `ANTIGRAVITY_WORKFLOW.md`.

## Gemini Web + Reference Overlay Lane

For high-risk procedure visuals, especially after one failed anatomy or label
iteration:

1. Build a small reference board from reputable procedure examples. Extract
   factual constraints only: patient orientation, approach geometry, needle
   direction, target anatomy, and danger anatomy. Do not copy, trace, or
   closely restyle a single reference image.
2. Ask Gemini web for an original anatomy-only base when labels or procedural
   paths have been unreliable. The base should contain no text, labels, dots,
   arrows, or path lines if those will be overlaid deterministically.
3. Add exact labels, leader lines, entry dots, target dots, arrows, and needle
   paths locally in a deterministic overlay.
4. Audit the composite image against `CLINICAL_IMAGE_RUBRIC.md`. A rubric PASS
   makes the image eligible for Patrick's clinical review only.

This overlay lane is preferred when Gemini repeatedly misspells labels, clips
text, adds extra labels, or draws unsafe/random procedure geometry.
It is mandatory after repeated geometry failures on the same asset. For example,
`pericardiocentesis_needle_path` should move to anatomy-only Gemini generation
plus a deterministic syringe/needle overlay if Gemini flips the substernal
needle direction or clears the direction only by routing the path through the
liver.

## Setup

Install the Google GenAI SDK in the Python environment you use for repo tooling:

```powershell
pip install -U google-genai
```

Set your Gemini API key locally:

```powershell
$env:GEMINI_API_KEY = "..."
```

Do not commit API keys, generated secrets, or local credential files.

## Generate Drafts

List available asset ids:

```powershell
python scripts/generate_visual_assets_gemini.py --list
```

Preview a prompt without calling Gemini:

```powershell
python scripts/generate_visual_assets_gemini.py cric_membrane --dry-run
```

Generate one draft:

```powershell
python scripts/generate_visual_assets_gemini.py cric_membrane --model gemini-3-pro-image
```

Generate the first batch:

```powershell
python scripts/generate_visual_assets_gemini.py --all --model gemini-3-pro-image
```

Draft outputs go to:

```text
tmp/visual-drafts/gemini/
```

## Promotion Rule

Do not set `visualAssets.assetName` just because an image was generated.
Do not force one generated image to teach multiple procedural decisions. If a
procedure needs separate landmark geometry, danger-zone avoidance, and
confirmation views, create separate focused `visualAssets` and review them one
at a time.

Promote only after review:

1. Review visual accuracy, label spelling, layout, and phone readability.
2. Record clinical review status.
3. Add the final PNG to the app bundle. Prefer `Procedures/Assets.xcassets/<assetId>.imageset/` for catalog-managed images, matching the currently bundled cricothyrotomy and canthotomy visuals. `Procedures/Resources/Visuals` is also supported when that folder is explicitly added to the Xcode target resources.
4. Confirm the image is included in the Xcode target resources.
5. Set `visualAssets.assetName` in `Procedures/Resources/procedures.json`.
6. Run `python scripts/validate_procedures.py`.

Structural validation does not prove clinical correctness.
