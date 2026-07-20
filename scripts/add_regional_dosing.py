#!/usr/bin/env python3
"""Inject structured max-dose (dosing) data into every Regional Anesthesia
procedure and repair dosing-unsafe prose found in the 2026-07 clinical audit.

Provenance: this script IS the record of how the dosing layer was generated.
All numbers are conventional maximums as published in the cited sources
(ASRA 2018 practice advisory; NYSORA local-anesthetic pharmacology chapter)
and every touched item remains reviewerStatus "Needs Clinical Review" —
nothing here is clinically approved until a qualified reviewer signs off.

Run from the repo root:
    python scripts/add_regional_dosing.py
The script is idempotent and fails loudly if an expected text target is
missing, so silent drift cannot masquerade as success.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"

RESCUE_CARD_ID = "local_anesthetic_systemic_toxicity"

DOSING_REFERENCES = [
    "Neal JM et al. ASRA Practice Advisory on Local Anesthetic Systemic Toxicity. Reg Anesth Pain Med. 2018.",
    "NYSORA. Clinical Pharmacology of Local Anesthetics (maximum recommended doses). nysora.com.",
]

# Conventional maximums per the references above. Values are deliberately the
# conservative, widely taught numbers; institutional policy overrides.
AGENTS = {
    "bupi": {
        "agent": "Bupivacaine (plain)",
        "concentrationNote": "0.25% = 2.5 mg/mL; 0.5% = 5 mg/mL",
        "maxDoseMgPerKg": 2.0,
        "absoluteMaxMg": 175,
    },
    "ropi": {
        "agent": "Ropivacaine (plain)",
        "concentrationNote": "0.2% = 2 mg/mL; 0.5% = 5 mg/mL",
        "maxDoseMgPerKg": 3.0,
        "absoluteMaxMg": 200,
    },
    "lido": {
        "agent": "Lidocaine (plain)",
        "concentrationNote": "1% = 10 mg/mL; 2% = 20 mg/mL",
        "maxDoseMgPerKg": 4.5,
        "absoluteMaxMg": 300,
    },
    "lido_epi": {
        "agent": "Lidocaine with epinephrine",
        "concentrationNote": "1% = 10 mg/mL; 2% = 20 mg/mL",
        "maxDoseMgPerKg": 7.0,
        "absoluteMaxMg": 500,
    },
}

CUMULATIVE_WARNING = (
    "All local anesthetic given this encounter shares one maximum: skin wheals, "
    "wound infiltration, prior blocks, and both sides of a bilateral block count "
    "together. Recalculate the remaining allowance before every additional dose."
)

MONITORING = [
    "Weigh or estimate the patient and calculate the maximum dose in mg AND mL before drawing up — say it out loud.",
    "Continuous cardiac monitoring and pulse oximetry from before injection through at least 30 minutes after.",
    "Confirm where 20% lipid emulsion is stocked before injecting — do not start without a LAST plan.",
    "Aspirate before injecting and give the dose in 3-5 mL increments with repeat aspiration.",
]

# Per-block agent sets and the typical volume (mL) used for the worked example.
# Volumes mirror each block's own equipment text.
BLOCKS = {
    "digital_nerve_block":               (["lido", "bupi"], 4),
    "fascia_iliaca_block":               (["ropi", "bupi"], 40),
    "block_interscalene":                (["bupi", "ropi"], 15),
    "block_supraclavicular":             (["bupi", "ropi"], 20),
    "block_raptir":                      (["bupi", "ropi"], 30),
    "block_radial_nerve":                (["lido", "bupi"], 10),
    "block_median_nerve":                (["lido", "bupi"], 10),
    "block_ulnar_nerve":                 (["lido", "bupi"], 10),
    "block_superficial_cervical_plexus": (["lido", "bupi"], 10),
    "block_serratus_anterior":           (["bupi", "ropi"], 30),
    "block_thoracic_esp":                (["bupi", "ropi"], 30),
    "block_tap":                         (["bupi", "ropi"], 30),
    "block_pecs":                        (["bupi", "ropi"], 30),
    "block_femoral_nerve":               (["bupi"], 20),
    "block_peng":                        (["bupi"], 30),
    "block_saphenous_nerve":             (["lido", "bupi"], 15),
    "block_popliteal_sciatic":           (["bupi", "ropi"], 30),
    "block_transgluteal_sciatic":        (["bupi", "ropi"], 30),
    "block_tibial_nerve":                (["lido", "bupi"], 10),
    "block_sural_nerve":                 (["lido", "bupi"], 5),
    "block_superficial_peroneal":        (["lido", "bupi"], 10),
    "block_deep_peroneal":               (["lido", "bupi"], 5),
    "block_supraorbital":                (["lido_epi", "lido"], 5),
    "block_infraorbital":                (["lido_epi", "lido"], 3),
    "block_mental":                      (["lido_epi", "lido"], 3),
    "block_inferior_alveolar":           (["bupi", "lido"], 3),
    "block_superior_alveolar":           (["bupi", "lido"], 2),
    "block_auricular":                   (["lido", "bupi"], 10),
}

# Blocks whose worked example must call out the bilateral trap explicitly.
BILATERAL_BLOCKS = {"block_tap", "block_pecs", "block_serratus_anterior", "block_thoracic_esp"}

# Prose repairs from the 2026-07 audit: (procedure id, section, exact old
# string) -> new string. The script fails if a target is missing so a silent
# content change elsewhere cannot hide a skipped safety fix.
TEXT_FIXES = [
    (
        "block_tap", "equipment",
        "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine or ropivacaine per side)",
        "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine or ropivacaine per side; "
        "for bilateral blocks the two sides share ONE weight-based maximum — dilute or reduce "
        "volume so the combined total stays under it)",
    ),
    (
        "block_tap", "steps",
        "Aspirate, then inject 20-30 mL of anesthetic.",
        "Aspirate, then inject 20-30 mL of anesthetic in 3-5 mL increments with repeat aspiration, "
        "staying under the calculated maximum dose.",
    ),
    (
        "block_interscalene", "steps",
        "Apply cardiac monitoring if using large volumes, and ensure intralipid is available.",
        "Apply continuous cardiac monitoring and pulse oximetry, and confirm lipid emulsion "
        "availability, before injecting any volume.",
    ),
]

# Contraindication additions from the audit (appended if not already present).
CONTRAINDICATION_ADDITIONS = {
    "block_tap": [
        "Therapeutic anticoagulation or significant coagulopathy (deep fascial plane; weigh risk/benefit and local policy)",
        "Bilateral block without a recalculated combined maximum dose (both sides share one limit)",
    ],
    "block_femoral_nerve": [
        "Prior femoral vascular surgery or graft at the injection site",
        "Therapeutic anticoagulation or significant coagulopathy (weigh risk/benefit and local policy)",
    ],
    "block_popliteal_sciatic": [
        "Injury at risk for compartment syndrome (e.g., tibial fracture) — the block can mask ischemic pain; discuss with the surgical team first",
    ],
    "block_transgluteal_sciatic": [
        "Injury at risk for compartment syndrome — the block can mask ischemic pain; discuss with the surgical team first",
    ],
}


def worked_example(block_id, agent_keys, volume_ml):
    primary = AGENTS[agent_keys[0]]
    if primary["agent"].startswith("Bupivacaine") or primary["agent"].startswith("Ropivacaine"):
        conc_pct, mg_per_ml = 0.25, 2.5
        conc_label = "0.25%"
    else:
        conc_pct, mg_per_ml = 1.0, 10.0
        conc_label = "1%"
    dose_mg = volume_ml * mg_per_ml
    max_70 = primary["maxDoseMgPerKg"] * 70
    max_50 = primary["maxDoseMgPerKg"] * 50
    text = (
        f"Worked example: {volume_ml} mL of {conc_label} {primary['agent'].split(' ')[0].lower()} "
        f"= {dose_mg:g} mg. Maximum at {primary['maxDoseMgPerKg']:g} mg/kg: 70 kg = {max_70:g} mg; "
        f"50 kg = {max_50:g} mg."
    )
    if block_id in BILATERAL_BLOCKS:
        both = dose_mg * 2
        text += (
            f" Bilateral at the same volume = {both:g} mg total, which EXCEEDS the maximum for "
            f"patients under {both / AGENTS[agent_keys[0]]['maxDoseMgPerKg']:g} kg — dilute or reduce volume."
        )
    return text


def build_dosing(block_id):
    agent_keys, volume_ml = BLOCKS[block_id]
    return {
        "agents": [AGENTS[key] for key in agent_keys],
        "workedExample": worked_example(block_id, agent_keys, volume_ml),
        "cumulativeWarning": CUMULATIVE_WARNING,
        "monitoring": MONITORING,
        "rescueCardID": RESCUE_CARD_ID,
    }


def main() -> int:
    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in procedures}

    regional = [item for item in procedures if item.get("category") == "Regional Anesthesia"]
    missing_from_table = [item["id"] for item in regional if item["id"] not in BLOCKS]
    if missing_from_table:
        print(f"ERROR: regional procedures without a dosing table entry: {missing_from_table}")
        return 1

    for block_id in BLOCKS:
        item = by_id.get(block_id)
        if item is None:
            print(f"ERROR: expected procedure not found: {block_id}")
            return 1
        item["dosing"] = build_dosing(block_id)
        references = item["sections"].setdefault("references", [])
        for reference in DOSING_REFERENCES:
            if reference not in references:
                references.append(reference)

    for block_id, section, old, new in TEXT_FIXES:
        section_items = by_id[block_id]["sections"][section]
        if new in section_items:
            continue  # already applied
        if old not in section_items:
            print(f"ERROR: text fix target missing in {block_id}.{section}: {old!r}")
            return 1
        section_items[section_items.index(old)] = new

    for block_id, additions in CONTRAINDICATION_ADDITIONS.items():
        contraindications = by_id[block_id]["sections"]["contraindications"]
        for line in additions:
            if line not in contraindications:
                contraindications.append(line)

    # Match the file's existing serialization (indent=2, ASCII-escaped, no
    # trailing newline, LF endings) so the diff shows only real content changes.
    PROCEDURES.write_bytes(
        json.dumps(procedures, indent=2, ensure_ascii=True).encode("utf-8")
    )
    print(f"Applied structured dosing to {len(BLOCKS)} regional anesthesia procedures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
