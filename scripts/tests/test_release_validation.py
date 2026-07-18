import importlib.util
import io
from pathlib import Path
from contextlib import redirect_stderr
import json
import struct
import tempfile
import unittest
from unittest import mock
import zlib


SCRIPT = Path(__file__).resolve().parents[1] / "validate_procedures.py"
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def item(title="Test", status="Externally Reviewed", references=None):
    return {
        "id": "test",
        "title": title,
        "reviewerStatus": status,
        "references": references or ["Smith et al. 2026."],
    }


def procedure(status="Externally Reviewed", references=None, visuals=None):
    value = item(status=status)
    value["sections"] = {"references": references or ["Smith et al. 2026."]}
    if visuals is not None:
        value["visualAssets"] = visuals
    return value


def valid_png():
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00\x00\x00\x00\xff")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


def png_with_short_scanline():
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


class ReleaseValidationTests(unittest.TestCase):
    def test_release_rejects_unreviewed_status_for_every_content_type(self):
        for status in (None, "Unknown", "Draft", "Needs Clinical Review"):
            with self.subTest(status=status, kind="procedure"):
                self.assertTrue(MODULE.release_readiness_issues([procedure(status=status)], [], []))
            with self.subTest(status=status, kind="rescue"):
                self.assertTrue(MODULE.release_readiness_issues([], [item(status=status)], []))
            with self.subTest(status=status, kind="kit"):
                self.assertTrue(MODULE.release_readiness_issues([], [], [item(status=status)]))

    def test_release_accepts_each_reviewed_status(self):
        for status in MODULE.REVIEWED_STATUSES:
            with self.subTest(status=status):
                self.assertEqual(
                    MODULE.release_readiness_issues(
                        [procedure(status=status)],
                        [item(status=status)],
                        [item(status=status)],
                    ),
                    [],
                )

    def test_release_allows_procedure_without_visual_metadata(self):
        self.assertEqual(MODULE.release_readiness_issues([procedure()], [], []), [])

    def test_release_rejects_placeholder_and_missing_visuals(self):
        for asset_name in (None, "", "   ", "does_not_exist.png"):
            with self.subTest(asset_name=asset_name):
                issues = MODULE.release_readiness_issues(
                    [procedure(visuals=[{"id": "visual", "assetName": asset_name}])],
                    [],
                    [],
                )
                self.assertTrue(any("visual" in issue[2] for issue in issues))

    def test_release_rejects_placeholder_and_generic_references(self):
        references = [
            "Procedures starter content. Replace with formal reviewer-approved references before release.",
            "Standard emergency medicine regional anesthesia literature.",
        ]
        for reference in references:
            with self.subTest(reference=reference):
                issues = MODULE.release_readiness_issues(
                    [procedure(references=[reference])],
                    [],
                    [],
                )
                self.assertTrue(any("traceable" in issue[2] for issue in issues))

    def test_release_rejects_blank_and_non_string_references(self):
        for reference in ("", "   ", None, 42, {"citation": "Smith"}):
            with self.subTest(reference=reference):
                issues = MODULE.release_readiness_issues(
                    [procedure(references=[reference])],
                    [],
                    [],
                )
                self.assertTrue(any("reference" in issue[2] for issue in issues))

    def test_visual_asset_requires_valid_bundled_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resources = root / "Procedures" / "Resources"
            assets = root / "Procedures" / "Assets.xcassets"
            resources.mkdir(parents=True)
            assets.mkdir(parents=True)
            project = root / "project.pbxproj"
            image = resources / "valid.png"
            image.write_bytes(valid_png())

            with mock.patch.object(MODULE, "ROOT", root), \
                 mock.patch.object(MODULE, "RESOURCES", resources), \
                 mock.patch.object(MODULE, "ASSET_CATALOG", assets), \
                 mock.patch.object(MODULE, "PROJECT_FILE", project):
                project.write_text("/* Begin PBXResourcesBuildPhase section */\n/* End PBXResourcesBuildPhase section */")
                self.assertFalse(MODULE.visual_asset_exists("valid.png"))

                project.write_text("/* Begin PBXResourcesBuildPhase section */\nResources/valid.png in Resources */\n/* End PBXResourcesBuildPhase section */")
                self.assertTrue(MODULE.visual_asset_exists("valid.png"))

    def test_visual_asset_rejects_directory_empty_and_corrupt_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resources = root / "Procedures" / "Resources"
            assets = root / "Procedures" / "Assets.xcassets"
            resources.mkdir(parents=True)
            assets.mkdir(parents=True)
            project = root / "project.pbxproj"
            project.write_text("/* Begin PBXResourcesBuildPhase section */\nResources/empty.png in Resources */\nResources/corrupt.png in Resources */\n/* End PBXResourcesBuildPhase section */")
            (resources / "empty.png").write_bytes(b"")
            (resources / "corrupt.png").write_bytes(b"not an image")

            with mock.patch.object(MODULE, "ROOT", root), \
                 mock.patch.object(MODULE, "RESOURCES", resources), \
                 mock.patch.object(MODULE, "ASSET_CATALOG", assets), \
                 mock.patch.object(MODULE, "PROJECT_FILE", project):
                for asset_name in (".", "empty.png", "corrupt.png"):
                    with self.subTest(asset_name=asset_name):
                        self.assertFalse(MODULE.visual_asset_exists(asset_name))

    def test_asset_catalog_image_must_be_valid_and_catalog_bundled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resources = root / "Procedures" / "Resources"
            assets = root / "Procedures" / "Assets.xcassets"
            image_set = assets / "diagram.imageset"
            resources.mkdir(parents=True)
            image_set.mkdir(parents=True)
            project = root / "project.pbxproj"
            (image_set / "diagram.png").write_bytes(valid_png())
            (image_set / "Contents.json").write_text(json.dumps({"images": [{"filename": "diagram.png"}]}))

            with mock.patch.object(MODULE, "ROOT", root), \
                 mock.patch.object(MODULE, "RESOURCES", resources), \
                 mock.patch.object(MODULE, "ASSET_CATALOG", assets), \
                 mock.patch.object(MODULE, "PROJECT_FILE", project):
                project.write_text("/* Begin PBXResourcesBuildPhase section */\n/* End PBXResourcesBuildPhase section */")
                self.assertFalse(MODULE.visual_asset_exists("diagram"))
                project.write_text("/* Begin PBXResourcesBuildPhase section */\nAssets.xcassets in Resources */\n/* End PBXResourcesBuildPhase section */")
                self.assertTrue(MODULE.visual_asset_exists("diagram"))
                (image_set / "diagram.png").write_bytes(b"corrupt")
                self.assertFalse(MODULE.visual_asset_exists("diagram"))

    def test_image_decoder_rejects_missing_pixel_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed_png = root / "short.png"
            malformed_jpeg = root / "no-scan.jpg"
            malformed_png.write_bytes(png_with_short_scanline())
            malformed_jpeg.write_bytes(
                b"\xff\xd8\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03"
                b"\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9"
            )
            self.assertFalse(MODULE.image_file_is_valid(malformed_png))
            self.assertFalse(MODULE.image_file_is_valid(malformed_jpeg))

    def test_unknown_argument_uses_argparse_exit_code_two(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as context:
                MODULE.parse_args(["--not-a-real-option"])
        self.assertEqual(context.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
