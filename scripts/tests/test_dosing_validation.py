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
