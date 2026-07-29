#!/usr/bin/env python3
"""Fail closed unless the fingerprinted procedure audit is complete.

Drift is measured per record, against a baseline derived from the audited
bytes. It used to be measured by comparing three whole-file SHA-256 constants,
which had three fatal properties:

  * A metadata edit was indistinguishable from a dose change. Adding
    `contentSource: "ai-draft"` to every record — the change that made the
    corpus *more* honest about being unreviewed — invalidated all 55 procedure
    audits at once, when exactly two procedures had changed clinically.
  * There was no exit. The only way to turn the gate green was to retype the
    constants, which is rubber-stamping with extra steps, and which
    AUDIT_PROTOCOL.md explicitly forbids.
  * Two of the three constants named bytes that no longer existed. The audit
    fingerprinted an uncommitted working tree, so the rescue-card baseline is
    in no git object at all and can never be satisfied.

So: baselines live in AUDIT_LEDGER.json, are derived only from immutable git
blobs (see generate_audit_ledger.py), and drift is resolved per record by an
amendment carrying the waiver fields RELEASE_CONSTITUTION.md already requires —
owner, rationale, commit, expiry, follow-up. Amendments expire, so a waiver
cannot quietly become permanent.
"""

import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_fingerprint


ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"
RESCUE_CARDS = ROOT / "Procedures" / "Resources" / "rescue_cards.json"
KITS = ROOT / "Procedures" / "Resources" / "kits.json"
AUDIT_ROOT = ROOT / "docs" / "audits" / "procedure-verification"
LEDGER = AUDIT_ROOT / "AUDIT_LEDGER.json"

# The SHA-256 of the procedures.json bytes the audit screened. This is a
# historical fact, quoted by the nine lane reports and the clinical owner
# queue to declare what they looked at. It is no longer compared against the
# shipping file; see the module docstring.
EXPECTED_SHA256 = "3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1"

# The rescue-card fingerprint AUDIT_PROTOCOL.md recorded. No object in this
# repository hashes to it, so it identifies bytes that were never committed.
# Kept as evidence of exactly that, not as something to compare against.
UNRECOVERABLE_RESCUE_SHA256 = "4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14"

# Set to a datetime.date in tests to make amendment expiry deterministic.
TODAY = None

KNOWN_CORPORA = ("procedures.json", "rescue_cards.json", "kits.json")
AMENDMENT_FIELDS = ("corpus", "recordId", "auditFingerprint", "owner", "rationale", "commit", "expires", "followUp")

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


def today() -> datetime.date:
    return TODAY or datetime.date.today()


def content_path(filename: str) -> Path:
    return {
        "procedures.json": PROCEDURES,
        "rescue_cards.json": RESCUE_CARDS,
        "kits.json": KITS,
    }[filename]


def load_ledger():
    if not LEDGER.is_file():
        return None, [f"missing audit ledger: {LEDGER.name}"]
    try:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{LEDGER.name} is not valid JSON: {exc}"]
    if ledger.get("schema") != "procedures.audit-ledger.v1":
        return None, [f"{LEDGER.name}: unsupported schema {ledger.get('schema')!r}"]
    algorithm = ledger.get("fingerprintAlgorithm")
    version = ledger.get("fingerprintVersion")
    if algorithm != "audit/v1" or version != audit_fingerprint.AUDIT_FINGERPRINT_VERSION:
        # An older digest answers a different question. "Cannot compare" must
        # never quietly read as "unchanged", so this fails rather than skips.
        return None, [
            f"{LEDGER.name}: baselines were written under {algorithm!r} "
            f"version {version!r} and cannot be compared against "
            f"audit/v1 version {audit_fingerprint.AUDIT_FINGERPRINT_VERSION} "
            "digests; the baselines must be re-derived from the audited bytes"
        ]
    return ledger, []


def amendment_index(ledger) -> tuple[dict, list[str]]:
    """Map (corpus, recordId) -> accepted fingerprint, rejecting bad waivers.

    An amendment is how a person says "this record changed after the audit, I
    looked at the change, and here is why the release may proceed anyway". It
    carries the same fields RELEASE_CONSTITUTION.md requires of any waiver, and
    it expires — an unbounded amendment is just a re-baseline wearing a hat.
    """
    accepted = {}
    issues = []
    for position, amendment in enumerate(ledger.get("amendments") or [], start=1):
        label = f"{LEDGER.name}: amendment {position}"
        if not isinstance(amendment, dict):
            issues.append(f"{label} is not an object")
            continue
        missing = [
            field
            for field in AMENDMENT_FIELDS
            if not str(amendment.get(field) or "").strip()
        ]
        if missing:
            issues.append(f"{label} is missing required waiver fields: {', '.join(missing)}")
            continue
        corpus = amendment["corpus"]
        record_id = amendment["recordId"]
        if corpus not in KNOWN_CORPORA:
            issues.append(f"{label} names unknown corpus {corpus!r}")
            continue
        try:
            expires = datetime.date.fromisoformat(amendment["expires"])
        except ValueError:
            issues.append(f"{label} has an unparseable expiry {amendment['expires']!r}")
            continue
        if expires < today():
            issues.append(
                f"{label} for {corpus} {record_id} expired on {expires.isoformat()}; "
                "an expired waiver is a stop-ship condition"
            )
            continue
        accepted[(corpus, record_id)] = amendment["auditFingerprint"]
    return accepted, issues


def corpus_drift_issues(ledger) -> tuple[list[str], list[str]]:
    """Return (blocking issues, non-blocking notices) for content drift.

    Drift blocks only where per-record audit evidence exists to be invalidated.
    procedures.json has an evidence section for each of its 55 records, so a
    drifted procedure means a lane report now describes text that is not
    shipping. Kits and rescue cards have no per-record evidence in any lane
    report, so their drift invalidates nothing and is reported rather than
    gated; the reviewed-status stop-ship in RELEASE_CONSTITUTION.md is what
    actually holds unreviewed content back, and it is far stricter than this.
    """
    issues = []
    notices = []
    accepted, amendment_issues = amendment_index(ledger)
    issues.extend(amendment_issues)

    for filename, corpus in sorted((ledger.get("corpora") or {}).items()):
        if filename not in KNOWN_CORPORA:
            issues.append(f"{LEDGER.name}: unknown corpus {filename!r}")
            continue
        gated = corpus.get("screening") == "per-record"
        sink = issues if gated else notices
        baseline = corpus.get("records") or {}

        try:
            items = json.loads(content_path(filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"{filename}: could not be read for drift comparison: {exc}")
            continue
        current = {
            item["id"]: audit_fingerprint.audit_fingerprint(item) for item in items
        }

        for record_id in sorted(set(baseline) - set(current)):
            sink.append(
                f"{filename}: {record_id} was audited but is no longer in the corpus"
            )
        for record_id in sorted(set(current) - set(baseline)):
            sink.append(
                f"{filename}: {record_id} is not in the audited baseline "
                "(added after the audit, never screened)"
            )
        for record_id in sorted(set(baseline) & set(current)):
            if current[record_id] == baseline[record_id]:
                continue
            waived = accepted.get((filename, record_id))
            if waived == current[record_id]:
                continue
            detail = (
                "an amendment exists but names a different fingerprint, so the "
                "content changed again after it was written"
                if waived
                else "no amendment covers this change"
            )
            sink.append(
                f"{filename}: {record_id} drifted from the audited baseline "
                f"({baseline[record_id][:12]} -> {current[record_id][:12]}); {detail}"
            )
    return issues, notices


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


def disposition_in(section: str) -> str | None:
    """The one parser for a disposition line.

    The index generator used to carry a second, looser regex for the same line.
    Two parsers over one artifact can disagree about what a report says, and the
    looser one crashed on a line the stricter one would have rejected.
    """
    match = DISPOSITION_LINE.search(section)
    return match.group(1).upper() if match else None


def lane_dispositions(procedure_ids: set[str]) -> dict:
    """procedure_id -> (disposition, report_name), read from the lane reports."""
    found = {}
    for report_name in REPORTS:
        report_path = AUDIT_ROOT / report_name
        if not report_path.is_file():
            continue
        text = report_path.read_text(encoding="utf-8")
        for procedure_id, section in procedure_sections(text, procedure_ids):
            disposition = disposition_in(section)
            if disposition:
                found[procedure_id] = (disposition, report_name)
    return found


def unresolved_finding_issues(procedure_ids: set[str]) -> list[str]:
    """Refuse to call an audit verified while its findings are still open.

    Every check in this file used to be about whether the *paperwork* was
    complete. None asked whether anything the paperwork found had been dealt
    with. With the fingerprints satisfied, the verifier would print "Verified
    nine fingerprinted audit reports" over a corpus where every procedure
    carried an unresolved release-blocking disposition — the single most
    dangerous output this script could produce, because it reads as a clean
    bill of health for the exact records the audit flagged.

    Closure is a clinical judgement, so nothing here closes a finding. This
    only refuses to let silence be mistaken for resolution.
    """
    blocking = sorted(
        procedure_id
        for procedure_id, (disposition, _) in lane_dispositions(procedure_ids).items()
        if disposition in ("STOP-SHIP", "MAJOR")
    )
    if not blocking:
        return []
    stop_ship = sorted(
        procedure_id
        for procedure_id, (disposition, _) in lane_dispositions(procedure_ids).items()
        if disposition == "STOP-SHIP"
    )
    return [
        f"{len(blocking)} of {len(procedure_ids)} procedures carry an unresolved "
        f"release-blocking screening disposition ({len(stop_ship)} STOP-SHIP, "
        f"{len(blocking) - len(stop_ship)} MAJOR). A clinical owner must "
        "adjudicate them via CLINICAL_OWNER_QUEUE.md; the audit packet is "
        "evidence of unresolved findings, not clearance to ship."
    ]


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


def audit_issues(
    require_synthesis: bool = True,
    notices: list | None = None,
    require_current_corpus: bool = True,
) -> list[str]:
    """Structural problems with the audit packet, worst-first.

    `require_current_corpus` exists for the index generator. The index is a
    derived view of what the lane reports say; it must stay regenerable while
    content drift is being worked through, or the only way to update it is to
    silence the drift first — which is the deadlock this whole rewrite exists
    to remove. Report structure is still fully checked.
    """
    issues = []
    procedure_ids = {
        item["id"] for item in json.loads(PROCEDURES.read_text(encoding="utf-8"))
    }

    if require_current_corpus:
        ledger, ledger_issues = load_ledger()
        issues.extend(ledger_issues)
        if ledger is not None:
            drift_issues, drift_notices = corpus_drift_issues(ledger)
            issues.extend(drift_issues)
            if notices is not None:
                notices.extend(drift_notices)
        issues.extend(unresolved_finding_issues(procedure_ids))
    else:
        ledger, _ = load_ledger()

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
        # The protocol is the historical record of what was screened. It must
        # keep naming the audited fingerprints even though they are no longer
        # compared against the shipping files, including the rescue-card one
        # whose bytes are lost — deleting it would erase the evidence that the
        # audit fingerprinted something it never committed.
        recorded = [UNRECOVERABLE_RESCUE_SHA256]
        if ledger is not None:
            recorded.extend(
                corpus["auditedFileSha256"]
                for corpus in (ledger.get("corpora") or {}).values()
                if corpus.get("auditedFileSha256")
            )
        for expected_hash in recorded:
            if expected_hash not in protocol_text:
                issues.append(
                    f"AUDIT_PROTOCOL.md: missing audited fingerprint {expected_hash[:12]}"
                )

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

        expected_dispositions = lane_dispositions(procedure_ids)
        for procedure_id in procedure_ids:
            if len(re.findall(rf"`{re.escape(procedure_id)}`", index_text)) != 1:
                issues.append(f"AUDIT_INDEX.md must list {procedure_id} exactly once")
            elif indexed_rows.get(procedure_id) != expected_dispositions.get(procedure_id):
                issues.append(
                    f"AUDIT_INDEX.md disposition for {procedure_id} does not match its lane report"
                )
    return issues


def main() -> int:
    notices = []
    issues = audit_issues(notices=notices)

    if notices:
        # Printed before the verdict either way. These are records with no
        # per-record audit evidence to invalidate, so they cannot fail this
        # gate — but drift in them is still something the release owner should
        # see rather than discover later.
        print("Content drift outside the per-record audit scope (not blocking):")
        for notice in notices:
            print(f"  - {notice}")
        print()

    if issues:
        print("Procedure audit verification failed:")
        for issue in issues:
            print(f"  - {issue}")
        print(
            "\nA drifted record means a lane report now describes text that is not "
            "shipping.\nResolve each one by re-screening it and recording an "
            "amendment in\ndocs/audits/procedure-verification/AUDIT_LEDGER.json with "
            "owner, rationale,\ncommit, expiry, and follow-up. Do not edit a baseline "
            "fingerprint: baselines\nare derived from the audited bytes and "
            "generate_audit_ledger.py --check will\nfail if one is changed by hand."
        )
        return 1

    print(
        "Verified nine fingerprinted audit reports with exactly one evidence-backed "
        "section for each of 55 procedures, and every audited record still matches "
        "the screened content."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
