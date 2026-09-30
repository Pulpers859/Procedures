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
    #    Writes render/patched.jpg; base.jpg is never overwritten. REPAINTED
    #    may also be a whole repainted image the size of the source (a
    #    same-chat repair): only the box is taken from it. --keep X0 Y0 X1 Y1
    #    takes back only part of the crop: show Gemini more context than
    #    you let it change.
    python3 scripts/visual_patch.py merge <id> REPAINTED.jpg [--feather 24]

    # Before judging any painting, lay it over the reference it was painted
    # from. Writes render/overlay.png; fails if the frame's shape changed.
    python3 scripts/visual_patch.py overlay <id> PAINTING.jpg

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


def merge(record: dict, repaint_path: Path, out: Path, feather: int = 24, colour_match: bool = True,
          keep: tuple | None = None) -> dict:
    source = ROOT / record["source"] if not Path(record["source"]).is_absolute() else Path(record["source"])
    if sha256(source) != record["sourceSha256"]:
        raise ValueError(f"{source} changed since the crop; crop again")
    image = Image.open(source).convert("RGB")
    x0, y0, x1, y1 = record["box"]
    size = (x1 - x0, y1 - y0)
    original = image.crop((x0, y0, x1, y1))
    repaint = Image.open(repaint_path).convert("RGB")
    if repaint.size == image.size:
        # A whole repainted image (a same-chat repair): take only the box from it.
        repaint = repaint.crop((x0, y0, x1, y1))
    repaint = repaint.resize(size, Image.LANCZOS)
    if keep:
        # Gemini saw the whole crop for context; take back only this part of it.
        k0, k1 = max(keep[0], x0), max(keep[1], y0)
        k2, k3 = min(keep[2], x1), min(keep[3], y1)
        if not (k0 < k2 and k1 < k3):
            raise ValueError(f"keep box {keep} does not overlap the crop {record['box']}")
        repaint = repaint.crop((k0 - x0, k1 - y0, k2 - x0, k3 - y0))
        x0, y0, x1, y1 = k0, k1, k2, k3
        size = (x1 - x0, y1 - y0)
        original = image.crop((x0, y0, x1, y1))

    feather = max(1, min(feather, min(size) // 4))
    # Sides lying on the image border are not faded: something that leaves
    # the frame there (an arm, a cable) must not dissolve at the edge.
    open_sides = (x0 == 0, y0 == 0, x1 == image.width, y1 == image.height)   # left, top, right, bottom
    inset = [0 if side else feather for side in open_sides]
    if colour_match:
        ring = _ring_mask(size, feather)
        repaint = _match_colour(repaint, original, ring)

    # Opaque in the middle, fading to zero at each inner box edge.
    pad = 2 * feather
    w, h = size
    big = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(big).rectangle((pad + inset[0] - (pad if open_sides[0] else 0),
                                   pad + inset[1] - (pad if open_sides[1] else 0),
                                   pad + w - inset[2] - 1 + (pad if open_sides[2] else 0),
                                   pad + h - inset[3] - 1 + (pad if open_sides[3] else 0)), fill=255)
    mask = big.filter(ImageFilter.GaussianBlur(feather / 2)).crop((pad, pad, pad + w, pad + h))
    edge = Image.new("L", size, 255)
    draw = ImageDraw.Draw(edge)
    for i, (is_open, line) in enumerate(zip(open_sides, ((0, 0, 0, h - 1), (0, 0, w - 1, 0), (w - 1, 0, w - 1, h - 1), (0, h - 1, w - 1, h - 1)))):
        if not is_open:
            draw.line(line, fill=0)
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


def overlay(painting: Path, reference: Path, out: Path) -> dict:
    """The reference's outlines in magenta over the painting, fitted by width as the plates place a base."""
    ref = Image.open(reference).convert("RGB")
    image = Image.open(painting).convert("RGB")
    k = ref.width / image.width
    shown = image.resize((ref.width, round(image.height * k)), Image.LANCZOS)
    fitted = Image.new("RGB", ref.size, (255, 255, 255))
    fitted.paste(shown, (0, round((ref.height - shown.height) / 2)))
    edges = ref.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 24 else 0)
    edges = edges.filter(ImageFilter.MaxFilter(3))
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.composite(Image.new("RGB", ref.size, (255, 0, 200)), fitted, edges).save(out)
    aspect, ref_aspect = image.width / image.height, ref.width / ref.height
    return {"out": str(out), "paintingSize": list(image.size), "aspect": round(aspect, 3),
            "referenceAspect": round(ref_aspect, 3), "frameMatches": abs(aspect - ref_aspect) < 0.03}


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
    m.add_argument("--keep", nargs=4, type=int, metavar=("X0", "Y0", "X1", "Y1"),
                   help="take back only this part of the crop (source pixels); the rest stays as it was")
    o = sub.add_parser("overlay", help="lay a painting over its reference before judging it")
    o.add_argument("asset_id")
    o.add_argument("painting", type=Path)
    o.add_argument("--reference", type=Path, help="default visuals/<id>/render/<id>-reference.png")
    args = ap.parse_args(argv)

    asset = VISUALS / args.asset_id
    render = asset / "render"
    if args.cmd == "overlay":
        reference = args.reference or render / f"{args.asset_id}-reference.png"
        if not reference.exists():
            print(f"{reference} not found; run render_visuals.py {args.asset_id} --reference first")
            return 1
        r = overlay(args.painting, reference, render / "overlay.png")
        print(f"{args.asset_id}: {r['out']}; painting {r['paintingSize'][0]}x{r['paintingSize'][1]}, aspect "
              f"{r['aspect']} vs reference {r['referenceAspect']}"
              + ("" if r["frameMatches"] else " - THE FRAME CHANGED: the painting was recomposed; reject it"))
        return 0 if r["frameMatches"] else 1
    if args.cmd == "crop":
        source = args.image or asset / "base.jpg"
        rec = crop(source, tuple(args.box), render, args.margin, render / f"{args.asset_id}-reference.png")
        print(f"{args.asset_id}: crop {rec['box']} of {rec['source']} -> {render / 'patch-crop.png'}"
              + (f" (+ patch-reference.png)" if "reference" in rec else ""))
        return 0

    record = json.loads((render / "patch.json").read_text(encoding="utf-8"))
    result = merge(record, args.repaint, args.out or render / "patched.jpg", args.feather, not args.no_colour_match,
                   tuple(args.keep) if args.keep else None)
    print(f"{args.asset_id}: merged into {result['out']}; changed outside the box: {result['changedOutsideBox']} px; "
          f"mean change inside: {result['meanChangeInsideBox']}")
    return 1 if result["changedOutsideBox"] else 0


if __name__ == "__main__":
    sys.exit(main())
