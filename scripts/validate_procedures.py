#!/usr/bin/env python3
"""Lightweight local content validation for Procedures.
Run from the project root:
    ./scripts/validate_procedures.py
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Mirror of ReviewerStatus.swift and ContentFreshness.swift. Keep these in sync
# so the Python validator and the in-app validator agree on governance rules.
REVIEWER_STATUSES = {
    "Draft",
    "Needs Clinical Review",
    "Internally Reviewed",
    "Externally Reviewed",
    "Institution-Specific",
}
REVIEWED_STATUSES = {"Internally Reviewed", "Externally Reviewed", "Institution-Specific"}
STALENESS_THRESHOLD_DAYS = 365


def review_age_days(last_reviewed):
    """Days since an ISO yyyy-MM-dd date, or None if it cannot be parsed."""
    try:
        reviewed = datetime.strptime(last_reviewed.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None
    return (date.today() - reviewed).days
RESOURCES = ROOT / "Procedures" / "Resources"
PROCEDURES = RESOURCES / "procedures.json"
RESCUE_CARDS = RESOURCES / "rescue_cards.json"
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
VALID_CATEGORIES = {
    "Airway", "Vascular Access", "Thoracic", "Cardiac / Resuscitation",
    "Neuro", "Regional Anesthesia", "Wound / Soft Tissue",
    "Ultrasound-Guided", "Sedation & Analgesia", "Other",
}
VALID_DIFFICULTIES = {"Basic", "Intermediate", "Advanced", "Rare-Crash"}
MINIMUM_TAGS = 5


def governance_issues(title, item):
    """Reviewer-status validity and last-reviewed aging, shared by both content
    types. An unparseable date is a blocker; staleness is a warning; an invalid
    or missing reviewer status is a warning."""
    issues = []
    last_reviewed = item.get("lastReviewed")
    if last_reviewed:
        age = review_age_days(last_reviewed)
        if age is None:
            issues.append(("BLOCKER", title, f"lastReviewed '{last_reviewed}' is not a valid yyyy-MM-dd date"))
        elif age > STALENESS_THRESHOLD_DAYS:
            issues.append(("WARNING", title, f"stale content: last reviewed {age} days ago (threshold {STALENESS_THRESHOLD_DAYS})"))

    status = item.get("reviewerStatus")
    if status is None:
        issues.append(("WARNING", title, "missing reviewerStatus; treated as 'Needs Clinical Review'"))
    elif status not in REVIEWER_STATUSES:
        issues.append(("WARNING", title, f"unknown reviewerStatus '{status}'"))
    return issues


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        print(f"BLOCKER: missing file: {path}")
        return None
    except json.JSONDecodeError as exc:
        print(f"BLOCKER: invalid JSON in {path}: {exc}")
        return None


def validate_procedures(data):
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

        category = item.get("category")
        if category and category not in VALID_CATEGORIES:
            issues.append(("BLOCKER", title, f"invalid category '{category}'; expected one of: {', '.join(sorted(VALID_CATEGORIES))}"))

        difficulty = item.get("difficulty")
        if difficulty and difficulty not in VALID_DIFFICULTIES:
            issues.append(("BLOCKER", title, f"invalid difficulty '{difficulty}'; expected one of: {', '.join(sorted(VALID_DIFFICULTIES))}"))

        tags = item.get("tags", [])
        if len(tags) < MINIMUM_TAGS:
            issues.append(("WARNING", title, f"only {len(tags)} search tags; target at least {MINIMUM_TAGS} for clinical shorthand discoverability"))

        issues.extend(governance_issues(title, item))

        # Visual assets are an optional enhancement, shown only when a real
        # image is bundled. Validate structure when present, but do not flag
        # their absence or pending artwork as content issues.
        for visual in item.get("visualAssets", []):
            for field in ["id", "kind", "title", "subtitle", "caption"]:
                if not visual.get(field):
                    issues.append(("WARNING", title, f"visual asset missing {field}"))
            asset_name = visual.get("assetName")
            if asset_name:
                candidates = [
                    RESOURCES / asset_name,
                    RESOURCES / f"{asset_name}.png",
                    RESOURCES / f"{asset_name}.jpg",
                    RESOURCES / f"{asset_name}.jpeg",
                ]
                if not any(path.exists() for path in candidates):
                    issues.append(("WARNING", title, f"visual asset file not found: {asset_name}"))

    return issues


def validate_rescue_cards(cards, procedure_ids):
    issues = []
    ids = [item.get("id") for item in cards]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    for duplicate_id in duplicate_ids:
        issues.append(("BLOCKER", duplicate_id, "duplicate rescue card id"))

    for item in cards:
        rid = item.get("id", "<missing id>")
        title = item.get("title", rid)
        for field in ["id", "title", "acuity", "lastReviewed", "version"]:
            if not item.get(field):
                issues.append(("BLOCKER", title, f"missing metadata: {field}"))
        for field in ["trigger", "immediateMoves", "reassess", "avoid", "tags", "references"]:
            if not isinstance(item.get(field), list) or not item.get(field):
                issues.append(("BLOCKER" if field in {"trigger", "immediateMoves", "references"} else "WARNING", title, f"missing or empty list: {field}"))
        if len(item.get("immediateMoves", [])) < 3:
            issues.append(("BLOCKER", title, "rescue card needs at least 3 immediate moves"))
        missing = [pid for pid in item.get("relatedProcedureIDs", []) if pid not in procedure_ids]
        if missing:
            issues.append(("WARNING", title, f"related procedure IDs not found: {', '.join(missing)}"))
        issues.extend(governance_issues(title, item))
    return issues


def validate_rescue_coverage(procedures, rescue_cards):
    """Flag procedures that have no rescue card coverage, especially high-risk ones."""
    issues = []
    covered_ids = set()
    for card in rescue_cards:
        covered_ids.update(card.get("relatedProcedureIDs", []))

    high_risk = {"Advanced", "Rare-Crash"}
    for proc in procedures:
        pid = proc.get("id", "<missing>")
        title = proc.get("title", pid)
        difficulty = proc.get("difficulty", "")
        if pid not in covered_ids:
            if difficulty in high_risk:
                issues.append(("WARNING", title, f"high-risk procedure ({difficulty}) has no rescue card coverage"))
            else:
                issues.append(("POLISH", title, "no rescue card coverage"))
    return issues


def main() -> int:
    procedures = load_json(PROCEDURES)
    rescue_cards = load_json(RESCUE_CARDS)
    if procedures is None or rescue_cards is None:
        return 1

    issues = []
    issues.extend(validate_procedures(procedures))
    procedure_ids = {item.get("id") for item in procedures}
    issues.extend(validate_rescue_cards(rescue_cards, procedure_ids))
    issues.extend(validate_rescue_coverage(procedures, rescue_cards))

    severity_order = {"BLOCKER": 0, "WARNING": 1, "POLISH": 2}
    issues.sort(key=lambda issue: (severity_order.get(issue[0], 99), issue[1], issue[2]))

    blockers = [issue for issue in issues if issue[0] == "BLOCKER"]
    for level, title, message in issues:
        print(f"{level}: {title}: {message}")

    total_items = len(procedures) + len(rescue_cards)
    reviewed = sum(
        1 for item in (procedures + rescue_cards)
        if item.get("reviewerStatus") in REVIEWED_STATUSES
    )
    print(
        f"\nValidated {len(procedures)} procedures and {len(rescue_cards)} rescue cards. "
        f"Blockers: {len(blockers)}. Total issues: {len(issues)}. "
        f"Clinically reviewed: {reviewed}/{total_items}."
    )
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
