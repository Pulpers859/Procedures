#!/usr/bin/env python3
"""Apply edits exported from the app back into the bundled content.

The app cannot write to its own bundle, so corrections a clinician makes at the
bedside are stored as local overrides and exported as JSON. This merges that
export into `Procedures/Resources/procedures.json` so the change lands as a
reviewable git diff rather than a wholesale file replacement.

Usage:
    python3 scripts/apply_local_edits.py path/to/procedure-edits-2026-07-27.json
    python3 scripts/apply_local_edits.py edits.json --dry-run
    python3 scripts/apply_local_edits.py edits.json --bump-version

Always re-run `python3 scripts/validate_procedures.py` afterwards: an edit can
empty a required section or drop the last reference, and only the validator
will catch that.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomic_write import atomic_write_text

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"
EXPORT_SCHEMA = "procedures.local-edits.v1"

# Mirror of EditableSection in Procedures/Data/ProcedureEditStore.swift. A key
# outside this set is refused rather than silently written into the content.
VALID_SECTIONS = {
    "shiftMode", "indications", "contraindications", "anatomy", "equipment",
    "positioning", "steps", "ultrasound", "confirmation", "troubleshooting",
    "complications", "aftercare", "documentation", "seniorPearls", "references",
}


def load_export(path: Path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: could not read export {path}: {exc}")

    # Accept both the wrapped export and a bare id -> edits mapping.
    if isinstance(payload, dict) and "edits" in payload:
        schema = payload.get("schema")
        if schema != EXPORT_SCHEMA:
            sys.exit(f"error: unsupported export schema {schema!r}; expected {EXPORT_SCHEMA!r}")
        return payload["edits"]
    if isinstance(payload, dict):
        return payload
    sys.exit("error: export must be a JSON object")


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
    by_id = {item.get("id"): item for item in procedures}

    applied, skipped = [], []
    for procedure_id, entry in sorted(edits.items()):
        procedure = by_id.get(procedure_id)
        if procedure is None:
            skipped.append(f"{procedure_id}: no such procedure in procedures.json")
            continue

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

    for line in applied:
        print(f"apply  {line}")
    for line in skipped:
        print(f"skip   {line}")

    if not applied:
        print("\nNothing to apply.")
        return 0

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
