#!/usr/bin/env python3
"""Guards the single source of truth for review state.

The app once kept two unrelated answers to "has this been reviewed?" — the
`reviewerStatus` bundled with the content, and the clinician's own sign-off
stored on the device. Bedside screens read the first, the Review Center read the
second, and neither knew about the other. Marking a procedure reviewed changed
one screen while its own detail page went on announcing "DRAFT — not clinically
reviewed" to the person who had just reviewed it.

That was fixed by routing every surface through `ReviewState`, but the fix is
one careless line from coming back: any new view can reach for
`procedure.reviewer.isClinicallyReviewed` and silently reintroduce a screen that
does not know about local reviews. Nothing would fail. The screen would just be
wrong, in the quietest possible way.

So this makes it fail. Run from CI alongside the other validators.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "Procedures"

# `isClinicallyReviewed` asks only what shipped. It is legitimate in exactly
# four places, and reaching for it anywhere else is the bug this script exists
# to catch.
CLINICAL_FLAG_ALLOWLIST = {
    # Defines it.
    "Models/ReviewerStatus.swift",
    # The one place the bundled status and the local record are reconciled.
    "Models/ReviewState.swift",
    # Validates the repo's own content, where the local device is irrelevant.
    "Models/ContentValidation.swift",
    # The governance panel, which deliberately discloses the *source* status
    # separately from the reader's review. It receives it as a parameter.
    "Components/SectionCard.swift",
}

# Observable stores held without a property wrapper compile fine and never
# re-render, which is the other way a screen goes stale: it reads the right
# value once and then never hears that it changed.
OBSERVED_STORES = ("UserDataStore", "ProcedureEditStore", "ProcedureRepository")
PROPERTY_WRAPPERS = ("@EnvironmentObject", "@ObservedObject", "@StateObject", "@Environment")

UI_DIRECTORIES = ("Views", "Components")

# This app has one user. Telling them a review was theirs is text they have to
# read to learn nothing — "Reviewed by you" where "Reviewed" says the same
# thing. The phrasing is easy to reintroduce without noticing, so it is caught
# here rather than left to review.
ATTRIBUTION_PHRASES = (
    "by you",
    "your review",
    "your edits",
    "your own review",
    "you have signed",
    "you flagged",
    "you signed off",
    "you set aside",
    "you reviewed",
    "my review",
    "my edits",
    "my reviews",
)
STRING_LITERAL = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')

CLINICAL_FLAG = re.compile(r"\bisClinicallyReviewed\b")
BUNDLED_REVIEWER = re.compile(r"\.reviewer\b")
STORED_STORE = re.compile(
    r"^\s*(?:private\s+|fileprivate\s+|internal\s+)?(?:let|var)\s+\w+\s*:\s*(" + "|".join(OBSERVED_STORES) + r")\b"
)


def _is_ui_file(relative: Path) -> bool:
    return relative.parts and relative.parts[0] in UI_DIRECTORIES


def _strip_comment(line: str) -> str:
    """Drops `//` comments so prose explaining the rule cannot trip it."""
    index = line.find("//")
    return line if index == -1 else line[:index]


def check(app_root: Path = APP) -> list[str]:
    failures: list[str] = []

    for path in sorted(app_root.rglob("*.swift")):
        relative = path.relative_to(app_root)
        key = relative.as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()

        for number, raw in enumerate(lines, start=1):
            line = _strip_comment(raw)
            location = f"{key}:{number}"

            if CLINICAL_FLAG.search(line) and key not in CLINICAL_FLAG_ALLOWLIST:
                failures.append(
                    f"{location}: reads `isClinicallyReviewed`, which knows only what shipped "
                    f"and not what the reader signed off. Use UserDataStore.reviewState(for:)."
                )

            if _is_ui_file(relative) and BUNDLED_REVIEWER.search(line) and "sourceStatus:" not in line:
                failures.append(
                    f"{location}: reads the bundled `.reviewer` directly. Only the governance "
                    f"panel may do that, by passing it as `sourceStatus:`."
                )

            for literal in STRING_LITERAL.findall(line):
                lowered = literal.lower()
                for phrase in ATTRIBUTION_PHRASES:
                    if phrase in lowered:
                        failures.append(
                            f'{location}: user-facing text says "{literal}". This app has one '
                            f'user; a review reads "Reviewed", not who reviewed it.'
                        )
                        break

            match = STORED_STORE.match(line)
            if _is_ui_file(relative) and match and not any(w in raw for w in PROPERTY_WRAPPERS):
                failures.append(
                    f"{location}: holds {match.group(1)} without an observation wrapper, so this "
                    f"view will not re-render when a review is recorded."
                )

    return failures


def main() -> int:
    failures = check()
    if failures:
        print("Review state must have exactly one source. Found:\n")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Review state sources verified: every UI surface routes through ReviewState.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
