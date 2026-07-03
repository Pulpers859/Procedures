# Procedures Agent Instructions

## Start Here
- Source-of-truth repo: `C:\Dev\Procedures`
- App source: `C:\Dev\Procedures\Procedures`
- Xcode project: `C:\Dev\Procedures\Procedures.xcodeproj`
- Working branch: `main`
- Work directly on `main`; do not create side branches or pull requests unless the user explicitly requests them.
- For risky, creative, or parallel agent work, use a detached sandbox worktree via `tools/New-AgentSandbox.ps1`; do not create side branches or commit/push from the sandbox.
- Commit and push completed tracked changes to `origin/main` in the same work cycle unless the user explicitly says not to.

## Product Priorities
1. Clinical safety and content integrity
2. Fast bedside retrieval and clear failure plans
3. Offline reliability and local data continuity
4. Accessible, calm, native iOS UX
5. Maintainable models, validation, and content workflows

## Source-of-Truth Rules
- Procedure content lives in `Procedures/Resources/procedures.json`.
- Rescue cards live in `Procedures/Resources/rescue_cards.json`.
- Do not hardcode clinical content or rescue cards into SwiftUI views.
- Treat visual assets as reviewed clinical content, not decoration.
- Run `python scripts/validate_procedures.py` after clinical content or schema changes.
- Structural validation does not prove clinical correctness. Clearly identify content that still needs expert review.

## Context Discipline
- Read this file first, then load only the skill and docs needed for the task.
- Use targeted searches and small reads before opening full JSON content files.
- Apply `procedures-handoff` automatically at the start of a fresh Procedures session unless the task is already narrowly scoped.
- Apply `procedures-content-audit` automatically for procedure JSON, rescue cards, clinical references, content validation, schema, reviewer status, or safety-critical copy.
- Apply `claude-code-efficiency` for broad, multi-file, research-heavy, or context-hungry work.
- Apply `ui-ux-resource-eval` only when evaluating external design tools, libraries, systems, or reference sites.

## External Agent Reconciliation
- If prior work by another agent, machine, terminal, or conversation is mentioned, reconcile its claimed changes against local files, local Git history, and `origin/main` before editing or making sync claims.
- Classify claimed work as present, missing, partially landed, or overwritten.
- Read `docs/EXTERNAL_AGENT_RECONCILIATION.md` when this applies.

## Read Deeper Only When Needed
- `PROJECT_HANDOFF.md`
- `docs/ai-instructions/PRODUCT_BRIEF.md`
- `docs/ai-instructions/SAFETY_AND_REVIEW_POLICY.md`
- `docs/ai-instructions/PROCEDURE_SCHEMA.md`
- `docs/ai-instructions/SWIFT_ARCHITECTURE.md`
- `docs/ai-instructions/UI_UX_RULES.md`
- `docs/ai-instructions/TESTING_CHECKLIST.md`
- `docs/ai-instructions/HIGH_YIELD_NEXT_STEPS.md`
- `docs/agent-sandbox-workflow.md`

## Validation Reality
- Windows can validate Git state, JSON content, scripts, and framework-light Swift logic.
- Real iOS build, simulator, accessibility, and runtime validation require macOS/Xcode.
