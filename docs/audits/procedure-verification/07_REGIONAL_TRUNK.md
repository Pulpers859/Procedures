# Regional Trunk Procedure Verification Audit

- Audit date: 2026-07-18
- Assigned IDs: `block_serratus_anterior`, `block_thoracic_esp`, `block_tap`, `block_pecs`
- Audited procedures SHA-256: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Boundary: AI-assisted discrepancy screening only. This report is not clinical approval, credentialing, an institutional protocol, or a substitute for qualified review.

## Owner adjudication - 2026-07-31

**How to read this section.** The lane report below is the AI screening record
against the audited snapshot and is left as written. This section records what
the clinical owner decided on 2026-07-31 and what changed in `4ea632d`. Every
`Screening disposition` line has been re-screened against the amended content,
with the original level named on each.

### Why this was not twenty-eight separate adjudications

Lanes 06 through 09 are twenty-eight near-identical records that drew
near-identical findings. Almost every one of them was told that its equipment
list omits asepsis, monitoring, and resuscitation readiness; that its
confirmation section proves where the drug went rather than whether the patient
is blocked; that it has no partial or failed-block pathway; and that its
references are untraceable. Twenty-eight bespoke rewrites of the same four
paragraphs would have produced twenty-eight slightly different versions of each,
which is how a corpus ends up with one block missing the sentence its
neighbours all carry.

So the answer is one safety spine, applied word-for-word and asserted identical
by test, in the same shape the vascular lane's pre-dilation gate uses. What is
per-block is what the lane reports actually named: the needle targets, the
overclaims, and the volumes.

### The spine

- **Spread on the screen is not success.** Twenty-five of the twenty-eight had
  one or two confirmation lines, and none of them tested the patient. Every
  block now tests the target's own territory - light touch or cold, and motor
  where the nerve has one, against the other side - and waits out the agent's
  onset before judging. A block called failed at five minutes was never tested.
- **A partial-block and a failed-block pathway on every card.** Supplement
  rather than repeat, and recalculate the remaining allowance first, because
  more of the same is how the ceiling gets crossed. This closes the P2 item.
- **Three stop signs on injection** - pain, paraesthesia, high resistance -
  none of which is a reason to push harder.
- **Setup that scales.** Major blocks get IV access, blood pressure, ECG,
  oximetry, and resuscitation equipment in the room. Minor blocks get asepsis
  and the location of the lipid emulsion. Demanding the full major-block setup
  for a digital block would produce a rule nobody follows, and a rule nobody
  follows is worse than no rule.
- **Antithrombotic handling matched to the depth of the block.** ASRA applies
  neuraxial-equivalent timing to deep blocks and asks a different question of
  everything else: can the site be compressed, how vascular is it, and what
  would a haematoma there do. Only the retroclavicular and transgluteal
  approaches get the neuraxial interval.
- **Aftercare for a limb that cannot feel.** Protection from pressure and heat,
  fall risk from motor block stated at handover, and - the one that matters
  most - how compartment syndrome announces itself through a working block. A
  team told only that blocks mask it watches for the wrong thing; a rising
  analgesic requirement and pain breaking through are the signs.
- **A pre-block neurological examination on every card**, because a deficit
  nobody looked for beforehand becomes the block's deficit afterwards.

### The four needle targets - owner-queue P0 item 4

In three of the four the wrong endpoint was the one written down, which is
worse than an omission: the reader takes the instruction as the technique.

1. **Popliteal sciatic** directed the needle "within its epineural sheath (the
   'Vloka sheath')". Epineural means inside the nerve's own covering. The
   target is the common paraneural sheath, outside both divisions, and the
   record now says the nerve should be pushed away by the injectate rather than
   swollen by it - and to stop and withdraw if it swells.
2. **Serratus anterior** said "hit the rib, slide off, inject". Off the rib is
   the intercostal space and the pleura is behind it. The rib is the endpoint,
   not a waypoint.
3. **PECS II** permitted an "or ribs" endpoint reached by passing through
   serratus. Removed; the pectoserratus plane is the only endpoint.
4. **Infraorbital** had no bounded trajectory at all. The palpating finger now
   stays over the foramen for the whole injection as the physical stop, the
   intraoral approach follows the second premolar's long axis to roughly 1.5-2
   cm, and nothing advances toward the orbit. Depth without a direction is the
   part that goes wrong: a shallow angle points at the orbit rather than the
   foramen.

### P1: the dosing governance model

- **The cumulative rule was wrong, not merely vague.** "All local anaesthetic
  this encounter shares one maximum" is not a valid mixed-agent calculation.
  Agents do not share a pool of milligrams. All forty dosing blocks in the
  corpus now say to work each agent out as a fraction of its own ceiling and
  keep the fractions under one - half a lidocaine maximum plus half a
  bupivacaine maximum is a full dose.
- **Every ceiling is now labelled as this app's governed policy** rather than
  as a fact about the drug, because the labels publish no universal mg/kg figure
  and explicitly require individualisation. Staying under the number is
  necessary and is not the same as being safe.
- **Site of absorption** is added as the individualisation axis the model
  lacked: the same milligram dose peaks higher from a vascular bed than from a
  subcutaneous wheal.
- **The TAP finding is answered without inventing a number.** No new ceiling was
  fabricated. Instead the four truncal fascial-plane blocks carry the
  pharmacokinetic evidence itself - bilateral dosing at 3 mg/kg of ropivacaine,
  and bilateral 200 mg totals, produced potentially toxic plasma concentrations
  at doses a weight-based calculator calls acceptable - and their cards name
  concentrations and volumes that keep a bilateral block well below that. The
  0.25% ropivacaine the records recommended is gone; no label supplies it.
- **Ten blocks stated a volume with no agent and no strength**, so the volume
  could not be converted to milligrams against the ceiling a few fields away.
  Each now names only the agents whose ceiling that volume actually fits under
  at the 50 kg reference weight. A thirty-millilitre block is not a lidocaine
  block, and the card says so.
- **Articaine** is resolved by taking it off the inferior alveolar card rather
  than by inventing a ceiling for it, with the reason - a reported and debated
  association with persistent paraesthesia after this block specifically - kept
  in the pearls.

### Stale findings

`workedExample` no longer exists anywhere in the corpus, so the 315 mg versus
300 mg lidocaine contradiction and the fascia iliaca 210 mg versus 200 mg
contradiction were both already resolved before this adjudication. So was the
"Standard emergency medicine regional anesthesia literature" placeholder. The
declared-placeholder artwork that drove the `digital_nerve_block` and
`fascia_iliaca_block` stop-ships stopped gating release on 2026-07-30.

### Two gaps the validator could not see

The tests written for this adjudication found two records - `digital_nerve_block`
and `fascia_iliaca_block` - that named no agent and no concentration anywhere,
beside a calculator offering three agents with three different ceilings. The
validator's rule needs a volume and the word "anesthetic" on one line with no
agent, and both records phrase it differently enough to slip past. Both now name
their agents.

The metadata findings were also real and unenforced: twenty-six records shipped
`reviewTime: "standard"`, which the schema does not list, because the validator
checked the field was present and never what it said. That check now exists. The
`icon` field, which said `lungs` on a mental nerve block, is deleted - no Swift
code has ever decoded it.

### Known residual gaps

- **`block_tap` stays MAJOR.** The ropivacaine ceiling itself is unchanged at 3
  mg/kg, and the pharmacokinetic evidence says that figure is not safe for a
  bilateral TAP. The card can no longer lead a reader to it, and the ceiling is
  still a pharmacy and regional-anaesthesia decision that this repository cannot
  make. That is the one open item left in these four lanes.
- Needle length is still given as a range on several blocks rather than being
  selected by measured depth.
- Coverage is stated as expected rather than guaranteed on the fascial-plane
  blocks, which is honest but leaves the reader to test it.
- Paediatric scope is not specified on any block in these lanes.
- Institutional credentialing for the deep and retroclavicular approaches is
  named as a requirement rather than resolved.

## `block_serratus_anterior` - Serratus Anterior Plane Block

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot. The findings are addressed in `4ea632d` by the shared safety spine and the per-block corrections recorded in the owner adjudication section at the top of this report. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because needle length is still a range rather than a measured depth, fascial-plane coverage is expected rather than guaranteed, and paediatric scope is deferred. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP.** because the senior pearl directs the operator to slide off the rib after contact, away from the consensus deep-plane target and toward an intercostal/pleural hazard. Additional `MAJOR` indication, setup, dosing, bleeding-risk, reassessment, and reference gaps require clinician review.

### Source-standard summary

The 2021 ASRA-ESRA nomenclature consensus defines superficial SAP injection as superficial to serratus anterior and deep SAP injection as between the posterior serratus surface and rib periosteum. The 2024 SABRE multicenter randomized trial supports SAPB as an adjunct to protocolized care for acute rib-fracture pain, but only 41% met its 4-hour composite analgesic endpoint, pneumonia and length of stay were unchanged, and the anterior-fracture subgroup did not favor SAPB. The original 2013 description supports both superficial and deep planes but does not establish all listed ED indications as standards of care.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `sections.seniorPearls`; related `sections.troubleshooting` | The instruction, briefly, "Hit the rib, slide off, inject" conflicts with the consensus deep SAP endpoint at the rib periosteum. Sliding off the rib can move the tip into an intercostal space while the pleura remains immediately relevant. The troubleshooting text correctly prioritizes rib visualization, but the two instructions do not form a safe, unambiguous endpoint. | Remove or replace the "slide off" action and have a regional-anesthesia clinician define the exact needle endpoint, hydrodissection method, and abort rule when the tip or pleura is not continuously visualized. |
| `MAJOR` | `sections.shiftMode`; `sections.indications` | "Essential" for multilevel rib fractures and chest-tube placement overstates the evidence. SABRE supports early analgesia as an adjunct to a rib-fracture care bundle, not universal necessity or outcome benefit. No authoritative primary evidence reviewed established SAPB as a standard for chest-wall abscess/laceration or as sufficient procedural anesthesia for tube thoracostomy. | Scope the indications and state whether each is analgesic adjunct, procedural anesthesia, or institution-specific practice; require a fallback analgesia/sedation plan for incomplete coverage. |
| `MAJOR` | `sections.shiftMode`; `sections.anatomy`; `sections.ultrasound`; `sections.confirmation` | The fixed "T3-T9" coverage reads as predictable. Fascial spread and clinical coverage vary by plane, level, volume, and patient. SABRE found benefit across a mixed fracture population but did not establish reliable T3-T9 blockade in every patient. | Decide whether to present coverage as expected/variable and define a clinical sensory and pain reassessment before relying on the block. |
| `MAJOR` | `sections.contraindications` | Antithrombotic therapy, coagulopathy, patient refusal/inability to consent, and altered local anatomy are not addressed. ESAIC/ESRA 2022 categorizes superficial and deep SAP approaches as superficial nerve procedures for antithrombotic timing, while ASRA 2025 requires non-deep peripheral techniques to be judged by compressibility, vascularity, and consequences of bleeding. A blanket prohibition is not supported, but omission of the decision process is unsafe in a trauma population. | Adopt an institution-approved bleeding-risk screen and clarify that drug interruption is not automatic for this classification; specify when anatomy, vascularity, or inability to monitor bleeding changes the plan. |
| `MAJOR` | `sections.equipment` | The needle and transducer are plausible, but the list omits skin antiseptic, sterile gloves/drape, a disinfected probe with sterile single-use cover and gel, syringes/labels, IV access, monitoring, and immediately available airway/resuscitation/LAST equipment. ASRA infection-control guidance requires sterile cover and sterile gel for regional anesthesia; the ASRA block checklist requires resuscitation equipment and lipid emulsion immediately available. | Define the minimum single-shot block setup and whether a 50 mm or 100 mm echogenic needle is selected by measured depth/body habitus rather than as an undifferentiated range. |
| `MAJOR` | `dosing.agents`; `dosing.workedExample`; `sections.equipment`; `sections.steps` | The arithmetic for 30 mL of 0.25% bupivacaine and its bilateral total is correct, and the cumulative-dose warning is valuable. However, `2 mg/kg/175 mg` bupivacaine and `3 mg/kg/200 mg` ropivacaine are presented as universal ceilings. The US bupivacaine label gives adult peripheral-block ranges up to 175 mg but says the maximum must be individualized by site, absorption, size, condition, and other factors; it does not establish a universal 2 mg/kg ceiling. The current ropivacaine label gives site-specific adult ranges, identifies 250 mg as the maximum recommended human nerve-block dose, and does not establish either 3 mg/kg or 200 mg as a universal absolute maximum. The text also recommends "0.25% ... ropivacaine," while the cited current label supplies 0.2% and 0.5%; any dilution/compounding workflow is unstated. | Replace universal-ceiling framing with a pharmacy/clinical-owner-approved policy tied to agent, formulation, site, patient factors, and all prior local anesthetic. Decide whether 0.25% ropivacaine is an approved local preparation and specify how it is obtained. |
| `MAJOR` | `dosing.monitoring`; `sections.aftercare`; `sections.complications` | Incremental 3-5 mL injection, repeat aspiration, continuous cardiac/pulse-oximetry monitoring, at least 30 minutes of observation after a potentially toxic dose, and advance LAST planning are supported. However, the record does not require functioning IV access or the actual LAST kit/lipid, airway equipment, and trained help at bedside. Bleeding/hematoma, infection, nerve injury, and block failure are absent from complications and aftercare. | Define pre-injection readiness and an aftercare bundle that includes clinical block assessment, pain/respiratory reassessment, injection-site bleeding, and explicit escalation for LAST or pneumothorax. |
| `MAJOR` | `sections.troubleshooting`; `sections.confirmation`; `sections.aftercare`; `sections.documentation` | Troubleshooting addresses only pleural visualization. There is no partial/failed-block pathway, no time-to-effect or sensory endpoint, no multimodal rescue plan, and no documentation of side, level, concentration, total mg, needle/probe approach, aspiration/incremental injection, pre/post neurologic status, or anticoagulant assessment. | Define success, partial failure, complete failure, reassessment timing, rescue analgesia, and the minimum procedure record. |
| `MAJOR` | `sections.references` | "Standard emergency medicine regional anesthesia literature" is not traceable, the cited ASRA advisory does not support the block-specific indications or technique, and NYSORA is a secondary source that cannot by itself support universal dose ceilings. | Replace the generic references with current direct, claim-matched primary/authoritative sources and an institution-approved dosing reference. |

### Equipment, dosing, and monitoring assessment

The stated 21G-22G, 50-100 mm needle range is plausible but needs depth-based selection and a complete aseptic/resuscitation setup. The 20-30 mL volume is within volumes used in published techniques, but it is not a universal dose and must be converted to total milligrams, including bilateral and prior local anesthetic. The current cumulative warning and incremental-injection language are strengths. The fixed dose ceilings need governance before release, and "lipid stocked" should be upgraded to immediately available LAST resources with IV access and trained response capability.

No additional material discrepancy was identified in the basic lateral positioning, identification of latissimus/serratus/rib/pleura, or linear fascial-spread confirmation beyond the target, coverage, failure-plan, and setup issues above.

### Reviewer questions and proposed disposition

1. What exact superficial and deep SAP needle endpoints will the institution teach, and will the "slide off" instruction be removed?
2. Which indications are supported as analgesic adjuncts, and what is the fallback for chest tube placement or incomplete rib-fracture analgesia?
3. Which patient/site-specific dosing policy replaces the universal mg/kg and absolute ceilings, including bilateral dosing and any 0.25% ropivacaine preparation?
4. What bleeding-risk, monitoring, sterile-equipment, and LAST-readiness checklist is mandatory before injection?

**Proposed reviewer disposition:** withhold from release until the needle-target instruction is corrected and the major indication, dosing, setup, and failure-plan decisions are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- ASRA-ESRA, [Standardizing nomenclature in regional anesthesia: abdominal wall, paraspinal, and chest wall blocks](https://doi.org/10.1136/rapm-2020-102451), 2021.
- Blanco et al., [Serratus plane block: a novel ultrasound-guided thoracic wall nerve block](https://pubmed.ncbi.nlm.nih.gov/23923989/), 2013 original description.
- Partyka et al., [Serratus Anterior Plane Blocks for Early Rib Fracture Pain Management: SABRE randomized clinical trial](https://jamanetwork.com/journals/jamasurgery/fullarticle/2818238), 2024.
- American College of Surgeons, [Best Practices Guidelines: Management of Chest Wall Injuries](https://www.facs.org/media/qdgliayt/2025_tr_bestpracticesguidelines_chest-wall.pdf), 2025.
- ESAIC/ESRA, [Regional anaesthesia in patients on antithrombotic drugs](https://esaic.org/wp-content/uploads/2023/12/regional_anaesthesia_in_patients_on_antithrom.pdf), 2022.
- ASRA Pain Medicine, [Regional anesthesia in the patient receiving antithrombotic or thrombolytic therapy, fifth edition](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766), 2025.
- ASRA Pain Medicine, [Consensus practice infection control guidelines for regional anesthesia and pain medicine](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651), 2025.
- US National Library of Medicine DailyMed, [Bupivacaine hydrochloride injection prescribing information](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ffecf450-1f01-4721-8e10-251385852612), revised 2023; [Ropivacaine hydrochloride injection prescribing information](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3d465e02-fd09-41b8-847f-bfe99cb4a712), revised 2025.
- ASRA Pain Medicine, [Third Practice Advisory on Local Anesthetic Systemic Toxicity](https://rapm.bmj.com/content/43/2/113), 2018; [LAST checklist](https://asra.com/news-publications/asra-updates/blog-landing/guidelines/2020/11/01/checklist-for-treatment-of-local-anesthetic-systemic-toxicity), 2020.

## `block_thoracic_esp` - Thoracic Erector Spinae Plane (ESP) Block

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally MAJOR against the audited snapshot. The findings are addressed in `4ea632d` by the shared safety spine and the per-block corrections recorded in the owner adjudication section at the top of this report. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because needle length is still a range rather than a measured depth, fascial-plane coverage is expected rather than guaranteed, and paediatric scope is deferred. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **MAJOR.** because the record presents disputed paravertebral spread and broad anterior/visceral coverage as settled mechanism, uses unsupported safety reassurance, and does not qualify a mixed-strength indication base. The defined needle target itself matches current nomenclature consensus.

### Source-standard summary

ASRA-ESRA consensus defines ESP injection between erector spinae muscle and the transverse process. Small randomized studies support possible analgesic benefit for multiple rib fractures, but definitive outcome evidence remains limited. Cadaveric evidence is inconsistent with the JSON's assured paravertebral mechanism: a 2018 study found no anterior spread to the paravertebral space, and a 2024 volume study likewise found no paravertebral, epidural, pleural, or ventral-ramus spread even with larger injections. Herpes-zoster evidence is largely case reports or retrospective data, and authoritative support for "thoracic spine fractures (lateral to midline)" as a general indication was not identified.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `MAJOR` | `sections.shiftMode`; `sections.anatomy` | The record states broad posterior/lateral/anterior somatic and visceral analgesia and says injection "allows" spread into the paravertebral space. These are mechanistic and coverage overclaims. Ivanusic 2018 and Gadsden 2024 found no paravertebral or ventral-ramus spread in their cadaver models; clinical effects may occur, but the pathway and dermatomal reliability remain variable. | Replace settled-mechanism language with a clinician-approved description of the intended target and variable expected coverage; decide what clinical endpoint is required before relying on anterior or visceral analgesia. |
| `MAJOR` | `sections.indications` | Multiple/posterior rib-fracture analgesia has limited trial support. Herpes-zoster evidence is low-level/retrospective, and no authoritative primary standard reviewed supported thoracic-spine fractures as a general indication. Fracture anatomy may also alter landmarks and risk. | Label evidence strength and whether each indication is routine, optional, rescue, or institution-specific; define exclusions when fracture or surgery distorts the target anatomy. |
| `MAJOR` | `sections.seniorPearls`; `sections.complications` | "Remarkably safe" and "keeping you far from the pleura" are stronger than the evidence. Pneumothorax, unintended neuraxial spread, LAST, bleeding, infection, and block failure remain possible; a bony target reduces but does not eliminate risk, especially if the operator is on a rib rather than a transverse process. | Remove absolute reassurance and define the sonographic features and stop conditions that distinguish transverse process from rib/pleura. |
| `MAJOR` | `sections.contraindications` | The record omits patient refusal/inability to consent, anticoagulant/coagulopathy assessment, and distorted local anatomy. ESAIC/ESRA 2022 lists ESP among superficial nerve procedures for antithrombotic timing; ASRA 2025 still requires assessment of compressibility, vascularity, and consequences of bleeding for non-deep peripheral techniques. | Adopt a reviewed bleeding-risk and anatomy screen rather than either silence or automatic neuraxial timing rules. |
| `MAJOR` | `sections.equipment` | The equipment list lacks sterile preparation/gloves/drape, disinfected probe with sterile cover/gel, labeled syringes, IV access, monitors, and immediately available airway/resuscitation/LAST equipment. The 50-100 mm needle range is not linked to measured target depth or body habitus. | Define the complete minimum setup and depth-based needle selection; decide whether a curvilinear probe is the default when a linear probe cannot show the target and pleura together. |
| `MAJOR` | `dosing.agents`; `dosing.workedExample`; `sections.equipment`; `sections.steps` | The bilateral bupivacaine arithmetic and cumulative warning are correct, but the universal `2 mg/kg/175 mg` and `3 mg/kg/200 mg` ceilings are not established by the cited authoritative labels. Bupivacaine labeling requires individualization; ropivacaine labeling uses site-specific ranges and a 250 mg maximum recommended human nerve-block dose, not a universal 200 mg absolute ceiling. "0.25% ropivacaine" also requires a defined preparation because the current label supplies 0.2% and 0.5%. | Adopt an institution/pharmacy-approved site- and patient-specific dosing source, define bilateral/repeat-dose calculations, and approve or remove the 0.25% ropivacaine preparation. |
| `MAJOR` | `sections.confirmation`; `sections.troubleshooting`; `sections.aftercare`; `sections.documentation` | Fascial "unzipping" confirms injectate location but not clinical success. There is no sensory/pain or respiratory reassessment, onset window, partial/failed-block pathway, rescue analgesia, injection-site bleeding check, or detailed documentation of side/level/concentration/total mg and antithrombotic decision. | Define clinical success and failure, reassessment timing, rescue treatment, and the minimum procedure record. |
| `MAJOR` | `sections.references` | The references are generic, rely on a LAST advisory and NYSORA for claims they do not directly support, and omit the original technique, current nomenclature, mechanism studies, antithrombotic guidance, and rib-fracture trials. | Add claim-matched primary/authoritative sources and an institution-approved dosing standard. |

### Equipment, dosing, and monitoring assessment

The target and in-plane approach are broadly consistent with consensus nomenclature, and a 20-30 mL injectate is represented in original and later studies, but no single volume assures a stated dermatomal or visceral effect. The shared dosing math, additive-toxicity warning, fractional injection, and at least 30-minute post-dose monitoring are useful. They do not replace patient/site-specific dosing, IV access, immediate LAST resources, continuous observation of consciousness/ventilation, or a clinical block assessment. Pediatric safety is not established in the cited ropivacaine label, and the bupivacaine label does not recommend use under age 12; the record should remain explicitly adult unless a separate pediatric policy is approved.

No additional material discrepancy was identified in the sitting/lateral positioning, sagittal probe orientation, identification of block-like transverse-process shadows, needle contact with the transverse process, or basic fascial-spread image beyond the mechanism and failure-plan limitations above.

### Reviewer questions and proposed disposition

1. What coverage and mechanism language will be used without promising paravertebral, anterior, or visceral effect?
2. Which of the three listed indications are approved, and how will weak/retrospective evidence be labeled?
3. What sonographic stop rule distinguishes transverse process from rib and prevents false reassurance about pleural distance?
4. Which dosing, anticoagulation, asepsis, monitoring, and rescue policies govern this bedside block?

**Proposed reviewer disposition:** retain as `Needs Clinical Review` and withhold from release until mechanism/coverage, indications, dosing, setup, and failure-plan language are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- ASRA-ESRA, [Standardizing nomenclature in regional anesthesia: abdominal wall, paraspinal, and chest wall blocks](https://doi.org/10.1136/rapm-2020-102451), 2021.
- Forero et al., [The Erector Spinae Plane Block: A Novel Analgesic Technique in Thoracic Neuropathic Pain](https://pubmed.ncbi.nlm.nih.gov/27501016/), 2016 original description.
- Ivanusic et al., [A Cadaveric Study Investigating the Mechanism of Action of Erector Spinae Blockade](https://pubmed.ncbi.nlm.nih.gov/29746445/), 2018.
- Gadsden et al., [Relationship between injectate volume and disposition in erector spinae plane block](https://pubmed.ncbi.nlm.nih.gov/37758461/), 2024 cadaveric study.
- Singh et al., [Thoracic epidural versus ESP block for multiple rib fractures](https://pubmed.ncbi.nlm.nih.gov/37601936/), 2023 pilot randomized trial.
- El Malla et al., [ESP versus serratus plane block in multiple rib fractures](https://pubmed.ncbi.nlm.nih.gov/34240173/), 2022 randomized trial.
- ESAIC/ESRA, [Regional anaesthesia in patients on antithrombotic drugs](https://esaic.org/wp-content/uploads/2023/12/regional_anaesthesia_in_patients_on_antithrom.pdf), 2022.
- ASRA Pain Medicine, [Regional anesthesia in the patient receiving antithrombotic or thrombolytic therapy, fifth edition](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766), 2025.
- ASRA Pain Medicine, [Consensus practice infection control guidelines](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651), 2025.
- DailyMed, [Bupivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ffecf450-1f01-4721-8e10-251385852612), revised 2023; [Ropivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3d465e02-fd09-41b8-847f-bfe99cb4a712), revised 2025.
- ASRA Pain Medicine, [Third Practice Advisory on LAST](https://rapm.bmj.com/content/43/2/113), 2018; [LAST checklist](https://asra.com/news-publications/asra-updates/blog-landing/guidelines/2020/11/01/checklist-for-treatment-of-local-anesthetic-systemic-toxicity), 2020.

## `block_tap` - Transversus Abdominis Plane (TAP) Block

**Screening disposition: `MAJOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot. The approach, coverage, anticoagulation classification, setup, and failure-plan findings are addressed in `4ea632d`, and the card now names concentrations and volumes that keep a bilateral block well below the concentrations the pharmacokinetic studies found troubling. It is not MINOR because the ropivacaine ceiling itself is unchanged at 3 mg/kg: no substitute figure was invented, and selecting one is a pharmacy and regional-anaesthesia decision this repository cannot make. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP.** because the structured dosing treats 3 mg/kg ropivacaine as a safe universal maximum for a block in which primary pharmacokinetic studies found potentially neurotoxic plasma concentrations at 3 mg/kg and after bilateral 200 mg dosing. Additional `MAJOR` approach/coverage, anticoagulation, setup, and failure-plan gaps require review.

### Source-standard summary

ASRA-ESRA consensus defines TAP injection between internal oblique and transversus abdominis; the described midaxillary technique is specifically a lateral/midaxillary TAP approach. Original work supports abdominal-wall postoperative analgesia, with approach-dependent coverage and no reliable visceral analgesia. A randomized trial supports TAP as part of balanced analgesia after open appendectomy, while the specific evidence for preoperative acute appendicitis pain is a small retrospective series. ESAIC/ESRA 2022 categorizes TAP as a superficial nerve procedure for antithrombotic timing. Bilateral TAP is a recognized high-volume systemic-absorption concern.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `dosing.agents[ropivacaine]`; `dosing.workedExample`; `dosing.cumulativeWarning`; `sections.equipment`; `sections.steps` | The record labels 3 mg/kg and 200 mg as ropivacaine maxima, which can be read as safe ceilings. In Griffiths 2010, bilateral TAP with 3 mg/kg produced potentially neurotoxic venous concentrations. In Torup 2012, bilateral 20 mL of 0.5% ropivacaine (200 mg; median 2.7 mg/kg) produced potentially toxic peak concentrations in 33% of patients. Current US labeling does not establish 3 mg/kg/200 mg as universal maxima and instead requires site/patient adjustment. | Do not release a TAP dosing card that normalizes dosing up to 3 mg/kg or 200 mg. A pharmacy and regional-anesthesia owner must select a lower, site-specific policy or otherwise define concentration/volume limits, patient modifiers, and cumulative dosing based on the institution's formulary and evidence. |
| `MAJOR` | `sections.indications`; `sections.shiftMode`; `sections.seniorPearls` | The senior pearl correctly says visceral pain is not blocked, but "appendicitis pain (pre-op)" is broader than the evidence. The best direct support reviewed is a 22-patient retrospective series; the randomized appendectomy evidence concerns postoperative balanced analgesia. A TAP block must not delay diagnostic reassessment, antibiotics, surgical care, or recognition of worsening visceral pathology. | Decide whether preoperative appendicitis pain remains an institution-specific adjunct indication, and state the diagnostic/surgical reassessment boundary and fallback analgesia. |
| `MAJOR` | `sections.positioning`; `sections.steps`; `sections.ultrasound`; `sections.troubleshooting` | The record teaches one midaxillary/lateral approach but labels the indication as generic postoperative abdominal pain. Original anatomical work differentiates lateral/posterior approaches for mainly infraumbilical surgery from subcostal approaches for upper/periumbilical incisions. A correct plane alone does not ensure incision-matched coverage. | Scope the card to the lateral/midaxillary TAP distribution or add separately reviewed approach selection; define how incision location and desired dermatomes determine the approach. |
| `MAJOR` | `sections.contraindications` | "Therapeutic anticoagulation or significant coagulopathy (deep fascial plane)" misclassifies TAP against ESAIC/ESRA 2022, which places TAP among superficial nerve procedures and permits superficial blocks in the presence of antithrombotic drugs. ASRA 2025 calls for site compressibility, vascularity, and consequences-of-bleeding assessment for non-deep techniques. Therapeutic anticoagulation may still change an individual decision, but is not a universal contraindication on this evidence. | Replace the "deep fascial plane" rationale with an institution-approved individualized bleeding-risk statement and drug-specific policy; avoid unnecessary interruption that creates thrombotic risk. |
| `MAJOR` | `sections.equipment` | The 80-100 mm needle and linear/curvilinear probe are plausible, but the list omits sterile prep/gloves/drape, disinfected probe with sterile cover and gel, syringes/labels, IV access, monitoring, and immediate airway/resuscitation/LAST resources. It also gives 20-30 mL per side without making the concentration-volume choice subordinate to a lower total-mg plan. | Define a complete setup and make total allowable milligrams, bilateral division, target depth, and body habitus determine concentration, volume, and needle length before medication is drawn. |
| `MAJOR` | `dosing.agents[bupivacaine]`; `sections.equipment` | The bupivacaine `2 mg/kg/175 mg` pair is also not a universal label-supported ceiling. The label allows adult peripheral-block doses up to 175 mg but requires individualization by site absorption, size, physical condition, and other factors. The current worked example is mathematically correct but can falsely imply that staying under the displayed number establishes safety. | Use a governed, agent- and TAP-specific policy and explicitly state that a calculated ceiling does not eliminate LAST risk. |
| `MAJOR` | `sections.confirmation`; `sections.troubleshooting`; `sections.complications`; `sections.aftercare`; `sections.documentation` | Imaging spread is described, but no clinical sensory/pain endpoint, onset window, partial/failed-block pathway, or rescue plan is given. Complications omit bleeding/hematoma, infection, vascular puncture, and block failure. Aftercare omits serial abdominal examination and injection-site assessment, which are material when the indication includes acute appendicitis. Documentation omits side(s), approach, concentration, total mg, cumulative prior dose, and antithrombotic decision. | Define clinical success/failure and rescue, serial abdominal reassessment for acute pathology, and the minimum bilateral procedure record. |
| `MAJOR` | `sections.references` | The generic references do not support lateral-versus-subcostal approach selection, appendicitis evidence strength, TAP pharmacokinetics, anticoagulation classification, or the universal dose ceilings. | Replace with direct primary/authoritative sources and an approved dosing policy. |

### Equipment, dosing, and monitoring assessment

The core three-layer anatomy, target plane, supine position, incremental injection, and linear spread confirmation are appropriate. The medication risk is not solved by correct arithmetic: both sides, skin local, prior blocks, and all amide local anesthetics must be included, and TAP absorption can produce high plasma levels below or at commonly quoted maximums. Continuous cardiac, oxygenation, ventilation/consciousness observation and at least 30 minutes after a potentially toxic dose are appropriate minimum concepts, but the 2010 TAP pharmacokinetic peak occurred at 30 minutes and mean concentrations remained elevated to 90 minutes; monitoring duration must be set by clinical policy and patient/dose risk rather than a universal 30-60 minute phrase.

No additional material discrepancy was identified in the basic muscle-layer anatomy, supine positioning, in-plane trajectory, or stated lack of visceral analgesia beyond the approach-selection and reassessment gaps above.

### Reviewer questions and proposed disposition

1. What TAP-specific ropivacaine and bupivacaine dosing policy will replace the universal maxima, especially for bilateral blocks?
2. Is this card limited to lateral/midaxillary TAP, and which operations/incisions are in scope?
3. Will preoperative appendicitis analgesia remain, and what serial examination/surgical escalation language is required?
4. How will the anticoagulation statement be reconciled with ESAIC/ESRA superficial-block classification and local policy?

**Proposed reviewer disposition:** withhold from release until the ropivacaine dosing ceiling is replaced by a qualified, TAP-specific policy and the major scope, anticoagulation, setup, and reassessment issues are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- ASRA-ESRA, [Standardizing nomenclature in regional anesthesia: abdominal wall, paraspinal, and chest wall blocks](https://doi.org/10.1136/rapm-2020-102451), 2021.
- Hebbard et al., [Ultrasound-guided transversus abdominis plane block](https://pubmed.ncbi.nlm.nih.gov/18020088/), 2007 original ultrasound description.
- Hebbard et al., [Continuous oblique subcostal TAP blockade: anatomy and clinical technique](https://pubmed.ncbi.nlm.nih.gov/20830871/), 2010.
- Niraj et al., [TAP block in open appendicectomy](https://pubmed.ncbi.nlm.nih.gov/19561014/), 2009 randomized trial.
- Ozciftci et al., [Preoperative TAP block in acute appendicitis pain](https://pubmed.ncbi.nlm.nih.gov/35179754/), 2022 retrospective study.
- Griffiths et al., [Plasma ropivacaine concentrations after ultrasound-guided TAP block](https://pubmed.ncbi.nlm.nih.gov/20861094/), 2010 pharmacokinetic study.
- Torup et al., [Potentially toxic ropivacaine concentrations after bilateral TAP blocks](https://pubmed.ncbi.nlm.nih.gov/22450529/), 2012 pharmacokinetic study.
- ESAIC/ESRA, [Regional anaesthesia in patients on antithrombotic drugs](https://esaic.org/wp-content/uploads/2023/12/regional_anaesthesia_in_patients_on_antithrom.pdf), 2022.
- ASRA Pain Medicine, [Regional anesthesia in the patient receiving antithrombotic or thrombolytic therapy, fifth edition](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766), 2025.
- DailyMed, [Bupivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ffecf450-1f01-4721-8e10-251385852612), revised 2023; [Ropivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3d465e02-fd09-41b8-847f-bfe99cb4a712), revised 2025.
- ASRA Pain Medicine, [Third Practice Advisory on LAST](https://rapm.bmj.com/content/43/2/113), 2018; [LAST checklist](https://asra.com/news-publications/asra-updates/blog-landing/guidelines/2020/11/01/checklist-for-treatment-of-local-anesthetic-systemic-toxicity), 2020.

## `block_pecs` - PECS I / II Block

**Screening disposition: `MINOR`.** Re-screened 2026-07-31 after owner adjudication; originally STOP-SHIP against the audited snapshot. The findings are addressed in `4ea632d` by the shared safety spine and the per-block corrections recorded in the owner adjudication section at the top of this report. Pending artwork stopped being release-gating on 2026-07-30 by owner decision. MINOR rather than no-material-discrepancy because needle length is still a range rather than a measured depth, fascial-plane coverage is expected rather than guaranteed, and paediatric scope is deferred. This is a discrepancy-screen result, not clinical approval; `reviewerStatus` is unchanged. Original screening rationale: **STOP-SHIP.** because the PECS II step permits an "or ribs" endpoint that is not the consensus pectoserratus target and can direct the needle through serratus toward an unintended deeper chest-wall plane near the pleura. The listed indications and asserted anterior-chest coverage also exceed the strongest evidence reviewed.

### Source-standard summary

The 2021 ASRA-ESRA consensus defines the interpectoral plane block (PECS I) between pectoralis major and minor and the pectoserratus plane block (the second component of original PECS II) between pectoralis minor and serratus anterior. The original 2012 PECS II description used 10 mL interpectoral plus 20 mL pectoserratus and was developed primarily for breast/axillary surgery. Randomized trials support perioperative breast-surgery analgesia, but a 2020 randomized study found PECS II alone did not produce anterior-chest sensory block and may miss medial breast/nipple-areolar coverage. Evidence reviewed for anterior rib fractures, breast-abscess incision/drainage, and pectoral tears was not sufficient to treat these as universally established indications or complete procedural anesthesia.

### Findings

| Level | Exact JSON location | Discrepancy and evidence | Clinician decision required |
|---|---|---|---|
| `STOP-SHIP` | `sections.steps` - PECS II target; related `sections.seniorPearls` | The step says to inject between pectoralis minor and serratus anterior "(or ribs)." ASRA-ESRA consensus places the pectoserratus target strictly between pectoralis minor and serratus anterior. A rib endpoint after passing through serratus is a different, deeper chest-wall plane; the same record warns that pleura is nearby. | Remove the alternative rib endpoint and have a regional-anesthesia clinician specify the exact pectoserratus endpoint, hydrodissection, needle-tip visibility, and stop rule before pleural/intercostal structures are approached. |
| `MAJOR` | `sections.indications`; `sections.shiftMode` | The card omits the best-supported use, breast/axillary surgical analgesia, while listing anterior rib fractures, breast-abscess I&D, and pectoral tears without evidence qualification. A PECS block should not be presented as complete procedural anesthesia for abscess drainage or as reliable medial/anterior rib analgesia without a tested sensory endpoint and fallback. | Define the intended ED versus perioperative scope, label evidence strength, and state whether each use is adjunct analgesia or procedural anesthesia requiring supplemental local anesthesia/sedation. |
| `MAJOR` | `sections.shiftMode`; `sections.confirmation`; `sections.aftercare` | "Provides analgesia to the anterior chest wall and axilla" is too broad. PECS II predominantly covers upper anterolateral/lateral chest and axillary structures; a 2020 randomized trial found no anterior-chest sensory block from PECS II alone and better medial coverage after adding a parasternal technique. Ultrasound layer separation confirms delivery, not clinical coverage. | Narrow the expected distribution and require mapped sensory/pain reassessment before relying on the block for an anterior or medial procedure. |
| `MAJOR` | `sections.anatomy`; `sections.ultrasound`; `sections.troubleshooting` | Color Doppler for the pectoral branch of the thoracoacromial artery is appropriate, but the record does not identify other vascular structures or define what to do when the artery, serratus, rib, intercostal layers, and pleura cannot all be distinguished. "Pectoralis minor and serratus anterior (or ribs)" is repeated conceptually in the technique. | Define mandatory structures, vascular avoidance, and an abort/reposition rule; align all anatomy and ultrasound wording with interpectoral plus pectoserratus planes. |
| `MAJOR` | `sections.contraindications` | Patient refusal/inability to consent, antithrombotic/coagulopathy assessment, altered anatomy, and inability to monitor bleeding are absent. ESAIC/ESRA 2022 categorizes interpectoral and pectoserratus blocks as superficial nerve procedures, but reports hematomas and requires assessment/monitoring of bleeding consequences. ASRA 2025 uses compressibility, vascularity, and consequence for non-deep peripheral blocks. | Adopt an institution-approved bleeding-risk screen and monitoring plan without automatically applying neuraxial interruption intervals. |
| `MAJOR` | `sections.equipment` | The transducer and 21G-22G, 50-100 mm needle range are plausible but incomplete. Sterile prep/gloves/drape, disinfected probe with sterile cover/gel, syringes/labels, IV access, monitors, and immediate airway/resuscitation/LAST resources are omitted. The total planned two-plane volume is not made subordinate to a total-mg calculation before draw-up. | Define the complete setup, depth-based needle selection, and a pre-draw calculation for all planes and both sides. |
| `MAJOR` | `dosing.agents`; `dosing.workedExample`; `sections.equipment`; `sections.steps` | The 10 mL plus 15-20 mL split is consistent with the scale of the original PECS II description, and the bilateral bupivacaine arithmetic/cumulative warning are useful. The universal bupivacaine `2 mg/kg/175 mg` and ropivacaine `3 mg/kg/200 mg` ceilings are not established as such by current US labels. The ropivacaine label instead uses site-specific ranges and a 250 mg nerve-block MRHD; "0.25% ropivacaine" requires a defined preparation. | Use a pharmacy/clinical-owner-approved dose policy by site, patient, total planes, laterality, and prior local anesthetic; approve or remove the 0.25% ropivacaine preparation. |
| `MAJOR` | `sections.troubleshooting`; `sections.complications`; `sections.aftercare`; `sections.documentation` | Troubleshooting only addresses one vessel. There is no partial/failed-block pathway, onset window, mapped clinical endpoint, rescue analgesia, or local hematoma check. Complications omit bleeding/hematoma, infection, nerve injury, and block failure. Documentation omits side, both targets, concentration, total mg, cumulative prior dose, needle approach, vascular survey, and antithrombotic decision. | Define clinical success/failure, rescue, site monitoring, and minimum documentation for each plane and side. |
| `MAJOR` | `sections.references` | Generic emergency-medicine literature, a LAST advisory, and NYSORA do not support the target, indications, coverage, two-plane volumes, anticoagulation classification, or universal dose ceilings. | Add the original descriptions, current nomenclature consensus, indication-specific trials, current antithrombotic/infection guidance, drug labels, and local dosing policy. |

### Equipment, dosing, and monitoring assessment

The original PECS II two-injection concept is recognizable, and Doppler use is a strength. The alternative rib endpoint must be removed before use. Total dose must include both planes, both sides, skin local, prior blocks, and any additional local anesthetic. Incremental injection and continuous monitoring through at least 30 minutes after a potentially toxic dose are appropriate, but immediate IV access, airway/resuscitation equipment, 20% lipid/LAST checklist, trained help, and clinical sensory/pain reassessment must be operational rather than implicit.

No additional material discrepancy was identified in supine positioning, 90-degree arm abduction when tolerated, basic pectoral muscle relationships, or the documented need to record volume in each plane beyond the target, coverage, and completeness issues above.

### Reviewer questions and proposed disposition

1. Will the PECS II target be limited to the pectoserratus plane with the "or ribs" endpoint removed?
2. Which indications are approved, and is the card for adjunct analgesia or procedural anesthesia in each case?
3. How will medial/anterior coverage limitations and failed-block rescue be made explicit?
4. Which cumulative dosing, bleeding-risk, asepsis, monitoring, and LAST-readiness policies govern two-plane and bilateral use?

**Proposed reviewer disposition:** withhold from release until the wrong-plane alternative is removed and the major indication, coverage, dosing, setup, and failure-plan gaps are resolved. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

### Primary/authoritative sources

- ASRA-ESRA, [Standardizing nomenclature in regional anesthesia: abdominal wall, paraspinal, and chest wall blocks](https://doi.org/10.1136/rapm-2020-102451), 2021.
- Blanco, [The 'pecs block': a novel technique for providing analgesia after breast surgery](https://doi.org/10.1111/j.1365-2044.2011.06838.x), 2011 original description.
- Blanco et al., [Ultrasound description of Pecs II (modified Pecs I)](https://doi.org/10.1016/j.redar.2012.07.003), 2012 original description.
- Kulhari et al., [Pectoral nerve block versus thoracic paravertebral block after radical mastectomy](https://pubmed.ncbi.nlm.nih.gov/27543533/), 2016 randomized trial.
- Abu Elyazed et al., [Pecto-intercostal fascial block combined with PECS II in modified radical mastectomy](https://pubmed.ncbi.nlm.nih.gov/32967391/), 2020 randomized trial.
- ESAIC/ESRA, [Regional anaesthesia in patients on antithrombotic drugs](https://esaic.org/wp-content/uploads/2023/12/regional_anaesthesia_in_patients_on_antithrom.pdf), 2022.
- ASRA Pain Medicine, [Regional anesthesia in the patient receiving antithrombotic or thrombolytic therapy, fifth edition](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766), 2025.
- ASRA Pain Medicine, [Consensus practice infection control guidelines](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651), 2025.
- DailyMed, [Bupivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ffecf450-1f01-4721-8e10-251385852612), revised 2023; [Ropivacaine hydrochloride injection label](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3d465e02-fd09-41b8-847f-bfe99cb4a712), revised 2025.
- ASRA Pain Medicine, [Third Practice Advisory on LAST](https://rapm.bmj.com/content/43/2/113), 2018; [LAST checklist](https://asra.com/news-publications/asra-updates/blog-landing/guidelines/2020/11/01/checklist-for-treatment-of-local-anesthetic-systemic-toxicity), 2020.

## Cross-cutting sources and limitations

- ASRA Pain Medicine's [Checklist for Performing Regional Nerve Blocks](https://asra.com/docs/default-source/guidelines-articles/195-full.pdf?sfvrsn=ee6a1d4e_2), 2014, supports immediate access to airway devices, suction, vasoactive drugs, and lipid emulsion.
- The current bupivacaine label directs careful and constant monitoring of cardiovascular/respiratory vital signs and consciousness after injection, use of the lowest effective individualized dose, and recognition that local-anesthetic toxicities are additive. The current ropivacaine label likewise requires fractional dosing, lowest effective dose, and careful monitoring. Neither label validates the shared JSON dose pairs as universal safe ceilings for all four blocks.
- The labels also create an age/special-population dependency not stated in these records: bupivacaine is not recommended under age 12; ropivacaine safety/efficacy is not established in pediatric patients; hepatic, renal, geriatric, pregnancy, and interacting-drug factors can alter risk. The assigned records are not tagged `Peds`, so this audit did not design a pediatric pathway, but a qualified reviewer should ensure the app cannot imply pediatric applicability.
- I found no newer ASRA LAST practice advisory than the 2018 executive summary or newer official treatment checklist than the 2020 checklist. The 2025 ASRA anticoagulation guideline was available online; its recommendations for non-deep peripheral techniques remain site- and consequence-based. The 2022 ESAIC/ESRA block table is not absolute and expressly allows institutional/technique/operator variation after individual risk-benefit analysis.
- Original fascial-plane descriptions and small trials do not prove universal dermatomal coverage, safety, optimal volume, or effectiveness for every listed ED indication. Several indication searches yielded only case reports, small retrospective cohorts, or no direct primary evidence; those uses are labeled `INSUFFICIENT EVIDENCE` within the relevant `MAJOR` scope findings rather than treated as disproven.
- Structural validation was not run because no JSON, schema, validator, or application file was changed. No iOS/Xcode/runtime behavior was assessed. Clinical correctness still requires expert review of the exact content version.

## Changed file

- `docs/audits/procedure-verification/07_REGIONAL_TRUNK.md`

`reviewerStatus` was not modified for any assigned procedure.
