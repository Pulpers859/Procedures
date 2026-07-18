import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "verify_xcresult_summary.py"
SPEC = importlib.util.spec_from_file_location("verify_xcresult_summary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class XCResultSummaryTests(unittest.TestCase):
    def test_accepts_exact_top_level_count(self):
        self.assertEqual(MODULE.verify_test_count({"totalTestCount": 30}, 30), 30)

    def test_rejects_zero_tests(self):
        with self.assertRaisesRegex(ValueError, "reported 0"):
            MODULE.verify_test_count({"totalTestCount": 0}, 30)

    def test_rejects_truncated_test_suite(self):
        with self.assertRaisesRegex(ValueError, "reported 29"):
            MODULE.verify_test_count({"totalTestCount": 29}, 30)

    def test_rejects_nested_misleading_count(self):
        with self.assertRaisesRegex(ValueError, "no top-level"):
            MODULE.verify_test_count({"suite": {"totalTestCount": 30}}, 30)


if __name__ == "__main__":
    unittest.main()
