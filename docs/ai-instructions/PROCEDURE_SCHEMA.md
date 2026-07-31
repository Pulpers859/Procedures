# Procedure Schema

Procedure content lives in `Procedures/Resources/procedures.json`.

Each procedure should follow this structure:

```json
{
  "id": "string",
  "title": "string",
  "category": "Airway | Vascular Access | Thoracic | Cardiac / Resuscitation | Neuro | Regional Anesthesia | Wound / Soft Tissue | Ultrasound-Guided | Other",
  "difficulty": "Basic | Intermediate | Advanced | Rare-Crash",
  "reviewTime": "60 sec | 2 min | 3 min | 4 min | 5 min | Deep",
  "setting": ["ED", "ICU", "Trauma", "Peds"],
  "lastReviewed": "YYYY-MM-DD",
  "version": "0.1.0",
  "reviewerStatus": "Draft | Needs Clinical Review | Internally Reviewed | Externally Reviewed | Institution-Specific",
  "tags": ["search", "synonyms"],
  "sections": {
    "shiftMode": [],
    "indications": [],
    "contraindications": [],
    "anatomy": [],
    "equipment": [],
    "positioning": [],
    "steps": [],
    "ultrasound": [],
    "confirmation": [],
    "troubleshooting": [],
    "complications": [],
    "aftercare": [],
    "documentation": [],
    "seniorPearls": [],
    "references": []
  }
}
```

## Dosing Schema

Two dosing blocks exist and mean different things. Rendering one as the other
puts a target dose under a "max dose" heading or vice versa.

`dosing` (`ProcedureDosing`) is a local-anesthetic safety **ceiling** - a
number never to exceed. It renders `MaxDoseCalculatorCard` and is
release-blocking for `Regional Anesthesia` category records; it is optional
for any other record that also injects local anesthetic (infiltration for
laceration repair, incision and drainage, etc.).

```json
"dosing": {
  "agents": [
    {"name": "Lidocaine plain", "maxMgPerKg": 4.5, "absoluteMaxMg": 300},
    {"name": "Bupivacaine plain", "maxMgPerKg": 2.5, "absoluteMaxMg": 175}
  ],
  "cumulativeWarning": "string - must state each agent is a fraction of its own ceiling, not a shared pool",
  "caveats": ["string - must include the site-of-injection absorption caveat and the owner-policy caveat"],
  "monitoring": ["string"],
  "rescueCardID": "local_anesthetic_systemic_toxicity"
}
```

Governance rules enforced by `scripts/validate_procedures.py` and
`scripts/tests/test_dosing_validation.py`:

- Every agent named anywhere in the record's steps/equipment/prose must appear
  in `dosing.agents` with a bound, or must not be named at all
  (`unbounded_agent_issues`). Do not invent a ceiling to satisfy this - remove
  the agent from prose instead, and explain why in `seniorPearls`.
- A record may only offer agents whose ceiling its own stated volume fits
  under at the 50 kg reference weight (`regional_dosing_issues` for
  `Regional Anesthesia`). A block whose volume doesn't fit any agent's ceiling
  needs a volume-free prose warning instead of a `dosing` block.
- Do not put two agents' percentages/volumes on the same textual line -
  `prose_dose_ceiling_issues` cannot tell which strength belongs to which
  agent and will misattribute the arithmetic.
- `cumulativeWarning` must frame toxicity as additive fractions of separate
  ceilings, never as agents sharing one number of milligrams.

`medicationDosing` (`ProcedureMedicationDosing`) is a systemic-medication
**target** dose (currently RSI induction/paralytic agents) - a dose to hit, not
a ceiling to stay under. It renders `MedicationDosingCard` under Shift Mode.

```json
"medicationDosing": {
  "indication": "string",
  "medications": [{"name": "string", "doseMgPerKg": 1.5, "notes": "string"}],
  "selectionGuidance": ["string"],
  "inductionRequirement": "string"
}
```

## Content rules

- Shift Mode should be short and actionable.
- Equipment should render as a checklist.
- Steps should be ordered.
- Complications should include practical rescue thinking.
- Documentation should be concise and chart-ready.
- References should be included but not dumped into Shift Mode.

## Visual Asset Metadata

Procedure content may include a `visualAssets` array. This is the structure that powers the premium visual landmark card.

```json
"visualAssets": [
  {
    "id": "chest_tube_safe_triangle",
    "kind": "Danger Zone",
    "title": "Chest tube safe triangle",
    "subtitle": "Visual slot for safe triangle, over-the-rib entry, and areas to avoid.",
    "assetName": "chest_tube_safe_triangle.png",
    "systemImage": "stethoscope",
    "caption": "Use one focused reviewed visual per teaching point. Split separate misses into separate visualAssets.",
    "clinicalWarning": "Do not place too low or under the rib."
  }
]
```

Allowed `kind` values:

- `Landmark`
- `Probe Position`
- `Danger Zone`
- `Confirmation`
- `Setup`

If `assetName` is null, the app renders a premium placeholder. When final artwork is available, add the bundled image file and set `assetName`.

Keep the visual layer restrained but not artificially single-image. A procedure
may have multiple `visualAssets` when each one prevents a distinct miss, such as
landmark geometry, danger-zone avoidance, or ultrasound confirmation. Do not
force those into one cramped diagram.

## Rescue Card Schema

Rescue cards live in `Procedures/Resources/rescue_cards.json`.

Required fields:

```json
{
  "id": "post_intubation_hypotension",
  "title": "Post-intubation hypotension",
  "acuity": "Crash",
  "relatedProcedureIDs": ["endotracheal_intubation"],
  "trigger": [],
  "immediateMoves": [],
  "reassess": [],
  "avoid": [],
  "tags": [],
  "lastReviewed": "YYYY-MM-DD",
  "version": "0.1.0",
  "reviewerStatus": "Draft | Needs Clinical Review | Internally Reviewed | Externally Reviewed | Institution-Specific",
  "references": []
}
```

Rescue cards must remain problem-first. They are not procedure complications paragraphs. They should answer: what is happening, what should I do now, what should I reassess, and what mistake should I avoid?

## Kit Schema

Kits live in `Procedures/Resources/kits.json`.

Required fields:

```json
{
  "id": "central_line_kit",
  "title": "Central Line Kit",
  "subtitle": "Standard triple-lumen CVC tray",
  "category": "Vascular Access",
  "relatedProcedureIDs": ["internal_jugular_cvc", "subclavian_cvc", "femoral_cvc"],
  "tags": ["cvc", "central line", "triple lumen"],
  "lastReviewed": "YYYY-MM-DD",
  "version": "0.1.0",
  "reviewerStatus": "Draft | Needs Clinical Review | Internally Reviewed | Externally Reviewed | Institution-Specific",
  "inKit": ["ChloraPrep", "Lidocaine 1%", "Guidewire", "Dilator", "Catheter"],
  "outsideKit": ["Sterile gown", "Sterile gloves", "Ultrasound probe cover", "Saline flushes"],
  "commonlyForgotten": ["Biopatch", "Extra chlorhexidine"],
  "patientSetup": ["Supine", "Trendelenburg if tolerated"],
  "sterileSetup": ["Full sterile drape", "Prep widely"],
  "backupEquipment": ["Arterial line kit (for rescue)"],
  "references": []
}
```
