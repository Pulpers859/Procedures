# Gemini Visual Asset Workflow

Use Gemini image generation outside the iOS app to create draft clinical illustrations. The app remains offline-first; only reviewed bundled image files should ship.

## Current Google Path

Use the Gemini API image models:

- `gemini-3-pro-image` for higher-quality production drafts.
- `gemini-3.1-flash-image` for faster or cheaper iteration.

Do not build new workflow around Imagen. Google marks Imagen 4 as deprecated with shutdown on August 17, 2026.

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

Promote only after review:

1. Review visual accuracy, label spelling, layout, and phone readability.
2. Record clinical review status.
3. Move the final PNG into `Procedures/Resources/Visuals`.
4. Add it to the Xcode target resources.
5. Set `visualAssets.assetName` in `Procedures/Resources/procedures.json`.
6. Run `python scripts/validate_procedures.py`.

Structural validation does not prove clinical correctness.
