"""Guards on the airway and sedation content adjudicated by the owner on
2026-07-30 (see docs/audits/procedure-verification/01_AIRWAY_SEDATION.md).

These are content assertions, not validator negative controls. They exist
because the findings behind them are the kind that get quietly reverted by a
later "tidy the wording" pass: a depth limit deleted as clutter, a hedge
reintroduced to make a sentence read more politely. Each test names the hazard
it is holding the line on.

Nothing here is clinical approval. It only proves the shipped bytes still say
what the adjudication decided they should say."""
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PROCEDURES = REPO / "Procedures" / "Resources" / "procedures.json"

AIRWAY_IDS = ("endotracheal_intubation", "cricothyrotomy", "procedural_sedation")


def load():
    items = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    return {item["id"]: item for item in items}


def all_lines(record):
    """Every prose line in the record, flattened. Deliberately section-blind:
    these guarantees are about whether the reader can find the sentence at all,
    not about which heading it sits under."""
    lines = []
    for value in (record.get("sections") or {}).values():
        if isinstance(value, list):
            lines.extend(str(entry) for entry in value)
    return lines


class AirwayScopeTests(unittest.TestCase):
    """Adult scope has to be stated in words, not implied by a missing tag.

    Dropping `Peds` from `setting` resolved the audit finding for a machine and
    for nobody else. A reader in a resus bay reads text; the absence of metadata
    is invisible to them."""

    def setUp(self):
        self.records = load()

    def test_every_airway_record_states_adult_scope_in_prose(self):
        for pid in AIRWAY_IDS:
            with self.subTest(procedure=pid):
                lines = all_lines(self.records[pid])
                self.assertTrue(
                    any("Adult scope only" in line for line in lines),
                    f"{pid} does not state adult scope in any section",
                )

    def test_no_airway_record_carries_the_peds_setting(self):
        for pid in AIRWAY_IDS:
            with self.subTest(procedure=pid):
                self.assertNotIn("Peds", self.records[pid].get("setting") or [])

    def test_the_paediatric_boundary_on_cricothyrotomy_is_a_number(self):
        """"Young children require special consideration" was the original
        wording. At 03:00 "young" can mean fourteen, and "special
        consideration" implies the same procedure done carefully when in fact
        the technique changes."""
        lines = all_lines(self.records["cricothyrotomy"])
        boundary = [line for line in lines if "8-10 years" in line]
        self.assertEqual(len(boundary), 1, lines)
        self.assertIn("cannula-based technique", boundary[0])
        self.assertFalse(
            any("Young children require special consideration" in line for line in lines)
        )


class IntubationSafetyNumbersTests(unittest.TestCase):
    """The numbers a reader cannot derive and will otherwise guess."""

    def setUp(self):
        self.record = load()["endotracheal_intubation"]
        self.lines = all_lines(self.record)

    def test_cuff_inflation_states_a_pressure_not_a_volume(self):
        """The equipment list offers a 10 mL syringe, which reads as an
        instruction to put 10 mL in. Cuff pressure is the number that matters."""
        cuff = [line for line in self.lines if "20-30 cmH2O" in line]
        self.assertEqual(len(cuff), 1, self.lines)
        self.assertIn("Millilitres are not a pressure", cuff[0])
        self.assertTrue(
            any("cuff manometer" in line for line in self.record["sections"]["equipment"])
        )

    def test_tube_depth_gives_a_starting_number(self):
        """Right mainstem intubation is in the complications list. A card that
        names the complication and no depth has described the problem only."""
        depth = [line for line in self.lines if "21 cm" in line and "23 cm" in line]
        self.assertEqual(len(depth), 1, self.lines)
        self.assertIn("three times the tube size", depth[0])

    def test_the_collar_comes_off_for_laryngoscopy(self):
        """The counterintuitive half of the 2024 cervical-spine guidance, and
        the half that actually improves the view."""
        collar = [line for line in self.lines if "front of the collar off" in line]
        self.assertEqual(len(collar), 1, self.lines)

    def test_the_old_cervical_spine_strawman_is_gone(self):
        """The original line argued against "paralysis avoidance", a position
        nobody holds, and offered manual in-line stabilisation as the whole
        answer."""
        self.assertFalse(
            any("rather than paralysis avoidance alone" in line for line in self.lines)
        )

    def test_sugammadex_is_ruled_out_as_a_cico_rescue(self):
        """Reversal is reached for as a fantasy escape from a cannot-oxygenate
        patient. Closing that off is worth more than omitting the drug."""
        line = [entry for entry in self.lines if "Sugammadex" in entry]
        self.assertEqual(len(line), 1, self.lines)
        self.assertIn("16 mg/kg", line[0])
        self.assertIn("front of the neck", line[0])

    def test_the_plan_letters_are_defined_where_they_are_used(self):
        """"Move to Plan B" is a pointer to a document the reader does not have
        open."""
        defined = [
            line for line in self.lines
            if "Plan A" in line and "Plan B" in line and "Plan D" in line
        ]
        self.assertEqual(len(defined), 1, self.lines)
        self.assertIn("supraglottic", defined[0])
        self.assertIn("front-of-neck", defined[0])

    def test_the_attempt_ceiling_survives_a_solo_operator(self):
        """DAS assumes a more experienced colleague exists. In a community ED at
        03:00 the reader is that colleague, and "plus one" invites a fourth
        attempt by the same pair of hands."""
        plus_one = [line for line in self.lines if "The plus-one is a handover" in line]
        self.assertEqual(len(plus_one), 1, self.lines)
        self.assertIn("the ceiling is three", plus_one[0])

    def test_awareness_under_paralysis_is_stated_as_a_duration_gap(self):
        """"Do not forget sedation" is not the same claim as "this patient will
        be awake and paralysed for 35 minutes"."""
        aware = [line for line in self.lines if "awake, paralysed" in line]
        self.assertEqual(len(aware), 1, self.lines)
        self.assertIn("35 minutes", aware[0])


class CricothyrotomyTechniqueTests(unittest.TestCase):
    """One named technique, and the two depth limits that bound it.

    The owner adopted DAS 2025 scalpel-bougie-tube on 2026-07-30. The prior text
    offered a menu ("finger, scalpel handle, or dilator") with an institutional
    escape hatch, which is how an operator improvises in the one procedure where
    improvising is the failure mode."""

    def setUp(self):
        self.record = load()["cricothyrotomy"]
        self.steps = self.record["sections"]["steps"]
        self.lines = all_lines(self.record)

    def test_the_technique_is_named_once_and_committed_to(self):
        named = [line for line in self.lines if "scalpel, bougie, tube (DAS 2025)" in line]
        self.assertEqual(len(named), 1, self.lines)
        self.assertFalse(
            any("unless your institution has a specific kit" in line for line in self.lines)
        )

    def test_a_commercial_kit_is_a_separate_pathway_not_a_substitute_item(self):
        """A Seldinger kit fails by wire kinking and dilator false passage; a
        scalpel technique fails by losing the tract. The troubleshooting for one
        is wrong for the other, so they cannot share a step list."""
        for fragment in ("instructions for use rather than these steps",
                         "not a substitute item in this list"):
            with self.subTest(fragment=fragment):
                self.assertTrue(any(fragment in line for line in self.lines), fragment)

    def test_the_scalpel_stays_in_the_hole(self):
        """The commonest failure is removing the scalpel and being unable to
        find the tract again in a bleeding neck."""
        guide = [step for step in self.steps if "Keep the scalpel in the hole" in step]
        self.assertEqual(len(guide), 1, self.steps)
        self.assertIn("rotate the blade 90 degrees", guide[0])
        self.assertIn("towards the feet", guide[0])

    def test_the_bougie_has_a_depth_limit(self):
        bougie = [step for step in self.steps if "10-15 cm" in step]
        self.assertEqual(len(bougie), 1, self.steps)
        self.assertIn("no further", bougie[0])

    def test_the_tube_has_a_stop_point(self):
        """The single commonest post-cricothyrotomy error, and it was absent
        entirely: a 6.0 railroaded to its usual mark is endobronchial."""
        stop = [step for step in self.steps if "cuff has passed the membrane" in step]
        self.assertEqual(len(stop), 1, self.steps)
        self.assertIn("right main bronchus", stop[0])

    def test_the_instruments_are_named_exactly(self):
        equipment = " ".join(self.record["sections"]["equipment"])
        self.assertIn("Number 10 scalpel blade", equipment)
        self.assertIn("6.0 cuffed tracheal tube", equipment)
        self.assertNotIn("often 6.0 adult ETT or trach/cric tube per kit", equipment)

    def test_full_block_is_required_and_explained(self):
        """Counterintuitive enough that stating it without the reason invites
        the reader to skip it: the patient is already not breathing."""
        block = [line for line in self.lines if "full neuromuscular block" in line]
        self.assertEqual(len(block), 1, self.lines)
        self.assertIn("counterintuitive", block[0])

    def test_oxygen_from_above_continues_through_the_incision(self):
        oxygen = [line for line in self.lines if "Oxygen from above continues" in line]
        self.assertEqual(len(oxygen), 1, self.lines)
        self.assertIn("do not stop because you have started cutting", oxygen[0])

    def test_ultrasound_is_pre_crisis_only(self):
        ultrasound = self.record["sections"]["ultrasound"]
        self.assertTrue(ultrasound, "the section was empty and the audit asked for a boundary")
        joined = " ".join(ultrasound)
        self.assertIn("before induction", joined)
        self.assertIn("Do not scan during an established cannot-oxygenate crisis", joined)

    def test_flat_capnography_does_not_condemn_the_tube(self):
        """A peri-arrest patient can have no ETCO2 through a correctly sited
        tube, and this may be the only airway they have."""
        flat = [line for line in self.lines if "Capnography can be flat" in line]
        self.assertEqual(len(flat), 1, self.lines)
        self.assertIn("circulation finding", flat[0])

    def test_bronchial_placement_and_pneumothorax_are_excluded_after_stabilising(self):
        aftercare = " ".join(self.record["sections"]["aftercare"])
        self.assertIn("exclude bronchial intubation and pneumothorax", aftercare)
        self.assertIn("bridge, not a destination", aftercare)


class SedationStaffingAndMonitoringTests(unittest.TestCase):
    """The hedges, and why naming the venue removes their excuse.

    "When possible" and "if available" existed because the text was trying to be
    true in venues where a dedicated monitor and capnography are not stocked.
    Once the record says adult ED/ICU, both hedges are indefensible."""

    def setUp(self):
        self.record = load()["procedural_sedation"]
        self.lines = all_lines(self.record)

    def test_the_monitor_is_dedicated_and_does_nothing_else(self):
        monitor = [line for line in self.lines if "does nothing else" in line]
        self.assertEqual(len(monitor), 1, self.lines)
        self.assertIn("proceduralist cannot do it", monitor[0])
        self.assertFalse(
            any("sedation/monitoring clinician when possible" in line for line in self.lines)
        )

    def test_capnography_is_required_rather_than_ideal(self):
        required = [line for line in self.lines if "Capnography is required, not optional" in line]
        self.assertEqual(len(required), 1, self.lines)
        self.assertIn("lagging indicator", required[0])
        for hedge in ("ideally ETCO2", "ETCO2 if available", "capnography when available"):
            with self.subTest(hedge=hedge):
                self.assertFalse(any(hedge in line for line in self.lines), hedge)

    def test_the_depth_continuum_is_stated(self):
        continuum = [line for line in self.lines if "you get the depth you get" in line]
        self.assertEqual(len(continuum), 1, self.lines)
        self.assertIn("one level deeper", continuum[0])

    def test_fasting_separates_urgency_from_risk(self):
        """"Recent oral intake is contextual" collapsed two different
        decisions: whether to wait, and whether this stomach changes the plan."""
        joined = " ".join(self.lines)
        self.assertIn("Urgent sedation is not delayed for fasting time", joined)
        self.assertIn("GLP-1 receptor agonist", joined)
        self.assertIn("not the number of hours you wait", joined)
        self.assertFalse(any("Recent oral intake is contextual" in line for line in self.lines))

    def test_laryngospasm_and_vomiting_appear_in_the_records_own_troubleshooting(self):
        """Both already have rescue-card coverage. A reader whose patient is
        obstructing is scanning the procedure they are in, not the rescue
        index."""
        troubleshooting = self.record["sections"]["troubleshooting"]
        self.assertTrue(any("Laryngospasm" in line for line in troubleshooting))
        self.assertTrue(any("Vomiting" in line for line in troubleshooting))
        joined = " ".join(troubleshooting)
        self.assertIn("laryngospasm rescue card", joined)
        self.assertIn("Do not blindly instrument the airway", joined)

    def test_reversal_lengthens_the_watch(self):
        """The intuition runs the other way: they are awake, so send them."""
        reversal = [line for line in self.lines if "longer watch, not a shorter one" in line]
        self.assertEqual(len(reversal), 1, self.lines)
        self.assertIn("two-hour window", reversal[0])

    def test_discharge_criteria_are_enumerated_rather_than_gestured_at(self):
        criteria = [line for line in self.lines if "Discharge criteria, all of them" in line]
        self.assertEqual(len(criteria), 1, self.lines)
        for item in ("baseline mental status", "protecting their own airway",
                     "vital signs at baseline", "pain controlled"):
            with self.subTest(criterion=item):
                self.assertIn(item, criteria[0])

    def test_the_local_anaesthetic_ceiling_is_cross_referenced(self):
        """Sedation and infiltration share one encounter and one ceiling, and a
        sedated patient cannot report early toxicity."""
        ceiling = [line for line in self.lines if "maximum local anaesthetic dose" in line]
        self.assertEqual(len(ceiling), 1, self.lines)
        self.assertIn("cannot report the early symptoms", ceiling[0])

    def test_airway_assessment_names_what_it_is_looking_for(self):
        assessment = [line for line in self.lines if "thyromental distance" in line]
        self.assertEqual(len(assessment), 1, self.lines)
        self.assertIn("not a box to tick", assessment[0])


class AirwayReferenceTests(unittest.TestCase):
    """All three records passed the release reference check while citing undated
    textbooks, because the check only looks for two specific placeholder
    phrases. Traceability is a separate property from passing that gate."""

    def setUp(self):
        self.records = load()

    def test_every_airway_record_cites_a_locatable_primary_source(self):
        for pid in AIRWAY_IDS:
            with self.subTest(procedure=pid):
                references = self.records[pid]["sections"]["references"]
                self.assertTrue(
                    any("https://" in reference for reference in references),
                    f"{pid} has no reference a reader can open",
                )

    def test_the_front_of_neck_card_cites_the_front_of_neck_guideline(self):
        references = " ".join(self.records["cricothyrotomy"]["sections"]["references"])
        self.assertIn("Difficult Airway Society", references)
        self.assertIn("das.uk.com", references)

    def test_the_undated_textbook_only_reference_lists_are_gone(self):
        for pid in AIRWAY_IDS:
            with self.subTest(procedure=pid):
                references = self.records[pid]["sections"]["references"]
                self.assertFalse(
                    any(reference.startswith("Tintinalli's") for reference in references),
                    f"{pid} still leads a reference with an undated textbook",
                )


if __name__ == "__main__":
    unittest.main()
