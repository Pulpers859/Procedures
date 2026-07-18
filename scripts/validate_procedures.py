#!/usr/bin/env python3
"""Local authoring and release-readiness validation for Procedures.
Run from the project root:
    ./scripts/validate_procedures.py
    ./scripts/validate_procedures.py --release
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
PROJECT_FILE = ROOT / "Procedures.xcodeproj" / "project.pbxproj"

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
ASSET_CATALOG = ROOT / "Procedures" / "Assets.xcassets"
PROCEDURES = RESOURCES / "procedures.json"
RESCUE_CARDS = RESOURCES / "rescue_cards.json"
KITS = RESOURCES / "kits.json"
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
RELEASE_REFERENCE_MARKERS = (
    "replace with formal reviewer-approved references before release",
    "standard emergency medicine regional anesthesia literature",
)


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


def image_file_is_valid(path: Path) -> bool:
    """Require Pillow to verify the container and fully decode pixel data."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            return image.width > 0 and image.height > 0
    except (OSError, UnidentifiedImageError, ValueError):
        return False


def resources_phase_text() -> str:
    try:
        project_text = PROJECT_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""
    marker = "/* Begin PBXResourcesBuildPhase section */"
    start = project_text.find(marker)
    end = project_text.find("/* End PBXResourcesBuildPhase section */", start)
    return project_text[start:end] if start >= 0 and end >= 0 else ""


def visual_asset_exists(asset_name: str) -> bool:
    """Require a valid image that the app target actually bundles."""
    if not isinstance(asset_name, str) or not asset_name.strip():
        return False
    asset_name = asset_name.strip()
    asset_path = Path(asset_name)
    if asset_path.is_absolute() or asset_name in {".", ".."} or ".." in asset_path.parts:
        return False
    stem = asset_path.stem if asset_path.suffix else asset_name
    extensions = [asset_path.suffix.lstrip(".")] if asset_path.suffix else ["png", "jpg", "jpeg"]
    if any(extension.lower() not in {"png", "jpg", "jpeg"} for extension in extensions):
        return False

    candidate_roots = [RESOURCES, RESOURCES / "Visuals"]
    candidates = []
    for root in candidate_roots:
        candidates.append(root / asset_name)
        candidates.extend(root / f"{asset_name}.{ext}" for ext in extensions if not asset_path.suffix)
    resource_phase = resources_phase_text()
    for path in candidates:
        if image_file_is_valid(path):
            relative = path.relative_to(ROOT / "Procedures").as_posix()
            if f"{relative} in Resources */" in resource_phase:
                return True

    image_set = ASSET_CATALOG / f"{stem}.imageset"
    if not image_set.is_dir() or "Assets.xcassets in Resources */" not in resource_phase:
        return False

    contents = image_set / "Contents.json"
    if contents.exists():
        try:
            metadata = json.loads(contents.read_text())
            for image in metadata.get("images", []):
                filename = image.get("filename")
                if filename and image_file_is_valid(image_set / filename):
                    return True
        except json.JSONDecodeError:
            pass

    return any(image_file_is_valid(image_set / f"{stem}.{ext}") for ext in extensions)


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

        # The equipment checklist keys persisted checked-state on the item string,
        # so duplicate strings would toggle together and collide in the UI list.
        equipment = sections.get("equipment", [])
        if isinstance(equipment, list):
            dupes = sorted({x for x in equipment if equipment.count(x) > 1})
            if dupes:
                issues.append(("WARNING", title, f"duplicate equipment items collide in the checklist: {', '.join(dupes)}"))

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
                if not visual_asset_exists(asset_name):
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


KIT_REQUIRED_FIELDS = ["id", "title", "subtitle", "category", "lastReviewed", "version"]
KIT_REQUIRED_LISTS = ["inKit", "patientSetup", "references", "tags"]


def validate_kits(kits, procedure_ids):
    issues = []

    if not kits:
        return issues

    ids = [item.get("id") for item in kits]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    for duplicate_id in duplicate_ids:
        issues.append(("BLOCKER", duplicate_id, "duplicate kit id"))

    for item in kits:
        kid = item.get("id", "<missing id>")
        title = item.get("title", kid)

        for field in KIT_REQUIRED_FIELDS:
            if not item.get(field):
                issues.append(("BLOCKER", title, f"missing metadata: {field}"))

        for field in KIT_REQUIRED_LISTS:
            val = item.get(field)
            if not isinstance(val, list) or not val:
                issues.append(("BLOCKER" if field in {"inKit", "references"} else "WARNING", title, f"missing or empty list: {field}"))

        missing = [pid for pid in item.get("relatedProcedureIDs", []) if pid not in procedure_ids]
        if missing:
            issues.append(("WARNING", title, f"related procedure IDs not found: {', '.join(missing)}"))

        # The room-setup checklist keys checked-state on the item string across
        # inKit + outsideKit combined; a duplicate would toggle in two places.
        checklist = (item.get("inKit") or []) + (item.get("outsideKit") or [])
        dupes = sorted({x for x in checklist if checklist.count(x) > 1})
        if dupes:
            issues.append(("WARNING", title, f"duplicate checklist items collide between inKit/outsideKit: {', '.join(dupes)}"))

        issues.extend(governance_issues(title, item))

    return issues


def release_readiness_issues(procedures, rescue_cards, kits):
    """Hard gates that apply only to a release candidate, not authoring work."""
    issues = []
    content_groups = (
        ("procedure", procedures),
        ("rescue card", rescue_cards),
        ("kit", kits),
    )

    for kind, items in content_groups:
        for item in items:
            title = item.get("title", item.get("id", f"<missing {kind} id>"))
            status = item.get("reviewerStatus")
            if status not in REVIEWED_STATUSES:
                issues.append((
                    "BLOCKER",
                    title,
                    f"release requires a clinically reviewed reviewerStatus for this {kind}; found '{status or 'missing'}'",
                ))

            if kind == "procedure":
                references = item.get("sections", {}).get("references", [])
            else:
                references = item.get("references", [])

            if not isinstance(references, list) or not references:
                issues.append((
                    "BLOCKER",
                    title,
                    "release requires at least one traceable reviewer-approved reference",
                ))
            for reference in references if isinstance(references, list) else []:
                if not isinstance(reference, str) or not reference.strip():
                    issues.append((
                        "BLOCKER",
                        title,
                        "release references must be nonblank strings",
                    ))
                    break
                normalized = reference.strip().lower()
                if any(marker in normalized for marker in RELEASE_REFERENCE_MARKERS):
                    issues.append((
                        "BLOCKER",
                        title,
                        "release requires traceable reviewer-approved references; placeholder or generic reference found",
                    ))
                    break

    for procedure in procedures:
        title = procedure.get("title", procedure.get("id", "<missing procedure id>"))
        for visual in procedure.get("visualAssets", []):
            visual_id = visual.get("id", "<missing visual id>")
            asset_name = visual.get("assetName")
            if not isinstance(asset_name, str) or not asset_name.strip():
                issues.append((
                    "BLOCKER",
                    title,
                    f"release requires bundled artwork for declared visual asset '{visual_id}'",
                ))
            elif not visual_asset_exists(asset_name):
                issues.append((
                    "BLOCKER",
                    title,
                    f"release visual asset '{visual_id}' is not present in the app bundle: {asset_name}",
                ))

    return issues


def collect_issues(procedures, rescue_cards, kits, release=False):
    issues = []
    issues.extend(validate_procedures(procedures))
    procedure_ids = {item.get("id") for item in procedures}
    issues.extend(validate_rescue_cards(rescue_cards, procedure_ids))
    issues.extend(validate_rescue_coverage(procedures, rescue_cards))
    issues.extend(validate_kits(kits, procedure_ids))
    if release:
        issues.extend(release_readiness_issues(procedures, rescue_cards, kits))
    return issues


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release",
        action="store_true",
        help="Apply stop-ship clinical review, provenance, and visual-asset gates.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    procedures = load_json(PROCEDURES)
    rescue_cards = load_json(RESCUE_CARDS)
    kits_data = load_json(KITS)
    if procedures is None or rescue_cards is None or kits_data is None:
        return 1

    issues = collect_issues(procedures, rescue_cards, kits_data, release=args.release)

    severity_order = {"BLOCKER": 0, "WARNING": 1, "POLISH": 2}
    issues.sort(key=lambda issue: (severity_order.get(issue[0], 99), issue[1], issue[2]))

    blockers = [issue for issue in issues if issue[0] == "BLOCKER"]
    for level, title, message in issues:
        print(f"{level}: {title}: {message}")

    total_items = len(procedures) + len(rescue_cards) + len(kits_data)
    reviewed = sum(
        1 for item in (procedures + rescue_cards + kits_data)
        if item.get("reviewerStatus") in REVIEWED_STATUSES
    )
    print(
        f"\nValidated {len(procedures)} procedures, {len(rescue_cards)} rescue cards, "
        f"and {len(kits_data)} kits. "
        f"Mode: {'release' if args.release else 'authoring'}. "
        f"Blockers: {len(blockers)}. Total issues: {len(issues)}. "
        f"Clinically reviewed: {reviewed}/{total_items}."
    )
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
