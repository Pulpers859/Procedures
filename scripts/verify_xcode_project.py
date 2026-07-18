#!/usr/bin/env python3
"""Verify Swift file references, target membership, and declared XCTest count."""

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECT_FILE = ROOT / "Procedures.xcodeproj" / "project.pbxproj"
APP_ROOT = ROOT / "Procedures"
TEST_ROOT = ROOT / "ProceduresTests"
APP_SOURCES_PHASE_ID = "FEF171F812B64D1C8E68286D"
TEST_SOURCES_PHASE_ID = "7E5700000000000000000005"


def extract_sources_phase(project_text: str, phase_id: str) -> str:
    marker = f"{phase_id} /* Sources */ = {{"
    start = project_text.find(marker)
    if start < 0:
        return ""
    files_start = project_text.find("files = (", start)
    files_end = project_text.find(");", files_start)
    if files_start < 0 or files_end < 0:
        return ""
    return project_text[files_start:files_end]


def source_membership_issues(
    project_text: str,
    app_files: list[Path],
    test_files: list[Path],
) -> list[str]:
    issues = []
    all_files = app_files + test_files
    filenames = [path.name for path in all_files]
    duplicates = sorted({name for name in filenames if filenames.count(name) > 1})
    for filename in duplicates:
        issues.append(f"duplicate Swift filename cannot be verified safely: {filename}")

    app_phase = extract_sources_phase(project_text, APP_SOURCES_PHASE_ID)
    test_phase = extract_sources_phase(project_text, TEST_SOURCES_PHASE_ID)
    if not app_phase:
        issues.append("main app Sources build phase is missing or unreadable")
    if not test_phase:
        issues.append("test Sources build phase is missing or unreadable")

    for source_root, files, phase in (
        (APP_ROOT, app_files, app_phase),
        (TEST_ROOT, test_files, test_phase),
    ):
        for path in files:
            relative = str(path.relative_to(source_root)).replace("\\", "/")
            has_reference = f"path = {relative};" in project_text
            has_sources_entry = f"{path.name} in Sources */" in phase
            if not has_reference:
                issues.append(f"missing PBXFileReference: {path.relative_to(ROOT).as_posix()}")
            if not has_sources_entry:
                issues.append(f"missing target Sources membership: {path.relative_to(ROOT).as_posix()}")

    disk_names = set(filenames)
    for phase_name, phase in (("app", app_phase), ("test", test_phase)):
        for filename in re.findall(r"/\* (?:.*/)?([^/]+\.swift) in Sources \*/", phase):
            if filename not in disk_names:
                issues.append(f"dangling {phase_name} Sources membership: {filename}")

    return sorted(set(issues))


def discover_swift_files(source_root: Path) -> list[Path]:
    return sorted(source_root.rglob("*.swift"))


def declared_xctest_count(test_files: list[Path]) -> int:
    pattern = re.compile(r"^\s*func\s+(test[A-Za-z0-9_]*)\s*\(", re.MULTILINE)
    return sum(len(pattern.findall(path.read_text(encoding="utf-8"))) for path in test_files)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test-count-only",
        action="store_true",
        help="Print only the source-derived XCTest declaration count.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    app_files = discover_swift_files(APP_ROOT)
    test_files = discover_swift_files(TEST_ROOT)

    if args.test_count_only:
        print(declared_xctest_count(test_files))
        return 0

    project_text = PROJECT_FILE.read_text(encoding="utf-8")
    issues = source_membership_issues(project_text, app_files, test_files)
    if issues:
        print("Xcode project verification failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(
        f"Verified Xcode Sources membership for {len(app_files) + len(test_files)} Swift files "
        f"and found {declared_xctest_count(test_files)} XCTest declarations."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
