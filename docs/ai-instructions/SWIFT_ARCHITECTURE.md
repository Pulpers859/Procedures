# Swift Architecture

## Stack

- SwiftUI
- Codable models
- Local bundled JSON
- ObservableObject repositories
- UserDefaults for MVP persistence

## Current folders

```text
Procedures/
  Models/
  Data/
  Views/
  Components/
  Resources/
```

Important bundled content files:

- `Procedures/Resources/procedures.json`
- `Procedures/Resources/rescue_cards.json`

## Data flow

- `ProcedureRepository` loads procedures and rescue cards from bundled JSON, then overlays local edits from `ProcedureEditStore` before publishing them.
- `UserDataStore` manages favorites, recents, notes, checklist progress, and local review records.
- Views receive both through environment objects.
- `ContentValidator` validates procedures, rescue cards, and visual metadata.

## Rules for future agents

- Do not hardcode procedure text inside SwiftUI views.
- Do not hardcode rescue cards in Swift.
- Do not mutate bundled procedure content. The bundle is read-only; clinician
  corrections live in `ProcedureEditStore` as section overrides in Documents and
  are merged onto a value copy at load. Every section can be reverted to what
  shipped, and `scripts/apply_local_edits.py` moves an export back into
  `procedures.json` as a reviewable diff.
- Do not treat local review records as bundled clinical approval; they are personal device state.
- Keep Review Center/editor workflow separate from the default bedside clinical flow.
- Keep rescue cards editable through `rescue_cards.json`.
- Keep visual metadata in procedure content via `visualAssets`; do not add decorative galleries without reviewed assets and a real product reason.
- Add user-specific content to `UserDataStore` or a future SwiftData layer.
- Keep procedure rendering generic so new procedures do not require new view code.
