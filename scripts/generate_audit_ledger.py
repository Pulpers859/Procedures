#!/usr/bin/env python3
"""Derive the audit ledger's per-record baselines from the audited bytes.

The point of this script is what it *refuses* to do.

The previous guard pinned three whole-file SHA-256 constants. Nobody could
check where they came from, and the only way to make a red gate green was to
retype them — which is indistinguishable from rubber-stamping. So the baseline
here is never taken from the working tree. It is read out of the immutable git
blob that holds the bytes the audit actually screened, and the blob is verified
against the file hash recorded in AUDIT_PROTOCOL.md before a single fingerprint
is computed.

Consequences, all deliberate:

  * You cannot mint an "audited" baseline for content that was never audited.
    There is no code path from today's procedures.json to a baseline entry.
  * If the audited blob is missing from the clone, this refuses to run rather
    than falling back to something that would look the same and mean nothing.
  * rescue_cards.json has no audited blob anywhere in this repository's object
    store, so it gets no audited baseline. Its entry is written by hand as
    `post-audit` and says so. That is the honest record: the audit named a
    rescue-card fingerprint it never committed, and those bytes are gone.

Usage:
    python3 scripts/generate_audit_ledger.py            # write the ledger
    python3 scripts/generate_audit_ledger.py --check    # verify, write nothing
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_fingerprint  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"
LEDGER = ROOT / "docs" / "audits" / "procedure-verification" / "AUDIT_LEDGER.json"

SCHEMA = "procedures.audit-ledger.v1"
AUDIT_DATE = "2026-07-18"

# The audited bytes, addressed by the git object that still holds them.
#
# These blob IDs were found by hashing every object in the repository — all
# 669, reachable and unreachable — and matching against the SHA-256 values
# AUDIT_PROTOCOL.md records. procedures.json and kits.json were found.
# rescue_cards.json was not, in any object, which is consistent with the
# protocol's own admission that it fingerprinted an uncommitted working tree.
AUDITED_BLOBS = {
    "procedures.json": (
        "9d17679217cece51047c9d762c5602766aca25b2",
        "3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1",
    ),
    "kits.json": (
        "0976cd8c5caab57435e2ae03cafb296695093688",
        "c4c40950e457eabb3b8830f838140cd43ff1c610a6c84e8abd9358951d39e520",
    ),
}

# Screening coverage is not the same as being named in a fingerprint. The nine
# lane reports carry a per-procedure evidence section for each of the 55
# procedures. They carry none for any kit, and none for nine of the ten rescue
# cards. Recording that here stops the ledger from implying an audit that does
# not exist.
SCREENING = {
    "procedures.json": "per-record",
    "kits.json": "none",
    "rescue_cards.json": "none",
}

UNRECOVERABLE_NOTE = (
    "AUDIT_PROTOCOL.md records rescue-card SHA-256 "
    "4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14 for the "
    "audited snapshot. Those bytes are in no object in this repository, "
    "reachable or unreachable, because the audit fingerprinted an uncommitted "
    "working tree. The audited baseline is therefore unrecoverable and is not "
    "reconstructed here: seeding it from current content would assert that "
    "today's text is what was screened. This baseline was established after the "
    "audit, catches drift from this point forward, and attests nothing about "
    "the audit."
)

KITS_NOTE = (
    "The audited bytes are recoverable and no kit has drifted materially, so "
    "this baseline is real. No kit has a per-record evidence section in any "
    "lane report, so it records integrity only, not screening."
)

PROCEDURES_NOTE = (
    "Derived from the audited bytes. Each of the 55 records has a per-record "
    "evidence section in a lane report."
)


def audited_bytes(filename: str) -> bytes:
    blob, expected_sha256 = AUDITED_BLOBS[filename]
    try:
        data = subprocess.run(
            ["git", "cat-file", "blob", blob],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit(
            f"error: the audited blob {blob} for {filename} is not in this clone.\n"
            "       Fetch full history (actions/checkout fetch-depth: 0) and retry.\n"
            "       Refusing to fall back to working-tree content: a baseline taken\n"
            "       from today's file would look identical and attest nothing."
        ) from exc

    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise SystemExit(
            f"error: blob {blob} does not hash to the audited {filename} "
            f"fingerprint (expected {expected_sha256}, found {actual})"
        )
    return data


def record_fingerprints(payload: bytes) -> dict:
    items = json.loads(payload.decode("utf-8"))
    return {
        item["id"]: audit_fingerprint.audit_fingerprint(item)
        for item in sorted(items, key=lambda value: value["id"])
    }


def current_bytes(filename: str) -> bytes:
    return (RESOURCES / filename).read_bytes()


def build_ledger(previous: dict | None) -> dict:
    corpora = {}

    for filename in ("procedures.json", "kits.json"):
        blob, expected_sha256 = AUDITED_BLOBS[filename]
        payload = audited_bytes(filename)
        corpora[filename] = {
            "baselineOrigin": "audited",
            "auditDate": AUDIT_DATE,
            "auditedFileSha256": expected_sha256,
            "auditedGitBlob": blob,
            "screening": SCREENING[filename],
            "note": PROCEDURES_NOTE if filename == "procedures.json" else KITS_NOTE,
            "records": record_fingerprints(payload),
        }

    # No audited blob exists, so this baseline can only ever be post-audit. It
    # is seeded once from current content and then frozen: regenerating must
    # not silently re-seed it, or every future drift would erase itself.
    filename = "rescue_cards.json"
    established = None
    records = None
    if previous:
        existing = previous.get("corpora", {}).get(filename)
        if existing:
            established = existing.get("establishedAt")
            records = existing.get("records")
    if records is None:
        records = record_fingerprints(current_bytes(filename))
        established = established or "2026-07-29"
    corpora[filename] = {
        "baselineOrigin": "post-audit",
        "auditedBaselineUnrecoverable": True,
        "establishedAt": established,
        "screening": SCREENING[filename],
        "note": UNRECOVERABLE_NOTE,
        "records": records,
    }

    return {
        "schema": SCHEMA,
        "fingerprintAlgorithm": "audit/v1",
        "fingerprintVersion": audit_fingerprint.AUDIT_FINGERPRINT_VERSION,
        "corpora": corpora,
        # Amendments are written by a person, never by this script. See
        # verify_procedure_audit.py for the fields the release gate requires.
        "amendments": previous.get("amendments", []) if previous else [],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed ledger matches the audited bytes; write nothing.",
    )
    args = parser.parse_args(argv)

    previous = None
    if LEDGER.is_file():
        previous = json.loads(LEDGER.read_text(encoding="utf-8"))

    ledger = build_ledger(previous)
    serialized = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not LEDGER.is_file():
            print(f"error: {LEDGER.relative_to(ROOT).as_posix()} is missing")
            return 1
        if LEDGER.read_text(encoding="utf-8") != serialized:
            print(
                "error: the committed audit ledger does not match the audited bytes.\n"
                "       Someone edited a baseline by hand. Re-run without --check\n"
                "       and review the diff before committing."
            )
            return 1
        print("Audit ledger matches the audited bytes.")
        return 0

    LEDGER.write_text(serialized, encoding="utf-8")
    print(f"Wrote {LEDGER.relative_to(ROOT).as_posix()}")
    for filename, corpus in ledger["corpora"].items():
        print(
            f"  {filename}: {len(corpus['records'])} records, "
            f"baseline {corpus['baselineOrigin']}, screening {corpus['screening']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
