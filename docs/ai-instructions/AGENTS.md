# AI Agent Instructions

You are helping build Procedures, a SwiftUI educational procedure-review app for emergency medicine and ICU clinicians.

The app is designed for trained clinicians who need rapid, structured, practical review before performing procedures on shift.

## Core principles

1. Optimize for on-shift use.
   - The user may have less than 2 minutes.
   - Avoid textbook prose.
   - Put Shift Mode first.

2. Safety over cleverness.
   - Do not invent clinical claims.
   - Content should include cautions, complications, and failure plans.
   - Content must not imply that app review replaces training, supervision, credentialing, local policy, or clinical judgment.

3. Structure matters.
   - Use the same procedure schema for every procedure.
   - Keep content separate from SwiftUI views.
   - Use local JSON for bundled procedure content.

4. Offline-first.
   - Core procedure content must load without internet.
   - User favorites, recents, and notes should persist locally.

5. Keep code maintainable.
   - Use SwiftUI.
   - Avoid massive views when practical.
   - Use strongly typed Codable models.
   - Keep user data separate from read-only procedure content.

6. Keep GitHub current.
   - If you make tracked repo changes, commit and push them to `origin/main` in the same work cycle by default.
   - Do not leave local-only repo changes waiting for a separate push request.
   - Only skip the push when the user explicitly says not to push or push is blocked by auth, network, or repo protection.

## Current MVP

The current MVP uses:

- SwiftUI
- Local bundled JSON
- ObservableObject stores
- UserDefaults for favorites, recents, and notes
- 5 main tabs: Guide, Procedures, Rescue, Kits, Saved

## High-Yield Future Suggestions

Before adding low-value features, consult `HIGH_YIELD_NEXT_STEPS.md`.

Priority order:
1. Expand the core ED/ICU procedure library with complete, validated content.
2. Make complication rescue cards first-class, problem-oriented clinical objects.
3. Add automated content validation and test coverage so missing critical sections cannot silently ship.
4. Improve the home screen into a clinical command center.
5. Evolve the schema only when flat arrays begin blocking real workflows.

Do not prioritize accounts, subscriptions, video libraries, cloud sync, or AI-generated clinical content until the core offline procedure and rescue-card experience is excellent.

## Current Direction: Fadial-Style Simplicity, Premium EM/ICU Execution

The app should intentionally move toward a simple, clean, bedside-first iOS experience: fast search, fast routing, sparse screens, and clinically useful cards. The direction is closer to a polished procedural command center than a textbook or generic education app.

Implement this hierarchy:

- Guide first: clinical pathways and command-center routing.
- Procedures second: full A-Z library.
- Rescue third: problem-first rescue cards.
- Kits fourth: physical setup checklists.
- Saved fifth: favorites, recent items, notes, local preferences, and content health.

Design rules:

- Do not bury urgent information under long section lists.
- Do not add visual clutter just to make the app feel premium.
- Prefer one excellent clinical card over a dense page.
- Make Shift Mode the default landing section inside procedure detail pages.
- Keep procedure images focused: landmark, probe, danger zone, or confirmation.
- Treat every visual as clinical content requiring review.

When adding new features, ask: will this help an on-shift clinician get safer, faster, or more prepared within 10 seconds? If not, it belongs later.

## Current Architecture Direction: Do Not Regress

As of the latest patch, Rescue Cards and Visual Asset metadata are part of the app's core content architecture.

### Rescue Cards

- Do not hardcode rescue cards in Swift.
- Add/edit rescue cards in `Procedures/Resources/rescue_cards.json`.
- Treat rescue cards as reviewed clinical content with `lastReviewed`, `version`, and `references`.
- Validate rescue cards with `./scripts/validate_procedures.py`.

### Visual Assets

- Do not add random image galleries.
- Each procedure should start with one primary visual asset that prevents a meaningful clinical miss.
- Add visual metadata to the procedure's `visualAssets` array.
- Add bundled artwork later and set `assetName`.
- If no artwork exists yet, keep the metadata placeholder rather than removing the visual section.

The design target remains: Fadial-style simplicity, premium clinical hierarchy, offline-first speed, and stronger EM/ICU rescue depth.

## Git Discipline: Non-Optional Default

- This repo uses a push-by-default workflow.
- Any agent with GitHub access should treat commit + push as part of finishing the task, not as a separate optional follow-up.
- Goal: the GitHub repo stays current so the user can fetch/pull on another machine, including the Mac/Xcode environment, without having to ask for a manual push afterward.
