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
                "agent": "Bupivacaine",
                "withEpinephrine": False,
                "maxDoseMgPerKg": 2.0,
                "absoluteMaxMg": 175,
                "concentrationsPercent": [0.25, 0.5],
            }
        ],
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
                agent = {"agent": "Bupivacaine", "maxDoseMgPerKg": bad}
                issues = MODULE.regional_dosing_issues([block(dosing_value=dosing(agents=[agent]))], RESCUE_IDS)
                self.assertTrue(any(issue[0] == "BLOCKER" and "maxDoseMgPerKg" in issue[2] for issue in issues))

    def test_a_missing_or_impossible_concentration_is_a_blocker(self):
        """The calculator divides the mg ceiling by this to print millilitres,
        so a bad percentage is a wrong volume in a syringe, not a doc gap."""
        for bad in (None, [], "1%", [0], [-1], [101], [True], ["1"]):
            with self.subTest(concentrations=bad):
                agent = {
                    "agent": "Bupivacaine",
                    "withEpinephrine": False,
                    "maxDoseMgPerKg": 2.0,
                    "concentrationsPercent": bad,
                }
                issues = MODULE.regional_dosing_issues(
                    [block(dosing_value=dosing(agents=[agent]))], RESCUE_IDS
                )
                self.assertTrue(
                    any(issue[0] == "BLOCKER" and "concentration" in issue[2] for issue in issues),
                    issues,
                )

    def test_a_missing_epinephrine_flag_is_a_blocker(self):
        """Plain and with-epinephrine are different ceilings for one drug. An
        absent flag makes the entry ambiguous about which one it states."""
        agent = {
            "agent": "Bupivacaine",
            "maxDoseMgPerKg": 2.0,
            "concentrationsPercent": [0.25],
        }
        issues = MODULE.regional_dosing_issues(
            [block(dosing_value=dosing(agents=[agent]))], RESCUE_IDS
        )
        self.assertTrue(any(issue[0] == "BLOCKER" and "withEpinephrine" in issue[2] for issue in issues))

    def test_dangling_rescue_card_id_is_a_blocker(self):
        issues = MODULE.regional_dosing_issues(
            [block(dosing_value=dosing(rescueCardID="does_not_exist"))], RESCUE_IDS
        )
        self.assertTrue(any(issue[0] == "BLOCKER" and "does_not_exist" in issue[2] for issue in issues))

    def test_thin_monitoring_and_missing_prose_fields_are_flagged(self):
        cases = (
            dosing(monitoring=["only one action"]),
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
                    "agent": "Bupivacaine",
                    "withEpinephrine": False,
                    "maxDoseMgPerKg": 2.0,
                    "concentrationsPercent": [0.25, 0.5],
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
                "agent": "Bupivacaine",
                "withEpinephrine": False,
                "maxDoseMgPerKg": 3.0,      # 210 mg at 70 kg
                "absoluteMaxMg": 175,       # but capped here
                "concentrationsPercent": [0.5],
            }],
        )
        issues = MODULE.prose_dose_ceiling_issues([item])
        self.assertTrue(issues)
        self.assertIn("175 mg", issues[0][2])

    def test_a_line_naming_a_different_agent_is_not_cross_checked(self):
        item = self.procedure(["Local anesthetic (40 mL of 0.5% ropivacaine)"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_a_strength_the_record_does_not_stock_is_still_converted(self):
        """This used to be skipped, because the mg/mL came from a prose note
        listing the strengths someone had written down and 2% was not on it.
        A strength the record fails to mention is exactly the one worth
        checking: 40 mL at 2% is 800 mg against a 140 mg ceiling."""
        item = self.procedure(["Local anesthetic (40 mL of 2% bupivacaine)"])
        issues = MODULE.prose_dose_ceiling_issues([item])
        self.assertTrue(issues)
        self.assertIn("800 mg", issues[0][2])

    def test_percent_to_mg_per_ml_is_the_definition(self):
        self.assertEqual(MODULE.mg_per_ml(1), 10)
        self.assertEqual(MODULE.mg_per_ml(0.25), 2.5)
        self.assertEqual(MODULE.mg_per_ml(2), 20)

    def test_prose_without_a_volume_or_percent_is_ignored(self):
        item = self.procedure(["Local anesthetic", "Sterile gloves and drape"])
        self.assertEqual(MODULE.prose_dose_ceiling_issues([item]), [])

    def test_release_level_promotes_to_blocker(self):
        item = self.procedure(["Local anesthetic (e.g., 20-30 mL of 0.25% or 0.5% bupivacaine)"])
        issues = MODULE.prose_dose_ceiling_issues([item], level="BLOCKER")
        self.assertTrue(all(issue[0] == "BLOCKER" for issue in issues))

    def test_shipped_content_has_no_ceiling_contradictions(self):
        """Locks the RAPTIR correction.

        RAPTIR offered "20-30 mL of 0.25% or 0.5% bupivacaine or ropivacaine".
        At the 0.5% its own concentrationNote defines as 5 mg/mL, 30 mL is
        150 mg against the 2 mg/kg ceiling the same record states — 140 mg at
        70 kg. The clinical owner adjudicated it: 0.5% is now capped at 20 mL
        (100 mg), with the arithmetic shown in the worked example.
        """
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.assertEqual(MODULE.prose_dose_ceiling_issues(procedures), [])

    def test_volume_range_parsing(self):
        self.assertEqual(MODULE._max_volume_ml("20-30 mL of 0.5%"), 30)
        self.assertEqual(MODULE._max_volume_ml("inject 5 mL slowly"), 5)
        self.assertEqual(MODULE._max_volume_ml("3-5 mL then 10 mL"), 5)
        self.assertIsNone(MODULE._max_volume_ml("no volume here"))


class UncomputableInjectateTests(unittest.TestCase):
    """"Local anesthetic (20-30 mL)" on a record listing two agents with
    different ceilings is 50-75 mg or 200-300 mg depending on which one is in
    the syringe. Structural only: does the record ever say what the drug is."""

    def procedure(self, equipment, steps=None):
        return {
            "id": "block_test",
            "title": "Test Block",
            "category": "Regional Anesthesia",
            "sections": {"equipment": equipment, "steps": steps or []},
            "dosing": dosing(),
        }

    def test_volume_with_no_agent_anywhere_is_flagged(self):
        item = self.procedure(["Local anesthetic (5-10 mL)"], ["Inject 5-10 mL of anesthetic."])
        issues = MODULE.uncomputable_injectate_issues([item])
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("never names an agent", issues[0][2])

    def test_agent_named_in_equipment_excuses_the_steps_line(self):
        item = self.procedure(
            ["Local anesthetic (15-20 mL of 0.25% bupivacaine)"],
            ["Aspirate, then inject 15-20 mL of anesthetic."],
        )
        self.assertEqual(MODULE.uncomputable_injectate_issues([item]), [])

    def test_one_issue_per_procedure_not_per_line(self):
        item = self.procedure(
            ["Local anesthetic (5-10 mL)"],
            ["Inject 5-10 mL of anesthetic.", "Inject a further 5 mL of anesthetic."],
        )
        self.assertEqual(len(MODULE.uncomputable_injectate_issues([item])), 1)

    def test_equipment_sizing_is_not_an_injectate(self):
        # "3-5 mL syringe" is a syringe, not a dose.
        item = self.procedure(["3-5 mL syringe", "Sterile gloves"])
        self.assertEqual(MODULE.uncomputable_injectate_issues([item]), [])

    def test_procedure_without_structured_dosing_is_not_gated(self):
        item = self.procedure(["Local anesthetic (5-10 mL)"])
        del item["dosing"]
        self.assertEqual(MODULE.uncomputable_injectate_issues([item]), [])

    def test_shipped_content_flags_only_whole_procedures(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        issues = MODULE.uncomputable_injectate_issues(procedures)
        titles = [issue[1] for issue in issues]
        self.assertEqual(len(titles), len(set(titles)), "one issue per procedure")


class UnboundedAgentTests(unittest.TestCase):
    """A drug the procedure tells you to use, with no stated maximum."""

    def procedure(self, equipment):
        return {
            "id": "block_test",
            "title": "Test Block",
            "category": "Regional Anesthesia",
            "sections": {"equipment": equipment, "steps": []},
            "dosing": dosing(),  # bupivacaine only
        }

    def test_agent_named_in_prose_without_a_ceiling_is_flagged(self):
        issues = MODULE.unbounded_agent_issues([self.procedure(["1% lidocaine or articaine"])])
        named = " ".join(issue[2] for issue in issues)
        self.assertIn("articaine", named)
        self.assertIn("lidocaine", named)

    def test_an_agent_with_a_ceiling_is_clean(self):
        self.assertEqual(
            MODULE.unbounded_agent_issues([self.procedure(["0.25% bupivacaine"])]), []
        )

    def test_shipped_content_has_exactly_the_known_gap(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        issues = MODULE.unbounded_agent_issues(procedures)
        self.assertEqual(
            [(issue[1], "articaine" in issue[2]) for issue in issues],
            [("Inferior Alveolar Nerve Block", True)],
            "a new unbounded agent appeared, or the known one was resolved",
        )


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
