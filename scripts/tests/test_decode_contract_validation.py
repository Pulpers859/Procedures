"""Negative controls for the decode-contract rules.

Swift decodes every content record through `FailableDecodable`, which turns a
malformed record into `nil` rather than throwing. A missing required field or
an out-of-enum value therefore does not fail loudly — the record is silently
dropped from the shipped app. Before these rules existed, every mutation below
passed `validate_procedures.py` with zero blockers, so content loss shipped
green.

Each test asserts the validator now blocks a mutation that Swift would drop.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_procedures.py"
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

RESOURCES = ROOT / "Procedures" / "Resources"
PROCEDURES = json.loads((RESOURCES / "procedures.json").read_text(encoding="utf-8"))
RESCUE_CARDS = json.loads((RESOURCES / "rescue_cards.json").read_text(encoding="utf-8"))
KITS = json.loads((RESOURCES / "kits.json").read_text(encoding="utf-8"))


def blockers(procedures, cards, kits):
    return [issue for issue in MODULE.collect_issues(procedures, cards, kits) if issue[0] == "BLOCKER"]


class DecodeContractTests(unittest.TestCase):
    def test_shipped_content_has_no_blockers(self):
        """Baseline: the real corpus must stay clean, so a failure below is the
        mutation and not pre-existing noise."""
        self.assertEqual(blockers(PROCEDURES, RESCUE_CARDS, KITS), [])

    def _procedures_with(self, mutate):
        mutated = copy.deepcopy(PROCEDURES)
        mutate(mutated)
        return mutated

    def test_procedure_missing_setting_is_a_blocker(self):
        for mutation in (lambda p: p[0].pop("setting"), lambda p: p[0].update(setting=[])):
            with self.subTest(mutation=mutation):
                self.assertTrue(blockers(self._procedures_with(mutation), RESCUE_CARDS, KITS))

    def test_procedure_with_unknown_setting_value_is_a_blocker(self):
        mutated = self._procedures_with(lambda p: p[0].update(setting=["Prehospital"]))
        self.assertTrue(blockers(mutated, RESCUE_CARDS, KITS))

    def test_procedure_missing_identity_or_review_time_is_a_blocker(self):
        for field in ("id", "title", "reviewTime"):
            with self.subTest(field=field):
                mutated = self._procedures_with(lambda p, f=field: p[0].pop(f))
                self.assertTrue(blockers(mutated, RESCUE_CARDS, KITS))

    def test_unknown_visual_asset_kind_is_a_blocker(self):
        def mutate(procedures):
            for procedure in procedures:
                if procedure.get("visualAssets"):
                    procedure["visualAssets"][0]["kind"] = "Diagram"
                    return
            self.fail("no procedure with visualAssets to mutate")

        self.assertTrue(blockers(self._procedures_with(mutate), RESCUE_CARDS, KITS))

    def test_rescue_card_with_wrong_case_acuity_is_a_blocker(self):
        # "CRASH" also silently disabled the Crash-card dose rule, which keys
        # on an exact string match.
        mutated = copy.deepcopy(RESCUE_CARDS)
        mutated[0]["acuity"] = "CRASH"
        self.assertTrue(blockers(PROCEDURES, mutated, KITS))

    def test_rescue_card_missing_related_procedure_ids_is_a_blocker(self):
        mutated = copy.deepcopy(RESCUE_CARDS)
        mutated[0].pop("relatedProcedureIDs")
        self.assertTrue(blockers(PROCEDURES, mutated, KITS))

    def test_kit_with_unknown_category_is_a_blocker(self):
        mutated = copy.deepcopy(KITS)
        mutated[0]["category"] = "Sundries"
        self.assertTrue(blockers(PROCEDURES, RESCUE_CARDS, mutated))

    def test_kit_missing_any_required_list_is_a_blocker(self):
        for field in ("outsideKit", "commonlyForgotten", "sterileSetup", "backupEquipment", "relatedProcedureIDs"):
            with self.subTest(field=field):
                mutated = copy.deepcopy(KITS)
                mutated[0].pop(field)
                self.assertTrue(blockers(PROCEDURES, RESCUE_CARDS, mutated))


if __name__ == "__main__":
    unittest.main()
