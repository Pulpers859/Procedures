# Procedure Verification Lane 08: Regional Lower Extremity

## Audit boundary

- AI-assisted discrepancy screen only. I am not a licensed clinical reviewer, and this report does not approve content.
- Assigned records: `fascia_iliaca_block`, `block_femoral_nerve`, `block_peng`, `block_saphenous_nerve`, `block_popliteal_sciatic`, `block_transgluteal_sciatic`, `block_tibial_nerve`, and `block_sural_nerve`.
- Before review, `Procedures/Resources/procedures.json` SHA-256 was confirmed as `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`.
- I screened all metadata, every section, equipment/instruments, visual-asset metadata where present, and every structured dosing field. Unmentioned fields had no additional material discrepancy in the sources reviewed.
- The generic reference string `Standard emergency medicine regional anesthesia literature` and edition-free references are not traceable support for technique, volume, safety, or dosing claims. NYSORA is secondary and was not used as sole support for a substantive finding.
- **MINOR metadata:** all assigned records except `fascia_iliaca_block` use `reviewTime: "standard"`, which is outside the values listed in `PROCEDURE_SCHEMA.md`; the same seven records use the nonidentifying `icon: "lungs"`. These should be reconciled with the schema/UI owner without changing clinical disposition.

## Cross-cutting source standards

- ASRA's infection-control guideline calls for chlorhexidine-alcohol skin preparation, sterile gloves, and single-use sterile gel and probe cover for ultrasound-guided regional anesthesia. [ASRA, *Consensus Practice Infection Control Guidelines*, 2025](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651)
- The bupivacaine label requires immediate oxygen, resuscitation equipment/drugs and capable personnel; IV access for major lower-extremity blocks; incremental injection; and careful cardiovascular, respiratory, and consciousness monitoring. It gives an adult plain peripheral-nerve-block ceiling of 175 mg but does not establish the JSON's universal 2 mg/kg rule. [FDA/DailyMed, *Bupivacaine Hydrochloride Injection Prescribing Information*, revised 2024](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=bcaab86f-20f0-4482-8d73-e29b36dced58)
- The plain-lidocaine label supports 4.5 mg/kg and generally 300 mg only for normal healthy adults, requires the lower effective dose, and directs reduction in children, older/debilitated patients, and cardiac or hepatic disease. [FDA/DailyMed, *Lidocaine Hydrochloride Injection Prescribing Information*, revised 2025](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=cddb2b22-fce3-8967-6e54-dca3df5ac4b3)
- The ropivacaine label uses procedure-specific adult ranges and patient/site adjustment; it does not establish a universal 3 mg/kg/200 mg rule. Its table permits 5-200 mg for minor nerve block/infiltration and higher ranges for selected major blocks. [FDA/DailyMed, *Ropivacaine Hydrochloride Injection Prescribing Information*, revised 2026](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?audience=professional&setid=3763b7b6-da49-4658-b93d-28f5da24d09e)
- ASRA says local-anesthetic toxicity is additive, recommends observation for at least 30 minutes after a potentially toxic dose, and supplies a 20% lipid-emulsion rescue checklist. The JSON warning that different local anesthetics "share one maximum" does not define a mixed-agent additive-dose calculation. [ASRA, *Third Practice Advisory on LAST*, 2018](https://rapm.bmj.com/content/rapm/43/2/113.full.pdf) and [ASRA, *LAST Checklist*, 2020](https://asra.com/docs/default-source/guidelines-articles/local-anesthetic-systemic-toxicity-rgb.pdf?sfvrsn=33b348e_2)
- ASRA applies neuraxial timing to deep plexus/deep peripheral blocks; other peripheral sites require assessment of compressibility, vascularity, and consequences of bleeding. [ASRA, *Regional Anesthesia in the Patient Receiving Antithrombotic or Thrombolytic Therapy*, fifth edition, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766)
- ASRA's neurologic-complications advisory addresses ultrasound, injection-pressure monitoring, preexisting neurologic disease, and avoidance of mechanical/injection injury; no single monitor eliminates nerve injury. [ASRA, *Second Practice Advisory on Neurologic Complications*, 2015](https://rapm.bmj.com/content/40/5/401)
- For lower-leg trauma at risk of acute compartment syndrome (ACS), the Association of Anaesthetists advises multidisciplinary protocols, avoidance of dense long-duration blocks that outlast surgery, and scheduled surveillance by trained staff with pressure measurement available. [Association of Anaesthetists, *Regional Analgesia for Lower Leg Trauma and the Risk of ACS*, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC9292897/)

## `fascia_iliaca_block` - Fascia Iliaca Compartment Block

**Screening disposition: STOP-SHIP**

**Source-standard summary.** AAOS strongly recommends multimodal analgesia incorporating a preoperative nerve block for older adults with hip fracture; its evidence base includes fascia iliaca and femoral blocks. Randomized ED evidence also supports fascia iliaca or femoral block for femoral-fracture analgesia. Cadaveric/radiologic work confirms that needle level and volume materially alter spread; 40 mL has been studied, but obturator and cranial spread are not guaranteed. [AAOS, *Management of Hip Fractures in Older Adults*, 2021](https://new.aaos.org/globalassets/quality-and-practice-resources/hip-fractures-in-the-elderly/hipfxcpg.pdf); [Rukerd et al., randomized ED trial, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10916633/); [Ten Hoope et al., radiological cadaver study, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10372149/)

**Findings.**

- Both `visualAssets` entries have `assetName: null` and captions that say reviewed artwork must replace the placeholder. Repo policy makes declared placeholder clinical assets stop-ship. The second asset's superficial-to-deep subtitle also places `sartorius/iliopsoas` before `fascia iliaca`, while its own target sentence says the plane is between fascia iliaca and iliacus; the exact layer diagram and wording require anatomical review before an asset is bundled.
- `dosing.workedExample` reports the 70 kg ropivacaine result as 210 mg even though `absoluteMaxMg` is 200 mg. It does not apply the record's own lower ceiling. The example dose of 100 mg is below both values, but the displayed maximum is internally contradictory.
- `sections.shiftMode`, `sections.complications`, and `sections.aftercare` do not state that femoral involvement may weaken quadriceps or require a post-block motor check, assisted-mobility/fall precaution, and handoff. This is especially material in the frail hip-fracture population highlighted by the record.
- `sections.contraindications` labels anticoagulation/coagulopathy only as a local-policy relative risk. A reviewer should classify this exact infrainguinal approach under the current ASRA compressibility/vascularity framework and define drug-specific action rather than leave bedside interpretation open.
- `sections.references` does not identify the technique variant or support the 40 mL concentration/volume, claimed nerve coverage, motor-risk plan, or dose ceilings.

**Equipment/instruments.** Probe choice, echogenic/short-bevel needle, extension tubing, hydrodissection saline, aspiration syringe, ECG/BP/pulse oximetry, lipid emulsion, and resuscitation equipment are substantially more complete than the other records. The list still lacks explicit sterile single-use gel, oxygen, and IV access. Needle length and concentration/volume need body-habitus and patient-risk qualification rather than an example-only description.

**Dosing/monitoring.** `40 mL x 2.5 mg/mL = 100 mg` is correct. The 3 mg/kg/200 mg ropivacaine rule is conservative relative to some labeled adult procedure ranges but is not established as a universal FDA rule; the bupivacaine 175 mg cap is labeled, while 2 mg/kg is not. The 30-minute monitoring statement aligns with ASRA for potentially toxic doses. The record appropriately calls for incremental 3-5 mL injection and cumulative accounting, but mixed-agent additivity, frail/elderly reduction, pediatric use, pregnancy, and hepatic/cardiac disease remain undefined.

**Reviewer question/proposed disposition.** Resolve or remove both declared visual placeholders; correct the ropivacaine lower-ceiling example; approve technique-specific volume/coverage, mobility precautions, anticoagulation handling, and patient-specific dose reduction. Keep `STOP-SHIP` until the visual release gate and dosing contradiction are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_femoral_nerve` - Femoral Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** AAOS supports preoperative nerve blocks for hip-fracture pain, and ED randomized trials show opioid reduction with ultrasound-guided femoral block. These sources support analgesia, not complete anesthesia of all structures of the femur or knee. Bupivacaine labeling also confirms that 0.25% can produce incomplete motor block and 0.5% produces motor blockade. [AAOS, *Management of Hip Fractures in Older Adults*, 2021](https://new.aaos.org/globalassets/quality-and-practice-resources/hip-fractures-in-the-elderly/hipfxcpg.pdf); [Gerlier et al., randomized ED trial, 2024](https://pubmed.ncbi.nlm.nih.gov/37650732/); [FDA/DailyMed, bupivacaine label, 2024](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=bcaab86f-20f0-4482-8d73-e29b36dced58)

**Findings.**

- `sections.shiftMode` says the block "provides anesthesia to the anterior thigh, femur, and knee." Femur and knee innervation is not exclusively femoral; the source evidence supports analgesia for selected injuries, not reliable complete anesthesia. Intended tissue/osseous coverage and supplemental rescue must be stated.
- `sections.indications` omits hip fracture despite stronger current evidence than some listed uses. Conversely, anterior-thigh laceration and patellar/knee-trauma use need a sensory map and a failed-coverage plan before a painful procedure.
- `sections.steps` directs a single 15-20 mL injection after one aspiration. It does not repeat the structured requirement for incremental injection/repeated aspiration or stop for pain, paresthesia, nerve swelling, high resistance/pressure, or loss of tip visualization. `sections.troubleshooting` addresses only identification and superficial spread.
- `sections.complications` lists only intravascular injection and nerve injury, omitting LAST, hematoma/bleeding, infection, and block failure. The strong `sections.aftercare` non-weight-bearing/fall warning is appropriate, but a documented post-block motor/neurovascular reassessment and handoff are not required.
- `sections.references` is not traceable support for indication, target, volume, or dosing.

**Equipment/instruments.** A linear probe and 21-22G 50-100 mm block needle are plausible, with length selected for depth. The list omits antiseptic, sterile gloves/drape, sterile cover/gel, extension tubing, aspiration/test-injection supplies, BP/ECG/pulse oximetry, IV access, oxygen/resuscitation equipment, and lipid rescue. These omissions are not cured by safety text living only in `dosing.monitoring`.

**Dosing/monitoring.** The worked arithmetic is correct: 20 mL of 0.25% bupivacaine is 50 mg; 2 mg/kg gives 140 mg at 70 kg and 100 mg at 50 kg, both below 175 mg. The 175 mg absolute cap is label-supported for an average adult peripheral block, but the 2 mg/kg rule requires an approved institutional/clinical source. The label requires dose individualization, IV access for major lower-extremity block, and continuous clinical monitoring; pediatric, pregnancy, frailty, hepatic/cardiac disease, and mixed-agent calculations are not operationalized.

**Reviewer question/proposed disposition.** Define analgesic versus anesthetic coverage and rescue, add injection stop rules and the complete major-block setup, and approve patient-specific dosing/antithrombotic policy. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_peng` - PENG (Pericapsular Nerve Group) Block

**Screening disposition: MAJOR**

**Source-standard summary.** The original PENG report described a 20 mL injection for hip-fracture analgesia in the plane deep to the iliopsoas tendon at the iliopubic eminence. A later sham-controlled trial supports early analgesia in selected elderly hip-fracture patients, but PENG remains a relatively new technique. It is not reliably motor-sparing: a randomized volume trial found quadriceps weakness at 6 hours in 5%, 20%, and 75% of 10, 20, and 30 mL groups, respectively. [Giron-Arango et al., original PENG description, 2018](https://pubmed.ncbi.nlm.nih.gov/30063657/); [Lin et al., randomized hip-fracture trial, 2023](https://rapm.bmj.com/content/48/11/535); [Wen et al., randomized volume trial, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11111422/)

**Findings.**

- `sections.shiftMode` calls PENG a "motor-sparing alternative," and `sections.seniorPearls` says it is "largely motor-sparing" while the record permits 20-30 mL. Current randomized evidence shows clinically important, volume-dependent quadriceps weakness, especially at 30 mL. `sections.aftercare` addresses only LAST and omits quadriceps assessment, assisted ambulation, and fall precautions.
- `sections.indications` includes acetabular pelvic fractures. The authoritative hip-fracture guideline and PENG trials reviewed here do not establish PENG as a reliable stand-alone block for the heterogeneous innervation and injury patterns of acetabular fracture. Evidence was insufficient in this screen; the reviewer must define the intended subset and rescue analgesia or remove the broad claim.
- `sections.contraindications` lists only site infection and allergy. It omits refusal/cooperation, preexisting neurologic deficit, and antithrombotic/bleeding assessment for a deep, nonreadily compressible target near femoral vessels.
- `sections.steps` supports the general IPE/deep-to-psoas-tendon target, but the 20-30 mL range is not reconciled with motor risk. It also lacks incremental injection, repeated aspiration, Doppler/vascular-path wording, and stop rules for pain, resistance, nerve swelling, or loss of tip visualization.
- `sections.complications`, `sections.documentation`, and `sections.references` omit motor block/fall, nerve injury, hematoma, infection, failed coverage, post-block motor/neurovascular findings, and traceable technique evidence.

**Equipment/instruments.** A depth-appropriate curvilinear or linear probe and 80-100 mm 21-22G block needle are plausible, with habitus-based qualification. The list omits sterile preparation and probe supplies, extension tubing/test-injection supplies, monitoring, IV access, oxygen/resuscitation equipment, and lipid emulsion. Femoral vessels should be mapped explicitly, and local credentialing should determine whether pressure monitoring or nerve stimulation is required.

**Dosing/monitoring.** The worked arithmetic is correct: 30 mL of 0.25% bupivacaine is 75 mg; 140 mg at 70 kg and 100 mg at 50 kg are below 175 mg. The 2 mg/kg ceiling is not established by the primary label, and a nominally dose-safe 30 mL volume still carries motor-risk implications. The generic monitoring fields include ECG/pulse oximetry and lipid readiness but omit BP, IV access, oxygen, patient-specific reduction, and a mixed-agent formula.

**Reviewer question/proposed disposition.** Replace the unqualified motor-sparing language, select a volume/concentration with explicit quadriceps/fall monitoring, define or remove acetabular-fracture use, and approve deep-block anticoagulation and safety setup. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_saphenous_nerve` - Saphenous Nerve (Adductor Canal) Block

**Screening disposition: MAJOR**

**Source-standard summary.** The saphenous nerve is sensory, and adductor-canal block generally preserves more quadriceps strength and balance than femoral block. That comparative advantage is not a guarantee of normal motor function or safe walking. A randomized volunteer trial studied 15 mL and found relative preservation, while low-volume anatomical/clinical work specifically evaluated vastus-medialis consequences and target level. [Kwofie et al., randomized blinded volunteer trial, 2013](https://pubmed.ncbi.nlm.nih.gov/23788068/); [Adoni et al., randomized target-level trial, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4152679/)

**Findings.**

- `sections.shiftMode` calls the technique purely sensory, and `sections.seniorPearls` says patients "can still walk." Although the named saphenous nerve is sensory, an adductor-canal injection can spread to motor branches or proximally. The record needs post-block quadriceps/ambulation assessment and fall precautions rather than permission to walk based on block name.
- `sections.indications` broadly lists medial lower-leg fractures. An isolated saphenous block covers medial cutaneous territory, not all osseous/deep pain from a lower-leg fracture. The record should distinguish cutaneous/procedural supplementation from complete fracture analgesia and define when a sciatic component is required.
- `sections.anatomy` uses "superficial femoral artery" while the steps use `femoral artery`; standardized vessel naming and the exact proximal/distal canal target should be selected. `sections.steps` also omit deliberate vein/Doppler mapping, incremental injection, repeated aspiration, and nerve-injury stop rules despite perivascular injection.
- `sections.complications` lists only intravascular injection. Motor weakness/fall, nerve injury, hematoma, infection, LAST, and block failure are absent; `sections.aftercare` only protects numb skin.
- `sections.references` does not support target level, volume, fracture coverage, motor claims, or dose ceilings.

**Equipment/instruments.** A linear probe, 21-22G 50-100 mm block needle, and 10-15 mL are plausible, with depth-based needle selection. The list omits skin antisepsis, sterile gloves/drape, sterile cover/gel, extension tubing/test-injection supplies, monitoring, IV access, oxygen/resuscitation equipment, and lipid rescue.

**Dosing/monitoring.** `15 mL x 10 mg/mL = 150 mg` is correct, but the example calls the 70 kg lidocaine maximum 315 mg even though the record and FDA label cap plain lidocaine at 300 mg; the lower ceiling is not applied. The 50 kg result is 225 mg. Lidocaine's 4.5 mg/kg/300 mg fields are label-supported only for normal healthy adults; bupivacaine's 175 mg cap is labeled but 2 mg/kg is not. The bupivacaine ceiling has no worked example. Mixed-agent additivity and patient-specific reduction remain undefined.

**Reviewer question/proposed disposition.** Remove the walking guarantee, add motor/fall assessment, define fracture coverage and target level, complete perivascular safety/setup, and correct the lidocaine lower-ceiling example. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_popliteal_sciatic` - Popliteal Sciatic Nerve Block

**Screening disposition: STOP-SHIP**

**Source-standard summary.** Randomized evidence distinguishes injection through the common **paraneural** sheath at the sciatic bifurcation from intraneural/intrafascicular injection and describes faster onset while preserving epineurium and intraneural structures. ASRA's neurologic advisory supports conservative responses to possible needle/injection injury. For trauma at ACS risk, current guidance favors a multidisciplinary surveillance protocol rather than an unsupported assumption that a block either always masks or never affects diagnosis. [Perlas et al., randomized paraneural-sheath trial, 2013](https://pubmed.ncbi.nlm.nih.gov/23558372/); [ASRA, neurologic-complications advisory, 2015](https://rapm.bmj.com/content/40/5/401); [Association of Anaesthetists, lower-leg trauma/ACS guideline, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC9292897/)

**Findings.**

- `sections.steps` directs the needle "within its epineural sheath (the 'Vloka sheath')." The supporting literature calls the target a common paraneural sheath and explicitly contrasts it with the epineurium/intraneural structures. This wording can be read as an instruction to enter the nerve and is a plausible nerve-injury hazard; it is STOP-SHIP until anatomically corrected by a qualified reviewer.
- `sections.troubleshooting` reinforces injection "inside the common paraneural sheath" but does not reconcile terminology or require absence of neural swelling. There are no stop rules for paresthesia, pain, high resistance/pressure, swelling, or uncertain tip position.
- `sections.contraindications` says a block can mask ischemic pain and only directs discussion with the surgical team. For tibial/lower-leg injury, current guidance requires a defined multidisciplinary protocol, appropriate low-density strategy where used, scheduled surveillance, breakthrough-pain escalation, and pressure measurement access.
- `sections.complications` lists only intravascular injection and nerve injury, omitting LAST, hematoma, infection, block failure, and delayed/persistent deficit. `sections.aftercare` appropriately mandates non-weight-bearing for foot drop but lacks scheduled neurovascular/ACS reassessment and limb protection.
- `sections.references` does not support sheath terminology, 20-30 mL, trauma use, or the ACS plan.

**Equipment/instruments.** The linear probe and 21-22G 50-100 mm needle are plausible. The list omits antiseptic/sterile supplies, extension tubing and test injection, Doppler qualification, monitoring, IV access, oxygen/resuscitation equipment, and lipid rescue. The popliteal artery and vein are close, and the needle path/vascular map should be explicit.

**Dosing/monitoring.** The worked bupivacaine calculation is correct: 30 mL of 0.25% is 75 mg, with 140 mg and 100 mg weight-based results below 175 mg. The 2 mg/kg bupivacaine and 3 mg/kg/200 mg ropivacaine rules are not universal label rules; no worked example tests the ropivacaine ceiling. A 20-30 mL choice must be reconciled with block density, motor duration, ACS surveillance, age/comorbidity, cumulative/mixed-agent exposure, and the lowest effective dose.

**Reviewer question/proposed disposition.** Replace the epineural instruction with a clinically approved, unambiguous target and sonographic confirmation/stop rules; add the full ACS surveillance pathway and safety setup. Keep `STOP-SHIP` until the needle-target wording is resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_transgluteal_sciatic` - Transgluteal / Proximal Sciatic Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** A proximal sciatic block covers sciatic motor/sensory territories, but posterior-thigh skin is supplied by the posterior femoral cutaneous nerve and may require a separate block for complete above-knee cutaneous anesthesia. The transgluteal sciatic target is deep and near noncompressible structures, so current antithrombotic guidance is materially different from a superficial ankle block. [Shabani et al., posterior femoral cutaneous nerve technique/anatomy, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11064292/); [ASRA, antithrombotic guideline, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766)

**Findings.**

- `sections.shiftMode` says the sciatic block provides anesthesia to the posterior thigh, and `sections.indications` lists posterior-thigh lacerations. That cutaneous territory is not reliably supplied by the sciatic nerve. This can produce failed/incomplete anesthesia for wound care unless posterior femoral cutaneous coverage is assessed and supplemented.
- `sections.indications` also lists hamstring tears and posterior-capsule knee trauma without defining whether the goal is partial analgesia or complete procedural anesthesia, the evidence base, or rescue coverage. Sciatic blockade also causes extensive distal motor/sensory loss disproportionate to some listed uses.
- `sections.contraindications` omits antithrombotic timing for a deep peripheral block, refusal/cooperation, and preexisting neurologic deficit. `sections.anatomy` and `sections.steps` do not identify inferior gluteal/other vascular danger structures or require a Doppler-safe path.
- `sections.steps` and `sections.troubleshooting` lack incremental injection/repeated aspiration and stop rules for pain, paresthesia, high resistance/pressure, swelling, or poor tip visualization. `sections.complications` omits LAST, hematoma/noncompressible bleeding, infection, and block failure.
- `sections.aftercare` appropriately identifies foot drop and strict non-weight-bearing, but documentation does not require a post-block motor/sensory exam, fall/limb-protection handoff, or ACS surveillance where relevant.

**Equipment/instruments.** A curvilinear probe and 80-100 mm 21-22G needle may be appropriate for selected adults, but depth varies substantially and needle length needs habitus qualification. The list omits complete sterile supplies, extension tubing/test injection, monitoring, IV access, oxygen/resuscitation equipment, and lipid rescue. Deep-block credentialing and pressure-monitoring policy require local approval.

**Dosing/monitoring.** The bupivacaine worked example is arithmetically correct and below both recorded ceilings. The bupivacaine 2 mg/kg and ropivacaine 3 mg/kg/200 mg limits require clinician/institutional authority; no ropivacaine example is supplied. The assertion in `sections.seniorPearls` that this nerve "takes" 20-30 mL is too categorical without technique-specific minimum-effective-volume evidence and patient adjustment. Mixed-agent calculation and special-population reductions are not defined.

**Reviewer question/proposed disposition.** Correct posterior-thigh coverage and indications, define deep-block antithrombotic/vascular safety and injection stop rules, and approve the lowest effective volume plus aftercare. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_tibial_nerve` - Tibial Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** Ultrasound-guided ankle-block studies use the posterior tibial artery as a landmark and show that low-volume image-guided techniques can be effective, but the artery and accompanying veins make vascular identification and incremental injection central safety steps. The block covers plantar/heel sensation; motor and gait effects still require patient assessment. [Fredrickson et al., randomized ultrasound-guided ankle-block trial, 2011](https://pubmed.ncbi.nlm.nih.gov/21610557/); [ASRA, neurologic-complications advisory, 2015](https://rapm.bmj.com/content/40/5/401)

**Findings.**

- `sections.steps` correctly identifies the nerve next to the posterior tibial artery and says to aspirate, but color Doppler appears only in `sections.troubleshooting`. The step should require artery/vein mapping, continuous tip visualization, incremental injection/repeated aspiration, and stop rules for pain, paresthesia, swelling, or resistance.
- `sections.contraindications` lists only site infection and allergy. Refusal/cooperation, preexisting tibial deficit, and antithrombotic/bleeding assessment under the superficial-site compressibility framework are absent.
- `sections.complications` lists only intravascular injection and nerve injury, omitting LAST, hematoma, infection, failed block, and persistent deficit. `sections.aftercare` appropriately warns about unrecognized plantar injury but does not require motor/gait assessment or supported ambulation where function is impaired.
- `sections.confirmation` and `sections.documentation` include plantar sensory change and pre/post examination, but no failure/rescue plan before plantar wound manipulation is given.
- `sections.references` does not support the target relationship, 5-10 mL volume, instrument choice, or dosing.

**Equipment/instruments.** A high-frequency linear probe and 25-27G 1.5-inch needle are plausible for a superficial ankle target, but the visibility/needle choice should be clinician approved. The list omits antiseptic, sterile gloves/drape, sterile cover/gel, syringe/extension supplies, monitoring, oxygen/resuscitation equipment, and lipid rescue. Landmark use should be a separately specified technique rather than a parenthetical alternative to incomplete ultrasound steps.

**Dosing/monitoring.** `10 mL x 10 mg/mL = 100 mg` is correct, but the example reports a 315 mg maximum at 70 kg instead of applying the 300 mg absolute ceiling. The 50 kg result is 225 mg. Lidocaine's 4.5 mg/kg/300 mg pair is label-supported for normal healthy adults; bupivacaine's 175 mg cap is labeled but 2 mg/kg is not, and there is no bupivacaine worked example. The fixed 30-minute monitoring requirement is conservative for a potentially toxic dose but should be tied to dose/risk and local policy for this low-volume block.

**Reviewer question/proposed disposition.** Correct the lidocaine ceiling, move vascular/incremental safety into the ordered steps, complete contraindication/complication/setup and functional aftercare, and approve dose/monitoring policy. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_sural_nerve` - Sural Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** A randomized volunteer study found improved sural-block success when ultrasound used the small/lesser saphenous vein as the landmark and local anesthetic was placed circumferentially around the vein. That technique makes explicit vascular identification, aspiration, tip visualization, and small incremental injection important; it does not justify an unqualified instruction to inject around a nerve/vein without those safeguards. [Redborg et al., randomized sural-block trial, 2009](https://pubmed.ncbi.nlm.nih.gov/19258984/); [ASRA, neurologic-complications advisory, 2015](https://rapm.bmj.com/content/40/5/401)

**Findings.**

- `sections.steps` ends with "Inject 3-5 mL of anesthetic around the nerve/vein" but does not instruct aspiration, incremental injection, Doppler/vein compression, continuous tip visualization, or a stop response. This conflicts with `dosing.monitoring`, which requires repeated aspiration and 3-5 mL increments, and creates avoidable intravascular-injection ambiguity beside the small saphenous vein.
- `sections.troubleshooting` offers a subcutaneous landmark wheal from Achilles tendon to lateral malleolus but does not identify it as a distinct technique with total volume, aspiration pattern, field boundaries, confirmation, or rescue for incomplete lateral-foot coverage.
- `sections.contraindications` omits refusal/cooperation, preexisting sural deficit, and bleeding assessment. `sections.complications` lists only intravascular injection, omitting nerve injury, hematoma, infection, LAST, and block failure.
- `sections.aftercare` says only "Routine wound care" despite deliberate lateral-foot sensory loss. It needs protection from thermal/pressure/weight-bearing injury and return precautions until sensation normalizes.
- `sections.references` does not support ultrasound versus landmark technique, volume, coverage, safety, or dosing.

**Equipment/instruments.** A linear probe and 25-27G 1.5-inch needle are plausible for this superficial sensory block, subject to operator visualization. The list omits antiseptic, sterile gloves/drape, sterile probe cover/gel, syringe/extension supplies, monitoring, oxygen/resuscitation equipment, and lipid rescue. A landmark field block needs its own complete equipment and dose accounting.

**Dosing/monitoring.** `5 mL x 10 mg/mL = 50 mg` is correct, but the example again displays 315 mg at 70 kg rather than the lower 300 mg absolute lidocaine ceiling; 50 kg equals 225 mg. The label supports 4.5 mg/kg/300 mg for normal healthy adults. Bupivacaine's 175 mg cap is label-supported but 2 mg/kg is not, and it has no worked example. Even though the intended 3-5 mL dose is small, prior blocks, wound infiltration, bilateral blocks, and mixed agents still require a defined additive calculation.

**Reviewer question/proposed disposition.** Correct the lidocaine lower-ceiling example, make aspiration/vascular mapping/incremental injection explicit, separate and complete the landmark technique, and add sensory-protection aftercare and the missing complications/setup. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## Sources and limitations

Additional authoritative/original sources used across the lane include [ASRA-ESRA, *Standardizing Nomenclature in Regional Anesthesia*, 2024](https://rapm.bmj.com/content/49/11/782), [Buttner et al., MRI study of subparaneural popliteal injection, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6534099/), [Kwofie et al., adductor-canal versus femoral motor/balance trial, 2013](https://pubmed.ncbi.nlm.nih.gov/23788068/), [Redborg et al., sural-block trial, 2009](https://pubmed.ncbi.nlm.nih.gov/19258984/), and the current FDA labels linked above. Secondary summaries were used only to orient source discovery and were not sole support for substantive findings.

Evidence limitations are important. Several technique/volume sources are small trials, volunteer studies, cadaver studies, or early PENG literature; they do not establish a single universal approach. This audit did not evaluate local credentialing, formulary concentrations, anticoagulant policy, procedural-sedation policy, or postoperative staffing. Pediatric and pregnancy dosing, frailty, hepatic/cardiac disease, preexisting neuropathy, mixed-local-anesthetic calculations, and block-specific antithrombotic decisions require qualified clinician and institutional review. Structural or arithmetic agreement is not clinical approval.

Changed file: `docs/audits/procedure-verification/08_REGIONAL_LOWER.md` only. No JSON, Swift, validator, rescue-card, or `reviewerStatus` content was changed.
