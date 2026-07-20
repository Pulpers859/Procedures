"""Negative controls for the contentSource provenance rules, plus assertions
against the real shipped content. These prove the validator refuses dishonest
provenance shapes; they say nothing about clinical correctness."""
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_procedures.py"
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def item(**overrides):
    value = {
        "id": "test_item",
        "title": "Test Item",
        "lastReviewed": "2026-01-01",
        "version": "1.0",
        "reviewerStatus": "Needs Clinical Review",
        "contentSource": "ai-draft",
    }
    value.update(overrides)
    return {key: field for key, field in value.items() if field is not None}


class ProvenanceGovernanceTests(unittest.TestCase):
    def test_declared_ai_draft_awaiting_review_is_clean_of_provenance_blockers(self):
        issues = MODULE.governance_issues("Test", item())
        self.assertFalse(any(issue[0] == "BLOCKER" for issue in issues), issues)

    def test_missing_content_source_warns(self):
        issues = MODULE.governance_issues("Test", item(contentSource=None))
        self.assertTrue(any("missing contentSource" in issue[2] for issue in issues))

    def test_unknown_content_source_warns(self):
        issues = MODULE.governance_issues("Test", item(contentSource="chatbot"))
        self.assertTrue(any("unknown contentSource" in issue[2] for issue in issues))

    def test_reviewed_status_on_ai_draft_is_a_blocker(self):
        for source in ("ai-draft", None):
            with self.subTest(source=source):
                issues = MODULE.governance_issues(
                    "Test", item(reviewerStatus="Internally Reviewed", contentSource=source)
                )
                self.assertTrue(
                    any(issue[0] == "BLOCKER" and "still 'ai-draft'" in issue[2] for issue in issues),
                    issues,
                )

    def test_reviewed_status_with_updated_provenance_is_clean(self):
        issues = MODULE.governance_issues(
            "Test", item(reviewerStatus="Internally Reviewed", contentSource="clinician-reviewed")
        )
        self.assertFalse(any(issue[0] == "BLOCKER" for issue in issues), issues)


class ProvenanceReleaseTests(unittest.TestCase):
    def test_release_blocks_missing_content_source(self):
        bare = {
            "id": "x", "title": "X",
            "reviewerStatus": "Internally Reviewed",
            "references": ["Smith et al. 2024"],
        }
        issues = MODULE.release_readiness_issues([], [dict(bare, immediateMoves=["a"] * 3)], [])
        self.assertTrue(
            any(issue[0] == "BLOCKER" and "content provenance" in issue[2] for issue in issues),
            issues,
        )


class ShippedProvenanceTests(unittest.TestCase):
    def test_every_shipped_item_declares_valid_provenance(self):
        for path in (MODULE.PROCEDURES, MODULE.RESCUE_CARDS, MODULE.KITS):
            items = MODULE.load_json(path)
            self.assertIsNotNone(items, path)
            for entry in items:
                self.assertIn(
                    entry.get("contentSource"),
                    MODULE.CONTENT_SOURCES,
                    f"{path.name}: {entry.get('id')} has no valid contentSource",
                )

    def test_shipped_content_has_no_provenance_contradictions(self):
        for path in (MODULE.PROCEDURES, MODULE.RESCUE_CARDS, MODULE.KITS):
            for entry in MODULE.load_json(path):
                issues = MODULE.governance_issues(entry.get("id", "?"), entry)
                blockers = [issue for issue in issues if issue[0] == "BLOCKER"]
                self.assertEqual(blockers, [], f"{path.name}: {entry.get('id')}")


if __name__ == "__main__":
    unittest.main()
