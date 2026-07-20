import json

RESCUE_FILE = r"C:\Dev\Procedures\Procedures\Resources\rescue_cards.json"

new_procedure_ids = [
    "block_interscalene", "block_supraclavicular", "block_raptir",
    "block_radial_nerve", "block_median_nerve", "block_ulnar_nerve",
    "block_superficial_cervical_plexus", "block_serratus_anterior", "block_thoracic_esp",
    "block_tap", "block_pecs",
    "block_femoral_nerve", "block_peng", "block_saphenous_nerve",
    "block_popliteal_sciatic", "block_transgluteal_sciatic", "block_tibial_nerve",
    "block_sural_nerve", "block_superficial_peroneal", "block_deep_peroneal",
    "block_supraorbital", "block_infraorbital", "block_mental",
    "block_inferior_alveolar", "block_superior_alveolar", "block_auricular"
]

def update_rescue_cards():
    with open(RESCUE_FILE, "r") as f:
        data = json.load(f)
        
    for card in data:
        if card["id"] == "local_anesthetic_systemic_toxicity":
            existing = set(card.get("relatedProcedureIDs", []))
            for pid in new_procedure_ids:
                if pid not in existing:
                    card["relatedProcedureIDs"].append(pid)
                    
    with open(RESCUE_FILE, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_rescue_cards()
    print("Updated rescue_cards.json with new procedure IDs for LAST.")
