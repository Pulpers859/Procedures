---
name: claude-code-efficiency
description: Keep Claude Code work token-efficient in the Procedures repo. Use for broad, research-heavy, multi-file, or cross-cutting tasks where careless context loading would waste tokens. Do not use for tiny one-file edits unless the task starts to sprawl.
---

# Procedures Claude Code Efficiency

Use this skill when the task is broad enough that context discipline matters.

## Required Read

1. Read `docs/CLAUDE_CODE_TOKEN_EFFICIENCY.md`.
2. Read `PROJECT_HANDOFF.md` only if repo orientation or workflow rules are needed.
3. Read `docs/ai-instructions/AGENTS.md` only if product constraints or agent rules are needed.

## Workflow

1. Classify the task:
   - runtime bug
   - content edit
   - UI/UX research
   - repo cleanup
   - sync or reconciliation
2. Identify the smallest source-of-truth surface for that task.
3. Search first, then open only the files that matter.
4. Work in bounded waves:
   - inspect
   - edit
   - verify
   - recap
5. Before switching domains, write a short recap instead of reloading broad context.

## Repo-Specific Guardrails

- Do not open full `Procedures/Resources/procedures.json` or `Procedures/Resources/rescue_cards.json` unless the task truly needs content inspection or content editing.
- Do not use web UI references for normal native SwiftUI implementation work.
- For external design research, choose at most one or two sources in a single pass.
- Treat BuilderIO-style efficiency ideas as patterns to adapt, not as a reason to import a large generic instruction set.
- When outside-agent work is part of the context, follow `docs/EXTERNAL_AGENT_RECONCILIATION.md` before making sync claims.

## Resource Defaults

- BuilderIO/skills: `Adapt`
- UI UX Pro Max: `Reference`
- 21st.dev: `Skip` for normal repo work
- UX Components: `Reference`
- Refero: `Reference`
