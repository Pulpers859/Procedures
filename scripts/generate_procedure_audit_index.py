#!/usr/bin/env python3
"""Generate the human-readable index for the fingerprinted procedure audit."""

from collections import Counter, defaultdict
import json
from pathlib import Path

from verify_procedure_audit import (
    AUDIT_ROOT,
    EXPECTED_SHA256,
    PROCEDURES,
    REPORTS,
    audit_issues,
    corpus_drift_issues,
    disposition_in,
    load_ledger,
    procedure_sections,
)


OUTPUT = AUDIT_ROOT / "AUDIT_INDEX.md"


def integrity_block() -> list[str]:
    """The integrity hold, computed rather than hand-written.

    It used to be a blockquote someone added by hand, which the generator did
    not emit — so the first regeneration would have silently deleted the
    warning and left a clean-looking index over a corpus that had drifted.
    Deriving it from the ledger means it cannot be lost, and cannot go stale
    while the corpus moves underneath it.
    """
    ledger, ledger_issues = load_ledger()
    if ledger is None:
        return [
            "> **Integrity unknown:** the audit ledger could not be read "
            f"({'; '.join(ledger_issues)}). Treat this index as out of date.",
            "",
        ]

    blocking, notices = corpus_drift_issues(ledger)
    drifted = sorted(
        issue.split(": ", 1)[1].split(" ", 1)[0]
        for issue in blocking
        if "drifted from the audited baseline" in issue
    )
    lines = []
    if drifted:
        lines += [
            f"> **Integrity hold:** {len(drifted)} of the audited procedures have "
            "changed since this audit, so their findings below describe text that "
            "is no longer shipping:",
            ">",
            "> " + ", ".join(f"`{record}`" for record in drifted),
            ">",
            "> Every other record still matches the bytes that were screened. See "
            "`AUDIT_LEDGER.json` for per-record baselines and any amendments.",
            "",
        ]
    else:
        lines += [
            "> **Integrity:** every audited procedure still matches the bytes that "
            "were screened, per `AUDIT_LEDGER.json`.",
            "",
        ]
    lines += [
        "> **Scope:** this packet screened procedures only. No kit and no rescue "
        "card has a per-record evidence section in any lane report, and the "
        "rescue-card snapshot the protocol names was never committed, so no "
        "rescue-card baseline can be recovered. Nothing here attests to either.",
        "",
    ]
    if notices:
        lines += [
            "> **Outside audit scope, changed since the baseline:** "
            + "; ".join(notice.split(": ", 1)[1] for notice in notices),
            "",
        ]
    return lines


def main() -> int:
    issues = audit_issues(require_synthesis=False, require_current_corpus=False)
    if issues:
        raise SystemExit("Refusing to index an incomplete audit:\n- " + "\n- ".join(issues))

    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in procedures}
    locations = {}
    for report_name in REPORTS:
        text = (AUDIT_ROOT / report_name).read_text(encoding="utf-8")
        for procedure_id, section in procedure_sections(text, set(by_id)):
            # Same parser the verifier uses. Two regexes over one line is how
            # the generator used to crash on input the verifier would reject.
            locations[procedure_id] = (disposition_in(section), report_name)

    counts = Counter(disposition for disposition, _ in locations.values())
    categories = defaultdict(list)
    for item in procedures:
        categories[item["category"]].append(item)

    lines = [
        "# Procedure Verification Audit Index",
        "",
        *integrity_block(),
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
    OUTPUT.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
