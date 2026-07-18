import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "verify_xcode_project.py"
SPEC = importlib.util.spec_from_file_location("verify_xcode_project", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def project_text(app_entry="", test_entry="", references=""):
    return f"""
    {references}
    {MODULE.APP_SOURCES_PHASE_ID} /* Sources */ = {{ files = (
        {app_entry}
    ); }};
    {MODULE.TEST_SOURCES_PHASE_ID} /* Sources */ = {{ files = (
        {test_entry}
    ); }};
    """


class ProjectMembershipTests(unittest.TestCase):
    def test_detects_missing_target_membership(self):
        source = MODULE.APP_ROOT / "MissingView.swift"
        text = project_text(references="path = MissingView.swift;")

        issues = MODULE.source_membership_issues(text, [source], [])

        self.assertTrue(any("missing target Sources membership" in issue for issue in issues))

    def test_detects_dangling_sources_membership(self):
        text = project_text(app_entry="/* DeletedView.swift in Sources */")

        issues = MODULE.source_membership_issues(text, [], [])

        self.assertIn("dangling app Sources membership: DeletedView.swift", issues)

    def test_accepts_reference_and_correct_phase_membership(self):
        source = MODULE.APP_ROOT / "Example.swift"
        text = project_text(
            app_entry="/* Example.swift in Sources */",
            references="path = Example.swift;",
        )

        self.assertEqual(MODULE.source_membership_issues(text, [source], []), [])

    def test_counts_declared_xctest_methods(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ExampleTests.swift"
            path.write_text(
                "func testOne() {}\n    func testTwo() throws {}\nfunc helper() {}\n",
                encoding="utf-8",
            )
            self.assertEqual(MODULE.declared_xctest_count([path]), 2)


if __name__ == "__main__":
    unittest.main()
