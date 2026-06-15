# Project Handoff

## Project Identity
- Project name: `Procedures`
- App/product name: `ProcedureSTAT`
- Project type: `iOS app`
- Source-of-truth repo path: `C:\Dev\Procedures`
- Actual app source root: `C:\Dev\Procedures\ProcedureSTAT`
- Xcode project: `C:\Dev\Procedures\ProcedureSTAT.xcodeproj`
- Stale/old copies to ignore if applicable: `None found during workspace/Desktop scan on 2026-06-14`
- Primary target for normal work: `Main iOS app`
- GitHub intent/status: `remote attached; local repo bootstrapped on 2026-06-14`
- GitHub remote: `https://github.com/Pulpers859/Procedures.git`

## Repo State
- Stable branch: `main`
- Working branch: `main`
- Expected default branch for normal work: `main`
- Sync-first rule: `Before normal work, fetch from origin first. If the working tree is clean, pull the tracked branch with --ff-only before editing. If local changes exist, fetch and reconcile instead of blindly pulling.`
- Branch policy note: `Main-only by default unless explicitly overridden`

## PowerShell / Terminal Standard
- Do not globally pin every PowerShell session to this project.
- Preferred dedicated shortcut name: `Procedures PowerShell`
- Shortcut should open directly in: `C:\Dev\Procedures`
- Avoid fragile startup command strings; the path is simple and does not need extra quoting tricks.

## How The Agent Should Operate
- Inspect before assuming.
- Work in `C:\Dev\Procedures` only unless the user explicitly asks to inspect another copy.
- Treat `ProcedureSTAT.xcodeproj` plus `ProcedureSTAT/` as the live runtime surface.
- Keep procedure content in `ProcedureSTAT/Resources/procedures.json`; do not hardcode clinical content into SwiftUI views.
- Fix root causes, not surface symptoms.
- Run the validation script after content changes: `python scripts/validate_procedures.py`.
- Before editing on an existing repo, fetch and check ahead/behind state; if clean, pull with `--ff-only`.
- Audit adjacent risks after making fixes.
- Clearly distinguish what was proven locally from what could not be verified on Windows.

## Architecture / Product Notes
- Main product purpose: `Offline-first emergency medicine / ICU procedure review app for trained clinicians`
- Key modules or directories:
  - `ProcedureSTAT/Views` - SwiftUI screens
  - `ProcedureSTAT/Components` - reusable UI pieces
  - `ProcedureSTAT/Data` - repositories and local persistence
  - `ProcedureSTAT/Models` - Codable domain models and validation types
  - `ProcedureSTAT/Resources/procedures.json` - bundled procedure content source of truth
  - `scripts/validate_procedures.py` - local content validator
  - `docs/` - project docs, product notes, and audits
- Known fragile areas:
  - `No XCTest target yet`
  - `Clinical content still needs expert review before real use`
  - `Build/run cannot be fully verified from this Windows workspace alone`
- Important evidence/product constraints:
  - `Educational tool only; not a substitute for supervision, credentialing, local policy, or clinical judgment`
  - `Offline-first behavior is intentional`
  - `User data is currently local-only`
- Runtime environments that matter: `iPhone simulator`, `iPhone device`

## Git / Release Notes
- Preferred everyday flow:
  - `git fetch --prune`
  - `git pull --ff-only`
  - `git st`
  - `git diff`
  - `git add .`
  - `git commit -m "..."`
  - `git push`
- Preferred branch model by default:
  - `work directly on main`
  - `do not create side branches unless explicitly instructed`

## Project-Specific Instructions For The Next Agent
```text
Project: Procedures
Active repo path: C:\Dev\Procedures
Actual app source root: C:\Dev\Procedures\ProcedureSTAT
Xcode project: C:\Dev\Procedures\ProcedureSTAT.xcodeproj
GitHub remote: https://github.com/Pulpers859/Procedures.git
Stable branch: main
Working branch: main

Important:
- Treat C:\Dev\Procedures as the source-of-truth repo root.
- Treat C:\Dev\Procedures\ProcedureSTAT as the live app source tree.
- No stale copy was found during the initial workspace/Desktop scan on 2026-06-14.
- If a later duplicate copy appears, verify it before working there.
- Before starting normal work, fetch from origin and sync main first when the working tree is clean.
- Run python scripts/validate_procedures.py after content edits.
- Keep work on main unless the user explicitly requests another branch model.
- Be explicit when a claim is proven by local inspection versus inferred because Xcode/iOS runtime verification was unavailable on this Windows machine.
```
