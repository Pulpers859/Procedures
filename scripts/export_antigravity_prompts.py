"""Export Antigravity-ready prompt files from the shared visual prompt spec.

Antigravity is driven with @-path prompt files (multi-line prompts passed as
plain strings are truncated to their first line). This script writes one prompt
file per visual asset under tmp/visual-drafts/antigravity/<assetId>/ using the
same prompt spec as the Gemini API lane, plus Antigravity-specific output and
sandbox instructions. See docs/visual-assets/ANTIGRAVITY_WORKFLOW.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from generate_visual_assets_gemini import REPO_ROOT, asset_map, build_prompt, load_specs

DEFAULT_PROMPTS = REPO_ROOT / "docs" / "visual-assets" / "gemini_prompts.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "visual-drafts" / "antigravity"

ANTIGRAVITY_FOOTER = """
Antigravity output instructions:
- Generate the image now and save it as a PNG at exactly this path:
  {image_path}
- Save files only inside that folder. Never read, create, or modify anything
  else in this repository, and never commit or push.
- Do not score, audit, or praise your own output. The controlling agent audits
  the saved image externally.
- Do not inspect the repository or run code. This conversation is a render lab
  only.
"""


def export_asset(asset: dict[str, Any], out_dir: Path, iteration: int) -> Path:
    topic_dir = out_dir / asset["assetId"]
    image_path = topic_dir / f"{asset['assetId']}_iter{iteration}.png"
    prompt = build_prompt(asset) + ANTIGRAVITY_FOOTER.format(image_path=image_path)
    prompt_path = topic_dir / f"{iteration:02d}_image_prompt.txt"
    topic_dir.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    return prompt_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Antigravity @-path prompt files for visual drafts.")
    parser.add_argument("asset_ids", nargs="*", help="Visual asset id(s) to export.")
    parser.add_argument("--all", action="store_true", help="Export every asset in the prompt spec.")
    parser.add_argument("--list", action="store_true", help="List available asset ids.")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS, help="Path to the prompt spec JSON.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Antigravity sandbox directory.")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration number for prompt and image names.")
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

    for asset_id in selected_ids:
        prompt_path = export_asset(assets[asset_id], args.out_dir, args.iteration)
        print(prompt_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
