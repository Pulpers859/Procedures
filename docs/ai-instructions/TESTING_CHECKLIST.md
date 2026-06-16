# Testing Checklist

## Automated tests

- The repo has a real XCTest target: `ProceduresTests`.
- The shared Xcode scheme is `Procedures`.
- Current XCTest files:
  - `ProceduresTests/ContentDecodingTests.swift`
  - `ProceduresTests/RescueSearchTests.swift`
  - `ProceduresTests/ValidationTests.swift`
- Run these tests in Xcode with `Product > Test` or `Command-U`.
- Beginner guide: `docs/ai-instructions/XCTEST_GUIDE.md`.
- Command-line test command on macOS:

```bash
xcodebuild test -project Procedures.xcodeproj -scheme Procedures -destination 'platform=iOS Simulator,name=iPhone 16'
```

Use a simulator name installed on the machine if `iPhone 16` is unavailable.

These tests are most valuable for bundled JSON decoding, search regressions, and validation rules. They do not replace manual simulator checks for layout, navigation feel, or visual polish.

## Manual tests

- App launches on iPhone simulator
- Procedures load from bundled JSON
- Rescue cards load from bundled JSON
- Search works for title and tags
- Rescue search works for shorthand terms like `ETT`, `TVP`, `wire`, and `apnea`
- Procedure detail opens to Shift Mode
- Visual Landmark card renders without layout breakage when `visualAssets` exist
- Visual Landmark card shows a placeholder cleanly when no bundled image file exists yet
- Equipment checklist toggles rows
- Favorite button persists after restart
- Recently viewed updates after opening procedure
- Notes save after editing
- Empty optional sections do not break layout
- Dark mode remains readable

## Search examples

- ETT
- tube
- RSI
- central line
- CVC
- guidewire
- TVP
- apnea
- finger block
- nailbed
