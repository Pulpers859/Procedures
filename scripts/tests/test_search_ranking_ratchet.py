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

    def test_dropping_a_tag_is_caught_as_a_lost_probe(self):
        """A deleted tag cannot surface as `worse`.

        The probe is derived from the tag, so removing the tag removes the
        probe from the set rather than moving it down - it lands in `removed`.
        That is still a query the reader could run and now cannot, so
        check_search_ranking exits non-zero on it too.

        This replaces an assertion that dropping central_venous_catheter's
        "catheter" tag made its "central line" probe rank worse. It no longer
        does: scoring now takes each term's best field rather than summing it
        across all of them, so the title "Central Venous Catheter" carries the
        term on its own. The scorer absorbing that regression is the point of
        the rarity/best-field rework - but the guard still has to fail on
        something, so it asserts the channel that does fire.
        """
        ranks = self._mutated(
            "central_venous_catheter", lambda p: p["tags"].remove("catheter")
        )
        worse, _, _, removed = ratchet.compare(ratchet.load_baseline(), ranks)
        self.assertEqual(worse, [], "no probe should rank lower; the title still carries it")
        self.assertTrue(
            any("central_venous_catheter|catheter" in line for line in removed),
            f"the ratchet did not notice the lost probe: {removed}",
        )

    def test_emptying_a_weighted_section_is_caught(self):
        ranks = self._mutated(
            "cricothyrotomy", lambda p: p["sections"].__setitem__("shiftMode", [])
        )
        worse, _, _, _ = ratchet.compare(ratchet.load_baseline(), ranks)
        self.assertTrue(worse, "emptying shiftMode cost nothing, which cannot be right")

    def test_a_lost_probe_fails_the_check_not_just_the_report(self):
        """Printing "gone" and exiting 0 is how a deleted tag would ship."""
        _, _, _, removed = ratchet.compare(
            ratchet.load_baseline(),
            self._mutated("block_auricular", lambda p: p["tags"].remove("ear block")),
        )
        self.assertTrue(removed, "dropping a distinctive tag must register somewhere")

    def test_an_unchanged_corpus_reports_nothing(self):
        worse, better, added, removed = ratchet.compare(
            ratchet.load_baseline(), ratchet.current_ranks()
        )
        self.assertEqual((worse, better, added, removed), ([], [], [], []))


if __name__ == "__main__":
    unittest.main()
