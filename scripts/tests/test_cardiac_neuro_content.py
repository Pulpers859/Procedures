"""Guards on the cardiac and neuro content adjudicated on 2026-07-31 (see
docs/audits/procedure-verification/04_CARDIAC_NEURO.md).

Same contract as test_airway_content.py: these are content assertions, not
validator negative controls. Each one holds the line on a specific hazard that a
later wording pass could quietly undo - a criterion softened back into a hedge,
a depth or a volume deleted as clutter, a confirmation step replaced by the
plausible one that does not work.

Nothing here is clinical approval. It only proves the shipped bytes still say
what the adjudication decided they should say."""
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PROCEDURES = REPO / "Procedures" / "Resources" / "procedures.json"

LANE_IDS = (
    "pericardiocentesis",
    "transvenous_pacemaker",
    "resuscitative_thoracotomy",
    "synchronized_cardioversion",
    "lumbar_puncture",
)


def load():
    items = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    return {item["id"]: item for item in items}


def all_lines(record):
    """Every prose line in the record, flattened. Section-blind on purpose: the
    guarantee is that the reader can find the sentence, not which heading it
    happens to sit under."""
    lines = []
    for value in (record.get("sections") or {}).values():
        if isinstance(value, list):
            lines.extend(str(entry) for entry in value)
    return lines


def joined(record):
    return "\n".join(all_lines(record)).lower()


class LaneScopeTests(unittest.TestCase):
    """Scope stated in words, not implied by absent metadata.

    Dropping a `Peds` tag satisfies a machine. A reader at 3am reads text, and
    the absence of a tag is invisible to them."""

    def setUp(self):
        self.records = load()

    def test_every_record_in_the_lane_states_its_age_scope(self):
        for pid in LANE_IDS:
            with self.subTest(pid):
                self.assertIn("adult", joined(self.records[pid]))

    def test_lumbar_puncture_no_longer_claims_paediatric_setting(self):
        """The card had `Peds` in `setting` and not one paediatric specific -
        no interspace, needle length, volume, sedation, or pressure range. The
        claim was the defect; removing it is reversible, shipping it was not."""
        record = self.records["lumbar_puncture"]
        self.assertNotIn("Peds", record["setting"])
        self.assertIn("pediatric and neonatal lp differ", joined(record))


class PericardiocentesisTests(unittest.TestCase):
    def setUp(self):
        self.record = load()["pericardiocentesis"]
        self.text = joined(self.record)

    def test_dissection_and_free_wall_rupture_are_surgical_not_cautious(self):
        """"Requires extreme caution" is what the record used to say, and it
        reads as permission. Draining restores the pressure gradient across the
        tear that the tamponade was containing."""
        self.assertIn("surgical emergency, not a needle", self.text)
        self.assertIn("free-wall rupture", self.text)
        self.assertIn("contained rupture into an uncontained one", self.text)

    def test_the_bridge_exception_is_bounded_by_aliquot_and_endpoint(self):
        """An exception with no ceiling is not an exception."""
        self.assertIn("10-20 ml at a time", self.text)
        self.assertIn("lowest blood pressure that perfuses", self.text)

    def test_emergency_drainage_has_a_stopping_point(self):
        """"Until hemodynamics improve or flow stops" had no ceiling in either
        direction and no decompression-syndrome warning."""
        self.assertIn("20-50 ml", self.text)
        self.assertIn("under about 500 ml", self.text)
        self.assertIn("pericardial decompression syndrome", self.text)

    def test_position_is_confirmed_before_dilating(self):
        """The vascular records carry a pre-dilation gate for the same reason:
        a needle hole in a chamber is survivable and a dilator hole may not be."""
        self.assertIn("before dilating over the wire", self.text)
        self.assertIn("no exception, including in an emergency", self.text)

    def test_the_colour_test_is_named_as_useless_in_haemopericardium(self):
        """The old confirmation line - "pericardial fluid rather than blood from
        chamber" - fails in precisely the trauma case this card exists for.
        Everything is blood there."""
        self.assertIn("color proves nothing", self.text)
        self.assertIn("agitated saline", self.text)

    def test_the_landmark_visual_is_labelled_as_the_no_ultrasound_fallback(self):
        """A fixed "aim at the left shoulder" trajectory competes with the
        record's own safest-pocket rule unless it is labelled as the fallback."""
        visual = next(
            v for v in self.record["visualAssets"]
            if v["id"] == "pericardiocentesis_needle_path"
        )
        self.assertIn("fallback", visual["title"].lower())
        self.assertIn("blind fallback route only", visual["subtitle"].lower())


class ResuscitativeThoracotomyTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["resuscitative_thoracotomy"])

    def test_signs_of_life_are_enumerated_rather_than_referenced(self):
        """The card told the reader to apply criteria it never stated, which
        produces confidence rather than a decision."""
        for sign in (
            "palpable pulse",
            "measurable blood pressure",
            "spontaneous respiratory effort",
            "pupillary reaction",
            "organized cardiac electrical activity",
        ):
            with self.subTest(sign):
                self.assertIn(sign, self.text)

    def test_the_cpr_windows_are_numbers(self):
        """"Short arrest interval" is not executable at 3am with a bleeding
        patient on the trolley."""
        self.assertIn("under 15 minutes for penetrating", self.text)
        self.assertIn("under 10 minutes for blunt", self.text)

    def test_ultrasound_standstill_is_confined_to_the_pea_branch(self):
        """Free-standing "standstill informs prognosis" turns a narrow algorithm
        branch into a general licence to stop."""
        self.assertIn("not a free-standing reason to stop", self.text)
        self.assertIn("in a patient with signs of life it changes nothing", self.text)

    def test_the_tray_names_something_that_divides_the_sternum(self):
        """"Extend across the sternum" is a step with no instrument behind it
        unless the tray is checked for one."""
        self.assertTrue(
            any(tool in self.text for tool in ("lebsche", "gigli", "trauma shears")),
            "no sternal-division instrument named",
        )

    def test_the_oesophagus_is_named_as_the_structure_clamped_by_mistake(self):
        self.assertIn("esophagus", self.text)
        self.assertIn("orogastric tube", self.text)

    def test_the_internal_mammaries_are_flagged_after_clamshell(self):
        """They do not bleed while the patient is arrested. They bleed at the
        moment success arrives."""
        self.assertIn("internal mammary arteries", self.text)

    def test_there_is_a_stated_termination_endpoint(self):
        self.assertIn("no organized cardiac activity after tamponade release", self.text)


class CardioversionEnergyTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["synchronized_cardioversion"])

    def test_the_current_initial_energies_are_stated(self):
        """The card carried the older start-low figures for fibrillation and
        grouped flutter with SVT."""
        self.assertIn("atrial fibrillation 200 j", self.text)
        self.assertIn("atrial flutter 200 j", self.text)
        self.assertIn("monomorphic vt with a pulse 100 j", self.text)
        self.assertNotIn("120-200 j", self.text)

    def test_the_manufacturer_dose_is_named_as_taking_precedence(self):
        """Biphasic waveforms are not interchangeable and the guideline itself
        defers to the manufacturer. Without this line the card asserts a
        universal number that its own source does not."""
        self.assertIn("manufacturer's recommended energy takes precedence", self.text)

    def test_sync_persistence_is_not_asserted_as_a_universal_default(self):
        """"Most devices reset" is a claim about defibrillators in general that
        current Philips and LIFEPAK platforms make configurable."""
        self.assertNotIn("most devices", self.text)
        self.assertIn("configurable", self.text)

    def test_the_af_anticoagulation_pathway_is_explicit_on_both_sides(self):
        self.assertIn("three weeks of uninterrupted therapeutic anticoagulation", self.text)
        self.assertIn("at least four weeks of uninterrupted therapeutic anticoagulation", self.text)
        self.assertIn("appendage thrombus", self.text)

    def test_the_telemetry_period_is_no_longer_an_invented_number(self):
        """"At least 1-3 hours" was not established by any reviewed source."""
        self.assertNotIn("1-3 hours", self.text)
        self.assertIn("no evidence-based universal telemetry duration", self.text)

    def test_implanted_devices_get_interrogated_afterwards(self):
        self.assertIn("interrogate any pacemaker or icd", self.text)


class LumbarPunctureTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["lumbar_puncture"])

    def test_antibiotics_are_not_gated_by_the_lp(self):
        """The STOP-SHIP. A card that describes the LP without this rule invites
        the reader to finish the procedure before treating the meningitis."""
        self.assertIn("antibiotics first", self.text)
        self.assertIn("deferring the lp for imaging never defers the antibiotics", self.text)
        self.assertIn("blood cultures, then antibiotics, then everything below", self.text)

    def test_the_imaging_criteria_are_named_features(self):
        """"Signs of elevated ICP/mass lesion" is a category, not a checklist."""
        for feature in ("focal neurological deficit", "papilledema", "abnormal posturing"):
            with self.subTest(feature):
                self.assertIn(feature, self.text)

    def test_the_atraumatic_needle_is_the_default_and_bevel_advice_is_scoped(self):
        """The old step said to orient the bevel, which is meaningless on the
        pencil-point needle the evidence prefers - and the missing pop is what
        makes an inexperienced operator advance too far."""
        self.assertIn("atraumatic pencil-point spinal needle, 22-25 gauge", self.text)
        self.assertIn("does not apply to a pencil-point needle", self.text)
        self.assertIn("subtle or absent pop", self.text)

    def test_the_haematoma_catch_exists_because_the_hold_table_cannot(self):
        """No hold interval was invented. What replaced the unanswerable
        question is the surveillance rule, which is what turns a rare bleed into
        a recoverable one."""
        self.assertIn("urinary retention after an lp", self.text)
        self.assertIn("urgent mri", self.text)
        self.assertIn("named local antithrombotic policy", self.text)

    def test_the_opening_pressure_has_stated_conditions(self):
        self.assertIn("before removing any csf", self.text)
        self.assertIn("zeroed at the interspace", self.text)
        self.assertIn("flexion falsely raises the opening pressure", self.text)

    def test_bed_rest_is_not_offered_as_prophylaxis(self):
        self.assertIn("bed rest does not prevent post-dural-puncture headache", self.text)


class TransvenousPacemakerTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["transvenous_pacemaker"])

    def test_the_access_hierarchy_is_stated_with_its_reasons(self):
        self.assertIn("right internal jugular is the preferred route", self.text)
        self.assertIn("avoid an intrathoracic subclavian puncture", self.text)
        self.assertIn("preserve the side planned for the permanent pacemaker", self.text)

    def test_no_capture_is_named_as_a_position_problem(self):
        """Climbing the output is the intuitive move and the wrong one."""
        self.assertIn("position, not power", self.text)

    def test_the_balloon_rules_are_present(self):
        """Air only, inflated past the introducer, and never forced."""
        self.assertIn("air only, never fluid or contrast", self.text)
        self.assertIn("past the introducer and never inside it", self.text)
        self.assertIn("never advance against resistance", self.text)

    def test_the_threshold_and_safety_margin_are_numeric(self):
        self.assertIn("two to three times", self.text)
        self.assertIn("above roughly 2 ma", self.text)
        self.assertIn("30-35 cm", self.text)

    def test_dwell_time_has_an_owner_and_a_review_cadence(self):
        self.assertIn("review the need every day", self.text)


class LaneReferenceTests(unittest.TestCase):
    """Every record in the lane cited undated textbooks or bare guideline names
    while passing the release reference gate, which only looks for two specific
    placeholder phrases. Traceability is a separate property from passing it."""

    def setUp(self):
        self.records = load()

    def test_no_record_in_the_lane_still_cites_an_undated_textbook(self):
        for pid in LANE_IDS:
            with self.subTest(pid):
                refs = " ".join(self.records[pid]["sections"]["references"]).lower()
                self.assertNotIn("roberts and hedges", refs)
                self.assertNotIn("tintinalli", refs)

    def test_every_record_in_the_lane_carries_a_resolvable_locator(self):
        for pid in LANE_IDS:
            with self.subTest(pid):
                refs = self.records[pid]["sections"]["references"]
                self.assertTrue(
                    any("https://" in ref or "doi.org" in ref for ref in refs),
                    f"{pid} has no resolvable reference locator",
                )


if __name__ == "__main__":
    unittest.main()
