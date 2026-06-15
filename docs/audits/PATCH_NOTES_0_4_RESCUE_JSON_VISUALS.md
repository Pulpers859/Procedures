# Procedures Patch 0.4 — Rescue JSON + Visual Asset Infrastructure

Overlay these files onto your existing `Procedures_MVP_0_3_GUIDE_FIRST` folder.

## Biggest changes

1. Rescue Cards are now loaded from JSON.
   - New file: `Procedures/Resources/rescue_cards.json`
   - Updated model: `Models/ComplicationRescueCard.swift`
   - Updated loader: `Data/ProcedureRepository.swift`
   - Updated views: Guide and Rescue tabs now use `repository.rescueCards`

2. Visual Landmark support is now real infrastructure, not just a generic placeholder.
   - Updated model: `ProcedureVisualAsset`
   - Updated content: each current procedure has `visualAssets` metadata
   - Updated detail UI: renders bundled image if `assetName` exists; otherwise renders a polished placeholder

## Important Xcode note

`Procedures.xcodeproj/project.pbxproj` was updated so `rescue_cards.json` is included in the app bundle.

If you manually copy files and skip the project file, Xcode may build but rescue cards will fail to load. Either copy the project file too, or manually add `rescue_cards.json` to the target's Resources build phase.

## Validation

Run:

```bash
./scripts/validate_procedures.py
```

Current expected output:

- 0 blockers
- polish warnings for visual metadata without final bundled artwork

That is intentional. The app now knows what visual each procedure needs; final reviewed artwork still needs to be created and attached.
