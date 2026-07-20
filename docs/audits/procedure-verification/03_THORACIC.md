# Thoracic Procedure Verification Audit

**Audit date:** 2026-07-18  
**Scope:** `thoracostomy_chest_tube`, `pigtail_catheter`, `needle_decompression`, `thoracentesis`  
**Corpus fingerprint:** `procedures.json` SHA-256 `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1` (matched before review)  
**Boundary:** AI-assisted discrepancy screen only. This report is not clinical approval, credentialing, or an institutional protocol.

## thoracostomy_chest_tube - Thoracostomy / Chest Tube

**Screening disposition: STOP-SHIP.** The release-blocking disposition is driven by unreviewed placeholder visual assets under the repository safety policy. The clinical text also has several `MAJOR` omissions requiring clinician adjudication.

### Source-standard summary

The [BTS Clinical Statement on pleural procedures (2023)](https://thorax.bmj.com/content/78/Suppl_3/s43) supports blunt-dissection drains, holding sutures, prompt post-insertion radiography, small-bore drains for most non-trauma indications, larger drains for unstable trauma/substantial air leak, controlled effusion drainage, avoidance of routine early suction, and explicit drain-system safety. The [WTA traumatic pneumothorax algorithm (2022)](https://www.westerntrauma.org/wp-content/uploads/2024/02/32-Evaluation-and-management-of-traumatic-pneumothorax_-A-Western-Trauma-Association-critical-decisions-algorithm.pdf) supports small-caliber thick-walled tubes for uncomplicated traumatic pneumothorax but consideration of 28 Fr with a significant hemothorax. The [WSES-AAST thoracic trauma guideline (2025)](https://link.springer.com/article/10.1186/s13017-025-00651-1) specifies escalation for instability or major ongoing tube output. The [EAST antibiotic prophylaxis guideline (2022)](https://www.east.org/education-resources/practice-management-guidelines/details/antibiotic-prophylaxis-for-tube-thoracostomy-placement-in-trauma-a-practice-management-guideline-from-the-eastern-association-for-the-surgery-of-trauma) conditionally recommends prophylaxis at insertion for adult trauma tube thoracostomy.

### Findings

- **STOP-SHIP - `visualAssets`:** Both declared assets have `assetName: null` and explicitly say artwork is pending clinical review. Repository policy makes placeholder clinical visuals release-blocking. The landmark wording is broadly consistent with reviewed standards, but no image can be treated as approved.
- **MAJOR - `equipment`, `shiftMode`, `steps`:** "Appropriate tube size" gives no decision rule. This record spans pneumothorax, hemothorax, empyema, ventilated patients, and unstable trauma, where BTS/WTA/WSES-AAST distinguish small-bore from larger-bore drainage. A vague selector is an incomplete instrument setup at the bedside.
- **MAJOR - `troubleshooting`, `aftercare`:** "Notify surgery/trauma if high-volume or ongoing" and "escalate early" do not define a local activation threshold or action. WSES-AAST (2025) identifies hemodynamic instability, more than 1,500 mL/24 h, or more than 200 mL/h for 3 consecutive hours as operative-management triggers, while noting that patient physiology and resuscitation needs matter. A clinician must choose the institution's exact trigger language.
- **MAJOR - `indications`, `equipment`, `steps`, `aftercare`:** The trauma pathway omits any decision on insertion-time antibiotic prophylaxis. EAST (2022) conditionally recommends it for adult trauma tube thoracostomy. The report should not invent an agent or dose; the clinician must decide whether to include or link the local prophylaxis protocol.
- **MAJOR - `equipment`, `steps`, dosing/monitoring:** The record says "local anesthetic" and "anesthetize ... generously" without concentration, weight-based ceiling, total-dose accounting, toxicity monitoring, or rescue readiness. BTS (2023) describes 1% lidocaine and a conservative 3 mg/kg (maximum 250 mg) pleural-procedure ceiling while acknowledging variation; the [Fresenius Kabi/FDA DailyMed label, revised 2025](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=cddb2b22-fce3-8967-6e54-dca3df5ac4b3) gives 4.5 mg/kg without epinephrine (generally no more than 300 mg), calls for the lowest effective dose, monitoring, and immediate resuscitation capability. The JSON has no structured `dosing` block; the current model only mandates one for regional anesthesia, so software validation would not detect this omission.
- **MAJOR - `troubleshooting`, `aftercare`:** The record does not state key drain-system failure controls: keep the bottle below the insertion site and upright, avoid clamping a bubbling drain except under specialist direction, prescribe/document suction if used, and control large-effusion drainage with a prompt stop/clamp response to repetitive cough or chest pain. BTS (2023) treats these as safety practice points because uncontrolled drainage can cause potentially fatal re-expansion pulmonary oedema.
- **MAJOR - `references`:** The references are undated textbooks and a local-policy reminder, with no current primary guideline, consensus statement, or direct locator capable of supporting the record's trauma, drain-size, suction, and failure-plan claims.

### Equipment, dosing, and remaining sections

The tray, scalpel, Kelly clamp, suture, occlusive dressing, connected underwater-seal/suction system, sterile barriers, analgesia/sedation planning, and ultrasound availability are directionally appropriate. Size selection, backup/rescue setup, controlled-drainage instructions, and local-anesthetic limits remain incomplete. Sedation monitoring and rescue requirements are institution-dependent and should link to a credentialed local pathway rather than be improvised here. No additional material discrepancy was identified in the reviewed positioning, ultrasound, confirmation, complications, documentation, or senior-pearl text; indications/contraindications remain dependent on patient physiology, anticoagulation, prior surgery/adhesions, and local trauma policy.

### Questions for the clinical reviewer

1. Define drain type/caliber by uncomplicated pneumothorax, pleural infection/effusion, significant hemothorax, unstable trauma, substantial air leak, and mechanical ventilation.
2. Select the local massive-hemothorax activation criteria and immediate surgical/trauma response.
3. Decide whether trauma antibiotic prophylaxis and pleural local-anesthetic limits belong in this card or in mandatory linked protocols.
4. Add the drain-system and controlled-effusion rescue actions, then commission and approve the two visual assets.

**Proposed clinician disposition:** Keep out of release pending correction and qualified thoracic/trauma review. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## pigtail_catheter - Pigtail Pleural Catheter

**Screening disposition: STOP-SHIP.** Placeholder clinical visuals and a missing immediate stop/clamp response for symptomatic effusion drainage are release-blocking; equipment and dosing details also require review.

### Source-standard summary

BTS (2023) supports small-bore drains (generally less than 14 Fr; 14 Fr or smaller for initial pleural-infection drainage), ultrasound for fluid, holding-suture securement, post-insertion radiography, and controlled drainage. The [EAST hemothorax practice guideline (2021)](https://pubmed.ncbi.nlm.nih.gov/33487403/) conditionally supports pigtail catheters for traumatic hemothorax only in hemodynamically stable patients. The [Cook Fuhrman Pleural Drainage Set IFU (current IFU accessed 2026)](https://ifu.cookmedical.com/data/IFU_PDF/C_T_PPD-M_REV0.PDF) warns that over-insertion of the needle, wire, dilator, or catheter can cause serious or life-threatening injury; selection must account for French size, length, patient size, and anatomy; and the wire must advance without impedance and extend beyond the catheter tip.

### Findings

- **STOP-SHIP - `visualAssets`:** Both assets are placeholders with `assetName: null` and pending-review captions. Their concepts are useful, but release requires clinically reviewed artwork and confirmation that the depicted wire/dilator depths match the selected kit IFU.
- **STOP-SHIP - `troubleshooting`, `aftercare`, `shiftMode`:** For effusion drainage, the record lists re-expansion pulmonary edema but gives no drainage-volume/rate plan and no immediate instruction to stop or clamp drainage for repetitive/persistent cough, chest pain/tightness, or worsening breathlessness. BTS (2023) calls for controlled drainage and prompt clamping of an effusion drain when repetitive coughing or chest pain develops because re-expansion pulmonary oedema can be fatal.
- **MAJOR - `equipment`, `steps`, `visualAssets`:** "Pigtail kit" and generic needle/wire/dilator language do not specify catheter French size/length, wire compatibility, or a patient-specific maximum insertion/dilator depth. The main steps say "dilate gently" but omit the IFU's life-threatening over-insertion warning and the requirement that the wire extend beyond the catheter tip; BTS also advises guarded dilators where possible. This is an incomplete Seldinger instrument and depth-safety setup.
- **MAJOR - `indications`, `contraindications`:** The trauma limitation is directionally correct but non-operational: "massive hemothorax or unstable trauma may need" escalation. EAST (2021) limits its conditional pigtail recommendation to hemodynamically stable traumatic hemothorax; WSES-AAST (2025) recommends a large tube for unstable traumatic hemothorax. The clinician must state whether instability/active major bleeding excludes bedside pigtail placement in the intended setting.
- **MAJOR - `equipment`, `steps`, dosing/monitoring:** Local anesthetic is named without concentration, maximum cumulative dose, toxicity monitoring, or rescue readiness. The BTS 2023 pleural-procedure limit and the 2025 DailyMed label differ in ceiling, making this a clinician/institution decision that should be explicit. There is no structured `dosing` block, and current validation would not require one for this category.
- **MAJOR - `references`:** Undated textbooks and a local-policy reminder do not support the Seldinger safety warnings, selected trauma use, tube size/length, or controlled-drainage plan.

### Equipment, dosing, and remaining sections

Ultrasound, sterile cover/gel, drainage connection, securement, occlusive dressing, and flush supplies are appropriate categories. The record correctly says not to force a resistant wire, to retain wire control, verify all side holes are intrathoracic, secure the catheter, and obtain imaging. No additional material discrepancy was identified in positioning, ultrasound anatomy, confirmation, obstruction/dislodgement troubleshooting, complications, documentation, or senior pearls. Anticoagulation, loculated fluid, sedation monitoring, flush regimen, and escalation destination remain local-policy or specialty dependencies.

### Questions for the clinical reviewer

1. Specify approved kit(s), catheter French size/length by indication, wire/dilator compatibility, and depth-limiting method from the chosen manufacturer IFU.
2. Make hemodynamic/respiratory instability and suspected major traumatic bleeding an explicit selection decision.
3. Add the controlled-effusion drainage prescription and immediate symptom response.
4. Decide how local-anesthetic dose ceilings and LAST readiness will be surfaced, then commission and approve both visuals.

**Proposed clinician disposition:** Keep out of release pending correction and qualified pulmonary/thoracic/trauma review. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## needle_decompression - Needle Decompression

**Screening disposition: STOP-SHIP.** The life-saving device is not numerically specified, creating a plausible failed-decompression risk; both visuals are also unreviewed placeholders.

### Source-standard summary

The [Joint Trauma System Wartime Thoracic Injury CPG (2018)](https://jts.health.mil/assets/docs/cpgs/Wartime_Thoracic_Injury_26_Dec_2018_ID74.pdf) specifies a 14-gauge or larger, 3.25-inch/8-cm catheter at the fourth or fifth intercostal space anterior axillary line, with second intercostal space midclavicular line as the alternate (and primary pediatric site), warns against short 5-cm IV catheters, and describes subsequent tube thoracostomy or stable-patient imaging. The WTA traumatic pneumothorax algorithm (2022) prefers finger thoracostomy over needle decompression when rapid skilled decompression is available because needle success is variable, followed by a chest tube. WSES-AAST (2025) identifies tension pneumothorax as requiring immediate treatment and chest tube as definitive treatment.

### Findings

- **STOP-SHIP - `equipment`, `shiftMode`, `steps`:** "Long large-bore angiocath or decompression device" and "short catheters fail" omit gauge and usable length. The visual mentions a possibly insufficient 5-cm catheter but does not positively specify the required device. JTS specifies 14 gauge or larger and 3.25 inches/8 cm for its adult trauma pathway. An unquantified device requirement can cause failure to reach the pleural space in a crashing patient.
- **STOP-SHIP - `visualAssets`:** Both landmark/danger-zone assets have `assetName: null` and pending-review captions. Wrong landmark depiction would be high consequence; release requires reviewed artwork.
- **MAJOR - `shiftMode`, `anatomy`, `steps`, `visualAssets`:** Site wording is internally inconsistent and partly ambiguous: the text allows "4th/5th anterior or mid-axillary," while the visual specifies anterior axillary and the JTS adult pathway specifies anterior axillary (with 2nd-space midclavicular alternate). "Anterior" alone is not a landmark, and "mid-axillary" is not the cited JTS location. The clinician must choose the standard(s) and exact intended site language for ED/ICU/trauma users.
- **MAJOR - `shiftMode`, `troubleshooting`, `aftercare`:** The fallback is inconsistent. Shift Mode permits an alternate decompression site; troubleshooting says to proceed directly to finger/tube thoracostomy rather than repeat needle attempts. JTS allows repeat needle decompression when tube placement is delayed, whereas WTA prefers finger thoracostomy when capability exists. This must be resolved into one capability- and setting-specific pathway with an immediate reassessment interval.
- **MAJOR - `shiftMode`, `confirmation`, `aftercare`:** "Definitive tube thoracostomy usually follows" and "if indicated" are too permissive for the trauma pathway without defining the stable-patient exception. JTS says needle decompression alone is insufficient in most cases but permits ultrasound/CXR assessment in stable patients; WTA says rapid decompression in significantly deteriorating trauma is followed by a tube. The clinician must define when immediate tube/finger thoracostomy is mandatory and when imaging-based reassessment is acceptable.
- **MAJOR - `references`:** The current references do not identify any device, landmark, trauma algorithm, pediatric distinction, or definitive-management standard.

### Equipment, dosing, and remaining sections

Rapid exposure, side confirmation, over-the-rib entry, immediate reassessment, chest-tube readiness, and reassessment of competing shock causes are appropriate. Chlorhexidine/alcohol "if time allows" is reasonable in a peri-arrest maneuver. Structured medication dosing is not applicable unless the clinician adds analgesia/sedation; no delay for medication should be introduced into the crash pathway. The listed BP, oxygenation, breath sounds, ventilator pressures, and chest rise are useful monitoring targets. No additional material discrepancy was identified in indications, contraindications, ultrasound, complications, documentation, or senior pearls. Pediatric technique is materially different in the JTS source; because this record is not tagged `Peds`, the reviewer should either state adult scope or add a separately reviewed pediatric path. Pregnancy and non-traumatic tension physiology remain evidence/context limitations.

### Questions for the clinical reviewer

1. Specify the stocked decompression device's gauge, usable catheter length, and approved manufacturer/device rather than relying on "long" and "large-bore."
2. Choose exact primary and alternate landmarks for each intended setting and reconcile text with the visual.
3. Define the immediate failed-needle pathway according to operator capability and the definitive thoracostomy/stable-imaging exception.
4. State adult-only scope or commission a separately sourced pediatric pathway, then approve both visuals.

**Proposed clinician disposition:** Keep out of release pending device, landmark, fallback, and visual correction with qualified trauma/emergency review. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## thoracentesis - Thoracentesis

**Screening disposition: STOP-SHIP.** The procedure explicitly permits vacuum-bottle therapeutic drainage, contradicting the current BTS safety statement; its only visual is also an unreviewed placeholder.

### Source-standard summary

BTS (2023) requires thoracic ultrasound for pleural-fluid aspiration, prefers a catheter for therapeutic aspiration over 60 mL, recommends slow manual syringe or gravity drainage, advises against vacuum bottles/wall suction, generally limits one attempt to 1.5 L, and says to stop for chest tightness, pain, persistent cough, or worsening breathlessness. The [BTS Guideline for pleural disease (2023)](https://thorax.bmj.com/content/78/11/1143) calls for immediate pH analysis in suspected pleural infection and warns against local-anesthetic/heparin contamination or delay; it recommends both plain and blood-culture containers when infection is suspected. The [Society of Hospital Medicine ultrasound position statement (2018)](https://cdn.mdedge.com/files/s3fs-public/Document/January-2018/jhm013020126.pdf) recommends against routine post-procedure CXR after successful ultrasound-guided thoracentesis in an asymptomatic patient with normal post-procedure lung sliding.

### Findings

- **STOP-SHIP - `equipment`, `steps`:** "Vacuum drainage bottles" are listed and the operator is told to drain by gravity "to vacuum bottle." BTS (2023) specifically advises against vacuum bottles or wall suction for therapeutic thoracentesis after an RCT found more pneumothorax, hemothorax, and re-expansion pulmonary oedema with continuous suction. This is a direct conflict with a current specialty-society safety statement.
- **STOP-SHIP - `visualAssets`:** The sole landmark asset has `assetName: null` and is explicitly a placeholder. The caption correctly identifies what an eventual image must show, but it cannot ship without clinical review.
- **MAJOR - `anatomy`:** The record says the main intercostal bundle is "nerve, artery, vein (NAV superior-to-inferior)." The conventional main-bundle order is vein-artery-nerve (VAN) from superior to inferior; an [original cadaveric chest-drain anatomy study (2005)](https://pubmed.ncbi.nlm.nih.gov/15971216/) also demonstrates clinically important positional variation. The operational advice to pass above the rib is correct, but the anatomy teaching is wrong and must be corrected by a qualified reviewer.
- **MAJOR - `equipment`, `aftercare`, `documentation`:** Specimen handling is incomplete and partly erroneous. "Blood culture bottles ... (highest yield for SBP/empyema detection)" imports `SBP` (spontaneous bacterial peritonitis) into pleural sampling and implies broad use. BTS (2023) specifies plain plus blood-culture containers when pleural infection is suspected. The record lists pH but only says it "degrades quickly if not capped"; current BTS guidance requires immediate analysis and avoidance of lidocaine/heparin contamination because either can change the result and the drain decision.
- **MAJOR - `equipment`, `steps`, dosing/monitoring:** It specifies 1% lidocaine but no patient-specific maximum, cumulative-dose accounting, toxicity monitoring, or rescue readiness. BTS (2023) describes a conservative 3 mg/kg (maximum 250 mg) limit for pleural procedures while acknowledging practice variation; the 2025 DailyMed label gives 4.5 mg/kg without epinephrine (generally no more than 300 mg) and requires monitoring/readiness. No structured `dosing` block is present, and the current category-based validator does not require one.
- **MINOR - `shiftMode`, `steps`, `confirmation`, `aftercare`, `documentation`:** Routine post-procedure ultrasound or CXR is repeatedly required for every patient. SHM (2018) recommends no routine CXR after an uncomplicated ultrasound-guided procedure when the patient is asymptomatic and normal lung sliding is present. Imaging remains indicated for symptoms, air aspiration, multiple attempts, uncertain findings, or local high-risk circumstances. The clinician should define selective rather than universal CXR criteria while retaining immediate ultrasound reassessment.
- **MINOR - `complications`:** The numerical pneumothorax rates ("5-10% without ultrasound; <1-3% with") have no cited study, population, or date and should not be retained as precise bedside risk estimates without a qualified source review.
- **MAJOR - `references`:** The section cites the superseded 2010 BTS procedure guideline and vague "ACEP and SCCM" guidance without title, year, or locator. It does not support the vacuum drainage method, universal imaging, specimen handling, or dosing claims.

### Equipment, dosing, and remaining sections

The kit, catheter/stopcock/syringe, ultrasound, sterile barriers, local-anesthetic needles, occlusive dressing, measurement container, and indication-based laboratory tubes are reasonable categories after removing vacuum drainage and adding correct pH/microbiology containers. Same-position ultrasound, diaphragm/solid-organ identification, catheter use for therapeutic drainage, symptom monitoring, 1.5-L general ceiling, occlusive dressing, prompt specimen transport, and volume/character documentation align with reviewed standards. No additional material discrepancy was identified in indications, positioning, ultrasound targeting, confirmation, troubleshooting, senior pearls, or most complications. Anticoagulation interruption/correction, sedation, pregnancy, and very small/loculated pockets are individualized or local-policy decisions; the broad "active ipsilateral pneumothorax - decompress first" contraindication was not established from the sources reviewed and needs clinician confirmation rather than AI rewriting.

### Questions for the clinical reviewer

1. Remove vacuum-bottle/wall-suction therapeutic aspiration and define the approved manual/gravity setup and symptom stop rule.
2. Correct intercostal bundle anatomy and approve the final landmark visual.
3. Specify indication-based specimen containers and immediate pH handling, including avoidance of lidocaine/heparin contamination; remove the `SBP` wording.
4. Select the local-anesthetic ceiling/monitoring pathway and selective post-procedure imaging criteria.
5. Replace the reference list with current named primary guidance and adjudicate the unsupported complication-rate numbers and ipsilateral-pneumothorax contraindication.

**Proposed clinician disposition:** Keep out of release pending correction and qualified pulmonary/critical-care review. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## Changed File and Sources / Limitations

**Changed file:** `docs/audits/procedure-verification/03_THORACIC.md` only. No JSON, Swift, validator, dosing structure, visual metadata, or reviewer status was modified.

Primary/authoritative sources reviewed:

- British Thoracic Society, [Clinical Statement on pleural procedures](https://thorax.bmj.com/content/78/Suppl_3/s43), 2023.
- British Thoracic Society, [Guideline for pleural disease](https://thorax.bmj.com/content/78/11/1143), 2023.
- British Thoracic Society, [Quality Standard for Pleural Disease](https://www.brit-thoracic.org.uk/clinical-resources/quality-standards/pleural-disease/), 2026.
- World Society of Emergency Surgery/American Association for the Surgery of Trauma, [Thoracic trauma WSES-AAST guidelines](https://link.springer.com/article/10.1186/s13017-025-00651-1), 2025.
- Western Trauma Association, [Evaluation and management of traumatic pneumothorax: critical decisions algorithm](https://www.westerntrauma.org/wp-content/uploads/2024/02/32-Evaluation-and-management-of-traumatic-pneumothorax_-A-Western-Trauma-Association-critical-decisions-algorithm.pdf), 2022.
- Eastern Association for the Surgery of Trauma, [Antibiotic prophylaxis for tube thoracostomy placement in trauma](https://www.east.org/education-resources/practice-management-guidelines/details/antibiotic-prophylaxis-for-tube-thoracostomy-placement-in-trauma-a-practice-management-guideline-from-the-eastern-association-for-the-surgery-of-trauma), 2022.
- Eastern Association for the Surgery of Trauma, [Management of simple and retained hemothorax](https://pubmed.ncbi.nlm.nih.gov/33487403/), 2021 (2020 guideline work; EAST notes an update is in progress).
- Joint Trauma System, [Wartime Thoracic Injury CPG, ID 74](https://jts.health.mil/assets/docs/cpgs/Wartime_Thoracic_Injury_26_Dec_2018_ID74.pdf), 2018.
- Society of Hospital Medicine, [Recommendations on ultrasound guidance for adult thoracentesis](https://cdn.mdedge.com/files/s3fs-public/Document/January-2018/jhm013020126.pdf), 2018.
- Cook Medical, [Fuhrman Pleural Drainage Set Instructions for Use](https://ifu.cookmedical.com/data/IFU_PDF/C_T_PPD-M_REV0.PDF), current IFU accessed 2026; the retrieved document did not expose a clear publication year, so kit-specific revision control must be checked locally.
- Fresenius Kabi/FDA DailyMed, [Lidocaine Hydrochloride Injection prescribing information](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=cddb2b22-fce3-8967-6e54-dca3df5ac4b3), revised 2025.
- Wraight, Tweedie, and Parkin, [Neurovascular anatomy and variation in the fourth, fifth, and sixth intercostal spaces: cadaveric study](https://pubmed.ncbi.nlm.nih.gov/15971216/), 2005.

Limitations: This was an adult-focused, source-comparison screen of the fingerprinted working-tree JSON, not observation of local practice or validation of any physical kit. Several trauma recommendations are conditional or consensus-based, and the JTS CPG is operational/military guidance; local ED/ICU/trauma capabilities may appropriately differ. Exact pediatric, pregnancy, anticoagulant, sedation, antibiotic-agent, local-anesthetic, drainage-device, and escalation protocols require institution-specific review. Structural validation cannot establish clinical correctness, no visual artwork was available to inspect, and no licensed clinician approved these findings.
