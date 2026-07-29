import contextlib
import hashlib
import importlib.util
import io
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


# Default to a non-blocking disposition. `MAJOR` here would trip the
# unresolved-findings check in every fixture and drown the thing under test.
CLEAN = "NO MATERIAL DISCREPANCY IDENTIFIED"


def report_text(fingerprint, repeated=False, disposition=CLEAN):
    section = f"""## `test_procedure` - Test Procedure

**Screening disposition: {disposition}**

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


def write_ledger(audit_root, procedures, *, baseline=None, amendments=None, audited_sha256=None):
    """Write a ledger whose procedure baseline matches `procedures` unless overridden."""
    items = json.loads(procedures.read_text())
    records = baseline
    if records is None:
        records = {
            item["id"]: MODULE.audit_fingerprint.audit_fingerprint(item)
            for item in items
        }
    ledger = {
        "schema": "procedures.audit-ledger.v1",
        "fingerprintAlgorithm": "audit/v1",
        "fingerprintVersion": MODULE.audit_fingerprint.AUDIT_FINGERPRINT_VERSION,
        "corpora": {
            "procedures.json": {
                "baselineOrigin": "audited",
                "auditedFileSha256": audited_sha256
                or hashlib.sha256(procedures.read_bytes()).hexdigest(),
                "screening": "per-record",
                "records": records,
            },
            "rescue_cards.json": {
                "baselineOrigin": "post-audit",
                "screening": "none",
                "records": {},
            },
            "kits.json": {
                "baselineOrigin": "audited",
                "screening": "none",
                "records": {},
            },
        },
        "amendments": amendments or [],
    }
    path = audit_root / "AUDIT_LEDGER.json"
    path.write_text(json.dumps(ledger, indent=2))
    return path


def audit_patch(procedures, audit_root, expected_fingerprint, reports, ledger_path=None):
    rescue_cards = procedures.parent / "rescue_cards.json"
    kits = procedures.parent / "kits.json"
    rescue_cards.write_text("[]")
    kits.write_text("[]")
    if ledger_path is None:
        ledger_path = write_ledger(audit_root, procedures)
    audited = json.loads(ledger_path.read_text())["corpora"]["procedures.json"][
        "auditedFileSha256"
    ]
    (audit_root / "AUDIT_PROTOCOL.md").write_text(
        f"Procedures: {audited}\nRescue: {MODULE.UNRECOVERABLE_RESCUE_SHA256}\n"
    )
    return mock.patch.multiple(
        MODULE,
        PROCEDURES=procedures,
        RESCUE_CARDS=rescue_cards,
        KITS=kits,
        AUDIT_ROOT=audit_root,
        LEDGER=ledger_path,
        EXPECTED_SHA256=expected_fingerprint,
        REPORTS=reports,
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
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
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
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
                issues = MODULE.audit_issues()
            self.assertTrue(any("more than once" in issue for issue in issues))

    def drift_fixture(self, directory, *, baseline=None, amendments=None, content=None):
        """A one-procedure audit whose ledger baseline can be made to disagree."""
        root = Path(directory)
        procedures = root / "procedures.json"
        audit_root = root / "audit"
        audit_root.mkdir()
        procedures.write_text(json.dumps(content or [{"id": "test_procedure", "title": "Test"}]))
        fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
        (audit_root / "report.md").write_text(report_text(fingerprint))
        ledger = write_ledger(
            audit_root, procedures, baseline=baseline, amendments=amendments
        )
        return procedures, audit_root, fingerprint, ledger

    def test_a_drifted_record_is_named_and_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(
                any("test_procedure drifted from the audited baseline" in i for i in issues),
                issues,
            )

    def test_an_unrelated_record_does_not_fail_when_another_drifts(self):
        """The defect that motivated this design: one edit invalidated all 55."""
        with tempfile.TemporaryDirectory() as directory:
            content = [{"id": "drifted", "title": "A"}, {"id": "stable", "title": "B"}]
            procedures, audit_root, fingerprint, _ = self.drift_fixture(
                directory, content=content
            )
            items = {i["id"]: i for i in content}
            baseline = {
                "drifted": "0" * 64,
                "stable": MODULE.audit_fingerprint.audit_fingerprint(items["stable"]),
            }
            ledger = write_ledger(audit_root, procedures, baseline=baseline)
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            drift = [i for i in issues if "drifted from the audited baseline" in i]
            self.assertEqual(len(drift), 1, drift)
            self.assertIn("drifted", drift[0])
            self.assertNotIn("stable", drift[0])

    def test_metadata_only_change_does_not_invalidate_the_audit(self):
        """`contentSource` was added to all 55 records and nuked the whole gate."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audited = {"id": "test_procedure", "title": "Test", "sections": {"steps": ["cut"]}}
            shipping = dict(
                audited,
                contentSource="ai-draft",
                reviewerStatus="Needs Clinical Review",
                lastReviewed="2026-07-29",
                version="0.2.0",
            )
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([shipping]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            ledger = write_ledger(
                audit_root,
                procedures,
                baseline={
                    "test_procedure": MODULE.audit_fingerprint.audit_fingerprint(audited)
                },
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertEqual(issues, [])

    def test_a_valid_amendment_clears_the_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = {"id": "test_procedure", "title": "Test"}
            current = MODULE.audit_fingerprint.audit_fingerprint(item)
            amendment = {
                "corpus": "procedures.json",
                "recordId": "test_procedure",
                "auditFingerprint": current,
                "owner": "Release owner",
                "rationale": "Re-screened after the dose correction.",
                "commit": "abc1234",
                "expires": "2999-01-01",
                "followUp": "docs/audits/...",
            }
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}, amendments=[amendment]
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertEqual(issues, [])

    def test_an_expired_amendment_is_stop_ship(self):
        with tempfile.TemporaryDirectory() as directory:
            item = {"id": "test_procedure", "title": "Test"}
            amendment = {
                "corpus": "procedures.json",
                "recordId": "test_procedure",
                "auditFingerprint": MODULE.audit_fingerprint.audit_fingerprint(item),
                "owner": "Release owner",
                "rationale": "Re-screened.",
                "commit": "abc1234",
                "expires": "2000-01-01",
                "followUp": "docs/audits/...",
            }
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}, amendments=[amendment]
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(any("expired on 2000-01-01" in i for i in issues), issues)
            self.assertTrue(any("drifted from the audited baseline" in i for i in issues), issues)

    def test_an_amendment_missing_waiver_fields_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            item = {"id": "test_procedure", "title": "Test"}
            amendment = {
                "corpus": "procedures.json",
                "recordId": "test_procedure",
                "auditFingerprint": MODULE.audit_fingerprint.audit_fingerprint(item),
                "owner": "",
                "rationale": "   ",
                "commit": "abc1234",
                "expires": "2999-01-01",
            }
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}, amendments=[amendment]
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            missing = [i for i in issues if "missing required waiver fields" in i]
            self.assertEqual(len(missing), 1, issues)
            for field in ("owner", "rationale", "followUp"):
                self.assertIn(field, missing[0])

    def test_an_amendment_is_void_once_the_content_changes_again(self):
        with tempfile.TemporaryDirectory() as directory:
            amendment = {
                "corpus": "procedures.json",
                "recordId": "test_procedure",
                "auditFingerprint": "1" * 64,
                "owner": "Release owner",
                "rationale": "Re-screened at an older revision.",
                "commit": "abc1234",
                "expires": "2999-01-01",
                "followUp": "docs/audits/...",
            }
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}, amendments=[amendment]
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(
                any("changed again after it was written" in i for i in issues), issues
            )

    def test_a_record_added_after_the_audit_fails_as_unscreened(self):
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={}
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(
                any("not in the audited baseline" in i for i in issues), issues
            )

    def test_a_removed_audited_record_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64, "deleted": "1" * 64}
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(
                any("deleted was audited but is no longer in the corpus" in i for i in issues),
                issues,
            )

    def test_a_stale_fingerprint_version_refuses_to_compare(self):
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(directory)
            payload = json.loads(ledger.read_text())
            payload["fingerprintVersion"] = MODULE.audit_fingerprint.AUDIT_FINGERPRINT_VERSION - 1
            ledger.write_text(json.dumps(payload))
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(any("must be re-derived" in i for i in issues), issues)

    def test_a_missing_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(directory)
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                ledger.unlink()
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(any("missing audit ledger" in i for i in issues), issues)

    def test_unscreened_corpus_drift_is_reported_but_not_blocking(self):
        """Kits and rescue cards have no per-record evidence to invalidate."""
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(directory)
            payload = json.loads(ledger.read_text())
            payload["corpora"]["kits.json"]["records"] = {"kit_ghost": "0" * 64}
            ledger.write_text(json.dumps(payload))
            notices = []
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                issues = MODULE.audit_issues(require_synthesis=False, notices=notices)
            self.assertEqual(issues, [])
            self.assertTrue(any("kit_ghost" in n for n in notices), notices)

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
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
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

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
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

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
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
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [wrong.md](wrong.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
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
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            )
            misleading_queue = queue_text(fingerprint).replace(
                "[Evidence](report.md)",
                "[Evidence](wrong-target?contains=report.md)",
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(misleading_queue)

            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
                issues = MODULE.audit_issues()
            self.assertTrue(any("missing evidence link to report.md" in issue for issue in issues))

    def test_open_release_blocking_findings_prevent_a_pass(self):
        """The gate used to print "Verified" over 55 open STOP-SHIP findings."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(
                report_text(fingerprint, disposition="STOP-SHIP")
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
                issues = MODULE.audit_issues(require_synthesis=False)
            self.assertTrue(
                any("unresolved release-blocking screening disposition" in i for i in issues),
                issues,
            )
            self.assertTrue(any("1 STOP-SHIP" in i for i in issues), issues)

    def test_the_index_generator_is_not_blocked_by_drift(self):
        """Regenerating a derived view must not require silencing the gate."""
        with tempfile.TemporaryDirectory() as directory:
            procedures, audit_root, fingerprint, ledger = self.drift_fixture(
                directory, baseline={"test_procedure": "0" * 64}
            )
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"], ledger):
                blocked = MODULE.audit_issues(require_synthesis=False)
                unblocked = MODULE.audit_issues(
                    require_synthesis=False, require_current_corpus=False
                )
            self.assertTrue(any("drifted" in i for i in blocked), blocked)
            self.assertEqual(unblocked, [])

    def test_a_duplicate_coverage_row_still_fails(self):
        """The exactly-one-row invariant must survive being scoped to rows."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            row = "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            (audit_root / "AUDIT_INDEX.md").write_text(row + row)
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
                issues = MODULE.audit_issues()
            self.assertTrue(any("exactly one coverage row" in i for i in issues), issues)

    def test_naming_a_record_outside_the_table_is_allowed(self):
        """The integrity hold names drifted records; that must not trip it."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            procedures = root / "procedures.json"
            audit_root = root / "audit"
            audit_root.mkdir()
            procedures.write_text(json.dumps([{"id": "test_procedure", "title": "Test"}]))
            fingerprint = hashlib.sha256(procedures.read_bytes()).hexdigest()
            (audit_root / "report.md").write_text(report_text(fingerprint))
            (audit_root / "AUDIT_INDEX.md").write_text(
                "> **Integrity hold:** `test_procedure` has changed.\n\n"
                "| Test | `test_procedure` - Test | `NO MATERIAL DISCREPANCY IDENTIFIED` | [report.md](report.md) |\n"
            )
            (audit_root / "CLINICAL_OWNER_QUEUE.md").write_text(queue_text(fingerprint))
            with audit_patch(procedures, audit_root, fingerprint, ["report.md"]):
                issues = MODULE.audit_issues()
            self.assertEqual(issues, [])


class FailureOutputTests(unittest.TestCase):
    """What the CI log tells a reader to do must match what went wrong.

    The remedy for drift is an amendment. There is no amendment for an open
    STOP-SHIP, so printing the amendment instructions under one sends the
    reader to the wrong tool.
    """

    def run_main(self, issues):
        with mock.patch.object(MODULE, "audit_issues", lambda **_: list(issues)):
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                code = MODULE.main()
        return code, captured.getvalue()

    def test_drift_prints_the_amendment_remedy(self):
        code, output = self.run_main(
            [f"procedures.json: block_raptir {MODULE.DRIFT_PHRASE} (aaa -> bbb); x"]
        )
        self.assertEqual(code, 1)
        self.assertIn("recording an amendment", output)

    def test_open_findings_alone_do_not_print_the_amendment_remedy(self):
        code, output = self.run_main(
            ["55 of 55 procedures carry an unresolved release-blocking "
             "screening disposition (28 STOP-SHIP, 27 MAJOR)."]
        )
        self.assertEqual(code, 1)
        self.assertIn("unresolved release-blocking", output)
        self.assertNotIn("amendment", output)


if __name__ == "__main__":
    unittest.main()
