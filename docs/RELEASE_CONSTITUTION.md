# Procedures Release Constitution

This document defines who may promote Procedures and what evidence must exist
before a build is treated as a clinical release candidate.

## Authority

- Release owner: Patrick, repository owner.
- Clinical owner: unassigned.
- Current release state: stop-ship until a qualified clinical owner accepts the
  release corpus and the strict release gate passes.

The release owner controls build promotion. Only the clinical owner may approve
clinical content or visuals. Local in-app review marks are editorial notes and
never substitute for source approval.

## Two Validation Modes

Authoring mode supports draft work and fails only on structural blockers:

```text
python -m pip install -r scripts/requirements-validation.txt
python scripts/validate_procedures.py
```

Release mode adds non-bypassable approval, provenance, and visual-asset gates:

```text
python scripts/validate_procedures.py --release
```

A release candidate must pass release mode. Ordinary branch development is
allowed to remain in authoring mode so unfinished content can be improved
without misrepresenting it as approved.

## Stop-Ship Conditions

A candidate cannot ship when any of the following is true:

- The clinical owner is unassigned.
- Any visible procedure, rescue card, or kit lacks a clinically reviewed status.
- A declared visual asset is a placeholder or missing from the bundle.
- A released item contains a known placeholder or generic reference marker.
- Authoring validation, validator negative controls, Xcode source-membership
  verification, XCTest, or the Release build fails.
- XCTest reports success with zero executed tests.
- Persistence migration, corrupt-load, offline, accessibility, or physical-device
  evidence required for the candidate is missing.

## Required Release Evidence

Each candidate must retain:

- Git commit and content versions under review.
- Strict validator output.
- Xcode test log, test count, and `.xcresult` bundle.
- Release-configuration build log.
- Clinical owner sign-off for the exact visible corpus and bundled visuals.
- Physical-device, offline, VoiceOver, and Dynamic Type checklist results.

Changing approved clinical content or a visual invalidates its prior approval.

## Waivers

Clinical review, missing artwork for a declared visual, failed tests, and zero-test
runs cannot be waived. A non-clinical warning may be waived only when the release
owner records an owner, rationale, affected commit, expiry date, and follow-up
issue. Undocumented or expired waivers are stop-ship conditions.
