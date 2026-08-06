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
  `seniorPearls`, plus `majorBlockMonitoring` and the dosing blocks). Changing
  one of those after a sign-off revokes it.
- `tags` are **not** hashed. When an edit costs a procedure its place in search
  - see `check_search_ranking.py` - a tag can carry the missing term back
  without disturbing a sign-off.

### What the two exports repeat, and why

The device is not a fork of the content, but for a long time it behaved like
one: it could send corrections to the repo and had no way to learn what the
repo did with them. Three costs came out of that, and each has its own fix.

**Already-landed work is re-sent.** A local edit is an override that survives
until the repo takes it - and nothing ever retired one, so a correction merged
and shipped months ago still rode in every export as a duplicate of the bundled
text. `ProcedureEditStore.retireLandedEdits()` drops any override whose text is
now character-identical to what shipped, and `UserDataStore.landedReviewKeys`
leaves promoted sign-offs out of the review export. **The bundle is the
acknowledgement**: a build that already contains the correction is proof the
repo took it, so no receipt or watermark is needed - and none could be trusted,
since only the bundle knows what was accepted. Both need a rebuild to take
effect, which is the same rebuild that shows the merged content anyway.

**A sign-off is not all-or-nothing when the material set grows.** Adding a
field bumps `FINGERPRINT_VERSION`, and every prior digest becomes
incomparable. `SECTIONS_BY_VERSION` keeps what each version hashed, so the
promoter can recompute an older digest against today's content and answer the
question the version number cannot: *the fields you signed are unchanged; only
`seniorPearls` is outside it - re-review that section.* Still a refusal, never
a promotion - the added fields genuinely have not been reviewed - but the
repair is one section rather than the whole record.

**Some hashed fields cannot be reached from the app.**
`majorBlockMonitoring`, `dosing`, and `medicationDosing` are material, are not
editable, and are not carried by the edit export. A device on an older bundle
produces a digest that no amount of re-reviewing will fix. The promoter probes
those fields on a mismatch and says so: rebuild, then sign off.

### Reading a blind merge

`apply_local_edits.py` compares the export's `baseMaterialFingerprint` against
the shipping record and prints **BLIND MERGE** for any edit written against
content the repo has since changed. The merge is a whole-section overwrite, so
there is no conflict to notice: anything the repo gained after the device's
last build is discarded silently. It is reported, never refused - the reviewer
is the authority on their own wording - but a flagged procedure's diff has to
be read as a merge, and any repo line that disappears from it is a line nobody
chose to remove.

## Historical Notes
- `audits/AUDIT_AND_NEXT_STEPS.md` - earlier audit log and roadmap snapshots kept for reference, not as the primary handoff file
- `audits/PATCH_NOTES_0_4_RESCUE_JSON_VISUALS.md` - imported patch notes for the rescue JSON / visual-asset architecture update
