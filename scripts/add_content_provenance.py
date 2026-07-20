#!/usr/bin/env python3
"""Stamp explicit content provenance onto every content item.

Provenance: every procedure, rescue card, and kit in this repository was
drafted with AI assistance and none has yet received a qualified clinical
review, so each item is stamped `"contentSource": "ai-draft"`. A clinician
sign-off must flip the field (to "clinician-reviewed") at the same time as
`reviewerStatus` — the validators treat a reviewed status on an ai-draft item
as a contradiction. `lastReviewed` dates on ai-draft items are machine-stamped
draft dates, not human review dates; the app labels them accordingly.

Run from the repo root:
    python scripts/add_content_provenance.py
Idempotent; fails loudly if a file's expected shape is missing so silent
drift cannot masquerade as success.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"
AI_DRAFT = "ai-draft"


def stamp_items(items):
    """Insert contentSource after reviewerStatus (or append) on each item that
    lacks it, preserving key order. Returns how many items were stamped."""
    stamped = 0
    for index, item in enumerate(items):
        if "contentSource" in item:
            continue
        rebuilt = {}
        for key, value in item.items():
            rebuilt[key] = value
            if key == "reviewerStatus":
                rebuilt["contentSource"] = AI_DRAFT
        if "contentSource" not in rebuilt:
            rebuilt["contentSource"] = AI_DRAFT
        items[index] = rebuilt
        stamped += 1
    return stamped


def stamp_json_file(path: Path) -> int:
    """procedures.json and rescue_cards.json round-trip byte-exactly through
    json.dumps(indent=2, ensure_ascii=True) with no trailing newline."""
    items = json.loads(path.read_text(encoding="utf-8"))
    stamped = stamp_items(items)
    if stamped:
        path.write_bytes(json.dumps(items, indent=2, ensure_ascii=True).encode("utf-8"))
    return stamped


def stamp_kits_file(path: Path) -> int:
    """kits.json is hand-formatted (inline arrays), so a JSON rewrite would
    reformat the file. Insert a contentSource line after each reviewerStatus
    line instead, and verify the result still parses to fully stamped items."""
    text = path.read_text(encoding="utf-8")
    kit_count = len(json.loads(text))
    if text.count('"contentSource"') == kit_count:
        return 0

    pattern = re.compile(r'^(\s*)("reviewerStatus": "[^"]*",?)$', re.MULTILINE)

    def insert(match):
        indent, line = match.group(1), match.group(2)
        separator = "" if line.endswith(",") else ","
        return f'{indent}{line}{separator}\n{indent}"contentSource": "{AI_DRAFT}"' + (
            "," if line.endswith(",") else ""
        )

    updated, replacements = pattern.subn(insert, text)
    if replacements != kit_count:
        print(f"ERROR: expected {kit_count} reviewerStatus lines in {path.name}, matched {replacements}")
        return -1
    parsed = json.loads(updated)
    missing = [item.get("id") for item in parsed if item.get("contentSource") != AI_DRAFT]
    if missing:
        print(f"ERROR: kits still missing contentSource after stamping: {missing}")
        return -1
    path.write_text(updated, encoding="utf-8", newline="\n")
    return replacements


def main() -> int:
    total = 0
    for name in ("procedures.json", "rescue_cards.json"):
        stamped = stamp_json_file(RESOURCES / name)
        print(f"{name}: stamped {stamped} items")
        total += stamped
    kits_stamped = stamp_kits_file(RESOURCES / "kits.json")
    if kits_stamped < 0:
        return 1
    print(f"kits.json: stamped {kits_stamped} items")
    total += kits_stamped
    print(f"Stamped contentSource on {total} content items.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
