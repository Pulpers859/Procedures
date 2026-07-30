#!/usr/bin/env python3
"""Local authoring and release-readiness validation for Procedures.
Run from the project root:
    ./scripts/validate_procedures.py
    ./scripts/validate_procedures.py --release
"""
import argparse
import json
import re
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
# Mirror of ContentSource in ReviewerStatus.swift. Undeclared provenance is
# treated as "ai-draft" (the least trusted answer), and a clinically reviewed
# reviewerStatus on an item still marked "ai-draft" is a contradiction: a
# sign-off must update provenance.
CONTENT_SOURCES = {"ai-draft", "human-authored", "clinician-reviewed"}
AI_DRAFT_SOURCE = "ai-draft"
STALENESS_THRESHOLD_DAYS = 365


def review_age_days(last_reviewed):
    """Days since an ISO yyyy-MM-dd date, or None if it cannot be parsed."""
    try:
        reviewed = datetime.strptime(last_reviewed.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None
    return (date.today() - reviewed).days
RESOURCES = ROOT / "Procedures" / "Resources"


def _locate_asset_catalog():
    """Find Assets.xcassets wherever Xcode currently keeps it.

    Xcode relocates the catalog on its own — it moved from Procedures/ to the
    repo root without any source change — and a hardcoded path turns that into
    three "visual asset file not found" warnings on content nobody touched. The
    build was fine throughout; only this check was looking in the old place.
    """
    for candidate in (ROOT / "Procedures" / "Assets.xcassets", ROOT / "Assets.xcassets"):
        if candidate.is_dir():
            return candidate
    return ROOT / "Procedures" / "Assets.xcassets"


ASSET_CATALOG = _locate_asset_catalog()
PROCEDURES = RESOURCES / "procedures.json"
RESCUE_CARDS = RESOURCES / "rescue_cards.json"
KITS = RESOURCES / "kits.json"
SYNONYMS = RESOURCES / "synonyms.json"
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
# Enum cases the Swift models decode. A value outside these sets does not throw
# in Swift — FailableDecodable turns the whole record into nil and it silently
# disappears from the app — so the validator must reject them here instead.
VALID_SETTINGS = {"ED", "ICU", "Trauma", "Peds"}
VALID_ACUITIES = {"Crash", "Urgent", "Watch"}
VALID_VISUAL_KINDS = {"Landmark", "Probe Position", "Danger Zone", "Confirmation", "Setup"}
MINIMUM_TAGS = 5
RELEASE_REFERENCE_MARKERS = (
    "replace with formal reviewer-approved references before release",
    "standard emergency medicine regional anesthesia literature",
)
REGIONAL_CATEGORY = "Regional Anesthesia"
# Drug or drug-class words that must never appear in a Crash card's immediate
# moves without a number (dose, concentration, or rate) on the same line. A
# rescue card that says "give a vasopressor" without a dose is a reading
# assignment, not a rescue card.
CRASH_DRUG_KEYWORDS = (
    "vasopressor", "push-dose", "pressor", "lipid", "succinylcholine",
    "epinephrine", "norepinephrine", "naloxone", "flumazenil",
    "benzodiazepine", "midazolam", "ketamine", "propofol", "reversal",
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

    source = item.get("contentSource")
    if source is None:
        issues.append(("WARNING", title, "missing contentSource provenance; treated as 'ai-draft'"))
    elif source not in CONTENT_SOURCES:
        issues.append(("WARNING", title, f"unknown contentSource '{source}'"))
    if (source or AI_DRAFT_SOURCE) == AI_DRAFT_SOURCE and status in REVIEWED_STATUSES:
        issues.append((
            "BLOCKER", title,
            "reviewerStatus claims clinical review but contentSource is still 'ai-draft'; a sign-off must update provenance",
        ))
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
        # Every field the Swift model declares non-optional must be checked
        # here. Swift decodes each record through FailableDecodable, so a
        # missing or misspelled value does not throw — the record is silently
        # dropped from the app. Without these checks that loss ships green.
        for field in ["id", "title", "reviewTime", "lastReviewed", "version", "category", "difficulty"]:
            if not item.get(field):
                issues.append(("BLOCKER", title, f"missing metadata: {field}"))

        setting = item.get("setting")
        if not isinstance(setting, list) or not setting:
            issues.append(("BLOCKER", title, "missing or empty 'setting'; Swift drops the record"))
        else:
            bad_settings = [s for s in setting if s not in VALID_SETTINGS]
            if bad_settings:
                issues.append((
                    "BLOCKER", title,
                    f"invalid setting(s) {bad_settings}; expected from: {', '.join(sorted(VALID_SETTINGS))}",
                ))

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
            kind = visual.get("kind")
            if kind and kind not in VALID_VISUAL_KINDS:
                issues.append((
                    "BLOCKER", title,
                    f"invalid visual asset kind '{kind}'; Swift drops the whole procedure. "
                    f"Expected one of: {', '.join(sorted(VALID_VISUAL_KINDS))}",
                ))
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
        acuity = item.get("acuity")
        if acuity and acuity not in VALID_ACUITIES:
            issues.append((
                "BLOCKER", title,
                f"invalid acuity '{acuity}'; Swift drops the card and the Crash dose rule "
                f"silently stops applying. Expected one of: {', '.join(sorted(VALID_ACUITIES))}",
            ))
        if not isinstance(item.get("relatedProcedureIDs"), list):
            issues.append(("BLOCKER", title, "missing 'relatedProcedureIDs'; Swift drops the card"))
        missing = [pid for pid in item.get("relatedProcedureIDs", []) if pid not in procedure_ids]
        if missing:
            issues.append(("WARNING", title, f"related procedure IDs not found: {', '.join(missing)}"))
        issues.extend(governance_issues(title, item))
    return issues


MEDICATION_DOSE_UNITS = ("mg/kg", "mcg/kg")


def medication_dosing_issues(procedures):
    """Systemic medication doses (`medicationDosing`), as opposed to the local
    anesthetic ceilings in `dosing`.

    Everything here is a BLOCKER. These are target doses of induction agents
    and paralytics: a wrong unit is a 1000-fold error, an inverted range is
    unreadable at speed, and a block that names a paralytic without requiring
    an induction agent invites paralysis without anesthesia."""
    issues = []
    for item in procedures:
        block = item.get("medicationDosing")
        if block is None:
            continue
        title = item.get("title", item.get("id", "<missing id>"))
        if not isinstance(block, dict) or not block:
            issues.append(("BLOCKER", title, "medicationDosing is present but not a populated object"))
            continue

        for field in ("indication", "inductionRequirement", "sourceNote"):
            if not str(block.get(field) or "").strip():
                issues.append(("BLOCKER", title, f"medicationDosing is missing {field}"))

        medications = block.get("medications")
        if not isinstance(medications, list) or not medications:
            issues.append(("BLOCKER", title, "medicationDosing has no medications"))
            continue

        for entry in medications:
            if not isinstance(entry, dict):
                issues.append(("BLOCKER", title, "medicationDosing entry is malformed"))
                continue
            name = str(entry.get("medication") or "").strip()
            if not name:
                issues.append(("BLOCKER", title, "medicationDosing entry is missing a medication name"))
                continue
            if not str(entry.get("role") or "").strip():
                issues.append(("BLOCKER", title, f"medicationDosing '{name}' is missing a role"))

            unit = entry.get("unit")
            if unit not in MEDICATION_DOSE_UNITS:
                issues.append((
                    "BLOCKER", title,
                    f"medicationDosing '{name}' has unit {unit!r}; expected one of "
                    f"{', '.join(MEDICATION_DOSE_UNITS)}",
                ))

            low = entry.get("doseLowPerKg")
            if not isinstance(low, (int, float)) or isinstance(low, bool) or low <= 0:
                issues.append((
                    "BLOCKER", title,
                    f"medicationDosing '{name}' has an invalid doseLowPerKg: {low!r}",
                ))
                continue

            high = entry.get("doseHighPerKg")
            if high is None:
                continue
            if not isinstance(high, (int, float)) or isinstance(high, bool):
                issues.append((
                    "BLOCKER", title,
                    f"medicationDosing '{name}' has an invalid doseHighPerKg: {high!r}",
                ))
            elif high < low:
                issues.append((
                    "BLOCKER", title,
                    f"medicationDosing '{name}' range is inverted: {low} to {high} {unit}",
                ))
    return issues


def regional_dosing_issues(procedures, rescue_card_ids, level="WARNING"):
    """Structured max-dose data is mandatory for regional anesthesia: a block
    that states an injectate volume without a weight-based ceiling is a
    patient-safety defect. Missing/thin dosing is `level` (WARNING while
    authoring, BLOCKER for release); malformed structure and broken rescue
    linkage are always blockers. Mirrors ContentValidation.swift."""
    issues = []
    for item in procedures:
        if item.get("category") != REGIONAL_CATEGORY:
            continue
        title = item.get("title", item.get("id", "<missing id>"))
        dosing = item.get("dosing")
        if not isinstance(dosing, dict) or not dosing:
            issues.append((level, title, "regional anesthesia procedure is missing structured max-dose (dosing) data"))
            continue

        agents = dosing.get("agents")
        if not isinstance(agents, list) or not agents:
            issues.append(("BLOCKER", title, "dosing block has no agents; a max-dose section without agents is unusable"))
        else:
            for agent in agents:
                if not isinstance(agent, dict) or not str(agent.get("agent") or "").strip():
                    issues.append(("BLOCKER", title, "dosing agent entry is malformed (missing 'agent' name)"))
                    continue
                name = agent["agent"]
                max_dose = agent.get("maxDoseMgPerKg")
                if not isinstance(max_dose, (int, float)) or isinstance(max_dose, bool) or max_dose <= 0:
                    issues.append(("BLOCKER", title, f"dosing agent '{name}' has an invalid maxDoseMgPerKg: {max_dose!r}"))
                # The calculator divides the milligram ceiling by the strength
                # to print a volume, so a missing or nonsense percentage is not
                # a documentation gap — it is a wrong number of millilitres
                # drawn into a syringe. Blockers, all of them.
                if not isinstance(agent.get("withEpinephrine"), bool):
                    issues.append(("BLOCKER", title, f"dosing agent '{name}' is missing the withEpinephrine flag; the ceiling depends on it"))
                strengths = agent.get("concentrationsPercent")
                if not isinstance(strengths, list) or not strengths:
                    issues.append(("BLOCKER", title, f"dosing agent '{name}' has no concentrationsPercent; the card cannot convert mg to mL"))
                else:
                    for percent in strengths:
                        if not isinstance(percent, (int, float)) or isinstance(percent, bool) or not 0 < percent <= 100:
                            issues.append(("BLOCKER", title, f"dosing agent '{name}' has an invalid concentration percentage: {percent!r}"))

        if not str(dosing.get("cumulativeWarning") or "").strip():
            issues.append((level, title, "dosing block is missing a cumulative-dose warning"))
        monitoring = dosing.get("monitoring")
        if not isinstance(monitoring, list) or len(monitoring) < 2:
            issues.append((level, title, "dosing block needs at least 2 monitoring/LAST-preparation actions"))

        rescue_id = dosing.get("rescueCardID")
        if not rescue_id:
            issues.append((level, title, "dosing block is missing rescueCardID (LAST rescue linkage)"))
        elif rescue_id not in rescue_card_ids:
            issues.append(("BLOCKER", title, f"dosing rescueCardID '{rescue_id}' not found in rescue_cards.json"))
    return issues


# Weights the ceiling is checked against. Not clinical guidance — just the two
# reference bodyweights the corpus's own worked examples already use, so the
# comparison is against a number the record itself states.
REFERENCE_WEIGHTS_KG = (70, 50)

VOLUME_RANGE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:-|–|\s+to\s+)\s*(\d+(?:\.\d+)?)\s*mL\b", re.IGNORECASE)
SINGLE_VOLUME = re.compile(r"(?<![-–\d.])(\d+(?:\.\d+)?)\s*mL\b", re.IGNORECASE)
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def mg_per_ml(percent):
    """1% is 1 g per 100 mL, so 10 mg/mL. An identity, not a clinical claim.

    This used to be looked up in a per-record prose note listing the strengths
    someone remembered to write down. A strength the prose mentioned but the
    note omitted was silently skipped, which is the wrong direction to fail in
    a check that exists to catch overdoses.
    """
    return percent * 10


def _max_volume_ml(text):
    """Top of the largest volume the line recommends, or None."""
    volumes = [float(high) for _, high in VOLUME_RANGE.findall(text)]
    if not volumes:
        # Avoid double-counting the halves of a range already matched above.
        without_ranges = VOLUME_RANGE.sub(" ", text)
        volumes = [float(value) for value in SINGLE_VOLUME.findall(without_ranges)]
    return max(volumes) if volumes else None


def prose_dose_ceiling_issues(procedures, level="WARNING"):
    """Multiplies the volumes stated in prose by the concentrations the same
    record offers, and compares the result against that record's own ceiling.

    The structured `dosing` block is validated rigorously; the free-text
    `equipment` and `steps` beside it were validated only for length. Nothing
    connected the two, so a procedure could recommend a volume that, at the
    higher concentration named on the same line, exceeded the maximum stated a
    few fields away — and pass clean in both authoring and release mode.

    This invents no clinical guidance. Every number comes from the record: the
    volume and the strength from its prose, the ceiling from its own
    maxDoseMgPerKg and absoluteMaxMg. It reports an internal contradiction,
    which is a question for the clinical owner rather than something to
    auto-correct.

    A percentage on a line naming a non-anesthetic — a chlorhexidine prep, say
    — would be converted too. Nothing in the corpus does that today, and the
    result would be a warning for a human to dismiss rather than a number
    anyone acts on, which is the safe direction for this check to be wrong in.
    """
    issues = []
    for item in procedures:
        dosing = item.get("dosing")
        if not isinstance(dosing, dict):
            continue
        agents = dosing.get("agents")
        if not isinstance(agents, list) or not agents:
            continue
        title = item.get("title", item.get("id", "<missing id>"))
        sections = item.get("sections") or {}

        for field in ("equipment", "steps"):
            for line in sections.get(field) or []:
                text = str(line)
                percents = [float(value) for value in PERCENT.findall(text)]
                volume = _max_volume_ml(text)
                if volume is None or not percents:
                    continue
                # The strongest concentration the line itself offers.
                strength = max(percents)
                milligrams = volume * mg_per_ml(strength)

                for agent in agents:
                    if not isinstance(agent, dict):
                        continue
                    per_kg = agent.get("maxDoseMgPerKg")
                    if not isinstance(per_kg, (int, float)) or isinstance(per_kg, bool):
                        continue
                    name = agent.get("agent", "<unnamed>")
                    # Only compare against an agent the line actually names.
                    stem = str(name).split()[0].lower()
                    if stem and stem not in text.lower():
                        continue
                    for weight in REFERENCE_WEIGHTS_KG:
                        ceiling = per_kg * weight
                        absolute = agent.get("absoluteMaxMg")
                        if isinstance(absolute, (int, float)) and not isinstance(absolute, bool):
                            ceiling = min(ceiling, float(absolute))
                        if milligrams > ceiling:
                            issues.append((
                                level, title,
                                f"{field}: '{text[:70]}' — {volume:g} mL at {strength:g}% is "
                                f"{milligrams:g} mg, above this procedure's own ceiling for "
                                f"{name} ({per_kg:g} mg/kg = {ceiling:g} mg at {weight} kg). "
                                f"Internal contradiction; needs clinician review."
                            ))
                            break
    return issues


LOCAL_ANESTHETIC_AGENTS = (
    "lidocaine", "bupivacaine", "ropivacaine", "articaine",
    "mepivacaine", "chloroprocaine", "prilocaine", "procaine",
)
ANESTHETIC_MENTION = re.compile(r"an[ae]sthetic", re.IGNORECASE)


def uncomputable_injectate_issues(procedures, level="WARNING"):
    """Flags an injectate volume the reader cannot convert to milligrams.

    A line reading "Local anesthetic (20-30 mL)" on a procedure whose dosing
    table lists two agents with different ceilings is 50-75 mg as 0.25%
    bupivacaine or 200-300 mg as 1% lidocaine — a fourfold spread the reader
    has to close from memory, in the section whose entire purpose is not making
    them do that.

    Structural only: it asks whether the record names an agent beside the
    volume, not whether the volume is right.
    """
    issues = []
    for item in procedures:
        if not isinstance(item.get("dosing"), dict):
            continue
        sections = item.get("sections") or {}
        lines = [str(line) for field in ("equipment", "steps") for line in sections.get(field) or []]

        # Reported once per procedure, not once per line. The question is
        # whether the record ever says what the drug is — a steps line that
        # omits it is fine when the equipment line names it, and flagging both
        # turns one answerable question into thirty.
        offending = [
            text for text in lines
            if ANESTHETIC_MENTION.search(text)
            and _max_volume_ml(text) is not None
            and not any(agent in text.lower() for agent in LOCAL_ANESTHETIC_AGENTS)
            and not PERCENT.search(text)
        ]
        if not offending:
            continue
        names_agent_somewhere = any(
            any(agent in text.lower() for agent in LOCAL_ANESTHETIC_AGENTS) and PERCENT.search(text)
            for text in lines
        )
        if names_agent_somewhere:
            continue

        title = item.get("title", item.get("id", "<missing id>"))
        issues.append((
            level, title,
            f"states an injectate volume ({offending[0][:52]}) but never names an agent "
            f"with a concentration in equipment or steps, so the volume cannot be "
            f"converted to mg against this procedure's own ceiling"
        ))
    return issues


def unbounded_agent_issues(procedures, level="WARNING"):
    """Flags an agent the prose tells you to use that has no stated maximum.

    `block_inferior_alveolar` offers "lidocaine/articaine" and its dosing table
    has no articaine entry — anywhere in the file. A drug the procedure names
    with no ceiling is the gap the structured dosing block exists to close.
    """
    issues = []
    for item in procedures:
        dosing = item.get("dosing")
        if not isinstance(dosing, dict):
            continue
        title = item.get("title", item.get("id", "<missing id>"))
        listed = " ".join(
            str(agent.get("agent") or "")
            for agent in dosing.get("agents") or []
            if isinstance(agent, dict)
        ).lower()
        sections = item.get("sections") or {}
        prose = " ".join(
            list(sections.get("equipment") or []) + list(sections.get("steps") or [])
        ).lower()
        for agent in LOCAL_ANESTHETIC_AGENTS:
            if agent in prose and agent not in listed:
                issues.append((
                    level, title,
                    f"names '{agent}' in equipment/steps but has no maxDoseMgPerKg "
                    f"entry for it, so the procedure states no ceiling for a drug it "
                    f"tells you to use"
                ))
    return issues


def crash_card_dose_issues(cards, level="WARNING"):
    """Every Crash-acuity immediate move naming a drug or drug class must carry
    a number on the same line (dose, concentration, mL, rate, or mg/kg)."""
    issues = []
    for card in cards:
        if card.get("acuity") != "Crash":
            continue
        title = card.get("title", card.get("id", "<missing id>"))
        for line in card.get("immediateMoves", []):
            if not isinstance(line, str):
                continue
            lowered = line.lower()
            if any(keyword in lowered for keyword in CRASH_DRUG_KEYWORDS) and not any(ch.isdigit() for ch in line):
                issues.append((level, title, f"Crash card names a drug/class without a dose: '{line[:70]}'"))
    return issues


def synonym_map_issues(synonyms):
    """The clinical-shorthand synonym map is content, not code, so it is
    validated like content. Search lowercases every query token, so keys and
    terms must be lowercase or they can never match; a malformed map would
    silently degrade bedside search. Mirrors ClinicalSynonyms in
    ProcedureRepository.swift."""
    issues = []
    if not isinstance(synonyms, dict) or not synonyms:
        issues.append(("BLOCKER", "synonyms.json", "synonym map must be a nonempty JSON object"))
        return issues
    for key, terms in synonyms.items():
        if not key or key != key.lower() or any(ch.isspace() for ch in key):
            issues.append(("BLOCKER", "synonyms.json", f"key must be lowercase with no whitespace: {key!r}"))
        if not isinstance(terms, list) or not terms:
            issues.append(("BLOCKER", "synonyms.json", f"'{key}' must map to a nonempty list of terms"))
            continue
        for term in terms:
            if not isinstance(term, str) or not term or term != term.lower():
                issues.append(("BLOCKER", "synonyms.json", f"'{key}' has a non-lowercase or empty term: {term!r}"))
        if key in terms:
            issues.append(("WARNING", "synonyms.json", f"'{key}' lists itself as a synonym; redundant"))

    resources_phase = resources_phase_text()
    if resources_phase and "Resources/synonyms.json in Resources */" not in resources_phase:
        issues.append((
            "BLOCKER", "synonyms.json",
            "not in the app target's Copy Bundle Resources phase; shorthand search would silently degrade",
        ))
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

        kit_category = item.get("category")
        if kit_category and kit_category not in VALID_CATEGORIES:
            issues.append((
                "BLOCKER", title,
                f"invalid kit category '{kit_category}'; Swift drops the kit. "
                f"Expected one of: {', '.join(sorted(VALID_CATEGORIES))}",
            ))

        # Non-optional in the Swift Kit model: absent means the kit is dropped.
        for field in ["outsideKit", "commonlyForgotten", "sterileSetup", "backupEquipment", "relatedProcedureIDs"]:
            if not isinstance(item.get(field), list):
                issues.append(("BLOCKER", title, f"missing list '{field}'; Swift drops the kit"))

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

            if item.get("contentSource") not in CONTENT_SOURCES:
                issues.append((
                    "BLOCKER",
                    title,
                    f"release requires declared content provenance (contentSource) for this {kind}",
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
                # Not a blocker since 2026-07-30, by owner decision. A
                # placeholder falls back to the asset's SF Symbol and the card
                # still reads correctly, so pending artwork is a feature in
                # progress rather than a defect in the text. See
                # docs/ai-instructions/SAFETY_AND_REVIEW_POLICY.md.
                issues.append((
                    "WARNING",
                    title,
                    f"visual asset '{visual_id}' has no bundled artwork yet; the card falls back to its SF Symbol",
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

    # Dosing-safety rules warn during authoring and become stop-ship in
    # release mode; structural corruption inside them is always a blocker.
    dosing_level = "BLOCKER" if release else "WARNING"
    rescue_card_ids = {item.get("id") for item in rescue_cards}
    issues.extend(medication_dosing_issues(procedures))
    issues.extend(regional_dosing_issues(procedures, rescue_card_ids, level=dosing_level))
    issues.extend(crash_card_dose_issues(rescue_cards, level=dosing_level))
    issues.extend(prose_dose_ceiling_issues(procedures, level=dosing_level))
    issues.extend(uncomputable_injectate_issues(procedures, level=dosing_level))
    issues.extend(unbounded_agent_issues(procedures, level=dosing_level))

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
    synonyms = load_json(SYNONYMS)
    if procedures is None or rescue_cards is None or kits_data is None or synonyms is None:
        return 1

    issues = collect_issues(procedures, rescue_cards, kits_data, release=args.release)
    issues.extend(synonym_map_issues(synonyms))

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
