# Airway and Sedation Procedure Verification Audit

- Audit date: 2026-07-18
- Assigned IDs: `endotracheal_intubation`, `cricothyrotomy`, `procedural_sedation`
- Audited procedures SHA-256: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Boundary: AI-assisted discrepancy screening only. This report is not clinical approval, credentialing, or an institutional protocol.

## `endotracheal_intubation` - Endotracheal Intubation

**Screening disposition: `STOP-SHIP`** because a declared visual is both a release-blocking placeholder and contains a bougie instruction that conflicts with current difficult-airway guidance. Additional `MAJOR` gaps require clinician review.

### Source-standard summary

Current adult guidance prioritizes physiology-aware preparation, NIV or HFNC when appropriate, continuous oxygen delivery, first-attempt success, videolaryngoscopy when possible, explicit attempt limits and plan transitions, visualized tube passage plus sustained waveform capnography, and prompt post-intubation care. Pediatric guidance additionally requires age/size-specific equipment, tube selection, position, and cuff-pressure safeguards. The JSON is strong on preoxygenation, suction, role assignment, waveform capnography, supraglottic/FONA backup, and post-intubation analgesia/sedation, but it does not fully operationalize these standards.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `visualAssets[laryngoscope_view]`; `sections.steps`; `sections.troubleshooting` | The placeholder metadata says, briefly, "Bougie or video laryngoscopy for grade III-IV," and the steps say to use a bougie early for a limited view. DAS 2025 says blind bougie insertion with a Cormack-Lehane grade 3 or 4 view should be avoided because of trauma or misplacement risk. `assetName` is also `null`; both declared assets are unbundled placeholders, which the repo safety policy independently treats as stop-ship. | Remove the asset from release or replace it with clinician-approved art/copy. Decide the intended visualized bougie indications and explicitly prohibit blind grade 3/4 insertion if that is the adopted standard. |
| `MAJOR` | `sections.shiftMode`, `steps`, `troubleshooting` | There is no attempt ceiling or explicit Plan A-to-B-to-C-to-D transition trigger. DAS 2025 uses a maximum 3+1 intubation attempts, requires a meaningful change between attempts, and says to abandon an attempt and prioritize oxygenation if hypoxemia occurs. Repeated attempts are associated with airway trauma and physiologic complications. | Adopt a reviewed attempt/transition framework appropriate to ED/ICU practice and specify who makes the final attempt and when oxygenation ends an attempt. |
| `MAJOR` | `setting: [Peds]`; `sections.equipment`, `steps`, `confirmation`, `aftercare` | The entry is labeled for pediatrics but supplies only an adult-generic setup. It lacks age/size-specific tubes, blades, masks, adjuncts and rescue devices; pediatric tube position and cuff-pressure safeguards; and a pediatric airway failure pathway. AHA/AAP 2025 requires attention to pediatric ETT size, position, and cuff inflation pressure (usually below 20-25 cm H2O), and emphasizes skilled personnel and specialized equipment. | Either scope this record to adults or add a separately reviewed pediatric pathway with age/weight-specific equipment, dosing, confirmation, ventilation, and rescue rules. |
| `MAJOR` | No `dosing` object; `sections.equipment` and `steps` instruct induction plus paralysis | No structured induction-agent or NMBA dose, route, weight basis, repeat rule, contraindication, or physiology-specific adjustment is present. SCCM 2023 recommends a sedative-hypnotic when an NMBA is used and an NMBA when a sedative-hypnotic is used for RSI; DAS 2025 includes sufficient-dose RSI examples. The current record cannot be dose-checked and is especially incomplete for the declared pediatric scope. | Decide whether this bedside entry should contain a pharmacist/clinician-reviewed adult RSI dosing structure, a separate pediatric structure, or an explicit link to an institution-controlled medication protocol. |
| `MAJOR` | `sections.contraindications`, `positioning`, `equipment` - cervical-spine statements | The record reduces suspected cervical-spine injury mainly to manual in-line stabilization. The 2024 multisociety guideline recommends minimizing movement, jaw thrust rather than head tilt/chin lift, videolaryngoscopy where possible, removal of the anterior collar during attempts, and regular VL-with-immobilization training. | Replace the single-line treatment with an institution-approved cervical-spine airway pathway or clearly link to one. |
| `MAJOR` | `sections.references` | The references are two undated textbooks and a nonspecific phrase about "ACEP and critical care airway education resources." They are not traceable to editions, recommendations, URLs, or the current 2025 ACEP and DAS guidance and therefore cannot support the detailed bedside claims. | Attach current primary guidelines with publisher, title, year, and direct URL; retain textbooks only as edition-specific background references. |
| `MINOR` | `sections.documentation` | Documentation text omits devices/blades used, number of attempts, changes between attempts, difficulty encountered, and communication of a difficult airway to the patient/ongoing team. DAS 2025 calls for documenting assessment, equipment/techniques, difficulties, outcomes, and written/verbal communication after a difficult airway. | Define the minimum airway-procedure record and difficult-airway handoff fields. |

### Equipment, dosing, and monitoring assessment

The adult equipment list appropriately includes tested suction, oxygenation/BVM with PEEP, laryngoscopes, stylet/bougie, capnography, securement, supraglottic rescue, and eFONA access. It should be clinician-reviewed for a second-generation SGA, cuff-pressure measurement, and age/size-specific pediatric inventory. No structured dosing exists, so dose accuracy was not assessable. Continuous waveform capnography is correctly prioritized; the confirmation language should be reconciled with the DAS 2025 two-point check and pediatric low-flow limitations.

No additional material discrepancy was identified in the reviewed indications, core anatomy, general positioning, ultrasound-as-adjunct statement, complication list, aftercare, or senior pearls beyond the scope and pathway issues above. This means only that no further conflict was found in the sources reviewed.

### Reviewer questions and proposed disposition

1. Will the clinical owner make this adult-only or commission a full pediatric branch?
2. Which attempt-limit and failed-airway algorithm is authoritative for this app's ED/ICU audience?
3. Should medication dosing live here or in a separately governed institutional RSI protocol?
4. Can the visual copy and artwork be withheld until an airway expert approves it?

**Proposed reviewer disposition:** withhold from release until the stop-ship visual/bougie issue is removed and the major scope, dosing, failure-plan, and reference decisions are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- American College of Emergency Physicians, [Clinical Policy: Critical Issues in the Management of Adult Patients Requiring Endotracheal Intubation in the Emergency Department](https://www.acep.org/siteassets/sites/acep/media/clinical-policies/final-cp-pdfs/endotracheal-intubation-cp.pdf), 2025.
- Difficult Airway Society, [DAS guidelines for management of unanticipated difficult tracheal intubation in adults](https://doi.org/10.1016/j.bja.2025.10.006), 2025 guideline / 2026 print publication.
- Society of Critical Care Medicine, [Clinical Practice Guidelines for Rapid Sequence Intubation in the Critically Ill Adult Patient](https://www.sccm.org/clinical-resources/guidelines/guidelines/guidelines-rapid-sequence-intubation), 2023.
- American Heart Association and American Academy of Pediatrics, [Part 8: Pediatric Advanced Life Support](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/pediatric-advanced-life-support), 2025.
- DAS/AoA/BSOA/ICS/NACCS/Faculty of Prehospital Care/RCEM, [Airway management in patients with suspected or confirmed cervical spine injury](https://das.uk.com/guidelines/cervical-spine-injury/), 2024.

## `cricothyrotomy` - Cricothyrotomy

**Screening disposition: `STOP-SHIP`** because a bundled clinical visual presents internally contradictory and potentially wrong-site anatomy. The text also has `MAJOR` equipment and sequence gaps against current eFONA guidance.

### Source-standard summary

DAS 2025 treats adult emergency front-of-neck airway as Plan D after failed tracheal, supraglottic, and facemask oxygenation. It emphasizes declaring CICO, maximal neck extension when feasible, full neuromuscular block in that pathway, continued oxygen delivery from above, a trained single technique, a number 10 scalpel, bougie, 6.0 cuffed tracheal tube, suction, a vertical skin incision when membrane palpability is uncertain, controlled bougie advancement to 10-15 cm, waveform-capnography confirmation, securement, and post-event surgical review. The JSON has the correct rescue intent, core thyroid/cricoid landmarks, suction/BVM/capnography, bougie-tube concept, and strong securement language.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `visualAssets[cric_danger_zone]` and bundled `cric_danger_zone.png` | The image depicts the thyroid isthmus across the cricothyroid-membrane region while the JSON subtitle says the isthmus is inferior. It also visibly says "Stag midline." Cadaveric anatomy places the isthmus most often over the second-fourth tracheal rings, and DAS identifies the membrane between thyroid and cricoid cartilages. A visual used to locate an emergency incision cannot carry contradictory anatomy. | Remove the image from release pending review by an airway clinician/anatomist and commission corrected, source-traceable artwork. |
| `MAJOR` | `sections.indications`, `shiftMode`, `steps` | One sequence is used for both post-induction CICO and other upper-airway obstruction/facial-trauma scenarios. DAS 2025's adult eFONA sequence assumes failed Plans A-C, full neuromuscular block, and ongoing oxygen delivery from above; those assumptions may not fit every broader indication in this record. | Decide whether this is specifically an adult CICO/eFONA card or a broader emergency surgical-airway card, then have a qualified reviewer define separate pathways where physiology and paralysis differ. |
| `MAJOR` | `sections.equipment` | "Scalpel" is underspecified, and "6.0 adult ETT or trach/cric tube per kit" mixes devices that may not use the same bougie-railroad workflow. DAS 2025 specifies a number 10 scalpel, bougie, 6.0 cuffed tracheal tube, and likely suction. Commercial kit tubes must follow their own IFU. | Select one trained default equipment set and sequence; name exact blade/tube characteristics and identify any kit-specific alternative as a separate IFU-governed pathway. |
| `MAJOR` | `sections.steps`, `troubleshooting` | The sequence does not state the DAS 2025 default vertical skin incision when membrane palpability is uncertain, membrane-incision blade orientation, gentle bougie advancement limit of 10-15 cm, or controlled tube advancement. It also omits full-block/oxygen-from-above actions for the DAS CICO pathway. These omissions affect false-passage, posterior injury, and endobronchial-placement risk. | Have the airway owner choose and fully specify the locally trained technique, including depth controls and failure actions, without blending incompatible variants. |
| `MAJOR` | `sections.ultrasound` (empty); `shiftMode` | DAS 2025 recommends assessing membrane palpability before eFONA and supports pre-induction ultrasound localization/marking when difficult airway management is anticipated; it does not suggest delaying an established CICO rescue for scanning. The JSON says to landmark early but leaves ultrasound entirely blank. | Decide whether to add a concise pre-crisis marking statement with a clear "do not delay eFONA" boundary. |
| `INSUFFICIENT EVIDENCE` | `sections.contraindications` - "Young children require special consideration" | "Young" is undefined. Pediatric FONA technique and age cutoffs vary, while the maintained DAS pediatric 1-8-year algorithm uses a different rescue pathway. The record is not tagged `Peds`, but the caution could still be acted on without an age boundary. | Declare the card adult-only or attach the institution's pediatric difficult-airway policy and an explicit age/size boundary approved by pediatric airway specialists. |
| `MINOR` | `sections.complications`, `aftercare` | Current DAS guidance specifically calls for excluding bronchial intubation and pneumothorax after stabilization. The JSON says "obtain imaging" and "arrange definitive airway/ENT/trauma/ICU follow-up" but does not name those immediate checks. | Define the required immediate post-eFONA assessment and surgical review wording. |
| `MAJOR` | `sections.references` | The record cites two undated textbooks and local policy only. It omits the current DAS eFONA standard and provides no direct traceability for equipment, sequence, pediatric boundary, or aftercare. | Add current primary guidance and kit IFUs for any commercial pathway; specify textbook editions. |

### Equipment, dosing, and monitoring assessment

Suction, BVM/oxygen, capnography, securement, and a bougie/tube are present, but the exact standard instruments and device compatibility are incomplete. No structured dosing object exists. Routine procedural dosing is not otherwise applicable, but the DAS adult CICO pathway's full-neuromuscular-block requirement creates a medication dependency that the current broad-scope card does not resolve. Waveform capnography and aggressive securement are appropriate.

No additional material discrepancy was identified in the core indications, landmark text, general positioning, confirmation, bleeding/false-passage troubleshooting, documentation, or senior pearls beyond the scope, sequence, visual, and aftercare findings above.

### Reviewer questions and proposed disposition

1. Is the intended standard the DAS 2025 adult CICO eFONA pathway or a different institutional technique?
2. Which exact scalpel, bougie, tube, and commercial-kit alternatives are stocked and trained?
3. Is the card explicitly adult-only, and where is the pediatric pathway?
4. Who will anatomically approve replacement artwork?

**Proposed reviewer disposition:** withhold from release until the danger-zone image is replaced or removed and an airway owner resolves the technique, equipment, scope, and reference gaps. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- Difficult Airway Society, [DAS guidelines for management of unanticipated difficult tracheal intubation in adults](https://doi.org/10.1016/j.bja.2025.10.006), 2025 guideline / 2026 print publication.
- Difficult Airway Society, [official 2025 algorithms page, including Plan D](https://das.uk.com/guidelines/das_intubation_guidelines/), 2025.
- Difficult Airway Society/Association of Paediatric Anaesthetists, [Paediatric difficult airway guidelines](https://das.uk.com/guidelines/paediatric-difficult-airway-guidelines/), maintained official guidance for children aged 1-8 years (algorithm published 2012).
- Dessie et al., [Anatomical variations and developmental anomalies of the thyroid gland in an Ethiopian population: a cadaveric study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6318459/), 2018.

## `procedural_sedation` - Procedural Sedation

**Screening disposition: `STOP-SHIP`** because its only declared visual is a release-blocking placeholder. The clinical text has multiple `MAJOR` scope, monitoring, staffing, dosing, pediatric, and rescue gaps.

### Source-standard summary

Authoritative guidance treats sedation as a depth continuum with the ability to rescue from unintended deeper sedation. It requires a dedicated qualified monitor in addition to the proceduralist, pre-sedation risk and airway assessment, age/size-appropriate rescue equipment, continuous oxygenation/ventilation assessment, agent- and depth-appropriate capnography, incremental medication administration, immediate access to indicated antagonists, and monitored recovery to defined criteria. ACEP supports not delaying urgent ED sedation solely for fasting time, while ASA/AAP guidance continues to distinguish elective fasting from urgent risk-benefit decisions. The JSON correctly emphasizes airway rescue readiness, suction/BVM, role assignment, incremental dosing, physiologic monitoring, and return to baseline, but its cross-setting wording is too permissive and nonspecific.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `visualAssets[sedation_room_setup]` | `assetName` is `null`, and the caption explicitly calls it placeholder metadata. The repo safety policy makes declared placeholder clinical visuals stop-ship. | Remove the declaration from release or provide reviewed, bundled room-setup artwork. |
| `MAJOR` | `sections.shiftMode`, `steps` | "Separate proceduralist from sedation/monitoring clinician when possible" weakens the requirement. ACEP 2014 says a nurse or other qualified person should continuously monitor in addition to the procedural provider; ASA 2018 requires a designated individual other than the practitioner; AAP/AAPD requires sufficient trained personnel and an independent observer for pediatric deep sedation. | Replace "when possible" with a depth-, venue-, and local-policy-specific minimum staffing rule, including monitor qualifications and permitted interruptible tasks. |
| `MAJOR` | `sections.shiftMode`, `equipment`, `confirmation`, `documentation` | Capnography is described as "ideally" or "if available." ASA 2018 recommends continual capnography unless precluded/invalidated; AAP/AAPD requires it for almost all deeply sedated children and documents vital signs at least every five minutes. ACEP 2014 is more permissive for ED sedation. Because the record spans ED, ICU, adults, children, and unspecified sedation depth, the current wording does not tell users which standard applies. | Define intended sedation depths and venues, then state the reviewed capnography and recording requirement plus the documented exceptions. |
| `MAJOR` | No `dosing` object; medication names appear only in tags; `sections.steps` | No agent-specific structured dose, route, weight basis, onset/peak, redose interval, maximum, age adjustment, hemodynamic qualifier, interaction warning, or reversal dose exists for ketamine, propofol, etomidate, opioids, or benzodiazepines. ASA 2018 requires incremental titration with time for peak effect and general-anesthesia-level rescue capability when agents intended for general anesthesia are used. No dose can be verified. | Decide whether to add pharmacist/clinician-reviewed adult and pediatric dosing structures or remove named-agent discoverability and link to a separately governed medication protocol. |
| `MAJOR` | `setting: [Peds]`; `sections.equipment`, `steps`, `aftercare` | Pediatric safeguards are not operationalized: no age/size-specific BVM masks, adjuncts, SGA/ETT equipment, pediatric defibrillator/rescue cart, kilogram weight/double-check process, PALS-level rescue requirement, or pediatric time-based record. AAP/AAPD explicitly requires age/size-appropriate equipment, trained rescue staff, and depth-specific monitoring/recovery. | Add a pediatric-specific branch reviewed by pediatric sedation experts or remove pediatric scope. |
| `MAJOR` | `sections.contraindications` - fasting language | "Recent oral intake is contextual" is defensible for urgent ED sedation, and ACEP says not to delay ED sedation based only on fasting. It does not distinguish that setting from elective sedation, for which AAP/ASA fasting guidance applies, or identify high aspiration-risk conditions that change the plan. | Separate urgent/emergent ED guidance from elective sedation and define when aspiration risk changes depth, agent, airway strategy, consultation, or delay. |
| `MAJOR` | `sections.troubleshooting`, `complications` | Laryngospasm, vomiting, and aspiration are listed complications, but troubleshooting provides no event-specific immediate rescue pathway for them. The protocol requires practical rescue thinking for high-risk complications; AAP/AAPD specifically requires personnel able to rescue laryngospasm and airway obstruction. | Add clinician-approved laryngospasm and emesis/aspiration rescue actions with escalation triggers and age/depth dependencies. |
| `MAJOR` | `sections.aftercare`, `confirmation`, `documentation` | "Appropriate baseline" is not paired with a defined recovery area, ongoing monitoring intervals, discharge criteria, observation after reversal, or resedation risk. ASA and AAP/AAPD require monitored recovery, age/size-appropriate rescue capability, and observation until discharge criteria are met; antagonists can wear off before the sedative/opioid. | Define recovery monitoring, discharge/admission criteria, post-antagonist observation, and outpatient supervision/precautions through local policy. |
| `MINOR` | `sections.indications`, `steps` | Painful procedures are listed, but the entry does not remind users that local/regional anesthetic doses from the same encounter require separate cumulative-dose control. AAP/AAPD recommends calculating the maximum mg/kg local-anesthetic dose before administration. | Decide whether to link to the app's governed local-anesthetic dosing/LAST content when local or regional anesthesia is combined with sedation. |
| `MAJOR` | `sections.references` | Two undated textbooks and a generic local-policy statement cannot support the detailed claims or reconcile conflicting ED, elective, moderate, deep, adult, and pediatric standards. | Add current primary references by scope and specify textbook editions. |

### Equipment, dosing, and monitoring assessment

The list includes cardiac monitoring, pulse oximetry, BP cycling, oxygen, BVM/PEEP, suction, basic adjuncts, advanced airway access, reversal medications, IV access, and procedural readiness. It does not define a complete age/size-specific rescue cart, SGA/ETT sizes, defibrillation capability, or monitoring interval. No structured dosing exists, so agent doses and reversals were not assessable. Monitoring language must be stratified by intended depth, age, procedure, and venue rather than "ideally/if available."

No additional material discrepancy was identified in the broad indications, airway-focused anatomy, basic positioning, general consent/time-out preparation, hypotension/apnea troubleshooting, documentation intent, or senior pearls beyond the findings above. The empty ultrasound section is appropriate for this generic procedure.

### Reviewer questions and proposed disposition

1. What sedation depths and clinical venues does this record govern?
2. What is the minimum dedicated-monitor qualification and capnography policy for each scope?
3. Will adult and pediatric medication dosing live here or in an institution-controlled protocol?
4. Should pediatric sedation be split into a separate record?
5. Which laryngospasm, aspiration, and recovery algorithms are locally approved?

**Proposed reviewer disposition:** withhold from release until the placeholder visual is removed and the staffing, depth/monitoring, dosing, pediatric, rescue, and recovery policies are explicitly resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- American Society of Anesthesiologists and partner societies, [Practice Guidelines for Moderate Procedural Sedation and Analgesia](https://doi.org/10.1097/ALN.0000000000002043), 2018.
- American Academy of Pediatrics and American Academy of Pediatric Dentistry, [Guidelines for Monitoring and Management of Pediatric Patients Before, During, and After Sedation for Diagnostic and Therapeutic Procedures](https://www.aapd.org/globalassets/media/policies_guidelines/bp_monitoringsedation.pdf), 2019.
- American College of Emergency Physicians, [Clinical Policy: Procedural Sedation and Analgesia in the Emergency Department](https://www.acep.org/siteassets/uploads/uploaded-files/acep/clinical-and-practice-management/clinical-policies/clinical-policy-procedural-sedation-and-analgesia-in-the-emergency-department.pdf), 2014 (still listed on ACEP's current clinical-policy page as of this audit).
- American Society of Anesthesiologists, [2023 Practice Guidelines for Preoperative Fasting: Modular Update](https://doi.org/10.1097/ALN.0000000000004381), 2023.

## Changed File

- `docs/audits/procedure-verification/01_AIRWAY_SEDATION.md` only.

## Sources and Limitations

This audit reviewed every JSON section, declared visual asset, equipment/instrument list, and structured dosing field for the three assigned IDs. The current JSON contains no structured dosing object for any of them, so dose correctness could not be tested. Bundled cricothyrotomy images were visually inspected; placeholder assets were confirmed absent from the asset catalog. Sources were limited to the primary/authoritative links listed per procedure. Standards differ by setting, sedation depth, age, institution, and device IFU; those conflicts are identified for clinician resolution rather than silently reconciled. No expert clinical review, bedside usability test, simulator test, or institutional-policy comparison was performed. No content was approved, and no `reviewerStatus` was changed.
