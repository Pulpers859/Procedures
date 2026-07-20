# Procedure Verification Lane 09: Distal and Craniofacial Regional Blocks

## Audit boundary

- AI-assisted evidence and discrepancy screen only. I am not a licensed clinical reviewer, and this report does not approve content.
- Assigned records: `block_superficial_peroneal`, `block_deep_peroneal`, `block_supraorbital`, `block_infraorbital`, `block_mental`, `block_inferior_alveolar`, `block_superior_alveolar`, and `block_auricular`.
- Before review, `Procedures/Resources/procedures.json` SHA-256 was confirmed as `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`.
- I screened all metadata, every section, equipment/instruments, and every structured dosing field. Unmentioned fields had no additional material discrepancy in the sources reviewed.
- All eight records remain `reviewerStatus: "Needs Clinical Review"`. No reviewer status or clinical-content file was changed.
- **MINOR metadata:** all eight records use `reviewTime: "standard"`, which is not one of the values listed in `PROCEDURE_SCHEMA.md`, and all use `icon: "lungs"`. The schema/UI owner should resolve these without changing the clinical disposition.

## Cross-cutting source standards and findings

- ACEP's current distal-leg block guides use a high-frequency linear probe, sterile probe cover, a visible in-plane needle tip, test aliquots, and incremental injection. They describe typical ultrasound-guided volumes of 3-5 mL for both superficial and deep peroneal blocks. [ACEP Sonoguide, *Superficial Peroneal Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/superficial-peroneal-nb) and [ACEP Sonoguide, *Deep Peroneal Nerve Block*, 2025](https://www.acep.org/sonoguide/nerve-blocks/deep-peroneal-nerve-block)
- ASRA's infection-control guideline calls for chlorhexidine-alcohol skin preparation with drying, sterile gloves, sterile gel, and a single-use sterile probe cover for ultrasound-guided regional anesthesia. The two peroneal records do not contain this setup. [ASRA, *Consensus Practice Infection Control Guidelines*, 2025](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651)
- The current plain-lidocaine label supports 4.5 mg/kg and generally no more than 300 mg in a normal healthy adult. The current dental lidocaine-with-epinephrine label supports 7 mg/kg and no more than 500 mg in a normal healthy adult, but the dental product is 2% in a 1.7 mL cartridge (34 mg), not an unspecified 1%/2% vial-cartridge equivalent. [FDA/DailyMed, *Xylocaine MPF Prescribing Information*, current label accessed 2026](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d5e0d06f-ba1e-44d4-aa89-39d6c146dc23) and [FDA/DailyMed, *Xylocaine Dental with Epinephrine Prescribing Information*, updated 2024](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=14b55cf9-f7cd-4bb4-a7c5-aba61abadef1)
- The current general bupivacaine label gives an adult plain-drug ceiling of 175 mg for local infiltration/peripheral block but requires patient- and site-specific individualization; it does not establish the JSON's universal 2 mg/kg rule. The dental bupivacaine product is 0.5% with epinephrine 1:200,000 in a 1.8 mL cartridge, usually 9 mg per injection site, with a 90 mg adult dental-sitting limit, and is not recommended for children. [FDA/DailyMed, *Bupivacaine Hydrochloride Injection Prescribing Information*, current label accessed 2026](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c4071146-7d89-4c3a-9278-389d801cf66d&type=display) and [FDA/DailyMed, *Marcaine Dental with Epinephrine Prescribing Information*, revised 2020/currently posted](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=3e196aa4-0b01-44db-9267-98a995b54743)
- **MAJOR dosing logic across all eight records:** `cumulativeWarning` says all local anesthetic "shares one maximum." ASRA describes local-anesthetic toxicity as additive, but different agents do not literally share one mg or mg/kg ceiling. A clinician/pharmacist must specify the approved mixed-agent calculation or prohibit mixing. [ASRA, *Third Practice Advisory on LAST*, 2018](https://rapm.bmj.com/content/43/2/113) and [ASRA, *LAST Checklist*, 2020](https://asra.com/docs/default-source/guidelines-articles/local-anesthetic-systemic-toxicity-rgb.pdf?sfvrsn=33b348e_2)
- **MAJOR dosing logic in three records:** the worked examples for `block_superficial_peroneal`, `block_deep_peroneal`, and `block_auricular` state that 4.5 mg/kg gives a 315 mg maximum at 70 kg, despite each record's 300 mg absolute ceiling. The bedside example must explicitly apply the lower applicable limit, which is 300 mg in that example.
- `dosing.monitoring` links to the existing LAST rescue card and appropriately calls for dose calculation, aspiration, ECG/pulse oximetry, and knowing the location of 20% lipid emulsion. However, the fixed "at least 30 minutes" rule comes from ASRA for *potentially toxic doses*, not clearly for every low-volume block. For head/neck injection, current labels instead emphasize constant observation, circulation/respiration monitoring, and immediately available oxygen, resuscitation equipment, drugs, and trained personnel. The JSON omits BP, patient consciousness, oxygen/airway equipment, and the rest of that operational setup. The reviewer should label the fixed duration as institutional policy or replace it with a dose/site/risk-specific standard. The generic 3-5 mL increment is also too coarse to create repeat-aspiration opportunities when the entire block is only 1-5 mL; dental labels call for slow injection and frequent aspiration. [FDA/DailyMed Xylocaine Dental label, 2024](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=14b55cf9-f7cd-4bb4-a7c5-aba61abadef1); [ASRA LAST advisory, 2018](https://rapm.bmj.com/content/43/2/113)
- Pediatric dosing is not safely derivable from the adult fields. AAPD uses a more conservative pediatric dental lidocaine limit of 4.4 mg/kg, advises a 30% amide-dose reduction in infants younger than 6 months, does not recommend bupivacaine below age 12, and requires sedative/CNS-depressant dose adjustment. Pregnancy, hepatic/cardiac disease, sulfite sensitivity, epinephrine interactions, and patient-specific vascular risk likewise require product- and patient-specific review. [AAPD, *Use of Local Anesthesia for Pediatric Dental Patients*, latest revision 2023, published in the 2025 Reference Manual](https://www.aapd.org/globalassets/media/policies_guidelines/bp_localanesthesia25.pdf)
- Every assigned `sections.references` array begins with the untraceable phrase "Standard emergency medicine regional anesthesia literature" and otherwise cites ASRA/NYSORA generically. Those references cannot support the procedure-specific anatomy, depth, direction, volume, cartridge formulation, or epinephrine claims. NYSORA was used only for orientation and was not sole support for a substantive finding.

## `block_superficial_peroneal` - Superficial Peroneal Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** ACEP describes the nerve between fibularis brevis and extensor digitorum longus in the mid-lower leg, with distal perforating branches that become difficult to see near the ankle. It recommends tracing the nerve from proximal, keeping the tip visible in-plane, testing with 0.5 mL, then injecting in 1 mL increments to a typical total of 3-5 mL. Proximal blocks may cause weakness. [ACEP Sonoguide, 2025](https://www.acep.org/sonoguide/nerve-blocks/superficial-peroneal-nb); [Canella et al., original sonographic anatomy study, 2009](https://pubmed.ncbi.nlm.nih.gov/19542411/)

**Findings.**

- `sections.steps` starts at the anterolateral distal leg and says only to identify the nerve as it exits fascia, although the source warns that the distal branches can be hard to visualize and recommends proximal tracing. The ultrasound and landmark techniques need separate target, volume, and failure paths.
- `sections.equipment` and `steps` prescribe 5-10 mL for the ultrasound-guided injection, while ACEP gives 3-5 mL. Ten mL may be a field-block volume, but the current text applies it directly around an identified nerve without a lowest-effective-dose rationale.
- The technique omits sterile preparation, in-plane/out-of-plane choice, continuous tip visualization, test aliquot, visible circumferential spread, and stop rules for pain, paresthesia, high pressure, nerve swelling, or absent ultrasound spread. `ultrasound` uses the imprecise phrase "pops through" rather than defining the fascial plane.
- `contraindications` omits refusal/inability to cooperate, preexisting neurologic deficit, compartment-syndrome surveillance, and a compressibility/antithrombotic assessment. ASRA says non-deep peripheral blocks should be assessed by compressibility, vascularity, and consequences of bleeding rather than a universal anticoagulant rule. [ASRA antithrombotic guideline, fifth edition, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766)
- `confirmation` gives only final numbness, with no baseline map, expected 15-20 minute onset, or failed-block decision. `complications` lists only intravascular injection and omits nerve injury/intraneural injection, hematoma, infection, LAST, and motor weakness if performed proximally. `aftercare` gives no numb-foot protection/fall advice. `documentation` omits side, technique, consent, time, dose in mg, and pre/post sensory-motor findings.
- Indication, broad distal sensory territory, supine positioning, and the landmark-field-block pearl are plausible, but distal sensory overlap means the exact wound area still requires testing.

**Equipment/instruments.** A linear probe and a 1.5-inch needle are plausible, but ACEP lists a 22-25G block needle and notes that smaller needles are harder to visualize; the unqualified 25-27G choice requires operator/credentialing review. The checklist lacks antiseptic, drying, sterile gloves, sterile cover/gel, syringe/flush, monitoring, oxygen/resuscitation equipment, and lipid rescue.

**Dosing/monitoring.** The plain-lidocaine fields match the adult label, but the 70 kg worked maximum must be capped at 300 mg. The 2 mg/kg bupivacaine rule lacks primary-label support even though 175 mg appears as an adult ceiling. Mixed-agent wording, patient-specific reductions, and the fixed observation rule need an approved policy.

**Reviewer question/proposed disposition.** Separate ultrasound and field-block paths; approve a technique-specific minimum volume and needle; add tip/spread/stop criteria, complete setup, clinical confirmation, and complications; and correct the lidocaine example and mixed-agent calculation. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_deep_peroneal` - Deep Peroneal Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** ACEP places the nerve near the anterior tibial artery just above the malleoli, usually lateral but sometimes anterior or medial. If the nerve is not visible, the artery may be used as the landmark for a carefully visualized perivascular injection. The standard uses in-plane tip visualization, 0.5 mL testing, 1 mL increments, aspiration, and 3-5 mL total. [ACEP Sonoguide, 2025](https://www.acep.org/sonoguide/nerve-blocks/deep-peroneal-nerve-block)

**Findings.**

- `sections.anatomy` presents a tendon relationship and `steps` says the nerve is "usually lateral" to the artery, but does not disclose the documented anterior/medial variants. `steps` then directs "inject 3-5 mL ... next to the artery" without requiring a visualized needle tip or visible extravascular spread. In this vascular target, that wording is too ambiguous for bedside use.
- Color Doppler and aspiration appear only in `troubleshooting`; they are core pre-injection safeguards. The record also omits a test aliquot, small incremental injections, stop rules, and action when no ultrasound bolus appears.
- `contraindications`, `confirmation`, `complications`, `aftercare`, and `documentation` have the same thin neurologic/bleeding/LAST/protection content described for the superficial block. The first-web-space indication, supine position, 3-5 mL total, and general sensory target are otherwise consistent with ACEP.

**Equipment/instruments.** The high-frequency probe and 1.5-inch length are plausible. The unqualified 25-27G needle differs from ACEP's 22-25G block-needle range and may impair visualization. Sterile skin/probe supplies, syringe/flush, Doppler requirement, monitoring, oxygen/resuscitation equipment, and lipid rescue are absent.

**Dosing/monitoring.** The actual 5 mL of 1% lidocaine calculation is 50 mg, but the same worked example incorrectly calls 315 mg the 70 kg maximum instead of applying the 300 mg ceiling. The bupivacaine, mixed-agent, patient-specific, incremental-injection, and monitoring issues are otherwise the same as above.

**Reviewer question/proposed disposition.** Make vessel mapping and tip/spread visualization mandatory, define perivascular placement and failure/abandonment criteria, complete the setup and complication plan, and correct dosing logic. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_supraorbital` - Supraorbital Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** The supraorbital exit has wide positional variation and may be a notch or a foramen. Contemporary procedural guidance keeps injection superficial at the superior rim, explicitly prohibits entering the foramen, uses slow injection after aspiration, and protects the orbit/upper eyelid with a finger or gauze under the rim. [Webster et al., original cadaveric variation study, 2013](https://pubmed.ncbi.nlm.nih.gov/23299811/); [MSD Manual Professional, *How To Do an Ophthalmic Nerve Block*, reviewed 2026](https://www.msdmanuals.com/professional/injuries-poisoning/how-to-do-anesthesia-procedures/how-to-do-an-ophthalmic-nerve-block). MSD is secondary and was used with the primary anatomy study and federal labels, not alone.

**Findings.**

- `sections.steps` says to insert subcutaneously and aim medially over the notch, then advance farther toward the bridge of the nose for the supratrochlear nerve. It gives no insertion depth, orbital-rim shielding, explicit prohibition on entering the notch/foramen, stop rule for paresthesia/pain, or instruction never to direct/advance into the orbit. Those omissions are clinically important with an unqualified 1.5-inch needle adjacent to the globe.
- Volume is internally inconsistent: `equipment` says 3-5 mL, the ordered supraorbital plus supratrochlear deposits total 2-4 mL, and `workedExample` uses 5 mL. The clinician must approve one total and per-site volume.
- The pupil-line landmark is a useful approximation, not a reliable fixed location given wide variation. `confirmation` should map the actual repair field after onset. The eyebrow field-block rescue is plausible only if it remains superficial along the bony rim and includes the same orbital safeguards.
- `complications` omits globe/orbital injury, intraneural injection/neuropathy, infection, LAST, and block failure. `aftercare` addresses eyelid swelling but not ocular symptoms requiring reassessment. `documentation` should include side, technique, dose in mg, pre/post V1 and ocular findings, and complications. Position, listed indications, and pressure below the rim are otherwise plausible.
- The epinephrine pearl is pharmacologically plausible for hemostasis/prolongation, but the record presents epinephrine as the default without sulfite, cardiovascular, interaction, compromised-perfusion, or pregnancy cautions from the label. It needs patient-specific qualification rather than a universal claim.

**Equipment/instruments.** A 25-27G needle is plausible, but a 1.5-inch needle without a shallow-depth limit creates avoidable orbital risk. The list lacks syringe, antiseptic/PPE, gauze for rim protection, monitoring, and immediate oxygen/resuscitation/LAST setup.

**Dosing/monitoring.** Lidocaine-with-epinephrine 7 mg/kg/500 mg and plain lidocaine 4.5 mg/kg/300 mg are supportable adult label limits, and the arithmetic in this example stays below the ceilings. The equipment's "1% or 2%" does not identify whether a vial or 2% dental cartridge is intended. Mixed-agent, epinephrine-patient, small-increment, and observation rules need approval.

**Reviewer question/proposed disposition.** Specify a superficial needle depth/direction with rim shielding and explicit globe/foramen stop rules, reconcile volume, complete ocular rescue/aftercare and equipment, and qualify epinephrine by formulation and patient risk. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_infraorbital` - Infraorbital Nerve Block

**Screening disposition: STOP-SHIP**

**Source-standard summary.** Cadaver studies place the infraorbital foramen variably below the inferior orbital rim; soft-tissue landmarks are approximations. For an intraoral approach, contemporary technique maintains a palpating finger over the foramen, follows a controlled tooth-axis trajectory, defines an approximate adult depth, and warns that an overly shallow angle can pass too far and enter the orbit. Injection is adjacent to, not within, the foramen. [Aziz et al., original cadaver study, 2000](https://pubmed.ncbi.nlm.nih.gov/10981979/); [Ercikti et al., original soft-tissue landmark study, 2016](https://pubmed.ncbi.nlm.nih.gov/27146295/); [MSD Manual Professional, intraoral technique, reviewed 2026](https://www.msdmanuals.com/professional/dental-disorders/how-to-do-dental-procedures/how-to-do-an-infraorbital-nerve-block-intraoral)

**Findings.**

- `sections.steps` directs a 1.5-inch needle superiorly toward a palpating finger but gives no controlled angle, depth, requirement to maintain the protecting finger, or endpoint by palpable needle tip. "Stop before hitting the bone or entering the foramen" does not prevent an overly shallow trajectory from advancing toward/into the orbit. This is a plausible serious globe/orbital injury pathway and is STOP-SHIP until a credentialed reviewer supplies explicit trajectory, depth, shielding, and abandonment criteria.
- The anatomy statement "roughly 1 cm" and directly below the pupil is only an approximation; the original studies show meaningful variation. The canine/first-premolar entry differs from the reviewed contemporary second-premolar technique and should be reconciled by a dental/maxillofacial reviewer rather than silently normalized.
- `troubleshooting` correctly says not to enter the foramen but claims "severe pressure necrosis" without a traceable source and does not address orbital entry, hematoma, positive aspiration, paresthesia, loss of landmark, or failed coverage. `complications` omits orbital/globe injury, hematoma, infection spread, LAST, and failure.
- `aftercare` lacks upper-lip/cheek bite or thermal-injury precautions and urgent ocular return symptoms. `documentation` should include exact site/side, depth/approach, dose in mg, epinephrine ratio, pre/post sensory and ocular exam, and reaction. Indications, positioning, intraoral preference, and target sensory territory are otherwise plausible.

**Equipment/instruments.** The 25-27G size and 2-3 mL volume are plausible, but the list lacks a dental aspirating syringe or defined vial syringe, intraoral light, gauze/cotton applicators, suction, PPE/eye protection, and emergency equipment. The 1.5-inch length needs an explicit insertion-depth limit.

**Dosing/monitoring.** Adult lidocaine limits and worked arithmetic are supportable, but 1%/2% with epinephrine is formulation-ambiguous: the current cited dental cartridge is 2% and 1.7 mL. Topical benzocaine adds a separate methemoglobinemia/pediatric risk and is not included in cumulative dose/safety screening. Mixed-agent and head/neck monitoring issues remain.

**Reviewer question/proposed disposition.** A maxillofacial/dental or regional-anesthesia reviewer must define the exact entry, angle, depth, maintained finger guard, orbital stop/abandonment criteria, and rescue actions; then reconcile formulation and equipment. Keep `STOP-SHIP` until corrected. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_mental` - Mental Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** The mental foramen is most often at the second premolar or between premolars but varies by patient/population. Contemporary intraoral technique advances approximately 0.5-1 cm parallel to the teeth and injects 1-2 mL adjacent to, not into, the foramen. Midline lip/chin work may require bilateral blocks. [Afkhami et al., original radiographic localization study, 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC4025417/); [Laher et al., original ultrasound localization study, 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4963689/); [MSD Manual Professional, mental block technique, reviewed 2026](https://www.msdmanuals.com/professional/dental-disorders/how-to-do-dental-procedures/how-to-do-a-mental-nerve-block)

**Findings.**

- `sections.steps` uses a 1.5-inch needle directed inferiorly but gives no 0.5-1 cm depth limit, bevel orientation, or stop rule. `equipment` and `steps` use 2-3 mL, exceeding the 1-2 mL contemporary reference range without a rationale. The instruction not to hit bone/enter the foramen is useful but insufficient by itself.
- `anatomy` says the foramen is below the first or second premolar and aligned with the pupil/other foramina. Original studies show variable premolar relationships; the vertical-line heuristic should not substitute for palpation/ultrasound when landmarks are uncertain.
- `indications` includes lower-lip and chin lacerations but neither `steps`, `confirmation`, nor `troubleshooting` says that midline work may need bilateral blocks. Confirmation should map the actual wound field and preserve the distinction that a mental block does not anesthetize the teeth.
- `complications` omits hematoma, infection spread, LAST, block failure, and needle breakage. `aftercare` omits lip-biting/thermal injury. `documentation` omits side, total mg, epinephrine ratio, injection type, and pre/post sensory deficit. The "fastest, easiest, and least painful" pearl is an unsupported superlative.

**Equipment/instruments.** Needle gauge is plausible, but length needs a defined shallow insertion. The record lacks a dental aspirating/narrow-barrel syringe, intraoral light, gauze/cotton applicators, suction, PPE/eye protection, and immediate emergency setup.

**Dosing/monitoring.** Adult lidocaine limits and worked arithmetic are supportable. The formulation remains ambiguous between vial and dental cartridge, topical benzocaine safety is not integrated, and mixed-agent/head-and-neck monitoring issues remain.

**Reviewer question/proposed disposition.** Approve a specific depth and lowest effective volume, add bilateral-midline guidance, replace fixed alignment/superlative wording, and complete equipment, complications, aftercare, and formulation details. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_inferior_alveolar` - Inferior Alveolar Nerve Block

**Screening disposition: MAJOR**

**Source-standard summary.** Accepted technique uses the coronoid notch/pterygomandibular triangle, a contralateral-premolar syringe angle, bone contact at about 20-25 mm, slight withdrawal, aspiration, and slow injection. The lingual nerve is commonly anesthetized incidentally; buccal soft-tissue coverage may require a separate long-buccal injection. Dental products have cartridge-specific concentrations and limits. [AAPD, pediatric dental local-anesthesia best practice, latest revision 2023](https://www.aapd.org/globalassets/media/policies_guidelines/bp_localanesthesia25.pdf); [Merck Manual Professional, IANB technique, reviewed 2026](https://www.merckmanuals.com/professional/dental-disorders/how-to-do-dental-procedures/how-to-do-an-inferior-alveolar-nerve-block); [FDA/DailyMed Xylocaine Dental label, 2024](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=14b55cf9-f7cd-4bb4-a7c5-aba61abadef1)

**Findings.**

- The landmark, contralateral approach, 20-25 mm depth, bone-contact warning, and posterior/anterior redirection logic are broadly consistent with accepted technique. However, `steps` calls only for one aspiration before 1.5-2 mL and then deposits another 0.5 mL while withdrawing; current product guidance calls for slow injection with frequent aspiration in this vascular area.
- `steps` labels the withdrawal deposit as a lingual block but does not discuss separate long-buccal coverage. `confirmation` treats tongue numbness plus lip/tooth numbness as "profound" success, although soft-tissue signs do not by themselves prove pulpal anesthesia. The reviewer should define the intended ED endpoint and rescue for incomplete dental or buccal coverage.
- `equipment` mixes 2-3 mL of 0.5% bupivacaine, lidocaine, or articaine without naming epinephrine ratios, cartridge sizes, mg per cartridge, or whether vial products are intended. The structured agents list only *plain* bupivacaine and plain lidocaine, while the current dental bupivacaine product is 0.5% with epinephrine and the dental lidocaine/articaine products are cartridge formulations with epinephrine. Articaine is named in equipment but absent from structured dosing entirely.
- `seniorPearls` says 0.5% bupivacaine gives 12-24 hours of profound relief. The current dental Marcaine label advises that anesthesia may persist up to 7 hours; this claim is not supportable and could create false expectations or delay reassessment/definitive dental care.
- `contraindications` makes `Coagulopathy` absolute without medication-, site-, compressibility-, or severity-specific guidance. Infection in the needle path is relevant, but dental pain/abscess still needs explicit definitive-treatment and deep-space-infection screening. `complications` omits hematoma, persistent paresthesia/neuropathy, infection spread, LAST, and failed block.
- `aftercare` appropriately warns against chewing numb tissue and calls for dental follow-up. `documentation` appropriately includes bone contact and volume/type but should also include side, injection type, total mg/cartridges, epinephrine ratio, aspiration result, pre/post deficits, and reaction. The "gold standard" label is unnecessary and unreferenced.

**Equipment/instruments.** A 25-27G long dental needle is plausible; AAPD notes that lower gauge improves aspiration reliability and that inferior alveolar blocks account for most needle fractures, especially with 30G needles. The list lacks an aspirating dental syringe, defined cartridges, gauze/cotton applicators, suction, intraoral light, PPE/eye protection, and immediate oxygen/resuscitation/LAST setup.

**Dosing/monitoring.** The 3 mL of 0.25% bupivacaine calculation is 7.5 mg and the weight arithmetic is correct, but it does not match `equipment` (0.5%) or the labeled dental formulation (0.5% with epinephrine). The 175 mg general plain-bupivacaine ceiling is not the dental product's 90 mg sitting limit. Pediatric use, especially bupivacaine below age 12 and articaine below age 4, must be explicit. Mixed-agent and head/neck monitoring issues remain.

**Reviewer question/proposed disposition.** Select actual vial or dental-cartridge formulations and align equipment, agents, examples, and ceilings; remove or support the 12-24 hour claim; define aspiration cadence, coverage/failure rescue, anticoagulation handling, and definitive-care escalation. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_superior_alveolar` - Superior Alveolar Nerve Block (Supraperiosteal)

**Screening disposition: MAJOR**

**Source-standard summary.** Supraperiosteal infiltration deposits anesthetic near the target tooth apex and can be effective in the porous maxilla, but success depends on tooth, agent, volume, anatomy, and inflammatory/pulpal state. Randomized trials in symptomatic irreversible pulpitis do not support a universal 95% success claim or one rescue path. Dental labels use product-specific cartridges and lowest-effective dosing. [Aggarwal et al., randomized comparison in irreversible pulpitis, 2011](https://pubmed.ncbi.nlm.nih.gov/22000449/); [Hosseini et al., randomized maxillary-molar infiltration trial, 2016](https://pubmed.ncbi.nlm.nih.gov/27141212/); [FDA/DailyMed Marcaine Dental label, revised 2020/currently posted](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=3e196aa4-0b01-44db-9267-98a995b54743)

**Findings.**

- `seniorPearls` says local infiltration "works beautifully 95% of the time." The record supplies no source or population, and original trials show materially lower/variable success in inflamed maxillary molars. This unsupported precision should be removed or tied to a defined population and outcome.
- Product details conflict: `equipment` calls for 1-2 mL of 0.5% bupivacaine or lidocaine, while structured dosing lists plain agents and the example uses 2 mL of 0.25% bupivacaine. The current dental bupivacaine label instead specifies 0.5% with epinephrine, usually a 1.8 mL cartridge per site. Lidocaine concentration/epinephrine status is not stated.
- `steps` gives a plausible shallow supraperiosteal path and aspiration, but no slow-injection time, repeat aspiration, stop rule for paresthesia/high pressure, or exact tooth-apex confirmation. `confirmation` says tooth/gingiva numbness without distinguishing soft-tissue numbness from adequate pulpal anesthesia before a painful procedure.
- `troubleshooting` attributes failure to infection-related pH and recommends infraorbital or posterior superior alveolar block. That is one possible mechanism/path, but the rescue depends on tooth/root, palatal innervation, diagnosis, and definitive dental plan; the current instruction is too universal.
- `complications` omits hematoma, neuropathy, infection spread, LAST, failed anesthesia, and soft-tissue injury. `aftercare` says only dental follow-up and omits numb-tissue precautions and escalation for spreading infection. `documentation` should include tooth number, formulation/concentration, total mg/cartridges, epinephrine ratio, aspiration/reaction, and confirmation.
- Indications, seated/head-supported positioning, topical preparation, and non-use of ultrasound are otherwise plausible. The title should be reviewed for search clarity because the taught procedure is tooth-specific supraperiosteal infiltration rather than blockade of one named superior alveolar trunk.

**Equipment/instruments.** A short 25-27G dental needle and 1-2 mL are plausible, but "1 inch is fine" needs patient/technique qualification. The list lacks an aspirating dental syringe, defined cartridge or vial, gauze/cotton applicators, suction, light, PPE/eye protection, and emergency setup.

**Dosing/monitoring.** The worked arithmetic is correct but mismatched to equipment and product. The general 2 mg/kg/175 mg plain-bupivacaine fields do not govern the cited dental cartridge's 90 mg sitting limit. Pediatric, mixed-agent, topical-anesthetic, and head/neck monitoring issues remain.

**Reviewer question/proposed disposition.** Remove the universal 95% claim, select and align actual formulations/concentrations/cartridges, define tooth/root-specific confirmation and failure rescue, and complete aftercare, complications, documentation, and equipment. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## `block_auricular` - Auricular Block

**Screening disposition: MAJOR**

**Source-standard summary.** Human dissection shows heterogeneous, overlapping innervation from cranial and cervical nerves; a field/ring block may anesthetize most of the auricle but conchal/meatal coverage is variable. A large clinical series of more than 10,000 ear/nose procedures found no epinephrine-associated tissue or flap necrosis with specified dilute preparations, contradicting an absolute ear/cartilage prohibition. [Peuker and Filler, original human cadaver study, 2002](https://pubmed.ncbi.nlm.nih.gov/11835542/); [Hafner et al., original clinical series, 2005](https://pubmed.ncbi.nlm.nih.gov/16372813/); [Bermejo et al., original concha/canal anatomy study, 2017](https://pubmed.ncbi.nlm.nih.gov/28396871/)

**Findings.**

- `equipment`, `complications`, and `documentation` say epinephrine must not be used because it causes cartilage ischemia/necrosis. The reviewed clinical series does not support that categorical claim. This does not mean epinephrine is appropriate for every patient or wound; the reviewer must replace the myth-based absolute with a patient-, perfusion-, concentration-, and local-policy decision.
- `shiftMode` says the ring targets three named nerves and gives "complete" auricular anesthesia except concha/canal, while `anatomy` says it "blocks them all." Human anatomy shows heterogeneous overlap and additional vagal contribution. `confirmation` should require testing the exact operative field rather than promise complete pinna anesthesia.
- `steps` advances a 1.5-inch needle in four long subcutaneous tracks from two punctures but provides no depth/plane, maximum advancement, aspiration cadence, incremental volume per track, or vessel/nerve stop rule. The nearby superficial temporal and posterior auricular vessels and variable nerve paths make those omissions important.
- `troubleshooting` recommends a local conchal wheal without volume, depth, canal/vascular precautions, or escalation if vagal stimulation, pain, or incomplete anesthesia occurs. This separate deeper/medial target needs an evidence-backed clinician decision rather than an informal rescue sentence.
- `complications` omits hematoma, nerve injury, infection, LAST, block failure, and needle injury. `aftercare` appropriately mentions wound care/compression for hematoma but should include protection of numb tissue and reassessment of perfusion/hematoma. `documentation` should record side, technique, total mg, concentration, epinephrine ratio if used, field testing, and complications.
- Indications and seated/lateral positioning are plausible. The pearl favoring a long needle to reduce skin punctures does not address the tradeoff of a longer unvisualized track and needs clinician approval.

**Equipment/instruments.** A 25-27G needle and 5-10 mL total are plausible for a field block, but the unqualified 1.5-inch length plus long tracking needs depth limits. The list lacks syringe, antiseptic/PPE, gauze, monitoring, and immediate oxygen/resuscitation/LAST setup.

**Dosing/monitoring.** Ten mL of 1% lidocaine is correctly 100 mg, but the worked example again fails to cap the 70 kg maximum at 300 mg. Plain bupivacaine 2 mg/kg is not established by the current primary label even though 175 mg is an adult ceiling. Mixed-agent and fixed-monitoring rules require approval.

**Reviewer question/proposed disposition.** Remove the categorical epinephrine-necrosis claim, define field-block plane/depth/aliquots and target-specific testing, decide whether/how conchal rescue is taught, complete complications/equipment, and correct dosing logic. Keep `MAJOR`. `reviewerStatus` remains unchanged (`Needs Clinical Review`).

## Sources and limitations

Additional authoritative sources used across the lane were [ASRA, antithrombotic guideline, fifth edition, 2025](https://rapm.bmj.com/content/early/2025/09/16/rapm-2024-105766), [ASRA, infection-control guideline, 2025](https://rapm.bmj.com/content/early/2025/01/14/rapm-2024-105651), [ASRA, LAST checklist, 2020](https://asra.com/docs/default-source/guidelines-articles/local-anesthetic-systemic-toxicity-rgb.pdf?sfvrsn=33b348e_2), [FDA/DailyMed, Articaine with Epinephrine label, current label accessed 2026](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=60d11ba2-e9e0-4f0a-bdfc-3bc49006c2df), and [FDA/DailyMed, general bupivacaine label, current label accessed 2026](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c4071146-7d89-4c3a-9278-389d801cf66d&type=display). Secondary procedural manuals were used only to orient technique comparison and were paired with primary anatomy studies, specialty guidance, or manufacturer labels.

Limitations: this was a source-and-discrepancy screen, not a systematic review or clinical validation. Technique evidence is uneven, anatomy varies, and product availability differs by institution. Pediatric, pregnancy, hepatic/cardiac disease, sulfite/epinephrine interactions, infection, sedation, antithrombotic therapy, body habitus, credentialing, monitoring, and emergency-readiness decisions remain clinician- and institution-specific. `python scripts/validate_procedures.py` completed in authoring mode with 0 blockers and 144 total existing issues; its assigned-record warnings about thin equipment, complication, documentation, Shift Mode, step, and troubleshooting sections are reflected above. Structural validation cannot prove clinical correctness. Qualified emergency-medicine, regional-anesthesia, dental/maxillofacial, ophthalmic-risk, pharmacy, infection-control, and institutional-policy review is required. No procedure is approved by this report, and every `reviewerStatus` remains unchanged.

Changed file: `docs/audits/procedure-verification/09_REGIONAL_DISTAL_CRANIOFACIAL.md` only.
