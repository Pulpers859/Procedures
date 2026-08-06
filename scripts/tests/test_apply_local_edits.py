"""Round-trip tests for applying app-exported edits back into the repo.

The critical property is diff cleanliness: the shipped procedures.json stores
non-ASCII as escapes ("\\u2013"), so writing with ensure_ascii=False rewrites
every line containing a dash and buries the real change in hundreds of diff
lines. These lock that down, plus the refusal rules.
"""
import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "apply_local_edits.py"
SPEC = importlib.util.spec_from_file_location("apply_local_edits", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

REAL_PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"


class ApplyLocalEditsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.copy = self.tmp / "procedures.json"
        shutil.copy(REAL_PROCEDURES, self.copy)
        self._original = MODULE.PROCEDURES
        MODULE.PROCEDURES = self.copy

    def tearDown(self):
        MODULE.PROCEDURES = self._original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _export(self, edits):
        path = self.tmp / "edits.json"
        path.write_text(json.dumps({
            "schema": MODULE.EXPORT_SCHEMA,
            "exportedAt": "2026-07-27",
            "edits": edits,
        }), encoding="utf-8")
        return path

    def _first_id(self):
        return json.loads(self.copy.read_text(encoding="utf-8"))[0]["id"]

    def test_no_op_export_leaves_the_file_byte_identical(self):
        before = self.copy.read_bytes()
        procedure_id = self._first_id()
        current = json.loads(self.copy.read_text(encoding="utf-8"))[0]["sections"]["steps"]
        export = self._export({procedure_id: {"editedAt": "2026-07-27", "sections": {"steps": current}}})
        MODULE.main([str(export)])
        self.assertEqual(self.copy.read_bytes(), before, "an unchanged edit must not rewrite the file")

    def test_real_edit_changes_only_the_edited_section(self):
        before = self.copy.read_text(encoding="utf-8").splitlines()
        procedure_id = self._first_id()
        export = self._export({procedure_id: {"editedAt": "2026-07-27", "sections": {"seniorPearls": ["One line"]}}})
        MODULE.main([str(export)])
        after = self.copy.read_text(encoding="utf-8").splitlines()

        changed = [line for line in after if line not in before]
        self.assertIn('        "One line"', changed)
        # Escaped non-ASCII must survive untouched, or the diff explodes.
        self.assertIn("\\u2013", self.copy.read_text(encoding="utf-8"))
        self.assertLess(len(changed), 5, f"edit touched too many lines: {changed}")

    def test_dry_run_writes_nothing(self):
        before = self.copy.read_bytes()
        export = self._export({self._first_id(): {"editedAt": "x", "sections": {"seniorPearls": ["Changed"]}}})
        MODULE.main([str(export), "--dry-run"])
        self.assertEqual(self.copy.read_bytes(), before)

    def test_unknown_section_and_unknown_procedure_are_refused(self):
        before = self.copy.read_bytes()
        export = self._export({
            "not_a_real_procedure": {"editedAt": "x", "sections": {"steps": ["x"]}},
            self._first_id(): {"editedAt": "x", "sections": {"bogusSection": ["x"]}},
        })
        MODULE.main([str(export)])
        self.assertEqual(self.copy.read_bytes(), before, "refused edits must not write")

    def test_non_string_lines_are_refused(self):
        before = self.copy.read_bytes()
        export = self._export({self._first_id(): {"editedAt": "x", "sections": {"steps": [1, 2]}}})
        MODULE.main([str(export)])
        self.assertEqual(self.copy.read_bytes(), before)

    def test_version_bump_is_opt_in(self):
        procedure_id = self._first_id()
        export = self._export({procedure_id: {"editedAt": "x", "sections": {"seniorPearls": ["Changed"]}}})
        MODULE.main([str(export)])
        unbumped = json.loads(self.copy.read_text(encoding="utf-8"))[0]["version"]

        export2 = self._export({procedure_id: {"editedAt": "x", "sections": {"seniorPearls": ["Changed again"]}}})
        MODULE.main([str(export2), "--bump-version"])
        bumped = json.loads(self.copy.read_text(encoding="utf-8"))[0]["version"]
        self.assertNotEqual(unbumped, bumped)

    def test_bump_patch_leaves_odd_versions_alone(self):
        self.assertEqual(MODULE.bump_patch("0.2.0"), "0.2.1")
        self.assertEqual(MODULE.bump_patch("1.0"), "1.0")
        self.assertEqual(MODULE.bump_patch("weird"), "weird")

    # -- the blind merge ------------------------------------------------
    #
    # An edit replaces a whole section, so a device working from an older
    # bundle discards whatever the repo gained in between and nothing in the
    # output says so. That is how the fascia iliaca equipment list, corrected
    # against ACEP Sonoguide, was quietly replaced by the pre-correction text.

    def _procedure(self):
        return json.loads(self.copy.read_text(encoding="utf-8"))[0]

    def _run(self, export):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            MODULE.main([str(export)])
        return out.getvalue()

    def test_an_edit_written_against_current_content_is_not_flagged(self):
        procedure = self._procedure()
        export = self._export({procedure["id"]: {
            "editedAt": "2026-08-06",
            "baseMaterialFingerprint": MODULE.review_fingerprint.procedure_fingerprint(procedure),
            "sections": {"steps": ["A deliberate replacement step"]},
        }})
        self.assertNotIn("BLIND MERGE", self._run(export))

    def test_an_edit_written_against_older_content_is_flagged_with_its_material_sections(self):
        procedure = self._procedure()
        export = self._export({procedure["id"]: {
            "editedAt": "2026-08-06",
            "baseMaterialFingerprint": "0" * 64,
            "sections": {"steps": ["Written on a stale bundle"], "anatomy": ["Not material"]},
        }})
        report = self._run(export)
        self.assertIn("BLIND MERGE", report)
        self.assertIn("steps", report)
        # anatomy is edited but not hashed, so naming it would send the reader
        # looking for a sign-off consequence that does not exist.
        self.assertNotIn("anatomy", report.split("BLIND MERGE")[1])

    def test_an_edit_carrying_no_base_is_not_flagged(self):
        """Exports predate the recorded base, and a warning on every record is
        a warning the reader learns to skip."""
        procedure = self._procedure()
        export = self._export({procedure["id"]: {
            "editedAt": "2026-08-06",
            "sections": {"steps": ["No base recorded"]},
        }})
        self.assertNotIn("BLIND MERGE", self._run(export))

    def test_flagging_does_not_refuse_the_edit(self):
        """The reviewer is the authority on their own wording. This reports a
        merge to read carefully; it never withholds one."""
        procedure = self._procedure()
        export = self._export({procedure["id"]: {
            "editedAt": "2026-08-06",
            "baseMaterialFingerprint": "0" * 64,
            "sections": {"steps": ["Written on a stale bundle"]},
        }})
        self._run(export)
        self.assertEqual(self._procedure()["sections"]["steps"], ["Written on a stale bundle"])


if __name__ == "__main__":
    unittest.main()
