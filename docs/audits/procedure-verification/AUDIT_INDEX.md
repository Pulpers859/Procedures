# Procedure Verification Audit Index

> **Integrity:** every audited procedure still matches the bytes that were screened, per `AUDIT_LEDGER.json`.

> **Scope:** this packet screened procedures only. No kit and no rescue card has a per-record evidence section in any lane report, and the rescue-card snapshot the protocol names was never committed, so no rescue-card baseline can be recovered. Nothing here attests to either.

## Result

- Audited procedures: **55/55**.
- Proposed `STOP-SHIP`: **0** (28 at audit; 11 re-screened on 2026-07-30 and 17 on 2026-07-31).
- Proposed `MAJOR`: **1** (27 at audit; 2 re-screened to `MINOR` on 2026-07-30 and 25 on 2026-07-31, and one STOP-SHIP re-screened down to `MAJOR` rather than clear - `block_tap`, whose ropivacaine ceiling remains an open pharmacy decision).
- Re-screened `MINOR` after owner adjudication: **54** (all nine lanes).
- Corpus SHA-256: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`.
- Audit date: 2026-07-18.

Every disposition is an AI-assisted discrepancy-screen result, not a
clinical approval. Declared visuals without artwork stopped being a release
gate on 2026-07-30 by owner decision, so a disposition driven by a pending
visual alone no longer reflects a release blocker; consult the individual
report before assigning remediation priority.

## Lane Reports

- [01 Airway Sedation](01_AIRWAY_SEDATION.md)
- [02 Vascular Access](02_VASCULAR_ACCESS.md)
- [03 Thoracic](03_THORACIC.md)
- [04 Cardiac Neuro](04_CARDIAC_NEURO.md)
- [05 General Procedures](05_GENERAL_PROCEDURES.md)
- [06 Regional Upper](06_REGIONAL_UPPER.md)
- [07 Regional Trunk](07_REGIONAL_TRUNK.md)
- [08 Regional Lower](08_REGIONAL_LOWER.md)
- [09 Regional Distal Craniofacial](09_REGIONAL_DISTAL_CRANIOFACIAL.md)

## Procedure Coverage

| Category | Procedure | Disposition | Report |
|---|---|---|---|
| Airway | `cricothyrotomy` - Cricothyrotomy | `MINOR` | [01_AIRWAY_SEDATION.md](01_AIRWAY_SEDATION.md) |
| Airway | `endotracheal_intubation` - Endotracheal Intubation | `MINOR` | [01_AIRWAY_SEDATION.md](01_AIRWAY_SEDATION.md) |
| Cardiac / Resuscitation | `pericardiocentesis` - Pericardiocentesis | `MINOR` | [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) |
| Cardiac / Resuscitation | `resuscitative_thoracotomy` - Resuscitative Thoracotomy | `MINOR` | [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) |
| Cardiac / Resuscitation | `synchronized_cardioversion` - Synchronized Cardioversion | `MINOR` | [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) |
| Cardiac / Resuscitation | `transvenous_pacemaker` - Transvenous Pacemaker | `MINOR` | [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) |
| Neuro | `lumbar_puncture` - Lumbar Puncture | `MINOR` | [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) |
| Other | `anterior_nasal_packing` - Anterior Nasal Packing | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Other | `knee_arthrocentesis` - Knee Arthrocentesis | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Other | `lateral_canthotomy` - Lateral Canthotomy & Cantholysis | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Other | `paracentesis` - Paracentesis | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Other | `peritonsillar_abscess_drainage` - Peritonsillar Abscess Drainage | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Other | `shoulder_reduction` - Shoulder Reduction (Anterior) | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Regional Anesthesia | `block_auricular` - Auricular Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_deep_peroneal` - Deep Peroneal Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `digital_nerve_block` - Digital Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `fascia_iliaca_block` - Fascia Iliaca Compartment Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_femoral_nerve` - Femoral Nerve Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_inferior_alveolar` - Inferior Alveolar Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_infraorbital` - Infraorbital Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_interscalene` - Interscalene Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_median_nerve` - Median Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_mental` - Mental Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_pecs` - PECS I / II Block | `MINOR` | [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md) |
| Regional Anesthesia | `block_peng` - PENG (Pericapsular Nerve Group) Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_popliteal_sciatic` - Popliteal Sciatic Nerve Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_raptir` - RAPTIR (Infraclavicular) Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_radial_nerve` - Radial Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_saphenous_nerve` - Saphenous Nerve (Adductor Canal) Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_serratus_anterior` - Serratus Anterior Plane Block | `MINOR` | [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md) |
| Regional Anesthesia | `block_superficial_cervical_plexus` - Superficial Cervical Plexus Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_superficial_peroneal` - Superficial Peroneal Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_superior_alveolar` - Superior Alveolar Nerve Block (Supraperiosteal) | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_supraclavicular` - Supraclavicular Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Regional Anesthesia | `block_supraorbital` - Supraorbital Nerve Block | `MINOR` | [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md) |
| Regional Anesthesia | `block_sural_nerve` - Sural Nerve Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_thoracic_esp` - Thoracic Erector Spinae Plane (ESP) Block | `MINOR` | [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md) |
| Regional Anesthesia | `block_tibial_nerve` - Tibial Nerve Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_transgluteal_sciatic` - Transgluteal / Proximal Sciatic Nerve Block | `MINOR` | [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md) |
| Regional Anesthesia | `block_tap` - Transversus Abdominis Plane (TAP) Block | `MAJOR` | [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md) |
| Regional Anesthesia | `block_ulnar_nerve` - Ulnar Nerve Block | `MINOR` | [06_REGIONAL_UPPER.md](06_REGIONAL_UPPER.md) |
| Sedation & Analgesia | `procedural_sedation` - Procedural Sedation | `MINOR` | [01_AIRWAY_SEDATION.md](01_AIRWAY_SEDATION.md) |
| Thoracic | `needle_decompression` - Needle Decompression | `MINOR` | [03_THORACIC.md](03_THORACIC.md) |
| Thoracic | `pigtail_catheter` - Pigtail Pleural Catheter | `MINOR` | [03_THORACIC.md](03_THORACIC.md) |
| Thoracic | `thoracentesis` - Thoracentesis | `MINOR` | [03_THORACIC.md](03_THORACIC.md) |
| Thoracic | `thoracostomy_chest_tube` - Thoracostomy / Chest Tube | `MINOR` | [03_THORACIC.md](03_THORACIC.md) |
| Ultrasound-Guided | `ultrasound_guided_piv` - Ultrasound-Guided Peripheral IV | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Vascular Access | `arterial_line` - Arterial Line | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Vascular Access | `central_venous_catheter` - Central Venous Catheter | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Vascular Access | `dialysis_catheter_vascath` - Dialysis Catheter (Vas-Cath) | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Vascular Access | `intraosseous_access` - Intraosseous (IO) Access | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Vascular Access | `introducer_sheath_cordis` - Introducer Sheath (Cordis) | `MINOR` | [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md) |
| Wound / Soft Tissue | `abscess_incision_drainage` - Abscess Incision & Drainage | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Wound / Soft Tissue | `foreign_body_removal_soft_tissue` - Foreign Body Removal (Soft Tissue) | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |
| Wound / Soft Tissue | `laceration_repair` - Laceration Repair (Suturing) | `MINOR` | [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md) |

## Release Boundary

No `reviewerStatus` was changed. A qualified clinical owner must adjudicate
each finding against the exact content version, local formulary, stocked
devices and IFUs, credentialing, and institutional policy before any record
can be marked reviewed or released.
