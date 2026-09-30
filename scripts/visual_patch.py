#!/usr/bin/env python3
"""Repaint one small area of a painted plate without letting the rest drift.

Gemini repaints the whole image on every edit, so a one-line repair can move
things it was never asked to touch. This confines a repair to a box:

    # 1. Cut the area out (base-image pixels). Writes, under visuals/<id>/render/:
    #    patch-crop.png       the area to send to Gemini (upscaled for detail)
    #    patch-reference.png  the same area of the layout reference, if exported
    #    patch.json           the box and the source file's hash
    python3 scripts/visual_patch.py crop <id> --box X0 Y0 X1 Y1 [--image PATH]

    # 2. The owner repaints only patch-crop.png in Gemini.

    # 3. Blend the repainted crop back with a feathered edge and matched colour.
    #    Writes render/patched.jpg; base.jpg is never overwritten.
    python3 scripts/visual_patch.py merge <id> REPAINTED.jpg [--feather 24]

Merge refuses a source that changed since the crop, and reports how much
changed outside the box (it must be zero) so drift cannot slip in.

Pillow only, so it runs wherever the validation suite runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[1]
VISUALS = ROOT / "visuals"
MIN_LONG_SIDE = 1024          # Gemini paints finer detail on a larger input


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clamp_box(box, size, margin):
    x0, y0, x1, y1 = box
    w, h = size
    return (max(0, x0 - margin), max(0, y0 - margin), min(w, x1 + margin), min(h, y1 + margin))


def crop(source: Path, box, out_dir: Path, margin: int = 56, reference: Path | None = None) -> dict:
    image = Image.open(source).convert("RGB")
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height):
        raise ValueError(f"box {box} is outside the {image.width}x{image.height} image")
    full = clamp_box(box, image.size, margin)
    region = image.crop(full)
    scale = max(1.0, MIN_LONG_SIDE / max(region.size))
    shown = region.resize((round(region.width * scale), round(region.height * scale)), Image.LANCZOS)

    out_dir.mkdir(parents=True, exist_ok=True)
    shown.save(out_dir / "patch-crop.png")
    record = {"source": str(source.resolve().relative_to(ROOT)) if source.resolve().is_relative_to(ROOT) else str(source),
              "sourceSha256": sha256(source), "sourceSize": list(image.size), "box": list(full), "scale": scale}

    if reference and reference.exists():
        ref = Image.open(reference).convert("RGB")
        k = ref.width / image.width
        dy = (ref.height - image.height * k) / 2
        ref_box = (round(full[0] * k), round(full[1] * k + dy), round(full[2] * k), round(full[3] * k + dy))
        ref.crop(ref_box).resize(shown.size, Image.LANCZOS).save(out_dir / "patch-reference.png")
        record["reference"] = str(reference.resolve().relative_to(ROOT)) if reference.resolve().is_relative_to(ROOT) else str(reference)

    (out_dir / "patch.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def _ring_mask(size, feather):
    """White on the band of width `feather` just inside the edge of `size`."""
    w, h = size
    mask = Image.new("L", size, 255)
    if w > 2 * feather and h > 2 * feather:
        ImageDraw.Draw(mask).rectangle((feather, feather, w - feather - 1, h - feather - 1), fill=0)
    return mask


def _match_colour(repaint: Image.Image, original: Image.Image, ring: Image.Image) -> Image.Image:
    """Per-channel gain and offset so the repaint's edge band matches the original's."""
    a, b = ImageStat.Stat(repaint, ring), ImageStat.Stat(original, ring)
    bands = []
    for ch, m_r, s_r, m_o, s_o in zip(repaint.split(), a.mean, a.stddev, b.mean, b.stddev):
        gain = s_o / s_r if s_r > 1e-6 else 1.0
        gain = min(max(gain, 0.6), 1.6)
        bands.append(ch.point(lambda v, g=gain, mr=m_r, mo=m_o: max(0, min(255, round((v - mr) * g + mo)))))
    return Image.merge("RGB", bands)


def merge(record: dict, repaint_path: Path, out: Path, feather: int = 24, colour_match: bool = True) -> dict:
    source = ROOT / record["source"] if not Path(record["source"]).is_absolute() else Path(record["source"])
    if sha256(source) != record["sourceSha256"]:
        raise ValueError(f"{source} changed since the crop; crop again")
    image = Image.open(source).convert("RGB")
    x0, y0, x1, y1 = record["box"]
    size = (x1 - x0, y1 - y0)
    original = image.crop((x0, y0, x1, y1))
    repaint = Image.open(repaint_path).convert("RGB").resize(size, Image.LANCZOS)

    feather = max(1, min(feather, min(size) // 4))
    if colour_match:
        repaint = _match_colour(repaint, original, _ring_mask(size, feather))

    # Opaque in the middle, fading to zero at the box edge.
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((feather, feather, size[0] - feather - 1, size[1] - feather - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather / 2))
    edge = Image.new("L", size, 255)
    ImageDraw.Draw(edge).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=0, width=1)
    mask = ImageChops.multiply(mask, edge)

    blended = Image.composite(repaint, original, mask)
    result = image.copy()
    result.paste(blended, (x0, y0))

    outside = ImageChops.difference(result, image)
    ImageDraw.Draw(outside).rectangle((x0, y0, x1 - 1, y1 - 1), fill=(0, 0, 0))
    hist = outside.convert("L").histogram()
    changed_outside = sum(hist) - hist[0]
    inside = ImageStat.Stat(ImageChops.difference(blended, original)).mean

    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out, quality=95)
    return {"out": str(out), "box": [x0, y0, x1, y1], "changedOutsideBox": changed_outside,
            "meanChangeInsideBox": round(sum(inside) / 3, 2), "feather": feather}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crop", help="cut an area out for repainting")
    c.add_argument("asset_id")
    c.add_argument("--box", nargs=4, type=int, required=True, metavar=("X0", "Y0", "X1", "Y1"), help="base-image pixels")
    c.add_argument("--image", type=Path, help="source painting (default visuals/<id>/base.jpg)")
    c.add_argument("--margin", type=int, default=56,
                   help="clean painting kept round the box, px; must exceed twice the feather (default 56)")
    m = sub.add_parser("merge", help="blend a repainted crop back")
    m.add_argument("asset_id")
    m.add_argument("repaint", type=Path)
    m.add_argument("--out", type=Path, help="default visuals/<id>/render/patched.jpg")
    m.add_argument("--feather", type=int, default=24, help="soft-edge width, px (default 24)")
    m.add_argument("--no-colour-match", action="store_true")
    args = ap.parse_args(argv)

    asset = VISUALS / args.asset_id
    render = asset / "render"
    if args.cmd == "crop":
        source = args.image or asset / "base.jpg"
        rec = crop(source, tuple(args.box), render, args.margin, render / f"{args.asset_id}-reference.png")
        print(f"{args.asset_id}: crop {rec['box']} of {rec['source']} -> {render / 'patch-crop.png'}"
              + (f" (+ patch-reference.png)" if "reference" in rec else ""))
        return 0

    record = json.loads((render / "patch.json").read_text(encoding="utf-8"))
    result = merge(record, args.repaint, args.out or render / "patched.jpg", args.feather, not args.no_colour_match)
    print(f"{args.asset_id}: merged into {result['out']}; changed outside the box: {result['changedOutsideBox']} px; "
          f"mean change inside: {result['meanChangeInsideBox']}")
    return 1 if result["changedOutsideBox"] else 0


if __name__ == "__main__":
    sys.exit(main())
