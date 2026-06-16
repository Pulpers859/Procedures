# XCTest Guide

## What XCTest is

XCTest is Apple's built-in testing framework for Xcode projects.

For Procedures, XCTest automatically checks that important non-visual app behavior still works after code or content changes.

## What we test here

The current target is `ProceduresTests`.

It covers:

- bundled `procedures.json` decoding
- bundled `rescue_cards.json` decoding
- no validation blockers in shipped content
- required procedure sections are present
- rescue-card related procedure IDs point to real procedures
- procedure and rescue-card search shorthand still works
- validator rules catch bad synthetic fixtures

This is the right level of testing for the current app because the app depends heavily on structured local JSON, search, and validation logic.

## What XCTest does not replace

XCTest does not fully answer:

- Does the screen look good?
- Is the navigation comfortable?
- Does the layout behave well on every device size?
- Is the clinical workflow fast enough at the bedside?

Those still need simulator checks and human review.

## How to run tests in Xcode

1. Open `Procedures.xcodeproj`.
2. Select the `Procedures` scheme near the top of Xcode.
3. Select an iPhone simulator.
4. Press `Command-U`.

You can also use:

`Product > Test`

When tests pass, Xcode shows green checkmarks in the test navigator.

When a test fails, Xcode shows the failed test name and a message explaining what was expected.

## How to run tests from Terminal on macOS

From the repo root:

```bash
xcodebuild test -project Procedures.xcodeproj -scheme Procedures -destination 'platform=iOS Simulator,name=iPhone 16'
```

If `iPhone 16` is not installed, use any simulator name available in Xcode.

To list available simulators:

```bash
xcrun simctl list devices available
```

## How to think about failures

If a decoding test fails:

- check the JSON file first
- look for missing keys, spelling mistakes, or schema drift
- run `python scripts/validate_procedures.py`

If a search test fails:

- check `ClinicalSynonyms`
- check search scoring or rescue-card matching
- make sure shorthand like `ETT`, `LP`, `TVP`, and `cric` still maps to useful results

If a validation test fails:

- check `ContentValidator`
- decide whether the validation rule or the test expectation changed

## When to add more tests

Add XCTest coverage when:

- a bug is fixed and could come back
- content schema changes
- search behavior changes
- validation rules change
- persistence or migration logic changes

Do not add XCTest just to prove a button is visually polished. Use simulator/manual checks for that.
