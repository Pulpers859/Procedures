#!/usr/bin/env python3
"""Promote sign-offs exported from the app into the bundled content.

A review recorded in the app is local to one device. Without this it can never
become the content's actual status: a clinician can work through every item and
each page still reads "AI draft - not clinically reviewed", because nothing
carries the sign-off back to the repo.

Promotion updates reviewerStatus AND contentSource together. The validator
treats a clinical reviewerStatus sitting on 'ai-draft' provenance as a
contradiction, and it is right to: a sign-off that leaves the provenance
claiming the text is an unreviewed AI draft has recorded nothing.

Refusals, all deliberate:
  * only the "Reviewed" disposition promotes; "Needs Edits" and "Deferred" are
    explicitly not sign-offs
  * a review whose material fingerprint no longer matches the shipping content
    is refused, because it signed off text that has since changed
  * a review carrying no fingerprint is refused unless --allow-unfingerprinted
  * unknown ids are refused rather than silently skipped

Usage:
    python3 scripts/apply_local_reviews.py path/to/procedure-reviews-2026-07-28.json
    python3 scripts/apply_local_reviews.py reviews.json --dry-run
    python3 scripts/apply_local_reviews.py reviews.json --status "Externally Reviewed"

Always re-run `python3 scripts/validate_procedures.py` afterwards.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"
EXPORT_SCHEMA = "procedures.local-reviews.v1"

# Mirror of ContentFingerprint in Procedures/Models/ReviewerStatus.swift.
SEPARATOR = "\x1f"
# Record separator. The unit separator above stops collisions *within* a list;
# this keeps the boundary *between* lists significant, so a line moving from
# the end of one section to the start of the next changes the digest.
SECTION_SEPARATOR = "\x1e"

# Bumped whenever the set of hashed fields changes. A digest written under an
# older version answers a different question and must not be compared; see
# LocalReviewRecord.contentState in UserDataStore.swift.
FINGERPRINT_VERSION = 2

REVIEWED_DISPOSITION = "Reviewed"
DEFAULT_STATUS = "Internally Reviewed"
REVIEWED_STATUSES = {"Internally Reviewed", "Externally Reviewed", "Institution-Specific"}
PROMOTED_SOURCE = "clinician-reviewed"

# key prefix -> (filename, list of the material section fields, in Swift order)
KINDS = {
    "procedure": ("procedures.json", None),
    "rescue": ("rescue_cards.json", ["immediateMoves", "trigger", "avoid", "reassess"]),
    "kit": ("kits.json", ["inKit", "outsideKit", "commonlyForgotten", "patientSetup", "sterileSetup"]),
}

# Mirror of Procedure.materialSectionNames, in Swift order.
PROCEDURE_MATERIAL_SECTIONS = [
    "shiftMode", "contraindications", "equipment",
    "steps", "confirmation", "troubleshooting", "complications",
]


def fingerprint(parts):
    joined = SEPARATOR.join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def sectioned_fingerprint(sections):
    """Mirror of ContentFingerprint.make(sections:). `sections` is an ordered
    sequence of (name, lines)."""
    parts = []
    for name, lines in sections:
        parts.append(SECTION_SEPARATOR + name)
        parts.extend(lines)
    return fingerprint(parts)


def dose_string(value):
    """Mirror of Procedure.doseString: String(format: "%.4f", value)."""
    return f"{float(value):.4f}"


def procedure_fingerprint(item):
    sections = item.get("sections") or {}
    grouped = [(name, list(sections.get(name) or [])) for name in PROCEDURE_MATERIAL_SECTIONS]
    dosing = item.get("dosing")
    if dosing:
        dose_parts = []
        for agent in dosing.get("agents") or []:
            absolute = agent.get("absoluteMaxMg")
            ceiling = dose_string(absolute) if absolute is not None else "-"
            dose_parts.append(
                f"{agent.get('agent')}|{dose_string(agent.get('maxDoseMgPerKg'))}|{ceiling}"
            )
        dose_parts.append(dosing.get("cumulativeWarning", ""))
        grouped.append(("dosing", dose_parts))
    return sectioned_fingerprint(grouped)


def listed_fingerprint(item, fields):
    return sectioned_fingerprint([(field, list(item.get(field) or [])) for field in fields])


def current_fingerprint(kind, item):
    _, fields = KINDS[kind]
    if fields is None:
        return procedure_fingerprint(item)
    return listed_fingerprint(item, fields)


def load_export(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: could not read export {path}: {exc}")
    if not isinstance(payload, dict):
        sys.exit("error: export must be a JSON object")
    if "reviews" in payload:
        schema = payload.get("schema")
        if schema != EXPORT_SCHEMA:
            sys.exit(f"error: unsupported export schema {schema!r}; expected {EXPORT_SCHEMA!r}")
        return payload["reviews"]
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("export", type=Path, help="JSON file exported from the app")
    parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing.")
    parser.add_argument(
        "--status",
        default=DEFAULT_STATUS,
        choices=sorted(REVIEWED_STATUSES),
        help=f"reviewerStatus to promote to (default: {DEFAULT_STATUS}).",
    )
    parser.add_argument(
        "--allow-unfingerprinted",
        action="store_true",
        help="Promote reviews recorded before fingerprints existed. The content they signed off cannot be verified.",
    )
    args = parser.parse_args(argv)

    reviews = load_export(args.export)
    files = {}
    for kind, (filename, _) in KINDS.items():
        path = RESOURCES / filename
        files[kind] = (path, json.loads(path.read_text(encoding="utf-8")))

    applied, skipped, refused = [], [], []
    changed_kinds = set()

    for key, record in sorted(reviews.items()):
        kind, _, item_id = key.partition(":")
        if kind not in KINDS:
            refused.append(f"{key}: unknown record kind")
            continue
        if not isinstance(record, dict):
            refused.append(f"{key}: malformed record")
            continue

        disposition = record.get("disposition")
        if disposition != REVIEWED_DISPOSITION:
            skipped.append(f"{key}: disposition '{disposition}' is not a sign-off")
            continue

        _, items = files[kind]
        item = next((entry for entry in items if entry.get("id") == item_id), None)
        if item is None:
            refused.append(f"{key}: no such {kind} in {KINDS[kind][0]}")
            continue

        recorded = record.get("materialFingerprint")
        # `or 1`, not a .get default: a record can carry the key with a null
        # value, and both that and an absent key mean "written before
        # versioning". Mirrors `fingerprintVersion ?? 1` in Swift.
        recorded_version = record.get("fingerprintVersion") or 1
        if not recorded:
            if not args.allow_unfingerprinted:
                refused.append(f"{key}: review carries no fingerprint; rerun with --allow-unfingerprinted to accept it")
                continue
        elif recorded_version != FINGERPRINT_VERSION:
            # A digest over a different field set cannot be compared. Treating
            # it as a match would promote a sign-off that never covered the
            # sections since added; treating it as a mismatch would claim the
            # content changed when only the question did. Neither is true, so
            # this refuses and says why.
            refused.append(
                f"{key}: review was recorded against fingerprint v{recorded_version}, "
                f"but the material field set is now v{FINGERPRINT_VERSION}. Re-review it in "
                f"the app so the sign-off covers the sections that were added."
            )
            continue
        elif recorded != current_fingerprint(kind, item):
            refused.append(
                f"{key}: content changed since this review; re-review it in the app rather than promoting a stale sign-off"
            )
            continue

        already = item.get("reviewerStatus") == args.status and item.get("contentSource") == PROMOTED_SOURCE
        if already:
            skipped.append(f"{key}: already {args.status}")
            continue

        item["reviewerStatus"] = args.status
        # Provenance must move with the status or the validator flags the pair
        # as a contradiction - correctly, since a sign-off that leaves the text
        # marked an unreviewed AI draft has recorded nothing.
        item["contentSource"] = PROMOTED_SOURCE
        review_date = record.get("date")
        if review_date:
            item["lastReviewed"] = review_date
        applied.append(f"{key}: -> {args.status} ({PROMOTED_SOURCE})")
        changed_kinds.add(kind)

    for line in applied:
        print(f"promote  {line}")
    for line in skipped:
        print(f"skip     {line}")
    for line in refused:
        print(f"REFUSE   {line}")

    if not applied:
        print("\nNothing to promote.")
        return 1 if refused else 0

    if args.dry_run:
        print(f"\nDry run: {len(applied)} sign-off(s) would be promoted. Nothing written.")
        return 0

    for kind in sorted(changed_kinds):
        path, items = files[kind]
        # Match the shipped formatting exactly: 2-space indent, ASCII-escaped,
        # no trailing newline. ensure_ascii=False rewrites every line holding a
        # dash and buries the real change.
        path.write_text(json.dumps(items, indent=2, ensure_ascii=True), encoding="utf-8")
        print(f"\nUpdated {path.name}.")

    print("Now run: python3 scripts/validate_procedures.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
