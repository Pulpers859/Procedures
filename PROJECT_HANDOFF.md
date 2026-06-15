# Project Handoff

## Project Identity
- Project name: `Procedures`
- App/product name: `Procedures`
- Project type: `iOS app`
- Source-of-truth repo path: `C:\Dev\Procedures`
- Actual app source root: `C:\Dev\Procedures\Procedures`
- Xcode project: `C:\Dev\Procedures\Procedures.xcodeproj`
- Stale/old copies to ignore if applicable: `None found during workspace/Desktop scan on 2026-06-14`
- Primary target for normal work: `Main iOS app`
- GitHub intent/status: `remote attached; local repo bootstrapped on 2026-06-14`
- GitHub remote: `https://github.com/Pulpers859/Procedures.git`
- Legacy bundle identifier intentionally retained: `com.pjkane859.ProcedureSTAT`

## Repo State
- Stable branch: `main`
- Working branch: `main`
- Expected default branch for normal work: `main`
- Sync-first rule: `Before normal work, fetch from origin first. If the working tree is clean, pull the tracked branch with --ff-only before editing. If local changes exist, fetch and reconcile instead of blindly pulling.`
- Branch policy note: `Main-only by default unless explicitly overridden`
- Commit/push rule: `If an agent makes tracked repo changes, it must commit and push them to origin/main in the same work cycle by default. Do not wait for a separate push request unless the user explicitly says not to push or push is blocked by auth/network/repo-protection failure.`

## PowerShell / Terminal Standard
- Do not globally pin every PowerShell session to this project.
- Preferred Claude shortcut name: `Procedures Claude Code`
- Shortcut should open directly in: `C:\Dev\Procedures`
- Repo launcher script: `tools/Launch-Procedures-Claude.ps1`
- The launcher checks root Claude memory and repo-local skills before starting Claude Code.

## How The Agent Should Operate
- Inspect before assuming.
- Work in `C:\Dev\Procedures` only unless the user explicitly asks to inspect another copy.
- Treat `Procedures.xcodeproj` plus `Procedures/` as the live runtime surface.
- Keep procedure content in `Procedures/Resources/procedures.json`; do not hardcode clinical content into SwiftUI views.
- Keep rescue-card content in `Procedures/Resources/rescue_cards.json`; do not reintroduce hardcoded rescue cards.
- Fix root causes, not surface symptoms.
- Run the validation script after content changes: `python scripts/validate_procedures.py`.
- Before editing on an existing repo, fetch and check ahead/behind state; if clean, pull with `--ff-only`.
- If the user mentions prior work by another AI agent, another machine, another terminal, or another conversation, do not assume the current diff or latest visible commit tells the full story.
- Before making new edits, rebases, resets, merges, or sync claims in that situation, perform an external-agent reconciliation pass:
  - inspect any outside artifact the user provides, such as a transcript, chat export, screenshot, commit list, or claimed fix summary
  - compare what that agent claimed to change against the current local files, the local Git history, and the current `main` branch on GitHub
  - tell the user plainly whether each claimed change is present, missing, partially landed, or overwritten
  - only after that comparison decide whether to pull, rebase, merge, patch missing work, or leave newer work intact
- Do not claim the repo is fully assessed or in sync until that reconciliation step is complete whenever outside-agent work is part of the context.
- Audit adjacent risks after making fixes.
- After making tracked repo changes, commit them and push `origin/main` in the same session by default so the GitHub repo stays current for pull/fetch on other machines and agents.
- Clearly distinguish what was proven locally from what could not be verified on Windows.

## Architecture / Product Notes
- Main product purpose: `Offline-first emergency medicine / ICU procedure review app for trained clinicians`
- Key modules or directories:
  - `Procedures/Views` - SwiftUI screens
  - `Procedures/Components` - reusable UI pieces
  - `Procedures/Data` - repositories and local persistence
  - `Procedures/Models` - Codable domain models and validation types
  - `Procedures/Resources/procedures.json` - bundled procedure content source of truth
  - `Procedures/Resources/rescue_cards.json` - bundled rescue-card content source of truth
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
  - `Bundle identifier intentionally remains com.pjkane859.ProcedureSTAT for continuity; changing it later will create a new iOS app identity`
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
Actual app source root: C:\Dev\Procedures\Procedures
Xcode project: C:\Dev\Procedures\Procedures.xcodeproj
GitHub remote: https://github.com/Pulpers859/Procedures.git
Stable branch: main
Working branch: main

Important:
- Treat C:\Dev\Procedures as the source-of-truth repo root.
- Treat C:\Dev\Procedures\Procedures as the live app source tree.
- No stale copy was found during the initial workspace/Desktop scan on 2026-06-14.
- If a later duplicate copy appears, verify it before working there.
- Before starting normal work, fetch from origin and sync main first when the working tree is clean.
- If prior outside-agent work is mentioned, perform the external-agent reconciliation pass before claiming sync status or choosing pull/rebase/merge/edit actions.
- Run python scripts/validate_procedures.py after content edits.
- Keep work on main unless the user explicitly requests another branch model.
- If you make tracked changes, you must commit them and push origin/main in the same work cycle by default. Do not leave local-only changes waiting for the user to ask for a push.
- Be explicit when a claim is proven by local inspection versus inferred because Xcode/iOS runtime verification was unavailable on this Windows machine.
```
