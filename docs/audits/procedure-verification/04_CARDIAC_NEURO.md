# Lane 04: Cardiac and Neuro Procedure Verification

- Audit date: 2026-07-18
- Audited snapshot: `Procedures/Resources/procedures.json` SHA-256 `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Scope: `pericardiocentesis`, `transvenous_pacemaker`, `resuscitative_thoracotomy`, `synchronized_cardioversion`, and `lumbar_puncture` only.
- Boundary: AI-assisted evidence and discrepancy screening, not medical approval. All findings and proposed dispositions require qualified clinical review.

Every JSON section, equipment/instrument list, visual-asset record, and structured-dosing field in each assigned procedure was screened. None of the five records contains a `structuredDosing` object.

## Owner adjudication - 2026-07-31

**How to read this section.** The lane report above is the AI screening record
against the audited snapshot and is left as written. This section records what
the clinical owner decided on 2026-07-31 and what changed in `05ca4f0`. The five
`Screening disposition` lines below have been re-screened against the amended
content; the original rationale is kept inline on each so nothing is quietly
rewritten.

### The shape of all three stop-ship findings was the same

Each of the three was a card that named a decision without stating it.
Pericardiocentesis said aortic dissection "requires extreme caution".
Resuscitative thoracotomy said to "apply the criteria, do not improvise them"
and then never gave them. Lumbar puncture described a meningitis workup without
the one rule that governs its timing. In all three the prose reads as competent,
which is what makes it dangerous: a reader takes the confident tone as evidence
that the missing specifics are somewhere else on the card.

That pattern is worth naming because it is invisible to every gate in this
repository. A record can pass the schema, the reference gate, the thin-section
check, and the fingerprint ledger while telling the reader to apply criteria it
does not contain.

### Decisions

1. **Aortic dissection and post-infarction free-wall rupture are surgical
   exclusions, not cautions.** The mechanism is now stated rather than implied:
   draining the pericardium restores the blood pressure and raises the
   transmural gradient across the tear, and the tamponade was the only thing
   slowing the bleed. The ESC bridge exception is kept but bounded - impending
   arrest with no immediate surgical option, small aliquots, target the lowest
   perfusing pressure, stop when it returns. The aliquot figure is written as an
   order of magnitude and labelled a local decision, because ESC describes the
   principle rather than a number.
2. **Cardioversion energies move to the current AHA figures.** Verified directly
   against AHA's adult advanced life support guidance rather than taken from the
   lane report: at least 200 J is reasonable for atrial fibrillation, 200 J may
   be reasonable for atrial flutter. The card states both and states that the
   recommendation is stronger for fibrillation than for flutter, because it is.
3. **No antithrombotic hold table was invented for lumbar puncture.** The
   question the audit asked - what interval, for which agent, at what renal
   function - cannot be answered by this repository, and a transposed
   neuraxial-anaesthesia interval would be a fabricated policy wearing a
   citation. What replaced it is the post-procedure surveillance rule, which is
   the thing that actually converts a rare spinal haematoma into a recoverable
   one.
4. **Lumbar puncture drops its `Peds` setting.** It claimed paediatric scope and
   contained no paediatric specific: no interspace, no needle length, no volume,
   no sedation, no age-adjusted opening pressure. Adding a partial paediatric
   section under a retained claim would have been worse than either alternative.
   This is reversible and is flagged as an open owner choice below.

### Adopted beyond the stated findings

- **Pericardiocentesis could not confirm its own needle position in the case it
  exists for.** The confirmation section relied on "drainage of pericardial
  fluid rather than blood from chamber". In haemopericardium the aspirate is
  blood, so the test returns the same answer whether the needle is in the sac or
  in the ventricle. Three tests that work replace it - agitated saline, direct
  visualisation of the catheter in the space, and a transduced waveform - and
  the non-clotting property of pericardial blood is demoted to a supporting sign.
- **A pre-dilation gate, matching the one the vascular records already carry.**
  A needle in the right ventricle makes a hole most patients survive. A dilator
  and a pigtail railroaded over a wire in the right ventricle makes one they may
  not. The wire is now confirmed inside the pericardial space before dilation,
  with no emergency exception, in the same shape the CVC, introducer, and
  dialysis records use.
- **The thoracotomy tray named no instrument that divides a sternum.** "Extend
  across the sternum (clamshell)" was a step with no means. The equipment list
  now asks which of a Lebsche knife, Gigli saw, or heavy trauma shears is
  actually in the tray.
- **The oesophagus is named as the structure cross-clamped by mistake**, with
  the orogastric tube as the way to tell, and the troubleshooting entry now says
  to question the clamp before questioning the patient.
- **The internal mammary arteries after a clamshell.** They do not bleed while
  the patient is arrested. They bleed at the moment the resuscitation starts
  working, which is the moment nobody is looking at the sternal edges.
- **The lumbar puncture steps were wrong for the needle the evidence prefers.**
  "Bevel oriented appropriately" is a cutting-needle instruction; a pencil-point
  needle has no bevel to orient and gives a subtle or absent pop, which is what
  makes an operator waiting for the pop advance too far. Both are now stated.
- **Cardioversion never mentioned the manufacturer's recommended dose.**
  Biphasic waveforms are not interchangeable and the AHA guidance defers to the
  manufacturer. That deference is now on the card, above the numbers.
- **Implanted device interrogation after cardioversion**, which the record
  omitted entirely, and removal of transdermal patches from the pad path.
- **No capture at maximum output is a position problem.** Climbing the output is
  the intuitive move and the wrong one; the pacing card now says so in shiftMode
  and in troubleshooting, together with the balloon rules the record lacked -
  air only, inflated past the introducer, never forced.
- **Access-site choice on the pacing card now protects the vein a permanent
  device will need**, which is a consequence of the choice that no complication
  list would have surfaced.

### Known residual gaps

- The narrow-complex SVT figure moved from `50-100 J` to `100 J`. That is a
  narrowing to the top of the range the card already carried, consistent with
  the verified fibrillation and flutter direction, but the SVT and monomorphic
  VT figures in the 2025 algorithm could not be extracted from the primary PDF
  in this environment - its energy table is not machine-readable text. The
  monomorphic VT figure is unchanged at 100 J. Both remain open to owner
  correction against the printed algorithm.
- No device in this lane is bound to a stocked IFU revision: the
  pericardiocentesis set, the pacing catheter and its generator and connector
  cable, the defibrillator, and the internal paddles. Each record now names what
  must be looked up rather than asserting a generic value. This stays under P3.1.
- The 8 cm implanted-device pad clearance is stated as the commonly cited
  minimum needing manufacturer confirmation rather than as a fact.
- The pericardial drain-removal threshold and the internal-defibrillation energy
  are written as the commonly used figures with their owners named, not as
  guideline values.
- Resuscitative thoracotomy reproduces the WTA 2024 criteria. The reference line
  asks for the local algorithm to be named, and the tray inventory and clamshell
  simulation check are unverified.
- Paediatric scope is deferred on all five records rather than specified.

## `pericardiocentesis` - Pericardiocentesis

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot, for the reason recorded next. The findings are addressed in `05ca4f0`. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because the bridge-drainage aliquot and the drain-removal threshold are stated as the commonly used figures with their owners named rather than as guideline values, the stocked kit is not bound to an IFU revision, and artwork is outstanding. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP** because of the potentially harmful treatment of aortic-dissection or free-wall-rupture tamponade as a generic caution rather than a surgical emergency with only tightly controlled bridge drainage in exceptional circumstances.

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

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null `assetName` values are warnings rather than release blockers since the owner decision of 2026-07-30; the card falls back to its SF Symbol and reads correctly.

## `transvenous_pacemaker` - Transvenous Pacemaker

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally MAJOR against the audited snapshot, for the reason recorded next. The findings are addressed in `05ca4f0`. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because the catheter, generator, and connector cable are named as things to look up locally rather than bound to a stocked IFU revision, and the balloon volume, threshold margin, and insertion depth are conventional figures qualified as typical. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **MAJOR** for access-site, device-binding, complication, and reference gaps.

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

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` is a warning rather than a release blocker since the owner decision of 2026-07-30.

## `resuscitative_thoracotomy` - Resuscitative Thoracotomy

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot, for the reason recorded next. The findings are addressed in `05ca4f0`. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because the criteria reproduced are WTA 2024's rather than a named institutional algorithm, the internal-defibrillation energy is an order of magnitude to confirm against the device, and the tray inventory and clamshell simulation check remain unverified. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP** because the card repeatedly directs the user to apply narrow criteria but does not actually state an operational adult decision pathway for a time-critical, invasive procedure.

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

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` is a warning rather than a release blocker since the owner decision of 2026-07-30.

## `synchronized_cardioversion` - Synchronized Cardioversion

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally MAJOR against the audited snapshot, for the reason recorded next. The findings are addressed in `05ca4f0`. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because the narrow-complex SVT and monomorphic VT energies could not be read from the primary algorithm PDF in this environment, the 8 cm implanted-device clearance is stated as needing manufacturer confirmation, and the observation period is deliberately left to local policy. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **MAJOR** for outdated energies, an incomplete anticoagulation pathway, a device-dependent synchronization claim, an unsupported telemetry period, and untraceable references.

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

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot, for the reason recorded next. The findings are addressed in `05ca4f0`. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because no antithrombotic hold table is stated - deliberately, since this repository cannot source one - the opening-pressure range is the commonly cited one, and paediatric scope was removed rather than specified. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP** because the meningitis indication lacks an explicit safeguard that imaging or LP must not cause a clinically significant delay to empiric antimicrobial treatment.

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

`reviewerStatus` remains unchanged (`Needs Clinical Review`). The null visual `assetName` values are warnings rather than release blockers since the owner decision of 2026-07-30.

## Changed File and Sources/Limitations

**Changed file:** `docs/audits/procedure-verification/04_CARDIAC_NEURO.md` only. No JSON, Swift, validator, dosing, or reviewer-status field was modified.

**Source approach:** Direct society/government guidelines, consensus documents, and representative manufacturer IFUs/product documentation were browsed on 2026-07-18. Secondary summaries were not used as sole support for any finding. Source years are stated above.

**Limitations:** This lane is not a licensed clinical review and cannot approve content. Evidence quality is limited for several rare procedures, and local credentialing, equipment, trauma-system capability, sedation, anticoagulation, transfusion, pediatric, and device-configuration policies materially affect the correct wording. Representative IFUs do not establish the institution's stocked device. Structural validation was not run because the clinical JSON and validators were intentionally left untouched. `reviewerStatus` remains unchanged for every assigned procedure.
