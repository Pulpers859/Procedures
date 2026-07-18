# Automated Testing Handoff

## Repository Profile

- Project type: Xcode iOS app.
- Project: `Procedures.xcodeproj`.
- Shared scheme: `Procedures`.
- Test target: `ProceduresTests`.
- Automation profile: `.swift-automation.json`.
- Physical-device validation remains required for release acceptance.

## Deterministic Workflows

### Content authoring

`.github/workflows/validate-content.yml` runs on pushes and pull requests. It:

1. Installs the pinned image-validation dependency and runs Python negative-control tests.
2. Runs permissive authoring validation.

### iOS build and XCTest

`.github/workflows/ios-tests.yml` dynamically selects an available iPhone
simulator by UDID, runs the shared scheme, requires the executed XCTest count to
exactly match the 30 source declarations, builds the Release configuration, and
retains logs plus the `.xcresult` bundle.

### Release readiness

`.github/workflows/release-readiness.yml` runs manually and for `v*` tags. It
executes the strict clinical release gate. The current corpus is expected to fail
until qualified review and final visual integration are complete.

## Local Windows Evidence

Windows can prove:

- Python validator tests.
- Xcode project source membership.
- JSON authoring validation.
- Expected failure of strict release validation for the unreviewed corpus.
- Framework-light Swift syntax checks where supported.

Windows cannot prove Xcode compilation, simulator XCTest execution, SwiftUI
behavior, VoiceOver order, haptics, or physical-device behavior.

## Required Commands

```text
python -m pip install -r scripts/requirements-validation.txt
python -m unittest discover -s scripts/tests -p "test_*.py"
python scripts/verify_xcode_project.py
python scripts/validate_procedures.py
python scripts/validate_procedures.py --release
```

The first four commands must pass during authoring. The fifth must fail today
and must pass before a release candidate is promoted.

## Secrets and Live Services

No secrets, paid AI calls, network fixtures, patient data, prompts, or model
responses are used by deterministic CI. There are no live-AI test surfaces.

## Evidence Still Required

- Physical-device offline, migration, accessibility, and bedside scenario runs.
- Named clinical owner and signed release corpus.

## Latest Automated Evidence

- Commit: `4a731bc`.
- Content validation: GitHub run `29632640552`, passed.
- Xcode build, exact XCTest count, and Release build: GitHub run
  `29632640535`, passed.
- Retained artifact: `procedures-xcode-evidence-29632640535`, expires
  2026-08-01.
