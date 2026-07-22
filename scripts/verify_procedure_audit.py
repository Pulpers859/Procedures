#!/usr/bin/env python3
"""Fail closed unless the fingerprinted procedure audit is complete."""

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"
RESCUE_CARDS = ROOT / "Procedures" / "Resources" / "rescue_cards.json"
KITS = ROOT / "Procedures" / "Resources" / "kits.json"
AUDIT_ROOT = ROOT / "docs" / "audits" / "procedure-verification"
EXPECTED_SHA256 = "3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1"
EXPECTED_RESCUE_SHA256 = "4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14"
EXPECTED_KITS_SHA256 = "c4c40950e457eabb3b8830f838140cd43ff1c610a6c84e8abd9358951d39e520"
REPORTS = [
    "01_AIRWAY_SEDATION.md",
    "02_VASCULAR_ACCESS.md",
    "03_THORACIC.md",
    "04_CARDIAC_NEURO.md",
    "05_GENERAL_PROCEDURES.md",
    "06_REGIONAL_UPPER.md",
    "07_REGIONAL_TRUNK.md",
    "08_REGIONAL_LOWER.md",
    "09_REGIONAL_DISTAL_CRANIOFACIAL.md",
]
DISPOSITIONS = (
    "STOP-SHIP",
    "MAJOR",
    "MINOR",
    "NO MATERIAL DISCREPANCY IDENTIFIED",
    "INSUFFICIENT EVIDENCE",
)
AUTHORITATIVE_HOST_SUFFIXES = (
    ".gov",
    ".mil",
    "acep.org",
    "aap.org",
    "aapd.org",
    "academic.oup.com",
    "acr.org",
    "asra.com",
    "bmj.com",
    "brit-thoracic.org.uk",
    "cookmedical.com",
    "dailymed.nlm.nih.gov",
    "east.org",
    "escardio.org",
    "entnet.org",
    "heart.org",
    "idsociety.org",
    "journals.lww.com",
    "kdigo.org",
    "kidney.org",
    "nice.org.uk",
    "onlinelibrary.wiley.com",
    "philips.com",
    "pubmed.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
    "rapm.bmj.com",
    "springer.com",
    "springeropen.com",
    "stryker.com",
    "teleflex.com",
    "thorax.bmj.com",
    "westerntrauma.org",
    "who.int",
)
DISPOSITION_LINE = re.compile(
    r"(?im)^\*\*Screening disposition:\s*`?"
    r"(STOP-SHIP|MAJOR|MINOR|NO MATERIAL DISCREPANCY IDENTIFIED|INSUFFICIENT EVIDENCE)"
    r"`?\b"
)
POSITIVE_APPROVAL_CLAIM = re.compile(
    r"(?i)\b(?:report|audit|screening|content|procedures?)\s+"
    r"(?:is|are|has been|have been)\s+clinically\s+(?:verified|approved)\b|"
    r"\bapproved for release\b|\bclinical approval\s+(?:is\s+)?(?:granted|confirmed|complete)\b|"
    r"\b(?:this|report|audit|screening)\s+is\s+(?:a\s+)?clinical approval\b"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def procedure_sections(text: str, procedure_ids: set[str]):
    headings = []
    for match in re.finditer(r"(?m)^##\s+(.+)$", text):
        heading = match.group(1)
        matched_ids = [
            procedure_id
            for procedure_id in procedure_ids
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(procedure_id)}(?![A-Za-z0-9_])", heading)
        ]
        if len(matched_ids) == 1:
            headings.append((match.start(), matched_ids[0]))

    for index, (start, procedure_id) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        yield procedure_id, text[start:end]


def has_authoritative_source(section: str) -> bool:
    for url in re.findall(r"https://[^)\s]+", section):
        host = (urlparse(url).hostname or "").lower()
        if any(
            host.endswith(suffix)
            if suffix.startswith(".")
            else host == suffix or host.endswith(f".{suffix}")
            for suffix in AUTHORITATIVE_HOST_SUFFIXES
        ):
            return True
    return False


def audit_issues(require_synthesis: bool = True) -> list[str]:
    issues = []
    fingerprints = (
        ("procedures.json", PROCEDURES, EXPECTED_SHA256),
        ("rescue_cards.json", RESCUE_CARDS, EXPECTED_RESCUE_SHA256),
        ("kits.json", KITS, EXPECTED_KITS_SHA256),
    )
    for label, path, expected_hash in fingerprints:
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            issues.append(
                f"{label} fingerprint changed: expected {expected_hash}, found {actual_hash}"
            )

    procedure_ids = {
        item["id"] for item in json.loads(PROCEDURES.read_text(encoding="utf-8"))
    }
    occurrences = {procedure_id: [] for procedure_id in procedure_ids}

    for report_name in REPORTS:
        report_path = AUDIT_ROOT / report_name
        if not report_path.is_file():
            issues.append(f"missing report: {report_path.relative_to(ROOT).as_posix()}")
            continue
        text = report_path.read_text(encoding="utf-8")
        if EXPECTED_SHA256 not in text:
            issues.append(f"{report_name}: missing exact corpus fingerprint")
        lower_text = text.lower()
        if not any(
            boundary in lower_text
            for boundary in (
                "not clinical approval",
                "not medical approval",
                "does not approve content",
            )
        ):
            issues.append(f"{report_name}: missing explicit non-approval boundary")
        if POSITIVE_APPROVAL_CLAIM.search(text):
            issues.append(f"{report_name}: contains a positive clinical-approval claim")

        for procedure_id, section in procedure_sections(text, procedure_ids):
            occurrences[procedure_id].append(report_name)
            if not DISPOSITION_LINE.search(section):
                issues.append(f"{report_name}: {procedure_id} has no exact recognized disposition line")
            if not re.search(r"(?i)\bequipment\b|\binstruments?\b", section):
                issues.append(f"{report_name}: {procedure_id} has no equipment/instrument assessment")
            if not re.search(
                r"(?i)\breviewer questions?\b|\bquestions? for (?:the )?clinical reviewer\b",
                section,
            ):
                issues.append(f"{report_name}: {procedure_id} has no reviewer question")
            if not has_authoritative_source(section):
                issues.append(f"{report_name}: {procedure_id} has no recognized authoritative source link")
            if not re.search(r"(?i)`?reviewerStatus`?\s+remains unchanged", section):
                issues.append(f"{report_name}: {procedure_id} does not preserve reviewerStatus explicitly")

    for procedure_id, report_names in sorted(occurrences.items()):
        if not report_names:
            issues.append(f"procedure not audited: {procedure_id}")
        elif len(report_names) > 1:
            issues.append(
                f"procedure audited more than once: {procedure_id} ({', '.join(report_names)})"
            )

    index_path = AUDIT_ROOT / "AUDIT_INDEX.md"
    queue_path = AUDIT_ROOT / "CLINICAL_OWNER_QUEUE.md"
    protocol_path = AUDIT_ROOT / "AUDIT_PROTOCOL.md"
    if require_synthesis:
        for required_path in (index_path, queue_path, protocol_path):
            if not required_path.is_file():
                issues.append(f"missing synthesis artifact: {required_path.name}")
            elif POSITIVE_APPROVAL_CLAIM.search(required_path.read_text(encoding="utf-8")):
                issues.append(f"{required_path.name}: contains a positive clinical-approval claim")

    if require_synthesis and protocol_path.is_file():
        protocol_text = protocol_path.read_text(encoding="utf-8")
        for label, _, expected_hash in fingerprints:
            if expected_hash not in protocol_text:
                issues.append(f"AUDIT_PROTOCOL.md: missing audited {label} fingerprint")

    if require_synthesis and queue_path.is_file():
        queue_text = queue_path.read_text(encoding="utf-8")
        if EXPECTED_SHA256 not in queue_text:
            issues.append("CLINICAL_OWNER_QUEUE.md: missing exact corpus fingerprint")
        for heading in (
            "## P0:",
            "## P1:",
            "## P2:",
            "## P3:",
            "## Recommended Human Review Order",
        ):
            if heading not in queue_text:
                issues.append(f"CLINICAL_OWNER_QUEUE.md: missing required section {heading}")
        if not re.search(r"(?i)no `?reviewerStatus`? should change", queue_text):
            issues.append("CLINICAL_OWNER_QUEUE.md: missing reviewerStatus release boundary")
        for report_name in REPORTS:
            if not re.search(
                rf"\[[^]]+\]\(\s*{re.escape(report_name)}(?:#[^)]+)?\s*\)",
                queue_text,
            ):
                issues.append(f"CLINICAL_OWNER_QUEUE.md: missing evidence link to {report_name}")

    if require_synthesis and index_path.is_file():
        index_text = index_path.read_text(encoding="utf-8")
        indexed_rows = {}
        for procedure_id in procedure_ids:
            row_match = re.search(
                rf"(?m)^\|[^\n]*\| `{re.escape(procedure_id)}`[^\n]*?\| `"
                rf"({'|'.join(re.escape(value) for value in DISPOSITIONS)})` \| "
                rf"\[[^]]+\]\(([^)]+)\) \|$",
                index_text,
            )
            if row_match:
                indexed_rows[procedure_id] = (row_match.group(1).upper(), row_match.group(2))

        expected_dispositions = {}
        for report_name in REPORTS:
            report_path = AUDIT_ROOT / report_name
            if report_path.is_file():
                for procedure_id, section in procedure_sections(
                    report_path.read_text(encoding="utf-8"), procedure_ids
                ):
                    match = DISPOSITION_LINE.search(section)
                    if match:
                        expected_dispositions[procedure_id] = (
                            match.group(1).upper(),
                            report_name,
                        )
        for procedure_id in procedure_ids:
            if len(re.findall(rf"`{re.escape(procedure_id)}`", index_text)) != 1:
                issues.append(f"AUDIT_INDEX.md must list {procedure_id} exactly once")
            elif indexed_rows.get(procedure_id) != expected_dispositions.get(procedure_id):
                issues.append(
                    f"AUDIT_INDEX.md disposition for {procedure_id} does not match its lane report"
                )
    return issues


def main() -> int:
    issues = audit_issues()
    if issues:
        print("Procedure audit verification failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(
        "Verified nine fingerprinted audit reports with exactly one evidence-backed "
        "section for each of 55 procedures."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
