#!/usr/bin/env python3
"""Negative controls for promoting app sign-offs into bundled content.

Promotion writes clinical review status into shipped content, so the failure
that matters is not "it did not work" but "it promoted something it should have
refused". Each test below fails if a refusal stops refusing.
"""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import apply_local_reviews as promote


BASE_PROCEDURE = {
    "id": "cricothyrotomy",
    "title": "Cricothyrotomy",
    "lastReviewed": "2026-06-14",
    "version": "0.2.0",
    "reviewerStatus": "Needs Clinical Review",
    "contentSource": "ai-draft",
    "sections": {
        "steps": ["identify the membrane", "incise vertically"],
        "complications": ["bleeding"],
        "contraindications": ["none absolute"],
    },
}


class ApplyLocalReviewsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        resources = Path(self.tmp.name)
        self.procedures_path = resources / "procedures.json"
        self.procedure = copy.deepcopy(BASE_PROCEDURE)
        self._write([self.procedure])
        for name in ("rescue_cards.json", "kits.json"):
            (resources / name).write_text("[]", encoding="utf-8")
        self._patch(promote, "RESOURCES", resources)

    def _patch(self, module, name, value):
        original = getattr(module, name)
        setattr(module, name, value)
        self.addCleanup(setattr, module, name, original)

    def _write(self, items):
        self.procedures_path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def _read(self):
        return json.loads(self.procedures_path.read_text(encoding="utf-8"))[0]

    def _export(self, **overrides):
        record = {
            "disposition": "Reviewed",
            "date": "2026-07-28",
            "contentVersion": "0.2.0",
            "materialFingerprint": promote.procedure_fingerprint(self.procedure),
            "fingerprintVersion": promote.FINGERPRINT_VERSION,
        }
        record.update(overrides)
        payload = {
            "schema": "procedures.local-reviews.v1",
            "exportedAt": "2026-07-28",
            "reviews": {"procedure:cricothyrotomy": record},
        }
        path = Path(self.tmp.name) / "reviews.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    # -- the promotion that should work ---------------------------------

    def test_matching_signoff_promotes_status_and_provenance_together(self):
        self.assertEqual(promote.main([self._export()]), 0)
        item = self._read()
        self.assertEqual(item["reviewerStatus"], "Internally Reviewed")
        # A status claiming review on 'ai-draft' provenance is the exact
        # contradiction the validator rejects.
        self.assertEqual(item["contentSource"], "clinician-reviewed")
        self.assertEqual(item["lastReviewed"], "2026-07-28")

    def test_dry_run_writes_nothing(self):
        promote.main([self._export(), "--dry-run"])
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    # -- refusals -------------------------------------------------------

    def test_refuses_signoff_whose_content_has_since_changed(self):
        stale = self._export()
        changed = copy.deepcopy(self.procedure)
        changed["sections"]["steps"] = ["a materially different step"]
        self._write([changed])

        promote.main([stale])

        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_refuses_review_with_no_fingerprint_unless_explicitly_allowed(self):
        promote.main([self._export(materialFingerprint=None)])
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

        promote.main([self._export(materialFingerprint=None), "--allow-unfingerprinted"])
        self.assertEqual(self._read()["reviewerStatus"], "Internally Reviewed")

    def test_refuses_a_signoff_recorded_against_an_older_field_set(self):
        """Version 1 hashed steps + complications + contraindications. Version 2
        adds shiftMode, equipment, confirmation and troubleshooting.

        A v1 digest cannot be compared against a v2 one: treating it as a match
        would promote a sign-off that never covered the added sections, and
        treating it as a mismatch would claim the content changed when only the
        question did. Neither is true, so it refuses and says which.
        """
        promote.main([self._export(fingerprintVersion=1)])
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_a_record_with_no_version_reads_as_version_one(self):
        # Records written before versioning carry no field at all.
        promote.main([self._export(fingerprintVersion=None)])
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_needs_edits_and_deferred_are_not_signoffs(self):
        for disposition in ("Needs Edits", "Deferred"):
            with self.subTest(disposition=disposition):
                self._write([copy.deepcopy(BASE_PROCEDURE)])
                promote.main([self._export(disposition=disposition)])
                self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_refuses_unknown_procedure_id(self):
        path = Path(self.tmp.name) / "unknown.json"
        path.write_text(
            json.dumps({
                "schema": "procedures.local-reviews.v1",
                "reviews": {"procedure:not_a_real_id": {"disposition": "Reviewed", "date": "2026-07-28", "materialFingerprint": "x"}},
            }),
            encoding="utf-8",
        )
        self.assertEqual(promote.main([str(path)]), 1)

    def test_refuses_wrong_schema(self):
        path = Path(self.tmp.name) / "wrong.json"
        path.write_text(json.dumps({"schema": "something.else.v9", "reviews": {}}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            promote.main([str(path)])

    # -- refusals that have to stay narrow ------------------------------
    #
    # These cover the half of a refusal that is not "did it refuse". A refusal
    # naming the wrong repair costs the reader the work of following it: seven
    # sign-offs were refused with "re-review it in the app so the sign-off
    # covers the sections that were added" when every field they hashed was
    # unchanged and one section was uncovered, and one was sent back to redo a
    # review that could not succeed on the build it was recorded on. Each test
    # here fails if a message stops being specific, and every one still asserts
    # that nothing was promoted.

    def _older_export(self, version=4):
        """A sign-off recorded before seniorPearls entered the material set."""
        return self._export(
            materialFingerprint=promote.procedure_fingerprint(self.procedure, version),
            fingerprintVersion=version,
        )

    def test_an_older_signoff_over_unchanged_text_names_only_the_new_section(self):
        self.procedure["sections"]["seniorPearls"] = ["never covered by a v4 sign-off"]
        self._write([self.procedure])

        with contextlib.redirect_stdout(io.StringIO()) as out:
            promote.main([self._older_export()])
        report = out.getvalue()

        self.assertIn("every field it hashed is unchanged", report)
        self.assertIn("Only seniorPearls is outside it", report)
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_an_older_signoff_over_changed_text_claims_nothing(self):
        changed = copy.deepcopy(self.procedure)
        export = self._older_export()
        changed["sections"]["steps"] = ["a materially different step"]
        self._write([changed])

        with contextlib.redirect_stdout(io.StringIO()) as out:
            promote.main([export])
        report = out.getvalue()

        self.assertIn("covers no part of the current text", report)
        self.assertNotIn("still holds", report)
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_drift_confined_to_an_uneditable_field_says_rebuild_not_re_review(self):
        """The fascia iliaca case. majorBlockMonitoring is hashed, is not
        editable in the app, and is not carried by the edit export, so a device
        on an older bundle produces a digest that re-reviewing cannot fix."""
        export = self._export()
        self.procedure["majorBlockMonitoring"] = True
        self._write([self.procedure])

        with contextlib.redirect_stdout(io.StringIO()) as out:
            promote.main([export])
        report = out.getvalue()

        self.assertIn("majorBlockMonitoring", report)
        self.assertIn("Rebuild the app", report)
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_per_section_digests_name_the_drifted_section(self):
        """The forward contract. Nothing writes sectionFingerprints yet; when
        the app does, a refusal stops guessing."""
        sections = self.procedure["sections"]
        digests = {
            name: promote.fingerprint(list(sections.get(name) or []))
            for name in promote.PROCEDURE_MATERIAL_SECTIONS
        }
        export = self._export(sectionFingerprints=digests)
        self.procedure["sections"]["complications"] = ["a different complication"]
        self._write([self.procedure])

        with contextlib.redirect_stdout(io.StringIO()) as out:
            promote.main([export])
        report = out.getvalue()

        self.assertIn("complications", report)
        self.assertNotIn("steps", report)
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_an_unreconstructable_version_is_still_refused(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            promote.main([self._export(fingerprintVersion=2)])
        report = out.getvalue()

        self.assertIn("cannot reconstruct", report)
        self.assertEqual(self._read()["reviewerStatus"], "Needs Clinical Review")

    def test_promotion_preserves_file_formatting(self):
        promote.main([self._export()])
        raw = self.procedures_path.read_text(encoding="utf-8")
        self.assertNotIn("–", raw, "non-ASCII must stay escaped or the diff explodes")
        self.assertTrue(raw.startswith("[\n  {"), "2-space indent must be preserved")


if __name__ == "__main__":
    unittest.main()
