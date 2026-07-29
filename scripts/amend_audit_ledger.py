#!/usr/bin/env python3
"""Record that a drifted record was re-screened, so the gate can go green.

There is deliberately no command that turns the release gate green on its own.
This one requires a person to supply, for each record, the five things
RELEASE_CONSTITUTION.md already demands of a waiver — owner, rationale,
affected commit, expiry, follow-up — and it refuses without them. The point is
not that a determined owner cannot wave a record through; in a single-maintainer
repo nothing can prevent that. The point is that waving a record through has to
be typed out, per record, with a name and a reason and an end date attached, so
it is a deliberate act recorded in git rather than a quiet regeneration.

The fingerprint is read from the current content, never supplied by hand, so an
amendment always attests to exactly what is shipping at the moment it is
written. Change the record again and the amendment stops applying — the gate
goes red and asks again, which is the correct behaviour, not a bug.

Usage:
    python3 scripts/amend_audit_ledger.py \\
        --record block_raptir --record anterior_nasal_packing \\
        --owner "Patrick" \\
        --rationale "Re-screened the dose ceiling against ASRA 2020; the audit
                     finding for this record is superseded by the correction." \\
        --commit fcd718f \\
        --expires 2026-10-31 \\
        --follow-up "docs/audits/procedure-verification/CLINICAL_OWNER_QUEUE.md#p1-dosing"
"""

import argparse
import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_fingerprint  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"
LEDGER = ROOT / "docs" / "audits" / "procedure-verification" / "AUDIT_LEDGER.json"

# Rationales that record nothing. A waiver whose reason is "fixed" leaves the
# next reader exactly as informed as no waiver at all.
EMPTY_RATIONALES = {
    "fixed", "n/a", "na", "none", "ok", "done", "updated", "no change",
    "not applicable", "re-screened", "reviewed", "tbd", "todo",
}
MINIMUM_RATIONALE_WORDS = 6


def load_records(corpus: str) -> dict:
    items = json.loads((RESOURCES / corpus).read_text(encoding="utf-8"))
    return {item["id"]: item for item in items}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--record", action="append", required=True, dest="records",
                        help="Record id to amend. Repeatable.")
    parser.add_argument("--corpus", default="procedures.json",
                        choices=["procedures.json", "rescue_cards.json", "kits.json"])
    parser.add_argument("--owner", required=True, help="Who adjudicated this.")
    parser.add_argument("--rationale", required=True,
                        help="What changed, what you checked, and why the release may proceed.")
    parser.add_argument("--commit", required=True, help="The commit that made the change.")
    parser.add_argument("--expires", required=True,
                        help="ISO date after which this waiver is a stop-ship condition.")
    parser.add_argument("--follow-up", required=True, dest="follow_up",
                        help="Where the outstanding work is tracked.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the amendments without writing them.")
    args = parser.parse_args(argv)

    rationale = " ".join(args.rationale.split())
    if rationale.strip().lower().rstrip(".") in EMPTY_RATIONALES:
        return fail(f"--rationale {rationale!r} records nothing. Say what changed and what you checked.")
    if len(rationale.split()) < MINIMUM_RATIONALE_WORDS:
        return fail(
            f"--rationale needs at least {MINIMUM_RATIONALE_WORDS} words; "
            "it is the only part of this waiver a future reader can learn from."
        )

    try:
        expires = datetime.date.fromisoformat(args.expires)
    except ValueError:
        return fail(f"--expires {args.expires!r} is not an ISO date (YYYY-MM-DD).")
    if expires <= datetime.date.today():
        return fail(f"--expires {args.expires} is not in the future.")

    if not LEDGER.is_file():
        return fail(f"{LEDGER.name} is missing; run generate_audit_ledger.py first.")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    corpus_entry = (ledger.get("corpora") or {}).get(args.corpus)
    if corpus_entry is None:
        return fail(f"{LEDGER.name} has no baseline for {args.corpus}.")

    records = load_records(args.corpus)
    baseline = corpus_entry.get("records") or {}
    amendments = ledger.setdefault("amendments", [])

    written = []
    for record_id in args.records:
        item = records.get(record_id)
        if item is None:
            return fail(f"{record_id} is not in {args.corpus}.")
        current = audit_fingerprint.audit_fingerprint(item)
        if baseline.get(record_id) == current:
            return fail(
                f"{record_id} still matches its audited baseline. There is nothing "
                "to amend, and recording a waiver for it would be noise."
            )
        amendment = {
            "corpus": args.corpus,
            "recordId": record_id,
            "auditFingerprint": current,
            "owner": args.owner,
            "rationale": rationale,
            "commit": args.commit,
            "expires": args.expires,
            "followUp": args.follow_up,
            "recordedAt": datetime.date.today().isoformat(),
        }
        # Supersede rather than accumulate: an older amendment for the same
        # record names a fingerprint that no longer applies anyway.
        amendments[:] = [
            existing
            for existing in amendments
            if not (
                existing.get("corpus") == args.corpus
                and existing.get("recordId") == record_id
            )
        ]
        amendments.append(amendment)
        written.append(record_id)

    amendments.sort(key=lambda value: (value.get("corpus", ""), value.get("recordId", "")))
    serialized = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"
    if args.dry_run:
        print(serialized)
        return 0

    LEDGER.write_text(serialized, encoding="utf-8")
    print(f"Recorded {len(written)} amendment(s) in {LEDGER.relative_to(ROOT).as_posix()}:")
    for record_id in written:
        print(f"  {args.corpus} {record_id} (expires {args.expires})")
    print("\nRun scripts/verify_procedure_audit.py to confirm the gate accepts them.")
    return 0


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
