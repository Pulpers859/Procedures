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

    def test_changing_selection_guidance_moves_the_fingerprint(self):
        """Which agent to reach for in shock is clinical content, not prose."""
        before = promote.procedure_fingerprint(self.base(block()))
        after = promote.procedure_fingerprint(
            self.base(block(selectionGuidance=["Shock: ketamine."]))
        )
        self.assertNotEqual(before, after)

    def test_absent_selection_guidance_is_stable(self):
        self.assertEqual(
            promote.procedure_fingerprint(self.base(block())),
            promote.procedure_fingerprint(self.base(block(selectionGuidance=None))),
        )


def shipped_block(procedure_id):
    import json
    items = json.loads(
        (SCRIPTS.parent / "Procedures" / "Resources" / "procedures.json").read_text(encoding="utf-8")
    )
    record = next(i for i in items if i["id"] == procedure_id)
    return record, record["medicationDosing"]


class ShippedRSIBlockTests(unittest.TestCase):
    """Guards on the intubation block. `procedural_sedation` carries one too
    since 2026-07-30, so the assertions below name their record rather than
    assuming they are looking at the only one."""

    def setUp(self):
        self.record, self.block = shipped_block("endotracheal_intubation")

    def test_the_shipped_block_validates(self):
        self.assertEqual(
            MODULE.medication_dosing_issues([{"title": "T", "medicationDosing": self.block}]), []
        )

    def test_an_induction_agent_is_present_with_a_dose(self):
        """A paralytic dose with no induction dose is the hazard this guards."""
        induction = [m for m in self.block["medications"] if m["role"] == "Induction"]
        self.assertTrue(induction)
        for med in induction:
            self.assertGreater(med["doseLowPerKg"], 0, med["medication"])

    def test_the_depolarising_blocker_uses_the_name_the_reader_uses(self):
        """One reader. 'Suxamethonium' is correct and unfamiliar to them."""
        names = [m["medication"] for m in self.block["medications"]]
        self.assertIn("Succinylcholine", names)
        self.assertNotIn("Suxamethonium", names)

    def test_the_shock_asymmetry_is_in_the_field_the_reader_cannot_skip(self):
        """The single most useful rule in RSI pharmacology, and it was absent:
        the induction dose comes down while the paralytic does not. It lives in
        `inductionRequirement` because that field renders once, at the top of
        the card, with a warning icon."""
        requirement = self.block["inductionRequirement"]
        self.assertIn("halve the induction dose", requirement)
        self.assertIn("full paralytic dose", requirement)

    def test_the_withdrawn_pretreatments_are_gone(self):
        """Owner decision, 2026-07-30. Defasciculating vecuronium risks a
        partially paralysed conscious patient for no benefit. Intravenous
        lidocaine is unsupported and silently consumed the same patient's
        local-anaesthetic ceiling if they went on to have a block."""
        names = [m["medication"] for m in self.block["medications"]]
        self.assertNotIn("Lidocaine", names)
        self.assertNotIn("Vecuronium (defasciculating)", names)

    def test_every_agent_states_an_onset(self):
        """"When do I look?" is the question being asked at the bedside. Every
        `onset` on this block was null."""
        for med in self.block["medications"]:
            with self.subTest(medication=med["medication"]):
                self.assertTrue(str(med.get("onset") or "").strip())

    def test_the_weight_basis_is_stated_where_it_differs(self):
        """Total, ideal, and lean body weight are three different numbers in a
        140 kg patient, and the card previously gave one instruction."""
        basis = {
            "Succinylcholine": "total body weight",
            "Rocuronium": "ideal body weight",
            "Propofol": "lean body weight",
        }
        by_name = {m["medication"]: m for m in self.block["medications"]}
        for name, expected in basis.items():
            with self.subTest(medication=name):
                self.assertIn(expected, by_name[name]["caution"] or "")

    def test_the_source_note_still_admits_what_it_is(self):
        """The owner re-affirmed these figures unchanged rather than re-deriving
        them. The note must not start reading like a primary citation."""
        note = self.block["sourceNote"]
        self.assertIn("cites no primary references", note)
        self.assertIn("adult-scoped", note)


class ShippedSedationBlockTests(unittest.TestCase):
    """The sedation block added on 2026-07-30.

    The record was already tagged `ketamine`, `propofol`, and `etomidate`, so it
    was reachable by drug name and answered with no dose at all. Promising
    pharmacology and delivering none is worse than not appearing in the search."""

    def setUp(self):
        self.record, self.block = shipped_block("procedural_sedation")

    def test_the_shipped_block_validates(self):
        self.assertEqual(
            MODULE.medication_dosing_issues([{"title": "T", "medicationDosing": self.block}]), []
        )

    def test_every_tagged_agent_now_carries_a_dose(self):
        named = {m["medication"].lower() for m in self.block["medications"]}
        for tag in ("ketamine", "propofol", "etomidate"):
            with self.subTest(tag=tag):
                self.assertIn(tag, self.record["tags"])
                self.assertIn(tag, named)

    def test_the_sedation_etomidate_dose_is_below_the_induction_dose(self):
        """Two cards in one app now name etomidate at 0.1-0.15 and at 0.3
        mg/kg. That is exactly the pair of numbers that gets crossed, so the
        relationship is asserted rather than left to the reader."""
        _, rsi = shipped_block("endotracheal_intubation")
        sedation = next(m for m in self.block["medications"] if m["medication"] == "Etomidate")
        induction = next(m for m in rsi["medications"] if m["medication"] == "Etomidate")
        ceiling = sedation["doseHighPerKg"] or sedation["doseLowPerKg"]
        self.assertLess(ceiling, induction["doseLowPerKg"])
        self.assertIn("half the intubation induction dose", sedation["caution"])

    def test_the_rescue_capability_guard_is_present(self):
        """`inductionRequirement` is named for RSI. Its purpose is to carry the
        sentence a reader must not be able to skip, and for sedation that
        sentence is about being able to rescue what you may create."""
        requirement = self.block["inductionRequirement"]
        self.assertIn("one level deeper", requirement)
        self.assertIn("before the first millilitre goes in", requirement)

    def test_ketamine_states_the_all_or_nothing_property(self):
        """An underdose does not give light sedation. It gives an agitated,
        undissociated patient, and the instinct is then to redose fast."""
        ketamine = next(m for m in self.block["medications"] if m["medication"] == "Ketamine")
        self.assertIn("all or nothing", ketamine["caution"])
        self.assertIn("No reversal agent exists", ketamine["caution"])
        self.assertIn("over 1-2 minutes", ketamine["caution"])

    def test_the_opioid_synergy_warning_appears_on_both_sides(self):
        """Additive would be survivable arithmetic. It is not additive."""
        by_name = {m["medication"]: m for m in self.block["medications"]}
        self.assertIn("Synergistic with opioids", by_name["Midazolam"]["caution"])
        self.assertIn("more than additive", by_name["Fentanyl"]["caution"])

    def test_the_analgesic_is_not_labelled_as_a_sedative(self):
        fentanyl = next(m for m in self.block["medications"] if m["medication"] == "Fentanyl")
        self.assertEqual(fentanyl["role"], "Analgesia")
        self.assertEqual(fentanyl["unit"], "mcg/kg")
        self.assertIn("Analgesia, not sedation", fentanyl["caution"])

    def test_the_source_note_does_not_overclaim_its_guidelines(self):
        """ASA 2018 and the ACEP policy govern staffing, monitoring, depth, and
        fasting. Neither is a dosing table, and the note must not imply it is."""
        note = self.block["sourceNote"]
        self.assertIn("rather than specific doses", note)
        self.assertIn("not independently verified", note)
        self.assertIn("Paediatric sedation is out of scope", note)


if __name__ == "__main__":
    unittest.main()
