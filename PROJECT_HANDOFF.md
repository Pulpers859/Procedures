# Project Handoff

## READ THIS FIRST — How To Get A Build Onto The Owner's iPhone

**The owner has no Apple Developer account and no Mac.** They install builds by
re-signing an unsigned `.ipa` with **Signulous** on the phone itself. Do not
tell them to open Xcode, connect a cable, use TestFlight, or download a CI
*artifact* — none of those work for them.

**There is a workflow that does this. Use it. Do not invent another.** It is
the same route the TimeCapsule repo uses, where it was proven.

### The whole loop

1. Commit and push to `main` as normal.
2. Trigger `.github/workflows/build-sideload-ipa.yml` (manual, no inputs) —
   with the GitHub tools, or:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" \
     -X POST \
     -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Content-Type: application/json" \
     -H "Accept: application/vnd.github+json" \
     "https://api.github.com/repos/Pulpers859/Procedures/actions/workflows/build-sideload-ipa.yml/dispatches" \
     -d '{"ref":"main"}'
   ```
   `204` means it started. `415` means `Content-Type: application/json` is missing.
3. Wait for it to finish. Poll, do not guess:
   ```bash
   curl -s "https://api.github.com/repos/Pulpers859/Procedures/actions/workflows/build-sideload-ipa.yml/runs?per_page=1"
   ```
4. Hand over the release link, and nothing else to do but tap it:
   `https://github.com/Pulpers859/Procedures/releases/download/sideload-<N>/Procedures.ipa`
   (`<N>` is the run number; the newest release shows it.)

They open it in Safari on the phone, sign it in Signulous, and install.

### Why a release and not an artifact

Actions **artifacts cannot be downloaded on a phone**: they need a signed-in
desktop browser. A **public release asset** has a plain direct URL Safari can
open and Signulous can be pointed at. The repo is public, so no sign-in is
needed. Do not revert to artifacts.

### What the workflow does

- Archives the Release configuration **unsigned** (`CODE_SIGNING_ALLOWED=NO`)
  on the same pinned runner as `ios-tests.yml`. Signulous re-signs with its own
  certificate.
- Fails if `procedures.json` or `rescue_cards.json` is not bundled, since an
  app without its content still installs.
- Zips `Payload/Procedures.app` into `Procedures.ipa` — that is the whole
  format — and publishes it as a prerelease tagged `sideload-<N>`, which the
  `v*` trigger in `release-readiness.yml` does not match.

### Limits of a sideloaded build

- Signulous certificates expire and can be revoked; when that happens the app
  stops opening until it is re-signed. That is the certificate, not the app.
- It installs under Signulous's signing identity, not the project's bundle
  identifier and team. Anything tied to those (App Groups, iCloud, push) would
  not work, and none of it is used today. Add any of them and this route
  needs revisiting.
- CI cannot see the phone. How it looks and behaves on device has to come back
  from the owner — ask for the specific observation.

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
  - `ProceduresTests/` - XCTest coverage for bundled JSON decoding, search behavior, and validation rules
  - `docs/` - project docs, product notes, and audits
- Known fragile areas:
  - `XCTest target exists and is intended for JSON decoding, search, and validation regression coverage`
  - `Clinical content still needs expert review before real use`
  - `Build/run cannot be fully verified from this Windows workspace alone`
  - `Xcode XCTest execution must be verified on macOS/Xcode or an available macOS CI runner`
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

## Git Safety For Claude Code / Multi-Machine Work
- The failure we just hit was local ref corruption: `.git/refs/heads/main` became invalid, so normal `fetch` and `pull` stopped working even though GitHub was fine.
- Treat GitHub as the handoff surface, not a shared live `.git` state across tools or machines.
- Use one working copy per active agent or machine. Do not run multiple agents or terminals that mutate the same clone at the same time.
- Do not place the live repo inside OneDrive, Dropbox, iCloud Drive, Google Drive sync folders, or similar file-sync tools that may touch `.git` internals mid-write.
- Do not manually copy `.git` folders between machines.
- Before starting work on a machine or in Claude Code:
  - run `git status -sb`
  - run `git fetch --prune`
  - if clean, run `git pull --ff-only`
  - if not clean, reconcile before pulling
- Before leaving a machine or ending an agent session:
  - commit tracked work
  - push to GitHub
  - confirm `git status -sb` is clean unless the user explicitly wants local-only WIP
- Do not force-close the terminal, Claude session, or machine during `fetch`, `pull`, `reset`, `rebase`, `checkout`, or large file updates.
- If work is long-running, risky, or performed by another remote agent, prefer a separate clone or worktree rather than sharing one mutable checkout.
- For local AI-agent experiments, prefer a detached sandbox worktree via `tools/New-AgentSandbox.ps1`; do not create side branches or commit/push from the sandbox. See `docs/agent-sandbox-workflow.md`.
- If Git starts reporting `bad object`, `failed to resolve HEAD`, or broken refs, stop normal sync work and inspect `.git` before attempting more pulls or resets.

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
- Use one working copy per active agent or machine; do not let multiple agents mutate the same clone concurrently.
- Use GitHub commits/pushes as the handoff point between machines instead of copying repo state around.
- Do not run this live repo from cloud-sync folders that may interfere with `.git`.
- If Git reports broken refs, bad objects, or unresolved HEAD, stop and inspect `.git` before normal fetch/pull/reset commands.
- If prior outside-agent work is mentioned, perform the external-agent reconciliation pass before claiming sync status or choosing pull/rebase/merge/edit actions.
- Run python scripts/validate_procedures.py after content edits.
- Keep work on main unless the user explicitly requests another branch model.
- If you make tracked changes, you must commit them and push origin/main in the same work cycle by default. Do not leave local-only changes waiting for the user to ask for a push.
- Be explicit when a claim is proven by local inspection versus inferred because Xcode/iOS runtime verification was unavailable on this Windows machine.
```
