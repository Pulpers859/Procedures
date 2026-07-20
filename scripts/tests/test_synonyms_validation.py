"""Negative controls for the synonym-map validation rules, plus an assertion
that the shipped synonyms.json passes them."""
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_procedures.py"
SPEC = importlib.util.spec_from_file_location("validate_procedures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SynonymMapValidationTests(unittest.TestCase):
    def test_well_formed_map_is_clean_of_blockers(self):
        issues = MODULE.synonym_map_issues({"cric": ["cricothyrotomy", "airway"]})
        # The bundling check may warn/block on fixture data only if the real
        # project file omits the resource; structural issues must be absent.
        structural = [issue for issue in issues if "phase" not in issue[2]]
        self.assertEqual(structural, [])

    def test_empty_or_non_object_map_is_a_blocker(self):
        for bad in ({}, [], "map", None):
            with self.subTest(map=bad):
                issues = MODULE.synonym_map_issues(bad)
                self.assertTrue(any(issue[0] == "BLOCKER" for issue in issues))

    def test_uppercase_or_whitespace_key_is_a_blocker(self):
        for key in ("Cric", "chest tube", ""):
            with self.subTest(key=key):
                issues = MODULE.synonym_map_issues({key: ["airway"]})
                self.assertTrue(any(issue[0] == "BLOCKER" and "lowercase" in issue[2] for issue in issues))

    def test_empty_or_uppercase_terms_are_blockers(self):
        for terms in ([], ["Airway"], [""], [42]):
            with self.subTest(terms=terms):
                issues = MODULE.synonym_map_issues({"cric": terms})
                self.assertTrue(any(issue[0] == "BLOCKER" for issue in issues))

    def test_self_reference_warns(self):
        issues = MODULE.synonym_map_issues({"cric": ["cric", "airway"]})
        self.assertTrue(any(issue[0] == "WARNING" and "itself" in issue[2] for issue in issues))

    def test_shipped_synonym_map_is_valid_and_bundled(self):
        synonyms = MODULE.load_json(MODULE.SYNONYMS)
        self.assertIsNotNone(synonyms)
        issues = MODULE.synonym_map_issues(synonyms)
        self.assertEqual([issue for issue in issues if issue[0] == "BLOCKER"], [])


if __name__ == "__main__":
    unittest.main()
