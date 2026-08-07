#!/usr/bin/env python3
"""The orientation an agent would otherwise re-derive, printed at SessionStart.

SessionStart hook stdout is added to the session's context. It is the only
channel in this repo that reaches an agent without the agent choosing to look,
and until now it carried one line about the branch policy.

That matters because this repo has eleven mechanisms that tell an agent it is
wrong and, before this file, none that told it what is true. The measured cost:
688 throwaway python one-liners across the session transcripts - 744 KB of
disposable code - and 65% of them were opening procedures.json and filtering
it. Files like Procedure.swift and ReviewCenterView.swift were re-read 15 and
16 times. Every one of those is a fact being rediscovered rather than handed
over.

Everything below is computed from the repo, never hardcoded, so it cannot drift
into telling a future session something that stopped being true. Keep it under
about twenty lines: this is paid on every session, and a brief nobody finishes
reading is the problem it was written to solve.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = []
    try:
        procedures = json.loads(
            (ROOT / "Procedures" / "Resources" / "procedures.json").read_text(encoding="utf-8"))
    except Exception:
        # Never let orientation break a session. Silence beats a traceback in
        # the first thing the agent reads.
        return 0

    status = Counter(p.get("reviewerStatus") or "Needs Clinical Review" for p in procedures)
    reviewed = sum(n for s, n in status.items() if s not in ("Needs Clinical Review", "Draft"))

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import apply_local_reviews as review
        version = review.FINGERPRINT_VERSION
        material = ", ".join(review.PROCEDURE_MATERIAL_SECTIONS)
    except Exception:
        version, material = "?", "?"

    try:
        head = subprocess.check_output(
            ["git", "log", "-1", "--format=%h %s"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
        # This repo writes long commit subjects; the brief only needs enough to
        # recognise where HEAD is.
        head = head[:60] + ("..." if len(head) > 60 else "")
    except Exception:
        head = "?"

    out.append(f"Content: {len(procedures)} procedures, {reviewed} clinically reviewed. HEAD {head}")
    out.append(f"Do NOT read procedures.json whole (~146k tokens). Query it:")
    out.append(f"  python3 scripts/pq.py ls|show|sections|grep|fp|diff|stats   (--kind rescue|kit, -h for more)")
    out.append(f"  e.g. pq show cricothyrotomy steps   |   pq grep bougie   |   pq fp fascia_iliaca_block")
    out.append(f"Sign-off fingerprint is v{version}. Material sections (editing one revokes a sign-off):")
    out.append(f"  {material}   plus majorBlockMonitoring and the dosing blocks. Tags are NOT hashed.")
    out.append(f"Reviewed edits are final - a line the reader removed stays removed. When a guard")
    out.append(f"  disagrees with a reviewed edit, the guard is what is wrong. See CLAUDE.md.")
    out.append(f"Round-trip order: apply_local_edits.py BEFORE apply_local_reviews.py, then validate.")
    out.append(f"Gate before pushing: validate_procedures.py, check_search_ranking.py,")
    out.append(f"  check_review_state_sources.py, python3 -m pytest scripts/tests -q")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
