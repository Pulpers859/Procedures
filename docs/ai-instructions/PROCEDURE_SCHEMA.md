# Procedure Schema

Procedure content lives in `Procedures/Resources/procedures.json`.

Each procedure should follow this structure:

```json
{
  "id": "string",
  "title": "string",
  "category": "Airway | Vascular Access | Thoracic | Cardiac / Resuscitation | Neuro | Regional Anesthesia | Wound / Soft Tissue | Ultrasound-Guided | Other",
  "difficulty": "Basic | Intermediate | Advanced | Rare-Crash",
  "reviewTime": "60 sec | 2 min | 5 min | Deep",
  "setting": ["ED", "ICU", "Trauma", "Peds"],
  "lastReviewed": "YYYY-MM-DD",
  "version": "0.1.0",
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
    "caption": "Use one reviewed visual that prevents the bad miss. Avoid decorative gallery bloat.",
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
  "references": []
}
```

Rescue cards must remain problem-first. They are not procedure complications paragraphs. They should answer: what is happening, what should I do now, what should I reassess, and what mistake should I avoid?
