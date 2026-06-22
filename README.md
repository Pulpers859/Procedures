# Procedures MVP 0.2

Procedures is a SwiftUI educational procedure-review app for emergency medicine and ICU clinicians.

This repo contains the `Procedures` iOS app plus supporting docs and validation scripts.

This phase includes:

- Updated Guide-first 5-tab SwiftUI layout
- Procedure library
- Weighted clinical search with shorthand/synonym support
- Shift Mode summaries
- Equipment checklists with persistent per-procedure state
- Problem-first complication Rescue Cards, now promoted to the Rescue tab
- Procedure-specific complication reviews
- Favorites
- Recently viewed procedures
- Local procedure notes
- Optional Review Center for content review, validation issues, and local reviewer notes
- Local bundled JSON procedure content
- Lightweight content validation script
- AI-agent instruction files

## Current bundled procedure library

- Endotracheal Intubation
- Cricothyrotomy
- Central Venous Catheter
- Thoracostomy / Chest Tube
- Pigtail Pleural Catheter
- Needle Decompression
- Pericardiocentesis
- Transvenous Pacemaker
- Procedural Sedation
- Lumbar Puncture
- Digital Nerve Block

## How to run in Xcode

1. Open `Procedures.xcodeproj` in Xcode.
2. Select the `Procedures` scheme.
3. Select an iPhone simulator.
4. Press Run.

If Xcode asks for signing, select your personal development team under:

`Procedures target > Signing & Capabilities > Team`

## How to run tests

The repo includes a real XCTest target named `ProceduresTests`.

In Xcode:

1. Open `Procedures.xcodeproj`.
2. Select the `Procedures` scheme.
3. Select an iPhone simulator.
4. Press `Command-U`, or choose `Product > Test`.

From Terminal on macOS:

```bash
xcodebuild test -project Procedures.xcodeproj -scheme Procedures -destination 'platform=iOS Simulator,name=iPhone 16'
```

If your Mac does not have an `iPhone 16` simulator, pick any installed iPhone simulator from Xcode's device menu and use that name in the command.

The current tests cover JSON decoding, rescue/procedure search behavior, and content validation rules. Keep using the manual checklist for visual layout, navigation, and bedside UX checks.

## Validate procedure content

From the project root:

```bash
python scripts/validate_procedures.py
```

The script validates duplicate IDs, required metadata, required section keys, and thin critical content. It should be run before adding or editing procedure content.

It now also validates:

- `Procedures/Resources/rescue_cards.json`
- rescue-card metadata and related procedure IDs
- `visualAssets` metadata on procedures
- missing bundled image files when `visualAssets.assetName` is set

## Important clinical disclaimer

The included clinical content is starter educational content for app development. It should be reviewed and edited before any real clinical use. The app does not replace clinical judgment, supervision, credentialing, or institutional policy.

## Where to add procedures

Add new procedures in:

`Procedures/Resources/procedures.json`

Add or edit rescue cards in:

`Procedures/Resources/rescue_cards.json`

Every procedure follows the schema described in:

`docs/ai-instructions/PROCEDURE_SCHEMA.md`

High-yield future work is listed in:

`docs/ai-instructions/HIGH_YIELD_NEXT_STEPS.md`

Repo workflow and handoff rules live in:

`PROJECT_HANDOFF.md`

Documentation is indexed in:

`docs/README.md`

## MVP 0.3 direction implemented in this patch

This patch moves the app toward a simple, clean bedside-reference model with a more premium EM/ICU structure:

- New **Guide** tab as the command center
- **Complications** renamed conceptually to **Rescue**
- **Equipment** renamed conceptually to **Kits**
- Clinical pathway routing: Airway, Lines, Thoracic, Resus, Blocks, Neuro
- Search now surfaces both procedures and rescue cards from the Guide tab
- Procedure pages now include a Visual Landmark placeholder card so future anatomy/probe/danger-zone images are structurally baked in
- Agent instructions now explicitly describe the desired product direction

## Suggested next build phase

MVP 0.3 should continue:

- Expand XCTest coverage for JSON decoding/search/content validation
- More core procedures: Cordis, Vas Cath, arterial line, US-guided PIV, paracentesis, thoracentesis, lateral canthotomy, abscess I&D, suture repair
- Structured equipment groups instead of one flat checklist
- One-tap copy documentation templates
- Reviewer metadata and content approval status
- More Rescue Cards, especially LAST, pneumothorax after CVC, laryngospasm, chest tube malposition, and post-LP neurologic symptoms

## MVP 0.4 partial patch direction

This repo now includes the starter architecture for the next content phase:

- Rescue Cards moved from hardcoded Swift into `Procedures/Resources/rescue_cards.json`
- `ProcedureRepository` now loads procedures and rescue cards separately
- Content validation now checks rescue-card structure and related procedure IDs
- Procedures now support `visualAssets` metadata
- Procedure detail can render a bundled visual when `visualAssets.assetName` is present, or a polished placeholder when artwork is not bundled yet

Current expected validation state:

- `0` blockers
- possible `POLISH` / `WARNING` output if final reviewed visual files are still missing

That is intentional. The app now has real infrastructure for rescue content and reviewed visuals, even before the final artwork set exists.
