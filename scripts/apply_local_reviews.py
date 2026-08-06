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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomic_write import atomic_write_text

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
# v5: added majorBlockMonitoring (see procedure_fingerprint below).
# v6: added seniorPearls, now the single home for clinical rationale.
FINGERPRINT_VERSION = 6

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
    "seniorPearls",
]

# Which material sections each fingerprint version hashed, in Swift order.
#
# Kept so an older digest can be recomputed against *today's* content. Without
# it, growing the material set revokes every sign-off in the corpus wholesale:
# the v6 bump refused seven reviews with "re-review it in the app" when all
# seven had signed off text that has not changed by a character. That is hours
# of the reader's work discarded to cover one section they were never asked
# about.
#
# Recomputing answers the question a version number cannot: did the fields the
# sign-off *did* cover change, or only the fields it did not? Only the second
# case can be narrowed, and it is the common one.
SECTIONS_BY_VERSION = {
    4: PROCEDURE_MATERIAL_SECTIONS[:-1],
    5: PROCEDURE_MATERIAL_SECTIONS[:-1],
    6: PROCEDURE_MATERIAL_SECTIONS,
}
# majorBlockMonitoring entered the digest at v5.
MAJOR_BLOCK_FROM_VERSION = 5

# Fields inside the fingerprint that the in-app editor cannot reach and the
# edit export does not carry. A mismatch confined to one of these cannot be
# fixed by re-reviewing: the device is running a bundle that predates the
# field, and only a rebuild moves it. "Content changed since this review" sends
# the reader back into the app to redo a review that will be refused again for
# the same reason - which is exactly what happened to the fascia iliaca block
# after majorBlockMonitoring was set on it.
UNEDITABLE_MATERIAL_FIELDS = ("majorBlockMonitoring", "dosing", "medicationDosing")


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


def procedure_fingerprint(item, version=FINGERPRINT_VERSION):
    sections = item.get("sections") or {}
    grouped = [
        (name, list(sections.get(name) or []))
        for name in SECTIONS_BY_VERSION.get(version, PROCEDURE_MATERIAL_SECTIONS)
    ]
    # Mirror of Procedure.requiresMajorBlockMonitoring - a monitoring
    # requirement is safety content, not editorial metadata.
    if version >= MAJOR_BLOCK_FROM_VERSION:
        grouped.append(("majorBlockMonitoring", ["true" if item.get("majorBlockMonitoring") else "false"]))
    dosing = item.get("dosing")
    if dosing:
        dose_parts = []
        for agent in dosing.get("agents") or []:
            absolute = agent.get("absoluteMaxMg")
            ceiling = dose_string(absolute) if absolute is not None else "-"
            strengths = ",".join(
                dose_string(percent) for percent in agent.get("concentrationsPercent") or []
            )
            # "epi"/"plain" rather than the bool: Python prints True, Swift
            # prints true, and the digests would never match again.
            epinephrine = "epi" if agent.get("withEpinephrine") else "plain"
            dose_parts.append(
                f"{agent.get('agent')}|{epinephrine}"
                f"|{dose_string(agent.get('maxDoseMgPerKg'))}|{ceiling}|{strengths}"
                f"|{agent.get('note') or '-'}"
            )
        dose_parts.append(dosing.get("cumulativeWarning", ""))
        dose_parts.extend(dosing.get("caveats") or [])
        grouped.append(("dosing", dose_parts))
    medication_dosing = item.get("medicationDosing")
    if medication_dosing:
        med_parts = [medication_dosing.get("indication", "")]
        for med in medication_dosing.get("medications") or []:
            high = med.get("doseHighPerKg")
            high_text = dose_string(high) if high is not None else "-"
            med_parts.append(
                f"{med.get('medication')}|{med.get('role')}"
                f"|{dose_string(med.get('doseLowPerKg'))}|{high_text}"
                f"|{med.get('unit')}|{med.get('caution') or '-'}"
            )
        med_parts.extend(medication_dosing.get("selectionGuidance") or [])
        med_parts.append(medication_dosing.get("inductionRequirement", ""))
        grouped.append(("medicationDosing", med_parts))
    return sectioned_fingerprint(grouped)


def listed_fingerprint(item, fields):
    return sectioned_fingerprint([(field, list(item.get(field) or [])) for field in fields])


def current_fingerprint(kind, item, version=FINGERPRINT_VERSION):
    _, fields = KINDS[kind]
    if fields is None:
        return procedure_fingerprint(item, version)
    # Rescue cards and kits hash a fixed field list that no version has
    # changed, so their digest is version-independent.
    return listed_fingerprint(item, fields)


def added_since(version):
    """The material fields a sign-off at `version` was never asked about."""
    older = set(SECTIONS_BY_VERSION.get(version, ()))
    added = [name for name in PROCEDURE_MATERIAL_SECTIONS if name not in older]
    if version < MAJOR_BLOCK_FROM_VERSION:
        added.append("majorBlockMonitoring")
    return added


def uncovered_fields(item, version):
    """Fields added since `version` that actually carry something to review.

    A monitoring flag sitting at false asks the reader nothing, and an empty
    section has no text to sign. Listing either turns a precise instruction
    into a chore, so both are dropped here rather than in the message.
    """
    sections = item.get("sections") or {}
    live = []
    for name in added_since(version):
        if name == "majorBlockMonitoring":
            if item.get("majorBlockMonitoring"):
                live.append(name)
        elif sections.get(name):
            live.append(name)
    return live


def explain_version_gap(kind, item, recorded, version):
    """Say what an older digest still proves, instead of discarding it.

    Returns the refusal text. A sign-off is never promoted across a version
    boundary - the added fields genuinely have not been reviewed - but there is
    a wide gap between "re-review this procedure" and "re-review one section",
    and the reader is owed the second when it is true.
    """
    if version not in SECTIONS_BY_VERSION:
        return (
            f"recorded against fingerprint v{version}, which this tool cannot reconstruct "
            f"(known: v{min(SECTIONS_BY_VERSION)}-v{max(SECTIONS_BY_VERSION)}). Re-review it in the app."
        )
    if current_fingerprint(kind, item, version) != recorded:
        return (
            f"recorded against fingerprint v{version}, and the fields that version hashed have "
            f"changed since. This sign-off covers no part of the current text; re-review the procedure."
        )
    missing = uncovered_fields(item, version)
    if not missing:
        # Everything v{version} hashed is unchanged and the fields added since
        # carry nothing to read. Nothing was reviewed that is not still true,
        # and nothing new asks for a decision.
        return (
            f"recorded against fingerprint v{version}; every field it hashed is unchanged and the "
            f"fields added since are empty here. Re-open it in the app and sign off to re-stamp it at "
            f"v{FINGERPRINT_VERSION} - nothing to re-read."
        )
    return (
        f"recorded against fingerprint v{version}; every field it hashed is unchanged. Only "
        f"{', '.join(missing)} is outside it. Re-review {'that section' if len(missing) == 1 else 'those sections'} "
        f"in the app - the rest of this sign-off still holds."
    )


def explain_drift(kind, item, record, recorded):
    """Name what moved when a same-version digest does not match.

    Two mechanisms, in order of how much they can prove:

    1. The export carries per-section digests. Then the drifted fields are
       named exactly, and this needs no guessing at all. Nothing writes that
       map yet; the script accepts it so the app change is purely additive.
    2. Otherwise, probe the fields the editor cannot reach. A device running a
       bundle from before `majorBlockMonitoring` was set, or before a dosing
       block existed, produces a digest that will never match however many
       times the reader signs off again - and the refusal has to say so, or it
       sends them back to repeat work that cannot succeed.
    """
    recorded_sections = record.get("sectionFingerprints")
    if isinstance(recorded_sections, dict) and recorded_sections:
        sections = item.get("sections") or {}
        drifted = [
            name for name, digest in sorted(recorded_sections.items())
            if fingerprint(list(sections.get(name) or [])) != digest
        ]
        if drifted:
            return f"content changed since this review: {', '.join(drifted)}. Re-review those sections in the app."

    for field in UNEDITABLE_MATERIAL_FIELDS:
        probe = dict(item)
        if field == "majorBlockMonitoring":
            probe[field] = not item.get(field)
        elif field in probe:
            del probe[field]
        else:
            continue
        if current_fingerprint(kind, probe) == recorded:
            return (
                f"the only difference from the reviewed text is '{field}', which the in-app editor "
                f"cannot reach and the edit export does not carry. The device is running a bundle "
                f"from before it changed. Rebuild the app on this content, then sign off - "
                f"re-reviewing on the current build will be refused again."
            )

    return "content changed since this review; re-review it in the app rather than promoting a stale sign-off"


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
            # A digest over a different field set cannot be compared directly.
            # Treating it as a match would promote a sign-off that never
            # covered the sections since added; treating it as a flat mismatch
            # would claim the content changed when only the question did.
            # Neither is true, so this refuses and says which of the two it is.
            refused.append(f"{key}: {explain_version_gap(kind, item, recorded, recorded_version)}")
            continue
        elif recorded != current_fingerprint(kind, item):
            refused.append(f"{key}: {explain_drift(kind, item, record, recorded)}")
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
        atomic_write_text(path, json.dumps(items, indent=2, ensure_ascii=True))
        print(f"\nUpdated {path.name}.")

    print("Now run: python3 scripts/validate_procedures.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
