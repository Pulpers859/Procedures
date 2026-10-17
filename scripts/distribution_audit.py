"""Tint map for a distribution plate: where the render differs from its base.

For the independent audit of every distribution plate (owner, 2026-10-15).
Renders the plate's SVG twice in Chromium, with and without its markings,
and compares the two (same resampling, so only the tint differs). Writes, in
`visuals/<id>/render/`:
- tintmap.png: the base in greyscale with every tinted pixel in solid colour
  (the tone that tinted it), so bleed onto a wrong part is obvious;
- tintmap.json: tinted-pixel counts per 50 px base cell and the bounding box
  of the tint on the skeleton and on the body, in base px.

Run: python3 scripts/distribution_audit.py <asset_id> [--threshold 10]
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
K = 1600 / 1200
OY = (1200 - 896 * K) / 2
SPLIT = {"front": 600, "back": 600, "head": 568, "hand": 384, "foot": 305, "side": 600, "head_back": 600}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("asset_id")
    ap.add_argument("--threshold", type=float, default=10.0, help="summed RGB change that counts as tint")
    args = ap.parse_args()
    folder = REPO / "visuals" / args.asset_id
    svg = (folder / f"{args.asset_id}.svg").read_text(encoding="utf-8")
    m = re.search(r'href="\.\./distribution_bases/(\w+)/base\.jpg"', svg)
    view = m.group(1) if m else "front"
    shots = []
    from playwright.sync_api import sync_playwright
    from render_visuals import chromium_path
    with sync_playwright() as pw:
        exe = chromium_path()
        browser = pw.chromium.launch(**({"executable_path": exe} if exe else {}))
        for hide in (False, True):
            page = browser.new_page(viewport={"width": 1600, "height": 1200})
            page.goto((folder / f"{args.asset_id}.svg").as_uri())
            if hide:
                page.evaluate("document.querySelectorAll('.marking').forEach(e => e.style.display = 'none')")
            shots.append(Image.open(io.BytesIO(page.screenshot())).convert("RGB"))
            page.close()
        browser.close()
    # Back to base px: crop the letterbox, scale to 1200 x 896.
    crop = (0, round(OY), 1600, round(OY + 896 * K))
    r, b = (np.asarray(im.crop(crop).resize((1200, 896), Image.LANCZOS)).astype(float) for im in shots)
    diff = np.abs(r - b).sum(axis=2)
    tinted = diff > args.threshold

    grey = np.repeat(b.mean(axis=2, keepdims=True), 3, axis=2) * 0.8 + 40
    out = grey.copy()
    # The tint is multiplied on, so r / b is the tint's colour at its
    # opacity; push it to full strength to show which tone it is.
    ratio = np.clip(r / np.maximum(b, 1), 0, 1)
    push = np.clip(255 - (255 - ratio * 255) * 3, 0, 255)
    out[tinted] = push[tinted]
    Image.fromarray(out.astype("uint8")).save(folder / "render" / "tintmap.png")

    ys, xs = np.nonzero(tinted)
    split = SPLIT.get(view, 600)
    report = {"view": view, "threshold": args.threshold, "tinted_px": int(tinted.sum())}
    for name, sel in (("skeleton", xs < split), ("body", xs >= split)):
        if sel.any():
            report[f"{name}_bbox"] = [int(xs[sel].min()), int(ys[sel].min()), int(xs[sel].max()), int(ys[sel].max())]
    cells = {}
    for y in range(0, 896, 50):
        for x in range(0, 1200, 50):
            n = int(tinted[y:y + 50, x:x + 50].sum())
            if n:
                cells[f"{x},{y}"] = n
    report["cells_50px"] = cells
    (folder / "render" / "tintmap.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(folder / "render" / "tintmap.png", report["tinted_px"], "px tinted;",
          {k: v for k, v in report.items() if k.endswith("bbox")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
