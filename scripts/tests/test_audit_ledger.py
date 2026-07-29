"""The audit ledger's baselines must stay derivable from the audited bytes.

These run against the real repository on purpose. The failure this guards is
not a logic error in a fixture — it is someone (or some agent) editing a
baseline fingerprint in AUDIT_LEDGER.json so a red gate goes green, which is
the exact move AUDIT_PROTOCOL.md forbids and which the previous whole-file
constants made the only available remedy.
"""

import importlib.util
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
LEDGER = ROOT / "docs" / "audits" / "procedure-verification" / "AUDIT_LEDGER.json"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FINGERPRINT = load("audit_fingerprint")


def have_audited_blobs() -> bool:
    generate = load("generate_audit_ledger")
    for blob, _ in generate.AUDITED_BLOBS.values():
        result = subprocess.run(
            ["git", "cat-file", "-e", blob], cwd=ROOT, capture_output=True
        )
        if result.returncode != 0:
            return False
    return True


class AuditFingerprintScopeTests(unittest.TestCase):
    def test_bookkeeping_changes_do_not_move_the_fingerprint(self):
        record = {"id": "x", "sections": {"steps": ["cut"]}}
        stamped = dict(record, contentSource="ai-draft", reviewerStatus="Needs Clinical Review",
                       lastReviewed="2026-07-29", version="9.9.9")
        self.assertEqual(
            FINGERPRINT.audit_fingerprint(record),
            FINGERPRINT.audit_fingerprint(stamped),
        )

    def test_references_are_in_scope(self):
        """The blind spot that made the material fingerprint the wrong tool."""
        before = {"id": "x", "sections": {"references": ["Standard literature."]}}
        after = {"id": "x", "sections": {"references": ["Zahed R, et al. Am J Emerg Med. 2013."]}}
        self.assertNotEqual(
            FINGERPRINT.audit_fingerprint(before),
            FINGERPRINT.audit_fingerprint(after),
        )

    def test_an_unknown_new_field_counts_as_content(self):
        """Denylist polarity: a field nobody classified must not be ignored."""
        before = {"id": "x"}
        after = {"id": "x", "someFieldAddedNextYear": ["clinically important"]}
        self.assertNotEqual(
            FINGERPRINT.audit_fingerprint(before),
            FINGERPRINT.audit_fingerprint(after),
        )

    def test_key_order_does_not_matter_but_value_order_does(self):
        self.assertEqual(
            FINGERPRINT.audit_fingerprint({"id": "x", "title": "T"}),
            FINGERPRINT.audit_fingerprint({"title": "T", "id": "x"}),
        )
        self.assertNotEqual(
            FINGERPRINT.audit_fingerprint({"id": "x", "sections": {"steps": ["a", "b"]}}),
            FINGERPRINT.audit_fingerprint({"id": "x", "sections": {"steps": ["b", "a"]}}),
        )


@unittest.skipUnless(have_audited_blobs(), "audited blobs absent (shallow clone)")
class ShippedLedgerTests(unittest.TestCase):
    def test_committed_ledger_matches_the_audited_bytes(self):
        result = subprocess.run(
            ["python3", str(SCRIPTS / "generate_audit_ledger.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_shipped_procedure_has_a_baseline_entry(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        baseline = ledger["corpora"]["procedures.json"]["records"]
        shipped = {
            item["id"]
            for item in json.loads(
                (ROOT / "Procedures" / "Resources" / "procedures.json").read_text(encoding="utf-8")
            )
        }
        self.assertEqual(shipped - set(baseline), set())

    def test_the_rescue_baseline_never_claims_to_be_audited(self):
        """Its audited bytes are unrecoverable; nothing may imply otherwise."""
        corpus = json.loads(LEDGER.read_text(encoding="utf-8"))["corpora"]["rescue_cards.json"]
        self.assertEqual(corpus["baselineOrigin"], "post-audit")
        self.assertTrue(corpus["auditedBaselineUnrecoverable"])
        self.assertNotIn("auditedFileSha256", corpus)
        self.assertEqual(corpus["screening"], "none")


if __name__ == "__main__":
    unittest.main()
