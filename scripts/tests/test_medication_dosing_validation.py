"""Negative controls for `medicationDosing` — systemic drug doses (RSI).

These are target doses of induction agents and paralytics, not the local
anaesthetic *ceilings* in `dosing`. Three failures are unrecoverable at the
bedside and every rule here exists for one of them: a unit typo is a
1000-fold error, an inverted range is unreadable at speed, and a block that
names a paralytic dose while saying nothing about induction invites paralysis
without anaesthesia.

The fingerprint tests matter just as much. A drug dose that moves without
moving the fingerprint leaves every sign-off reading "Reviewed" over a dose
nobody re-read.
"""

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPTS / "validate_procedures.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

sys.path.insert(0, str(SCRIPTS))
import apply_local_reviews as promote  # noqa: E402


def medication(**overrides):
    value = {
        "medication": "Rocuronium",
        "role": "Neuromuscular blocker",
        "doseLowPerKg": 0.6,
        "doseHighPerKg": 1.2,
        "unit": "mg/kg",
        "onset": None,
        "durationNote": "lasts about 45 min",
        "caution": None,
    }
    value.update(overrides)
    return value


def block(**overrides):
    value = {
        "indication": "Rapid sequence induction and intubation, adult.",
        "inductionRequirement": "Give an induction agent with the paralytic.",
        "sourceNote": "Owner-accepted source.",
        "medications": [medication()],
    }
    value.update(overrides)
    return value


def issues_for(block_value):
    return MODULE.medication_dosing_issues(
        [{"title": "Endotracheal Intubation", "medicationDosing": block_value}]
    )


def blockers_for(block_value):
    return [text for level, _, text in issues_for(block_value) if level == "BLOCKER"]


class MedicationDosingValidationTests(unittest.TestCase):
    def test_a_well_formed_block_passes(self):
        self.assertEqual(issues_for(block()), [])

    def test_absent_block_is_not_an_issue(self):
        """Only intubation carries one; 54 other records must stay silent."""
        self.assertEqual(MODULE.medication_dosing_issues([{"title": "T"}]), [])

    def test_a_wrong_unit_is_a_blocker(self):
        """mg vs mg/kg on a 70 kg patient is the whole dose, not a typo."""
        bad = block(medications=[medication(unit="mg")])
        self.assertTrue(any("expected one of" in text for text in blockers_for(bad)))

    def test_an_unknown_unit_is_a_blocker(self):
        bad = block(medications=[medication(unit="units/kg")])
        self.assertTrue(blockers_for(bad))

    def test_an_inverted_range_is_a_blocker(self):
        bad = block(medications=[medication(doseLowPerKg=1.2, doseHighPerKg=0.6)])
        self.assertTrue(any("inverted" in text for text in blockers_for(bad)))

    def test_a_single_value_dose_is_allowed(self):
        self.assertEqual(issues_for(block(medications=[medication(doseHighPerKg=None)])), [])

    def test_a_zero_or_negative_dose_is_a_blocker(self):
        for value in (0, -1.0):
            with self.subTest(value=value):
                bad = block(medications=[medication(doseLowPerKg=value)])
                self.assertTrue(blockers_for(bad))

    def test_a_non_numeric_dose_is_a_blocker(self):
        bad = block(medications=[medication(doseLowPerKg="0.6")])
        self.assertTrue(blockers_for(bad))

    def test_dropping_the_induction_requirement_is_a_blocker(self):
        """The guard against a paralytic dose with no anaesthesia."""
        bad = block(inductionRequirement="   ")
        self.assertTrue(any("inductionRequirement" in text for text in blockers_for(bad)))

    def test_an_empty_medication_list_is_a_blocker(self):
        self.assertTrue(blockers_for(block(medications=[])))

    def test_a_missing_source_note_is_a_blocker(self):
        self.assertTrue(any("sourceNote" in text for text in blockers_for(block(sourceNote=""))))


class MedicationDosingFingerprintTests(unittest.TestCase):
    """A dose change must invalidate a sign-off."""

    def base(self, med_block):
        return {"sections": {}, "medicationDosing": med_block}

    def test_changing_a_dose_moves_the_fingerprint(self):
        before = promote.procedure_fingerprint(self.base(block()))
        after = promote.procedure_fingerprint(
            self.base(block(medications=[medication(doseHighPerKg=1.4)]))
        )
        self.assertNotEqual(before, after)

    def test_changing_the_unit_moves_the_fingerprint(self):
        before = promote.procedure_fingerprint(self.base(block()))
        after = promote.procedure_fingerprint(
            self.base(block(medications=[medication(unit="mcg/kg")]))
        )
        self.assertNotEqual(before, after)

    def test_changing_a_caution_moves_the_fingerprint(self):
        """Contraindication text is as material as the number."""
        before = promote.procedure_fingerprint(self.base(block()))
        after = promote.procedure_fingerprint(
            self.base(block(medications=[medication(caution="Avoid in hyperkalaemia.")]))
        )
        self.assertNotEqual(before, after)

    def test_changing_the_induction_requirement_moves_the_fingerprint(self):
        before = promote.procedure_fingerprint(self.base(block()))
        after = promote.procedure_fingerprint(
            self.base(block(inductionRequirement="Induction agent per local protocol."))
        )
        self.assertNotEqual(before, after)

    def test_a_record_without_the_block_is_unaffected(self):
        """Adding the field must not disturb the other 54 sign-offs."""
        self.assertEqual(
            promote.procedure_fingerprint({"sections": {}}),
            promote.procedure_fingerprint({"sections": {}, "medicationDosing": None}),
        )


if __name__ == "__main__":
    unittest.main()
