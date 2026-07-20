# General Procedures Verification Lane

Audit date: 2026-07-18  
Scope: `paracentesis`, `lateral_canthotomy`, `shoulder_reduction`, `knee_arthrocentesis`, `anterior_nasal_packing`, `peritonsillar_abscess_drainage`, `abscess_incision_drainage`, `laceration_repair`, `foreign_body_removal_soft_tissue`  
Procedures SHA-256 reviewed: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`

This is an AI-assisted discrepancy screen, not clinical approval. I am not a licensed reviewer. Dispositions use `AUDIT_PROTOCOL.md`; structural or policy compliance does not establish clinical correctness.

## Disposition Summary

| Procedure ID | Screening disposition | Principal reason |
|---|---|---|
| `paracentesis` | **STOP-SHIP** | Declared placeholder visual is a release stop; albumin and coagulation statements also need major clinical revision. |
| `lateral_canthotomy` | **MAJOR** | Instrument choice and superior-cantholysis trigger are not sufficiently safety-bounded. |
| `shoulder_reduction` | **STOP-SHIP** | Neurovascular compromise is presented as a contraindication to reduction; declared visual is also a placeholder. |
| `knee_arthrocentesis` | **STOP-SHIP** | Declared visuals are placeholders; synovial WBC/PMN interpretation is overstated. |
| `anterior_nasal_packing` | **MAJOR** | RAPID RHINO inflation conflicts with manufacturer instructions; anticoagulation guidance omits the society standard. |
| `peritonsillar_abscess_drainage` | **MAJOR** | Airway readiness and topical-anesthetic safety are incomplete; steroid regimen is unsupported as written. |
| `abscess_incision_drainage` | **STOP-SHIP** | Declared visual is a placeholder; routine irrigation and routine packing/loop-drain language conflict with trial evidence. |
| `laceration_repair` | **STOP-SHIP** | Declared visual is a placeholder; tetanus prophylaxis omits the vaccine/TIG decision pathway. |
| `foreign_body_removal_soft_tissue` | **STOP-SHIP** | Digital tourniquet instructions lack a removal fail-safe; declared visual is also a placeholder. |

## `paracentesis` - Paracentesis

**Screening disposition: STOP-SHIP.** Clinical screen: **MAJOR**.

**Coverage and source standard.** Reviewed metadata and every section (`shiftMode` through `references`), plus `visualAssets`, equipment/instruments, medication statements, confirmation, rescue, and monitoring. AASLD and BSG/BASL support prompt diagnostic paracentesis for new or admitted cirrhotic ascites, ascitic cell count/culture and SAAG-based evaluation, no routine coagulation-product correction, and albumin after >5 L removal. BSG/BASL also permits albumin below 5 L for acute-on-chronic liver failure or high AKI risk.

**Findings.**

- **STOP-SHIP - `visualAssets`:** `paracentesis_liq_site.assetName` is `null` and its caption calls it a placeholder. The repo safety policy explicitly makes declared placeholders stop-ship for release. Clinician decision: approve and bundle a clinically reviewed landmark image or remove the declaration until one exists.
- **MAJOR - `shiftMode`, `steps`, `aftercare`, `documentation`:** "Do not give albumin" below 5 L is too absolute. Current guidance allows case-specific albumin below 5 L in ACLF or high post-paracentesis AKI risk. Clinician decision: define the exception population, solution concentration, dose, timing, and reassessment target.
- **MAJOR - `contraindications`:** the fixed `INR >2.0` / platelets `<50,000` relative-contraindication thresholds are not supported by the cited current cirrhosis guidance, which recommends against routine PT/platelet testing and prophylactic blood products for paracentesis. Clinician decision: replace numeric gates with a reviewed bleeding-risk framework, including DIC/active bleeding and local procedural policy.
- **MAJOR - `equipment` and diagnostic `steps`:** ascitic albumin is listed, but a paired serum albumin needed to calculate SAAG is not explicit for new-onset ascites. Clinician decision: specify the minimum diagnostic panel and when expanded tests (cytology, glucose, LDH, amylase) are indicated rather than presenting one undifferentiated specimen list.

**Equipment/instruments.** Ultrasound, Doppler vessel check, sterile setup, catheter/drainage tubing, collection containers, and bedside blood-culture bottles are generally coherent. The exact catheter choice, vacuum limit, blood-culture bottle volume, and laboratory containers remain manufacturer/local-lab dependencies.

**Dosing/monitoring.** The >5 L albumin range of 6-8 g/L is supported, but no structured dosing object exists and the below-5-L exception is missing. BP/HR monitoring is present; the reviewer should define escalation thresholds and whether renal function/electrolyte follow-up is required after high-risk large-volume drainage.

**Reviewer question and proposed disposition.** Does the clinical owner approve a risk-qualified albumin rule and removal of fixed INR/platelet gates? Keep **STOP-SHIP** until the declared visual is resolved and **MAJOR** clinical items are signed off. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- AASLD, [Diagnosis, Evaluation, and Management of Ascites, Spontaneous Bacterial Peritonitis and Hepatorenal Syndrome](https://www.aasld.org/practice-guidelines/diagnosis-evaluation-and-management-ascites-spontaneous-bacterial-peritonitis) (practice guidance, updated 2021).
- British Society of Gastroenterology/British Association for the Study of the Liver, [Guidelines on the management of ascites in cirrhosis](https://gut.bmj.com/content/70/1/9) (2021).

## `lateral_canthotomy` - Lateral Canthotomy & Cantholysis

**Screening disposition: MAJOR.**

**Coverage and source standard.** Reviewed every section, equipment/instruments, medication language, and the bundled visual declaration. The Joint Trauma System requires immediate lateral canthotomy with complete inferior cantholysis for orbital compartment syndrome, use of blunt scissors, and reassessment of vision and IOP before considering superior release. AAO material likewise cautions that superior cantholysis adds lacrimal artery/gland risk.

**Findings.**

- **MAJOR - `equipment` and `steps`:** equipment permits "iris or sharp straight scissors" while the JTS technique specifically calls for blunt scissors advanced toward the lateral orbital rim. In this distorted, time-critical field, a sharp-tip option increases globe-injury risk. Clinician decision: name an approved blunt instrument and acceptable backup.
- **MAJOR - `shiftMode`, `steps`, `troubleshooting`:** "if still tense, release the superior crus" is less specific than the JTS trigger (persistent elevated IOP, poor vision, and tense orbit after complete inferior release). AAO material warns of lacrimal artery/gland injury and limited evidence of added decompression after adequate inferior release. Clinician decision: define the reassessment sequence, confirm complete inferior cantholysis first, and state when superior release requires ophthalmic expertise.
- **MINOR - `confirmation` and `documentation`:** the content mentions vision/pupils/IOP, but does not explicitly preserve bilateral baseline and serial values or record inability to test. Clinician decision: align documentation with the JTS expectation for vision and RAPD documentation whenever possible.

**Equipment/instruments.** Hemostat, forceps, lighting, gauze, and tonometry are reasonable; replace the sharp-scissors option. The referenced `canthotomy_inferior_crus` bitmap is bundled, but this lane cannot establish clinical artwork approval.

**Dosing/monitoring.** No structured dosing exists. Local anesthetic with epinephrine has no concentration, volume, cumulative maximum, or toxicity monitoring. JTS describes a small subdermal dose but urgency must not be delayed. The reviewer must decide whether to encode a complete local-anesthetic limit and the acetazolamide adjunct pathway or leave medications to a linked protocol.

**Reviewer question and proposed disposition.** What exact criteria authorize superior cantholysis, and which blunt scissors are required? Maintain **MAJOR** until those points and visual approval are clinically resolved. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- U.S. Joint Trauma System, [Eye Trauma: Initial Care Clinical Practice Guideline](https://jts.health.mil/assets/docs/cpgs/Eye_Trauma_Initial_Care_01_Jun_2021_ID03.pdf) (2021).
- American Academy of Ophthalmology EyeWiki, [Orbital Compartment Syndrome](https://eyewiki.aao.org/Orbital_Compartment_Syndrome) (accessed 2026; specialty-society reference).
- FDA/DailyMed, [Xylocaine with epinephrine prescribing information](https://www.dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=74bad838-2800-4d36-a3ee-cc1d739d24c2&type=display) (label updated 2026).

## `shoulder_reduction` - Shoulder Reduction (Anterior)

**Screening disposition: STOP-SHIP.**

**Coverage and source standard.** Reviewed every section, the three named reduction families, sedation/intra-articular anesthesia, equipment, imaging, neurovascular checks, aftercare, and the placeholder visual. Authoritative guidance treats an unreduced shoulder as an emergency, requires pre/post neurovascular documentation, and calls for urgent specialist involvement when neurovascular compromise is present; compromise does not safely function as a simple contraindication to reduction.

**Findings.**

- **STOP-SHIP - `contraindications`:** "Neurovascular compromise needing urgent surgical evaluation" can be read as a reason not to reduce. Delay may prolong axillary artery or plexus compression. Current guidance calls for emergent reduction of unreduced shoulders plus immediate orthopedic/vascular involvement and post-reduction reassessment. Clinician decision: state the sequence for pulseless/ischemic limbs, consultation, immediate reduction, and persistent post-reduction deficits.
- **STOP-SHIP - `visualAssets`:** `shoulder_scapular_manip.assetName` is `null`. Resolve the declared placeholder before release.
- **MAJOR - `equipment`, `steps`, dosing:** an intra-articular block is offered without an agent, concentration, volume, maximum cumulative dose, contraindications, sterile technique detail, or toxicity monitoring. Clinician decision: either supply a complete reviewed block protocol/structured dose or remove it as an actionable option.
- **MINOR - `aftercare`:** sling duration, rehabilitation start, age/first-dislocation distinctions, and expedited follow-up triggers are left entirely to "orthopedic guidance." A 2026 BESS guideline underscores staged rehabilitation; the reviewer should decide the minimum bedside aftercare message.

**Equipment/instruments.** Monitoring, oxygen, capnography, and an airway kit are appropriately named for sedation. The sheet is technique-dependent; the procedure should ensure that escalation does not mean progressively higher traction force.

**Dosing/monitoring.** No structured dosing exists for intra-articular local anesthetic, sedation, or analgesia. Sedation monitoring is named but pre-sedation assessment, recovery criteria, pediatric dosing, pregnancy, and agent-specific rescue remain local-protocol dependencies.

**Reviewer question and proposed disposition.** Should neurovascular compromise trigger immediate gentle reduction with simultaneous specialist mobilization, and what exceptions require the operating room first? Maintain **STOP-SHIP** pending that decision and placeholder removal. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- Royal Children's Hospital Melbourne, [Shoulder Dislocations - Emergency Department](https://www.rch.org.au/clinicalguide/guideline_index/fractures/Shoulder_Dislocations_-_Emergency_Department/) (updated 2020).
- UK Defence Medical Command, [Joint Dislocations](https://cgo.mod.uk/clinical-guidelines-for-operations/treatment-guidelines/musculoskeletal/joint-dislocations/) (2026).
- British Elbow and Shoulder Society, [Practice guidelines: rehabilitation following traumatic anterior shoulder dislocation](https://pmc.ncbi.nlm.nih.gov/articles/PMC13056797/) (2026).

## `knee_arthrocentesis` - Knee Arthrocentesis

**Screening disposition: STOP-SHIP.** Clinical screen: **MAJOR**.

**Coverage and source standard.** Reviewed every section, both declared visuals, equipment/containers, local anesthesia, sampling order, antimicrobial timing, confirmation, and aftercare. The EBJIS SANJO guideline prioritizes bacterial identification, WBC/PMN, and crystals; recommends aspiration promptly; and defers antibiotics until sampling only when the patient is not septic.

**Findings.**

- **STOP-SHIP - `visualAssets`:** both knee visual declarations have `assetName: null`. Resolve the placeholders before release.
- **MAJOR - `seniorPearls`:** "WBC over 50,000 with >90% PMNs is septic until proven otherwise" overstates the diagnostic performance. SANJO says >50,000 is suggestive but insufficient alone, gives no diagnostic PMN cutoff, and notes crystals do not exclude infection. Clinician decision: replace the threshold heuristic with a probability-based interpretation tied to culture, clinical status, and urgent disposition.
- **MAJOR - `shiftMode` and `aftercare`:** "tap before antibiotics when feasible" does not name the explicit sepsis/septic-shock exception. Clinician decision: define when immediate empiric therapy must not wait for aspiration.
- **MINOR - `equipment`:** named tube colors and direct use of a blood-culture bottle are local-laboratory dependent. SANJO recommends sterile containers and inoculating remaining fluid into blood-culture bottles after primary samples. Clinician decision: verify specimen order and containers with the intended lab.

**Equipment/instruments.** The 18G aspiration needle, large syringe, sterile prep, linear ultrasound, and alternate superolateral/suprapatellar approaches are coherent. The absolute claim that ultrasound "increases success" should be kept proportional to operator skill and effusion size.

**Dosing/monitoring.** No structured dosing exists. The listed 1% lidocaine/5 mL setup is below normal adult maximums but does not cover cumulative dose, pediatric weight-based limits, hepatic/cardiac risk, or local-anesthetic toxicity response.

**Reviewer question and proposed disposition.** What synovial-fluid language should replace the 50,000/90% rule, and what exact sepsis exception should be surfaced? Maintain **STOP-SHIP** until visuals are resolved and **MAJOR** interpretation/timing language is approved. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- European Bone and Joint Infection Society, [Guideline for management of septic arthritis in native joints (SANJO)](https://jbji.copernicus.org/articles/8/29/2023/) (2023).
- FDA, [Xylocaine and Xylocaine with epinephrine prescribing information](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/006488Orig1s100lbl.pdf) (2024).

## `anterior_nasal_packing` - Anterior Nasal Packing

**Screening disposition: MAJOR.**

**Coverage and source standard.** Reviewed every section, all named devices/topicals, cautery, anticoagulation, packing removal, antibiotic language, and lack of visual assets. The AAO-HNSF guideline calls for resorbable packing in patients with bleeding disorders or antithrombotic use, first-line local treatment before reversal/withdrawal absent life-threatening bleeding, and explicit packing/removal education. RAPID RHINO instructions require sterile-water activation and air-only inflation.

**Findings.**

- **MAJOR - `equipment` and `steps`:** RAPID RHINO is instructed to inflate with "air or saline," and equipment lists water or saline for inflation. Manufacturer instructions say soak in sterile water for at least 30 seconds, then inflate slowly with **air only** while using the pilot cuff. Clinician decision: make device-specific instructions conform to the current IFU and separate them from other balloon products.
- **MAJOR - `troubleshooting`, `equipment`, `aftercare`:** for anticoagulated patients, "correct coagulopathy as able" omits AAO-HNSF's requirement to use first-line measures before reversal/withdrawal unless bleeding is life-threatening and omits resorbable packing. Clinician decision: define life-threatening criteria, resorbable materials, hematology/ENT escalation, and who may alter antithrombotic therapy.
- **INSUFFICIENT EVIDENCE - `aftercare`:** "Prescribe antibiotics ... per institutional protocol" remains controversial; AAO-HNSF identifies the benefit and ideal duration of systemic antibiotics after packing as a research need. Clinician decision: either encode a qualified local policy with duration/indications or avoid a default-prescribing command.
- **MINOR - `documentation`:** guideline-required documentation of bleeding-risk factors, packing type, removal plan, and 30-day outcome/transition of care is incomplete.

**Equipment/instruments.** Lighting, speculum, Frazier suction, PPE, cautery, and anterior packing options are appropriate. Each commercial device needs its own IFU, inflation medium/volume or tactile endpoint, and contraindications; they are not interchangeable.

**Dosing/monitoring.** No structured dosing exists for oxymetazoline, phenylephrine, 4% lidocaine, or injected/local epinephrine combinations. Concentration, maximum amount, cardiovascular cautions, pediatric/pregnancy limits, and post-packing respiratory monitoring are local-policy dependencies.

**Reviewer question and proposed disposition.** Which exact pack devices and IFU revisions will the app support, and what is the local anticoagulation/antibiotic policy? Maintain **MAJOR** until device and antithrombotic language is corrected. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- AAO-HNSF, [Clinical Practice Guideline: Nosebleed (Epistaxis) Executive Summary](https://journals.sagepub.com/doi/abs/10.1177/0194599819889955) (2020).
- Smith+Nephew/ArthroCare, [RAPID RHINO product usage instructions](https://rapidrhino.com/usage-instructions/) (current manufacturer instructions, accessed 2026).
- AAO-HNSF, [Nosebleed guideline research needs](https://www.entnet.org/resource/cpg-nosebleed-epistaxis-research-needs/) (2020).

## `peritonsillar_abscess_drainage` - Peritonsillar Abscess Drainage

**Screening disposition: MAJOR.**

**Coverage and source standard.** Reviewed every section, needle depth/trajectory, suction, anesthesia, airway and deep-space escalation, antibiotics/steroids, and the empty visual array. A multidisciplinary tonsillitis guideline recognizes aspiration, incision/drainage, and abscess tonsillectomy as effective options selected by cooperation, comorbidity, complications, and prior failure; evidence does not establish one universal first-line drainage technique. Bedside drainage must occur where airway complications can be managed.

**Findings.**

- **MAJOR - `shiftMode`, `contraindications`, `equipment`, `steps`:** suction is present, but there is no explicit airway assessment, monitoring, oxygen/airway/resuscitation equipment, or stop/escalation criteria for drooling, stridor, respiratory distress, severe sepsis, or extension. Clinician decision: define which patients are eligible for bedside aspiration and which require controlled airway/ENT/operative management first.
- **MAJOR - `equipment` and dosing:** benzocaine/Cetacaine spray is named without a metered dose, maximum exposure, susceptible populations, monitoring, or methemoglobinemia rescue. Current labels warn that methemoglobinemia can be serious or fatal and require prompt treatment. Clinician decision: approve a specific labeled product and complete safety pathway, or use an alternative reviewed topical agent.
- **MAJOR - `aftercare`:** "consider medrol dose pack" is not supported by the cited evidence. PTA trials and guideline summaries evaluate a single adjunct corticosteroid dose, with heterogeneous and limited outcomes, not an unspecified multi-day pack. Clinician decision: choose a specific evidence-based single-dose regimen or remove the command.
- **INSUFFICIENT EVIDENCE - `shiftMode`:** "needle aspiration is the first-line" is stronger than the 2016 guideline, which considers aspiration, incision/drainage, and abscess tonsillectomy effective and individualized. Clinician decision: state the institution's preferred approach and selection criteria.

**Equipment/instruments.** A guarded 18G needle, 10 mL syringe, strong lighting, tongue depressor, suction, and forward seating are coherent. A 1 cm guard is close to published limits, but the reviewer should confirm the precise maximum insertion depth and whether inferior redirection is acceptable.

**Dosing/monitoring.** No structured dosing exists. Lidocaine/epinephrine has a nominal syringe volume but no cumulative maximum; antibiotics lack dose/duration, allergy/pregnancy/pediatric adjustments, and IV-to-oral criteria; the steroid instruction is incomplete. Observation for oral intake and airway stability before discharge is not explicit.

**Reviewer question and proposed disposition.** What bedside-airway eligibility rule, topical anesthetic, antibiotic course, and optional steroid regimen will ENT approve? Maintain **MAJOR** pending those decisions. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- German interdisciplinary guideline, [Clinical practice guideline: tonsillitis II. Surgical management](https://pubmed.ncbi.nlm.nih.gov/26882912/) (2016).
- DailyMed, [Cetacaine Topical Anesthetic prescribing information](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=af1773c5-5d5b-4278-b551-30ad2df6d5b5) (label updated 2021; accessed 2026).
- Chau et al., [Corticosteroids in peritonsillar abscess treatment: a blinded placebo-controlled trial](https://onlinelibrary.wiley.com/doi/pdf/10.1002/lary.24283) (2014).

## `abscess_incision_drainage` - Abscess Incision & Drainage

**Screening disposition: STOP-SHIP.** Clinical screen: **MAJOR**.

**Coverage and source standard.** Reviewed every section, ultrasound, incision/dissection, irrigation, packing/loop drainage, cultures, antibiotics, equipment, follow-up, and the placeholder visual. IDSA makes incision and drainage the core treatment and uses systemic illness/host factors to guide antibiotics. Later randomized evidence found no outcome benefit from routine cavity irrigation and no benefit, with more pain, from routine packing of simple abscesses under 5 cm. A BMJ guideline makes a weak, shared-decision recommendation for TMP-SMX or clindamycin after drainage of uncomplicated abscesses.

**Findings.**

- **STOP-SHIP - `visualAssets`:** `abscess_technique.assetName` is `null`. Resolve the declared placeholder before release.
- **MAJOR - `shiftMode`, `equipment`, `steps`, `confirmation`, `documentation`:** vigorous 500-1000 mL irrigation "until clear" is treated as mandatory and a confirmation criterion. A randomized trial found no improvement in treatment success and identified added pain/time/cost and splash contamination concerns. Clinician decision: decide whether irrigation is optional, and define exceptions rather than a universal endpoint.
- **MAJOR - `shiftMode`, `steps`, `confirmation`:** every cavity is directed to receive a loop drain or loose packing. A randomized trial found routine packing of simple abscesses under 5 cm added pain without reducing reintervention; loop drainage has separate selection criteria. Clinician decision: specify no-packing eligibility and when loop or packing is indicated.
- **MAJOR - `shiftMode` and `aftercare`:** "most simple abscesses ... do not need antibiotics" reflects IDSA's selective approach but does not acknowledge the later modest reduction in failure/recurrence that drove a weak shared-decision recommendation. Clinician decision: choose the governing standard and expose the indications, benefit/harms discussion, and local resistance constraints.

**Equipment/instruments.** Scalpel, hemostat/scissors, ultrasound with Doppler, dressing, and culture supplies are generally appropriate. The procedure should not require a large irrigation volume or drain/packing for every simple cavity.

**Dosing/monitoring.** No structured dosing exists. Lidocaine with epinephrine lacks cumulative maximum/toxicity monitoring. TMP-SMX and doxycycline are named without dose, duration, age/pregnancy cautions, renal adjustment, or alternatives; this is not a complete antibiotic protocol.

**Reviewer question and proposed disposition.** Will the clinical owner adopt optional irrigation, a no-packing pathway for eligible simple abscesses, and a shared antibiotic decision? Maintain **STOP-SHIP** until the visual is resolved and **MAJOR** technique statements are approved. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- IDSA, [Practice Guidelines for Skin and Soft Tissue Infections](https://www.idsociety.org/practice-guideline/skin-and-soft-tissue-infections/) (2014).
- Chinnock and Hendey, [Irrigation of Cutaneous Abscesses Does Not Improve Treatment Success](https://www.sciencedirect.com/science/article/abs/pii/S0196064415011889) (randomized trial, 2016).
- O'Malley et al., [Routine packing of simple cutaneous abscesses is painful and probably unnecessary](https://pubmed.ncbi.nlm.nih.gov/19388915/) (randomized trial, 2009).
- BMJ Rapid Recommendations, [Antibiotics after incision and drainage for uncomplicated skin abscesses](https://www.bmj.com/content/360/bmj.k243) (2018).

## `laceration_repair` - Laceration Repair (Suturing)

**Screening disposition: STOP-SHIP.** Clinical screen: **MAJOR**.

**Coverage and source standard.** Reviewed every section, exploration through range of motion, irrigation/closure selection, equipment and sutures, local anesthesia, tetanus, aftercare, documentation, and the placeholder visual. CDC requires wound classification plus vaccination-history assessment and, for selected dirty/major wounds, tetanus immune globulin (TIG). FDA labeling requires cumulative local-anesthetic dose limits and physiologic monitoring.

**Findings.**

- **STOP-SHIP - `visualAssets`:** `suture_eversion.assetName` is `null`. Resolve the declared placeholder before release.
- **MAJOR - `equipment`, `steps`, `aftercare`, `documentation`:** "update tetanus" omits the actual vaccine/TIG decision. CDC distinguishes clean/minor from dirty/major wounds; TIG is indicated for dirty/major wounds with unknown/incomplete primary series and for patients with HIV or severe immunodeficiency, at 250 IU IM. Clinician decision: embed the current CDC algorithm or link to a reviewed versioned protocol and name TIG in equipment/documentation when indicated.
- **MAJOR - `equipment` and dosing:** lidocaine with/without epinephrine is actionable but has no concentration selection, total dose calculation, high-risk adjustment, monitoring, or local-anesthetic systemic-toxicity response. Clinician decision: add a complete structured dose or explicitly defer dosing to a linked medication protocol.
- **MINOR - `contraindications` and `aftercare`:** wound-age limits, bite prophylaxis, specialist locations, and suture-removal timing are intentionally nonspecific. This avoids false universal cutoffs but leaves bedside decisions undiscoverable; the reviewer should decide which minimum location-specific rules belong here.

**Equipment/instruments.** Needle driver, toothed forceps, scissors, irrigation, lighting, layered absorbable and skin sutures, and dressings are reasonable. Suture sizes are examples and require patient/site qualification. No additional material conflict was identified in exploration, edge eversion, or closure-choice language against the sources reviewed.

**Dosing/monitoring.** No structured dosing exists. CDC's TIG dose and vaccine timing are absent. FDA adult maxima for normal healthy adults are 4.5 mg/kg (300 mg total) without epinephrine and 7 mg/kg (500 mg total) with epinephrine, but the clinician must decide how this app handles pediatric and comorbidity adjustments rather than copying a universal limit.

**Reviewer question and proposed disposition.** Should this procedure own the full tetanus and local-anesthetic algorithms or link to versioned medication/prevention modules? Maintain **STOP-SHIP** until the visual is resolved and the tetanus gap is closed. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- CDC, [Clinical Guidance for Wound Management to Prevent Tetanus](https://www.cdc.gov/tetanus/hcp/clinical-guidance/index.html) (2025).
- FDA, [Xylocaine and Xylocaine with epinephrine prescribing information](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/006488Orig1s100lbl.pdf) (2024).

## `foreign_body_removal_soft_tissue` - Foreign Body Removal (Soft Tissue)

**Screening disposition: STOP-SHIP.**

**Coverage and source standard.** Reviewed every section, radiography/ultrasound/CT escalation, incision/dissection, confirmation, equipment, digital tourniquet, wound closure, tetanus/antibiotics, and the placeholder visual. ACR supports US or noncontrast CT after negative radiographs when suspicion persists and notes that glass is not invariably visible. ACEP supports high-frequency ultrasound for radiolucent localization and image-guided removal. A UK national patient-safety alert documents amputations from forgotten digital tourniquets.

**Findings.**

- **STOP-SHIP - `equipment` and `positioning`:** a tourniquet or Penrose is instructed for digits, but there is no highly visible device requirement, application-time record, timer, removal step, removal confirmation, or post-removal perfusion check. The NPSA found 15 serious incidents, 10 further operations, and two amputations from retained digital tourniquets. Clinician decision: define an approved device and a mandatory application/removal safety check, or remove this instruction.
- **STOP-SHIP - `visualAssets`:** `fb_us_appearance.assetName` is `null`. Resolve the declared placeholder before release.
- **MAJOR - `shiftMode`, `steps`, `confirmation`, `seniorPearls`:** "X-ray detects glass" and "wood and plastic are invisible" are overly absolute. ACR states that glass/ceramic are not always seen, and negative radiographs with persistent suspicion warrant US or noncontrast CT depending on anatomy/material. Clinician decision: qualify sensitivity by material, size, location, and modality, and prevent negative imaging from becoming proof of complete removal.
- **MINOR - `ultrasound`:** the described echogenic/shadowing patterns are reasonable, but ultrasound sensitivity is operator-, depth-, and material-dependent. Document scan planes, depth, relation to tendon/vessel/nerve, and uncertainty.

**Equipment/instruments.** Fine forceps, #11/#15 blade, hemostats, iris scissors, linear ultrasound, irrigation, and closure supplies are coherent for selected superficial objects. Deep objects, critical-structure proximity, hands/feet, and fragmented material appropriately trigger stopping/referral, but the procedure should also identify when CT or operative imaging is preferred.

**Dosing/monitoring.** No structured dosing exists. Lidocaine 1%/2% with or without epinephrine lacks cumulative maximum and toxicity monitoring. Tetanus instructions omit the CDC vaccine/TIG pathway; antibiotic language is broad and remains wound-/host-/material-specific.

**Reviewer question and proposed disposition.** What digital-tourniquet fail-safe and imaging escalation algorithm will be mandatory? Maintain **STOP-SHIP** until those decisions and the placeholder visual are resolved. `reviewerStatus` remains unchanged.

**Primary/authoritative sources.**

- UK National Patient Safety Agency/MHRA archive, [Reducing risks of tourniquets left on after finger and toe surgery](https://www.cas.mhra.gov.uk/ViewandAcknowledgment/ViewAttachment.aspx?Attachment_id=101035) (2010).
- American College of Radiology, [Suspected Osteomyelitis, Septic Arthritis, or Soft Tissue Infection - 2022 Update](https://acsearch.acr.org/docs/3094201/Narrative/) (2022).
- American College of Emergency Physicians, [Foreign Body Localization](https://www.acep.org/sonoguide/procedures/foreign-bodies/) (2020).
- CDC, [Clinical Guidance for Wound Management to Prevent Tetanus](https://www.cdc.gov/tetanus/hcp/clinical-guidance/index.html) (2025).

## Changed File and Sources/Limitations

Changed file: `docs/audits/procedure-verification/05_GENERAL_PROCEDURES.md` only.

Sources were limited to the directly linked specialty-society/government/consensus guidance, manufacturer instructions or labels, and original trials above. Secondary summaries were used only for orientation and not as sole support for a substantive finding. Some procedure domains lack a recent universal society guideline, and institutional policies may legitimately differ for sedation, antimicrobial selection, anticoagulation, specimen handling, and follow-up. This lane did not validate clinician credentialing, local formularies, manufacturer IFU revisions beyond the linked material, pediatric/pregnancy dosing, artwork clinical approval, or iOS rendering. No JSON, Swift, validator, rescue-card, or reviewer-status field was changed. Every assigned procedure still requires qualified human review and approval of the exact content version.
