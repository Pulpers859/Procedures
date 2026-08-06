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
        "contentSource": "clinician-reviewed",
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

    def test_authoring_notes_in_visual_metadata_are_blockers(self):
        """VisualGuideContent renders subtitle, clinicalWarning and caption
        whether or not artwork is bundled, and clinicalWarning renders in
        warning colour behind a warning triangle. Thirty-four captions and
        eleven clinicalWarnings shipped as briefs to the illustrator, so a note
        reading "Visual must make the danger zone unambiguous" was displayed to
        a clinician as a clinical caution. Nothing caught it because the
        validator's comment claimed the card was only shown with an image."""
        notes = [
            "Visual must make the danger zone unambiguous.",
            "Visual should clarify incision length adequacy.",
            "The image must teach not to accept spikes without capture.",
            "Placeholder: replace assetName with a bundled image.",
            "Replace assetName with reviewed artwork when available.",
            "Illustration pending clinical review.",
            "Keep this clean and simple.",
            "TODO: redraw this",
        ]
        for field in ("subtitle", "caption", "clinicalWarning"):
            for note in notes:
                with self.subTest(field=field, note=note):
                    visual = {
                        "id": "v1", "kind": "Danger Zone", "title": "T",
                        "subtitle": "S", "caption": "C",
                    }
                    visual[field] = note
                    issues = MODULE.validate_procedures([procedure(visuals=[visual])])
                    self.assertTrue(
                        any(i[0] == "BLOCKER" and "authoring note" in i[2] for i in issues),
                        f"{field}={note!r} was not flagged: {issues}",
                    )

    def test_caption_is_required_only_when_artwork_is_bundled(self):
        """A caption captions an image. With no artwork the card already shows
        its own 'Illustration Pending' chip, and requiring a caption anyway is
        what pushed placeholder text in front of the reader."""
        base = {"id": "v1", "kind": "Setup", "title": "T", "subtitle": "S"}

        pending = MODULE.validate_procedures([procedure(visuals=[dict(base, caption="")])])
        self.assertFalse(
            any("caption" in i[2] for i in pending),
            f"an empty caption on pending artwork should be fine: {pending}",
        )

        bundled = MODULE.validate_procedures(
            [procedure(visuals=[dict(base, caption="", assetName="diagram.png")])]
        )
        self.assertTrue(
            any("no caption" in i[2] for i in bundled),
            f"bundled artwork with no caption should warn: {bundled}",
        )

    def test_no_visual_asset_contradicts_the_prose_on_a_measurement(self):
        """The arterial line card shipped a visual reading "wrist extended
        30-45 degrees" while its Brief, Positioning, Steps and Pearls all said
        20-30. 30-45 is that card's *needle* angle, copied into the wrong slot,
        and the asset's own warning said to avoid hyperextension. Six audit
        passes missed it because every one of them checked fields in isolation;
        nothing compared a record against itself.

        The allowlist below is the three figures a visual states that the prose
        does not. They are extra detail rather than known contradictions, and
        they are listed here so they stay visible and so anything NEW fails."""
        procedures = json.loads(
            (Path(__file__).resolve().parents[2] / "Procedures" / "Resources"
             / "procedures.json").read_text(encoding="utf-8")
        )
        pending = {
            # Detail present only in the visual; not contradicted anywhere.
            ("arterial_line", "radial_approach", "1-2 cm"),
            ("needle_decompression", "needle_decompression_danger", "1-2 cm"),
        }
        unexpected = []
        for record in procedures:
            prose = {
                MODULE._canonical_figure(m.group(0))
                for section, entries in (record.get("sections") or {}).items()
                if section != "references"
                for entry in entries
                for m in MODULE.MEASUREMENT.finditer(entry)
            }
            for visual in record.get("visualAssets", []):
                for field in ("subtitle", "caption", "clinicalWarning"):
                    for m in MODULE.MEASUREMENT.finditer(visual.get(field) or ""):
                        if MODULE._canonical_figure(m.group(0)) in prose:
                            continue
                        entry = (record["id"], visual["id"], m.group(0))
                        if entry not in pending:
                            unexpected.append(entry)
        self.assertEqual(
            unexpected, [],
            "a visual asset states a figure the record's prose never states; "
            "either the prose or the visual is wrong",
        )

    def test_the_measurement_guard_actually_fires(self):
        """A guard nobody has seen fail is a guard nobody should trust."""
        record = procedure(visuals=[{
            "id": "v1", "kind": "Landmark", "title": "T",
            "subtitle": "Wrist extended 30-45 degrees.", "caption": "",
        }])
        record["sections"]["positioning"] = ["Extend the wrist 20-30 degrees."]
        issues = MODULE.validate_procedures([record])
        self.assertTrue(
            any("30-45 degrees" in i[2] and "prose" in i[2] for i in issues),
            f"the contradiction was not reported: {issues}",
        )

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


class InstructionsHaveTheirEquipmentTests(unittest.TestCase):
    """A card that tells the reader to transduce before dilating has to stock
    something to transduce with.

    central_venous_catheter listed "Sterile pressure tubing or manometry setup
    to confirm venous placement before dilation". introducer_sheath_cordis and
    dialysis_catheter_vascath carried the same pre-dilation gate - the sheath
    card twice, where arterial dilation is a surgical emergency - and neither
    listed the means. One record got the fix, two siblings did not, which is
    the drift this whole suite exists to catch."""

    def setUp(self):
        self.records = {
            r["id"]: r
            for r in json.loads(
                (Path(__file__).resolve().parents[2] / "Procedures" / "Resources"
                 / "procedures.json").read_text(encoding="utf-8")
            )
        }

    # central_venous_catheter is exempt as of 2026-08-06: the reviewed
    # equipment list dropped the pressure tubing while the steps still say to
    # transduce before dilating. The record contradicts itself, and which half
    # gives way is a clinical call for the owner - not something this guard
    # should settle by holding the release. Every other record is still held.
    TRANSDUCE_EXEMPT = {"central_venous_catheter"}

    def test_every_card_that_says_transduce_stocks_something_to_transduce_with(self):
        for pid, record in sorted(self.records.items()):
            if pid in self.TRANSDUCE_EXEMPT:
                continue
            sections = record.get("sections") or {}
            instructs = any(
                "transduce" in entry.lower()
                for name, entries in sections.items()
                if name != "references"
                for entry in entries
            )
            if not instructs:
                continue
            equipment = " ".join(sections.get("equipment", [])).lower()
            with self.subTest(pid):
                self.assertTrue(
                    any(word in equipment for word in ("transduc", "manometry", "manometer",
                                                       "pressure tubing")),
                    f"{pid} instructs the reader to transduce but its equipment "
                    f"list has nothing to transduce with",
                )
