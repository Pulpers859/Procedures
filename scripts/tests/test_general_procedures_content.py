"""Guards on the general-procedures content adjudicated on 2026-07-31 (see
docs/audits/procedure-verification/05_GENERAL_PROCEDURES.md).

Same contract as the other content-guard suites: each test names the hazard it
holds the line on, and none of it is clinical approval. It proves the shipped
bytes still say what the adjudication decided."""
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PROCEDURES = REPO / "Procedures" / "Resources" / "procedures.json"

LANE_IDS = (
    "paracentesis",
    "lateral_canthotomy",
    "shoulder_reduction",
    "knee_arthrocentesis",
    "anterior_nasal_packing",
    "peritonsillar_abscess_drainage",
    "abscess_incision_drainage",
    "laceration_repair",
    "foreign_body_removal_soft_tissue",
)

# Every record in the lane that injects local anaesthetic. Nasal packing is
# deliberately absent: it uses 4% topical on mucosa, which the infiltration
# calculator would model wrongly, so its ceiling is stated in prose instead.
INFILTRATING_IDS = tuple(pid for pid in LANE_IDS if pid != "anterior_nasal_packing")


def load():
    return {item["id"]: item for item in json.loads(PROCEDURES.read_text(encoding="utf-8"))}


def joined(record):
    lines = []
    for value in (record.get("sections") or {}).values():
        if isinstance(value, list):
            lines.extend(str(entry) for entry in value)
    return "\n".join(lines).lower()


class ShoulderReductionTests(unittest.TestCase):
    """The STOP-SHIP and owner-queue P0 item 6. Neurovascular compromise sat in
    `contraindications`, where it reads as a reason to wait. The humeral head is
    what is compressing the artery."""

    def setUp(self):
        self.record = load()["shoulder_reduction"]
        self.text = joined(self.record)

    def test_compromise_is_not_listed_as_a_contraindication(self):
        contra = " ".join(self.record["sections"]["contraindications"]).lower()
        self.assertNotIn("neurovascular compromise needing urgent surgical evaluation", contra)
        self.assertIn("neurovascular compromise is not a contraindication", contra)

    def test_compromise_is_stated_as_a_reason_to_reduce_sooner(self):
        self.assertIn("reduce sooner, not wait", self.text)
        self.assertIn("call the specialist in parallel, not first", self.text)

    def test_the_pulseless_limb_has_an_explicit_sequence(self):
        self.assertIn("call vascular surgery and reduce now", self.text)

    def test_the_nerve_case_and_the_vessel_case_are_separated(self):
        """They are different problems with different urgency, and collapsing
        them is what produced the original contraindication line."""
        self.assertIn("axillary nerve deficit", self.text)
        self.assertIn("pulseless or ischemic limb", self.text)


class TourniquetFailSafeTests(unittest.TestCase):
    """The other STOP-SHIP. The UK alert counted two amputations from digital
    tourniquets nobody removed. A fail-safe is a visible device, a recorded
    time, its own removal step, and a perfusion check - not a reminder."""

    def setUp(self):
        self.text = joined(load()["foreign_body_removal_soft_tissue"])

    def test_the_device_must_be_impossible_to_miss(self):
        self.assertIn("cannot be forgotten", self.text)
        self.assertIn("left hanging outside the drape", self.text)

    def test_application_and_removal_times_are_both_recorded(self):
        self.assertIn("record the time of application", self.text)
        self.assertIn("total tourniquet time", self.text)

    def test_removal_is_its_own_step_with_a_perfusion_check(self):
        self.assertIn("remove the tourniquet and say so out loud", self.text)
        self.assertIn("capillary refill", self.text)

    def test_imaging_absolutes_are_qualified(self):
        """"X-ray detects glass" and "wood is invisible" both turned a
        probability into a rule, in opposite directions."""
        self.assertIn("it's not a rule-out", self.text)
        self.assertNotIn("x-ray detects glass, metal, gravel, and bone.", self.text)


class ParacentesisTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["paracentesis"])

    def test_the_numeric_clotting_gates_are_gone(self):
        """INR and platelet thresholds are not bleeding-risk scores in
        cirrhosis, and the guidance recommends against the tests themselves."""
        self.assertNotIn("are relative contraindications", self.text)
        self.assertIn("no inr or platelet threshold applies", self.text)

    def test_the_sub_five_litre_albumin_exception_exists(self):
        self.assertIn("acute-on-chronic liver failure", self.text)
        self.assertIn("a judgement call, not a threshold", self.text)

    def test_the_paired_serum_albumin_is_ordered_with_the_tap(self):
        """A lone ascitic albumin cannot produce a gradient, and the serum half
        is the one that gets forgotten."""
        self.assertIn("paired serum albumin", self.text)


class KneeArthrocentesisTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["knee_arthrocentesis"])

    def test_the_fifty_thousand_heuristic_is_replaced(self):
        self.assertNotIn("septic until proven otherwise, regardless of crystals", self.text)
        self.assertIn("no synovial white cell count rules septic arthritis in or out", self.text)

    def test_crystals_do_not_exclude_infection(self):
        self.assertIn("gout and a septic joint can coexist in the same knee", self.text)

    def test_the_sepsis_exception_to_tapping_first_is_named(self):
        self.assertIn("if septic or in shock: antibiotics first (blood cultures first), tap after", self.text)


class CanthotomyTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["lateral_canthotomy"])

    def test_the_scissors_are_blunt(self):
        self.assertIn("blunt-tipped scissors", self.text)
        self.assertNotIn("iris or sharp straight scissors\n", self.text + "\n")

    def test_superior_release_requires_a_complete_inferior_release_first(self):
        """The commonest reason the orbit is still tense is an incomplete
        inferior cantholysis, not a need to go superior."""
        self.assertIn("confirm the inferior release is complete", self.text)
        self.assertIn("lacrimal artery and gland risk", self.text)

    def test_both_eyes_and_untestable_findings_are_documented(self):
        self.assertIn("both eyes documented", self.text)
        self.assertIn("recorded as not testable", self.text)


class NasalPackingTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["anterior_nasal_packing"])

    def test_rapid_rhino_is_water_outside_and_air_inside(self):
        """The card said "air or saline" for the cuff. The manufacturer says
        sterile water to activate the coating and air only in the cuff."""
        self.assertIn("sterile water for at least 30 seconds", self.text)
        self.assertIn("inflate the cuff slowly with air only", self.text)
        self.assertNotIn("inflate balloon with air or saline", self.text)

    def test_local_measures_come_before_reversing_an_anticoagulant(self):
        self.assertIn("reserve reversal or withholding the drug for life-threatening bleeding", self.text)
        self.assertIn("resorbable packing", self.text)

    def test_antibiotics_after_packing_are_not_a_default_prescription(self):
        self.assertIn("antibiotics after packing are not automatic", self.text)
        self.assertNotIn("prescribe antibiotics covering for toxic shock", self.text)

    def test_the_topical_lidocaine_dose_is_quantified(self):
        """4% on mucosa absorbs close to intravenous rates and this record has
        no calculator, so the milligrams have to be in the sentence."""
        self.assertIn("40 mg per milliliter", self.text)


class PeritonsillarTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["peritonsillar_abscess_drainage"])

    def test_the_airway_question_precedes_the_technique_question(self):
        self.assertIn("stridor, drooling or inability to handle secretions", self.text)
        self.assertIn("the airway question comes before the technique question", self.text)

    def test_benzocaine_carries_its_methaemoglobinaemia_pathway(self):
        self.assertIn("methemoglobinemia", self.text)
        self.assertIn("methylene blue", self.text)

    def test_the_steroid_is_a_single_dose_not_a_pack(self):
        self.assertNotIn("medrol dose pack", self.text)
        self.assertIn("supports one dose, not a multi-day tapering pack", self.text)

    def test_aspiration_is_not_overclaimed_as_first_line(self):
        self.assertNotIn("needle aspiration is the first-line ed drainage technique", self.text)
        self.assertIn("no drainage technique is established as superior", self.text)


class AbscessTests(unittest.TestCase):
    def setUp(self):
        self.text = joined(load()["abscess_incision_drainage"])

    def test_irrigation_is_optional_rather_than_a_confirmation_criterion(self):
        self.assertNotIn("until return is clear", self.text)
        self.assertIn("irrigation is optional", self.text)

    def test_packing_is_not_routine_for_a_small_simple_cavity(self):
        self.assertIn("packing is also not routine", self.text)
        self.assertIn("under about 5 cm", self.text)

    def test_antibiotics_are_framed_as_a_shared_decision(self):
        self.assertIn("antibiotics are a shared decision rather than a reflex in either direction", self.text)
        self.assertIn("weak shared-decision recommendation", self.text)


class TetanusTests(unittest.TestCase):
    """"Update tetanus" is not a decision. The vaccine and the immune globulin
    are two separate answers to two separate questions, and the globulin half is
    the one that goes missing."""

    def setUp(self):
        self.text = joined(load()["laceration_repair"])

    def test_the_wound_classification_and_the_dose_count_are_both_required(self):
        self.assertIn("clean and minor, or dirty and major", self.text)
        self.assertIn("count the patient's prior tetanus doses", self.text)

    def test_both_intervals_are_stated(self):
        self.assertIn("10 or more years ago for a clean minor wound", self.text)
        self.assertIn("5 or more years ago for a dirty or major wound", self.text)

    def test_immune_globulin_has_its_dose_and_its_immunodeficiency_rule(self):
        self.assertIn("250 iu intramuscularly", self.text)
        self.assertIn("regardless of the vaccination history", self.text)

    def test_the_globulin_is_stocked_rather_than_assumed(self):
        self.assertIn("tetanus immune globulin, both obtainable in the department", self.text)


class LaneDosingTests(unittest.TestCase):
    """Eight records told the reader to inject a local anaesthetic and stated no
    ceiling anywhere. The validator never asked, because both of its
    agent-ceiling rules only fire on records that already carry a `dosing`
    block - the gate was weakest exactly where the content was."""

    def setUp(self):
        self.records = load()

    def test_every_infiltrating_record_now_carries_a_ceiling(self):
        for pid in INFILTRATING_IDS:
            with self.subTest(pid):
                dosing = self.records[pid].get("dosing")
                self.assertIsInstance(dosing, dict, f"{pid} has no dosing block")
                self.assertTrue(dosing["agents"])
                self.assertEqual(dosing["rescueCardID"], "local_anesthetic_systemic_toxicity")

    def test_the_cumulative_rule_is_fractional_not_a_shared_pool(self):
        """Two agents do not share one number of milligrams. The old wording
        said they did, which is the P1 finding."""
        for pid in INFILTRATING_IDS:
            with self.subTest(pid):
                warning = self.records[pid]["dosing"]["cumulativeWarning"].lower()
                self.assertIn("not interchangeable", warning)
                self.assertIn("fraction of its own ceiling", warning)

    def test_the_site_of_injection_is_named_as_an_absorption_modifier(self):
        for pid in INFILTRATING_IDS:
            with self.subTest(pid):
                caveats = " ".join(self.records[pid]["dosing"]["caveats"]).lower()
                self.assertIn("peaks higher from a vascular bed", caveats)


class LaneReferenceTests(unittest.TestCase):
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


class KitAndCardAgreementTests(unittest.TestCase):
    """A kit and its procedure card are read together - the kit to gather the
    equipment, the card to do the procedure. When they disagree the reader
    collects the wrong thing before ever opening the card.

    The lumbar puncture kit listed "20g Quincke for standard adult" and filed
    the atraumatic needle under backup equipment, while the card said in three
    separate places that the atraumatic pencil-point needle is the default and
    the Quincke is the fallback. Nothing compared the two objects."""

    def setUp(self):
        self.kits = {
            kit["id"]: kit
            for kit in json.loads(
                (Path(__file__).resolve().parents[2] / "Procedures" / "Resources"
                 / "kits.json").read_text(encoding="utf-8")
            )
        }
        self.records = load()

    def _kit_text(self, kit_id):
        kit = self.kits[kit_id]
        return " ".join(
            item
            for key in ("inKit", "outsideKit", "commonlyForgotten",
                        "patientSetup", "sterileSetup", "backupEquipment")
            for item in kit.get(key, [])
        ).lower()

    def test_the_lp_kit_agrees_with_the_card_on_which_needle_is_default(self):
        card = " ".join(self.records["lumbar_puncture"]["sections"]["equipment"]).lower()
        self.assertIn("atraumatic pencil-point spinal needle", card)
        self.assertIn("the default for adults", card)
        self.assertIn("quincke", card)
        self.assertIn("fallback", card)

        kit = self._kit_text("kit_lumbar_puncture")
        self.assertIn("pencil-point", kit)
        self.assertIn("the default for adults", kit)
        # The inversion that shipped: Quincke presented as the standard choice.
        self.assertNotIn("quincke for standard adult", kit)
        # The card requires an introducer twice; the kit never mentioned one.
        self.assertIn("introducer", kit)
        # Quincke may appear, but only as the fallback.
        quincke = [s for s in kit.split(";") if "quincke" in s]
        for clause in quincke:
            self.assertTrue(
                "fallback" in clause or "no atraumatic needle is stocked" in clause,
                f"Quincke named without marking it the fallback: {clause.strip()!r}",
            )

    def test_the_chest_tube_kit_agrees_with_the_card_on_large_bore_size(self):
        """The kit said 28-36 Fr for hemothorax where the card said 28-32 Fr.
        Same device, same indication, two ranges, and a reader who sizes from
        the kit picks a tube the card does not sanction. Owner kept 28-32 on
        2026-08-04, so the kit follows the card."""
        card = " ".join(
            self.records["thoracostomy_chest_tube"]["sections"]["equipment"]
        ).lower()
        kit = self._kit_text("kit_chest_tube")
        self.assertIn("28-32 fr", card)
        self.assertIn("28-32 fr", kit)
        self.assertNotIn("28-36 fr", kit)
