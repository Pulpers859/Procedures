#!/usr/bin/env python3
"""Add topical tranexamic acid (TXA) to anterior nasal packing.

Provenance: the 2026-07 bedside-search review found "TXA" returned zero
results because the word appears nowhere in the corpus, including nasal
packing where topical TXA is standard EM practice (e.g. Zahed R et al.,
Am J Emerg Med 2013; Roberts and Hedges'). This adds an equipment line and
search tags. Content remains an AI draft pending clinical review; no
reviewerStatus changes.

Run from the repo root:
    python scripts/add_txa_epistaxis_content.py
Idempotent; fails loudly if the target procedure is missing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"

TARGET_ID = "anterior_nasal_packing"
EQUIPMENT_LINE = (
    "Tranexamic acid (TXA) for topical use per local policy (e.g. 500 mg/5 mL "
    "injectable solution applied on a pledget or used to soak the pack)"
)
NEW_TAGS = ["txa", "tranexamic acid", "nosebleed"]
REFERENCE = (
    "Zahed R, Moharamzadeh P, Alizadeharasi S, Ghasemi A, Saeedi M. A new and "
    "rapid method for epistaxis treatment using injectable form of tranexamic "
    "acid topically: a randomized controlled trial. Am J Emerg Med. 2013;31(9):1389-1392."
)


def main() -> int:
    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    target = next((item for item in procedures if item.get("id") == TARGET_ID), None)
    if target is None:
        print(f"ERROR: expected procedure not found: {TARGET_ID}")
        return 1

    changed = False
    equipment = target["sections"]["equipment"]
    if EQUIPMENT_LINE not in equipment:
        equipment.append(EQUIPMENT_LINE)
        changed = True
    for tag in NEW_TAGS:
        if tag not in target["tags"]:
            target["tags"].append(tag)
            changed = True
    references = target["sections"]["references"]
    if REFERENCE not in references:
        references.append(REFERENCE)
        changed = True

    if changed:
        # Match the file's serialization exactly (indent=2, ASCII, no trailing
        # newline) so the diff shows only real content changes.
        PROCEDURES.write_bytes(
            json.dumps(procedures, indent=2, ensure_ascii=True).encode("utf-8")
        )
    print(f"{TARGET_ID}: {'updated' if changed else 'already up to date'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
