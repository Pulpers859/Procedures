---
name: procedures-content-audit
description: Audit Procedures clinical JSON, rescue cards, schema changes, references, validation behavior, reviewer metadata, and safety-critical UI copy. Use automatically when adding or editing procedures or rescue cards, reviewing clinical content quality, debugging content validation, changing Codable models or schemas, checking stale references, or assessing release readiness.
---

# Procedures Content Audit

Use this skill to review clinical content with structural rigor while preserving the boundary between software validation and clinical approval.

## Workflow

1. Read `references/content-audit-map.md`.
2. Identify the exact procedure, rescue card, schema field, or validator rule in scope.
3. Inspect only the relevant JSON fragment plus its model, validator, and rendering path.
4. Classify findings:
   - `BLOCKER`: invalid structure, missing critical content, broken relation, decode/runtime failure
   - `WARNING`: thin safety content, vague reassessment, weak failure plan, stale or incomplete metadata
   - `POLISH`: presentation or completeness improvement without immediate structural risk
   - `CLINICAL REVIEW REQUIRED`: medically substantive claim that software inspection cannot approve
5. Check alignment across:
   - JSON schema
   - Swift Codable models
   - Python validator
   - in-app `ContentValidator`
   - UI rendering and search behavior
6. Run `python scripts/validate_procedures.py` after changes.
7. State what is structurally proven and what still requires qualified clinical review.

## Rules

- Never invent, silently strengthen, or approve clinical claims.
- Do not use AI-generated anatomy or clinical instructions as release-ready content without review.
- Keep Shift Mode concise and actionable.
- Require explicit failure/rescue thinking for high-risk procedures.
- Prefer concrete reassessment targets over phrases such as "monitor closely."
- Keep references and review metadata attached to clinical content.
- Do not weaken validators merely to make content pass.
- Treat search discoverability as a safety feature; check normal shorthand and synonyms when relevant.
