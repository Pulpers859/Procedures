"""Negative controls for the regional-anesthesia dosing rules and the
Crash-card drug-without-a-dose rule. These prove the validator refuses unsafe
content shapes; they say nothing about clinical correctness."""
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_procedures.py"
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def dosing(**overrides):
    value = {
        "agents": [
            {
                "agent": "Bupivacaine (plain)",
                "concentrationNote": "0.25% = 2.5 mg/mL",
                "maxDoseMgPerKg": 2.0,
                "absoluteMaxMg": 175,
            }
        ],
        "workedExample": "70 kg adult: 2 mg/kg = 140 mg = 56 mL of 0.25%.",
        "cumulativeWarning": "All local anesthetic this encounter shares one maximum.",
        "monitoring": [
            "Continuous cardiac monitoring and pulse oximetry through 30 min after injection.",
            "Confirm 20% lipid emulsion location before injecting.",
        ],
        "rescueCardID": "local_anesthetic_systemic_toxicity",
    }
    value.update(overrides)
    return value


def block(dosing_value="default"):
    item = {
        "id": "block_test",
        "title": "Test Block",
        "category": "Regional Anesthesia",
    }
    if dosing_value == "default":
        item["dosing"] = dosing()
    elif dosing_value is not None:
        item["dosing"] = dosing_value
    return item


RESCUE_IDS = {"local_anesthetic_systemic_toxicity"}


def crash_card(immediate_moves):
    return {
        "id": "crash_test",
        "title": "Crash Test Card",
        "acuity": "Crash",
        "immediateMoves": immediate_moves,
    }


class RegionalDosingTests(unittest.TestCase):
    def test_well_formed_dosing_is_clean(self):
        self.assertEqual(MODULE.regional_dosing_issues([block()], RESCUE_IDS), [])

    def test_non_regional_procedure_needs_no_dosing(self):
        item = {"id": "chest_tube", "title": "Chest Tube", "category": "Thoracic"}
        self.assertEqual(MODULE.regional_dosing_issues([item], RESCUE_IDS), [])

    def test_missing_dosing_warns_in_authoring_and_blocks_in_release(self):
        for level in ("WARNING", "BLOCKER"):
            with self.subTest(level=level):
                issues = MODULE.regional_dosing_issues([block(dosing_value=None)], RESCUE_IDS, level=level)
                self.assertTrue(any(issue[0] == level and "max-dose" in issue[2] for issue in issues))

    def test_empty_agents_is_always_a_blocker(self):
        issues = MODULE.regional_dosing_issues([block(dosing_value=dosing(agents=[]))], RESCUE_IDS)
        self.assertTrue(any(issue[0] == "BLOCKER" and "no agents" in issue[2] for issue in issues))

    def test_nonpositive_or_missing_mg_per_kg_is_a_blocker(self):
        for bad in (0, -1, None, "2", True):
            with self.subTest(max_dose=bad):
                agent = {"agent": "Bupivacaine", "concentrationNote": "x", "maxDoseMgPerKg": bad}
                issues = MODULE.regional_dosing_issues([block(dosing_value=dosing(agents=[agent]))], RESCUE_IDS)
                self.assertTrue(any(issue[0] == "BLOCKER" and "maxDoseMgPerKg" in issue[2] for issue in issues))

    def test_dangling_rescue_card_id_is_a_blocker(self):
        issues = MODULE.regional_dosing_issues(
            [block(dosing_value=dosing(rescueCardID="does_not_exist"))], RESCUE_IDS
        )
        self.assertTrue(any(issue[0] == "BLOCKER" and "does_not_exist" in issue[2] for issue in issues))

    def test_thin_monitoring_and_missing_prose_fields_are_flagged(self):
        cases = (
            dosing(monitoring=["only one action"]),
            dosing(workedExample=" "),
            dosing(cumulativeWarning=""),
            dosing(rescueCardID=None),
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertTrue(MODULE.regional_dosing_issues([block(dosing_value=case)], RESCUE_IDS))

    def test_shipped_content_has_dosing_on_every_regional_block(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        rescue_cards = MODULE.load_json(MODULE.RESCUE_CARDS)
        self.assertIsNotNone(procedures)
        self.assertIsNotNone(rescue_cards)
        rescue_ids = {card.get("id") for card in rescue_cards}
        issues = MODULE.regional_dosing_issues(procedures, rescue_ids, level="BLOCKER")
        self.assertEqual(issues, [], f"shipped regional blocks must carry release-grade dosing: {issues}")


class ProseDoseCeilingTests(unittest.TestCase):
    """The structured dosing block was validated rigorously; the free-text
    equipment/steps beside it were validated only for length. Nothing connected
    the two, so a procedure could recommend a volume that, at the higher
    concentration named on the same line, exceeded the ceiling stated a few
    fields away — and pass clean in both modes.

    Every number in the check comes from the record itself. These tests assert
    the arithmetic and the negative controls, not clinical correctness.
    """

    def procedure(self, lines, agents=None):
        return {
            "id": "block_test",
            "title": "Test Block",
            "category": "Regional Anesthesia",
            "sections": {"equipment": lines, "steps": []},
            "dosing": dosing(agents=agents) if agents else dosing(
                agents=[{
                    "agent": "Bupivacaine (plain)",
                    "concentrationNote": "0.25% = 2.5 mg/mL; 0.5% = 5 mg/mL",
                    "maxDoseMgPerKg": 2.0,
                }]
            ),
        }

    def test_volume_at_the_stronger_concentration_breaching_the_ceiling_is_flagged(self):
        # 30 mL x 5 mg/mL = 150 mg, against 2 mg/kg x 70 kg = 140 mg.
        item = self.procedure(["Local anesthetic (e.g., 20-30 mL of 0.25% or 0.5% bupivacaine)"])
        issues = MODULE.prose_dose_ceiling_issues([item])
        self.assertTrue(issues, "150 mg against a 140 mg ceiling should be reported")
        self.assertIn("150 mg", issues[0][2])

    def test_volume_within_the_ceiling_is_clean(self):
        # 20 mL x 2.5 mg/mL = 50 mg, well under.
        item = self.procedure(["Local anesthetic (20 mL of 0.25% bupivacaine)"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_exactly_at_the_ceiling_is_not_reported(self):
        """Strict `>` only. Zero-margin dosing is a clinical judgement, not an
        internal contradiction, and this rule reports contradictions."""
        # 20 mL x 5 mg/mL = 100 mg == 2 mg/kg x 50 kg.
        item = self.procedure(["Local anesthetic (20 mL of 0.5% bupivacaine)"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_absolute_ceiling_is_honoured_when_lower(self):
        item = self.procedure(
            ["Local anesthetic (40 mL of 0.5% bupivacaine)"],
            agents=[{
                "agent": "Bupivacaine (plain)",
                "concentrationNote": "0.5% = 5 mg/mL",
                "maxDoseMgPerKg": 3.0,      # 210 mg at 70 kg
                "absoluteMaxMg": 175,       # but capped here
            }],
        )
        issues = MODULE.prose_dose_ceiling_issues([item])
        self.assertTrue(issues)
        self.assertIn("175 mg", issues[0][2])

    def test_a_line_naming_a_different_agent_is_not_cross_checked(self):
        item = self.procedure(["Local anesthetic (40 mL of 0.5% ropivacaine)"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_a_concentration_the_record_does_not_define_is_skipped(self):
        # 2% is not in the concentrationNote, so there is no mg/mL to multiply.
        item = self.procedure(["Local anesthetic (40 mL of 2% bupivacaine)"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_prose_without_a_volume_or_percent_is_ignored(self):
        item = self.procedure(["Local anesthetic", "Sterile gloves and drape"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_release_level_promotes_to_blocker(self):
        item = self.procedure(["Local anesthetic (e.g., 20-30 mL of 0.25% or 0.5% bupivacaine)"])
        issues = MODULE.prose_dose_ceiling_issues([item], level="BLOCKER")
        self.assertTrue(all(issue[0] == "BLOCKER" for issue in issues))

    def test_volume_range_parsing(self):
        self.assertEqual(MODULE._max_volume_ml("20-30 mL of 0.5%"), 30)
        self.assertEqual(MODULE._max_volume_ml("inject 5 mL slowly"), 5)
        self.assertEqual(MODULE._max_volume_ml("3-5 mL then 10 mL"), 5)
        self.assertIsNone(MODULE._max_volume_ml("no volume here"))


class CrashCardDoseTests(unittest.TestCase):
    def test_drug_class_without_number_is_flagged(self):
        issues = MODULE.crash_card_dose_issues([crash_card(["Give push-dose vasopressor if crashing."])])
        self.assertTrue(any("without a dose" in issue[2] for issue in issues))

    def test_drug_with_dose_on_same_line_passes(self):
        issues = MODULE.crash_card_dose_issues(
            [crash_card(["Push-dose epinephrine 5-20 mcg IV (10 mcg/mL) every 2-5 min."])]
        )
        self.assertEqual(issues, [])

    def test_non_drug_moves_are_ignored(self):
        issues = MODULE.crash_card_dose_issues([crash_card(["Call for help and reassess the airway."])])
        self.assertEqual(issues, [])

    def test_urgent_cards_are_not_gated(self):
        card = crash_card(["Give push-dose vasopressor."])
        card["acuity"] = "Urgent"
        self.assertEqual(MODULE.crash_card_dose_issues([card]), [])

    def test_release_level_promotes_to_blocker(self):
        issues = MODULE.crash_card_dose_issues(
            [crash_card(["Give push-dose vasopressor if crashing."])], level="BLOCKER"
        )
        self.assertTrue(any(issue[0] == "BLOCKER" for issue in issues))

    def test_shipped_crash_cards_carry_doses(self):
        rescue_cards = MODULE.load_json(MODULE.RESCUE_CARDS)
        self.assertIsNotNone(rescue_cards)
        issues = MODULE.crash_card_dose_issues(rescue_cards)
        self.assertEqual(issues, [], f"shipped Crash cards must dose every named drug: {issues}")


if __name__ == "__main__":
    unittest.main()
