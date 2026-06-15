# Procedures Handoff Map

## Canonical Paths

- Repo: `C:\Dev\Procedures`
- App source: `C:\Dev\Procedures\Procedures`
- Xcode project: `C:\Dev\Procedures\Procedures.xcodeproj`
- Procedure content: `Procedures/Resources/procedures.json`
- Rescue content: `Procedures/Resources/rescue_cards.json`
- Content validator: `scripts/validate_procedures.py`
- GitHub: `https://github.com/Pulpers859/Procedures.git`

## Task Routing

- Clinical content or rescue cards:
  - use `procedures-content-audit`
  - read `docs/ai-instructions/PROCEDURE_SCHEMA.md`
  - read `docs/ai-instructions/SAFETY_AND_REVIEW_POLICY.md`
- UI/UX implementation:
  - read `docs/ai-instructions/UI_UX_RULES.md`
  - use current SwiftUI skills as needed
- External UI/UX tools:
  - use `ui-ux-resource-eval`
- Broad or cross-cutting work:
  - use `claude-code-efficiency`
- Outside-agent work:
  - read `docs/EXTERNAL_AGENT_RECONCILIATION.md`

## Product Risks

1. Incorrect or stale clinical content
2. Missing failure plans or rescue actions
3. Content that passes schema checks but lacks expert review
4. Search terms that fail under normal clinical shorthand
5. Slow or cluttered bedside retrieval
6. Missing Xcode/runtime validation
