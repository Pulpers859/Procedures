# Procedures Content Audit Map

## Sources of Truth

- Procedure JSON: `Procedures/Resources/procedures.json`
- Rescue JSON: `Procedures/Resources/rescue_cards.json`
- Schema guide: `docs/ai-instructions/PROCEDURE_SCHEMA.md`
- Safety policy: `docs/ai-instructions/SAFETY_AND_REVIEW_POLICY.md`
- Procedure model: `Procedures/Models/Procedure.swift`
- Rescue model: `Procedures/Models/ComplicationRescueCard.swift`
- Runtime validator: `Procedures/Models/ContentValidation.swift`
- Script validator: `scripts/validate_procedures.py`
- Loader/search: `Procedures/Data/ProcedureRepository.swift`

## Minimum Review Questions

- Does the JSON decode into the current Swift model?
- Do script and runtime validators enforce compatible rules?
- Are IDs unique and related procedure IDs resolvable?
- Are Shift Mode, equipment, steps, complications, and references present?
- Does a high-risk procedure have an explicit failure plan?
- Does a rescue card include trigger, immediate actions, reassessment, and mistakes to avoid?
- Are dates, versions, references, and reviewer expectations visible?
- Can a clinician find it using common shorthand?
- Does the UI preserve urgent hierarchy and offline availability?

## Release Boundary

Passing these checks means the content is structurally ready for review. It does not mean the clinical content is medically approved.
