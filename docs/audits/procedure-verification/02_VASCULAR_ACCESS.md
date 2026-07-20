# Vascular Access Procedure Verification

## Audit boundary

- Assigned IDs only: `central_venous_catheter`, `arterial_line`, `introducer_sheath_cordis`, `dialysis_catheter_vascath`, `intraosseous_access`, and `ultrasound_guided_piv`.
- Snapshot checked before review: `Procedures/Resources/procedures.json` SHA-256 `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1` (match).
- This is an AI-assisted discrepancy screen, not clinical approval. Dispositions identify content requiring qualified clinician decisions.
- Every named section, equipment/instruments, visual-asset declaration, and structured-dosing field was screened. None of the six objects contains a structured-dosing field.
- Independent release gate: every assigned procedure declares one or more `visualAssets` with `assetName: null`. Per `docs/ai-instructions/SAFETY_AND_REVIEW_POLICY.md`, placeholders are stop-ship for release even where the clinical screening disposition below is `MAJOR`.

## `central_venous_catheter` - Central Venous Catheter

**Screening disposition: `STOP-SHIP`**

**Source-standard summary.** ASA requires confirmation that the needle/catheter is venous without relying on blood color or nonpulsatile flow, and requires venous guidewire confirmation after a thin-wall-needle technique before dilation. If a dilator or large-bore catheter enters an adult artery, it should remain in place while surgical or interventional removal is arranged. Current CDC guidance supports real-time ultrasound, maximal sterile barrier, alcoholic chlorhexidine greater than 0.5% (or an alternative when contraindicated), and prompt removal when no longer needed.

**Findings.**

- `STOP-SHIP` - `sections.steps`, `sections.shiftMode`, and `sections.ultrasound`: the sequence says to "confirm venous blood return" and makes wire imaging conditional ("when possible" / "when feasible") before dilation. For the described thin-wall-needle Seldinger technique, this does not reliably require an ASA-accepted venous confirmation method and can permit dilation after blood-return assessment alone.
- `STOP-SHIP` - `sections.troubleshooting` and `sections.complications`: "manage as arterial puncture/cannulation based on catheter size and site" does not state the immediate adult rescue action for an artery containing the dilator or large-bore catheter: leave it in place and urgently involve vascular/general surgery or interventional radiology. Pull-and-pressure after large-bore neck/chest arterial cannulation can cause stroke, hemothorax, fistula, or uncontrolled hemorrhage.
- `MAJOR` - `sections.references`: the entries are nonspecific textbook/guidance descriptions without authors/edition, guideline title, year, or URL; they cannot be traced to the claims above.

**Equipment/instruments.** The kit sequence is broadly recognizable, including needle, wire, scalpel, dilator, catheter, flushes, securement, sterile probe cover/gel, and confirmation workflow. It does not require a pressure-transduction/manometry option or another unambiguous venous-confirmation method before dilation. "Chlorhexidine prep" also omits the CDC concentration/alcohol qualification and alternative for contraindication. Device size/lumen choice is acknowledged but not operationalized.

**Dosing/monitoring.** No structured dosing is present. Local anesthetic is named without concentration, amount, patient-specific maximum, toxicity precautions, or monitoring; the current FDA label for plain lidocaine gives a normal-healthy-adult ceiling of 4.5 mg/kg and generally 300 mg, but a clinician must decide whether and how procedural local-anesthetic dosing belongs here. Post-placement monitoring names major complications but does not provide explicit immediate reassessment triggers beyond instability.

**Reviewer questions and proposed disposition.** Must venous access and wire position be confirmed with an accepted method before dilation in every non-exempt scenario, with the emergency exception defined? Should the arterial-cannulation rescue state the adult leave-in-place/urgent-consult action and distinguish small-needle puncture from dilator/large catheter injury? Proposed disposition remains `STOP-SHIP` until those decisions are made by a qualified clinician. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [American Society of Anesthesiologists, *Practice Guidelines for Central Venous Access 2020* (2020)](https://journals.lww.com/anesthesiology/fulltext/2020/01000/practice_guidelines_for_central_venous_access.9.aspx); [Association of Anaesthetists, *Safe Vascular Access 2025* (2025)](https://associationofanaesthetists-publications.onlinelibrary.wiley.com/doi/full/10.1111/anae.16727); [CDC, *Guidelines for Prevention of Intravascular Catheter-Related Infections* summary (2011 guideline; page updated 2024)](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infections/summary-recommendations.html); [DailyMed/FDA label, Lidocaine Hydrochloride Injection (current label accessed 2026)](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=cddb2b22-fce3-8967-6e54-dca3df5ac4b3).

**Remaining sections reviewed.** Indications, contraindications/coagulopathy, anatomy, positioning, confirmation, aftercare, documentation, senior pearls, and complications beyond the findings above had no additional material discrepancy identified against the sources reviewed. Pregnancy, pediatric use, sedation, and institution-specific coagulation thresholds remain outside this adult-oriented text and require local policy/clinician review if intended.

## `arterial_line` - Arterial Line

**Screening disposition: `MAJOR`**

**Source-standard summary.** CDC recommends at least cap, mask, sterile gloves, and a small sterile fenestrated drape for peripheral arterial catheter insertion; maximal barriers for femoral/axillary sites; alcoholic chlorhexidine greater than 0.5%; a sterile closed pressure-monitoring system; clinically indicated rather than routine catheter replacement; and prompt removal when no longer required. Accurate invasive pressure use also requires leveling/zeroing and assessment for over- or underdamping, commonly by a fast-flush dynamic-response test.

**Findings.**

- `MAJOR` - `sections.equipment` and `sections.steps`: the list includes sterile gloves/drape but omits cap and mask, and the steps do not distinguish maximal barrier requirements for femoral access. This is incomplete against CDC arterial-catheter insertion precautions.
- `MAJOR` - `sections.confirmation`, `sections.troubleshooting`, and `sections.aftercare`: "arterial waveform ... is definitive confirmation" confirms arterial residence, but the content then permits clinical reliance after zeroing without a dynamic-response/fast-flush assessment. Over- or underdamping can materially distort systolic/diastolic pressure and influence vasopressor decisions. Troubleshooting covers only a dampened waveform, not underdamping/resonance.
- `MINOR` - `sections.complications`: "Infection, especially after 72-96 hours" is not a current replacement rule and may imply a time-based resite. CDC says replace an arterial catheter only for a clinical indication and not routinely for infection prevention.
- `MAJOR` - `sections.references`: the textbook citation lacks edition/year, and the claimed SCCM/ACEP guidelines are not identified by title, year, or URL.

**Equipment/instruments.** The catheter, transducer, saline flush bag pressurized to 300 mmHg, monitor, ultrasound, local anesthetic, and securement are present. Additions requiring clinician decision are the missing cap/mask, site-dependent barrier level, a closed sterile flush-system requirement, and equipment/workflow for dynamic-response assessment. "All ports flush" is inaccurate terminology for a typical single-lumen arterial catheter.

**Dosing/monitoring.** No structured dosing is present. The only drug detail is 1% lidocaine without dose/maximum or toxicity monitoring. Continuous pressure monitoring is central to this procedure, but the quality-control sequence is incomplete as above. Distal perfusion checks are appropriately included.

**Reviewer questions and proposed disposition.** Should the procedure explicitly require CDC barrier elements and maximal barriers for femoral/axillary placement? What dynamic-response validation and repeat-check cadence should be required before titrating treatment to the displayed pressure? Should the 72-96-hour phrase be removed or replaced with clinically indicated removal language? Proposed disposition is `MAJOR` pending clinician revision. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [CDC, intravascular-catheter recommendations, sections on arterial catheters and pressure systems (2011 guideline; page updated 2024)](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infections/summary-recommendations.html); [Saugel et al., *How to Measure Blood Pressure Using an Arterial Catheter: A Systematic 5-Step Approach* (2020)](https://pubmed.ncbi.nlm.nih.gov/32331527/); [Romagnoli et al., original observational study of invasive-pressure monitoring accuracy (2014)](https://pubmed.ncbi.nlm.nih.gov/25433536/).

**Remaining sections reviewed.** Shift mode, indications, contraindications/anticoagulation, anatomy, positioning, ordered insertion steps, ultrasound, complications, documentation, and senior pearls had no additional material discrepancy identified. Site choice and collateral-flow testing are practice-variable and need local clinician policy rather than a universal threshold.

## `introducer_sheath_cordis` - Introducer Sheath (Cordis)

**Screening disposition: `STOP-SHIP`**

**Source-standard summary.** Large introducers magnify the consequences of arterial injury. ASA and the 2025 multi-society vascular-access guideline require an adult dilator/large catheter inadvertently placed in an artery to be left in place while urgent surgical/interventional removal is planned. Device selection, French size, wire compatibility, sheath/hemostasis-valve design, and insertion/removal sequence must follow the exact manufacturer IFU.

**Findings.**

- `STOP-SHIP` - `sections.troubleshooting` and `sections.complications`: the text calls 8.5 Fr arterial dilation a surgical emergency but gives no immediate action once dilation/sheath placement has occurred. The required adult rescue decision is not "remove and compress"; the device should remain in place while vascular/general surgery or interventional radiology is contacted urgently.
- `MAJOR` - `sections.steps` and `sections.equipment`: "dilator and sheath advance together" and "remove the dilator and wire together" are presented as universal despite the object naming a generic introducer/Cordis kit. Introducer designs, valves, companion catheters, French sizes, lengths, and wire compatibility vary. The text must either bind to a reviewed product/IFU or explicitly defer device-specific assembly and sequence to the selected IFU.
- `MAJOR` - `sections.steps`: as in the CVC object, venous blood return plus wire ultrasound "when feasible" is weaker than the required high-confidence pre-dilation confirmation for this 8.5 Fr tract.
- `MAJOR` - `sections.references`: no cited source is uniquely identifiable or directly supports the device sequence.

**Equipment/instruments.** The generic list covers the major components, but no exact sheath size/length, guidewire diameter, hemostasis-valve/side-arm configuration, compatibility with a pacing or PA catheter, or exact IFU is specified. Teleflex's current Arrow PSI family alone includes 8.5 and 9 Fr 10 cm kits with a hemostasis valve and side arm; that illustrates why the selected product and IFU must govern rather than a universalized sequence.

**Dosing/monitoring.** No structured dosing is present. Local anesthetic lacks concentration/dose/maximum. Monitoring for bleeding, air embolism, arrhythmia, and pneumothorax is named, but no explicit continuous occlusion/hemostasis-valve check is given while the central lumen is not occupied by another catheter.

**Reviewer questions and proposed disposition.** Which introducer product(s), sizes, and IFUs is this object intended to cover? What exact rescue wording is required after an artery has been dilated or cannulated? What accepted venous/wire confirmation is mandatory before the large dilator advances? Proposed disposition remains `STOP-SHIP` until a qualified clinician resolves these points. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [American Society of Anesthesiologists, *Practice Guidelines for Central Venous Access 2020* (2020)](https://journals.lww.com/anesthesiology/fulltext/2020/01000/practice_guidelines_for_central_venous_access.9.aspx); [Association of Anaesthetists, *Safe Vascular Access 2025* (2025)](https://associationofanaesthetists-publications.onlinelibrary.wiley.com/doi/full/10.1111/anae.16727); [Teleflex, Arrowg+ard Blue Percutaneous Sheath Introducer product/IFU reference (current page accessed 2026)](https://www.teleflex.com/usa/en/product-areas/vascular-access/central-access/percutaneous-sheath-introducer/index.html); [CDC, intravascular-catheter recommendations (2011 guideline; page updated 2024)](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infections/summary-recommendations.html).

**Remaining sections reviewed.** Shift mode, indications, contraindications/coagulopathy, anatomy, positioning, ultrasound, confirmation, aftercare, documentation, and senior pearls had no additional material discrepancy identified beyond the confirmation/rescue/IFU issues above. Pacing and PA-catheter use require separate device-specific monitoring and are not fully taught here.

## `dialysis_catheter_vascath` - Dialysis Catheter (Vas-Cath)

**Screening disposition: `STOP-SHIP`**

**Source-standard summary.** KDIGO recommends a nontunneled uncuffed catheter for acute RRT, site order of right IJ, femoral, left IJ, then subclavian, ultrasound guidance, and chest radiograph before first use of IJ/subclavian acute dialysis catheters. Catheter length and tip location are site-specific: KDIGO describes 12-15 cm right IJ, 15-20 cm left IJ, and 19-24 cm femoral lengths, with a semirigid nontunneled IJ tip at the SVC-right atrial junction rather than in the heart. Large-bore arterial cannulation requires the same leave-in-place urgent-consult rescue as other central dilators/catheters.

**Findings.**

- `STOP-SHIP` - `sections.troubleshooting` and `sections.complications`: "arterial cannulation ... (surgical emergency)" lacks the immediate adult action after a dilator or large dialysis catheter has entered an artery. Leaving the device in place and urgent specialist consultation must be decided and stated.
- `MAJOR` - `sections.equipment`, `sections.anatomy`, and `sections.steps`: the object does not identify catheter French size or site-specific length. "Advance ... to the planned depth" is not enough for a device where inadequate length can leave a femoral tip outside a large central vein and impair flow/raise recirculation, while excessive depth of a semirigid IJ catheter can enter the heart.
- `MAJOR` - `sections.steps`: venous blood return and wire confirmation "when feasible" are too weak before serial dilation for a 12-14 Fr-class catheter.
- `MAJOR` - `sections.references`: KDOQI is named without the guideline year/link; the other entries are nonspecific and do not support the stated insertion details.

**Equipment/instruments.** Major components and serial dilators are present, but size/length selection by site, product-specific priming volumes, caps/connectors, and the exact IFU are absent. The current Teleflex acute dialysis range, for example, spans 12 and 14 Fr and 13-25 cm, confirming that "dual-lumen catheter" is not a sufficient instrument specification.

**Dosing/monitoring.** No structured dosing is present. "Heparin or citrate ... per local protocol" and "prescribed catheter lock volume" appropriately defer a product- and patient-specific order, but the content should require the exact labeled lumen priming volume, lock agent/concentration, contraindications (including HIT for heparin), and aspiration/disposal behavior required by that product/policy. This is a clinician/pharmacy decision; a universal replacement dose should not be inferred. Dialysis flow/recirculation monitoring after connection is not described.

**Reviewer questions and proposed disposition.** Which acute dialysis catheter sizes/lengths and IFUs are supported for each site? Should the KDIGO length/tip distinctions be encoded or should the procedure require product/site selection through a reviewed table? What immediate large-bore arterial rescue wording and lock-solution safeguards are required? Proposed disposition remains `STOP-SHIP`. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [KDIGO, *Clinical Practice Guideline for Acute Kidney Injury*, vascular access for RRT (2012, recommendations 5.4.1-5.4.4)](https://kdigo.org/wp-content/uploads/2019/01/KDIGO-2012-AKI-Guideline-English.pdf); [National Kidney Foundation, KDOQI *Vascular Access Guideline* (2019)](https://www.kidney.org/professionals/kdoqi/guidelines-and-commentaries/vascular-access); [American Society of Anesthesiologists, *Practice Guidelines for Central Venous Access 2020* (2020)](https://journals.lww.com/anesthesiology/fulltext/2020/01000/practice_guidelines_for_central_venous_access.9.aspx); [Teleflex, Arrow acute hemodialysis catheter specifications/IFU reference (current page accessed 2026)](https://www.teleflex.com/usa/en/product-areas/vascular-access/central-access/acute-hemodialysis-catheters/); [FDA, DefenCath prescribing information illustrating lock-volume/aspiration requirements (2023)](https://www.fda.gov/media/179230/download).

**Remaining sections reviewed.** Shift mode, indications, contraindications, positioning, ultrasound, confirmation imaging, complications, aftercare, documentation, and senior pearls had no additional material discrepancy identified. The right-IJ preference, avoidance of subclavian when possible, and pre-use radiograph for IJ/subclavian acute catheters align with KDIGO. Pregnancy, pediatrics, and long-term/tunneled dialysis access are not covered.

## `intraosseous_access` - Intraosseous (IO) Access

**Screening disposition: `STOP-SHIP`**

**Source-standard summary.** The current Teleflex EZ-IO materials distinguish adults from infants/children: typical initial 2% preservative-free, epinephrine-free lidocaine is 40 mg in adults but 0.5 mg/kg in infants/children (maximum 40 mg), infused over 120 seconds, followed by a 60-second dwell and then saline flush; flush is 5-10 mL adult and 2-5 mL infant/child. Needle length must be selected by weight, anatomy, tissue depth, and visibility of the 5 mm mark. The proximal humerus uses a device-specific 45-degree-to-anterior-plane/posteromedial trajectory, while tibial sites use 90 degrees to bone. AHA 2025 recommends adult IV first in cardiac arrest, with IO reasonable when IV attempts fail or are not feasible.

**Findings.**

- `STOP-SHIP` - `sections.shiftMode` and `sections.steps`: the procedure is tagged/set for `Peds` but gives a universal "20-40 mg lidocaine 2%" dose. A 20-40 mg fixed dose can greatly exceed the manufacturer-supported pediatric 0.5 mg/kg initial dose. It also omits the 120-second infusion, contraindication/precaution check, and subsequent-dose distinction.
- `STOP-SHIP` - `sections.steps`: the sequence flushes every patient with 10 mL before lidocaine, then says to give lidocaine before flushing. The manufacturer sequence for a pain-responsive patient is lidocaine first, dwell, then age-specific flush; infants/children receive 2-5 mL, not a universal 10 mL.
- `MAJOR` - `sections.steps`, `sections.anatomy`, and both visual assets: a universal 90-degree-to-bone instruction is applied to the humerus. Current EZ-IO instructions distinguish proximal humerus (45 degrees to the anterior plane, posteromedial) from tibia/femur (90 degrees to bone).
- `MAJOR` - `sections.equipment`: "appropriate needle size" gives no usable selection rule. The current device requires weight/anatomy/tissue-depth selection and visibility of the 5 mm mark before drilling; the content omits both.
- `MAJOR` - `sections.contraindications`: "same bone within 24-48 hours" is ambiguous. Current EZ-IO labeling states attempted or established IO access in the target bone within the past 48 hours is contraindicated and also includes excessive tissue/absent landmarks, which are missing.
- `MAJOR` - `sections.references`: no current AHA guideline year/link or device IFU is identified.

**Equipment/instruments.** The driver, needle, extension, pressure setup, stabilizer, and sharps container are present. Needle lengths/weight ranges, the 5 mm skin-to-hub adequacy check, and priming-volume implications for small pediatric lidocaine doses are missing.

**Dosing/monitoring.** No structured dosing object exists despite explicit lidocaine instructions. The free-text fixed pediatric dose, flush volume, timing, repeat-dose plan, contraindications, and toxicity monitoring are materially incomplete. Placement/extravasation monitoring is otherwise present, but the text should also require patency/site-and-limb reassessment before every infusion as the manufacturer does.

**Reviewer questions and proposed disposition.** A qualified clinician/pharmacist must choose whether to encode product-specific age/weight dosing and monitoring or remove the drug recipe in favor of a verified institutional order set. Which IO device(s) are supported, and should site-specific trajectories and needle-selection rules be tied to each IFU? Proposed disposition remains `STOP-SHIP` until pediatric dosing/sequence is corrected and independently reviewed. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [Teleflex, Arrow EZ-IO Procedure Competency Template (2021)](https://www.teleflex.com/usa/en/clinical-resources/ez-io/documents/EM_IOS_EZIO%20Procedure-Competency-Template_MC-000270_rev2c.pdf); [Teleflex, current Arrow EZ-IO procedure template, document MCI-2019-0395 (accessed 2026)](https://www.teleflex.com/global/clinical-resources/documents/MCI-2019-0395_Arrow_EZ-IO_Intraosseous_Procedure_Template_LR.pdf); [Teleflex, current EZ-IO indication/contraindication page, Rev 1 dated March 2026](https://go.teleflex.com/EZUI-Procedure-Tray-Data-Sheet.html); [American Heart Association, *2025 Guidelines: Adult Advanced Life Support*, vascular access section (2025)](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-advanced-life-support).

**Remaining sections reviewed.** Indications, positioning, empty ultrasound section, confirmation, troubleshooting, complications, aftercare, documentation, and senior pearls had no additional material discrepancy identified beyond the device/dose issues above. The 24-hour removal instruction is conservative relative to current labeling, which allows up to 48 hours in selected patients age 12 or older when alternate access is not established.

## `ultrasound_guided_piv` - Ultrasound-Guided Peripheral IV

**Screening disposition: `MAJOR`**

**Source-standard summary.** The 2019 Society of Hospital Medicine statement supports ultrasound for difficult peripheral access, real-time needle-tip visualization, vessel/nerve identification, and catheter length appropriate to depth. The 2025 multi-society vascular-access guideline recommends long peripheral or midline devices when ultrasound is required and at least one-third of the catheter intraluminal. CDC's 2025 safety alert requires single-use gel explicitly labeled sterile for central and peripheral IV placement. Contrast injection additionally depends on catheter verification, securement, location/gauge/flow, and device/radiology policy.

**Findings.**

- `MAJOR` - `sections.equipment`: "sterile or single-use probe cover and gel per local policy" can be read to allow single-use but nonsterile gel. CDC specifically requires single-use gel labeled sterile for percutaneous procedures, including peripheral IV placement; "single use" or "bacteriostatic" is not equivalent to sterile.
- `MAJOR` - `sections.indications`, `sections.equipment`, and `sections.confirmation`: contrast administration is listed as an indication without requiring a catheter/device, gauge, site, and flow rate approved by radiology/manufacturer policy. The ACR requires meticulous IV confirmation and device-specific power-injection limits; an easily flushing long PIV is not by itself authorization for power injection.
- `MAJOR` - `sections.shiftMode`, `sections.anatomy`, and `sections.steps`: the fixed combination "0.3-1.5 cm deep," "4.8 cm or longer," and only one-third intraluminal is too permissive at the deepest target. Evidence associates more than 2.75 cm intravascular length with better survival and depth over 1.2 cm with higher failure; device length must be selected from measured trajectory/depth and required intravascular length, with escalation to an ultralong PIV or midline when needed.
- `MAJOR` - `sections.references`: the ACEP/society references are not identified by title, year, or URL, and no infection-control or catheter-length source is supplied.

**Equipment/instruments.** The linear probe, long catheter, antiseptic, extension, flush, and securement are present. The sterile gel requirement is incorrect/ambiguous, and catheter gauge/length selection is not linked to measured depth, intended therapy, dwell, or power-injection rating. "Sterile or single-use probe cover" also needs clinician/infection-prevention review because the sterile field/cover standard depends on insertion technique and local aseptic protocol.

**Dosing/monitoring.** No structured dosing is present and no medication dose is instructed. Monitoring appropriately mentions infiltration, arterial puncture, nerve symptoms, and repeated site checks, but contrast-specific extravasation response and vesicant/irritant compatibility remain outside the procedure and must be governed by a reviewed institutional policy.

**Reviewer questions and proposed disposition.** Should the gel language be changed to the CDC's exact sterile single-use requirement? What measured-depth/intravascular-length rule and escalation threshold should replace the fixed 4.8 cm minimum? Should contrast be removed as a generic indication or explicitly conditioned on catheter and radiology/manufacturer authorization? Proposed disposition is `MAJOR`. `reviewerStatus` remains unchanged.

**Primary/authoritative sources:** [CDC, *Use Only Sterile Ultrasound Gel for Percutaneous Procedures* (2025)](https://www.cdc.gov/healthcare-associated-infections/bulletins/outbreak-ultrasound-gel.html); [Society of Hospital Medicine, *Recommendations on Ultrasound Guidance for Central and Peripheral Vascular Access in Adults* (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10193861/); [Association of Anaesthetists, *Safe Vascular Access 2025* (2025)](https://associationofanaesthetists-publications.onlinelibrary.wiley.com/doi/full/10.1111/anae.16727); [Pandurangadu et al., original catheter-survival study (2018)](https://pubmed.ncbi.nlm.nih.gov/30021833/); [Fields et al., predictors of ultrasound-guided PIV failure (2022)](https://pubmed.ncbi.nlm.nih.gov/36113061/); [American College of Radiology, *Manual on Contrast Media* (2024 edition with 2025 chapter updates)](https://cs.acr.org/-/media/ACR/Files/Clinical-Resources/Contrast_Media.pdf).

**Remaining sections reviewed.** Shift mode, contraindications, positioning, ultrasound technique, troubleshooting, complications, aftercare, documentation, and senior pearls had no additional material discrepancy identified beyond the sterility, device-selection, and contrast-policy findings. Pediatric, pregnancy, vesicant, and prolonged-dwell use are not supported by this adult ED/ICU object and require separate policy.

## Changed file and sources/limitations

- Changed file: `docs/audits/procedure-verification/02_VASCULAR_ACCESS.md` only.
- Sources were limited to specialty/multi-society guidance, government guidance, manufacturer materials/IFU-linked resources, FDA labeling, and original peer-reviewed studies. Secondary summaries were not used as sole support for any finding.
- Limitations: I am not a licensed reviewer and did not approve any content. I did not verify institution-specific kits, formularies, catheter brands, power-injection policies, coagulation thresholds, sedation practice, or local rescue pathways. Some device materials are manufacturer educational templates that explicitly defer medication decisions to the prescriber and institutional policy. Structural validity does not establish clinical correctness.
- `reviewerStatus` was not changed for any procedure. No JSON, Swift, validator, or other repository file was modified.
