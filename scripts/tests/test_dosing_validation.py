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
                "note": None,
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


class ShippedPreparationTableTests(unittest.TestCase):
    """Locks the ceilings the clinical owner designated on 2026-07-30.

    Bupivacaine and ropivacaine come from the reference the owner nominated;
    lidocaine with epinephrine at 7 mg/kg was confirmed separately against the
    calculator he uses. Ropivacaine carries no absolute ceiling because that
    source states none - it is purely weight-based, and inventing a cap here
    would silently withhold dose from a large patient.

    These are exact-value assertions on purpose. Everything else in this file
    checks that the *shape* is safe; nothing checked that the numbers were the
    ones anybody chose.
    """

    EXPECTED = [
        ("Lidocaine", False, 4.5, 300, [1.0, 2.0]),
        ("Lidocaine", True, 7.0, 500, [1.0, 2.0]),
        ("Bupivacaine", False, 2.5, 175, [0.25, 0.5, 0.75]),
        ("Bupivacaine", True, 3.0, 225, [0.25, 0.5, 0.75]),
        ("Ropivacaine", False, 3.0, None, [0.2, 0.5]),
    ]

    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        # Regional only, matching testEveryRegionalBlockShipsTheSamePreparationTable
        # on the Swift side. The selector used to be "any block with dosing",
        # which was the same set at the time and stopped being so when the
        # intraosseous card took a lidocaine ceiling of its own. That table is
        # locked by IntraosseousDosingTests below rather than left unguarded.
        self.tables = [
            p["dosing"]["agents"] for p in procedures
            if p.get("dosing") and p.get("category") == MODULE.REGIONAL_CATEGORY
        ]
        self.assertEqual(len(self.tables), 28)

    def test_every_block_ships_the_designated_table(self):
        for table in self.tables:
            actual = [
                (a["agent"], a["withEpinephrine"], a["maxDoseMgPerKg"],
                 a["absoluteMaxMg"], a["concentrationsPercent"])
                for a in table
            ]
            self.assertEqual(actual, self.EXPECTED)

    def test_ropivacaine_says_why_it_has_no_epinephrine_variant(self):
        """An absent row with no explanation reads as an oversight."""
        ropivacaine = [a for a in self.tables[0] if a["agent"] == "Ropivacaine"]
        self.assertEqual(len(ropivacaine), 1)
        self.assertIn("pinephrine", ropivacaine[0]["note"] or "")

    def test_the_long_acting_agents_carry_their_relative_cardiotoxicity(self):
        """Choosing between bupivacaine and ropivacaine is the decision this
        card is consulted for. Stating the ceilings without the difference in
        cardiotoxicity answers the arithmetic and not the question."""
        notes = {
            (a["agent"], a["withEpinephrine"]): a["note"] or ""
            for a in self.tables[0]
        }
        self.assertIn("cardiotox", notes[("Ropivacaine", False)])
        self.assertIn("cardiotox", notes[("Bupivacaine", False)])
        self.assertIn("cardiotox", notes[("Bupivacaine", True)])

    def test_every_block_gives_the_same_incremental_injection_rule(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        rules = {
            line
            for p in procedures if p.get("dosing")
            for line in p["dosing"]["monitoring"]
            if "increments" in line
        }
        self.assertEqual(len(rules), 1, rules)
        self.assertIn("3 mL increments", rules.pop())

    def test_the_source_published_volumes_reproduce(self):
        """The reference states its own maximum volumes. If the card computes
        different ones, the card is wrong - this is the arithmetic check that
        catches a transcription error in the ceilings themselves."""
        bupivacaine = next(
            a for a in self.tables[0]
            if a["agent"] == "Bupivacaine" and not a["withEpinephrine"]
        )
        # 175 mg plain, at each stocked strength.
        for percent, expected_ml in ((0.25, 70), (0.5, 35), (0.75, 23)):
            volume = bupivacaine["absoluteMaxMg"] / MODULE.mg_per_ml(percent)
            self.assertEqual(int(volume), expected_ml, f"{percent}%")

        # Ropivacaine is quoted per kilogram: 3 mg/kg is 1.5 mL/kg at 0.2%
        # and 0.6 mL/kg at 0.5%.
        ropivacaine = next(a for a in self.tables[0] if a["agent"] == "Ropivacaine")
        for percent, expected_ml_per_kg in ((0.2, 1.5), (0.5, 0.6)):
            self.assertAlmostEqual(
                ropivacaine["maxDoseMgPerKg"] / MODULE.mg_per_ml(percent),
                expected_ml_per_kg,
                places=6,
                msg=f"{percent}%",
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


class IntraosseousDosingTests(unittest.TestCase):
    """The intraosseous card used to instruct a flat "20-40 mg lidocaine 2%"
    on a procedure tagged for paediatrics. At 0.5 mg/kg a 6 kg infant is owed
    3 mg, so the card as written was a sixfold overdose that a reader following
    it exactly would have given.

    It is structured data now for the same reason the regional blocks are: a
    frozen sentence with a number in it cannot recalculate itself, and this one
    had already drifted from the source it came from.
    """

    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.io = next(p for p in procedures if p["id"] == "intraosseous_access")
        self.dosing = self.io["dosing"]
        self.agent = self.dosing["agents"][0]

    def test_the_ceiling_is_weight_based_with_a_hard_cap(self):
        self.assertEqual(len(self.dosing["agents"]), 1)
        self.assertEqual(self.agent["agent"], "Lidocaine")
        self.assertFalse(self.agent["withEpinephrine"])
        self.assertEqual(self.agent["maxDoseMgPerKg"], 0.5)
        self.assertEqual(self.agent["absoluteMaxMg"], 40)
        self.assertEqual(self.agent["concentrationsPercent"], [2.0])

    def test_an_infant_dose_is_nothing_like_the_adult_dose(self):
        """The exact arithmetic the old fixed dose got wrong."""
        for weight, expected_mg in ((6, 3.0), (20, 10.0), (70, 35.0), (100, 40.0)):
            computed = min(self.agent["maxDoseMgPerKg"] * weight, self.agent["absoluteMaxMg"])
            self.assertEqual(computed, expected_mg, f"{weight} kg")
        # 0.15 mL of 2% for that infant - a volume nobody reliably works out
        # from a fixed-dose sentence at three in the morning.
        self.assertAlmostEqual(3.0 / MODULE.mg_per_ml(2.0), 0.15)

    def test_the_preparation_is_named_as_preservative_and_epinephrine_free(self):
        note = self.agent["note"] or ""
        self.assertIn("reservative-free", note)
        self.assertIn("pinephrine-free", note)

    def test_the_adult_flat_dose_is_not_silently_dropped(self):
        """The calculator returns 35 mg at 70 kg where the manufacturer gives
        adults 40 mg. Erring low on an analgesic is the safe direction, but the
        reader has to be told, not left to find the discrepancy."""
        self.assertIn("40 mg", self.agent["note"] or "")

    def test_the_sequence_puts_lidocaine_before_the_flush(self):
        """Flushing an un-anaesthetised marrow is the painful step. The card
        used to flush 10 mL first and then offer the lidocaine, which defeats
        the entire purpose of carrying it."""
        steps = self.io["sections"]["steps"]
        lidocaine = next(i for i, s in enumerate(steps) if "lidocaine" in s.lower())
        flush = next(i for i, s in enumerate(steps) if "then flush" in s.lower())
        self.assertLess(lidocaine, flush)
        self.assertIn("120 seconds", steps[lidocaine])
        self.assertIn("60 seconds", steps[flush])

    def test_the_flush_volume_is_age_specific(self):
        joined = " ".join(self.io["sections"]["steps"] + self.dosing["monitoring"])
        self.assertIn("5-10 mL", joined)
        self.assertIn("2-5 mL", joined)
        self.assertNotIn("Flush with 10 mL normal saline", joined)

    def test_the_humerus_is_not_drilled_at_ninety_degrees(self):
        joined = " ".join(self.io["sections"]["steps"] + self.io["sections"]["anatomy"])
        self.assertIn("45 degrees", joined)
        self.assertIn("posteromedial", joined)

    def test_needle_choice_is_anchored_to_the_five_millimetre_mark(self):
        steps = " ".join(self.io["sections"]["steps"])
        self.assertIn("5 mm mark", steps)


class VascularAccessRescueTests(unittest.TestCase):
    """Three records need the same two paragraphs: the pre-dilation gate and
    the arterial-injury rescue. If the wording diverges the reader meets two
    versions of one doctrine at the worst possible moment, so it is asserted
    identical rather than merely present.
    """

    LARGE_BORE = ("central_venous_catheter", "introducer_sheath_cordis", "dialysis_catheter_vascath")

    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.records = {p["id"]: p for p in procedures if p["id"] in self.LARGE_BORE}
        self.assertEqual(len(self.records), 3)

    def _matching(self, section, fragment):
        found = []
        for pid in self.LARGE_BORE:
            lines = [l for l in self.records[pid]["sections"][section] if fragment in l]
            self.assertEqual(len(lines), 1, f"{pid}.{section}: {fragment!r}")
            found.append(lines[0])
        return found

    def test_the_pre_dilation_gate_is_word_for_word_the_same(self):
        gates = self._matching("steps", "before dilating")
        self.assertEqual(len(set(gates)), 1, "the confirmation gate has diverged")
        self.assertIn("two planes", gates[0])
        self.assertIn("transduce", gates[0])

    def test_colour_and_pulsatility_are_explicitly_rejected(self):
        for gate in self._matching("steps", "before dilating"):
            self.assertIn("do not confirm venous placement", gate)

    def test_no_record_still_makes_wire_confirmation_conditional(self):
        for pid, record in self.records.items():
            for section in ("steps", "shiftMode", "ultrasound"):
                for line in record["sections"][section]:
                    if "wire" not in line.lower():
                        continue
                    for hedge in ("when possible", "when feasible"):
                        self.assertNotIn(hedge, line, f"{pid}.{section}: {line}")

    def test_the_large_bore_rescue_is_word_for_word_the_same(self):
        rescues = self._matching("troubleshooting", "leave it in place")
        self.assertEqual(len(set(rescues)), 1, "the arterial rescue has diverged")
        for phrase in ("Do not remove", "do not compress", "vascular surgery", "interventional radiology"):
            self.assertIn(phrase, rescues[0])

    def test_the_needle_only_branch_is_stated_separately(self):
        """Without the distinction the reader applies leave-in-place to a
        finder needle, or pull-and-pressure to a dilated artery."""
        branches = self._matching("troubleshooting", "needle only")
        self.assertEqual(len(set(branches)), 1)
        self.assertIn("hold firm pressure", branches[0])

    def test_every_record_says_to_transduce_when_unsure(self):
        # Deliberately not "transduce it": the leave-in-place rescue says that
        # too, about a different device in a different situation.
        answers = self._matching("troubleshooting", "Unsure whether you are in the artery")
        self.assertEqual(len(set(answers)), 1)

    def test_air_embolism_has_a_rescue_card_reachable_from_each_record(self):
        cards = {c["id"]: c for c in MODULE.load_json(MODULE.RESCUE_CARDS)}
        card = cards["air_embolism_vascular_access"]
        for pid in self.LARGE_BORE:
            self.assertIn(pid, card["relatedProcedureIDs"])
        moves = " ".join(card["immediateMoves"])
        self.assertIn("Occlude", moves)
        self.assertIn("left lateral", moves.lower())


class ArterialLineTraceTests(unittest.TestCase):
    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.record = next(p for p in procedures if p["id"] == "arterial_line")
        self.sections = self.record["sections"]

    def test_both_damping_directions_are_covered(self):
        """Underdamping is the dangerous direction and the card described only
        the other one: a resonant trace reads systolic high and hides the
        hypotension you are titrating against."""
        joined = " ".join(self.sections["troubleshooting"]).lower()
        self.assertIn("overdamped", joined)
        self.assertIn("underdamped", joined)

    def test_the_square_wave_test_is_required_before_treating_a_number(self):
        joined = " ".join(self.sections["steps"] + self.sections["confirmation"]).lower()
        self.assertIn("square-wave", joined)

    def test_titration_falls_back_to_map_until_the_trace_is_validated(self):
        joined = " ".join(self.sections["steps"] + self.sections["shiftMode"])
        self.assertIn("MAP", joined)

    def test_the_time_based_resite_rule_is_gone(self):
        """A scheduled arterial-line change does not lower infection and buys
        the patient another puncture."""
        joined = " ".join(
            self.sections["complications"] + self.sections["aftercare"]
        )
        self.assertNotIn("72-96", joined)
        self.assertIn("Do not resite on a schedule", joined)

    def test_the_single_lumen_catheter_is_not_described_as_having_ports(self):
        self.assertNotIn("All ports flush", " ".join(self.sections["confirmation"]))


class DialysisCatheterLengthTests(unittest.TestCase):
    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.sections = next(
            p for p in procedures if p["id"] == "dialysis_catheter_vascath"
        )["sections"]

    def test_length_is_specified_per_site(self):
        """"Advance to the planned depth" is not a specification. A short
        femoral catheter recirculates and dialyses nothing."""
        joined = " ".join(
            self.sections["anatomy"] + self.sections["steps"] + self.sections["shiftMode"]
        )
        for length in ("12-15 cm", "15-20 cm", "19-24 cm"):
            self.assertIn(length, joined)

    def test_the_lock_is_aspirated_before_use(self):
        """The card told the reader to instil a lock and never to withdraw it."""
        joined = " ".join(self.sections["aftercare"] + self.sections["shiftMode"])
        self.assertIn("aspirated and discarded before every use", joined)

    def test_the_priming_volume_is_read_off_the_device(self):
        joined = " ".join(self.sections["steps"])
        self.assertIn("printed on that lumen", joined)

    def test_heparin_induced_thrombocytopenia_is_called_out(self):
        joined = " ".join(self.sections["equipment"])
        self.assertIn("thrombocytopenia", joined)


class PeripheralIVLengthTests(unittest.TestCase):
    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.sections = next(
            p for p in procedures if p["id"] == "ultrasound_guided_piv"
        )["sections"]

    def test_gel_must_be_labelled_sterile(self):
        """"Sterile or single-use ... per local policy" reads as though
        non-sterile single-use gel is an acceptable branch. It is not, for a
        percutaneous procedure."""
        joined = " ".join(self.sections["equipment"])
        self.assertIn("labelled sterile", joined)
        self.assertNotIn("Sterile or single-use", joined)

    def test_the_intraluminal_length_target_replaced_the_fixed_minimum(self):
        joined = " ".join(
            self.sections["shiftMode"] + self.sections["anatomy"] + self.sections["steps"]
        )
        self.assertIn("2.75 cm", joined)
        self.assertNotIn("one third of the catheter", joined)

    def test_contrast_is_conditioned_rather_than_implied(self):
        joined = " ".join(self.sections["indications"] + self.sections["confirmation"])
        self.assertIn("power-rated catheter", joined)

    def test_the_deep_extravasation_is_described_as_unwitnessed(self):
        joined = " ".join(self.sections["complications"])
        self.assertIn("unwitnessed", joined)


class PleuralProcedureTests(unittest.TestCase):
    """The thoracic lane, after the owner adjudicated its seventeen questions
    on 2026-07-30."""

    PLEURAL = ("thoracostomy_chest_tube", "pigtail_catheter", "thoracentesis")

    def setUp(self):
        procedures = MODULE.load_json(MODULE.PROCEDURES)
        self.records = {p["id"]: p for p in procedures}
        self.all_procedures = procedures

    def sections(self, pid, *names):
        return " ".join(
            line for name in names for line in self.records[pid]["sections"].get(name) or []
        )

    # ---- shared across the three pleural records

    def test_the_pleural_ceiling_is_the_conservative_bts_figure(self):
        """Owner decision: 3 mg/kg to 250 mg, not the label's 4.5 and 300. A
        wide infiltration of skin, periosteum and pleura in a patient who may
        already be hypoxic is the reason to take the lower number."""
        for pid in self.PLEURAL:
            with self.subTest(pid):
                agents = self.records[pid]["dosing"]["agents"]
                self.assertEqual(len(agents), 1)
                self.assertEqual(agents[0]["agent"], "Lidocaine")
                self.assertEqual(agents[0]["maxDoseMgPerKg"], 3.0)
                self.assertEqual(agents[0]["absoluteMaxMg"], 250)
                self.assertEqual(
                    self.records[pid]["dosing"]["rescueCardID"],
                    "local_anesthetic_systemic_toxicity",
                )

    def test_the_pleural_ceiling_deliberately_differs_from_the_regional_table(self):
        """A divergence this size reads as an error unless the record says why."""
        regional = next(
            p for p in self.all_procedures
            if p.get("category") == MODULE.REGIONAL_CATEGORY and p.get("dosing")
        )
        plain = next(
            a for a in regional["dosing"]["agents"]
            if a["agent"] == "Lidocaine" and not a["withEpinephrine"]
        )
        pleural = self.records["thoracentesis"]["dosing"]["agents"][0]
        self.assertNotEqual(plain["maxDoseMgPerKg"], pleural["maxDoseMgPerKg"])
        note = pleural["note"] or ""
        self.assertIn("BTS", note)
        self.assertIn("3 mg/kg", note)
        self.assertIn("4.5 mg/kg", note)

    def test_the_controlled_drainage_rule_is_word_for_word_the_same(self):
        found = []
        for pid in self.PLEURAL:
            lines = [
                line
                for name in ("steps", "troubleshooting", "shiftMode")
                for line in self.records[pid]["sections"].get(name) or []
                if "Drain to symptoms" in line
            ]
            self.assertTrue(lines, pid)
            found.extend(lines)
        self.assertEqual(len(set(found)), 1, "the controlled-drainage rule has diverged")
        rule = found[0]
        for phrase in ("clamp", "repetitive cough", "re-expansion", "1.5 L"):
            self.assertIn(phrase, rule)

    def test_re_expansion_oedema_has_a_rescue_card_reachable_from_each(self):
        cards = {c["id"]: c for c in MODULE.load_json(MODULE.RESCUE_CARDS)}
        card = cards["re_expansion_pulmonary_edema"]
        for pid in self.PLEURAL:
            self.assertIn(pid, card["relatedProcedureIDs"])
        avoid = " ".join(card["avoid"]).lower()
        self.assertIn("diuretic", avoid)

    def test_every_thoracic_record_states_adult_scope(self):
        for pid in self.PLEURAL + ("needle_decompression",):
            with self.subTest(pid):
                self.assertIn(
                    "Adult scope only",
                    self.sections(pid, "contraindications", "shiftMode"),
                )

    # ---- thoracentesis

    def test_vacuum_drainage_is_gone(self):
        """BTS advises against vacuum bottles and wall suction for therapeutic
        aspiration; the card both stocked them and instructed their use."""
        joined = self.sections("thoracentesis", "equipment", "steps", "shiftMode").lower()
        # The word still appears, as a prohibition. What must be gone is the
        # instruction to use one, and the bottle sitting in the kit list.
        self.assertNotIn("gravity to vacuum bottle", joined)
        self.assertNotIn("and vacuum drainage bottles for therapeutic", joined)
        self.assertIn("vacuum bottles and wall suction are not used", joined)
        self.assertIn("never a vacuum bottle or wall suction", joined)
        self.assertIn("gravity", joined)
        self.assertIn("syringe aspiration", joined)

    def test_the_intercostal_bundle_order_is_corrected_everywhere(self):
        """It was stated wrong in two places: anatomy and shiftMode."""
        joined = self.sections("thoracentesis", "anatomy", "shiftMode")
        self.assertNotIn("NAV", joined)
        self.assertNotIn("nerve-artery-vein", joined)
        self.assertIn("vein-artery-nerve", joined + " " + joined)
        self.assertIn("vein, artery,", joined)
        # The bundle is not reliably under the rib; saying so is the point.
        self.assertIn("not reliably", joined)

    def test_specimen_handling_is_corrected(self):
        joined = self.sections("thoracentesis", "equipment", "aftercare")
        self.assertNotIn("SBP", joined, "spontaneous bacterial peritonitis is not a pleural diagnosis")
        self.assertIn("in addition to plain containers", joined)
        self.assertIn("blood-gas syringe", joined)
        self.assertIn("7.2", joined)
        self.assertIn("lidocaine", joined.lower())

    def test_post_procedure_imaging_is_selective_not_routine(self):
        joined = self.sections(
            "thoracentesis", "shiftMode", "steps", "confirmation", "aftercare"
        )
        self.assertIn("only on the selective criteria", joined)
        self.assertIn("lung sliding", joined)

    def test_the_unsourced_pneumothorax_rates_are_gone(self):
        joined = self.sections("thoracentesis", "complications")
        self.assertNotIn("5-10%", joined)
        self.assertNotIn("<1-3%", joined)

    # ---- needle decompression

    def test_the_decompression_device_is_numerically_specified(self):
        """"Long large-bore angiocath" is not a specification, and a 5 cm
        catheter does not reach pleura in a large share of adults."""
        joined = self.sections("needle_decompression", "equipment", "shiftMode")
        self.assertIn("14 gauge or larger", joined)
        self.assertIn("8 cm", joined)
        self.assertNotIn("Long large-bore angiocath", joined)

    def test_the_landmarks_are_reconciled_to_one_standard(self):
        joined = self.sections("needle_decompression", "shiftMode", "steps", "anatomy")
        self.assertIn("anterior axillary line", joined)
        self.assertIn("2nd intercostal space, midclavicular", joined + joined)
        self.assertNotIn("mid-axillary", joined, "not the cited standard and posterior to the intent")

    def test_the_failed_needle_pathway_no_longer_contradicts_itself(self):
        """shiftMode allowed another needle while troubleshooting forbade it."""
        joined = self.sections("needle_decompression", "shiftMode", "troubleshooting")
        self.assertIn("decide by capability", joined)
        self.assertIn("finger thoracostomy", joined)

    def test_a_tube_is_the_default_rather_than_the_exception(self):
        joined = self.sections("needle_decompression", "confirmation", "aftercare", "shiftMode")
        self.assertIn("A tube follows", joined)
        self.assertNotIn("Definitive tube thoracostomy usually follows", joined)

    # ---- chest tube and pigtail split

    def test_the_chest_tube_card_is_the_large_bore_card(self):
        joined = self.sections("thoracostomy_chest_tube", "shiftMode", "equipment", "indications")
        self.assertIn("28-32 Fr", joined)
        self.assertIn("pigtail catheter card", joined)
        self.assertNotIn("Appropriate tube size or pigtail if selected", joined)

    def test_the_pigtail_card_is_the_small_bore_card(self):
        joined = self.sections("pigtail_catheter", "shiftMode", "equipment", "indications")
        self.assertIn("8-14 Fr", joined)
        self.assertIn("14 Fr or smaller", joined)
        self.assertIn("chest tube card", joined)

    def test_instability_excludes_a_bedside_pigtail(self):
        """EAST confines its conditional recommendation to stable patients;
        "may need" was not a decision."""
        joined = self.sections("pigtail_catheter", "contraindications", "shiftMode")
        self.assertIn("excludes a bedside pigtail", joined)
        self.assertNotIn("may need large-bore tube", joined)

    def test_dilation_is_limited_to_the_measured_chest_wall(self):
        joined = self.sections("pigtail_catheter", "steps", "shiftMode")
        self.assertIn("measured chest-wall depth", joined)
        self.assertIn("without impedance", joined)
        self.assertIn("beyond the catheter tip", joined)

    def test_the_massive_hemothorax_trigger_is_numeric_and_framed_as_a_call(self):
        joined = self.sections("thoracostomy_chest_tube", "troubleshooting", "shiftMode")
        self.assertIn("1,500 mL", joined)
        self.assertIn("200 mL/h", joined)
        self.assertIn("triggers to call, not thresholds to wait for", joined)

    def test_the_drain_system_safety_rules_are_present_on_both_drains(self):
        for pid in ("thoracostomy_chest_tube", "pigtail_catheter"):
            with self.subTest(pid):
                joined = self.sections(pid, "troubleshooting")
                self.assertIn("Never clamp a bubbling drain", joined)
                self.assertIn("below the insertion site", joined)
                self.assertIn("three sides", joined)

    def test_antibiotic_prophylaxis_states_the_duration_rule(self):
        """The agent is local policy; the duration is the part people get
        wrong, and it is the part that is well supported."""
        joined = self.sections("thoracostomy_chest_tube", "equipment", "steps", "aftercare")
        self.assertIn("Do not continue", joined)
        self.assertIn("at insertion", joined)


if __name__ == "__main__":
    unittest.main()
