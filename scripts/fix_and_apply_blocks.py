import json
import sys

from add_nerve_blocks_batch1 import new_blocks as blocks1
from add_nerve_blocks_batch2 import new_blocks as blocks2
from add_nerve_blocks_batch3 import new_blocks as blocks3
from add_nerve_blocks_batch4 import new_blocks as blocks4

PROCEDURES_FILE = r"C:\Dev\Procedures\Procedures\Resources\procedures.json"

all_new_blocks = blocks1 + blocks2 + blocks3 + blocks4

def transform_block(block):
    sections_dict = {}
    keys_to_move = [
        "shiftMode", "indications", "contraindications", "anatomy", 
        "equipment", "positioning", "steps", "ultrasound", 
        "confirmation", "troubleshooting", "complications", 
        "aftercare", "documentation", "seniorPearls"
    ]
    for key in keys_to_move:
        if key in block:
            sections_dict[key] = block.pop(key)
            
    sections_dict["references"] = ["Standard emergency medicine regional anesthesia literature."]
            
    block["sections"] = sections_dict
    block["category"] = "Regional Anesthesia"
    block["difficulty"] = "Advanced"
    block["setting"] = ["ED", "Trauma"]
    block["lastReviewed"] = "2026-07-14"
    block["reviewerStatus"] = "Needs Clinical Review"
    block["version"] = "0.1.0"
    
    if "tags" not in block:
        block["tags"] = ["regional", "nerve block", "ultrasound"]
        if "searchTerms" in block:
            block["tags"].extend(block.pop("searchTerms"))
        
    return block

def load_data():
    with open(PROCEDURES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(PROCEDURES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load_data()
    existing_ids = set(p["id"] for p in data)
    
    added = 0
    for block in all_new_blocks:
        transformed = transform_block(block)
        if transformed["id"] not in existing_ids:
            data.append(transformed)
            added += 1
            
    save_data(data)
    print(f"Successfully added {added} formatted blocks to {PROCEDURES_FILE}")
