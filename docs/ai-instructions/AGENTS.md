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

7. Reconcile outside agent work before sync claims.
   - If the user mentions prior work by another AI agent, another machine, another terminal, or another conversation, do not assume the current diff or latest visible commit tells the full story.
   - Before making new edits, rebases, resets, merges, or sync claims, perform an external-agent reconciliation pass.
   - Inspect any outside artifact the user provides, such as a transcript, chat export, screenshot, commit list, or claimed fix summary.
   - Compare what the other agent claimed to change against the current local files, the local Git history, and the current `main` branch on GitHub.
   - Tell the user plainly whether each claimed change is present, missing, partially landed, or overwritten.
   - Only after that comparison should you decide whether to pull, rebase, merge, patch missing work, or leave newer work intact.
   - Do not say the repo is fully assessed or in sync until that reconciliation step is complete whenever outside-agent work is part of the context.

8. Use the UI/UX resource playbook for external design-tooling decisions.
   - When evaluating external UI/UX resources, component libraries, design systems, visual reference sites, or design-oriented agent skills for this app, read `docs/AI_UI_UX_RESOURCE_EVALUATION_PLAYBOOK.md` first and follow its `Adopt / Adapt / Reference / Skip` process.
   - Do not use this playbook for every UI task by default.
   - Use it when the work involves design-system decisions, component library selection, UI inspiration sources, redesign planning, or deciding whether an external UI/UX repo or website should influence the app.
   - Use the playbook as a neutral decision framework, not as a preset recommendation.
   - Inspect this app's actual platform, workflows, implementation stack, design maturity, and constraints before deciding what fits.

9. Keep Claude Code context lean on broad tasks.
   - Use `docs/CLAUDE_CODE_TOKEN_EFFICIENCY.md` when the task is research-heavy, cross-cutting, or likely to burn context.
   - Prefer targeted file reads, source-of-truth paths, bounded work waves, and short recaps over broad repo sweeps.
   - Do not browse external design resources unless the task actually needs outside design evidence.

10. Use repo-local skills automatically when the task matches.
   - Use `procedures-handoff` at the start of a fresh repo session unless the task is already narrowly scoped.
   - Use `procedures-content-audit` for clinical JSON, rescue cards, schema, references, validation, reviewer status, or safety-critical copy.
   - Use `claude-code-efficiency` for broad, research-heavy, or cross-cutting work.
   - Use `ui-ux-resource-eval` only for external UI/UX tooling and reference decisions.
   - Prefer the smallest matching skill set instead of loading everything.

11. Protect local Git integrity during Claude Code and multi-machine work.
   - Treat GitHub commits and pushes as the handoff boundary between machines and agents.
   - Do not assume multiple agents can safely mutate the same local clone at the same time.
   - Before normal work: run `git status -sb`, then `git fetch --prune`, then `git pull --ff-only` if the tree is clean.
   - If the tree is not clean, reconcile before pulling.
   - Do not interrupt active `git fetch`, `git pull`, `git reset`, `git rebase`, or checkout operations.
   - If Git reports broken refs, `bad object`, or unresolved `HEAD`, stop and inspect `.git` before continuing.
   - Do not rely on cloud-sync tools or manual repo-copying as a substitute for normal GitHub push/pull handoff.

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

## External-Agent Reconciliation: Non-Optional Default

- When outside-agent work is part of the context, reconciliation comes before sync claims.
- Do not treat `git diff`, the current working tree, or the latest visible local commit as a full accounting by themselves.
- Compare claimed outside work against:
  - current local files
  - local Git history
  - current GitHub `main`
- Report whether each claimed change is present, missing, partially landed, or overwritten before choosing the next Git action.
