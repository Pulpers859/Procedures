# Procedure Verification Lane 06: Regional Upper Extremity

## Audit boundary

- AI-assisted discrepancy screen only. I am not a licensed clinical reviewer, and this report does not approve content.
- Assigned records: `digital_nerve_block`, `block_interscalene`, `block_supraclavicular`, `block_raptir`, `block_radial_nerve`, `block_median_nerve`, `block_ulnar_nerve`, and `block_superficial_cervical_plexus`.
- Before review, `Procedures/Resources/procedures.json` SHA-256 was confirmed as `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`.
- I screened all metadata, every section, equipment/instruments, visual-asset metadata where present, and every structured dosing field. Unmentioned fields had no additional material discrepancy in the sources reviewed.
- The common reference strings `Standard emergency medicine regional anesthesia literature` and edition-free textbooks do not let a reviewer trace individual claims. NYSORA is secondary and cannot be the sole support under the audit protocol.
- **MINOR metadata:** all assigned records except `digital_nerve_block` use `reviewTime: "standard"`, which is outside the values listed in `PROCEDURE_SCHEMA.md`. The same seven records use `icon: "lungs"`, including distal radial/median/ulnar blocks where it is not a procedure-identifying icon. These should be reconciled with the schema/UI owner without changing clinical disposition.

## Cross-cutting source standards

- ASRA's 2025 infection-control guideline calls for chlorhexidine-alcohol skin preparation with adequate drying, sterile gloves, and sterile gel plus a single-use sterile probe cover for ultrasound-guided regional anesthesia. Its broader aseptic framework also addresses draping, cap, and mask use by procedure class and setting. [ASRA, *Consensus Practice Infection Control Guidelines*, 2025](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651)
- The current FDA lidocaine label requires the lowest effective dose, immediate oxygen/resuscitation capability, careful cardiovascular/respiratory/consciousness monitoring after injection, and IV access for major brachial-plexus blocks. It caps plain lidocaine in normal healthy adults at 4.5 mg/kg and generally 300 mg. [FDA/DailyMed, *Lidocaine Hydrochloride Injection Prescribing Information*, current label accessed 2026](https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid=240c4744-e58c-4c08-93ad-8d6418c4f8a9&type=pdf)
- The current bupivacaine label gives an adult peripheral-nerve-block ceiling of 175 mg without epinephrine but says dose limits must be individualized by block, site vascularity, size, and physical status; it does not establish the JSON's universal 2 mg/kg rule. [FDA/DailyMed, *Bupivacaine Hydrochloride Injection Prescribing Information*, revised 2025](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=02d0e5f1-5fab-4420-b673-785fd81d7ae2&type=display)
- The current ropivacaine label provides procedure-specific adult ranges, says major-block dosing must be adjusted for site and patient status, and specifically warns that supraclavicular blocks may have more serious adverse reactions. It does not establish the JSON's universal 3 mg/kg/200 mg rule. [FDA/DailyMed, *Ropivacaine Hydrochloride Injection Prescribing Information*, revised 2026](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=8c5c762f-d266-4b1a-809e-f11bfc89bc2d)
- ASRA states that local-anesthetic toxic effects are additive and provides a 20% lipid-emulsion rescue checklist. The JSON's phrase that different agents "share one maximum" does not explain how to calculate an additive mixed-agent limit. [ASRA, *Third Practice Advisory on LAST*, 2018](https://rapm.bmj.com/content/43/2/113) and [ASRA, *LAST Checklist*, 2020](https://asra.com/docs/default-source/guidelines-articles/local-anesthetic-systemic-toxicity-rgb.pdf?sfvrsn=33b348e_2)
- ASRA's fifth-edition antithrombotic guideline applies neuraxial timing to deep plexus/deep peripheral blocks, explicitly including infraclavicular block, and calls for other peripheral sites to be assessed by compressibility, vascularity, and consequences of bleeding. [ASRA, *Regional Anesthesia in the Patient Receiving Antithrombotic or Thrombolytic Therapy*, fifth edition, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766)

## `digital_nerve_block` - Digital Nerve Block

**Screening disposition: STOP-SHIP**

**Source-standard summary.** ACEP's 2025 review distinguishes dorsal, transthecal, volar, and circumferential techniques and recommends matching the approach to the injured surface; it notes that a dorsal web-space block can have incomplete distal/nail-bed coverage. Randomized evidence likewise found more predictable coverage with the two-injection dorsal technique but less injection pain with a volar approach. The FDA lidocaine label calls for restricted quantities in digits and the lowest effective dose. [ACEP, *Digital Nerve Blocks*, 2025](https://www.acep.org/siteassets/sites/acep/media/moc/moc-documents/cdem_39_llsa.pdf); [Turkish Journal of Emergency Medicine, randomized trial, 2022](https://pubmed.ncbi.nlm.nih.gov/35936956/)

**Findings.**

- `visualAssets[0].assetName` is `null`, and its caption explicitly calls it placeholder metadata. The repo safety policy says declared placeholder assets are stop-ship; the `clinicalWarning` also contains the nonclinical phrase "Fadial-style clarity." The reviewer must either remove the declaration for release or provide and approve the exact bundled clinical asset.
- `dosing.workedExample` says the 70 kg lidocaine maximum is 315 mg, while `dosing.agents[0].absoluteMaxMg` is 300 mg and the FDA label generally caps plain adult lidocaine at 300 mg. This internally contradictory worked example must be corrected to the clinician-approved rule (typically the lower applicable limit) before bedside use.
- `sections.steps` mixes an unspecified "chosen technique" with a dorsal-lateral two-sided sequence and gives no per-injection or total digit volume. Because `sections.indications` includes nail-bed injury, the current confirmation/failure plan does not tell the user when the selected approach may miss distal dorsal coverage or which supported rescue approach to use.
- `sections.references` gives no edition/year for the textbooks and no direct source for technique choice, volume, digit perfusion rescue, or bupivacaine limits.

**Equipment/instruments.** The 3-5 mL syringe and 25-30G needle are plausible. The checklist should be reviewed against ASRA asepsis: it says only `Gloves` and `Alcohol or chlorhexidine prep`, without sterile-glove qualification, chlorhexidine-alcohol/drying language, or immediate oxygen/resuscitation capability. Ring removal and pre-block neurovascular examination are appropriately present.

**Dosing/monitoring.** The lidocaine concentration and 4.5 mg/kg/300 mg fields match the adult plain-lidocaine label, subject to patient-specific reduction. The bupivacaine 2 mg/kg value is not established by the cited primary label even though the 175 mg cap appears there. The universal 30-minute monitoring rule is not sourced as a standard for every low-volume digital block and should be designated as institutional policy or supported. Pediatric, pregnancy, hepatic/cardiac disease, end-artery compromise, and mixed-local-anesthetic calculations remain clinician-dependent.

**Reviewer question/proposed disposition.** Correct the contradictory lidocaine example, resolve the release-blocking visual placeholder, select and describe supported technique-specific coverage/volume/failure guidance, and approve an asepsis/monitoring standard. Keep `STOP-SHIP` until those items are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_interscalene` - Interscalene Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** Interscalene block is effective for shoulder analgesia but respiratory effect is volume- and technique-dependent. In a randomized trial, 20 mL produced diaphragmatic paralysis in 100% while 5 mL produced it in 45%, so 100% is not a universal rate. ACEP also cautions against use with respiratory compromise and known contralateral laryngeal-nerve palsy. Clavicle studies use combined cervical-plexus plus brachial-plexus/fascial techniques rather than establishing this record's stand-alone lateral-clavicle claim. [Riazi et al., randomized trial, 2008](https://pubmed.ncbi.nlm.nih.gov/18682410/); [ACEP Sonoguide, *Interscalene Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/interscalene-nerve-block); [Zhuo et al., randomized trial, 2022](https://pubmed.ncbi.nlm.nih.gov/35061634/)

**Findings.**

- `sections.shiftMode` states "phrenic nerve palsy (100% block)" while prescribing 10-15 mL. The cited 100% rate came from 20 mL in the randomized source; low-volume ultrasound-guided blocks reduced, but did not eliminate, paresis. The fixed percentage is unsupported and may distort risk/benefit decisions.
- `sections.indications` lists lateral-third clavicle fracture without saying whether the block is an analgesic adjunct or requires superficial/intermediate cervical plexus or another component for reliable clavicular coverage. The reviewer must define intended coverage and the failure/rescue plan.
- `sections.contraindications` appropriately identifies severe pulmonary disease and contralateral phrenic palsy but omits the documented contralateral recurrent-laryngeal-nerve concern and gives no antithrombotic/bleeding-site assessment.
- `sections.troubleshooting` calls phrenic block an "expected complication" but gives only reassurance, oxygen monitoring, and nonspecific respiratory support. It needs clinician-defined escalation criteria for dyspnea/hypoxemia and an alternative block decision before injection.
- `sections.references` cannot support the technique-specific claims because the lead reference is only "Standard emergency medicine regional anesthesia literature."

**Equipment/instruments.** A high-frequency linear probe and 21-22G 50 mm echogenic short-bevel needle are plausible for selected adults, but length needs body-habitus qualification. The operational list omits sterile gloves/drape, BP monitoring, IV access, oxygen, and cardiopulmonary resuscitation equipment despite this being a major brachial-plexus block. Sterile cover/gel and chlorhexidine are present, but drying is not.

**Dosing/monitoring.** The worked bupivacaine arithmetic (15 mL of 0.25% = 37.5 mg) is correct. The bupivacaine and ropivacaine universal mg/kg/absolute ceilings need a clinician-selected authoritative policy; FDA labels instead require site/patient individualization. The structured monitoring list has ECG/pulse oximetry and lipid access but omits BP, IV access, oxygen/resuscitation readiness, and patient-specific dose reduction. The fixed 30-minute duration should be sourced or marked institutional.

**Reviewer question/proposed disposition.** Replace the fixed 100% claim with volume/technique-specific language, decide clavicle coverage and respiratory rescue thresholds, and complete the major-block setup. Keep `MAJOR` pending qualified review. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_supraclavicular` - Supraclavicular Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** Contemporary studies show clinically important but variable hemidiaphragmatic paresis: 47.5% with 25 mL in one randomized trial, 44% any paresis with 30 mL in another, and occurrence even at low volumes in a dose-response study. Pneumothorax remains possible despite ultrasound. ACEP supports arm-below-shoulder indications and explicitly cautions in lung disease. [Kim et al., randomized trial, 2021](https://pubmed.ncbi.nlm.nih.gov/34548555/); [Petrar et al., randomized trial, 2015](https://pubmed.ncbi.nlm.nih.gov/25650633/); [Tedore et al., dose-response study, 2020](https://pubmed.ncbi.nlm.nih.gov/33004656/); [ACEP Sonoguide, *Supraclavicular Brachial Plexus Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/supraclavicular-block)

**Findings.**

- `sections.equipment` specifies 15-20 mL, but `sections.steps` directs 10-15 mL in the corner pocket plus another 5-10 mL superficially, permitting 15-25 mL. The conflicting total volume must be reconciled because respiratory effect and toxicity are dose/volume dependent.
- `sections.troubleshooting` says "bouncing off the rib into the corner pocket is safer." First-rib visualization is a valid pleural safety landmark, but the reviewed sources do not establish deliberate rib contact/bouncing as a preferred rescue maneuver. A regional-anesthesia reviewer should decide whether to remove or tightly qualify this instruction.
- `sections.complications` and `sections.aftercare` name pneumothorax and dyspnea but do not provide a delayed-pneumothorax failure plan, diagnostic trigger, observation/return precaution, or escalation action.
- The approximate `~50%` phrenic-risk statement is plausible for some studied volumes but should be tied to volume/technique rather than presented as a stable incidence.
- `sections.references` lacks a traceable technique or complication source.

**Equipment/instruments.** Probe, sterile cover/gel, skin prep, hydrodissection saline, and a short-bevel echogenic needle are reasonable. A fixed 50 mm needle may be inadequate in some body habitus; ACEP's current ED guide lists a longer 3.5-inch 22G option. Sterile gloves/drape, BP monitoring, IV access, oxygen, and resuscitation equipment are absent from the equipment checklist.

**Dosing/monitoring.** The worked example (20 mL of 0.25% bupivacaine = 50 mg) is correct, but the total-volume conflict can change the actual dose. The FDA ropivacaine label specifically warns that supraclavicular blocks may have a higher frequency of serious adverse reactions. Universal bupivacaine/ropivacaine ceilings, mixed-agent calculation, and fixed 30-minute monitoring need authoritative or institutional approval; BP and IV access are missing.

**Reviewer question/proposed disposition.** Set one clinician-approved total volume/concentration, remove or validate the rib-bounce instruction, and add an actionable respiratory/pneumothorax rescue pathway and complete setup. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_raptir` - RAPTIR (Infraclavicular) Block

**Screening disposition: STOP-SHIP**

**Source-standard summary.** The original ED report said RAPTIR likely reduces phrenic, vascular, nerve, and pneumothorax risks; it did not say those risks are absent. Randomized data support distal-upper-limb efficacy with 30 mL, but the needle passes through the clavicle's acoustic shadow. A published hemothorax case and cadaver concerns demonstrate potentially serious injury in a noncompressible blind segment. ASRA classifies infraclavicular block among deep plexus/peripheral techniques for antithrombotic management. [Luftig et al., original ED description, 2017](https://pubmed.ncbi.nlm.nih.gov/28126454/); [Grape et al., randomized trial, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6435841/); [Ribeiro et al., hemothorax case report, 2023](https://pubmed.ncbi.nlm.nih.gov/38169999/); [ASRA antithrombotic guideline, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766)

**Findings.**

- `sections.shiftMode` says the block avoids "the pneumothorax/phrenic risk" of supraclavicular blocks. Evidence supports risk reduction, not elimination. This false reassurance concerns potentially life-threatening thoracic injury and is STOP-SHIP.
- `sections.steps` says to visualize the tip "as it enters" the infraclavicular beam but does not explicitly acknowledge the unvisualized retroclavicular segment, define a safe trajectory through that blind segment, or state when to abandon the approach.
- `sections.complications` lists only vascular puncture, nerve injury, and rare pneumothorax. It omits reported hemothorax and the specific noncompressible vascular/suprascapular-neurovascular hazard beneath the clavicle. `sections.troubleshooting` likewise has no thoracic/bleeding rescue pathway.
- `sections.contraindications` says only `Coagulopathy` for bleeding risk. ASRA's current deep-block guidance requires drug-specific neuraxial-equivalent timing for antithrombotic therapy, not an undefined coagulopathy screen.
- `sections.references` relies on generic literature and does not cite the technique's limited evidence base or reported serious complication.

**Equipment/instruments.** A high-frequency linear or depth-appropriate curvilinear probe and 80-100 mm echogenic block needle are plausible. The checklist omits sterile gloves/drape, sterile-gel wording, BP monitoring, IV access, oxygen, and resuscitation equipment. The reviewer should decide whether nerve stimulation/pressure monitoring is required locally; neither is proven to eliminate injury, but the blind segment makes explicit local credentialing and abandonment criteria important.

**Dosing/monitoring.** The worked example (30 mL of 0.25% bupivacaine = 75 mg) is arithmetically correct. The 20-30 mL range overlaps published trials, but the universal bupivacaine/ropivacaine ceilings and mixed-agent warning still need an approved primary source. Major-block setup is incomplete despite ECG/pulse oximetry and lipid access in `dosing.monitoring`.

**Reviewer question/proposed disposition.** Replace the no-risk claim, explicitly address the acoustic-shadow segment and abandonment criteria, add hemothorax/noncompressible-bleeding rescue, and encode current antithrombotic handling. Keep `STOP-SHIP` until a credentialed regional-anesthesia reviewer resolves these items. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_radial_nerve` - Radial Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** ACEP's 2025 guide emphasizes overlapping hand sensory territories and says the radial nerve has only a small exclusive cutaneous territory. At the elbow it bifurcates into deep and superficial branches; a forearm approach blocks only the superficial branch, while a proximal approach is needed for both branches and fracture-related coverage. High-resolution ultrasound anatomy confirms the branching and changing nerve-vessel relationships. [ACEP Sonoguide, *Radial Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/radial-nerve-block); [Radiologia Brasileira, ultrasound anatomy study, 2021](https://pubmed.ncbi.nlm.nih.gov/34866699/)

**Findings.**

- `sections.shiftMode` combines two materially different targets (spiral groove or elbow), while `sections.steps` teaches only "the level of the elbow crease" and never confirms whether the main nerve or a branch is being blocked.
- `sections.shiftMode` overstates predictable anesthesia as dorsal thumb, index, and lateral middle finger. ACEP emphasizes extensive overlap and only a small exclusive radial territory; the record does not warn that distal dorsal/nail-bed sensation may come from median/ulnar nerves or require testing/supplementation.
- `sections.indications` includes dorsal-hand fractures without distinguishing superficial soft-tissue anesthesia from osteotomal fracture analgesia or specifying when an above-elbow block is necessary. `sections.confirmation` and `troubleshooting` provide no branch-specific motor/sensory test or incomplete-block rescue.
- `sections.contraindications`, `complications`, `aftercare`, and `documentation` are too thin for a trauma block: no refusal/cooperation, preexisting deficit/compartment-syndrome concern, bleeding assessment, infection prevention, LAST action, or explicit post-block protection/return precautions.
- `sections.references` is not traceable to the claimed level, coverage, or dose.

**Equipment/instruments.** The list omits skin antiseptic, sterile gloves, sterile gel/probe cover, syringes/flush, BP/ECG/pulse oximetry, IV/oxygen/resuscitation equipment, and lipid rescue. ACEP lists a 20-22G 1.5-inch-or-longer block needle and reserves thinner needles for more advanced users; the unqualified 25-27G 1.5-inch choice may impair visualization and should be approved or revised.

**Dosing/monitoring.** `workedExample` repeats the 315 mg versus 300 mg lidocaine contradiction. If median, ulnar, and radial blocks are combined at the listed 5-10 mL each, total local-anesthetic volume can reach 30 mL before skin wheals or prior dosing; ACEP specifically warns this can approach or cross toxicity thresholds. Mixed-agent additivity and the fixed 30-minute monitoring rule require clinician/institutional definition.

**Reviewer question/proposed disposition.** Choose one taught target level or provide separate level-specific paths, correct sensory/osteotomal coverage and rescue testing, complete the setup/contraindication content, and correct dosing logic. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_median_nerve` - Median Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** ACEP describes the median nerve in the FDS/FDP fascial plane, recommends a proximal forearm target to include branches, prefers an in-plane approach, and stresses overlapping hand territory. It cautions that forearm blocks are not generally reliable for wrist-fracture osteotomes and warns that combined forearm blocks can reach toxic dosing. [ACEP Sonoguide, *Median Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/median-nerve-block); [Nagdev et al., randomized volunteer comparison, 2016](https://pubmed.ncbi.nlm.nih.gov/26920669/)

**Findings.**

- `sections.steps` permits an out-of-plane approach but gives no out-of-plane tip-tracking method, test aliquot, needle-path vascular check, or stop rule for pain, paresthesia, nerve swelling, or high resistance. The cited ACEP technique recommends in-plane guidance.
- `sections.shiftMode` presents a broad palmar distribution without the source-standard warning about overlap and small exclusive territory. `sections.indications` lists volar finger fractures/dislocations but does not distinguish procedural skin anesthesia from fracture osteotomes or give an incomplete-block rescue plan.
- `sections.confirmation` records only fluid spread, not a target-specific sensory/motor assessment before the painful procedure. `sections.troubleshooting` helps identify FDS/FDP but does not address failed coverage or suspected intraneural/intravascular injection.
- Contraindications, complications, aftercare, documentation, and references have the same clinically important omissions described for the radial record.

**Equipment/instruments.** The unqualified 25-27G 1.5-inch needle differs from ACEP's standard 20-22G block-needle recommendation, with thinner needles presented for advanced users. Skin prep, sterile gloves/gel/cover, syringes, monitoring, IV/oxygen/resuscitation equipment, and lipid rescue are absent.

**Dosing/monitoring.** `workedExample` incorrectly leaves the 70 kg plain-lidocaine result at 315 mg despite the 300 mg cap. The 5-10 mL block range is within ACEP's technique range, but combined blocks and skin wheals must be summed. The mixed-agent and universal monitoring language requires approved calculation and policy.

**Reviewer question/proposed disposition.** Decide whether to teach only in-plane guidance or add a complete out-of-plane method; define fracture versus soft-tissue use, sensory confirmation, and rescue; complete setup and correct the lidocaine example. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_ulnar_nerve` - Ulnar Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** ACEP supports forearm ulnar block for ulnar-hand soft-tissue procedures and isolated fifth-metacarpal fractures, but stresses overlapping territory, pre-scan identification of the artery, a sterile setup, test aliquots, incremental injection, and visible separation of nerve and artery. The dorsal cutaneous branch arises proximal to the wrist, supporting a more proximal target when dorsal coverage is required. [ACEP Sonoguide, *Ulnar Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/ulnar-nerve-block); [Radiologia Brasileira, ultrasound anatomy study, 2021](https://pubmed.ncbi.nlm.nih.gov/34866699/)

**Findings.**

- `sections.shiftMode` states coverage of the fifth digit and medial half of the fourth without qualifying palmar/dorsal overlap or requiring a mapped sensory check. The more proximal dorsal-cutaneous-branch pearl is useful but is not integrated into target selection or confirmation.
- `sections.steps` uses an in-plane medial approach and aspiration, but omits a small test aliquot, explicit continuous needle-tip visualization, stop rules for pain/paresthesia/resistance, and what to do if anesthetic does not separate the artery and nerve.
- `sections.confirmation` is ultrasound-only. There is no preprocedure target-specific sensory/motor confirmation or failed-block rescue before fracture manipulation or wound work.
- Contraindications, complications, aftercare, documentation, and references remain too thin for trauma use and omit compartment-syndrome/neurologic surveillance, bleeding assessment, LAST response, and traceable evidence.

**Equipment/instruments.** The unqualified 25-27G needle should be reconciled with ACEP's 20-22G standard block-needle recommendation and advanced-user caveat for thinner needles. The list lacks the complete aseptic and resuscitation setup described above.

**Dosing/monitoring.** `workedExample` again conflicts with the 300 mg adult lidocaine cap. A single 5-10 mL range is supported by ACEP, but combined forearm blocks can reach 30 mL and require a pre-draw cumulative calculation including skin wheals and prior local anesthetic. Mixed-agent and fixed observation policies need approval.

**Reviewer question/proposed disposition.** Tie target level to required dorsal/palmar coverage, add clinical confirmation and injection stop/rescue rules, complete setup/contraindications, and correct dosing logic. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_superficial_cervical_plexus` - Superficial Cervical Plexus Block

**Screening disposition: MAJOR**

**Source-standard summary.** ASRA-ESRA nomenclature defines superficial cervical plexus block as injection superficial to the investing fascia at the midpoint of the posterior SCM border; injection deep to the investing fascia but superficial to prevertebral fascia is an intermediate block. A randomized trial found injection depth changes diaphragmatic function and other spread-related effects. Clavicle trials generally combine cervical-plexus coverage with interscalene or clavipectoral coverage rather than proving this block alone covers the fracture. [ASRA-ESRA, *Standardizing Nomenclature in Regional Anesthesia*, 2024](https://rapm.bmj.com/content/49/11/782); [Opperer et al., randomized trial, 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8867263/); [Zhuo et al., randomized trial, 2022](https://pubmed.ncbi.nlm.nih.gov/35061634/)

**Findings.**

- `sections.steps` directs injection "immediately deep to the posterior border of the SCM" without identifying the investing and prevertebral fasciae. If this means beneath the SCM/investing fascia, the taught procedure is an intermediate block despite the superficial title. This plane ambiguity changes spread and respiratory/airway risk.
- `sections.indications` lists clavicle fracture without identifying whether this is cutaneous analgesia, an adjunct, or sole fracture anesthesia. The reviewed randomized clavicle evidence used a second brachial-plexus or clavipectoral component. A failure plan for incomplete osseous coverage is absent.
- Internal-jugular cannulation pain control is listed without a direct authoritative source, patient-selection rationale, comparison with local infiltration, or guidance to identify/avoid the IJV and other deeper vessels. Evidence was insufficient in this screen to support it as a routine indication.
- `sections.complications` and `sections.aftercare` mention phrenic block/dyspnea but omit voice/swallowing change, recurrent-laryngeal spread, local-anesthetic spread to deeper spaces, airway escalation, bilateral-block caution, and patient-specific pulmonary/contralateral nerve considerations.
- `sections.references` does not support the named plane, indications, complication profile, or dosing.

**Equipment/instruments.** A high-frequency linear probe, 25-27G 1.5-inch needle, and 5-10 mL volume are plausible depending on the actual plane. The list lacks skin antiseptic, sterile gloves, sterile single-use gel/probe cover, syringes, monitoring, IV/oxygen/resuscitation setup, and lipid rescue. The external jugular vein is noted in anatomy but vascular mapping is not an explicit step.

**Dosing/monitoring.** `workedExample` repeats the 315 mg versus 300 mg lidocaine contradiction. The 5-10 mL range has adult precedent, but a clinician must approve the concentration/volume for the precisely named plane and respiratory-risk population. Fixed bupivacaine limits, mixed-agent additivity, and 30-minute observation need authoritative or institutional definition.

**Reviewer question/proposed disposition.** Name and teach one anatomically explicit fascial plane, define clavicle and IJV indications plus rescue, add airway/respiratory cautions, complete setup, and correct the lidocaine example. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## Sources and limitations

Additional primary/authoritative sources used across the lane include [ASRA, neurologic-complications advisory, 2015](https://rapm.bmj.com/content/40/5/401), [ASRA-led regional-anesthesia documentation Delphi consensus, 2022](https://rapm.bmj.com/content/early/2022/02/21/rapm-2021-103136), [Liebmann et al., ED forearm-block feasibility study, 2006](https://doi.org/10.1016/j.annemergmed.2006.04.014), and [Tran et al., randomized superficial-cervical-plexus technique comparison, 2010](https://pubmed.ncbi.nlm.nih.gov/20975470/). Secondary reviews were used only for orientation and were not sole support for substantive findings.

Limitations: this was a source-and-discrepancy screen, not independent replication of every technique or a systematic review. Several questions remain institution-, product-, credentialing-, body-habitus-, age-, pregnancy-, organ-function-, and antithrombotic-specific. FDA labels do not supply a single universal mg/kg maximum for every drug/block combination. Structural validity was not re-run because no JSON/schema file was changed, and no macOS/Xcode runtime review was applicable. Qualified emergency-medicine, regional-anesthesia, pharmacy, infection-control, and institutional-policy review is still required. No `reviewerStatus` was changed and no procedure is approved by this report.

Changed file: `docs/audits/procedure-verification/06_REGIONAL_UPPER.md` only.
