"""The ranking ratchet has to fail when retrieval gets worse.

A guard that cannot fail is worse than no guard, because it reads as coverage.
These tests break the content on purpose and check the ratchet notices.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_search_ranking as ratchet  # noqa: E402
import search_model  # noqa: E402


class ProbeDerivationTests(unittest.TestCase):
    def test_probes_are_the_records_own_title_and_tags(self):
        procedure = {"title": "Central Venous Catheter", "tags": ["central line", "CVC"]}
        self.assertEqual(
            search_model.self_retrieval_probes(procedure),
            ["Central Venous Catheter", "central line", "CVC"],
        )

    def test_a_tag_repeating_the_title_is_probed_once(self):
        procedure = {"title": "Arterial Line", "tags": ["arterial line", "a-line"]}
        self.assertEqual(
            search_model.self_retrieval_probes(procedure), ["Arterial Line", "a-line"]
        )

    def test_every_shipped_procedure_yields_at_least_one_probe(self):
        for procedure in search_model.PROCEDURES:
            with self.subTest(procedure=procedure["id"]):
                self.assertTrue(search_model.self_retrieval_probes(procedure))


class BaselineTests(unittest.TestCase):
    def test_the_committed_baseline_matches_the_shipped_content(self):
        """Same check CI runs. Here too, so a local test run catches it before
        the push rather than after."""
        worse, _, added, removed = ratchet.compare(
            ratchet.load_baseline(), ratchet.current_ranks()
        )
        self.assertEqual(worse, [], "bedside retrieval regressed against the baseline")
        self.assertEqual(added, [], "new probes; regenerate with --update")
        self.assertEqual(removed, [], "probes disappeared; regenerate with --update")


class RatchetFiresTests(unittest.TestCase):
    """Mutation tests. Each breaks retrieval and expects a complaint."""

    def _mutated(self, procedure_id, mutate):
        procedures = copy.deepcopy(search_model.PROCEDURES)
        mutate(next(p for p in procedures if p["id"] == procedure_id))
        return ratchet.current_ranks(procedures)

    def test_dropping_a_tag_that_carried_a_term_is_caught(self):
        """The exact 2026-08-05 regression: trimming the central-line shiftMode
        removed the last high-weight "catheter", and "central line" started
        answering with the dialysis catheter."""
        ranks = self._mutated(
            "central_venous_catheter", lambda p: p["tags"].remove("catheter")
        )
        worse, _, _, _ = ratchet.compare(ratchet.load_baseline(), ranks)
        self.assertTrue(
            any("central_venous_catheter|central line" in line for line in worse),
            f"the ratchet did not notice: {worse}",
        )

    def test_emptying_a_weighted_section_is_caught(self):
        ranks = self._mutated(
            "cricothyrotomy", lambda p: p["sections"].__setitem__("shiftMode", [])
        )
        worse, _, _, _ = ratchet.compare(ratchet.load_baseline(), ranks)
        self.assertTrue(worse, "emptying shiftMode cost nothing, which cannot be right")

    def test_an_unchanged_corpus_reports_nothing(self):
        worse, better, added, removed = ratchet.compare(
            ratchet.load_baseline(), ratchet.current_ranks()
        )
        self.assertEqual((worse, better, added, removed), ([], [], [], []))


if __name__ == "__main__":
    unittest.main()
