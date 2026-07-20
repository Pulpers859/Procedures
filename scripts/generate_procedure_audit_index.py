#!/usr/bin/env python3
"""Generate the human-readable index for the fingerprinted procedure audit."""

from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from verify_procedure_audit import (
    AUDIT_ROOT,
    EXPECTED_SHA256,
    PROCEDURES,
    REPORTS,
    audit_issues,
    procedure_sections,
)


OUTPUT = AUDIT_ROOT / "AUDIT_INDEX.md"
DISPOSITION_PATTERN = re.compile(
    r"(?i)Screening disposition[^\n]*?\b"
    r"(STOP-SHIP|MAJOR|MINOR|NO MATERIAL DISCREPANCY IDENTIFIED|INSUFFICIENT EVIDENCE)\b"
)


def main() -> int:
    issues = audit_issues(require_synthesis=False)
    if issues:
        raise SystemExit("Refusing to index an incomplete audit:\n- " + "\n- ".join(issues))

    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in procedures}
    locations = {}
    for report_name in REPORTS:
        text = (AUDIT_ROOT / report_name).read_text(encoding="utf-8")
        for procedure_id, section in procedure_sections(text, set(by_id)):
            match = DISPOSITION_PATTERN.search(section)
            locations[procedure_id] = (match.group(1).upper(), report_name)

    counts = Counter(disposition for disposition, _ in locations.values())
    categories = defaultdict(list)
    for item in procedures:
        categories[item["category"]].append(item)

    lines = [
        "# Procedure Verification Audit Index",
        "",
        "## Result",
        "",
        f"- Audited procedures: **{len(procedures)}/{len(procedures)}**.",
        f"- Proposed `STOP-SHIP`: **{counts['STOP-SHIP']}**.",
        f"- Proposed `MAJOR`: **{counts['MAJOR']}**.",
        f"- Corpus SHA-256: `{EXPECTED_SHA256}`.",
        "- Audit date: 2026-07-18.",
        "",
        "Every disposition is an AI-assisted discrepancy-screen result, not a",
        "clinical approval. Some `STOP-SHIP` dispositions arise from an unapproved",
        "declared visual while the clinical-text findings are `MAJOR`; consult the",
        "individual report before assigning remediation priority.",
        "",
        "## Lane Reports",
        "",
    ]
    for report_name in REPORTS:
        label = report_name.removesuffix(".md").replace("_", " ").title()
        lines.append(f"- [{label}]({report_name})")

    lines.extend([
        "",
        "## Procedure Coverage",
        "",
        "| Category | Procedure | Disposition | Report |",
        "|---|---|---|---|",
    ])
    for category in sorted(categories):
        for item in sorted(categories[category], key=lambda value: value["title"]):
            disposition, report_name = locations[item["id"]]
            lines.append(
                f"| {category} | `{item['id']}` - {item['title']} | "
                f"`{disposition}` | [{report_name}]({report_name}) |"
            )

    lines.extend([
        "",
        "## Release Boundary",
        "",
        "No `reviewerStatus` was changed. A qualified clinical owner must adjudicate",
        "each finding against the exact content version, local formulary, stocked",
        "devices and IFUs, credentialing, and institutional policy before any record",
        "can be marked reviewed or released.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
