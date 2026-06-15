---
name: procedures-handoff
description: Orient an agent to the Procedures repo, source-of-truth paths, main-only Git workflow, clinical content boundaries, validation commands, and current product priorities. Use automatically at the start of a fresh Procedures session, when resuming old work, preparing a handoff, or deciding which files and skills a task requires.
---

# Procedures Handoff

Use this skill to rebuild the minimum correct context before editing.

## Workflow

1. Confirm:
   - repo root: `C:\Dev\Procedures`
   - app source: `C:\Dev\Procedures\Procedures`
   - Xcode project: `C:\Dev\Procedures\Procedures.xcodeproj`
   - current branch and working-tree state
   - ahead/behind state against `origin/main`
2. Read `references/handoff-map.md`.
3. Classify the task:
   - Swift/runtime
   - procedure or rescue content
   - validation/schema
   - UI/UX
   - Git/sync
4. Load only the matching docs and files.
5. If outside-agent work is mentioned, reconcile it before sync or edit decisions.
6. After tracked changes, validate, commit, and push `main` unless explicitly told not to.

## Rules

- Do not treat validator-clean clinical content as expert-approved.
- Do not hardcode procedure or rescue content in SwiftUI.
- Do not load the full JSON library for unrelated code work.
- Preserve offline-first behavior and local-only user data.
- Clearly state what was validated on Windows versus what still needs Xcode.
