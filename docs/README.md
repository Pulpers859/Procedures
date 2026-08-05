# Documentation Index

## Live Project Docs
- `../PROJECT_HANDOFF.md` - repo identity, source-of-truth rules, Git/GitHub workflow, and next-agent operating instructions
- `AI_UI_UX_RESOURCE_EVALUATION_PLAYBOOK.md` - neutral framework for evaluating external UI/UX repos, libraries, reference sites, and agent skills for this app
- `CLAUDE_CODE_TOKEN_EFFICIENCY.md` - repo-specific guidance for improving Claude Code token efficiency without adding heavy permanent tooling
- `EXTERNAL_AGENT_RECONCILIATION.md` - standalone reconciliation note for multi-agent / multi-machine repo work
- `../AGENTS.md` - root Codex and general agent startup instructions
- `../CLAUDE.md` - root Claude Code memory loaded by the dedicated launcher
- `ai-instructions/AGENTS.md` - product-specific guidance for future coding agents
- `ai-instructions/PRODUCT_BRIEF.md` - app purpose, users, and non-goals
- `ai-instructions/PROCEDURE_SCHEMA.md` - source-of-truth JSON schema for bundled procedures
- `ai-instructions/VISUAL_ASSET_PRODUCTION_GUIDE.md` - workflow for creating, reviewing, bundling, and validating clinical procedure illustrations
- `visual-assets/GEMINI_WORKFLOW.md` - Gemini image-generation workflow for draft procedure illustrations
- `visual-assets/ANTIGRAVITY_WORKFLOW.md` - local Google Antigravity render lane for draft illustrations (discovery, CLI verbs, operating loop)
- `visual-assets/IMAGE_GENERATION_CONSTITUTION.md` - standing generation rules every prompt must obey (labels are nouns, placement over symmetry, direction via arrows); governs how images are made
- `visual-assets/CLINICAL_IMAGE_RUBRIC.md` - authoritative clinical-correctness rubric and per-image answer key for grading generated visuals (99% gate)
- `visual-assets/gemini_prompts.json` - shared prompt specs for AI-generated visual drafts (both render lanes)
- `../Procedures/Resources/procedures.json` - bundled procedure content
- `../Procedures/Resources/rescue_cards.json` - bundled rescue-card content
- `ai-instructions/SWIFT_ARCHITECTURE.md` - current runtime structure and data flow
- `../scripts/apply_local_edits.py` - merges edits exported from the app back into `procedures.json` as a reviewable diff (run **before** `apply_local_reviews.py`; see the round-trip below)
- `../scripts/apply_local_reviews.py` - promotes sign-offs exported from the app into `reviewerStatus` and `contentSource`, refusing any review whose content has changed since it was recorded
- `ai-instructions/TESTING_CHECKLIST.md` - manual verification checklist
- `AUTOMATED_TESTING_HANDOFF.md` - CI surfaces, evidence boundaries, and required commands
- `RELEASE_CONSTITUTION.md` - release authority and non-bypassable stop-ship gates
- `audits/procedure-verification/AUDIT_INDEX.md` - fingerprinted 55-procedure AI discrepancy-screen index and dispositions
- `audits/procedure-verification/CLINICAL_OWNER_QUEUE.md` - ranked human adjudication queue for direct hazards, dosing, scope, devices, visuals, and references
- `ai-instructions/XCTEST_GUIDE.md` - beginner guide for running and interpreting the `ProceduresTests` XCTest target
- `ai-instructions/UI_UX_RULES.md` - bedside UX direction and navigation rules
- `ai-instructions/SAFETY_AND_REVIEW_POLICY.md` - clinical safety/document review expectations
- `ai-instructions/HIGH_YIELD_NEXT_STEPS.md` - prioritized roadmap notes
- `templates/UI_UX_PLAYBOOK_AGENTS_SNIPPET.txt` - reusable AGENTS insert for other repos
- `templates/UI_UX_PLAYBOOK_AGENT_REQUEST.txt` - reusable prompt for UI/UX resource evaluation tasks
- `templates/ui-ux-resource-eval/SKILL.md` - portable local-skill template for other repos
- `../.claude/skills/procedures-handoff/SKILL.md` - fast repo orientation and task routing
- `../.claude/skills/procedures-content-audit/SKILL.md` - clinical content, schema, reference, and validator audit workflow

## Review Round-Trip

Content edited and signed off in the app comes back as **two separate
exports**, from two different sections of Review Center. Both are needed, and
the order is not interchangeable:

1. **Edits** -> Review Center > Edits > *Export Edits*
2. `python3 scripts/apply_local_edits.py <edits>.json` (add `--dry-run` first;
   it reports the retrieval cost of the edit before writing anything)
3. `python3 scripts/validate_procedures.py`
4. **Reviews** -> Review Center > Reviews > *Export Reviews*
5. `python3 scripts/apply_local_reviews.py <reviews>.json`
6. `python3 scripts/validate_procedures.py` and
   `python3 scripts/check_search_ranking.py`

**Edits must be applied before reviews.** A sign-off is a hash of the text as
the reviewer saw it, which means the *edited* text. Promote first and every
sign-off is refused with "content changed since this review" - correctly, but
the message points at the wrong cause and reads like a stale build.

Two consequences worth knowing before editing:

- Only the material sections are hashed (`shiftMode`, `contraindications`,
  `equipment`, `steps`, `confirmation`, `troubleshooting`, `complications`,
  plus the dosing blocks). Changing one of those after a sign-off revokes it.
- `tags` are **not** hashed. When an edit costs a procedure its place in search
  - see `check_search_ranking.py` - a tag can carry the missing term back
  without disturbing a sign-off.

## Historical Notes
- `audits/AUDIT_AND_NEXT_STEPS.md` - earlier audit log and roadmap snapshots kept for reference, not as the primary handoff file
- `audits/PATCH_NOTES_0_4_RESCUE_JSON_VISUALS.md` - imported patch notes for the rescue JSON / visual-asset architecture update
