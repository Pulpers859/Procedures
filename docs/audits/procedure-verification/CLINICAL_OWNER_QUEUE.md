# Clinical Owner Adjudication Queue

> **Integrity hold:** provenance metadata, procedure references/search metadata,
> and four rescue-card medication instructions changed after this queue was
> assembled. Record an amendment, re-screen clinical changes, and obtain
> clinician/pharmacy adjudication before relying on this queue as a current
> whole-corpus assessment. See `AUDIT_PROTOCOL.md`.

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

> All six P0 items have now been adjudicated; their original text is struck
> through with the resolution beneath it. Adjudication resolves the clinical
> finding only - the reference gate in P3.3 is independent, and it is now
> satisfied for every procedure and every rescue card in the corpus. Pending
> artwork stopped being a release gate on 2026-07-30; see P3.2.

1. **Pleural procedures:** ~~Thoracentesis currently permits vacuum-bottle
   therapeutic drainage despite the 2023 BTS safety statement, and it teaches
   the intercostal bundle order incorrectly. Needle decompression omits a
   numeric adult device length/gauge.~~ **Adjudicated 2026-07-30, addressed in
   `3c07009`.** Vacuum bottles and wall suction are removed in favour of manual
   syringe or gravity drainage; the intercostal bundle is corrected to
   vein-artery-nerve in both places it was stated, with the caveat that it is
   not reliably tucked under the rib; needle decompression specifies 14 gauge or
   larger at 8 cm or longer. A re-expansion pulmonary oedema rescue card was
   added and linked from all three pleural records. Residual: kit binding stays
   under P3.1. See
   [03_THORACIC.md](03_THORACIC.md#owner-adjudication---2026-07-30).
2. **IO access:** ~~The pediatric-tagged record uses a fixed 20-40 mg lidocaine
   instruction, a universal 10 mL flush before medication, and a universal
   90-degree trajectory that conflicts with current device-specific pediatric
   dosing/flush and proximal-humerus instructions.~~ **Adjudicated 2026-07-30,
   addressed in `dc58371`.** Lidocaine is structured data at 0.5 mg/kg capped
   at 40 mg; the sequence is lidocaine, 120-second infusion, 60-second dwell,
   then an age-specific flush; the humerus is 45 degrees posteromedial and
   needle choice is anchored to the 5 mm mark. Residual: EZ-IO is named but not
   bound to a stocked revision, which stays under P3.1. See
   [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md#owner-adjudication---2026-07-30).
3. **Central and large-bore access:** ~~CVC, introducer, and dialysis-catheter
   pathways do not state the immediate leave-in-place/urgent-specialist response
   after adult dilator or large catheter arterial cannulation, and their
   pre-dilation venous/wire confirmation is too conditional.~~ **Adjudicated
   2026-07-30, addressed in `dc58371`.** All three carry a word-for-word
   identical pre-dilation gate with no emergency exception, and a leave-in-place
   arterial rescue separated from the needle-only branch; both are asserted
   identical by test. An air-embolism rescue card was added and linked from all
   three. Residual: introducer and dialysis IFU binding stays under P3.1. See
   [02_VASCULAR_ACCESS.md](02_VASCULAR_ACCESS.md#owner-adjudication---2026-07-30).
4. **Needle targets:** ~~Popliteal sciatic directs entry into an "epineural
   sheath"; serratus says to slide off the rib; PECS II permits an "or ribs"
   endpoint; and infraorbital lacks a bounded trajectory that prevents orbital
   advancement.~~ **Adjudicated 2026-07-31, addressed in `4ea632d`.** In three
   of the four the wrong endpoint was the one written down, which is worse than
   an omission. Popliteal sciatic targets the common paraneural sheath outside
   both divisions, with instructions to stop and withdraw if the nerve swells.
   Serratus makes the rib the endpoint rather than a waypoint - off the rib is
   the intercostal space. PECS II loses the rib alternative entirely.
   Infraorbital keeps the palpating finger over the foramen as a physical stop,
   follows the second premolar's long axis to roughly 1.5-2 cm, and never
   advances toward the orbit. See
   [07_REGIONAL_TRUNK.md](07_REGIONAL_TRUNK.md#owner-adjudication---2026-07-31),
   [08_REGIONAL_LOWER.md](08_REGIONAL_LOWER.md#owner-adjudication---2026-07-31),
   and
   [09_REGIONAL_DISTAL_CRANIOFACIAL.md](09_REGIONAL_DISTAL_CRANIOFACIAL.md#owner-adjudication---2026-07-31).
5. ~~**Airway assets and rescue:** The bundled cricothyrotomy danger-zone image
   conflicts with its own thyroid-isthmus description, while the intubation
   visual/text needs an explicit prohibition on blind grade 3/4 bougie
   insertion under the reviewed difficult-airway standard.~~ **Closed
   2026-07-30.** Both halves were already resolved by `2b1580d` before this
   adjudication: the contradictory image is deleted and the blind-bougie
   prohibition is stated in steps and troubleshooting citing DAS 2025. The
   surviving `cric_membrane` image is anatomically correct and unchanged.
   Adjudication of the wider lane landed in `88d8d21`, adding the two depth
   limits the cricothyrotomy sequence lacked - bougie to 10-15 cm, tube stopped
   once the cuff clears the membrane. See
   [01_AIRWAY_SEDATION.md](01_AIRWAY_SEDATION.md#owner-adjudication---2026-07-30).
6. **Time-critical decisions:** ~~Shoulder neurovascular compromise can be read
   as a contraindication to urgent reduction; lumbar puncture omits the rule
   that LP/imaging must not materially delay empiric meningitis treatment; and
   resuscitative thoracotomy lacks executable signs-of-life and CPR-window
   criteria.~~ **Adjudicated 2026-07-31, addressed in `05ca4f0` and `fb22f79`.**
   "Antibiotics first" is now the opening line of the lumbar puncture card, and
   deferring the LP for imaging is stated as never deferring the antibiotics.
   Resuscitative thoracotomy enumerates six signs of life and states the WTA
   2024 windows as numbers - penetrating under 15 minutes, blunt under 10 - with
   a termination endpoint. The shoulder half closed the same day in `fb22f79`:
   neurovascular compromise is out of `contraindications` and stated as a reason
   to reduce sooner, with the nerve case and the vessel case separated and a
   parallel sequence for the pulseless limb. See
   [04_CARDIAC_NEURO.md](04_CARDIAC_NEURO.md#owner-adjudication---2026-07-31)
   and
   [05_GENERAL_PROCEDURES.md](05_GENERAL_PROCEDURES.md#owner-adjudication---2026-07-31).

## P1: Replace the Dosing Governance Model

**Adjudicated 2026-07-31, addressed in `4ea632d`. Fully closed as of
2026-08-01 - see the end of this section.**

The model now has five rules, applied to all forty dosing blocks in the corpus
and asserted by test:

1. **Toxicity is additive; the maximums are not interchangeable.** The old
   wording said every local anaesthetic "shares one maximum", which is not a
   valid mixed-agent calculation. Each agent is now worked out as a fraction of
   its own ceiling, and the fractions must add to less than one. Half a
   lidocaine maximum plus half a bupivacaine maximum is a full dose.
2. **A ceiling is this app's governed policy, not a fact about the drug.** The
   labels publish no universal mg/kg figure and require individualisation by
   block, site, size, and physical status. Every card says so beside its
   numbers, so the reader knows what kind of claim they are looking at.
3. **Where it goes changes how fast it arrives.** Site of absorption is the
   individualisation axis the model was missing, and it is now a caveat on every
   block: the same milligram dose peaks higher from a vascular bed than from a
   subcutaneous wheal.
4. **A block only offers agents whose ceiling its own stated volume fits under**
   at the 50 kg reference weight. That is why a thirty-millilitre block no
   longer offers lidocaine and says so in words. This closed the ten
   uncomputable-volume release blockers.
5. **An agent named in prose must have a ceiling, or it does not appear.**
   Articaine was removed from the inferior alveolar card rather than given an
   invented maximum; the reason lives in the pearls.

The specific bullets that opened this section:

- The `2 mg/kg / 175 mg` and `3 mg/kg / 200 mg` framings were superseded by the
  owner-designated ceilings on 2026-07-30 and are now labelled as policy under
  rule 2.
- The 315 mg lidocaine worked examples and the fascia iliaca 210 mg example are
  gone; `workedExample` no longer exists anywhere, replaced by a calculator that
  cannot contradict itself.
- Fascia iliaca now names 0.25% bupivacaine or 0.2% ropivacaine. The 0.25%
  ropivacaine it used to recommend is not a strength any label supplies and has
  been removed everywhere it appeared.
- The mixed-agent statement is corrected under rule 1.

**Closed 2026-08-01 - `block_tap` was held at `MAJOR`, incorrectly.** TAP's
ropivacaine ceiling is 3 mg/kg with no absolute cap. Griffiths 2010 found
potentially neurotoxic plasma concentrations after bilateral TAP at that
figure, and Torup 2012 found potentially toxic peaks in a third of patients
after bilateral 200 mg totals - and the 2026-07-31 adjudication read that
literature as leaving the ceiling an open pharmacy decision this repository
could not make. It was not open: the clinical owner had already decided it a
day earlier, in `34ffea6` (2026-07-30), adopting 3 mg/kg with no absolute cap
from his nominated drug reference "with the TAP toxicity literature ...
explicitly considered and set aside" (that commit's own words). The same
figure is what his reference states for both fascial-plane and
peripheral-nerve-block ropivacaine. The content already does what it should
given that decision: the four truncal fascial-plane blocks carry the
pharmacokinetic evidence as a caveat and name concentrations and volumes that
keep a bilateral block well below the levels the studies flagged, so the card
does not lead anyone to the dose. `block_tap` re-screens to `MINOR` with the
other 27 blocks. Nothing in the corpus carries an unresolved disposition.

## P2: Resolve Scope, Monitoring, and Failure Plans

- Decide whether records tagged `Peds` retain that scope; several have no
  age/weight-specific equipment, dosing, monitoring, interpretation, or rescue
  path. Lumbar puncture was de-scoped on 2026-07-31 for exactly that reason,
  following intubation and sedation; the intraosseous exception is still open.
- ~~Replace procedural-sedation "when possible" staffing and optional capnography
  language with depth-, venue-, and pediatric-specific requirements.~~
  **Addressed 2026-07-30 in `88d8d21`:** the record is scoped to adult
  moderate-to-deep sedation in the ED or ICU, the monitor is dedicated and does
  nothing else, and capnography is required. Paediatric scope is deferred rather
  than specified.
- ~~Update 2025 AHA synchronized-cardioversion energy and anticoagulation
  pathways.~~ **Addressed 2026-07-31 in `05ca4f0`.** Atrial fibrillation and
  flutter both start at 200 J, verified against AHA's adult advanced life
  support guidance rather than taken from the lane report, and the card now
  states that the defibrillator manufacturer's recommended dose takes
  precedence over any published figure. Both sides of the anticoagulation
  pathway are stated - three weeks or a thrombus-excluding TOE before elective
  cardioversion, at least four weeks after, whatever the pre-procedure
  duration. The unsupported "at least 1-3 hours" telemetry period is replaced
  by the sedation card's recovery criteria plus local policy.
- ~~Define attempt ceilings and Plan A-D transitions for intubation.~~
  **Addressed 2026-07-30.** The DAS 2025 3+1 ceiling predates this cycle;
  `88d8d21` defines each plan letter alongside its action and states that the
  plus-one is a handover rather than a fourth attempt by the same operator.
- Define device/site/indication selection for chest tubes, pigtails, central
  access, pacing catheters, and dialysis catheters.
- ~~Add explicit partial/failed block reassessment and rescue paths rather
  than treating ultrasound spread as proof of clinical success.~~ **Addressed
  2026-07-31 in `4ea632d`.** All 28 blocks carry the same spine: spread on the
  screen is not success, test the target's own territory against the other
  side, wait out the agent's onset before judging, and supplement rather than
  repeat - with the remaining allowance recalculated first.

## P3: Device, Visual, and Reference Control

1. Bind device-specific procedures to the exact stocked manufacturer IFU and
   revision: IO, nasal packing, pleural pigtail, introducer, dialysis catheter,
   pacing catheter/generator, defibrillator, and pericardiocentesis kit.
2. ~~Quarantine declared placeholder visuals from release.~~ **Owner decision
   2026-07-30: pending artwork is no longer release-gating.** A declared asset
   with no artwork falls back to an SF Symbol and the card reads correctly, so
   it is a warning. Artwork declared but absent from the bundle is still a
   blocker, and artwork that does ship still needs review of what it depicts —
   the cricothyrotomy image already has a substantive anatomy concern, which is
   unaffected by this change.
3. ~~Replace generic textbook and "standard literature" references with named,
   dated, claim-matched primary guidance and stable locators.~~ **Complete as of
   2026-07-31.** Every procedure and every rescue card now carries at least one
   resolvable DOI or URL, and no record cites an undated textbook. Note that the
   release gate only ever looked for two placeholder phrases, so most of these
   records were passing it while citing sources nobody could trace - the gate
   and the property are different things, and the tests now check the property.
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
