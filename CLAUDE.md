# Procedures Claude Code Memory

## Start Here
- Source-of-truth repo: `C:\Dev\Procedures`
- App source: `C:\Dev\Procedures\Procedures`
- Xcode project: `C:\Dev\Procedures\Procedures.xcodeproj`
- Work only on `main` unless the user explicitly requests otherwise.
- Commit and push completed tracked changes to `origin/main` in the same work cycle unless explicitly told not to.

## Product Priorities
1. Clinical safety and content integrity
2. Fast bedside retrieval and explicit failure plans
3. Offline reliability and local data continuity
4. Accessible, calm, native iOS UX
5. Maintainable validation and content architecture

## Audience
- This app has exactly one user: the repo owner. It is not a multi-user or team product.
- Never attribute anything in the UI back to the reader. A sign-off reads `Reviewed`, never `Reviewed by you`. Same for `My Reviews`, `My Edits`, `your review`, `you flagged`.
- The reader already knows what they did. Attribution is text they must read to learn nothing.
- Enforced by `scripts/check_review_state_sources.py`, which fails the build on that phrasing. Explaining the rule in a comment is fine; shipping it in a string is not.
- Keep the local-versus-upstream distinction in code (`ReviewState.reviewedLocally` vs `.clinicallyReviewed`) — it still drives export and validation. Only the copy collapses.

## Core Rules
- Keep procedure content in `Procedures/Resources/procedures.json`.
- Keep rescue cards in `Procedures/Resources/rescue_cards.json`.
- Never invent clinical claims or present unreviewed content as clinically approved.
- Do not hardcode clinical content into SwiftUI views.
- Run `python scripts/validate_procedures.py` after content or schema edits.
- Treat validator-clean content as structurally valid, not necessarily clinically correct.
- Preserve the educational disclaimer and local-policy boundaries.

## Automatic Skills
- Use `procedures-handoff` at the beginning of a fresh repo session unless the task is already narrowly scoped.
- Use `procedures-content-audit` for procedure/rescue content, schema, references, validation, reviewer status, or safety-critical copy.
- Use `claude-code-efficiency` for broad or context-heavy tasks.
- Use `ui-ux-resource-eval` only for external UI/UX resource decisions.

## Context Discipline
- Search first and open only task-relevant files.
- Avoid loading full clinical JSON files unless the task requires content inspection or editing.
- Read deeper docs only when the task needs them; start from `PROJECT_HANDOFF.md` and `docs/README.md`.

## External Agent Reconciliation
- When outside-agent work is mentioned, compare claimed changes against current files, local history, and `origin/main` before editing or claiming sync.
- Read `docs/EXTERNAL_AGENT_RECONCILIATION.md`.

## Validation Reality
- Windows can validate Git, JSON, scripts, and limited Swift logic.
- Xcode and iOS runtime verification require macOS.
