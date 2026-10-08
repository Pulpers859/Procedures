"""Guards for the code-drawn visuals in `visuals/`.

No browser here: the geometry checks run in `scripts/render_visuals.py`. This
only keeps the committed files honest - the SVG is what `draw.py` produces,
every spec names real labels, and nothing reaches the app bundle unless the
owner approved that exact drawing.
"""

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VISUALS = REPO / "visuals"
ASSETS = REPO / "Assets.xcassets"
PROCEDURES = REPO / "Procedures" / "Resources" / "procedures.json"


def asset_dirs():
    return sorted(p for p in VISUALS.iterdir() if (p / "draw.py").exists())


def build(asset_dir):
    spec = importlib.util.spec_from_file_location(f"draw_{asset_dir.name}", asset_dir / "draw.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def visual_ids():
    data = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    procedures = data if isinstance(data, list) else data["procedures"]
    return {v["id"] for p in procedures for v in (p.get("visualAssets") or [])}


class CodeDrawnVisualsTest(unittest.TestCase):
    def test_there_is_at_least_one_drawing(self):
        self.assertTrue(asset_dirs())

    def test_committed_svg_matches_draw_py(self):
        for asset_dir in asset_dirs():
            with self.subTest(asset=asset_dir.name):
                committed = (asset_dir / f"{asset_dir.name}.svg").read_text(encoding="utf-8")
                self.assertEqual(committed, build(asset_dir),
                                 "run python3 scripts/render_visuals.py " + asset_dir.name)

    def test_spec_names_a_real_slot_and_its_labels_are_drawn(self):
        ids = visual_ids()
        for asset_dir in asset_dirs():
            with self.subTest(asset=asset_dir.name):
                spec = json.loads((asset_dir / "spec.json").read_text(encoding="utf-8"))
                self.assertEqual(spec["assetId"], asset_dir.name)
                self.assertIn(asset_dir.name, ids, "spec must match a visualAssets id")
                svg = (asset_dir / f"{asset_dir.name}.svg").read_text(encoding="utf-8")
                for label, target in spec["labels"].items():
                    self.assertIn(f'data-label="{label}"', svg)
                    self.assertIn(f'id="{target}"', svg)
                for element in spec["requiredElements"]:
                    self.assertIn(f'id="{element}"', svg)

    def test_bundled_plates_ship_as_jpeg(self):
        """Owner, 2026-10-02: lossless PNG pairs made the app ~140 MB. Plates
        ship as JPEG, with a dark file only when the dark render differs."""
        for asset_dir in asset_dirs():
            imageset = ASSETS / f"{asset_dir.name}.imageset"
            if not imageset.exists():
                continue
            with self.subTest(asset=asset_dir.name):
                self.assertEqual(list(imageset.glob("*.png")), [], "re-promote: plates ship as JPEG")
                images = json.loads((imageset / "Contents.json").read_text(encoding="utf-8"))["images"]
                for image in images:
                    self.assertTrue((imageset / image["filename"]).is_file(), image["filename"])

    def test_bundled_drawing_is_the_approved_one(self):
        for asset_dir in asset_dirs():
            imageset = ASSETS / f"{asset_dir.name}.imageset"
            if not imageset.exists():
                continue
            with self.subTest(asset=asset_dir.name):
                review = json.loads((asset_dir / "spec.json").read_text(encoding="utf-8"))["review"]
                # Either line ending: approvals recorded on a Windows checkout
                # hashed CRLF bytes; the repo keeps LF (2026-10-08).
                svg = (asset_dir / f"{asset_dir.name}.svg").read_bytes().replace(b"\r\n", b"\n")
                hashes = {hashlib.sha256(svg).hexdigest(), hashlib.sha256(svg.replace(b"\n", b"\r\n")).hexdigest()}
                self.assertEqual(review["status"], "approved", "bundled without owner approval")
                self.assertIn(review["sourceSha256"], hashes,
                              "drawing changed after approval; re-review before shipping")


if __name__ == "__main__":
    unittest.main()
