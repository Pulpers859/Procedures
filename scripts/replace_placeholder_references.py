#!/usr/bin/env python3
"""Replace the recycled placeholder reference on the 26 batch nerve blocks
with traceable citations.

Provenance: the 26 nerve-block procedures added by the batch generator scripts
all shipped with the same placeholder line ("Standard emergency medicine
regional anesthesia literature."), which release mode rightly blocks. This
script swaps that line for real, conventional sources: the NYSORA technique
chapter for the block, the seminal description paper where one exists, and
Roberts and Hedges' as the EM procedure baseline. Citations are drafted from
conventional knowledge and must be confirmed by the clinical reviewer during
per-item adjudication — this script does not clinically approve anything and
changes no reviewerStatus.

Run from the repo root:
    python scripts/replace_placeholder_references.py
Idempotent; fails loudly if an expected placeholder is missing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "Procedures" / "Resources" / "procedures.json"

PLACEHOLDER = "Standard emergency medicine regional anesthesia literature."

ROBERTS_HEDGES = (
    "Roberts JR, Custalow CB, Thomsen TW, eds. Roberts and Hedges' Clinical "
    "Procedures in Emergency Medicine and Acute Care. 7th ed. Elsevier; 2019."
)
NYSORA = "NYSORA. {chapter}. nysora.com."

# Per-block replacements. Every block gets Roberts & Hedges as the EM baseline
# plus a technique-specific source; seminal first-description papers are used
# where the block has one.
REPLACEMENTS = {
    "block_interscalene": [
        NYSORA.format(chapter="Ultrasound-Guided Interscalene Brachial Plexus Block"),
        ROBERTS_HEDGES,
    ],
    "block_supraclavicular": [
        NYSORA.format(chapter="Ultrasound-Guided Supraclavicular Brachial Plexus Block"),
        ROBERTS_HEDGES,
    ],
    "block_raptir": [
        "Charbonneau J, Frechette Y, Sansoucy Y, Echave P. The ultrasound-guided "
        "retroclavicular block: a prospective feasibility study. Reg Anesth Pain Med. 2015;40(5):605-609.",
        NYSORA.format(chapter="Ultrasound-Guided Infraclavicular Brachial Plexus Block"),
    ],
    "block_radial_nerve": [
        "Liebmann O, Price D, Mills C, et al. Feasibility of forearm ultrasonography-guided "
        "nerve blocks of the radial, ulnar, and median nerves for hand procedures in the "
        "emergency department. Ann Emerg Med. 2006;48(5):558-562.",
        ROBERTS_HEDGES,
    ],
    "block_median_nerve": [
        "Liebmann O, Price D, Mills C, et al. Feasibility of forearm ultrasonography-guided "
        "nerve blocks of the radial, ulnar, and median nerves for hand procedures in the "
        "emergency department. Ann Emerg Med. 2006;48(5):558-562.",
        ROBERTS_HEDGES,
    ],
    "block_ulnar_nerve": [
        "Liebmann O, Price D, Mills C, et al. Feasibility of forearm ultrasonography-guided "
        "nerve blocks of the radial, ulnar, and median nerves for hand procedures in the "
        "emergency department. Ann Emerg Med. 2006;48(5):558-562.",
        ROBERTS_HEDGES,
    ],
    "block_superficial_cervical_plexus": [
        NYSORA.format(chapter="Ultrasound-Guided Cervical Plexus Block"),
        ROBERTS_HEDGES,
    ],
    "block_serratus_anterior": [
        "Blanco R, Parras T, McDonnell JG, Prats-Galino A. Serratus plane block: a novel "
        "ultrasound-guided thoracic wall nerve block. Anaesthesia. 2013;68(11):1107-1113.",
        ROBERTS_HEDGES,
    ],
    "block_thoracic_esp": [
        "Forero M, Adhikary SD, Lopez H, Tsui C, Chin KJ. The erector spinae plane block: "
        "a novel analgesic technique in thoracic neuropathic pain. Reg Anesth Pain Med. "
        "2016;41(5):621-627.",
        ROBERTS_HEDGES,
    ],
    "block_tap": [
        "McDonnell JG, O'Donnell B, Curley G, et al. The analgesic efficacy of transversus "
        "abdominis plane block after abdominal surgery: a prospective randomized controlled "
        "trial. Anesth Analg. 2007;104(1):193-197.",
        NYSORA.format(chapter="Ultrasound-Guided Transversus Abdominis Plane Block"),
    ],
    "block_pecs": [
        "Blanco R. The 'pecs block': a novel technique for providing analgesia after breast "
        "surgery. Anaesthesia. 2011;66(9):847-848.",
        ROBERTS_HEDGES,
    ],
    "block_femoral_nerve": [
        NYSORA.format(chapter="Ultrasound-Guided Femoral Nerve Block"),
        ROBERTS_HEDGES,
    ],
    "block_peng": [
        "Giron-Arango L, Peng PWH, Chin KJ, Brull R, Perlas A. Pericapsular nerve group "
        "(PENG) block for hip fracture. Reg Anesth Pain Med. 2018;43(8):859-863.",
        ROBERTS_HEDGES,
    ],
    "block_saphenous_nerve": [
        NYSORA.format(chapter="Ultrasound-Guided Saphenous (Adductor Canal) Nerve Block"),
        ROBERTS_HEDGES,
    ],
    "block_popliteal_sciatic": [
        NYSORA.format(chapter="Ultrasound-Guided Popliteal Sciatic Nerve Block"),
        ROBERTS_HEDGES,
    ],
    "block_transgluteal_sciatic": [
        NYSORA.format(chapter="Ultrasound-Guided Sciatic Nerve Block"),
        ROBERTS_HEDGES,
    ],
    "block_tibial_nerve": [
        NYSORA.format(chapter="Ultrasound-Guided Ankle Block"),
        ROBERTS_HEDGES,
    ],
    "block_sural_nerve": [
        NYSORA.format(chapter="Ultrasound-Guided Ankle Block"),
        ROBERTS_HEDGES,
    ],
    "block_superficial_peroneal": [
        NYSORA.format(chapter="Ultrasound-Guided Ankle Block"),
        ROBERTS_HEDGES,
    ],
    "block_deep_peroneal": [
        NYSORA.format(chapter="Ultrasound-Guided Ankle Block"),
        ROBERTS_HEDGES,
    ],
    "block_supraorbital": [
        "Salam GA. Regional anesthesia for office procedures: part I. Head and neck "
        "surgeries. Am Fam Physician. 2004;69(3):585-590.",
        ROBERTS_HEDGES,
    ],
    "block_infraorbital": [
        "Salam GA. Regional anesthesia for office procedures: part I. Head and neck "
        "surgeries. Am Fam Physician. 2004;69(3):585-590.",
        ROBERTS_HEDGES,
    ],
    "block_mental": [
        "Salam GA. Regional anesthesia for office procedures: part I. Head and neck "
        "surgeries. Am Fam Physician. 2004;69(3):585-590.",
        ROBERTS_HEDGES,
    ],
    "block_inferior_alveolar": [
        "Malamed SF. Handbook of Local Anesthesia. 7th ed. Elsevier; 2019.",
        ROBERTS_HEDGES,
    ],
    "block_superior_alveolar": [
        "Malamed SF. Handbook of Local Anesthesia. 7th ed. Elsevier; 2019.",
        ROBERTS_HEDGES,
    ],
    "block_auricular": [
        "Tintinalli JE, Ma OJ, Yealy DM, et al, eds. Tintinalli's Emergency Medicine: "
        "A Comprehensive Study Guide. 9th ed. McGraw-Hill; 2020.",
        ROBERTS_HEDGES,
    ],
}


def main() -> int:
    procedures = json.loads(PROCEDURES.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in procedures}

    remaining = [
        item["id"] for item in procedures
        if PLACEHOLDER in item["sections"]["references"] and item["id"] not in REPLACEMENTS
    ]
    if remaining:
        print(f"ERROR: placeholder present on procedures without a replacement: {remaining}")
        return 1

    replaced = 0
    for block_id, citations in REPLACEMENTS.items():
        item = by_id.get(block_id)
        if item is None:
            print(f"ERROR: expected procedure not found: {block_id}")
            return 1
        references = item["sections"]["references"]
        if PLACEHOLDER not in references:
            if all(citation in references for citation in citations):
                continue  # already applied
            print(f"ERROR: {block_id} has neither the placeholder nor the replacements")
            return 1
        index = references.index(PLACEHOLDER)
        references[index:index + 1] = [
            citation for citation in citations if citation not in references
        ]
        replaced += 1

    if replaced:
        # Match the file's serialization exactly (indent=2, ASCII, no trailing
        # newline) so the diff shows only real content changes.
        PROCEDURES.write_bytes(
            json.dumps(procedures, indent=2, ensure_ascii=True).encode("utf-8")
        )
    print(f"Replaced the placeholder reference on {replaced} procedures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
