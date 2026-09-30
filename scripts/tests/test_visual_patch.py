"""visual_patch.py confines a repaint to its box and blends it back cleanly."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

SCRIPT = Path(__file__).resolve().parents[1] / "visual_patch.py"
spec = importlib.util.spec_from_file_location("visual_patch", SCRIPT)
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)


def painting(path: Path) -> Path:
    img = Image.new("RGB", (400, 300), (236, 224, 200))
    ImageDraw.Draw(img).ellipse((150, 100, 250, 200), fill=(200, 60, 50))
    img.save(path)
    return path


class VisualPatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.source = painting(self.dir / "base.png")

    def tearDown(self):
        self.tmp.cleanup()

    def test_crop_writes_upscaled_area_and_record(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render", margin=10)
        self.assertEqual(rec["box"], [130, 80, 270, 220])
        crop = Image.open(self.dir / "render" / "patch-crop.png")
        self.assertGreaterEqual(max(crop.size), vp.MIN_LONG_SIDE)
        self.assertEqual(json.loads((self.dir / "render" / "patch.json").read_text())["sourceSha256"], rec["sourceSha256"])

    def test_merge_changes_nothing_outside_the_box(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render", margin=10)
        repaint = Image.open(self.dir / "render" / "patch-crop.png").convert("RGB")
        ImageDraw.Draw(repaint).rectangle((0, 0, repaint.width, repaint.height), fill=(60, 90, 200))
        repaint.save(self.dir / "repaint.png")
        result = vp.merge(rec, self.dir / "repaint.png", self.dir / "out.jpg", feather=12, colour_match=False)
        self.assertEqual(result["changedOutsideBox"], 0)
        out = Image.open(self.dir / "out.jpg").convert("RGB")
        centre = out.getpixel((200, 150))
        self.assertLess(abs(centre[2] - 200), 20, "the centre takes the repaint")
        self.assertLess(sum(abs(a - b) for a, b in zip(out.getpixel((131, 150)), (236, 224, 200))), 30,
                        "the box edge fades back to the original")

    def test_identity_repaint_is_nearly_invisible(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render", margin=10)
        result = vp.merge(rec, self.dir / "render" / "patch-crop.png", self.dir / "out.png")
        self.assertEqual(result["changedOutsideBox"], 0)
        self.assertLess(result["meanChangeInsideBox"], 3)

    def test_colour_match_pulls_a_tinted_repaint_back(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render", margin=10)
        tinted = Image.open(self.dir / "render" / "patch-crop.png").convert("RGB")
        tinted = ImageChops.add(tinted, Image.new("RGB", tinted.size, (0, 0, 40)))
        tinted.save(self.dir / "tinted.png")
        plain = vp.merge(rec, self.dir / "tinted.png", self.dir / "a.png", colour_match=False)
        matched = vp.merge(rec, self.dir / "tinted.png", self.dir / "b.png", colour_match=True)
        self.assertLess(matched["meanChangeInsideBox"], plain["meanChangeInsideBox"])

    def test_full_size_repaint_contributes_only_its_box(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render", margin=10)
        whole = Image.new("RGB", (400, 300), (20, 160, 60))          # the whole picture drifted
        whole.save(self.dir / "whole.png")
        result = vp.merge(rec, self.dir / "whole.png", self.dir / "out.png", feather=12, colour_match=False)
        self.assertEqual(result["changedOutsideBox"], 0)
        self.assertEqual(Image.open(self.dir / "out.png").convert("RGB").getpixel((200, 150)), (20, 160, 60))

    def test_side_on_the_image_border_is_not_faded(self):
        rec = vp.crop(self.source, (140, 0, 260, 120), self.dir / "render", margin=10)
        self.assertEqual(rec["box"][1], 0)
        solid = Image.new("RGB", (400, 300), (20, 160, 60))
        solid.save(self.dir / "solid.png")
        vp.merge(rec, self.dir / "solid.png", self.dir / "out.png", feather=12, colour_match=False)
        out = Image.open(self.dir / "out.png").convert("RGB")
        self.assertEqual(out.getpixel((200, 0)), (20, 160, 60), "the repaint reaches the top edge")
        self.assertNotEqual(out.getpixel((131, 60)), (20, 160, 60), "an inner side still fades")

    def test_keep_takes_back_only_part_of_the_crop(self):
        rec = vp.crop(self.source, (100, 60, 300, 240), self.dir / "render", margin=0)
        solid = Image.new("RGB", (400, 300), (20, 160, 60))
        solid.save(self.dir / "solid.png")
        result = vp.merge(rec, self.dir / "solid.png", self.dir / "out.png", feather=8, colour_match=False,
                          keep=(100, 60, 300, 120))
        out = Image.open(self.dir / "out.png").convert("RGB")
        self.assertEqual(result["box"], [100, 60, 300, 120])
        self.assertEqual(out.getpixel((200, 90)), (20, 160, 60), "inside the keep box takes the repaint")
        self.assertEqual(out.getpixel((200, 150)), (200, 60, 50), "the rest of the crop stays original")
        self.assertEqual(result["changedOutsideBox"], 0)

    def test_merge_refuses_a_changed_source(self):
        rec = vp.crop(self.source, (140, 90, 260, 210), self.dir / "render")
        Image.new("RGB", (400, 300), (0, 0, 0)).save(self.source)
        with self.assertRaises(ValueError):
            vp.merge(rec, self.dir / "render" / "patch-crop.png", self.dir / "out.png")

    def test_overlay_draws_the_reference_outlines_over_the_painting(self):
        reference = self.dir / "reference.png"
        ref = Image.new("RGB", (800, 600), (255, 255, 255))
        ImageDraw.Draw(ref).rectangle((100, 100, 300, 300), fill=(40, 40, 40))
        ref.save(reference)
        result = vp.overlay(self.source, reference, self.dir / "overlay.png")
        self.assertTrue(result["frameMatches"])
        out = Image.open(self.dir / "overlay.png").convert("RGB")
        self.assertEqual(out.size, (800, 600))
        self.assertEqual(out.getpixel((400, 300)), (200, 60, 50), "the painting shows through, full strength")
        self.assertEqual(out.getpixel((100, 200)), (255, 0, 200), "the reference's outline is drawn over it")

    def test_overlay_flags_a_recomposed_frame(self):
        reference = self.dir / "reference.png"
        Image.new("RGB", (800, 600), (255, 255, 255)).save(reference)
        wide = self.dir / "wide.png"
        Image.new("RGB", (1600, 900), (10, 10, 10)).save(wide)       # came back 16:9
        self.assertFalse(vp.overlay(wide, reference, self.dir / "overlay.png")["frameMatches"])

    def test_crop_rejects_a_box_outside_the_image(self):
        with self.assertRaises(ValueError):
            vp.crop(self.source, (300, 200, 500, 280), self.dir / "render")


if __name__ == "__main__":
    unittest.main()
