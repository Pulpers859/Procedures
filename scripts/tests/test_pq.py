#!/usr/bin/env python3
"""Guards on the content query tool and the SessionStart brief.

Both exist to stop agents rediscovering the same facts: 688 throwaway python
one-liners across this repo's session transcripts, 65% of them opening
procedures.json and filtering it. A query tool that silently stops working, or
a brief that silently stops printing, puts that cost straight back.

The brief is asserted for freshness rather than wording: it is generated from
the repo, and the failure that matters is it telling a future session something
that is no longer true.
"""
import importlib.util
import io
import json
import contextlib
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


pq = _load("pq")
PROCEDURES = json.loads(
    (ROOT / "Procedures" / "Resources" / "procedures.json").read_text(encoding="utf-8"))


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        pq.main(argv)
    return out.getvalue()


class QueryToolTests(unittest.TestCase):
    def test_ls_lists_every_record_once(self):
        lines = [l for l in run(["ls"]).strip().split("\n") if l]
        self.assertEqual(len(lines), len(PROCEDURES))

    def test_show_returns_only_the_requested_section(self):
        text = run(["show", "cricothyrotomy", "steps"])
        self.assertIn("## steps", text)
        self.assertNotIn("## equipment", text)

    def test_show_matches_the_file_exactly(self):
        """The whole point is trusting this instead of opening the JSON."""
        record = next(p for p in PROCEDURES if p["id"] == "cricothyrotomy")
        text = run(["show", "cricothyrotomy", "steps"])
        for line in record["sections"]["steps"]:
            self.assertIn(line, text)

    def test_sections_marks_exactly_the_material_ones(self):
        import apply_local_reviews as review
        text = run(["sections", "cricothyrotomy"])
        marked = {l.split()[0] for l in text.split("\n") if "*material" in l}
        record = next(p for p in PROCEDURES if p["id"] == "cricothyrotomy")
        expected = {s for s in review.PROCEDURE_MATERIAL_SECTIONS
                    if record["sections"].get(s)}
        self.assertEqual(marked, expected)

    def test_fp_agrees_with_the_promoter(self):
        """A fingerprint that disagreed with apply_local_reviews.py would be
        worse than no fingerprint at all."""
        import apply_local_reviews as review
        record = next(p for p in PROCEDURES if p["id"] == "cricothyrotomy")
        text = run(["fp", "cricothyrotomy"])
        self.assertIn(review.current_fingerprint("procedure", record), text)

    def test_unknown_id_exits_with_a_suggestion(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(err):
            run(["show", "cricothyro"])
        self.assertIn("cricothyrotomy", str(cm.exception))

    def test_every_kind_loads(self):
        for kind in ("procedure", "rescue", "kit"):
            with self.subTest(kind=kind):
                self.assertTrue(run(["--kind", kind, "stats"]).strip())

    def test_it_is_read_only(self):
        """Writing content goes through apply_local_edits.py, which produces a
        reviewable diff and reports the retrieval cost."""
        source = (ROOT / "scripts" / "pq.py").read_text(encoding="utf-8")
        self.assertNotIn("write_text", source)
        self.assertNotIn("json.dump", source)


class SessionBriefTests(unittest.TestCase):
    def setUp(self):
        self.text = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "session_brief.py")],
            capture_output=True, text=True, cwd=ROOT).stdout

    def test_the_counts_are_current(self):
        reviewed = sum(1 for p in PROCEDURES
                       if (p.get("reviewerStatus") or "Needs Clinical Review")
                       not in ("Needs Clinical Review", "Draft"))
        self.assertIn(f"{len(PROCEDURES)} procedures", self.text)
        self.assertIn(f"{reviewed} clinically reviewed", self.text)

    def test_it_names_the_current_fingerprint_version(self):
        import apply_local_reviews as review
        self.assertIn(f"v{review.FINGERPRINT_VERSION}", self.text)

    def test_it_lists_the_current_material_sections(self):
        import apply_local_reviews as review
        for section in review.PROCEDURE_MATERIAL_SECTIONS:
            self.assertIn(section, self.text)

    def test_it_points_at_a_query_tool_that_exists(self):
        self.assertIn("scripts/pq.py", self.text)
        self.assertTrue((ROOT / "scripts" / "pq.py").exists())

    def test_it_stays_short_enough_to_be_read(self):
        """Paid on every session. A brief nobody finishes is the problem it was
        written to solve."""
        self.assertLessEqual(len(self.text.strip().split("\n")), 16)
        self.assertLess(len(self.text), 1600)

    def test_the_session_start_hook_still_prints_it(self):
        hook = (ROOT / ".claude" / "hooks" / "install-main-only.sh").read_text(encoding="utf-8")
        self.assertIn("session_brief.py", hook)


if __name__ == "__main__":
    unittest.main()
