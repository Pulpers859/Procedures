import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "verify_procedure_audit.py"
SPEC = importlib.util.spec_from_file_location("verify_procedure_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def report_text(fingerprint, repeated=False):
    section = """## `test_procedure` - Test Procedure

**Screening disposition: MAJOR**

Equipment and instruments were assessed.
Reviewer question: what should the clinical owner approve?
Source: [Authoritative source](https://www.cdc.gov/standard)
`reviewerStatus` remains unchanged.
"""
    return (
        f"Corpus fingerprint: `{fingerprint}`\n"
        "Boundary: AI-assisted discrepancy screen only; not clinical approval.\n\n"
        f"{section}{section if repeated else ''}"
    )


def queue_text(fingerprint):
    return (
        f"Corpus: {fingerprint}.\n"
        "[Evidence](report.md)\n"
        "## P0: Direct harm\n## P1: Dosing\n## P2: Scope\n## P3: Control\n"
        "## Recommended Human Review Order\n"
        "No `reviewerStatus` should change.\n"
    )


class ProcedureAuditVerifierTests(unittest.TestCase):
    def test_complete_single_procedure_report_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Category | Procedure | Disposition | Report |\n"
                "|---|---|---|---|\n"
                "| Test | `test_procedure` - Test | `MAJOR` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                self.assertEqual(MODULE.audit_issues(), [])

    def test_duplicate_procedure_section_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint, repeated=True))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `MAJOR` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any("more than once" in issue for issue in issues))

    def test_changed_corpus_hash_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            actual = hashlib.sha256(procedures.read_bytes()).hexdigest()
            expected = "0" * 64
            (audit_root / "report.md").write_text(report_text(expected))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `MAJOR` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(expected))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=expected,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any(actual in issue for issue in issues))

    def test_contradictory_incomplete_report_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(
                f"Corpus fingerprint: {fingerprint}\n"
                "## test_procedure - Test\n"
                "Screening disposition: TBD\n"
                "A random MAJOR word and https://example.org/link.\n"
                "This is clinical approval. reviewerStatus is not unchanged.\n"
            )
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `MAJOR` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any("disposition line" in issue for issue in issues))
            self.assertTrue(any("equipment" in issue for issue in issues))
            self.assertTrue(any("reviewer question" in issue for issue in issues))
            self.assertTrue(any("authoritative" in issue for issue in issues))
            self.assertTrue(any("approval claim" in issue for issue in issues))
            self.assertTrue(any("preserve reviewerStatus" in issue for issue in issues))

    def test_report_validation_can_run_before_synthesis_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                self.assertEqual(MODULE.audit_issues(require_synthesis=False), [])

    def test_index_disposition_must_match_the_exact_procedure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `STOP-SHIP` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any("does not match its lane report" in issue for issue in issues))

    def test_index_report_link_must_match_the_exact_lane(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `MAJOR` | [wrong.md](wrong.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any("does not match its lane report" in issue for issue in issues))

    def test_queue_lane_link_target_must_be_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "| Test | `test_procedure` - Test | `MAJOR` | [report.md](report.md) |\n"
            )
            misleading_queue = queue_text(fingerprint).replace(
                "[Evidence](report.md)",
                "[Evidence](wrong-target?contains=report.md)",
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(misleading_queue)

            with mock.patch.multiple(
                MODULE,
                PROCEDURES=procedures,
                AUDIT_ROOT=audit_root,
                EXPECTED_SHA256=fingerprint,
                REPORTS=["report.md"],
            ):
                issues = MODULE.audit_issues()
            self.assertTrue(any("missing evidence link to report.md" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
