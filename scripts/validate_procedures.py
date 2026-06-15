#!/usr/bin/env python3
"""Lightweight local content validation for ProcedureSTAT.

Run from the project root:
    python scripts/validate_procedures.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "ProcedureSTAT" / "Resources" / "procedures.json"
REQUIRED_SECTIONS = [
    "shiftMode", "indications", "contraindications", "anatomy", "equipment",
    "positioning", "steps", "ultrasound", "confirmation", "troubleshooting",
    "complications", "aftercare", "documentation", "seniorPearls", "references"
]
MINIMUMS = {
    "shiftMode": 6,
    "equipment": 5,
    "steps": 5,
    "complications": 4,
    "troubleshooting": 3,
    "documentation": 4,
    "references": 1,
}


def main() -> int:
    data = json.loads(PROCEDURES.read_text())
    issues = []
    ids = [item.get("id") for item in data]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    for duplicate_id in duplicate_ids:
        issues.append(("BLOCKER", duplicate_id, "duplicate procedure id"))

    for item in data:
        pid = item.get("id", "<missing id>")
        title = item.get("title", pid)
        sections = item.get("sections", {})
        for key in REQUIRED_SECTIONS:
            if key not in sections:
                issues.append(("BLOCKER", title, f"missing section: {key}"))
            elif not isinstance(sections[key], list):
                issues.append(("BLOCKER", title, f"section is not a list: {key}"))
            elif key in MINIMUMS and len(sections[key]) < MINIMUMS[key]:
                level = "BLOCKER" if key in {"shiftMode", "equipment", "steps", "complications", "references"} and len(sections[key]) == 0 else "WARNING"
                issues.append((level, title, f"thin section: {key} has {len(sections[key])}, target {MINIMUMS[key]}"))
        for field in ["lastReviewed", "version", "category", "difficulty"]:
            if not item.get(field):
                issues.append(("BLOCKER", title, f"missing metadata: {field}"))

    blockers = [issue for issue in issues if issue[0] == "BLOCKER"]
    for level, title, message in issues:
        print(f"{level}: {title}: {message}")
    print(f"\nValidated {len(data)} procedures. Blockers: {len(blockers)}. Total issues: {len(issues)}.")
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
