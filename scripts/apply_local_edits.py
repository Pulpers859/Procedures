#!/usr/bin/env python3
"""Apply edits exported from the app back into the bundled content.

The app cannot write to its own bundle, so corrections a clinician makes at the
bedside are stored as local overrides and exported as JSON. This merges that
export into `Procedures/Resources/procedures.json` so the change lands as a
reviewable git diff rather than a wholesale file replacement. Rescue card and
kit edits in the same export (its `cardEdits` key) go into
`rescue_cards.json` and `kits.json`.

Usage:
    python3 scripts/apply_local_edits.py path/to/procedure-edits-2026-07-27.json
    python3 scripts/apply_local_edits.py edits.json --dry-run
    python3 scripts/apply_local_edits.py edits.json --bump-version

Always re-run `python3 scripts/validate_procedures.py` afterwards: an edit can
empty a required section or drop the last reference, and only the validator
will catch that.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomic_write import atomic_write_text
import apply_local_reviews as review_fingerprint
import search_model

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"
RESCUE_CARDS = ROOT / "Procedures" / "Resources" / "rescue_cards.json"
KITS = ROOT / "Procedures" / "Resources" / "kits.json"
EXPORT_SCHEMA = "procedures.local-edits.v1"

# Mirror of EditableSection in Procedures/Data/ProcedureEditStore.swift. A key
# outside this set is refused rather than silently written into the content.
VALID_SECTIONS = {
    "shiftMode", "indications", "contraindications", "anatomy", "equipment",
    "positioning", "steps", "ultrasound", "confirmation", "troubleshooting",
    "complications", "aftercare", "documentation", "seniorPearls", "references",
}


# Mirror of CardField in Procedures/Data/ProcedureEditStore.swift.
CARD_FIELDS = {
    "rescue": {"trigger", "immediateMoves", "avoid", "reassess"},
    "kit": {"inKit", "outsideKit", "commonlyForgotten", "patientSetup", "sterileSetup", "backupEquipment"},
}


def load_card_edits(path: Path):
    """The export's `cardEdits` mapping ("rescue:<id>" / "kit:<id>"), or {}."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("cardEdits"), dict):
        return payload["cardEdits"]
    return {}


def write_kits_preserving_layout(raw: str, kits: list, touched) -> str:
    """kits.json is hand laid out (short lists inline, raw UTF-8). Rewrite only
    the touched lists so the diff shows the edit and nothing else."""
    by_id = {kit["id"]: kit for kit in kits}
    decoder = json.JSONDecoder()
    for kit_id, field in sorted(touched):
        start = raw.index(f'"id": "{kit_id}"')
        nxt = raw.find('"id": "', start + 10)
        match = re.compile(r'\n(\s*)"' + re.escape(field) + r'": ').search(raw, start)
        if not match or (nxt != -1 and match.start() > nxt):
            raise SystemExit(f"error: could not find {kit_id}.{field} in kits.json")
        indent = match.group(1)
        _, end = decoder.raw_decode(raw, match.end())
        items = ",\n".join(indent + "  " + json.dumps(x, ensure_ascii=False) for x in by_id[kit_id][field])
        raw = raw[:match.end()] + f"[\n{items}\n{indent}]" + raw[end:]
    if json.loads(raw) != kits:
        raise SystemExit("error: kits.json rewrite did not round-trip; nothing written")
    return raw


def apply_card_edits(card_edits, dry_run: bool):
    """Applies rescue card and kit edits. Returns the lines to report."""
    if not card_edits:
        return [], []
    rescue = json.loads(RESCUE_CARDS.read_text(encoding="utf-8"))
    kits_raw = KITS.read_text(encoding="utf-8")
    kits = json.loads(kits_raw)
    records = {"rescue": {c["id"]: c for c in rescue}, "kit": {k["id"]: k for k in kits}}
    applied, skipped, touched_kits = [], [], set()
    for key, entry in sorted(card_edits.items()):
        kind, _, card_id = key.partition(":")
        if kind not in CARD_FIELDS:
            skipped.append(f"{key}: unknown card kind, refused")
            continue
        record = records[kind].get(card_id)
        if record is None:
            skipped.append(f"{key}: no such card")
            continue
        fields = entry.get("fields") if isinstance(entry, dict) else None
        if not isinstance(fields, dict) or not fields:
            skipped.append(f"{key}: no field edits")
            continue
        changed = []
        for field, lines in sorted(fields.items()):
            if field not in CARD_FIELDS[kind]:
                skipped.append(f"{key}.{field}: unknown field, refused")
                continue
            if not isinstance(lines, list) or any(not isinstance(line, str) for line in lines):
                skipped.append(f"{key}.{field}: not a list of strings, refused")
                continue
            if record.get(field) == lines:
                continue
            record[field] = lines
            changed.append(field)
            if kind == "kit":
                touched_kits.add((card_id, field))
        if changed:
            applied.append(f"{key}: {', '.join(changed)}")
    if applied and not dry_run:
        if any(line.startswith("rescue:") for line in applied):
            atomic_write_text(RESCUE_CARDS, json.dumps(rescue, indent=2, ensure_ascii=True) + "\n")
        if touched_kits:
            atomic_write_text(KITS, write_kits_preserving_layout(kits_raw, kits, touched_kits))
    return applied, skipped


def load_export(path: Path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: could not read export {path}: {exc}")

    # Accept both the wrapped export and a bare id -> edits mapping.
    if isinstance(payload, dict) and ("edits" in payload or "cardEdits" in payload):
        schema = payload.get("schema")
        if schema != EXPORT_SCHEMA:
            sys.exit(f"error: unsupported export schema {schema!r}; expected {EXPORT_SCHEMA!r}")
        return payload.get("edits") or {}
    if isinstance(payload, dict):
        return payload
    sys.exit("error: export must be a JSON object")


def report_retrieval_change(before, after, edited_ids):
    """Say what the edit cost bedside retrieval, before anything is written.

    An edit to one section can hand a query to a neighbouring procedure without
    touching a word of clinical meaning: trimming the central-line shiftMode
    removed the last high-weight occurrence of "catheter", and "central line"
    began answering with the dialysis catheter. Nothing in the edit looked
    wrong, and the record still said everything it needed to say.

    Each record is probed with its own title and its own tags, so this covers
    whatever was edited rather than whatever someone once wrote a query for.
    Reported, never refused: the clinician's wording is the authority here, and
    a ranking slip is a thing to know about, not a veto.
    """
    before_index = search_model.SearchIndex(before)
    after_index = search_model.SearchIndex(after)
    by_id = {item.get("id"): item for item in after}

    losses = []
    for procedure_id in sorted(edited_ids):
        procedure = by_id.get(procedure_id)
        if procedure is None:
            continue
        for probe in search_model.self_retrieval_probes(procedure):
            was = before_index.rank_of(probe, procedure_id)
            now = after_index.rank_of(probe, procedure_id)
            if was is None or now is None or now <= was:
                continue
            winner = (after_index.search(probe) or ["nothing"])[0]
            losses.append(f"{procedure_id}: {probe!r} #{was} -> #{now}, now answered by {winner}")

    if not losses:
        print("\nBedside retrieval: no edited record lost ground on its own title or tags.")
        return
    print("\nRETRIEVAL: this edit costs the following searches:")
    for line in losses:
        print(f"  {line}")
    print(
        "  Adding the missing term as a tag restores ranking without touching prose;\n"
        "  tags are outside the material fingerprint, so a sign-off survives it."
    )


def edited_blind(procedure, entry) -> bool:
    """True when this edit was written against text the repo has since moved past.

    The app records the bundled material fingerprint at the moment a procedure's
    first section is edited. When that no longer matches the shipping content,
    the device wrote its replacement without ever seeing what the repo now says,
    and applying it discards the difference silently - the merge is a whole-
    section overwrite, so there is no conflict for anyone to notice.

    That is not hypothetical. The repo corrected the fascia iliaca equipment
    list against ACEP Sonoguide; the device, still on the older bundle, replaced
    the corrected lines with its own. Nothing in the output said so.

    Flagged, never refused. The reader is the clinical authority on their own
    wording and frequently means to replace it - but the diff for a flagged
    procedure has to be read as a merge, not as a change.

    The export carries no fingerprint version, so every reconstructable version
    is tried: a base written by an older build is still a valid base.
    """
    base = entry.get("baseMaterialFingerprint") if isinstance(entry, dict) else None
    if not base:
        # Written before the app recorded a base, or by a hand-built export.
        # Nothing to compare, and a warning on every record would train the
        # reader to skip the ones that mean something.
        return False
    return not any(
        review_fingerprint.procedure_fingerprint(procedure, version) == base
        for version in review_fingerprint.SECTIONS_BY_VERSION
    )


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) == 3 and parts[2].isdigit():
        return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
    return version


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("export", type=Path, help="JSON file exported from the app")
    parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing.")
    parser.add_argument(
        "--bump-version",
        action="store_true",
        help="Increment the patch version of each edited procedure.",
    )
    args = parser.parse_args(argv)

    edits = load_export(args.export)
    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    # Kept for the retrieval comparison below: the entries are mutated in place.
    before = copy.deepcopy(procedures)
    by_id = {item.get("id"): item for item in procedures}

    applied, skipped, edited_ids, blind = [], [], [], []
    for procedure_id, entry in sorted(edits.items()):
        procedure = by_id.get(procedure_id)
        if procedure is None:
            skipped.append(f"{procedure_id}: no such procedure in procedures.json")
            continue

        # Checked against the pre-edit record, so it reports the base this edit
        # was written against rather than the one this run just created.
        stale_base = edited_blind(procedure, entry)

        sections = entry.get("sections") if isinstance(entry, dict) else None
        if not isinstance(sections, dict) or not sections:
            skipped.append(f"{procedure_id}: no section edits")
            continue

        changed = []
        for key, lines in sorted(sections.items()):
            if key not in VALID_SECTIONS:
                skipped.append(f"{procedure_id}.{key}: unknown section, refused")
                continue
            if not isinstance(lines, list) or any(not isinstance(line, str) for line in lines):
                skipped.append(f"{procedure_id}.{key}: not a list of strings, refused")
                continue
            if procedure["sections"].get(key) == lines:
                continue
            procedure["sections"][key] = lines
            changed.append(key)

        if changed:
            if args.bump_version and isinstance(procedure.get("version"), str):
                procedure["version"] = bump_patch(procedure["version"])
            applied.append(f"{procedure_id}: {', '.join(changed)}")
            edited_ids.append(procedure_id)
            if stale_base:
                material = [key for key in changed if key in review_fingerprint.PROCEDURE_MATERIAL_SECTIONS]
                blind.append(
                    f"{procedure_id}: {', '.join(material) if material else 'no material section'}"
                )

    card_applied, card_skipped = apply_card_edits(load_card_edits(args.export), args.dry_run)

    for line in applied + card_applied:
        print(f"apply  {line}")
    for line in skipped + card_skipped:
        print(f"skip   {line}")
    if blind:
        print("\nBLIND MERGE: these edits were written against content the repo has since changed.")
        print("The overwrite is silent, so read their diff as a merge - anything the repo gained")
        print("after the device's last build is being discarded. Material sections overwritten:")
        for line in blind:
            print(f"  {line}")

    if card_applied:
        print(
            f"\n{'Dry run: ' if args.dry_run else ''}{len(card_applied)} rescue card(s)/kit(s)"
            f" {'would change' if args.dry_run else 'updated'}."
        )

    if not applied:
        if not card_applied:
            print("\nNothing to apply.")
        return 0

    # Before the write, so --dry-run shows the retrieval cost too.
    report_retrieval_change(before, procedures, edited_ids)

    if args.dry_run:
        print(f"\nDry run: {len(applied)} procedure(s) would change. Nothing written.")
        return 0

    # Match the existing file byte-for-byte outside the edit: 2-space indent,
    # ASCII-escaped non-ASCII (the shipped file stores "\u2013", not an en
    # dash), and no trailing newline. Getting this wrong rewrites every line
    # containing a dash and buries the real change in hundreds of diff lines.
    atomic_write_text(
        PROCEDURES,
        json.dumps(procedures, indent=2, ensure_ascii=True),
    )
    try:
        display_path = PROCEDURES.relative_to(ROOT)
    except ValueError:
        # PROCEDURES can be pointed elsewhere (tests, alternate checkout).
        display_path = PROCEDURES
    print(f"\nUpdated {len(applied)} procedure(s) in {display_path}.")
    print("Now run: python3 scripts/validate_procedures.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
