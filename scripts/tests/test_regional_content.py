"""Guards on the regional-anaesthesia content adjudicated on 2026-07-31 (lane
reports 06 through 09) and on the P1 dosing governance model.

Twenty-eight records with near-identical findings got one safety spine applied
word-for-word rather than twenty-eight bespoke edits, so most of what these
tests assert is uniformity: the guarantee is that no block is missing the
sentence its neighbours all carry. The per-block classes hold the line on the
four needle targets from owner-queue P0 item 4 and the specific overclaims each
lane report named."""
import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PROCEDURES = REPO / "Procedures" / "Resources" / "procedures.json"
RESCUE_CARDS = REPO / "Procedures" / "Resources" / "rescue_cards.json"

VALID_REVIEW_TIMES = {"60 sec", "2 min", "3 min", "4 min", "5 min", "Deep"}
TRUNCAL = {"block_tap", "block_serratus_anterior", "block_pecs", "block_thoracic_esp"}


def load():
    return json.loads(PROCEDURES.read_text(encoding="utf-8"))


def regional():
    return [p for p in load() if p.get("category") == "Regional Anesthesia"]


def by_id():
    return {p["id"]: p for p in load()}


def joined(record):
    lines = []
    for value in (record.get("sections") or {}).values():
        if isinstance(value, list):
            lines.extend(str(entry) for entry in value)
    return "\n".join(lines).lower()


class SafetySpineTests(unittest.TestCase):
    """One spine, applied identically. A block that quietly loses a line its 27
    neighbours carry is the failure mode this suite exists for - it would read
    fine and be missing the part that matters.

    The fragments asserted below are the canonical spine wording. Rewording the
    spine in procedures.json means changing it in all 28 records and updating
    the fragment here in the same commit - that coupling is deliberate, because
    it is what stops one record drifting on its own."""

    def setUp(self):
        self.blocks = regional()
        self.assertEqual(len(self.blocks), 28)

    def test_every_block_states_that_spread_is_not_success(self):
        """Ultrasound confirms where the drug went. Twenty-five of these records
        had one or two confirmation lines and none of them tested the patient."""
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn(
                    "spread on the screen shows where the drug went, "
                    "not whether the patient is blocked",
                    joined(block),
                )

    def test_every_block_carries_an_onset_time_before_calling_failure(self):
        """The guarantee is the times themselves, so pin those rather than the
        sentence around them."""
        for block in self.blocks:
            with self.subTest(block["id"]):
                text = joined(block)
                self.assertIn("onset time before judging", text)
                self.assertIn("lidocaine 5-10 minutes", text)
                self.assertIn("bupivacaine and ropivacaine 15-30", text)

    def test_every_block_has_a_partial_and_a_failed_pathway(self):
        """P2: "add explicit partial/failed block reassessment and rescue paths
        rather than treating ultrasound spread as proof of clinical success"."""
        for block in self.blocks:
            with self.subTest(block["id"]):
                text = joined(block)
                self.assertIn("partial block:", text)
                self.assertIn("failed block:", text)
                self.assertIn("do not re-inject the same volume in the same place", text)
                self.assertIn("infiltration within the remaining ceiling", text)

    def test_every_block_has_the_three_stop_signs(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn(
                    "pain on injection, paresthesia, or high resistance", joined(block)
                )

    def test_every_block_protects_the_insensate_part(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn("protect the insensate part", joined(block))

    def test_every_block_says_how_compartment_syndrome_announces_itself(self):
        """The fear is that a block hides it. What actually happens is that the
        presentation changes, and a team told only "blocks mask it" watches for
        the wrong thing."""
        for block in self.blocks:
            with self.subTest(block["id"]):
                text = joined(block)
                self.assertIn(
                    "compartment syndrome still shows through a working block", text
                )
                self.assertIn("rising analgesic requirement", text)
                self.assertIn("pain breaking through", text)

    def test_every_block_requires_chlorhexidine_that_is_allowed_to_dry(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn("left to dry", joined(block))

    def test_every_block_documents_a_pre_existing_deficit_first(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn(
                    "pre-existing neurological deficit in the target territory",
                    joined(block),
                )

    def test_the_setup_requirement_scales_with_the_block(self):
        """Requiring IV access and full monitoring for a digital block produces
        a rule nobody follows, which is worse than no rule. Major blocks get the
        full setup; minor blocks get asepsis and the location of the lipid.

        The full-setup requirement is `majorBlockMonitoring: true` plus the
        shared string in MajorBlockMonitoring.requirement (SwiftUI side), not
        copy-pasted prose - see scripts/apply_local_reviews.py's
        procedure_fingerprint for why it still has to be material content."""
        major = {
            "block_interscalene", "block_supraclavicular", "block_raptir",
            "block_superficial_cervical_plexus", "block_serratus_anterior",
            "block_thoracic_esp", "block_tap", "block_pecs", "block_femoral_nerve",
            "block_peng", "fascia_iliaca_block", "block_popliteal_sciatic",
            "block_transgluteal_sciatic", "block_saphenous_nerve",
        }
        for block in self.blocks:
            with self.subTest(block["id"]):
                text = joined(block)
                self.assertIn("lipid emulsion", text)
                if block["id"] in major:
                    self.assertTrue(block.get("majorBlockMonitoring"))
                else:
                    self.assertFalse(block.get("majorBlockMonitoring"))

    def test_antithrombotic_handling_matches_the_depth_of_the_block(self):
        """ASRA applies neuraxial-equivalent timing to deep blocks and asks a
        different question - compressibility, vascularity, consequence - of the
        rest. TAP had it exactly backwards and called itself a deep plane."""
        deep = {"block_raptir", "block_transgluteal_sciatic"}
        for block in self.blocks:
            with self.subTest(block["id"]):
                text = joined(block)
                if block["id"] in deep:
                    self.assertIn("neuraxial-equivalent timing", text)
                else:
                    self.assertIn("site compressibility, vascularity", text)
                    # The retired wording argued the point instead of stating it.
                    self.assertNotIn("do not transpose a neuraxial interval", text)


    def test_every_block_documents_side_agent_and_total_milligrams(self):
        """Three lane reports named this one: documentation omitted side,
        approach, concentration, total mg, cumulative prior dose, and the
        antithrombotic decision. Twenty-three of the 28 had a single line."""
        for block in self.blocks:
            with self.subTest(block["id"]):
                doc = " ".join(block["sections"]["documentation"]).lower()
                self.assertIn("side and level", doc)
                self.assertIn("total in milligrams", doc)
                self.assertIn("running total", doc)
                self.assertIn("bleeding-risk assessment", doc)
                self.assertIn("recorded as pre-existing", doc)

    def test_every_block_calculates_before_it_draws_up(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn(
                    "before drawing up - say it out loud", joined(block)
                )

    def test_every_block_plans_for_failure_before_starting(self):
        for block in self.blocks:
            with self.subTest(block["id"]):
                self.assertIn("backup plan before you start", joined(block))


class MetadataTests(unittest.TestCase):
    def test_no_record_carries_an_out_of_schema_review_time(self):
        """26 blocks shipped `reviewTime: "standard"`. The validator checked
        that the field was present and never what it said."""
        for record in load():
            with self.subTest(record["id"]):
                self.assertIn(record["reviewTime"], VALID_REVIEW_TIMES)

    def test_the_dead_icon_field_is_gone(self):
        """It was on 26 records, it said "lungs" on a mental nerve block, and no
        Swift code has ever decoded it."""
        for record in load():
            with self.subTest(record["id"]):
                self.assertNotIn("icon", record)


class DosingGovernanceTests(unittest.TestCase):
    """P1. The ceilings themselves are the owner's and are locked elsewhere;
    what changed here is what the card says about them."""

    def setUp(self):
        self.with_dosing = [p for p in load() if p.get("dosing")]

    def test_every_dosing_block_exists_on_the_expected_count(self):
        """40 from the regional/infiltration governance pass, plus 4 added when
        unbounded_agent_issues was widened to scan procedures with no dosing
        block at all: pericardiocentesis, lumbar_puncture, arterial_line, and
        anterior_nasal_packing all named lidocaine with no ceiling anywhere."""
        self.assertEqual(len(self.with_dosing), 44)

    def test_the_cumulative_rule_is_fractional_everywhere(self):
        """"All local anesthetic this encounter shares one maximum" is not a
        valid mixed-agent calculation. Agents do not share a pool of
        milligrams - each has its own ceiling and the fractions add."""
        warnings = {p["dosing"]["cumulativeWarning"] for p in self.with_dosing}
        self.assertEqual(len(warnings), 1, "the cumulative rule has diverged")
        warning = warnings.pop().lower()
        self.assertIn("not interchangeable", warning)
        self.assertIn("fraction of its own ceiling", warning)
        self.assertNotIn("share one maximum", warning)

    def test_the_intraosseous_card_is_excluded_from_the_ceiling_framing(self):
        """Its lidocaine figure is the dose to give, not a maximum to stay
        under - the card's own first caveat says so. Two caveats written about
        ceilings contradict that, and a contradiction on a paediatric analgesic
        dose is exactly the kind this model exists to prevent."""
        caveats = " ".join(
            next(p for p in load() if p["id"] == "intraosseous_access")["dosing"]["caveats"]
        ).lower()
        self.assertIn("the dose to give, not a range to stay under", caveats)
        self.assertNotIn("the ceiling is a limit rather than a target", caveats)
        self.assertNotIn("governed policy", caveats)

    def test_every_block_says_the_ceiling_is_a_policy_not_a_fact(self):
        """The labels publish no universal mg/kg figure - they require
        individualisation. Presenting the number without that reads as
        pharmacology rather than as this app's governed choice."""
        for record in self.with_dosing:
            if record["id"] == "intraosseous_access":
                continue  # a target dose, not a ceiling; see the test above
            with self.subTest(record["id"]):
                caveats = " ".join(record["dosing"]["caveats"]).lower()
                self.assertIn("this app's governed policy", caveats)
                self.assertIn("peaks higher from a vascular bed", caveats)

    def test_the_truncal_blocks_carry_the_pharmacokinetic_warning(self):
        """The TAP stop-ship: bilateral dosing at 3 mg/kg ropivacaine, and
        bilateral 200 mg totals, produced potentially toxic plasma
        concentrations at doses a weight-based calculator calls acceptable."""
        for record in self.with_dosing:
            caveats = " ".join(record["dosing"]["caveats"]).lower()
            present = "potentially toxic plasma concentrations" in caveats
            with self.subTest(record["id"]):
                self.assertEqual(present, record["id"] in TRUNCAL)

    def test_no_block_states_a_volume_it_cannot_convert_to_milligrams(self):
        """Ten blocks said "Local anesthetic (5-10 mL)" beside a table with
        three agents and three different ceilings."""
        for record in regional():
            with self.subTest(record["id"]):
                lines = " ".join(
                    record["sections"]["equipment"] + record["sections"]["steps"]
                ).lower()
                self.assertTrue(
                    any(agent in lines for agent in ("lidocaine", "bupivacaine", "ropivacaine")),
                    "no agent named anywhere in equipment or steps",
                )

    def test_every_strength_named_in_prose_is_one_the_calculator_can_convert(self):
        """A card that recommends "0.25% bupivacaine or ropivacaine" has offered
        0.25% ropivacaine, which is not a supplied strength - fascia_iliaca_block
        says so in as many words - and is not in that card's own concentration
        list. The reader picks ropivacaine, opens the calculator, and cannot get
        from milligrams to millilitres.

        Three records shipped that phrasing. The neighbouring test checks the
        agent is *named*; this one checks the strength is *usable*.

        block_superior_alveolar and block_auricular had the same defect in the
        "X% A or B" form and were resolved by the owner on 2026-08-04: both now
        offer either 0.5% bupivacaine or 1% lidocaine, and both strengths are in
        those cards' concentration lists. There is nothing left to exempt."""
        pending = set()
        agent_word = r"(lidocaine|bupivacaine|ropivacaine)"
        shared = re.compile(rf"(\d+(?:\.\d+)?)\s*%\s+{agent_word}\s+or\s+{agent_word}\b", re.I)
        direct = re.compile(rf"(\d+(?:\.\d+)?)\s*%\s+{agent_word}\b", re.I)
        for record in regional():
            offered = {}
            for agent in (record.get("dosing") or {}).get("agents", []):
                base = (agent.get("agent") or "").lower().replace(" with epinephrine", "").strip()
                offered.setdefault(base, set()).update(
                    float(c) for c in (agent.get("concentrationsPercent") or [])
                )
            # A sentence that exists to rule a strength OUT is not recommending
            # it. fascia_iliaca_block says "0.25% ropivacaine is not a supplied
            # strength and is not used here" - that is the fix, not the defect.
            disclaimer = re.compile(
                r"not a supplied strength|is not used|not offered|not stocked", re.I
            )
            for section in ("equipment", "steps"):
                for line in record["sections"].get(section, []):
                    named = set()
                    for sentence in re.split(r"(?<=[.;])\s+", line):
                        if disclaimer.search(sentence):
                            continue
                        for m in shared.finditer(sentence):
                            named.add((m.group(2).lower(), float(m.group(1))))
                            named.add((m.group(3).lower(), float(m.group(1))))
                        for m in direct.finditer(sentence):
                            named.add((m.group(2).lower(), float(m.group(1))))
                    for agent, percent in sorted(named):
                        if agent not in offered or not offered[agent]:
                            continue
                        if (record["id"], agent, percent) in pending:
                            continue
                        with self.subTest(record["id"], agent=agent, percent=percent):
                            self.assertIn(
                                percent, offered[agent],
                                f"{record['id']} names {percent}% {agent} in {section} "
                                f"but the calculator offers only "
                                f"{sorted(offered[agent])}%, so mg cannot be "
                                f"converted to mL",
                            )

    def test_large_volume_blocks_do_not_offer_lidocaine(self):
        """The governance rule: a block only offers agents whose ceiling its
        stated volume fits under. Thirty millilitres is not a lidocaine block."""
        for pid in ("block_popliteal_sciatic", "block_transgluteal_sciatic", "block_saphenous_nerve"):
            with self.subTest(pid):
                text = joined(by_id()[pid])
                self.assertIn("not a lidocaine block", text)


class NeedleTargetTests(unittest.TestCase):
    """Owner-queue P0 item 4. Four records pointed a needle somewhere it should
    not go, and in three of them the wrong endpoint was the one written down."""

    def setUp(self):
        self.records = by_id()

    def test_popliteal_sciatic_targets_the_paraneural_not_the_epineural_sheath(self):
        """"Within its epineural sheath" reads as an instruction to enter the
        nerve. The target is the common paraneural sheath, outside both
        divisions."""
        text = joined(self.records["block_popliteal_sciatic"])
        self.assertNotIn("epineural sheath (the 'vloka sheath')", text)
        self.assertIn("outside the nerves, not inside them", text)
        self.assertIn("stop and withdraw - the injectate should push the nerve away, not swell it", text)

    def test_serratus_does_not_slide_off_the_rib(self):
        """Off the rib is the intercostal space, and the pleura is behind it."""
        text = joined(self.records["block_serratus_anterior"])
        self.assertNotIn("hit the rib, slide off, inject", text)
        self.assertIn("the rib is the endpoint, not a waypoint", text)
        self.assertIn("off the rib is the intercostal space", text)

    def test_pecs_two_has_no_rib_endpoint(self):
        text = joined(self.records["block_pecs"])
        self.assertNotIn("serratus anterior (or ribs). inject", text)
        self.assertIn("stop at that plane - passing through serratus onto the ribs", text)

    def test_infraorbital_has_a_bounded_trajectory(self):
        """Depth without a direction is the part that goes wrong: a shallow
        angle points at the orbit."""
        text = joined(self.records["block_infraorbital"])
        self.assertIn("keep the palpating finger over the foramen", text)
        self.assertIn("long axis of the second premolar", text)
        self.assertIn("never advance toward or into the orbit", text)


class OverclaimTests(unittest.TestCase):
    def setUp(self):
        self.records = by_id()

    def test_interscalene_phrenic_risk_is_volume_dependent(self):
        """The 100% figure came from 20 mL. This card prescribes 10-15."""
        text = joined(self.records["block_interscalene"])
        self.assertNotIn("phrenic nerve palsy (100% block)", text)
        self.assertIn("volume-dependent, not universal", text)
        self.assertIn("contralateral recurrent laryngeal nerve palsy", text)

    def test_supraclavicular_states_one_total_volume(self):
        """Equipment said 15-20 mL and the steps added up to 15-25."""
        record = self.records["block_supraclavicular"]
        text = joined(record)
        self.assertIn("20 ml total", text)
        self.assertNotIn("15-20 ml", text)
        self.assertNotIn("15-25", text)
        self.assertNotIn("bouncing off the rib", text)

    def test_raptir_reduces_risk_rather_than_removing_it(self):
        text = joined(self.records["block_raptir"])
        self.assertNotIn("without the pneumothorax/phrenic risk", text)
        self.assertIn("less phrenic and pleural risk than a supraclavicular block, but not zero", text)
        self.assertIn("hemothorax", text)
        self.assertIn("acoustic shadow", text)

    def test_esp_is_not_described_as_remarkably_safe(self):
        text = joined(self.records["block_thoracic_esp"])
        self.assertNotIn("remarkably safe", text)
        self.assertIn("does not remove it", text)
        self.assertIn("variable, not dermatomally predictable", text)

    def test_serratus_is_an_adjunct_rather_than_essential(self):
        text = joined(self.records["block_serratus_anterior"])
        self.assertNotIn("essential for multi-level rib fractures", text)
        self.assertIn("useful, not essential", text)

    def test_tap_is_classified_as_a_superficial_block(self):
        text = joined(self.records["block_tap"])
        self.assertIn("not an automatic prohibition", text)
        self.assertIn("superficial, compressible plane block, not a deep block", text)
        self.assertNotIn("deep fascial plane", text)

    def test_supraorbital_states_one_volume(self):
        """Equipment said 3-5 mL, the steps added to 2-4, the worked example
        used 5. Beside an eye."""
        text = joined(self.records["block_supraorbital"])
        self.assertIn("4 ml total", text)
        self.assertIn("never direct or advance the needle into the orbit", text)


class RegionalReferenceTests(unittest.TestCase):
    def test_no_regional_block_still_cites_an_undated_textbook(self):
        for record in regional():
            with self.subTest(record["id"]):
                refs = " ".join(record["sections"]["references"]).lower()
                self.assertNotIn("roberts and hedges", refs)
                self.assertNotIn("tintinalli", refs)
                self.assertNotIn("nysora", refs)

    def test_every_regional_block_cites_the_shared_safety_sources(self):
        for record in regional():
            with self.subTest(record["id"]):
                refs = " ".join(record["sections"]["references"])
                self.assertIn("rapm-2024-105651", refs)   # ASRA infection control
                self.assertIn("AAP.0000000000000720", refs)  # ASRA LAST advisory
                self.assertIn("rapm-2024-105766", refs)   # ASRA antithrombotic


class RescueCardReferenceTests(unittest.TestCase):
    """Eight rescue cards carried the literal placeholder string the release
    gate looks for, which is why they were the last non-reviewer blockers in
    the corpus."""

    def test_no_rescue_card_carries_a_placeholder_reference(self):
        cards = json.loads(RESCUE_CARDS.read_text(encoding="utf-8"))
        for card in cards:
            with self.subTest(card["id"]):
                refs = " ".join(card.get("references") or []).lower()
                self.assertTrue(refs.strip(), "no references at all")
                self.assertNotIn("replace with formal reviewer-approved references", refs)

    def test_every_rescue_card_has_a_resolvable_locator(self):
        cards = json.loads(RESCUE_CARDS.read_text(encoding="utf-8"))
        for card in cards:
            with self.subTest(card["id"]):
                refs = card.get("references") or []
                self.assertTrue(
                    any("https://" in ref or "doi.org" in ref for ref in refs),
                    f"{card['id']} has no resolvable reference locator",
                )


if __name__ == "__main__":
    unittest.main()
