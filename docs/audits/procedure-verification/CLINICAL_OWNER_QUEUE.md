# Clinical Owner Adjudication Queue

## Status

This queue synthesizes the nine fingerprinted AI discrepancy reports. It is not
a substitute for reading the per-procedure evidence, and it does not authorize
content changes or clinical approval.

Audited `procedures.json` SHA-256:
`3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`.

Evidence lanes: [airway/sedation](01_AIRWAY_SEDATION.md),
[vascular access](02_VASCULAR_ACCESS.md), [thoracic](03_THORACIC.md),
[cardiac/neuro](04_CARDIAC_NEURO.md), [general procedures](05_GENERAL_PROCEDURES.md),
[regional upper](06_REGIONAL_UPPER.md), [regional trunk](07_REGIONAL_TRUNK.md),
[regional lower](08_REGIONAL_LOWER.md), and
[regional distal/craniofacial](09_REGIONAL_DISTAL_CRANIOFACIAL.md).

## P0: Remove Direct Harm Pathways Before Broader Editing

1. **Pleural procedures:** Thoracentesis currently permits vacuum-bottle
   therapeutic drainage despite the 2023 BTS safety statement, and it teaches
   the intercostal bundle order incorrectly. Needle decompression omits a
   numeric adult device length/gauge. See [03_THORACIC.md](03_THORACIC.md).
2. **IO access:** The pediatric-tagged record uses a fixed 20-40 mg lidocaine
   instruction, a universal 10 mL flush before medication, and a universal
   90-degree trajectory that conflicts with current device-specific pediatric
   dosing/flush and proximal-humerus instructions. See
   [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md).
3. **Central and large-bore access:** CVC, introducer, and dialysis-catheter
   pathways do not state the immediate leave-in-place/urgent-specialist response
   after adult dilator or large catheter arterial cannulation, and their
   pre-dilation venous/wire confirmation is too conditional. See
   [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md).
4. **Needle targets:** Popliteal sciatic directs entry into an "epineural
   sheath"; serratus says to slide off the rib; PECS II permits an "or ribs"
   endpoint; and infraorbital lacks a bounded trajectory that prevents orbital
   advancement. See [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md),
   [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md), and
   [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md).
5. **Airway assets and rescue:** The bundled cricothyrotomy danger-zone image
   conflicts with its own thyroid-isthmus description, while the intubation
   visual/text needs an explicit prohibition on blind grade 3/4 bougie
   insertion under the reviewed difficult-airway standard. See
   [01_AIRWAY_SEDATION.md](01_AIRWAY_SEDATION.md).
6. **Time-critical decisions:** Shoulder neurovascular compromise can be read as
   a contraindication to urgent reduction; lumbar puncture omits the rule that
   LP/imaging must not materially delay empiric meningitis treatment; and
   resuscitative thoracotomy lacks executable signs-of-life and CPR-window
   criteria. See [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md) and
   [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md).

## P1: Replace the Dosing Governance Model

The new regional-anesthesia dosing blocks are useful structurally but are not
ready for clinical reliance:

- `2 mg/kg / 175 mg` bupivacaine and `3 mg/kg / 200 mg` ropivacaine are framed
  as universal ceilings even though current labels require site- and
  patient-specific individualization and do not establish those exact universal
  pairs.
- Several lidocaine examples calculate 315 mg for a 70 kg patient while the same
  record declares a 300 mg absolute ceiling; the lower limit is not applied.
- Fascia iliaca uses 0.25% ropivacaine in its example without listing that
  concentration or defining a preparation, and it fails to apply its 200 mg
  absolute ceiling to the 70 kg calculation.
- The statement that different local anesthetics "share one maximum" is not a
  valid mixed-agent calculation. Toxicity is additive, but agents do not share
  one interchangeable mg or mg/kg ceiling.
- TAP evidence identified potentially toxic ropivacaine concentrations at doses
  the current record presents as within its maximum.

Required owners: regional anesthesiology and clinical pharmacy. Required output:
a versioned, formulary-specific policy for agent, formulation, concentration,
site, laterality, prior dosing, patient modifiers, monitoring, and LAST rescue.
The full evidence is in reports 06 through 09.

## P2: Resolve Scope, Monitoring, and Failure Plans

- Decide whether records tagged `Peds` retain that scope; several have no
  age/weight-specific equipment, dosing, monitoring, interpretation, or rescue
  path.
- Replace procedural-sedation "when possible" staffing and optional capnography
  language with depth-, venue-, and pediatric-specific requirements.
- Update 2025 AHA synchronized-cardioversion energy and anticoagulation pathways.
- Define attempt ceilings and Plan A-D transitions for intubation.
- Define device/site/indication selection for chest tubes, pigtails, central
  access, pacing catheters, and dialysis catheters.
- Add explicit partial/failed block reassessment and rescue paths rather than
  treating ultrasound spread as proof of clinical success.

## P3: Device, Visual, and Reference Control

1. Bind device-specific procedures to the exact stocked manufacturer IFU and
   revision: IO, nasal packing, pleural pigtail, introducer, dialysis catheter,
   pacing catheter/generator, defibrillator, and pericardiocentesis kit.
2. Quarantine declared placeholder visuals from release. Independently re-review
   existing artwork; the cricothyrotomy image already has a substantive anatomy
   concern.
3. Replace generic textbook and "standard literature" references with named,
   dated, claim-matched primary guidance and stable locators.
4. Require the clinical owner to sign the exact JSON and asset fingerprints;
   changing either invalidates prior approval.

## Recommended Human Review Order

1. Emergency medicine plus trauma/airway: P0 crash and time-critical records.
2. Regional anesthesiology plus pharmacy: all dosing and needle-target findings.
3. Critical care/pulmonary/vascular access: pleural and large-bore device paths.
4. Pediatrics: every record retaining `Peds` scope.
5. Ophthalmology, ENT, dental/maxillofacial, orthopedics, nephrology, and
   infectious diseases for their assigned procedure groups.
6. Clinical informatics/editorial review only after substantive decisions are
   resolved, followed by independent second-clinician sign-off.

No `reviewerStatus` should change until the applicable owner has reviewed the
exact revised content and the release validator passes.
