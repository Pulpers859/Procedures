import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_review_state_sources import check  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class CheckReviewStateSourcesTests(unittest.TestCase):
    """A guard is only worth having if it actually fires."""

    def setUp(self):
        import tempfile

        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        (self.root / "Views").mkdir()
        (self.root / "Components").mkdir()
        (self.root / "Models").mkdir()
        (self.root / "Data").mkdir()

    def tearDown(self):
        self._temp.cleanup()

    def write(self, relative, body):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    # The regression this exists to prevent.

    def test_a_new_view_reading_the_bundled_flag_fails(self):
        self.write(
            "Views/NewScreen.swift",
            "struct NewScreen: View {\n"
            "    var body: some View {\n"
            "        if !procedure.reviewer.isClinicallyReviewed { Text(\"Draft\") }\n"
            "    }\n"
            "}\n",
        )
        failures = check(self.root)
        self.assertTrue(any("isClinicallyReviewed" in f for f in failures), failures)

    def test_a_view_reaching_for_bundled_reviewer_fails(self):
        self.write(
            "Views/NewScreen.swift",
            "let status = procedure.reviewer\n",
        )
        failures = check(self.root)
        self.assertTrue(any("bundled `.reviewer`" in f for f in failures), failures)

    def test_governance_panel_may_pass_the_source_status_through(self):
        self.write(
            "Views/Detail.swift",
            "LocalReviewPanel(sourceStatus: procedure.reviewer, sourceOrigin: procedure.source)\n",
        )
        self.assertEqual(check(self.root), [])

    # The other way a screen goes stale: it never hears about the change.

    def test_unobserved_store_in_a_view_fails(self):
        self.write(
            "Views/NewScreen.swift",
            "struct NewScreen: View {\n"
            "    let userData: UserDataStore\n"
            "}\n",
        )
        failures = check(self.root)
        self.assertTrue(any("without an observation wrapper" in f for f in failures), failures)

    def test_observed_store_in_a_view_passes(self):
        self.write(
            "Views/NewScreen.swift",
            "struct NewScreen: View {\n"
            "    @EnvironmentObject private var userData: UserDataStore\n"
            "}\n",
        )
        self.assertEqual(check(self.root), [])

    def test_store_outside_the_ui_layer_is_not_policed(self):
        self.write("Data/SomeService.swift", "let userData: UserDataStore\n")
        self.assertEqual(check(self.root), [])

    # Allowlist and comment handling.

    def test_allowlisted_model_files_may_define_and_reconcile(self):
        self.write("Models/ReviewerStatus.swift", "var isClinicallyReviewed: Bool { true }\n")
        self.write("Models/ReviewState.swift", "if sourceStatus.isClinicallyReviewed { }\n")
        self.write("Models/ContentValidation.swift", "filter { !$0.reviewer.isClinicallyReviewed }\n")
        self.assertEqual(check(self.root), [])

    def test_prose_explaining_the_rule_does_not_trip_it(self):
        self.write(
            "Views/NewScreen.swift",
            "// Deliberately does not read isClinicallyReviewed or .reviewer here.\n"
            "let state = userData.reviewState(for: procedure)\n",
        )
        self.assertEqual(check(self.root), [])

    # And the real tree must stay clean.

    def test_the_shipping_app_passes(self):
        self.assertEqual(check(REPO_ROOT / "Procedures"), [])


if __name__ == "__main__":
    unittest.main()
