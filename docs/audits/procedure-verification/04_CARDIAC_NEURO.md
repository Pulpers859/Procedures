# Lane 04: Cardiac and Neuro Procedure Verification

- Audit date: 2026-07-18
- Audited snapshot: `Procedures/Resources/procedures.json` SHA-256 `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Scope: `pericardiocentesis`, `transvenous_pacemaker`, `resuscitative_thoracotomy`, `synchronized_cardioversion`, and `lumbar_puncture` only.
- Boundary: AI-assisted evidence and discrepancy screening, not medical approval. All findings and proposed dispositions require qualified clinical review.

Every JSON section, equipment/instrument list, visual-asset record, and structured-dosing field in each assigned procedure was screened. None of the five records contains a `structuredDosing` object.

## `pericardiocentesis` - Pericardiocentesis

**Screening disposition: `STOP-SHIP` (proposed; clinician adjudication required).** The concern is the potentially harmful treatment of aortic-dissection or free-wall-rupture tamponade as a generic caution rather than a surgical emergency with only tightly controlled bridge drainage in exceptional circumstances.

**Source-standard summary.** ESC 2025 recommends imaging-guided pericardiocentesis for tamponade and specified symptomatic/diagnostic effusions, identifies imaging as essential, advises avoiding large-volume drainage (usually keeping initial drainage below 500 mL) because of pericardial decompression syndrome, and recommends surgical drainage when percutaneous drainage is infeasible or for purulent effusion/clot. ESC procedural guidance describes aortic dissection and post-infarction free-wall rupture as contraindications to needle pericardiocentesis except very small, controlled bridge drainage when immediate surgery is unavailable. The entry site should be chosen by the closest, largest safe pocket without an intervening vital structure.

**Findings.**

1. **`STOP-SHIP` - `sections.contraindications`, `steps`, `troubleshooting`:** The statement that aortic dissection "requires extreme caution" does not communicate the ESC surgical-emergency pathway or the exceptional nature and tightly controlled goal of bridge drainage. The clinician must decide whether to state an explicit surgical-first exclusion and a narrowly defined bridge exception for impending arrest when surgery is not immediately available.
2. **`MAJOR` - `sections.steps`, `complications`, `aftercare`:** "Aspirate ... until hemodynamics improve or flow stops" has no staged-drainage ceiling, decompression-syndrome warning, or drain-removal target. The clinician must select the emergency aspiration endpoint and post-stabilization drainage protocol, including when surgical drainage is preferred for clot or purulence.
3. **`MAJOR` - `sections.confirmation`, `troubleshooting`, `visualAssets`:** Fluid color/pulsatility is not a complete chamber-puncture exclusion plan. The record does not state how to confirm intrapericardial needle/catheter position when uncertain (for example, image confirmation under an approved local method). The fixed "aims toward the left shoulder" placeholder geometry can also compete with the record's otherwise correct safest-pocket rule; the clinician must decide whether any landmark trajectory should remain in an ultrasound-first card.
4. **`MAJOR` - `sections.references`:** Generic textbooks without edition/year/page and a local-policy reminder cannot support the current high-risk details. Current guideline and device-IFU citations are needed.

**Equipment/instruments.** "Long spinal needle or pericardiocentesis kit" does not identify a wire-compatible needle, wire, dilator, pigtail catheter, drainage tubing/adapter, or compatible sizes. Cook's current set IFU demonstrates that component and compatibility details are device-specific and flags incompletely characterized phthalate effects in pregnant/nursing patients and children. A clinician must identify the locally stocked kit/IFU, population precautions, and complete catheter-drainage setup; no replacement sizes are proposed here.

**Dosing and monitoring.** No structured dosing is present. Local anesthetic is mentioned without agent, concentration, maximum dose, or toxicity rescue pathway; this is acceptable only if the product deliberately defers dosing to a linked institutional protocol. Continuous ECG/hemodynamic monitoring and serial ultrasound are present, but drainage-volume/time monitoring is incomplete.

**Other sections reviewed.** No separate material discrepancy was identified in `shiftMode`, `indications`, `anatomy`, `positioning`, `ultrasound`, `documentation`, or `seniorPearls` beyond the linked findings above. Pediatric and pregnancy technique were not claimed by the setting metadata; anticoagulation remains explicitly contextual.

**Reviewer questions.** Should aortic-dissection/free-wall-rupture tamponade be an explicit surgical-first exclusion? What controlled bridge-drainage endpoint, decompression-syndrome warning, position-confirmation method, local kit, and drain-management target are approved? Should the fixed subxiphoid trajectory placeholder be removed?

**Sources.** [European Society of Cardiology, 2025 ESC Guidelines for the Management of Myocarditis and Pericarditis (2025)](https://academic.oup.com/eurheartj/article/46/40/3952/8234483); [ESC Council for Cardiology Practice, Pericardiocentesis in Cardiac Tamponade: Indications and Practical Aspects (2017)](https://www.escardio.org/communities/councils/cardiology-practice/scientific-documents-and-publications/ejournal/volume-15/Pericardiocentesis-in-cardiac-tamponade-indications-and-practical-aspects/); [Cook Medical, Pericardiocentesis Sets Instructions for Use, Rev. 11 (current revision, accessed 2026)](https://ifu.cookmedical.com/data/IFU_PDF/C_T_TTPS_REV11.PDF).

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null `assetName` values also remain an independent release blocker under the repository safety policy.

## `transvenous_pacemaker` - Transvenous Pacemaker

**Screening disposition: `MAJOR` (proposed; clinician adjudication required).**

**Source-standard summary.** AHA 2025 supports temporary transvenous pacing for persistent hemodynamically unstable bradycardia refractory to medical therapy, with transcutaneous pacing and/or adrenergic support while preparing. ESC 2021 limits temporary transvenous pacing to severe hemodynamically compromising or anticipated bradyarrhythmia, reversible indications, or a bridge to permanent pacing, and recommends the shortest feasible dwell time. ESC also describes access-site tradeoffs, avoidance of intrathoracic subclavian puncture, and risks including bleeding, perforation/tamponade, infection, thrombosis, arrhythmia, malfunction, and displacement.

**Findings.**

1. **`MAJOR` - `sections.anatomy`, `positioning`, `ultrasound`, `aftercare`:** The record does not provide an access-site decision framework or the ESC cautions for intrathoracic subclavian, jugular, and femoral access. It also lacks an explicit daily-necessity/shortest-duration plan and a pathway to active-fixation temporary pacing when prolonged support is expected. The clinician must define local access and escalation policy.
2. **`MAJOR` - `sections.equipment`, `steps`:** The generic setup omits the compatible patient cable/adapters, sheath-catheter compatibility, sterile contamination sleeve/locking mechanism, and product-specific balloon inflation medium/volume and deflation requirements. "Inflate balloon per catheter instructions" is directionally safe but not enough to confirm that the bedside setup is complete. The local catheter, generator, connection path, and IFUs must be named or deliberately deferred to a kit-specific checklist.
3. **`MAJOR` - `sections.contraindications`, `complications`:** Device-specific exclusions and warnings cannot be checked because no catheter/kit is identified. The complication list also omits bleeding/hematoma, thrombosis, and catheter-related bloodstream/device infection explicitly emphasized by ESC.
4. **`MAJOR` - `sections.references`:** The generic textbook citations have no edition/year/page and do not support device-specific setup or current indications.

**Equipment/instruments.** The core items are present: introducer, balloon-tipped catheter, generator, pads, ultrasound, sterile supplies, and backup pacing/pressors. Manufacturer documentation shows that catheter French size, recommended introducer, connector type, balloon capacity, and final-position instructions vary. A clinician must reconcile the card to the institution's actual kit and external generator rather than adopt a generic size.

**Dosing and monitoring.** No structured dosing is present. Pressors and sedation are referenced without agents/doses; the card should link to the approved bradycardia and sedation pathways if medication support is intended. Electrical plus mechanical capture, continuous monitoring, imaging, and re-checks after movement are appropriately emphasized. The clinician should decide whether capture threshold, output safety margin, sensitivity, rate, insertion depth, and dwell-time documentation need explicit fields.

**Other sections reviewed.** `shiftMode`, `indications`, `confirmation`, `troubleshooting`, `documentation`, and `seniorPearls` are broadly concordant with the reviewed standards. No pediatric or pregnancy claim is made. Infection/thrombus at the access site is acknowledged but remains incomplete without product and local-policy detail.

**Reviewer questions.** Which access-site hierarchy, catheter/introducer/generator system, balloon IFU, connector checklist, output/sensing targets, and maximum dwell/escalation plan are institutionally approved? Should the card link directly to the 2025 bradycardia medication pathway?

**Sources.** [American Heart Association, Part 9: Adult Advanced Life Support, 2025 CPR and ECC Guidelines (2025)](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-advanced-life-support); [European Society of Cardiology/European Heart Rhythm Association, Guidelines on Cardiac Pacing and CRT (2021)](https://academic.oup.com/eurheartj/article/42/35/3427/6358547); [Teleflex, Arrow Temporary Pacing Catheters and Kits (current manufacturer product information, accessed 2026)](https://www.teleflex.us.com/usa/en/product-areas/interventional/cardiac-diagnostics/pacing-catheters-and-kits/index.html); [Teleflex, Arrow Right Heart Catheters and Vascular Access product brochure (2026)](https://www.teleflex.com/usa/en/product-areas/interventional/cardiac-diagnostics/arrow-balloon-wedge-pressure-catheters/CC_RH_Right-Heart-Product-Brochure_BR_MC-000166_Rev%203_final.pdf).

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` remains an independent release blocker under repository policy.

## `resuscitative_thoracotomy` - Resuscitative Thoracotomy

**Screening disposition: `STOP-SHIP` (proposed; clinician adjudication required).** The card repeatedly directs the user to apply narrow criteria but does not actually state an operational adult decision pathway for a time-critical, invasive procedure.

**Source-standard summary.** The WTA 2024 adult algorithm defines signs of life, uses CPR-duration cutoffs of less than 10 minutes for blunt and less than 15 minutes for penetrating trauma, distinguishes injury pattern and tamponade, and limits the role of cardiac ultrasound to a specific decision branch. It also distinguishes thoracotomy from possible Zone 1 REBOA for selected abdominopelvic injury. EAST 2015 stratifies recommendations by mechanism, injury location, and signs of life rather than by penetrating chest trauma alone.

**Findings.**

1. **`STOP-SHIP` - `sections.shiftMode`, `indications`, `contraindications`:** "Short window," "short arrest interval," and "prolonged pulselessness" are not executable criteria. The record omits the actual signs-of-life definition, CPR cutoffs, and several EAST/WTA mechanism-location branches. A qualified trauma group must choose one named institutional algorithm and reproduce its inclusion/termination criteria exactly.
2. **`MAJOR` - `sections.ultrasound`, `confirmation`, `troubleshooting`:** "Cardiac standstill ... informs prognosis" is too broad. WTA places ultrasound motion/standstill in a defined PEA-only branch; it is not a free-standing termination criterion. The clinician must define when ultrasound may affect the decision and when it must not delay thoracotomy.
3. **`MAJOR` - `sections.steps`, `aftercare`:** Descending-aortic cross-clamping is presented generically. The card does not state the injury-pattern decision, reassessment endpoint, distal-ischemia implication, or where REBOA is a local alternative. The clinician must define indications and clamp-time communication/escalation requirements.
4. **`MAJOR` - `sections.equipment`:** The parenthetical tray list names a scalpel, Mayo scissors, and rib spreader but does not establish that the local tray contains a sternal-division instrument for clamshell extension, compatible internal-defibrillation equipment, vascular-control tools, and exposure-protection supplies in usable configuration. A local tray inventory and simulation check are required.
5. **`MAJOR` - `sections.references`:** The references name EAST/WTA/ATLS but provide no year, direct guideline, or selected institutional algorithm; they cannot support the card's vague decision language.

**Equipment/instruments.** Major instrument classes are named, including retractor, vascular clamps, forceps, suction, packing, Foley/suture wound control, internal paddles, rapid infuser, blood, and PPE. Exact instrument availability, sternum-division method, internal-paddle compatibility, and massive-transfusion workflow remain unverified.

**Dosing and monitoring.** No structured dosing is present. Blood-product resuscitation is qualitative and must remain tied to the institutional massive-transfusion protocol. The record includes airway, transfusion, clamp-time awareness, and operative destination but no explicit physiologic termination/ROSC thresholds from the selected algorithm.

**Other sections reviewed.** The incision level, superior-rib entry, anterior-to-phrenic-nerve pericardiotomy, temporary wound control, internal massage, complications, documentation, and senior pearls are broadly consistent with the reviewed sources. The visual is metadata-only and clinically unapproved.

**Reviewer questions.** Which WTA/EAST-derived local algorithm governs signs of life, blunt/penetrating CPR windows, injury-pattern branches, ultrasound use, REBOA, and termination? Does the actual tray support clamshell conversion and internal defibrillation without additional equipment?

**Sources.** [Western Trauma Association, Adult Emergency Resuscitative Thoracotomy Algorithm and Procedure Guide (2024)](https://westerntrauma.org/wp-content/uploads/2024/02/ERT-Algorithm-Procedures.pdf); [Eastern Association for the Surgery of Trauma, Emergency Department Thoracotomy Practice Management Guideline (2015)](https://www.east.org/education-resources/practice-management-guidelines/details/emergency-department-thoracotomy).

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` remains an independent release blocker under repository policy.

## `synchronized_cardioversion` - Synchronized Cardioversion

**Screening disposition: `MAJOR` (proposed; clinician adjudication required).**

**Source-standard summary.** The AHA 2025 electrical-cardioversion algorithm lists initial biphasic energies of 200 J for atrial fibrillation, 200 J for atrial flutter, 100 J for narrow-complex tachycardia, and 100 J for monomorphic VT; polymorphic VT requires unsynchronized high-energy shock. It requires sedation when feasible, notes possible re-synchronization after each shock, and directs immediate unsynchronized shocks if critical deterioration makes synchronization delay unsafe. The 2023 ACC/AHA/ACCP/HRS AF guideline requires three weeks of uninterrupted therapeutic anticoagulation or thrombus-excluding imaging before elective cardioversion when AF duration is at least 48 hours, and at least four weeks of uninterrupted anticoagulation afterward.

**Findings.**

1. **`MAJOR` - `sections.shiftMode`, `steps`:** The energy line is outdated against AHA 2025: AF `120-200 J` should be adjudicated against 200 J, and atrial flutter is grouped with SVT at `50-100 J` rather than the current 200 J flutter recommendation. The clinician must approve device-specific energies and escalation.
2. **`MAJOR` - `sections.indications`, `complications`, `aftercare`:** "After appropriate anticoagulation" and "resume or initiate ... as indicated" omit the AF-duration, pre-cardioversion anticoagulation/imaging, post-cardioversion four-week, LAA thrombus, and elevated-risk short-duration AF decision points. A clinician must define the urgent-versus-elective thromboembolism pathway and whether it is embedded or linked.
3. **`MINOR` - `sections.steps`, `seniorPearls`:** Rechecking synchronization before every shock is correct, but "most devices" reset is not device-independent. Current Philips and LIFEPAK IFUs show that persistence/reset can be configured. The safety instruction should be tied to the local defibrillator configuration/IFU without asserting a universal default.
4. **`INSUFFICIENT EVIDENCE` - `sections.aftercare`:** A universal telemetry period of "at least 1-3 hours" was not established by the reviewed authoritative sources and depends on arrhythmia, sedation, comorbidity, treatment, and institutional policy. The clinician must approve a disposition/monitoring standard.
5. **`MAJOR` - `sections.references`:** Generic ACLS/AF/textbook labels without years or direct sources do not support the current energy and anticoagulation details.

**Equipment/instruments.** Defibrillator, pads, ECG, IV, oxygenation/ventilation monitoring, suction, airway equipment, and crash-cart support are present. The asserted 8 cm implanted-device separation and pad-vector claims require confirmation against the local defibrillator/pad and implanted-device guidance. The clinician should verify whether two IV sites and the listed resuscitation drugs are requirements or optional local preparation.

**Dosing and monitoring.** No structured dosing is present. Sedative choices are named without doses, analgesia strategy, contraindications, or a medication-specific monitoring/recovery pathway. That avoids an incorrect dose but is not a complete sedation protocol; the procedure should link to an approved sedation/dosing source. Pulse oximetry, capnography, ECG, airway backup, immediate rhythm/hemodynamic reassessment, and post-shock 12-lead ECG are present.

**Other sections reviewed.** `contraindications`, `anatomy`, `positioning`, `confirmation`, `troubleshooting`, and `documentation` are broadly concordant apart from the device-specific questions above. `ultrasound` is empty and not required for routine cardioversion. No pediatric or pregnancy claim is made.

**Reviewer questions.** Will the card adopt the 2025 AHA energies? What urgent/elective AF/AFL anticoagulation and imaging pathway is approved? Which defibrillator model/configuration governs synchronization persistence, pad placement, and implanted-device clearance? What sedation and recovery protocol is linked?

**Sources.** [American Heart Association, Electrical Cardioversion Algorithm (2025)](https://www.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-ACLS-Electrical-Cardioversion-250514.pdf); [ACC/AHA/ACCP/HRS, Guideline for the Diagnosis and Management of Atrial Fibrillation (2023; Circulation publication 2024)](https://www.heart.org/-/media/Files/Professional/Quality-Improvement/Get-With-the-Guidelines/Get-With-The-Guidelines-AFIB/AFib-Month/joglaretal20232023areportofaccahaaccphrsguidelineforthediagnosisandmanagementofatrialfibrillation.pdf); [Philips, HeartStart Intrepid Instructions for Use (2026)](https://www.documents.philips.com/assets/Instruction%20for%20Use/20260409/61228223de4b4609bcb7b42700742496.pdf?feed=ifu_docs_feed); [Stryker, LIFEPAK 15 Operating Instructions (current revision accessed 2026)](https://www.stryker.com/content/dam/stryker/ems/resources/operating-instructions/international/3314911-030_int-eng_lifepak_15_operating_instructions.pdf).

`reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `lumbar_puncture` - Lumbar Puncture

**Screening disposition: `STOP-SHIP` (proposed; clinician adjudication required).** The meningitis indication lacks an explicit safeguard that imaging or LP must not cause a clinically significant delay to empiric antimicrobial treatment.

**Source-standard summary.** WHO 2025 and NICE 2024 advise against routine cranial imaging before LP, define clinical features that require imaging/deferral, and state that LP should not delay antibiotics in suspected bacterial meningitis. NICE also calls for stabilization of airway, breathing, shock, seizures, and bleeding risk, and measurement of blood glucose immediately before LP when meningitis is suspected. CDC recommends a surgical mask for LP. Evidence-based guidance strongly favors atraumatic needles in adults and children; consensus technique requires lateral recumbency for opening pressure and supports stylet replacement before needle removal. Antithrombotic hold times vary by agent, dose, renal function, and laboratory assessment.

**Findings.**

1. **`STOP-SHIP` - `sections.indications`, `contraindications`, `steps`:** The record does not state that LP or pre-LP imaging must not materially delay empiric antibiotics for suspected bacterial meningitis. It also replaces guideline imaging/deferral criteria with the nonspecific phrase "signs of elevated ICP/mass lesion" and does not explicitly require stabilization of shock, airway/respiratory compromise, or uncontrolled seizures. The clinician must approve a precise meningitis safety pathway, including blood cultures/glucose and treatment timing.
2. **`MAJOR` - `sections.equipment`, `steps`, `complications`:** "Spinal needle with stylet" does not express the strong all-age preference for an atraumatic/pencil-point needle or the required introducer where applicable. The clinician must select approved needle designs/gauges/lengths for adult and pediatric use and define exceptions.
3. **`MAJOR` - `sections.shiftMode`, `contraindications`:** "Anticoagulation depending context" is not operational for a neuraxial procedure with potentially catastrophic concealed bleeding. The clinician must link a current local antithrombotic table that accounts for agent, dose, renal function, timing, platelet/coagulation assessment, urgency, and reversal policy; this report does not transpose neuraxial-anesthesia intervals into an LP order set.
4. **`MINOR` - `sections.positioning`, `steps`, `confirmation`:** Lateral decubitus is correctly required for opening pressure, but the record does not state the approved horizontal/relaxed measurement position, manometer zero/reference, timing before CSF removal, or how sedation/straining affects interpretation. The clinician must define the measurement standard.
5. **`INSUFFICIENT EVIDENCE` - pediatric scope:** The procedure declares `Peds`, but the record provides no age/size-specific needle, positioning/sedation, CSF-volume, opening-pressure interpretation, or neonatal pathway. The reviewed general sources do not validate a complete pediatric/neonatal card. A pediatric clinician must approve these elements or narrow the setting claim.
6. **`MAJOR` - `sections.references`:** Generic textbooks and local-policy language without editions, years, or direct guidance do not support meningitis timing, imaging, anticoagulation, infection control, or pediatric claims.

**Equipment/instruments.** Mask, sterile gloves/prep/drape, styleted needle, manometer, labeled tubes, local anesthetic, assistant, and longer backup needles are present. The card needs clinician-approved atraumatic needle/introducer options and age/body-habitus-specific kit guidance. CDC mask guidance is satisfied in the equipment list.

**Dosing and monitoring.** No structured dosing is present. Local anesthetic is named without concentration or maximum dose; pediatric use makes weight-based limits material if dosing is to be displayed. Sedation is not addressed despite the pediatric setting; any sedation content must link to a monitored institutional pathway. Neurologic reassessment and return precautions are present.

**Other sections reviewed.** `anatomy`, `ultrasound`, `troubleshooting`, `aftercare`, `documentation`, `seniorPearls`, and the instruction to replace the stylet are broadly concordant. Symptomatic supine rest is not presented as proven prophylaxis, but it should not be reframed as preventing post-dural-puncture headache. Both visual assets remain unreviewed placeholders.

**Reviewer questions.** What exact meningitis antibiotic/imaging/stabilization pathway is approved? Which atraumatic needles and pediatric variants are stocked? What local antithrombotic policy and opening-pressure standard should be linked? Does the card retain `Peds`, and if so, who supplies neonatal/child-specific sedation, volume, and interpretation limits?

**Sources.** [World Health Organization, Guidelines on Meningitis Diagnosis, Treatment and Care (2025)](https://iris.who.int/bitstream/handle/10665/381006/9789240108042-eng.pdf); [NICE, Bacterial Meningitis and Meningococcal Disease, NG240 (2024)](https://www.nice.org.uk/guidance/NG240/chapter/recommendations); [CDC/HICPAC, Safe Injection and Special Lumbar Puncture Infection-Control Practices (2007 guideline; current CDC page)](https://www.cdc.gov/injection-safety/hcp/clinical-guidance/index.html); [BMJ Rapid Recommendation, Atraumatic Versus Conventional Needles for Lumbar Puncture (2018)](https://www.bmj.com/content/361/bmj.k1920); [Consensus Guidelines for Lumbar Puncture in Neurological Diseases (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5454085/); [ASRA Pain Medicine, Antithrombotic/Thrombolytic Therapy Guidelines, fifth edition (2025)](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766).

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` values remain an independent release blocker under repository policy.

## Changed File and Sources/Limitations

**Changed file:** `docs/audits/procedure-verification/04_CARDIAC_NEURO.md` only. No JSON, Swift, validator, dosing, or reviewer-status field was modified.

**Source approach:** Direct society/government guidelines, consensus documents, and representative manufacturer IFUs/product documentation were browsed on 2026-07-18. Secondary summaries were not used as sole support for any finding. Source years are stated above.

**Limitations:** This lane is not a licensed clinical review and cannot approve content. Evidence quality is limited for several rare procedures, and local credentialing, equipment, trauma-system capability, sedation, anticoagulation, transfusion, pediatric, and device-configuration policies materially affect the correct wording. Representative IFUs do not establish the institution's stocked device. Structural validation was not run because the clinical JSON and validators were intentionally left untouched. `reviewerStatus` remains unchanged for every assigned procedure.
