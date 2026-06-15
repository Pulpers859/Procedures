# Swift Architecture

## Stack

- SwiftUI
- Codable models
- Local bundled JSON
- ObservableObject repositories
- UserDefaults for MVP persistence

## Current folders

```text
ProcedureSTAT/
  Models/
  Data/
  Views/
  Components/
  Resources/
```

## Data flow

- `ProcedureRepository` loads read-only procedure content from bundled JSON.
- `UserDataStore` manages favorites, recents, and notes.
- Views receive both through environment objects.

## Rules for future agents

- Do not hardcode procedure text inside SwiftUI views.
- Do not mutate bundled procedure content.
- Add user-specific content to `UserDataStore` or a future SwiftData layer.
- Keep procedure rendering generic so new procedures do not require new view code.
