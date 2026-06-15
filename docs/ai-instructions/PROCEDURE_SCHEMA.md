# Procedure Schema

Procedure content lives in `ProcedureSTAT/Resources/procedures.json`.

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
