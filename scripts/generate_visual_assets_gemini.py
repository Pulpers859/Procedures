"""Generate draft procedure visuals with Gemini image models.

The prompt rules enforced in build_prompt() are governed by
docs/visual-assets/IMAGE_GENERATION_CONSTITUTION.md. When you change the
labeling or style rules here, update the constitution and CLINICAL_IMAGE_RUBRIC.md
so generation and grading stay in sync.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROMPTS = REPO_ROOT / "docs" / "visual-assets" / "gemini_prompts.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "visual-drafts" / "gemini"
DEFAULT_MODEL = "gemini-3-pro-image"


def load_specs(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def asset_map(specs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["assetId"]: item for item in specs["assets"]}


def build_prompt(asset: dict[str, Any]) -> str:
    required_labels = asset.get("requiredLabels", [])
    if required_labels:
        labels = "\n".join(f"- {label}" for label in required_labels)
        label_contract = f"""Required text labels, verbatim:
{labels}

Render every required label exactly once, with exactly that spelling. Do not add
any other text anywhere in the image: no title, heading, subtitle, caption,
watermark, signature, logo, parenthetical explanation, duplicated label, or
invented anatomy label.

Labeling rules:
- Every label names an anatomical structure or the single target the leader
  line touches. Labels are nouns, never instructions. Do not write directive,
  imperative, or warning text (for example, no "cut away from", "avoid",
  "do not", "danger"). Convey direction or motion with an arrow, not words.
- Each label must sit on the side of the image nearest the structure it
  points to, and its leader line must land exactly on that structure. Correct,
  unambiguous placement always wins over visual symmetry.
"""
        label_style = """- Large readable labels in a soft, rounded, humanist sans-serif, with
  generous letter, word, and line spacing so words never appear to touch.
- Position each label freely wherever its leader line can reach the correct
  structure by the shortest clear path. Do NOT force the labels into two even
  columns and do NOT balance the count per side; an uneven layout with correct
  placement is required over a symmetric layout that mislabels anything."""
    else:
        label_contract = """Text policy:
Render no text anywhere in the image: no labels, title, heading, subtitle,
caption, watermark, signature, logo, letters, numbers, parenthetical
explanation, or invented anatomy label. Teach the procedure through anatomy,
trajectory, arrows, shading, and composition instead of words.
"""
        label_style = """- No in-image labels. Use visual hierarchy, arrows, target dots, color, and
  composition to make the teaching point readable at phone size."""

    return f"""Create one clinical illustration draft for the Procedures iOS app.

Procedure: {asset["procedure"]}
Visual asset id: {asset["assetId"]}
Visual kind: {asset["kind"]}
Clinical purpose: {asset["purpose"]}

Primary request:
{asset["prompt"]}

{label_contract}
Trajectory rules:
- For any arrow, needle, incision, or tool trajectory, start the path at the
  real entry point. If showing both a correct and incorrect path, use the same
  entry point when that is the clinical comparison. No looping, curling, or
  arrows starting inside the target organ.

Style requirements:
- Premium medical illustration, not stock art.
- Clean true 4:3 composition for an iPhone procedure card; do not render a
  near-square canvas unless the asset spec explicitly requests it.
{label_style}
- Tighten the crop so the key anatomy fills most of the frame. Keep only
  enough margin for required labels or procedural overlays; avoid large
  empty low-information areas.
- Sparse visual hierarchy: one main teaching point, no gallery layout.
- Do not cram separate teaching points into one frame. If another visual asset
  covers a different concept, keep this image focused on its own purpose.
- High contrast, light background, calm clinical palette.
- Red or orange only for danger, incision, or warning.
- Blue or cyan for ultrasound or landmark guidance.

Clinical safety constraints:
- This is a draft for clinician review, not final medical authority.
- Do not invent extra clinical claims beyond the requested labels and anatomy.
- Keep the diagram schematic and focused on the miss the visual prevents.

Avoid:
{asset["avoid"]}
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def inline_data_bytes(inline_data: Any) -> bytes:
    data = getattr(inline_data, "data", None)
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return base64.b64decode(data)
    raise TypeError("Unsupported inline image payload returned by Gemini.")


def inline_data_extension(inline_data: Any) -> str:
    mime_type = getattr(inline_data, "mime_type", "") or getattr(inline_data, "mimeType", "")
    if mime_type == "image/jpeg":
        return "jpg"
    return "png"


def response_parts(response: Any) -> list[Any]:
    parts: list[Any] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        parts.extend(getattr(content, "parts", []) or [])
    return parts


def generate_asset(
    asset: dict[str, Any],
    model: str,
    aspect_ratio: str,
    resolution: str,
    out_dir: Path,
    overwrite: bool,
) -> list[Path]:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise SystemExit("Missing dependency. Install with: pip install -U google-genai") from exc

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set. Set it locally before live generation.")

    if os.environ.get("GEMINI_API_KEY"):
        os.environ.pop("GOOGLE_API_KEY", None)

    prompt = build_prompt(asset)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = out_dir / f"{asset['assetId']}.prompt.txt"
    notes_path = out_dir / f"{asset['assetId']}.notes.txt"
    write_text(prompt_path, prompt)

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution,
                ),
            ),
        )
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        prefix = f"Gemini API request failed"
        if status:
            prefix += f" ({status})"
        raise SystemExit(f"{prefix}: {exc}") from exc

    saved: list[Path] = [prompt_path]
    notes: list[str] = []
    image_index = 1
    for part in response_parts(response):
        text = getattr(part, "text", None)
        if text:
            notes.append(text)

        inline_data = getattr(part, "inline_data", None)
        if inline_data:
            extension = inline_data_extension(inline_data)
            suffix = "" if image_index == 1 else f"-{image_index}"
            image_path = out_dir / f"{asset['assetId']}{suffix}.{extension}"
            if image_path.exists() and not overwrite:
                raise SystemExit(f"Refusing to overwrite existing file: {image_path}")
            image_path.write_bytes(inline_data_bytes(inline_data))
            saved.append(image_path)
            image_index += 1

    metadata = {
        "assetId": asset["assetId"],
        "procedure": asset["procedure"],
        "model": model,
        "aspectRatio": aspect_ratio,
        "resolution": resolution,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "draft-needs-clinician-review",
    }
    write_text(out_dir / f"{asset['assetId']}.metadata.json", json.dumps(metadata, indent=2) + "\n")
    saved.append(out_dir / f"{asset['assetId']}.metadata.json")

    if notes:
        write_text(notes_path, "\n\n".join(notes))
        saved.append(notes_path)

    if image_index == 1:
        raise SystemExit(f"Gemini returned no image for {asset['assetId']}. Check notes and model access.")

    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate draft procedure visuals with Gemini image models.")
    parser.add_argument("asset_ids", nargs="*", help="Visual asset id(s) to generate.")
    parser.add_argument("--all", action="store_true", help="Generate every asset in the prompt spec.")
    parser.add_argument("--list", action="store_true", help="List available asset ids.")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling Gemini.")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS, help="Path to Gemini prompt spec JSON.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Draft output directory.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini image model.")
    parser.add_argument("--aspect-ratio", default=None, help="Image aspect ratio, defaults to prompt spec value.")
    parser.add_argument("--resolution", default=None, help="Image size, defaults to prompt spec value.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing draft outputs.")
    args = parser.parse_args()

    specs = load_specs(args.prompts)
    assets = asset_map(specs)

    if args.list:
        for asset_id in assets:
            print(asset_id)
        return 0

    selected_ids = list(assets) if args.all else args.asset_ids
    if not selected_ids:
        parser.error("Provide asset id(s), --all, or --list.")

    missing = [asset_id for asset_id in selected_ids if asset_id not in assets]
    if missing:
        raise SystemExit(f"Unknown asset id(s): {', '.join(missing)}")

    aspect_ratio = args.aspect_ratio or specs.get("defaultAspectRatio", "4:3")
    resolution = args.resolution or specs.get("defaultResolution", "2K")

    for asset_id in selected_ids:
        asset = assets[asset_id]
        prompt = build_prompt(asset)
        if args.dry_run:
            print(f"--- {asset_id} ---")
            print(prompt)
            continue

        saved = generate_asset(
            asset=asset,
            model=args.model,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            out_dir=args.out_dir,
            overwrite=args.overwrite,
        )
        print(f"{asset_id}:")
        for path in saved:
            print(f"  {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
